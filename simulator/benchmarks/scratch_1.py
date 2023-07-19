import pandas as pd
from benchmarks import benchmark

import simulator

input={
        "REQUEST_DURATION_FPGA_USAGE_RATIO": 1,
        "MAX_REQUESTS": 0,
        "NUM_NODES": 4,
        "FUNCTION_KEEPALIVE": 60,
        "FPGA_RECONFIGURATION_TIME": 0.3,
        "NUM_FPGA_SLOTS_PER_NODE": 4,

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": {
                "BITSTREAM_WEIGHT": 1,
                "UTILIZATION_WEIGHT": 1,
                "RECONFIGURATION_WEIGHT": 1,
            }
    }

nodes, apps, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing = simulator.run_on_file(
        FPGA_BITSTREAM_LOCALITY_WEIGHT=input["SCHEDULER_WEIGHTS"]["BITSTREAM_WEIGHT"],
        RECENT_FPGA_USAGE_TIME_WEIGHT=input["SCHEDULER_WEIGHTS"]["UTILIZATION_WEIGHT"],
        RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=input["SCHEDULER_WEIGHTS"]["RECONFIGURATION_WEIGHT"],

        MAX_REQUESTS=10000,
        NUM_NODES=input["NUM_NODES"],
        FUNCTION_KEEPALIVE=input["FUNCTION_KEEPALIVE"],
        FPGA_RECONFIGURATION_TIME=input["FPGA_RECONFIGURATION_TIME"],
        NUM_FPGA_SLOTS_PER_NODE=input["NUM_FPGA_SLOTS_PER_NODE"],
        REQUEST_DURATION_FPGA_USAGE_RATIO=input["REQUEST_DURATION_FPGA_USAGE_RATIO"],

        csv_file_path="../AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt",
    )

# Suppose your dictionary looks like this
your_dict = metrics["fpga_usage_per_node"]

print(your_dict)

# Convert dictionary to pandas Series
data = pd.Series(your_dict)

# Compute various statistics
median = data.median()
mean = data.mean()
q1 = data.quantile(0.25)
q3 = data.quantile(0.75)
min_val = data.min()
max_val = data.max()
std_dev = data.std()

print(f"Median: {median}")
print(f"Mean: {mean}")
print(f"First Quartile (Q1): {q1}")
print(f"Third Quartile (Q3): {q3}")
print(f"Minimum: {min_val}")
print(f"Maximum: {max_val}")
print(f"Standard Deviation: {std_dev}")