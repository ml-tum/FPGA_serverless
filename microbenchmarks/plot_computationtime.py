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

df = pd.read_csv('./computation_time.csv', sep=", ")
df['runtime_ms'] = df['computation_time'] / int(1e6)
df.replace('c0', 'sha3', inplace=True)
df.replace('c4', 'nw', inplace=True)
df.replace('c8', 'hyperloglog', inplace=True)
df.replace('c9', 'corner', inplace=True)
df.replace('sha3', 'SHA3', inplace=True)
df.replace('hyperloglog', 'Hyper-\nloglog', inplace=True)
df.replace('corner', 'Corner \ndetection', inplace=True)
df.replace('nw', 'Needleman-\nWunsch', inplace=True)


def simple_bars(df: pd.DataFrame):
    width = 3.3
    #aspect = 1.2
    aspect = 1.4
    g = catplot(
        data=df,
        y="application",
        x="runtime_ms",
        hue="platform",
        kind="bar", 
        ci="sd",  # show standard deviation! otherwise with_stddev_to_long_form does not work.
        height=width/aspect,
        aspect=aspect,
        palette="pastel",
        orient="h",
        saturation=1
    )
    g.ax.set_xlabel("                           Computation time [ms]")
    g.ax.set_ylabel("")
    #g.set(xscale='log')
    #g.ax.set_yticklabels(["Re-use", "Reconfig"])
    hatches = ["", ".."]
    apply_hatch(g, patch_legend=False, hatch_list=hatches)

    FONT_SIZE = 9
    g.ax.annotate(
        "Lower is better",
        xycoords="axes points",
        xy=(0, 0),
        xytext=(-30, -27),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )
    g.ax.annotate(
        "",
        xycoords="axes points",
        xy=(-30-15, -25),
        xytext=(-30, -25),
        fontsize=FONT_SIZE,
        arrowprops=dict(arrowstyle="-|>", color="navy"),
    )

    g.ax.bar_label(g.ax.containers[-1], fmt='Mean:\n%.2f', label_type='edge')

    g.despine()
    return g


graph = simple_bars(df)

#mean_values = df.groupby(by=['application','platform'])['runtime_ms'].mean()
#for i, mean_val in enumerate(mean_values):
#    graph.ax.text(i, mean_val, f'{mean_val:.2f}', ha='center', va='bottom')


graph.savefig("microbenchmark_computation_time.pdf", bbox_inches='tight')
