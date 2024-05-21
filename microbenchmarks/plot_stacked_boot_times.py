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


def stacked_bars(df: pd.DataFrame):
    width = 3.7
    aspect = 2.8
    g = df.plot(
        stacked=True,
        kind='barh',
        x='Index',
        color=sns.color_palette("pastel"),
        figsize=(width,width/aspect),
        width=0.75
    )
    g.aspect = aspect
    g.set_ylabel("")
    g.set_xlabel("Time [ms]")
    #g.set_xlim((0,3000))
    hatches = ["", "..", "*", "o"]
    #apply_hatch(g, patch_legend=False, hatch_list=hatches)
    for bars, hatch in zip(g.containers, hatches):
        for bar in bars:
            bar.set_hatch(hatch)
            bar.set_edgecolor('k')

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

    g.legend(prop={'size': 7})

    sns.despine(ax=g)
    return plt



df = pd.read_csv('./stacked_boot_times.tsv', sep="\t")
order = ['Funky','Docker','Kata-containers']
mapping = {day: i for i, day in enumerate(order)}
key = df['Index'].map(mapping)
df = df.iloc[key.argsort()]
df.replace('Funky', 'F3',inplace=True)
df.replace('Kata-containers', 'Kata\ncontainers',inplace=True)


graph = stacked_bars(df)
graph.savefig("microbenchmark_stacked_boot_times.pdf", bbox_inches='tight')
