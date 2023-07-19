import datetime

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('benchmark_results_20230602101916.csv')

# Group by 'num_nodes' and 'num_fpga_slots_per_node' and compute the mean 'coldstart_percent'
grouped_df = df.groupby(['num_nodes', 'num_fpga_slots_per_node'])['coldstart_percent'].mean().reset_index()

# Create a pivot table for the data to organize for the bar chart
pivot_df = grouped_df.pivot_table(values='coldstart_percent', index='num_nodes', columns='num_fpga_slots_per_node')

# Plotting
bar_width = 0.1
fig, ax = plt.subplots()

# Loop over each group of num_fpga_slots_per_node to create a bar for each
for i, fpga_slot in enumerate(pivot_df.columns):
    ax.bar(np.arange(len(pivot_df.index)) + i*bar_width, pivot_df[fpga_slot], width=bar_width, label=f'FPGA Slots: {fpga_slot}')

ax.set_xlabel('Number of Nodes')
ax.set_ylabel('Coldstart Percent')
ax.set_xticks(np.arange(len(pivot_df.index)) + bar_width / 2)
ax.set_xticklabels(pivot_df.index)
ax.legend()

plt.show()
plt.savefig(f'benchmark_results_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')
