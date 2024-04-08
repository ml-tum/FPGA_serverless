#!/usr/bin/env python3

import pandas as pd
import numpy as np
import re
import sys
from pathlib import Path
from typing import Any, List
from natsort import natsort_keygen
import warnings
import plot

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

TEST_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TEST_ROOT.parent.parent
MEASURE_RESULTS = TEST_ROOT.joinpath("measurements")

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

# hatches = ["", "..", "//"]
hatches = ["", "..", "**"]
hatches_mpk = ["", "**"]
hatch_base = hatches[0]
barheight = 0.5
app_height = 1.8

def sort(df: pd.DataFrame, systems: List[str], col = "system") -> pd.DataFrame:
    sparse = pd.concat([ df[df[col] == n] for n in systems ])
    return pd.concat([ sparse, df ]).drop_duplicates(keep='first')

def annotate_bar_values_s(g: Any):
    for c in g.ax.containers:
        labels = [f'   {(v.get_width()):.2f}s' for v in c]
        g.ax.bar_label(c, labels=labels, label_type='edge')

def annotate_bar_values_s2_ax(ax: Any, fontsize=7, rotation=0):
    for c in ax.containers:
        labels = [f'{(v.get_height()):.2f}s' for v in c]
        ax.bar_label(c, labels=labels, label_type='edge',
                     padding=2, fontsize=fontsize, rotation=rotation)

def annotate_bar_values_s2(g: Any):
    for c in g.ax.containers:
        labels = [f'{(v.get_height()):.2f}s' for v in c]
        g.ax.bar_label(c, labels=labels, label_type='edge',
                       padding=3, fontsize=5)

def annotate_bar_values_us(g: Any, offsets=None):
    for i, c in enumerate(g.ax.containers):
        if offsets is None:
            space = [' '*3]*len(c)
        else:
            space = [' '*s for s in offsets]
        labels = [f'{s}{(v.get_width()*1000*1000):.1f}us' for s,v in zip(space, c)]
        g.ax.bar_label(c, labels=labels, label_type='edge', fontsize=7)

def simple_bars(df: pd.DataFrame, name: str, names: List[str] = []) -> Any:
    if len(names) == 0: names = [name]

    width = 3.3
    aspect = 1.2
    ##g = df.plot(x="app", y="execution_times", kind="bar")
    g = catplot(
        data=df,
        y="app",
        x="execution_times",
        kind="bar",
        ci="sd",  # show standard deviation! otherwise with_stddev_to_long_form does not work.
        height=width/aspect,
        aspect=aspect,
        palette=[col_base, col_base, palette[1], palette[2]],
    )
    g.ax.set_ylabel("Apps")
    g.ax.set_xlabel("Time (s)")
    g.ax.set_yticklabels(["AES", "GZIP", "SHA3", "NeWu"])
    # hatches = ["//", "..", "//|", "..|"]
    hatches = ["", "|", "..", "..|"]
    apply_hatch(g, patch_legend=False, hatch_list=hatches)
    ##annotate_bar_values_kB(g)
    g._legend.remove()
    ##g._legend.set_title("")
    ##sns.move_legend(g, "upper right", bbox_to_anchor=(0.77, 1.01), labelspacing=.2)
    # g.ax.set_xlim(0, 2500000)
    ##g.ax.set_xlim(0, 2800000)

    FONT_SIZE = 9
    g.ax.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(0, 0),
        xytext=(-20, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )
    g.ax.annotate(
        "",
        xycoords="axes points",
        xy=(-20-15, -25),
        xytext=(-20, -25),
        fontsize=FONT_SIZE,
        arrowprops=dict(arrowstyle="-|>", color="navy"),
    )

    g.despine()
    ##format(g.ax.xaxis, "useconds")
    return g

