import datetime
import json
import multiprocessing
import os
import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas
import matplotlib.ticker as mtick
from scipy.stats import norm

from benchmark import run_benchmark
import pandas as pd

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5], # 50% of requests run on FPGA
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01], # min 10ms
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.75], # spend 75% of the real utilization on FPGA

        "MAX_REQUESTS": [0],
        "NUM_NODES": [10],
        "FUNCTION_PLACEMENT_IS_COLDSTART": [False],
        "FUNCTION_KEEPALIVE": [60],
        "FPGA_RECONFIGURATION_TIME": [0.01],
        "NUM_FPGA_SLOTS_PER_NODE": [4],

        # testing variables ceteris paribus:
        "SCHEDULER_WEIGHTS": [
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 1,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 2,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 2,
            },
            {
                "FPGA_BITSTREAM_LOCALITY_WEIGHT": 0,
                "RECENT_FPGA_USAGE_TIME_WEIGHT": 0,
                "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": 0,
            },
        ]
    }

    # os.environ['ENABLE_PROGRESS_LOGS'] = '1'
    # results = run_benchmark(inputs)
    # with open(f"benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
    #     results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
    #     f.write(results_json)

    # load results from json file
    with open("benchmark_results_20230703215812.json", "r") as f: results = json.load(f)


    df = pd.DataFrame(results)


    def format_scheduling_weights(scheduler_weights):
        if scheduler_weights == "0-0-0":
            return "Baseline"
        if scheduler_weights == "1-1-1" or scheduler_weights == "2-2-2" or scheduler_weights == "3-3-3" or scheduler_weights == "4-4-4":
            return "FPGA-aware"
        return scheduler_weights

    fpga_usage_times_across_runs = []
    data_lines = []
    for _, benchmarkRun in df.iterrows():
        metricsTimeline = benchmarkRun['metrics_per_node_over_time']
        schedulerWeights = benchmarkRun['scheduler_weights']

        time_series = []

        # node-grouped usage time
        time_series_node_based = []

        # fpga usage time median for all nodes over time
        fpga_usage_times_per_run = []

        for snapshot in metricsTimeline:
            fpga_reconfiguration_times = pd.Series(snapshot['fpga_reconfiguration_time'])
            fpga_usage_times = pd.Series(snapshot['fpga_usage_time'])
            baseline_utilization_times = pd.Series(snapshot['baseline_utilization_time'])

            timestamp = snapshot['timestamp']

            # edge case if we run on loaded data from JSON (when datetime was converted to string already)
            # if timestamp is not datetime.datetime but string, convert to datetime.datetime
            # date is stored as 2021-01-31 01:00:00.001491
            if not isinstance(timestamp, datetime.datetime):
                timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

            time_series.append({
                'timestamp': timestamp,
                # median over all nodes first
                'fpga_usage_time_median': fpga_usage_times.median(),
                'fpga_usage_time_p95': fpga_usage_times.quantile(0.95),
                'fpga_usage_time_p99': fpga_usage_times.quantile(0.99),
                'fpga_reconfiguration_time_median': fpga_reconfiguration_times.median(),
                'fpga_reconfiguration_time_p95': fpga_reconfiguration_times.quantile(0.95),
                'fpga_reconfiguration_time_p99': fpga_reconfiguration_times.quantile(0.99),
                'baseline_utilization_time_median': baseline_utilization_times.median(),
                'baseline_utilization_time_p95': baseline_utilization_times.quantile(0.95),
                'baseline_utilization_time_p99': baseline_utilization_times.quantile(0.99),
            })

            fpga_usage_times_per_run.append(fpga_usage_times.median())

            for node_id, node_snapshot in enumerate(snapshot['fpga_usage_time']):
                time_series_node_based.append({
                    'timestamp': timestamp,
                    'node_id': node_id,
                    'fpga_usage_time': node_snapshot,
                })

        df_time_series = pd.DataFrame(time_series)
        df_time_series_node_based = pd.DataFrame(time_series_node_based)

        print(format_scheduling_weights(schedulerWeights))

        # then distribution of median over all nodes over time
        described = df_time_series['fpga_usage_time_median'].describe()
        described.name = f"Median FPGA usage ({schedulerWeights})"
        print(described)
        # described.to_latex(
        #     buf=f"../../../figures/median-{schedulerWeights}.tex",
        #     # escape percent signs
        #     escape=True,
        # )

        data_lines.append((schedulerWeights, df_time_series, df_time_series_node_based))
        fpga_usage_times_across_runs.append((schedulerWeights,fpga_usage_times_per_run))

    # sort fpga_usage_times_across by scheduler weights ascending
    fpga_usage_times_across_runs.sort(key=lambda x: x[0])

    baseline_utilization_times_across_runs = fpga_usage_times_across_runs[0][1]
    fpga_aware_utilization_times_across_runs = fpga_usage_times_across_runs[1][1]

    oldmedian = data_lines[0][1]['fpga_usage_time_median'].median()
    newmedian = data_lines[1][1]['fpga_usage_time_median'].median()

    # create table with mean, median, p95, p99 of old and new median, diff in median and diff in median in %
    tbl = pd.DataFrame()
    # distribution of median over all nodes over time
    tbl['Baseline'] = data_lines[0][1]['fpga_usage_time_median'].describe(percentiles=[0.25, 0.5, 0.75, 0.95, 0.99])
    tbl['FPGA-aware'] = data_lines[1][1]['fpga_usage_time_median'].describe(percentiles=[0.25, 0.5, 0.75, 0.95, 0.99])
    tbl['Difference'] = tbl['FPGA-aware'] - tbl['Baseline']
    tbl['Difference in \\%'] = tbl['Difference'] / tbl['Baseline'] * 100

    # bold font for median
    tbl.loc['50%'] = tbl.loc['50%'].apply(lambda x: "\\textbf{%.2f}" % x)

    # rename 25%, 50%, 75% to p25, p50, p75
    tbl = tbl.rename(index={'25%': 'p25', '50%': 'median', '75%': 'p75', '95%': 'p95', '99%': 'p99'})

    tbl.to_latex(
        buf="../../../figures/utilization-summary.tex",
        escape=False,
        float_format="%.2f",
    )

    # # median diff
    # median_diff = newmedian - oldmedian
    # median_percentage_diff = (newmedian - oldmedian) / oldmedian * 100
    #
    # diffseries = pd.Series([oldmedian,newmedian, median_diff, median_percentage_diff])
    # diffseries.index = ["Baseline median", "FPGA-aware median", "Difference in median", "Difference in median in %"]
    # diffseries.name = ""
    # diffseries.to_latex(
    #     buf="../../../figures/median-diff.tex",
    #     # escape percent signs
    #     escape=True,
    #
    # )


    # zip both together and subtract for differences
    differences_over_baseline = [fpga_aware_utilization_times_across_runs[i] - baseline_utilization_times_across_runs[i] for i in range(len(baseline_utilization_times_across_runs))]

    print("Differences in fpga usage times")
    print(differences_over_baseline)

    print("Median difference described")
    print(np.median(differences_over_baseline))
    print(pd.Series(differences_over_baseline).describe())

    differences_desc = pd.Series(differences_over_baseline).describe()
    differences_desc.name = "Difference in FPGA usage time"

    differences_desc.to_latex(
        buf="../../../figures/utilization.tex",
        # escape percent signs
        escape=True,
        float_format="%.2f",
    )

    diff_p1 = np.quantile(differences_over_baseline, 0.01)
    diff_p5 = np.quantile(differences_over_baseline, 0.05)
    diff_p25 = np.quantile(differences_over_baseline, 0.25)
    diff_p50 = np.quantile(differences_over_baseline, 0.50)
    diff_p75 = np.quantile(differences_over_baseline, 0.75)
    diff_p95 = np.quantile(differences_over_baseline, 0.95)
    diff_p99 = np.quantile(differences_over_baseline, 0.99)


    def plot_utilization():
        fig, axs = plt.subplots(1, 1, figsize=(8, 5))

        # for schedulerWeights, df_time_series, df_time_series_node_based in data_lines:
        #     axs[0].plot(df_time_series['timestamp'], df_time_series['fpga_usage_time_median'],
        #             label=f'median FPGA utilization ({format_scheduling_weights(schedulerWeights)})', linewidth=0.8)
        #
        # axs[0].set_title(f'Resource utilization comparison (log scale)')
        # axs[0].set_xlabel('Time')
        # axs[0].set_ylabel('FPGA resource utilization (seconds)')
        #
        # axs[0].set_xlim([datetime.datetime(2021, 1, 31, 1, 0, 0), datetime.datetime(2021, 2, 13, 1, 30, 0)])
        # axs[0].set_yscale('log')
        # # axs[0]s[0].set_ylim([0, 100])
        #
        # axs[0].legend()
        #
        # plt.gcf().autofmt_xdate()  # Rotation

        #
        # # render ticks nicely to not overlap
        # fig.autofmt_xdate()

        # # on second subplot, render histogram of differences_over_baseline
        # # normalize frequencies to 1
        weights = np.ones_like(differences_over_baseline)/float(len(differences_over_baseline))
        axs.hist(differences_over_baseline, weights=weights, bins=100, color='blue', alpha=0.7)
        # draw lines at 25%, 50%, 75%, 95%, 99% quantiles
        axs.axvline(diff_p5, color='black', linestyle='dashed', linewidth=1, label=f'p5 ({round(diff_p5,2)}s)')
        axs.axvline(diff_p25, color='red', linestyle='dashed', linewidth=1, label=f'p25 ({round(diff_p25,2)}s)')
        axs.axvline(diff_p50, color='orange', linestyle='dashed', linewidth=1, label=f'p50 ({round(diff_p50,2)}s)')
        axs.axvline(diff_p75, color='green', linestyle='dashed', linewidth=1, label=f'p75 ({round(diff_p75,2)}s)')
        axs.set_title('Resource utilization difference')
        axs.set_xlabel('Resource utilization difference (seconds)')
        axs.set_ylabel('Frequency')
        axs.set_xlim([-10, 10])
        # format y axis to percentage
        axs.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        axs.legend()

        fig.suptitle(f'FPGA resource utilization comparison (FPGA-aware vs. baseline)')

        plt.tight_layout()

    plot_utilization()
    plt.show()

    plot_utilization()
    plt.savefig(f'../../../figures/fpga_utilization_benchmark.png')
