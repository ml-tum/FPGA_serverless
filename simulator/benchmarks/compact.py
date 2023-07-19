import datetime
import multiprocessing

import matplotlib.pyplot as plt
import numpy as np
from benchmark import run_benchmark

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "MAX_REQUESTS": [0],
        "NUM_NODES": [10],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.3],
        "NUM_FPGA_SLOTS_PER_NODE": [2, 4],
        "SCHEDULER_WEIGHTS": [
            {
                "BITSTREAM_WEIGHT": 1,
                "UTILIZATION_WEIGHT": 1,
                "RECONFIGURATION_WEIGHT": 1,
            },
            {
                "BITSTREAM_WEIGHT": 0,
                "UTILIZATION_WEIGHT": 1,
                "RECONFIGURATION_WEIGHT": 1,
            }
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    df = run_benchmark(inputs)

    df.to_csv(f"benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv")

    # Group by 'num_nodes' and 'num_fpga_slots_per_node' and compute the mean 'coldstart_percent'
    grouped_df_num_fpga_slots = df.groupby(['scheduler_weights', 'num_fpga_slots_per_node'])['coldstart_percent'].mean().reset_index()
    grouped_df_function_keepalive = df.groupby(['scheduler_weights', 'function_keepalive'])['coldstart_percent'].mean().reset_index()

    # Create a pivot table for the data to organize for the bar chart
    pivot_df_num_fpga_slots = grouped_df_num_fpga_slots.pivot_table(values='coldstart_percent', index='scheduler_weights', columns='num_fpga_slots_per_node')
    pivot_df_function_keepalive = grouped_df_function_keepalive.pivot_table(values='coldstart_percent', index='scheduler_weights', columns='function_keepalive')

    # Plotting
    bar_width = 0.1
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))

    # Loop over each group of num_fpga_slots_per_node to create a bar for each
    for i, fpga_slot in enumerate(pivot_df_num_fpga_slots.columns):
        axs[0].bar(np.arange(len(pivot_df_num_fpga_slots.index)) + i * bar_width, pivot_df_num_fpga_slots[fpga_slot], width=bar_width,
               label=f'FPGA Slots: {fpga_slot}')

    def format_scheduling_weights(scheduler_weights):
        if scheduler_weights == "1-1-1":
            return "Bitstream Locality, Equal Utilization and Reconfiguration"
        if scheduler_weights == "0-1-1":
            return "No Bitstream Locality, Equal Utilization and Reconfiguration"
        return scheduler_weights

    axs[0].set_xlabel('Number of Nodes')
    axs[0].set_ylabel('Coldstart Percent')
    axs[0].set_xticks(np.arange(len(pivot_df_num_fpga_slots.index)) + bar_width / 2)
    axs[0].set_xticklabels([format_scheduling_weights(scheduler_weights) for scheduler_weights in pivot_df_num_fpga_slots.index])
    axs[0].legend()

    # Plot for 'function_keepalive'
    for i, keepalive in enumerate(pivot_df_function_keepalive.columns):
        axs[1].bar(np.arange(len(pivot_df_function_keepalive.index)) + i * bar_width, pivot_df_function_keepalive[keepalive], width=bar_width,
                   label=f'Keepalive: {keepalive}')

    axs[1].set_xlabel('Number of Nodes')
    axs[1].set_ylabel('Coldstart Percent')
    axs[1].set_xticks(np.arange(len(pivot_df_function_keepalive.index)) + bar_width / 2)
    axs[1].set_xticklabels(pivot_df_function_keepalive.index)
    axs[1].legend()

    plt.tight_layout()
    plt.show()
