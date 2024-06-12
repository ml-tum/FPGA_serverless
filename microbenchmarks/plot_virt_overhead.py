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

def parse_ov_system(df: pd.DataFrame) -> pd.DataFrame:
    def h(row):
        if "FPGA_alloc" in row.system:
            return "call_fpga_acc"
        elif "FPGA_exec" in row.system:
            return "call_fpga_acc"
        elif "FPGA_release" in row.system:
            return "wait_fpga_acc"

    app = df.apply(h, axis=1)
    ret = df.assign(app=app)

    def k(row):
        if "-native" in row.system:
            return f"{row.app}-native"
        else:
            return f"{row.app}-unikernel"

    devapp = ret.apply(k, axis=1)
    ret = ret.assign(devapp=devapp)

    def k(row):
        if "-native" in row.system:
            return f"native"
        else:
            return f"unikernel"

    execdev = ret.apply(k, axis=1)
    ret = ret.assign(execdev=execdev)
    return ret


def virt_ov(df: pd.DataFrame, name: str, names: [str] = []):
    if len(names) == 0: names = [name]
    print(df)
    df = df.melt(id_vars=["Unnamed: 0"], var_name="system", value_name=f"exec-time")
    print(df)
    df = parse_ov_system(df)
    print(df)
    df = df.sort_values(by="devapp")
    print(df)
    df=apply_aliases(df)
    print(df)
    df['exec-time'] *= 1000
    print(df)

    width = 3.3
    aspect = 2.4
    g = catplot(
        data=apply_aliases(df),
        y=column_alias("app"),
        # order=systems_order(df),
        x=column_alias(f"exec-time"),
        kind="bar",
        hue="execdev",
        height=width/aspect,
        aspect=aspect,
        palette='pastel',
        saturation=1
    )

    g.ax.set_ylabel("")
    g.ax.set_xlabel("Execution time (µs)")
    g.ax.set_yticklabels(df['app'].unique())
    hatches = ["", ".."]
    apply_hatch(g, patch_legend=True, hatch_list=hatches)

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

    g._legend.set(visible=False)
    g.ax.legend(prop={'size': 7}, loc='right', bbox_to_anchor=(1,0.275))

    g.despine()
    return g


df = pd.read_csv('./virt_overhead.tsv', sep="\t")

#merge 'alloc' and 'exec'
df['FPGA_exec-native'] += df['FPGA_alloc-native']
df['FPGA_exec-unikernel'] += df['FPGA_alloc-unikernel']
df = df.drop(columns=['FPGA_alloc-native', 'FPGA_alloc-unikernel'])

graph = virt_ov(df, "Virtualization overhead")
graph.savefig("microbenchmark_virt_overhead.pdf", bbox_inches='tight')