def stacked_bars(df: pd.DataFrame, name: str, names: List[str] = []) -> Any:
    if len(names) == 0: names = [name]

    print(df)
    width = 3.3
    aspect = 1.2
    g = df.plot(
        stacked=True,
        kind='barh',
        x='Index',
        color=[palette[1], col_base, palette[3], palette[2]],
    )
    #plt.gca().invert_yaxis()
    g.set_ylabel("Apps")
    g.set_xlabel("Time (s)")
    g.set_yticks(g.get_yticks());
    ##g.set_yticklabels(["AES", "GZIP", "SHA3", "NeWu"])
    ##g.set_yticklabels(["AES", "GZIP", "SHA3", "NeWu"])
    # hatches = ["//", "..", "//|", "..|"]
    hatches = ["", "/", "..", "*"]
    for bars, hatch in zip(g.containers, hatches):
        for bar in bars:
            bar.set_hatch(hatch)
            bar.set_edgecolor('k')
    ##apply_hatch(plt, patch_legend=False, hatch_list=hatches)
    ##annotate_bar_values_kB(g)
    ##g._legend.remove()
    ##g._legend.set_title("")
    ##sns.move_legend(g, "upper right", bbox_to_anchor=(0.77, 1.01), labelspacing=.2)
    # g.ax.set_xlim(0, 2500000)
    ##g.ax.set_xlim(0, 2800000)

    FONT_SIZE = 9
    g.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(0, 0),
        xytext=(-20, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )
    g.annotate(
        "",
        xycoords="axes points",
        xy=(-20-15, -25),
        xytext=(-20, -25),
        fontsize=FONT_SIZE,
        arrowprops=dict(arrowstyle="-|>", color="navy"),
    )

    ##g.despine()
    ##format(g.ax.xaxis, "useconds")
    return plt

def parse_app_system(df: pd.DataFrame) -> pd.DataFrame:
    def h(row: Any) -> Any:
        if "hyperloglog" in row.system:
            return "HyperLogLog"
        elif "corner" in row.system:
            return "Corner-Detection"
        elif "gzip" in row.system:
            return "Gzip"
        elif "newu" in row.system:
            return "NeWu"

    app = df.apply(h, axis=1)
    ret = df.assign(app=app)

    def k(row: Any) -> Any:
        if "-cpu" in row.system:
            return f"{row.app}-cpu"
        else:
            return f"{row.app}-fpga"

    devapp = ret.apply(k, axis=1)
    ret = ret.assign(devapp=devapp)

    def k(row: Any) -> Any:
        if "-cpu" in row.system:
            return f"cpu"
        else:
            return f"fpga"

    execdev = ret.apply(k, axis=1)
    ret = ret.assign(execdev=execdev)

    return ret

def images(df: pd.DataFrame, name: str, names: List[str] = []) -> Any:
    if len(names) == 0: names = [name]
    df = df.melt(id_vars=["Unnamed: 0"], var_name="system", value_name=f"exec-time")
    df = parse_app_system(df)
    df = df.sort_values(by="devapp", ascending=False)
    print(df)

    # df = pd.concat([ df[df["system"] == n] for n in names ])
    # df = df.append(dict(system=r"human", seconds=0.013), ignore_index=True)
    # sns.set(font_scale=1.1)
    # width = 2.8
    width = 3.3
    aspect = 1.2
    g = catplot(
        data=apply_aliases(df),
        y=column_alias("app"),
        # order=systems_order(df),
        x=column_alias(f"exec-time"),
        kind="bar",
        hue="execdev",
        height=width/aspect,
        aspect=aspect,
        palette=[col_base, palette[1]],
    )
    # apply_to_graphs(g.ax, False, 0.285)
    # g.ax.set_xscale("log")
    g.ax.set_ylabel("")
    g.ax.set_xlabel("Execution time (ms)")
    g.ax.set_yticklabels(df['app'].unique())
    # hatches = ["//", "..", "//|", "..|"]
    hatches = ["", "|", "..", "..|"]
    apply_hatch(g, patch_legend=True, hatch_list=hatches)
    g._legend.set_title("")
    sns.move_legend(g, "upper right", bbox_to_anchor=(0.87, 1.01), labelspacing=.2)
    # g.ax.set_xlim(0, 2500000)
    #g.ax.set_xlim(0, 2800000)

    FONT_SIZE = 9
    g.ax.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(-0, 0),
        xytext=(-65, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )
    g.ax.annotate(
        "",
        xycoords="axes points",
        xy=(-70-15, -25),
        xytext=(-70, -25),
        fontsize=FONT_SIZE,
        arrowprops=dict(arrowstyle="-|>", color="navy"),
    )

    g.despine()
    format(g.ax.xaxis, "kB")
    return g

