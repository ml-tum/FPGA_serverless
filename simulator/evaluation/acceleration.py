import datetime
import os
import json
import sys

sys.path.append("../")
sys.path.append("../benchmarks")
sys.path.append("../../miscs/evaluation/")

import pandas as pd
from pathlib import Path

from benchmark import run_benchmark

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

# What we need to draw in this file :
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
# palette = sns.color_palette("colorblind")
# palette = [palette[-1], palette[1], palette[2]]
col_base = palette[0]

notAccelerated = {
    # strategy just refers to a list of characterized functions sourced from benchmarks
    "label": "Not Accelerated",
    "value": {
        # these are characterized functions
        1: {
            # an average function that benefits somewhat from being on the FPGA
            "label": "f1",
            "mean_speedup": 1,  # 100% of original duration
            "run_on_fpga": False,
            "fpga_ratio": 0,
            "characterization": {
                "avg_req_per_sec": 1,
                "avg_req_duration": 50,
            }
        },
    }
}

fullyAccelerated = {
    # strategy just refers to a list of characterized functions sourced from benchmarks
    "label": "Fully Accelerated",
    "value": {
        # these are characterized functions
        1: {
            # an average function that benefits somewhat from being on the FPGA
            "label": "f1",
            "mean_speedup": 1,  # 80% of original duration
            "run_on_fpga": True,
            "fpga_ratio": 1,
            "characterization": {
                "avg_req_per_sec": 1,
                "avg_req_duration": 50,
            }
        },
    }
}


def main() -> None:
    maxRequests = os.getenv("MAX_REQUESTS", "1000")
    inputs = {
        "MAX_REQUESTS": [int(maxRequests)],
        "NUM_NODES": [1000],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],
        "FUNCTION_HOST_COLDSTART_TIME_MS": [100],

        # TODO Use realistic values based on findings from microbenchmarks
        "CHARACTERIZED_FUNCTIONS": [
            notAccelerated,
            fullyAccelerated
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
        with open(f"acceleration_figure_evaluation_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                  "w") as f:
            results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
            f.write(results_json)

    print("starting to prepare for plotting")

    df = pd.DataFrame(results)

    assert isinstance(df, pd.DataFrame)

    # replace characterized_functions with characterized_functions.label
    df["characterized_functions"] = df["characterized_functions"].apply(lambda x: x["label"])

    width = 3.3
    aspect = 1.2

    graph = catplot(
        data=df,
        x="characterized_functions",
        y="makespan",
        kind="point",
        errorbar="sd",
        height=width / aspect,
        aspect=aspect,
        linestyle="none",
        # palette=[col_base, palette[1]], # , col_base, palette[1], palette[2]
    )
    graph.ax.set_ylabel("Makespan")
    graph.ax.set_xlabel("Acceleration Strategy")
    # graph.ax.set_yticklabels(["AES", "GZIP", "SHA3", "NeWu"])
    # hatches = ["//", "..", "//|", "..|"]
    # hatches = ["", "|", "..", "..|"]
    # apply_hatch(g, patch_legend=False, hatch_list=hatches)
    ##annotate_bar_values_kB(g)
    # graph._legend.remove()
    ##graph._legend.set_title("")
    ##sns.move_legend(g, "upper right", bbox_to_anchor=(0.77, 1.01), labelspacing=.2)
    # graph.ax.set_xlim(0, 2500000)
    ##graph.ax.set_xlim(0, 2800000)

    FONT_SIZE = 9
    graph.ax.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(0, 0),
        xytext=(-20, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )
    # graph.ax.annotate(
    #     "",
    #     xycoords="axes points",
    #     xy=(-20-15, -25),
    #     xytext=(-20, -25),
    #     fontsize=FONT_SIZE,
    #     arrowprops=dict(arrowstyle="-|>", color="navy"),
    # )

    graph.despine()
    ##format(g.ax.xaxis, "useconds")

    fname = "figure_acceleration"
    graph.savefig(MEASURE_RESULTS / fname, bbox_inches='tight')


if __name__ == "__main__":
    main()
