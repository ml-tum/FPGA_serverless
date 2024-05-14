from unittest import TestCase
from simulator import run_on_file
import datetime
import plotly.express as px
import pandas as pd

# TEST TRACES
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
            FPGA_RECONFIGURATION_TIME=0.1,
            CHARACTERIZED_FUNCTIONS_LABEL="strat1",
            FPGA_BITSTREAM_LOCALITY_WEIGHT=1,
            FUNCTION_PLACEMENT_IS_COLDSTART=False,
            RECENT_FPGA_USAGE_TIME_WEIGHT=1,
            FUNCTION_HOST_COLDSTART_TIME_MS=0.1,
        )

        sum_delays = 0
        for key in metrics["latencies"]:
            sum_delays += metrics["latencies"][key][4]

        self.assertEqual(sum_delays, 71.0)

        self.assertEqual(metrics["latencies"], {'1-a-2021-01-31 01:00:00': (datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            1000.0,
                                                                            0.0,
                                                                            0),
                                                '2-b-2021-01-31 01:00:01': (datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            2000.0,
                                                                            0.0,
                                                                            0),
                                                '3-c-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 6),
                                                                            3000.0,
                                                                            1.0,
                                                                            0),
                                                '4-d-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 6),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            4000.0,
                                                                            4.0,
                                                                            0),
                                                '5-e-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 15),
                                                                            5000.0,
                                                                            8.0,
                                                                            0),
                                                '6-f-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 15),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            6000.0,
                                                                            13.0,
                                                                            0),
                                                '7-g-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 28),
                                                                            7000.0,
                                                                            19.0,
                                                                            0),
                                                '8-h-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 28),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 36),
                                                                            8000.0,
                                                                            26.0,
                                                                            0)})

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
            FPGA_RECONFIGURATION_TIME=0.1,
            CHARACTERIZED_FUNCTIONS_LABEL="strat1",
            FPGA_BITSTREAM_LOCALITY_WEIGHT=1,
            FUNCTION_PLACEMENT_IS_COLDSTART=False,
            RECENT_FPGA_USAGE_TIME_WEIGHT=1,
            FUNCTION_HOST_COLDSTART_TIME_MS=0.1,
        )

        sum_delays = 0
        for key in metrics["latencies"]:
            sum_delays += metrics["latencies"][key][4]

        self.assertEqual(sum_delays, 28.0)

        self.assertEqual(metrics["latencies"], {'1-a-2021-01-31 01:00:00': (datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            1000.0,
                                                                            0.0,
                                                                            0),
                                                '2-b-2021-01-31 01:00:01': (datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 1),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            2000.0,
                                                                            0.0,
                                                                            1),
                                                '3-c-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 5),
                                                                            3000.0,
                                                                            0.0,
                                                                            0),
                                                '4-d-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 3),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 7),
                                                                            4000.0,
                                                                            1.0,
                                                                            1),
                                                '5-e-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 5),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            5000.0,
                                                                            3.0,
                                                                            0),
                                                '6-f-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 7),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 13),
                                                                            6000.0,
                                                                            5.0,
                                                                            1),
                                                '7-g-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 10),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 17),
                                                                            7000.0,
                                                                            8.0,
                                                                            0),
                                                '8-h-2021-01-31 01:00:02': (datetime.datetime(2021, 1, 31, 1, 0, 2),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 13),
                                                                            datetime.datetime(2021, 1, 31, 1, 0, 21),
                                                                            8000.0,
                                                                            11.0,
                                                                            1)})

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