def compute_ratio(x: pd.DataFrame) -> pd.Series:
    title = x.benchmark_title.iloc[0]
    scale = x.scale.iloc[0]
    native = x.value.iloc[0]
    if len(x.value) == 2:
        l = x.value.iloc[1]
    else:
        print(f"WARNING: found only values for {title} for {x.identifier.iloc[0]}")
        # FIXME
        import math

        l = math.nan
    if x.proportion.iloc[0] == "LIB":
        diff = l / native
        proportion = "lower is better"
    else:
        diff = native / l
        proportion = "higher is better"

    result = dict(
        title=x.title.iloc[0],
        benchmark_title=title,
        benchmark_group=x.benchmark_name,
        diff=diff,
        native=native,
        we=l,
        scale=scale,
        proportion=proportion,
    )
    return pd.Series(result, name="metrics")


CONVERSION_MAPPING = {
    "MB": 10e6,
    "KB": 10e3,
}

ALL_UNITS = "|".join(CONVERSION_MAPPING.keys())
UNIT_FINDER = re.compile(r"(\d+)\s*({})".format(ALL_UNITS), re.IGNORECASE)


def unit_replacer(matchobj: re.Match) -> str:
    """Given a regex match object, return a replacement string where units are modified"""
    number = matchobj.group(1)
    unit = matchobj.group(2)
    new_number = int(number) * CONVERSION_MAPPING[unit]
    return f"{new_number} B"


def sort_row(val: pd.Series) -> Any:
    return natsort_keygen()(val.apply(lambda v: UNIT_FINDER.sub(unit_replacer, v)))


def bar_colors_rainbow(graph: Any, df: pd.Series, num_colors: int) -> None:
    colors = sns.color_palette(n_colors=num_colors)
    groups = 0
    last_group = df[0].iloc[0]
    for i, patch in enumerate(graph.axes[0][0].patches):
        if last_group != df[i].iloc[0]:
            last_group = df[i].iloc[0]
            groups += 1
        patch.set_facecolor(colors[groups])


def bar_colors(graph: Any, colors) -> None:
    for i, patch in enumerate(graph.axes[0][0].patches):
        patch.set_facecolor(colors[i%len(colors)])


def sort_baseline_first(df: pd.DataFrame, baseline_system: str) -> pd.DataFrame:
    beginning = df[df["system"] == baseline_system]
    end = df[df["system"] != baseline_system]
    return pd.concat([beginning, end])

def main() -> None:

    if len(sys.argv) < 2:
        print(f"USAGE: {sys.argv[0]} graph.tsv...")

    for arg in sys.argv[1:]:
        tsv_path = Path(arg)
        df = pd.read_csv(tsv_path, sep="\t")
        assert isinstance(df, pd.DataFrame)
        name = tsv_path.stem

        if name.startswith("apps_in_bars"):
            graph = simple_bars(df, "execution_time")
        elif name.startswith("stacked_boot_times"):
            graph = stacked_bars(df, "Startup_time")
        elif name.startswith("cpu_vs_fpga"):
            graph = images(df, "Execution time CPU vs FPGA")
        elif name.startswith("flat_cpu_vs_fpga"):
            graph = images(df, "Execution time CPU vs FPGA")
        else:
            print(f"unhandled graph name: {tsv_path}", file=sys.stderr)
            sys.exit(1)

        fname = name + ".pdf"
        print(f"write {fname}")
        graph.savefig(MEASURE_RESULTS / name, bbox_inches='tight')
        graph.savefig(MEASURE_RESULTS / fname, bbox_inches='tight')

if __name__ == "__main__":
    # main_old()
    main()
