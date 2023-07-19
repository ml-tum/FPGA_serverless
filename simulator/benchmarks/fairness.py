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
import scipy
import scipy.stats as st

from benchmark import run_benchmark
import pandas as pd

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)

    inputs = {
        "REQUEST_RUN_ON_FPGA_PERCENTAGE": [0.5],  # 50% of requests run on FPGA
        "REQUEST_RUN_ON_FPGA_MIN_DURATION": [0.01],  # min 10ms
        "REQUEST_DURATION_FPGA_USAGE_RATIO": [0.75],  # spend 75% of the real utilization on FPGA

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
    # with open(f"fairness_benchmark_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w") as f:
    #     results_json = json.dumps(results, indent=4, sort_keys=True, default=str)
    #     f.write(results_json)

    # load results from json file
    with open("fairness_benchmark_results_20230705114144.json", "r") as f:
        results = json.load(f)

    df = pd.DataFrame(results)


    def format_scheduling_weights(scheduler_weights):
        if scheduler_weights == "0-0-0":
            return "Baseline"
        if scheduler_weights == "1-2-2":
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

            fpga_usage_times_mean = fpga_usage_times.mean()
            if fpga_usage_times_mean > 0:
                fpga_usage_time_cov = fpga_usage_times.std() / fpga_usage_times.mean()
            else:
                fpga_usage_time_cov = 0

            fpga_reconfiguration_times_mean = fpga_reconfiguration_times.mean()
            if fpga_reconfiguration_times_mean > 0:
                fpga_reconfiguration_time_cov = fpga_reconfiguration_times.std() / fpga_reconfiguration_times.mean()
            else:
                fpga_reconfiguration_time_cov = 0

            time_series.append({
                'timestamp': timestamp,
                # median over all nodes first
                'fpga_usage_time_median': fpga_usage_times.median(),
                'fpga_usage_time_std': fpga_usage_times.std(),
                'fpga_usage_time_cov': fpga_usage_time_cov,
                'fpga_usage_time_p95': fpga_usage_times.quantile(0.95),
                'fpga_usage_time_p99': fpga_usage_times.quantile(0.99),
                'fpga_reconfiguration_time_median': fpga_reconfiguration_times.median(),
                'fpga_reconfiguration_time_cov': fpga_reconfiguration_time_cov,
                'fpga_reconfiguration_time_std': fpga_reconfiguration_times.std(),
                'fpga_reconfiguration_time_p95': fpga_reconfiguration_times.quantile(0.95),
                'fpga_reconfiguration_time_p99': fpga_reconfiguration_times.quantile(0.99),
                'baseline_utilization_time_median': baseline_utilization_times.median(),
                'baseline_utilization_time_p95': baseline_utilization_times.quantile(0.95),
                'baseline_utilization_time_p99': baseline_utilization_times.quantile(0.99),
                'baseline_utilization_time_std': baseline_utilization_times.std(),
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
        print("var(fpga_usage_time_median)")
        print(df_time_series['fpga_usage_time_median'].var())

        print("median(fpga_usage_time_std)")
        print(df_time_series['fpga_usage_time_std'].median())

        print("cov(fpga_usage_time_std)")
        print(df_time_series['fpga_usage_time_cov'].median())

        data_lines.append((schedulerWeights, df_time_series, df_time_series_node_based))
        fpga_usage_times_across_runs.append((schedulerWeights, fpga_usage_times_per_run))

    # sort fpga_usage_times_across by scheduler weights ascending
    fpga_usage_times_across_runs.sort(key=lambda x: x[0])

    baseline_utilization_times_across_runs = fpga_usage_times_across_runs[0][1]
    fpga_aware_utilization_times_across_runs = fpga_usage_times_across_runs[1][1]

    old_usage_time_cov = data_lines[0][1]['fpga_usage_time_cov'].median()
    new_usage_time_cov = data_lines[1][1]['fpga_usage_time_cov'].median()
    usage_time_cov_diff = (new_usage_time_cov - old_usage_time_cov) / old_usage_time_cov

    old_reconfiguration_time_cov = data_lines[0][1]['fpga_reconfiguration_time_cov'].median()
    new_reconfiguration_time_cov = data_lines[1][1]['fpga_reconfiguration_time_cov'].median()
    reconfiguration_time_cov_diff = (
                                            new_reconfiguration_time_cov - old_reconfiguration_time_cov) / old_reconfiguration_time_cov

    # create a comparison table between baseline and fpga-aware for std and cov
    tbl = pd.DataFrame({
        'metric': ['cov(usage time)', 'cov(reconfiguration time)'],
        'Baseline': [old_usage_time_cov, old_reconfiguration_time_cov],
        'FPGA-aware': [new_usage_time_cov, new_reconfiguration_time_cov],
        '$\\Delta$': [f"{usage_time_cov_diff * 100:.2f}\\%", f"{reconfiguration_time_cov_diff * 100:.2f}\\%"],
    })
    # set table name to "Dispersion in FPGA usage time"
    tbl = tbl.set_index('metric')
    tbl.index.name = 'Dispersion of FPGA utilization'

    print(tbl)
    tbl.to_latex(
        buf="../../../figures/fpga-utilization-dispersion.tex",
        escape=False,
        float_format="%.2f",
    )
