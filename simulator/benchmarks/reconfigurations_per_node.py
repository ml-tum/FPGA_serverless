import datetime
import json
import multiprocessing
import os
import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas

from tabulate import tabulate

from benchmark import run_benchmark
import pandas as pd

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5],  # 50% of requests run on FPGA
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01],  # min 10ms
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.75],  # spend 75% on FPGA

        "MAX_REQUESTS": [0],
        "NUM_NODES": [10, 20, 40],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": [
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 0,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 0,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 0,
            },
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    # results = run_benchmark(inputs)
    # with open(f"reconfigurations_per_node_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
    #     results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
    #     f.write(results_json)

    # load results from json file
    with open("reconfigurations_per_node_benchmark_results_20230704103812.json", "r") as f:
        results = json.load(f)

    df = pd.DataFrame(results)

    # print cold start percent grouped by nodes, scheduler_weights
    print("COLD STARTS")
    print(df.groupby(['nodes', 'scheduler_weights'])[["coldstart_percent"]].median())
    # print differences in cold start percent between baseline and FPGA-aware scheduler
    print(df.groupby(['nodes', 'scheduler_weights'])[["coldstart_percent"]].median().unstack().diff(axis=1).iloc[:, -1])
    # print differences in percent
    group_diffs = df.groupby(['nodes', 'scheduler_weights'])[["coldstart_percent"]].median().unstack().diff(
        axis=1).iloc[:, -1] / df.groupby(['nodes', 'scheduler_weights'])[["coldstart_percent"]].median().unstack().iloc[
                              :, 0]
    print(group_diffs)

    # group df by nodes, then calculate median of fpga_reconfigurations_per_node for each group
    for index, row in df.iterrows():
        # stored as a dict in the format of {"node_id": [datetime_str, ...]}
        fpga_reconfigurations_per_node = row['fpga_reconfigurations_per_node']

        # convert to a dict of {"node_id": len([datetime_str, ...])}
        fpga_reconfigurations_per_node = {node_id: len(reconfigurations) for node_id, reconfigurations in
                                          fpga_reconfigurations_per_node.items()}

        # calculate median
        median = np.median(list(fpga_reconfigurations_per_node.values()))

        # store median in df
        df.at[index, 'fpga_reconfigurations_per_node_median'] = median

    print("FPGA RECONFIGURATIONS PER NODE")

    # group df by nodes, then calculate median of fpga_reconfigurations_per_node for each group
    print(df.groupby(['nodes', 'scheduler_weights'])['fpga_reconfigurations_per_node_median'].median())

    # for each subgroup, calculate the difference in percentage between the baseline and the FPGA-aware scheduler
    print(df.groupby(['nodes', 'scheduler_weights'])['fpga_reconfigurations_per_node_median'].median().unstack().diff(
        axis=1).iloc[:, -1])
    # print relative difference
    group_diffs = df.groupby(['nodes', 'scheduler_weights'])[
                      'fpga_reconfigurations_per_node_median'].median().unstack().diff(axis=1).iloc[:, -1] / \
                  df.groupby(['nodes', 'scheduler_weights'])[
                      'fpga_reconfigurations_per_node_median'].median().unstack().iloc[:, 0]
    print(group_diffs)


    def format_scheduling_weights(scheduler_weights):
        if scheduler_weights == "0-0-0":
            return "Baseline"
        if scheduler_weights == "1-2-2":
            return "FPGA-aware"
        return scheduler_weights


    def plot_utilization():
        fig, ax = plt.subplots(figsize=(10, 4))

        ax.set_title('FPGA reconfigurations per node')
        ax.set_ylabel('FPGA reconfigurations per node')

        # iterate over df rows
        for index, row in df.iterrows():
            # stored as a dict in the format of {"node_id": [datetime_str, ...]}
            fpga_reconfigurations_per_node = row['fpga_reconfigurations_per_node']

            # convert to a dict of {"node_id": len([datetime_str, ...])}
            fpga_reconfigurations_per_node = {node_id: len(reconfigurations) for node_id, reconfigurations in
                                              fpga_reconfigurations_per_node.items()}

            # plot aggregate as boxplot
            ax.boxplot(
                fpga_reconfigurations_per_node.values(),
                positions=[index],
                widths=0.6,
                labels=[
                    f"{format_scheduling_weights(row['scheduler_weights'])} {'({}%)'.format(round(group_diffs[row['nodes']] * 100, 2)) if row['scheduler_weights'] == '1-2-2' else ''}"],
                patch_artist=True,
                boxprops=dict(facecolor="blue", color="black", alpha=0.7),
                medianprops=dict(color="white"),
            )

            if index % 2 == 0:
                # render index in the middle of the two boxplots
                current_pos = index
                next_pos = current_pos + 1
                middle = (current_pos + next_pos) / 2
                ax.text(
                    middle, 0, '{} nodes'.format(row['nodes']), ha='center')

        plt.tight_layout()


    plot_utilization()
    plt.show()

    plot_utilization()
    plt.savefig(f'../../../figures/fpga_reconfigurations_per_node.png')

    df['Nodes'] = df['nodes']
    df['Scheduler Weights'] = df['scheduler_weights']
    df['Cold Start \\%'] = df['coldstart_percent']
    df['FPGA Reconfigurations Per Node'] = df['fpga_reconfigurations_per_node_median']

    rows = ""
    # group by number of nodes, then iterate over rows
    for nodes, group in df.groupby(['nodes']):
        fpga_reconfigurations_per_node_baseline = \
            group[group['scheduler_weights'] == '0-0-0']['fpga_reconfigurations_per_node_median'].iloc[0]
        fpga_reconfigurations_per_node_fpga_aware = \
            group[group['scheduler_weights'] == '1-2-2']['fpga_reconfigurations_per_node_median'].iloc[0]
        fps_diff = (
                           fpga_reconfigurations_per_node_fpga_aware - fpga_reconfigurations_per_node_baseline) / fpga_reconfigurations_per_node_baseline

        coldstart_percent_baseline = group[group['scheduler_weights'] == '0-0-0']['coldstart_percent'].iloc[0]
        coldstart_percent_fpga_aware = group[group['scheduler_weights'] == '1-2-2']['coldstart_percent'].iloc[0]
        coldstart_percent_diff = (
                                         coldstart_percent_fpga_aware - coldstart_percent_baseline) / coldstart_percent_baseline

        # get number of nodes
        num_nodes = group['nodes'].iloc[0]

        rows += f"{num_nodes} & {fpga_reconfigurations_per_node_baseline:.2f} & {fpga_reconfigurations_per_node_fpga_aware:.2f} & {fps_diff * 100:.2f}\\% & {coldstart_percent_baseline:.2f}\\% & {coldstart_percent_fpga_aware:.2f}\\% & {coldstart_percent_diff * 100:.2f}\\% \\\\\n"

    full_latex = """\\begin{tabular}{l|rrr|rrr}
\\toprule
& \multicolumn{3}{c}{FPGA reconfigurations per node} & \multicolumn{3}{c}{Cold start \%} \\\\
Nodes & Baseline & FPGA-aware & $\\Delta$ & Baseline & FPGA-aware & $\\Delta$ \\\\
\\midrule
""" + rows + """
\\bottomrule
\\end{tabular}"""

    with open('../../../figures/benchmark_results.tex', 'w') as f:
        f.write(full_latex)
