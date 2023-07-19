import datetime
import multiprocessing
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from benchmark import run_benchmark

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5],  # 50% of requests run on FPGA
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01],  # min 10ms
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.675],  # spend 75% on FPGA

        "FUNCTION_PLACEMENT_IS_COLDSTART": [True, False],

        "MAX_REQUESTS": [0],
        "NUM_NODES": [10],
        "FUNCTION_KEEPALIVE": [0, 30, 60, 120, 600],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],
        "SCHEDULER_WEIGHTS": [
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 2,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            },
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    # os.environ['ENABLE_LOGS'] = '1'
    results = run_benchmark(inputs)
    df = pd.DataFrame(results)
    df.to_csv(f"keepalive_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv")

    # df = pd.read_csv('keepalive_benchmark_results_20230619133015.csv')

    # plot a bar chart that shows the coldstart percent for different keepalive times

    def plot_results():
        # set figsize=(15, 5)
        plt.figure(figsize=(10, 3))

        ### placement is coldstart = True

        grouped = df[df['function_placement_is_coldstart'] == True].groupby(['function_keepalive'])[
            'coldstart_percent'].mean().reset_index()

        # use range(len(grouped)) to ensure equal spacing
        plt.bar(range(len(grouped)), grouped['coldstart_percent'], width=0.5, color='blue', alpha=0.4, label='Placement + FPGA reconfiguration')

        # for every entry, add a text label within the bar at the top
        for i, row in grouped.iterrows():
            # center the text label above the bar
            plt.text(i, row['coldstart_percent'] - 5, f'{round(row["coldstart_percent"], 2)}%',
                     horizontalalignment='center', verticalalignment='top')

        ### placement is coldstart = False

        # only consider the first set of results (coldstart=True)
        grouped = df[df['function_placement_is_coldstart'] == False].groupby(['function_keepalive'])['coldstart_percent'].mean().reset_index()

        # use range(len(grouped)) to ensure equal spacing
        plt.bar(range(len(grouped)), grouped['coldstart_percent'], width=0.5, color='blue', alpha=0.6, label='FPGA reconfiguration only')

        # for every entry, add a text label above the bar
        for i, row in grouped.iterrows():
            # center the text label above the bar
            plt.text(i, row['coldstart_percent'] - 5, f'{round(row["coldstart_percent"], 2)}%',
                     horizontalalignment='center', verticalalignment='top', color='white')

        # then set x-tick labels to 'function_keepalive' values
        plt.xticks(range(len(grouped)), grouped['function_keepalive'])

        # place legend below plot
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2)



        plt.xlabel('Keepalive Time (s)')
        plt.ylabel('Coldstart Percent')
        plt.title('Effects of Function Keepalive Time on Coldstart Percentages')

        # add legend for other assumptions, place in top right corner
        num_nodes = df['num_nodes'].unique()[0]
        num_fpga_slots_per_node = df['num_fpga_slots_per_node'].unique()[0]
        reconfiguration_time = round(df['fpga_reconfiguration_time'].unique()[0] * 1000)

        # text = f'{num_nodes} nodes, {num_fpga_slots_per_node} FPGA slots per node,\n{reconfiguration_time}ms reconfiguration time,\nequal scheduler weights'
        #plt.text(0.95, 0.85, text, horizontalalignment='right', verticalalignment='center',
        #         transform=plt.gca().transAxes)

        plt.tight_layout()

    plot_results()
    plt.show()

    # compare coldstart percent for different scheduler weights
    coldstart_difference = df.groupby(['function_keepalive'])['coldstart_percent'].median().reset_index()
    print(coldstart_difference)

    coldstart_difference = df.groupby(['function_keepalive'])['coldstart_percent'].median().reset_index()
    print(coldstart_difference)

    plot_results()
    plt.savefig(f'../../../figures/function_keepalive.png')
