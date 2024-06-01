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

from data import characterized_collection

# What we need to draw in this file :
# - Figure~\ref{fig:scalability} shows latency boxplots for the scale-out experiment as we increase the number of machines from $1$ to $1,000$ and increase slots on each machine from $1$ to $4$
#   (plot description: grouped boxplot of number of slots, increasing number of machines left to right).
#   As can be seen, the latency plots tighten as the cluster size increases, which is explained by a reduction in cold starts.

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
        # "metrics_per_node_over_time", #
        # "latencies"
        # }

        "METRICS_TO_RECORD": [{"latencies"}],

        "MAX_REQUESTS": [int(maxRequests)],
        "NUM_NODES": [1, 10, 25, 50, 100, 150, 250, 500, 1000, 2500, 5000, 10_000],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [10],
        "NUM_FPGA_SLOTS_PER_NODE": [1, 2, 4],
        "FUNCTION_HOST_COLDSTART_TIME_MS": [100],

        # TODO Use realistic values based on findings from microbenchmarks
        "CHARACTERIZED_FUNCTIONS": [
            {
                # strategy just refers to a list of characterized functions sourced from benchmarks
                "label": "Characterized Functions",
                "value": characterized_collection()
            }
        ],

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
        with open(f"scalability_figure_evaluation_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                  "w") as f:
            results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
            f.write(results_json)

    print("starting to prepare for plotting")

    df = pd.DataFrame(results)

    assert isinstance(df, pd.DataFrame)

    width = 3.3
    aspect = 1.2

    df.rename(columns={"num_fpga_slots_per_node": "FPGA Slots per Node"}, inplace=True)

    # Assuming df is your original DataFrame
    df["latencies"] = df["latencies"].apply(lambda x: [y[3] for y in x.values()])

    df_expanded = df.explode('latencies').reset_index(drop=True)
    df_expanded['latencies'] = df_expanded['latencies'].astype(float)

    # Create the boxplot
    graph = sns.catplot(
        data=df_expanded,
        x="nodes",
        y="latencies",
        hue="FPGA Slots per Node",
        kind="box",
        height=width / aspect,
        aspect=aspect,
        palette=[col_base, palette[1], palette[2]],
        showfliers=False
    )

    graph.ax.set_ylabel("Latency in ms")
    graph.ax.set_xlabel("Number of Nodes")

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

    fname = "figure_scalability" + ".pdf"
    graph.savefig(MEASURE_RESULTS / fname, bbox_inches='tight')


if __name__ == "__main__":
    main()
