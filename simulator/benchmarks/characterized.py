import json

from matplotlib import pyplot as plt

from benchmark import run_benchmark
import datetime
import pandas as pd

if __name__ == "__main__":
    inputs = {
        "MAX_REQUESTS": [0],
        "NUM_NODES": [10],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],

        "CHARACTERIZED_FUNCTIONS": [
            {
                # strategy just refers to a list of characterized functions sourced from benchmarks
                "label": "strat1",
                "value": {
                    # these are characterized functions
                    1: {
                        # an average function that benefits somewhat from being on the FPGA
                        "label": "f1",
                        "mean_speedup": 0.8,  # 80% of original duration
                        "run_on_fpga": True,
                        "fpga_ratio": 0.5,
                        "characterization": {
                            "avg_req_per_sec": 1,
                            "avg_req_duration": 50,
                        }
                    },
                    2: {
                        # a frequently-called function that somewhat benefits from being on the FPGA
                        "label": "f2",
                        "mean_speedup": 0.95,  # 95% of original duration
                        "run_on_fpga": True,
                        "fpga_ratio": 0.5,
                        "characterization": {
                            "avg_req_per_sec": 2,
                            "avg_req_duration": 10,
                        }
                    },
                    3: {
                        # a slow-running function that benefits strongly from being run on the FPGA
                        "label": "f3",
                        "mean_speedup": 0.5,  # 50% of original duration
                        "run_on_fpga": True,
                        "fpga_ratio": 0.8,
                        "characterization": {
                            "avg_req_per_sec": 1,
                            "avg_req_duration": 1000,
                        }
                    },
                }
            },
            {
                "label": "strat2",
                "value": {
                    1: {
                        "label": "f1",
                        "mean_speedup": 1,
                        "run_on_fpga": True,
                        "fpga_ratio": 0.5,
                        "characterization": {
                            "avg_req_per_sec": 1,
                            "avg_req_duration": 1,
                        }
                    },
                }
            }
        ],

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

    results = run_benchmark(inputs)
    with open(f"characterized_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
        results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
        f.write(results_json)

    df = pd.DataFrame(results)


    def format_characterized_functions(value):
        return value["label"]


    df['characterized_functions'] = df['characterized_functions'].apply(format_characterized_functions)

    grouped_df = df.groupby(['characterized_functions', 'scheduler_weights'])['coldstart_percent'].mean().reset_index()

    # Create a bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    # You can customize the appearance of the bar chart as per your preferences
    grouped_df.plot.bar(x='characterized_functions', y='coldstart_percent', ax=ax)

    # create second x-axis
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(ax.get_xticks())
    ax2.set_xticklabels(grouped_df['scheduler_weights'])

    # Set labels and title
    ax.set_yscale('log')
    ax.set_xlabel('Characterized Functions and Scheduler Weights')
    ax.set_ylabel('Cold Start Difference')
    plt.title('Difference in Cold Starts by Characterized Functions and Scheduler Weights')

    # Show the plot
    plt.show()
