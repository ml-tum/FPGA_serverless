import datetime
import json
import multiprocessing
import os
import random
from benchmark import apply_median_utilization

from matplotlib.ticker import PercentFormatter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas

from benchmark import run_benchmark
import pandas as pd

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5],
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01],
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.75],

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
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 2,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 1,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 1,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 4,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 1,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 1,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 6,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 1,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 1,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 8,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 1,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 1,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 3,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 3,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 4,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 4,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 6,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 6,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 8,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 8,
            },
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    # results = run_benchmark(inputs)
    # with open(f"scheduler_weights_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
    #     results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
    #     f.write(results_json)

    # load results from json file
    with open("scheduler_weights_benchmark_results_20230703195803.json", "r") as f:
        results = json.load(f)

    df = pd.DataFrame(results)
    apply_median_utilization(df)

    df['Nodes'] = df['num_nodes']
    df['FPGA utilization'] = df['median_fpga_utilization']
    df['Cold start \\%'] = df['coldstart_percent']
    df['Scheduler Weights'] = df['scheduler_weights']

    # get table that shows the median FPGA utilization and coldstart_percent for each num_nodes
    tbl = df[['Scheduler Weights', 'FPGA utilization', 'Cold start \\%']].groupby(['Scheduler Weights']).median()

    tbl.to_latex(
        buf='../../../figures/scheduler_weights.tex',
        float_format="{:0.2f}".format,
        caption=False,
        label=False,
    )

    # create new df from tbl
    df = pd.DataFrame(tbl)

    print(tbl)


    def plot():
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Plot the "FPGA utilization" on ax1
        ax1.plot(df.index, df['FPGA utilization'], color='b', marker='^', linestyle='None', label='FPGA utilization')

        ax1.set_xlabel('Scheduler Weights')
        ax1.set_ylabel('FPGA utilization', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        # instantiate a second axes that shares the same x-axis
        ax2 = ax1.twinx()

        # Plot the "Cold start %" on ax2
        ax2.plot(df.index, df['Cold start \\%'], color='r', marker='o', linestyle='None', label='Cold start %')

        ax2.set_ylabel('Cold start %', color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        plt.title('FPGA utilization and Cold Start % for different Scheduler Weights')
        plt.xticks(rotation=45)  # Rotates X-Axis Ticks by 45-degrees

        # draw legends below the plot
        ax1.legend(loc='lower center', bbox_to_anchor=(0.4, -0.3), ncol=2)
        ax2.legend(loc='lower center', bbox_to_anchor=(0.6, -0.3), ncol=2)

        ax2.invert_yaxis()

        fig.tight_layout()  # otherwise the right y-label is slightly clipped


    plot()
    plt.show()

    plot()
    plt.savefig('../../../figures/scheduler_weights.png', dpi=300)
