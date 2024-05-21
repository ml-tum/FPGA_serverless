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

df = pd.read_csv('./reconfig_time_20240509T153347.csv', sep=",")
df['runtime_ms'] = df['runtime_ns'] / int(1e6)

def simple_bars(df: pd.DataFrame):
    width = 3.3
    #aspect = 1.2
    aspect = 2.4
    g = catplot(
        data=df,
        y="always_reconfigure",
        x="runtime_ms",
        kind="bar",
        ci="sd",  # show standard deviation! otherwise with_stddev_to_long_form does not work.
        height=width/aspect,
        aspect=aspect,
        palette="pastel",
        orient="h",
        saturation=1
    )
    g.ax.set_xlabel("Execution time [ms]")
    g.ax.set_ylabel("")
    g.ax.set_yticklabels(["Re-use", "Reconfig"])
    hatches = ["", ".."]
    apply_hatch(g, patch_legend=False, hatch_list=hatches)

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
    return g

graph = simple_bars(df)
graph.savefig("microbenchmark_reconfig_time.pdf", bbox_inches='tight')
