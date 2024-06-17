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

df = pd.read_csv('./log_computation_time_intro_120624.csv', sep=", ")
df['runtime_ms'] = df['computation_time'] / int(1e6)

df.replace('c0', 'sha3', inplace=True)
df.replace('c4', 'nw', inplace=True)
df.replace('c8', 'hyperloglog', inplace=True)
df.replace('c9', 'corner', inplace=True)
df.replace('sha3', 'SHA3', inplace=True)
df.replace('hyperloglog', 'HLL', inplace=True)
df.replace('corner', 'HCD', inplace=True)
df.replace('nw', 'NW', inplace=True)

print("SHA3: " + str(df.query('platform=="fpga" and application.str.startswith("SHA3")')['runtime_ms'].mean()))
print("HLL: " + str(df.query('platform=="fpga" and application.str.startswith("HLL")')['runtime_ms'].mean()))
print("HCD: " + str(df.query('platform=="fpga" and application.str.startswith("HCD")')['runtime_ms'].mean()))
print("NW: " + str(df.query('platform=="fpga" and application.str.startswith("NW")')['runtime_ms'].mean()))

def simple_bars(df: pd.DataFrame):
    width = 3.3
    #aspect = 1.2
    aspect = 1.7

    g = catplot(
        data=df,
        x="application",
        y="runtime_ms",
        hue="platform",
        kind="bar", 
        ci="sd",  # show standard deviation! otherwise with_stddev_to_long_form does not work.
        height=width/aspect,
        aspect=aspect,
        palette="pastel",
        orient="v",
        saturation=1
    )
    g.ax.set_xlabel("")
    g.ax.set_ylabel("Execution time (ms)")
    #g.set(xscale='log')
    #g.ax.set_yticklabels(["Re-use", "Reconfig"])
    hatches = ["", ".."]
    apply_hatch(g, patch_legend=False, hatch_list=hatches)

    FONT_SIZE = 9
    g.ax.annotate(
        "↓ Lower is better",
        xycoords="axes fraction",
        xy=(0.2, 1),
        xytext=(0.2, 1),
        fontsize=FONT_SIZE,
        color="navy",
        weight="bold",
    )

    g.ax.annotate(
        "< 1",
        xycoords="axes points",
        xy=(73, 8),
        xytext=(73, 8),
        fontsize=FONT_SIZE-1,
        color="black",
    )
    g.ax.annotate(
        "< 2",
        xycoords="axes points",
        xy=(117, 8),
        xytext=(117, 8),
        fontsize=FONT_SIZE-1,
        color="black",
    )
    g.ax.annotate(
        "< 1 ms",
        xycoords="axes points",
        xy=(165, 8),
        xytext=(165, 8),
        fontsize=FONT_SIZE-1,
        color="black",
    )

    g.ax.legend(prop={'size': 7}, loc='right', bbox_to_anchor=(0.27,0.82))
    g._legend.set(visible=False)


    g.despine()
    return g


graph = simple_bars(df)

#mean_values = df.groupby(by=['application','platform'])['runtime_ms'].mean()
#for i, mean_val in enumerate(mean_values):
#    graph.ax.text(i, mean_val, f'{mean_val:.2f}', ha='center', va='bottom')



graph.savefig("microbenchmark_computation_time.pdf", bbox_inches='tight')
