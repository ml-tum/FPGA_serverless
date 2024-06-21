from unittest import TestCase
from simulator import run_on_file
import datetime
import plotly.express as px
import pandas as pd

# TEST TRACES (duration in ms)
"""
app,func,end_timestamp,duration
1,a,1,1
2,b,3,2
3,c,5,3
4,d,6,4
5,e,7,5
6,f,8,6
7,g,9,7
8,h,10,8
"""


class TestWaiting(TestCase):
    def test_waiting_single_slot(self):
        nodes, functions, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing = run_on_file(
            csv_file_path="../test-waiting.csv",
            NUM_NODES=1,
            NUM_FPGA_SLOTS_PER_NODE=1,
            MAX_REQUESTS=0,
            ENABLE_LOGS=True,
            ENABLE_PRINT_RESULTS=True,
            ARRIVAL_POLICY="FIFO",
            FUNCTION_KEEPALIVE=60,
            ENABLE_PROGRESS_LOGS=True,
            CHARACTERIZED_FUNCTIONS={
                "1": {
                    "characterization": {
                        "avg_req_duration": 50,
                        "avg_req_per_sec": 1
                    },
                    "fpga_ratio": 1,
                    "label": "f1",
                    "mean_speedup": 1,
                    "run_on_fpga": True
                }
            },
            RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=1,
            FPGA_RECONFIGURATION_TIME=10,
            CHARACTERIZED_FUNCTIONS_LABEL="strat1",
            FPGA_BITSTREAM_LOCALITY_WEIGHT=1,
            FUNCTION_PLACEMENT_IS_COLDSTART=False,
            RECENT_FPGA_USAGE_TIME_WEIGHT=1,
            FUNCTION_HOST_COLDSTART_TIME_MS=0,
            ACCELERATE_REQUESTS=1
        )

        sum_delays = 0
        for key in metrics["latencies"]:
            sum_delays += metrics["latencies"][key][5]

        self.assertEqual(sum_delays, 71.0 * 1000)

        # (arrival_timestamp, processing_start_timestamp, response_timestamp, invocation_latency, duration_ms, delay)
        self.assertEqual(metrics["latencies"], {'1-a-2021-01-31 01:00:00': (datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            1010.0,
                                                                            1000.0,
                                                                            0),
                                                '2-b-2021-01-31 01:00:01': (datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            2010.0,
                                                                            2000.0,
                                                                            0),
                                                '3-c-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 6),
                                                                            4010.0,
                                                                            3000.0,
                                                                            1000.0),
                                                '4-d-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 6),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            8010.0,
                                                                            4000.0,
                                                                            4000.0),
                                                '5-e-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 15),
                                                                            13010.0,
                                                                            5000.0,
                                                                            8000.0),
                                                '6-f-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 15),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            19010.0,
                                                                            6000.0,
                                                                            13000.0),
                                                '7-g-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 28),
                                                                            26010.0,
                                                                            7000.0,
                                                                            19000.0),
                                                '8-h-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 28),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 36),
                                                                            34010.0,
                                                                            8000.0,
                                                                            26000.0)})

        # create a gantt chart for the arrival, processing start, and response times of each request
        df_rows = []

        for key in metrics["latencies"]:
            df = df_rows.append({
                "Task": key + "-arrival",
                "Start": metrics["latencies"][key][0],
                "Finish": metrics["latencies"][key][1],
                "Resource": key.split("-")[1]
            })

            df = df_rows.append({
                "Task": key + "-processing",
                "Start": metrics["latencies"][key][1],
                "Finish": metrics["latencies"][key][2],
                "Resource": key.split("-")[1]
            })

        df = pd.DataFrame(
            columns=["Task", "Start", "Finish", "Resource"],
            data=df_rows
        )

        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
        fig.update_yaxes(categoryorder="total descending")

        fig.show()

    def test_waiting_multi_slot(self):
        nodes, functions, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing = run_on_file(
            csv_file_path="../test-waiting.csv",
            NUM_NODES=1,
            NUM_FPGA_SLOTS_PER_NODE=2,
            MAX_REQUESTS=0,
            ENABLE_LOGS=True,
            ENABLE_PRINT_RESULTS=True,
            ARRIVAL_POLICY="FIFO",
            FUNCTION_KEEPALIVE=60,
            ENABLE_PROGRESS_LOGS=True,
            ACCELERATE_REQUESTS=1,
            CHARACTERIZED_FUNCTIONS={
                "1": {
                    "characterization": {
                        "avg_req_duration": 50,
                        "avg_req_per_sec": 1
                    },
                    "fpga_ratio": 1,
                    "label": "f1",
                    "mean_speedup": 1,
                    "run_on_fpga": True
                }
            },
            RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=1,
            FPGA_RECONFIGURATION_TIME=10,
            CHARACTERIZED_FUNCTIONS_LABEL="strat1",
            FPGA_BITSTREAM_LOCALITY_WEIGHT=1,
            FUNCTION_PLACEMENT_IS_COLDSTART=False,
            RECENT_FPGA_USAGE_TIME_WEIGHT=1,
            FUNCTION_HOST_COLDSTART_TIME_MS=0,
        )

        sum_delays = 0
        for key in metrics["latencies"]:
            sum_delays += metrics["latencies"][key][5]

        self.assertEqual(28.0 * 1000, sum_delays)

        self.assertEqual(metrics["latencies"], {'1-a-2021-01-31 01:00:00': (datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            1010.0,
                                                                            1000.0,
                                                                            0),
                                                '2-b-2021-01-31 01:00:01': (datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            2010.0,
                                                                            2000.0,
                                                                            0),
                                                '3-c-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 5),
                                                                            3010.0,
                                                                            3000.0,
                                                                            0),
                                                '4-d-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 7),
                                                                            5010.0,
                                                                            4000.0,
                                                                            1000.0),
                                                '5-e-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 5),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            8010.0,
                                                                            5000.0,
                                                                            3000.0),
                                                '6-f-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 7),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 13),
                                                                            11010.0,
                                                                            6000.0,
                                                                            5000.0),
                                                '7-g-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 17),
                                                                            15010.0,
                                                                            7000.0,
                                                                            8000.0),
                                                '8-h-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 13),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            19010.0,
                                                                            8000.0,
                                                                            11000.0)})

        # create a gantt chart for the arrival, processing start, and response times of each request
        df_rows = []

        for key in metrics["latencies"]:
            df = df_rows.append({
                "Task": key + "-arrival",
                "Start": metrics["latencies"][key][0],
                "Finish": metrics["latencies"][key][1],
                "Resource": key.split("-")[1],
                "Slot": metrics["latencies"][key][5]
            })

            df = df_rows.append({
                "Task": key + "-processing",
                "Start": metrics["latencies"][key][1],
                "Finish": metrics["latencies"][key][2],
                "Resource": key.split("-")[1],
                "Slot": metrics["latencies"][key][5]
            })

        df = pd.DataFrame(
            columns=["Task", "Start", "Finish", "Resource", "Slot"],
            data=df_rows
        )

        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Slot")
        fig.update_yaxes(categoryorder="total descending")

        fig.show()

    def test_cpu_only(self):
        nodes, functions, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing = run_on_file(
            csv_file_path="../test-waiting.csv",
            NUM_NODES=1,
            NUM_FPGA_SLOTS_PER_NODE=0,
            MAX_REQUESTS=0,
            ENABLE_LOGS=True,
            ENABLE_PRINT_RESULTS=True,
            ARRIVAL_POLICY="FIFO",
            FUNCTION_KEEPALIVE=60,
            ENABLE_PROGRESS_LOGS=True,
            CHARACTERIZED_FUNCTIONS={
                "1": {
                    "characterization": {
                        "avg_req_duration": 50,
                        "avg_req_per_sec": 1
                    },
                    "fpga_ratio": 0,
                    "label": "f1",
                    "mean_speedup": 1,
                    "run_on_fpga": True
                }
            },
            RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=1,
            FPGA_RECONFIGURATION_TIME=10,
            CHARACTERIZED_FUNCTIONS_LABEL="strat1",
            FPGA_BITSTREAM_LOCALITY_WEIGHT=1,
            FUNCTION_PLACEMENT_IS_COLDSTART=False,
            RECENT_FPGA_USAGE_TIME_WEIGHT=1,
            FUNCTION_HOST_COLDSTART_TIME_MS=0,
        )

        sum_delays = 0
        for key in metrics["latencies"]:
            sum_delays += metrics["latencies"][key][5]

        self.assertEqual(sum_delays, 71.0 * 1000)

        # (arrival_timestamp, processing_start_timestamp, response_timestamp, invocation_latency, duration_ms, delay)
        self.assertEqual(metrics["latencies"], {'1-a-2021-01-31 01:00:00': (datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            1000.0,
                                                                            1000.0,
                                                                            0),
                                                '2-b-2021-01-31 01:00:01': (datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            2000.0,
                                                                            2000.0,
                                                                            0),
                                                '3-c-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 6),
                                                                            4000.0,
                                                                            3000.0,
                                                                            1000.0),
                                                '4-d-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 6),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            8000.0,
                                                                            4000.0,
                                                                            4000.0),
                                                '5-e-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 15),
                                                                            13000.0,
                                                                            5000.0,
                                                                            8000.0),
                                                '6-f-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 15),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            19000.0,
                                                                            6000.0,
                                                                            13000.0),
                                                '7-g-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 28),
                                                                            26000.0,
                                                                            7000.0,
                                                                            19000.0),
                                                '8-h-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 28),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 36),
                                                                            34000.0,
                                                                            8000.0,
                                                                            26000.0)})

        # create a gantt chart for the arrival, processing start, and response times of each request
        df_rows = []

        for key in metrics["latencies"]:
            df = df_rows.append({
                "Task": key + "-arrival",
                "Start": metrics["latencies"][key][0],
                "Finish": metrics["latencies"][key][1],
                "Resource": key.split("-")[1]
            })

            df = df_rows.append({
                "Task": key + "-processing",
                "Start": metrics["latencies"][key][1],
                "Finish": metrics["latencies"][key][2],
                "Resource": key.split("-")[1]
            })

        df = pd.DataFrame(
            columns=["Task", "Start", "Finish", "Resource"],
            data=df_rows
        )

        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
        fig.update_yaxes(categoryorder="total descending")

        fig.show()

    def test_cpu_mixed(self):
        nodes, functions, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing = run_on_file(
            csv_file_path="../test-waiting.csv",
            NUM_NODES=1,
            NUM_FPGA_SLOTS_PER_NODE=0,
            MAX_REQUESTS=0,
            ENABLE_LOGS=True,
            ENABLE_PRINT_RESULTS=True,
            ARRIVAL_POLICY="FIFO",
            FUNCTION_KEEPALIVE=60,
            ENABLE_PROGRESS_LOGS=True,
            ACCELERATE_REQUESTS=1,
            CHARACTERIZED_FUNCTIONS={
                "1": {
                    "characterization": {
                        "avg_req_duration": 50,
                        "avg_req_per_sec": 1
                    },
                    "fpga_ratio": 0.5,
                    "label": "f1",
                    "mean_speedup": 2,
                    "run_on_fpga": True
                }
            },
            RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=1,
            FPGA_RECONFIGURATION_TIME=10,
            CHARACTERIZED_FUNCTIONS_LABEL="strat1",
            FPGA_BITSTREAM_LOCALITY_WEIGHT=1,
            FUNCTION_PLACEMENT_IS_COLDSTART=False,
            RECENT_FPGA_USAGE_TIME_WEIGHT=1,
            FUNCTION_HOST_COLDSTART_TIME_MS=0,
        )

        sum_delays = 0
        for key in metrics["latencies"]:
            sum_delays += metrics["latencies"][key][5]

        self.assertEqual(sum_delays, 32.5 * 1000)

        # (arrival_timestamp, processing_start_timestamp, response_timestamp, invocation_latency, duration_ms, delay)
        self.assertEqual(metrics["latencies"], {'1-a-2021-01-31 01:00:00': (datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 0,
                                                                                              500000),
                                                                            500.0,
                                                                            500.0,
                                                                            0),
                                                '2-b-2021-01-31 01:00:01': (datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            1000.0,
                                                                            1000.0,
                                                                            0),
                                                '3-c-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3,
                                                                                              500000),
                                                                            1500.0,
                                                                            1500.0,
                                                                            0),
                                                '4-d-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3,
                                                                                              500000),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 5,
                                                                                              500000),
                                                                            3500.0,
                                                                            2000.0,
                                                                            1500.0),
                                                '5-e-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 5,
                                                                                              500000),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 8),
                                                                            6000.0,
                                                                            2500.0,
                                                                            3500.0),
                                                '6-f-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 8),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 11),
                                                                            9000.0,
                                                                            3000.0,
                                                                            6000.0),
                                                '7-g-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 11),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 14,
                                                                                              500000),
                                                                            12500.0,
                                                                            3500.0,
                                                                            9000.0),
                                                '8-h-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 14,
                                                                                              500000),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 18,
                                                                                              500000),
                                                                            16500.0,
                                                                            4000.0,
                                                                            12500.0)})

        # create a gantt chart for the arrival, processing start, and response times of each request
        df_rows = []

        for key in metrics["latencies"]:
            df = df_rows.append({
                "Task": key + "-arrival",
                "Start": metrics["latencies"][key][0],
                "Finish": metrics["latencies"][key][1],
                "Resource": key.split("-")[1]
            })

            df = df_rows.append({
                "Task": key + "-processing",
                "Start": metrics["latencies"][key][1],
                "Finish": metrics["latencies"][key][2],
                "Resource": key.split("-")[1]
            })

        df = pd.DataFrame(
            columns=["Task", "Start", "Finish", "Resource"],
            data=df_rows
        )

        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
        fig.update_yaxes(categoryorder="total descending")

        fig.show()
