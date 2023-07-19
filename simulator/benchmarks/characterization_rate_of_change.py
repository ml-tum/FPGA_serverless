import datetime
import json
import multiprocessing
import os
import random
from benchmark import apply_median_utilization

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas

from benchmark import run_benchmark
import pandas as pd

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0, 0.25, 0.5, 0.75, 1],
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01, 0.1],
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0, 0.25, 0.5, 0.75, 1],

        "MAX_REQUESTS": [0],
        "NUM_NODES": [10],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": [
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 1,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 1,
            },
            # {
            #     "FPGA_BITSTREAM_LOCALITY_WEIGHT": 2,
            #     "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
            #     "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            # },
            # {
            #     "FPGA_BITSTREAM_LOCALITY_WEIGHT": 4,
            #     "RECENT_FPGA_USAGE_TIME_WEIGHT": 4,
            #     "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 4,
            # },
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    # results = run_benchmark(inputs)
    # with open(
    #         f"characterization_rate_of_change_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json",
    #         "w") as f:
    #     results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
    #     f.write(results_json)

    # load results from json file
    with open("characterization_rate_of_change_benchmark_results_20230701160400.json", "r") as f:
        results = json.load(f)

    df = pd.DataFrame(results)
    apply_median_utilization(df)

    df['r'] = df['request_duration_fpga_usage_ratio']
    df['p'] = df['request_run_on_fpga_percentage']
    df['m'] = df['request_run_on_fpga_min_duration']

    # get subset for request_run_on_fpga_min_duration=0.1
    longer = df[df['request_run_on_fpga_min_duration'] == 0.1]


    def format_float(num):
        try:
            return "{:.2f}".format(float(num))
        except ValueError:
            return num


    # get table of median FPGA utilization with request_run_on_fpga_percentage as columns, request_duration_fpga_usage_ratio as rows
    tbl = longer.pivot_table(index='r', columns='p', values='median_fpga_utilization', aggfunc='mean')

    tbl.index = tbl.index.to_series().apply(format_float)
    tbl.columns = tbl.columns.to_series().apply(format_float)

    # print table
    tbl.to_latex(
        buf='../../../figures/characterization_rate_of_change_longer.tex',
        float_format="{:0.2f}".format,
        caption=False,
        label=False,
        # instead of lrrrrr, use c|ccccc
        column_format='c|ccccc',
    )

    shorter = df[df['request_run_on_fpga_min_duration'] == 0.01]

    tbl = shorter.pivot_table(index='r', columns='p', values='median_fpga_utilization', aggfunc='mean')

    tbl.index = tbl.index.to_series().apply(format_float)
    tbl.columns = tbl.columns.to_series().apply(format_float)

    shorter_output = tbl.to_latex(
        buf='../../../figures/characterization_rate_of_change_shorter.tex',
        float_format="{:0.2f}".format,
        caption=False,
        label=False,
        column_format='c|ccccc',
    )
