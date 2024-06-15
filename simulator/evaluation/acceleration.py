import os
import json
import sys

import numpy as np

sys.path.append("../")
sys.path.append("../benchmarks")
sys.path.append("../../miscs/evaluation/")

import pandas as pd
from pathlib import Path

from benchmark import run_benchmark

import datetime

from plot import (
    apply_aliases,
    catplot,
    column_alias,
    explode,
    sns,
    PAPER_MODE,
    plt,
    mpl,
    format,
    magnitude_formatter,
    change_width,
    apply_hatch,
    apply_hatch2,
    apply_hatch_ax,
)
from plot import ROW_ALIASES, COLUMN_ALIASES, FORMATTER

from data import characterized_collection, percentage_acceleration

# - Figure~\ref{fig:acceleration} shows the results of this experiment
#   (plot description: boxplot for each combination with makespan reported as a separate number).
#   In this section, we evaluate the impact of accelerating a subset of the functions in a workload.
#   We consider the following subset of functions \todo{Define subset}
#   and their corresponding type as per Table~\ref{tab:benchmark_summary}.
#   We run several simulations using our trace with FCFS scheduling  and a cluster of $1000$ for each combination of functions,
#   ranging from all functions being always accelerated to none. We measure the makespan and latency statistics in each case.

TEST_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TEST_ROOT.parent.parent
MEASURE_RESULTS = TEST_ROOT

FORMATTER.update(
    {
        "iops": magnitude_formatter(3),
        "io_throughput": magnitude_formatter(6),
        "useconds": magnitude_formatter(-6),
        "kB": magnitude_formatter(3),
        "MB": magnitude_formatter(6),
        "krps": magnitude_formatter(3, offsetstring=True),
        "mrps": magnitude_formatter(6, offsetstring=True),
    }
)

if PAPER_MODE:
    out_format = ".pdf"
else:
    out_format = ".png"

palette = sns.color_palette("pastel")
col_base = palette[0]


def main() -> None:
    maxRequests = os.getenv("MAX_REQUESTS", "1000")

    accelerations = [
        {
            "label": "0%",
            "value": percentage_acceleration(0)
        },
        {
            "label": "25%",
            "value": percentage_acceleration(25)
        },
        {
            "label": "50%",
            "value": percentage_acceleration(50)
        },
        {
            "label": "75%",
            "value": percentage_acceleration(75)
        },
        {
            "label": "100%",
            "value": percentage_acceleration(100)
        }
    ]

    inputs = {
        # The following metrics are available:
        # METRICS_TO_RECORD = {
        # "coldstarts", number of cold starts
        # "makespan", total time spent on all computations and processing delays (waiting on slot to become available)
        # "request_duration", # sum of all request durations (accounting for speedup)
        # "fpga_reconfigurations_per_node", # map of all nodes, value is list of reconfiguration timestamps
        # "fpga_usage_per_node", # map with entry for each node and sum of time spent on fpga on this node
        # "requests_per_node", # number of requests per node
        # "request_duration_per_node", # sum of all request durations per node
        # "function_placements_per_node", # map of all nodes, value is list of function placement timestamps
        # "metrics_per_node_over_time", # utilization snapshots at different points in time
        # "latencies" # map for each request, value is (arrival_timestamp, processing_start_timestamp, response_timestamp, invocation_latency, duration_ms, delay)
        # }

        "METRICS_TO_RECORD": [{"latencies"}],

        "MAX_REQUESTS": [int(maxRequests)],
        "NUM_NODES": [1000],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [10],
        "NUM_FPGA_SLOTS_PER_NODE": [4],
        "FUNCTION_HOST_COLDSTART_TIME_MS": [100],

        # TODO Use realistic values based on findings from microbenchmarks
        "CHARACTERIZED_FUNCTIONS": accelerations,

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": [
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            }
        ]
    }

    run_on_file = os.getenv("PLOT_ON_RESULTS", "")
    if len(run_on_file) > 0:
        print("loading benchmark results from file, this may take a while")
        with open(run_on_file, "r") as f:
            results = json.load(f)
    else:
        print("starting benchmark")

        results = run_benchmark(inputs)
        with open(f"acceleration_figure_evaluation_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                  "w") as f:
            results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
            f.write(results_json)

    print("starting to prepare for plotting")

    df = pd.DataFrame(results)

    assert isinstance(df, pd.DataFrame)

    width = 3.3
    aspect = 1.2

    # replace characterized_functions with characterized_functions.label
    df["characterized_functions"] = df["characterized_functions"].apply(lambda x: x["label"])

    df.rename(columns={"characterized_functions": "Acceleration"}, inplace=True)

    # convert acceleration to int
    df["Acceleration"] = df["Acceleration"].apply(lambda x: int(x.replace("%", "")))

    # Assuming df is your original DataFrame
    df["latencies"] = df["latencies"].apply(lambda x: [y[3] for y in x.values()])

    df_expanded = df.explode('latencies').reset_index(drop=True)
    df_expanded['latencies'] = df_expanded['latencies'].astype(float)

    # Create the boxplot
    graph = sns.catplot(
        data=df_expanded,
        x="Acceleration",
        y="latencies",
        kind="box",
        height=width / aspect,
        aspect=aspect,
        palette=[col_base, palette[1], palette[2]],
        showfliers=False
    )

    graph.ax.set_ylabel("Latency in ms")
    graph.ax.set_xlabel("Acceleration")

    # add percent sign to x-axis
    graph.ax.set_xticklabels([f"{x}%" for x in range(0, 101, 25)])

    FONT_SIZE = 9
    graph.ax.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(0, 0),
        xytext=(-20, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
        arrowprops=dict(arrowstyle="-|>", color="navy"),
    )

    graph.despine()

    fname = "figure_acceleration" + ".pdf"
    graph.savefig(MEASURE_RESULTS / fname, bbox_inches='tight')


if __name__ == "__main__":
    main()
