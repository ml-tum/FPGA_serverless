import numpy as np
import pandas as pd
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
    ROW_ALIASES,
    COLUMN_ALIASES, 
    FORMATTER
)

df = pd.read_csv('./e2e_chaining_20240520T191825.csv', sep=",")
df['runtime_ms'] = df['runtime_ns'] / int(1e6)

def simple_bars(df: pd.DataFrame):
    width = 3.3
    #aspect = 1.2
    aspect = 2.4
    #aspect = 1.8
    g = catplot(
        data=df,
        y="scenario",
        x="runtime_ms",
        kind="bar",
        ci="sd",  # show standard deviation! otherwise with_stddev_to_long_form does not work.
        height=width/aspect,
        aspect=aspect,
        palette="pastel",
        orient="h",
        saturation=1
    )
    g.ax.set_xlabel("                 Execution time (ms)")
    g.ax.set_ylabel("")
    g.ax.set_yticklabels(["Client-side\npiping", "Server-side\npiping", "F3"])
    hatches = ["", "..", "*"]
    apply_hatch(g, patch_legend=False, hatch_list=hatches)

    FONT_SIZE = 9
    g.ax.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(0, 0),
        xytext=(-40, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )
    g.ax.annotate(
        "",
        xycoords="axes points",
        xy=(-40-15, -25),
        xytext=(-40, -25),
        fontsize=FONT_SIZE,
        arrowprops=dict(arrowstyle="-|>", color="navy"),
    )

    g.despine()
    return g

graph = simple_bars(df)
graph.savefig("e2e_benchmark_chaining.pdf", bbox_inches='tight')

print("Pipe avg: " + str(df.query('scenario == "pipe"')['runtime_ms'].mean()))
print("FD avg: " + str(df.query('scenario == "functiondirector"')['runtime_ms'].mean()))
print("Combined avg: " + str(df.query('scenario == "combined"')['runtime_ms'].mean()))
