import datetime
import os

import numpy as np

import simulator
import itertools
import multiprocessing
from tqdm import tqdm


def run_simulator(input):
    schedulerWeights = input["SCHEDULER_WEIGHTS"]

    nodes, apps, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing = simulator.run_on_file(
        FPGA_BITSTREAM_LOCALITY_WEIGHT=schedulerWeights["FPGA_BITSTREAM_LOCALITY_WEIGHT"],
        RECENT_FPGA_USAGE_TIME_WEIGHT=schedulerWeights["RECENT_FPGA_USAGE_TIME_WEIGHT"],
        RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=schedulerWeights["RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT"],

        CHARACTERIZED_FUNCTIONS=input["CHARACTERIZED_FUNCTIONS"]["value"],

        MAX_REQUESTS=input["MAX_REQUESTS"],
        NUM_NODES=input["NUM_NODES"],
        FUNCTION_KEEPALIVE=input["FUNCTION_KEEPALIVE"],
        FPGA_RECONFIGURATION_TIME=input["FPGA_RECONFIGURATION_TIME"],
        NUM_FPGA_SLOTS_PER_NODE=input["NUM_FPGA_SLOTS_PER_NODE"],
        FUNCTION_HOST_COLDSTART_TIME_MS=input.get("FUNCTION_PLACEMENT_IS_COLDSTART", False),

        ARRIVAL_POLICY=input.get("ARRIVAL_POLICY", False),

        FUNCTION_PLACEMENT_IS_COLDSTART=input.get("FUNCTION_PLACEMENT_IS_COLDSTART", False),

        csv_file_path="../resampled.csv",

        ENABLE_PROGRESS_LOGS=os.getenv("ENABLE_PROGRESS_LOGS", False),
        ENABLE_LOGS=os.getenv("ENABLE_LOGS", False),
    )

    return {
        "coldstarts": metrics['coldstarts'],
        "coldstart_percent": coldstart_percent,
        "time_spent_on_cold_starts": time_spent_on_cold_starts,
        "time_spent_processing": time_spent_processing,
        "nodes": len(nodes),
        "apps": len(apps),
        "arrival_policy": input.get("ARRIVAL_POLICY", False),
        "function_placements_per_node": metrics["function_placements_per_node"],
        "fpga_reconfigurations_per_node": metrics["fpga_reconfigurations_per_node"],
        "metrics_per_node_over_time": metrics["metrics_per_node_over_time"],
        "makespan": metrics["makespan"],
        "max_requests": input["MAX_REQUESTS"],
        "num_nodes": input["NUM_NODES"],
        "function_keepalive": input["FUNCTION_KEEPALIVE"],
        "fpga_reconfiguration_time": input["FPGA_RECONFIGURATION_TIME"],
        "num_fpga_slots_per_node": input["NUM_FPGA_SLOTS_PER_NODE"],
        "function_placement_is_coldstart": input.get("FUNCTION_PLACEMENT_IS_COLDSTART", False),

        "characterized_functions": input["CHARACTERIZED_FUNCTIONS"],

        "scheduler_weights": encode_scheduler_weights(schedulerWeights),
    }


def encode_scheduler_weights(scheduler_weights):
    return f"{scheduler_weights['FPGA_BITSTREAM_LOCALITY_WEIGHT']}-{scheduler_weights['RECENT_FPGA_USAGE_TIME_WEIGHT']}-{scheduler_weights['RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT']}"


def decode_scheduler_weights(scheduler_weights):
    scheduler_weights = scheduler_weights.split("-")
    return {
        "FPGA_BITSTREAM_LOCALITY_WEIGHT": float(scheduler_weights[0]),
        "RECENT_FPGA_USAGE_TIME_WEIGHT": float(scheduler_weights[1]),
        "RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT": float(scheduler_weights[2]),
    }


def run_benchmark(inputs):
    pool = multiprocessing.Pool(processes=8)

    inputs = [dict(zip(inputs, v)) for v in itertools.product(*inputs.values())]
    pbar = tqdm(total=len(inputs))

    results = []

    for result in pool.imap_unordered(run_simulator, inputs):
        results.append(result)
        pbar.update()

    pool.close()
    pool.join()

    pbar.close()

    # create table of results
    return results


def get_median_fpga_utilization(metrics_per_node_over_time):
    median = np.median(
        np.concatenate(
            [
                snapshot['fpga_usage_time']
                for snapshot in metrics_per_node_over_time
            ]
        )
    )

    return median


def apply_median_utilization(df):
    df['median_fpga_utilization'] = df['metrics_per_node_over_time'].apply(get_median_fpga_utilization)
