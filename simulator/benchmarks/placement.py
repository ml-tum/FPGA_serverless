import multiprocessing
import os

import matplotlib.pyplot as plt
from benchmark import run_benchmark,encode_scheduler_weights
import pandas as pd

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        # for this illustration, we spend all requests on fpga
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5],
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01],
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.75],

        # runs on a subset for easier comprehension
        "MAX_REQUESTS": [2000],
        "NUM_NODES": [40],
        "FUNCTION_KEEPALIVE": [30],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": [
            {
                # bitstream locality works against equal distribution, so we do not consider it in this benchmark
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 2,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            },
            {
                # bitstream locality works against equal distribution, so we do not consider it in this benchmark
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 0,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 0,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 0,
            },
        ]
    }

    results = run_benchmark(inputs)
    df = pd.DataFrame(results)


    def prep_data(filtered_df):
        data = []
        nodes = filtered_df['function_placements_per_node'].values[0].keys()
        for node in nodes:
            timestamps = filtered_df['function_placements_per_node'].values[0][node]
            for timestamp in timestamps:
                data.append({'node': node, 'start': timestamp})

        placements = pd.DataFrame(columns=['node', 'start'], data=data)

        placements = placements.sort_values('node', ascending=False)

        return placements

    def plot_timeline(title, placements, ax):
        # Create a list of functions
        earliest_placement = placements['start'].min()
        latest_placement = placements['start'].max()

        for node in range(inputs['NUM_NODES'][0]):
            node_data = placements[placements['node'] == node]
            if len(node_data) == 0:
                # plot gray line for node
                ax.plot([earliest_placement, latest_placement], [node] * 2, color='lightgray')
            else:
                ax.plot(
                    node_data['start'],
                    [node] * len(node_data),
                    label=node,
                    marker='o',
                    # set marker size to 2
                    # markersize=4,
                    # set line width to 1
                    # linewidth=1,
                )


        ax.set_yticks(range(inputs['NUM_NODES'][0]))
        # invert y axis
        ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_xlabel('Time')
        ax.set_ylabel('Nodes')
        ax.set_title(title)
        # make sure x axis is nice
        plt.gcf().autofmt_xdate()

    df_utilization_based = df[df['scheduler_weights'] == encode_scheduler_weights(inputs['SCHEDULER_WEIGHTS'][0])]
    placements_utilization_based = prep_data(df_utilization_based)

    print("Utilization based")
    print(placements_utilization_based.describe())

    df_naive = df[df['scheduler_weights'] == encode_scheduler_weights(inputs['SCHEDULER_WEIGHTS'][1])]
    placements_naive = prep_data(df_naive)

    print("Naive")
    print(placements_naive.describe())


    def render():
        fig, axs = plt.subplots(1, 2, figsize=(10, 8))
        fig.suptitle('Function placement timeline')
        plt.tight_layout()
        plot_timeline('Baseline function placement', placements_naive, axs[0])
        plot_timeline('FPGA-aware function placement', placements_utilization_based, axs[1])

    render()
    plt.show()

    render()
    if inputs["MAX_REQUESTS"][0] == 20_000:
        plt.savefig('../../../figures/extended_placement_timeline.png')
    else:
        plt.savefig('../../../figures/placement_timeline.png')
