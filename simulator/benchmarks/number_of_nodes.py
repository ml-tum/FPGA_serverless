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
        "NUM_NODES": [1, 2, 5, 10, 20, 40, 60, 80],
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
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    # results = run_benchmark(inputs)
    # with open(f"number_of_nodes_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
    #     results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
    #     f.write(results_json)

    # load results from json file

    # finals number_of_nodes_benchmark_results_20230703170232.json
    # prefer number_of_nodes_benchmark_results_20230703184900.json


    results = []
    with open("number_of_nodes_benchmark_results_20230703170232.json", "r") as f:
        results = json.load(f)

    df = pd.DataFrame(results)
    apply_median_utilization(df)

    df['Nodes'] = df['num_nodes']
    df['FPGA utilization'] = df['median_fpga_utilization']
    df['Cold start \\%'] = df['coldstart_percent']


    # get table that shows the median FPGA utilization and coldstart_percent for each num_nodes
    tbl = df[['Nodes', 'FPGA utilization', 'Cold start \\%']].groupby(['Nodes']).median()

    tbl.to_latex(
        buf='../../../figures/number_of_nodes.tex',
        float_format="{:0.2f}".format,
        caption=False,
        label=False,
    )

    def plot():
        # draw line plot depicting median fpga utilization and cold start percentage relative to number of nodes
        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_xlabel('Nodes', fontsize=14)
        # set tick size of 14
        ax1.tick_params(axis='x', labelsize=14)

        ax1.set_ylabel('FPGA utilization', fontsize=14)
        ax1.plot(tbl.index, tbl['FPGA utilization'], color='blue')
        # low values should be more zoomed in
        ax1.set_yscale('log')
        ax1.tick_params(axis='y', labelcolor='blue', labelsize=14)


        ax2 = ax1.twinx()
        ax2.set_ylabel(
            'Cold start %',
            # set size of 14
            fontsize=14,
        )

        ax2.plot(tbl.index, tbl['Cold start \\%'], color='green', linestyle='--')
        ax2.tick_params(axis='y', labelcolor='green', labelsize=14)
        ax2.yaxis.set_major_formatter(PercentFormatter(xmax=100))

        # place figure in center top above the plot
        fig.legend(['FPGA utilization', 'Cold start %'], loc='upper center', ncol=2, bbox_to_anchor=(0.5, 0.95), fontsize=14)

        fig.tight_layout()

    plot()
    plt.show()

    plot()
    plt.savefig('../../../figures/number_of_nodes.png', dpi=300)
