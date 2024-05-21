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

data = pd.DataFrame({},columns=['regions', 'iter', 'runtime_ms'])
dataBars = pd.DataFrame({},columns=['regions','runtime_ms'])

files = ["parallelism_20240518T120444.csv","parallelism_20240518T124215.csv","parallelism_20240518T130318.csv"]

df0 = pd.read_csv(files[0], sep=",")
df1 = pd.read_csv(files[1], sep=",")
df2 = pd.read_csv(files[2], sep=",")

df = pd.concat([df0,df1,df2])
df['runtime_ms'] = df['runtime_ns'] / int(1e6)


grouped = df.groupby(by=['regions','batch'])
for key, group in grouped:
    regions = key[0]
    values = sorted(group['runtime_ms'])
    for i,val in enumerate(values):
        newrow = pd.DataFrame([{'regions': regions, 'iter': i, 'runtime_ms': val}])
        data = pd.concat([data, newrow])


def lineplot(df: pd.DataFrame):
    width = 3.3
    aspect = 1.2
    g = sns.catplot(
        data = data,
        x = 'iter',
        y = 'runtime_ms',
        hue = 'regions',
        ci='sd',
        kind='point',
        markers=[".", "^","*"],
        #height=width/aspect,
        #aspect=aspect,
        palette="pastel",
        linewidth=0.5,
        markersize=3,
        #markeredgecolor="black",
        markerfacecolor="white"
    )
    g.ax.set_ylabel("Execution time, incl. waiting for slot [ms]")
    g.ax.set_xlabel("Invocation #")
    g.ax.set_xticklabels(['1'] + ['']*8 + ['10'] + ['']*9 + ['20'] + ['']*9 +['30'])
    hatches = ["", "..", "*"]
    apply_hatch(g, patch_legend=False, hatch_list=hatches)

    g.despine()
    return g


def simple_bars(df: pd.DataFrame):
    width = 3.3
    #aspect = 1.2
    #aspect = 2.4
    aspect = 2.4
    g = catplot(
        data=df,
        y = 'regions',
        x = 'runtime_ms',
        kind="bar",
        ci="sd",  # show standard deviation! otherwise with_stddev_to_long_form does not work.
        height=width/aspect,
        aspect=aspect,
        palette="pastel",
        orient="h",
        saturation=1
    )
    g.ax.set_xlabel("Time to completion [ms]")
    g.ax.set_ylabel("")
    g.ax.set_yticklabels(["1 region", "2 regions", "4 regions"])
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

graph = lineplot(df)
graph.figure.savefig("microbenchmark_parallelism_lines.pdf", bbox_inches='tight')

maxIter = data['iter'].max()
dataBars = data.query(f"iter=={maxIter}")
graph2 = simple_bars(dataBars)
graph2.figure.savefig("microbenchmark_parallelism_bars.pdf", bbox_inches='tight')
