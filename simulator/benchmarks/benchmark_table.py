import pandas as pd
import pylatex

if __name__ == "__main__":
    # inputs = {
    #     "MAX_REQUESTS": [1000, 0],
    #     "NUM_NODES": [1, 5, 10, 15, 20],
    #     "FUNCTION_KEEPALIVE": [None, 60, 60 * 60, 60 * 60 * 24],
    #     "FPGA_RECONFIGURATION_TIME": [0.3, 0.01],
    #     "NUM_FPGA_SLOTS_PER_NODE": [2, 4, 8, 16],
    # }

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5],  # 50% of requests run on FPGA
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01],  # min 10ms
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.75],  # spend 75% on FPGA

        "MAX_REQUESTS": [0],
        "NUM_NODES": [10, 20, 40],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": [
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 1,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 1,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 0,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 0,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 0,
            },
        ]
    }

    # results = run_benchmark(inputs)
    # df.to_csv(f"benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv")

    results = pd.read_csv("benchmark_results_20230617182215.csv")
    df = pd.DataFrame(results)
    print("COLD STARTS")

    grouped = df.groupby(['nodes', 'scheduler_weights'])[["coldstart_percent"]].median()
    print(grouped)
    # print differences in cold start percent between baseline and FPGA-aware scheduler

    coldstart_difference = df.groupby(['nodes', 'scheduler_weights'])[["coldstart_percent"]].median().unstack().diff(axis=1).iloc[:, -1]

    print(coldstart_difference)



