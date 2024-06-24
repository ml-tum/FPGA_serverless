import os

import newrelic.agent
import random
import preprocess
from collections import deque

from process import process_row
from util import create_node


@newrelic.agent.function_trace()
def run_on_file(
        csv_file_path='AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt',

        CHARACTERIZED_FUNCTIONS_LABEL="",
        CHARACTERIZED_FUNCTIONS=None,

        # system parameters
        NUM_NODES=10, NUM_FPGA_SLOTS_PER_NODE=2, FPGA_RECONFIGURATION_TIME=10,
        FUNCTION_KEEPALIVE=60 * 60 * 12, MAX_REQUESTS=100_000, FUNCTION_HOST_COLDSTART_TIME_MS=100,

        # logging
        ENABLE_LOGS=False,
        ENABLE_PROGRESS_LOGS=False,
        ENABLE_PRINT_RESULTS=False,

        # arrival policy (FIFO, PRIORITY)
        ARRIVAL_POLICY="FIFO",

        # scheduler weights
        RECENT_FPGA_USAGE_TIME_WEIGHT=1, RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=1, FPGA_BITSTREAM_LOCALITY_WEIGHT=1,

        # in the production system, we do not use scale to zero so functions are already
        # placed on nodes before their first invocation, thus placement is not part of the cold start
        # if scale to zero is assumed, functions might have to be placed just in time, adding to the cold start
        FUNCTION_PLACEMENT_IS_COLDSTART=False,

        METRICS_TO_RECORD: set = None,

        RECORD_PRIORITY_LATENCIES: bool = False,

        ACCELERATE_REQUESTS: float = 0
):
    if METRICS_TO_RECORD is None:
        METRICS_TO_RECORD = {"coldstarts", "request_duration",
                             "fpga_reconfigurations_per_node", "fpga_usage_per_node", "requests_per_node",
                             "request_duration_per_node", "function_placements_per_node", "metrics_per_node_over_time",
                             "latencies"}

    FPGA_RECONFIGURATION_TIME_MS = FPGA_RECONFIGURATION_TIME

    commitHash = os.getenv("COMMIT_HASH", "unknown")

    newrelic.agent.add_custom_attributes([
        ("COMMIT_HASH", commitHash),
        ("CHARACTERIZED_FUNCTIONS_LABEL", CHARACTERIZED_FUNCTIONS_LABEL),
        ("NUM_NODES", NUM_NODES),
        ("NUM_FPGA_SLOTS_PER_NODE", NUM_FPGA_SLOTS_PER_NODE),
        ("FPGA_RECONFIGURATION_TIME", FPGA_RECONFIGURATION_TIME),
        ("FUNCTION_KEEPALIVE", FUNCTION_KEEPALIVE),
        ("MAX_REQUESTS", MAX_REQUESTS),
        ("FUNCTION_HOST_COLDSTART_TIME_MS", FUNCTION_HOST_COLDSTART_TIME_MS),
        ("ARRIVAL_POLICY", ARRIVAL_POLICY),
        ("RECENT_FPGA_USAGE_TIME_WEIGHT", RECENT_FPGA_USAGE_TIME_WEIGHT),
        ("RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT", RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT),
        ("FPGA_BITSTREAM_LOCALITY_WEIGHT", FPGA_BITSTREAM_LOCALITY_WEIGHT),
        ("ENABLE_LOGS", ENABLE_LOGS),
        ("ENABLE_PROGRESS_LOGS", ENABLE_PROGRESS_LOGS),
        ("ENABLE_PRINT_RESULTS", ENABLE_PRINT_RESULTS),
        ("FUNCTION_PLACEMENT_IS_COLDSTART", FUNCTION_PLACEMENT_IS_COLDSTART),
        ("METRICS_TO_RECORD", METRICS_TO_RECORD),
        ("RECORD_PRIORITY_LATENCIES", RECORD_PRIORITY_LATENCIES),
        ("ACCELERATE_REQUESTS", ACCELERATE_REQUESTS),
    ])

    # stable random seed for reproducibility
    random.seed(42)

    nodes = {}
    functions = {}

    metrics = {
        # global counters, cannot be disabled
        'requests': 0,

        # metrics that can be disabled
        'coldstarts': 0,

        'request_duration': 0,

        'fpga_reconfigurations_per_node': {},
        'fpga_usage_per_node': {},
        'requests_per_node': {},
        'request_duration_per_node': {},
        'function_placements_per_node': {},
        'metrics_per_node_over_time': [],

        'latencies': {}
    }

    for i in range(NUM_NODES):
        created_node = create_node(nodes, NUM_FPGA_SLOTS_PER_NODE, ARRIVAL_POLICY)

    if ENABLE_LOGS:
        print("Loading traces")

    # load traces from disk
    traces = preprocess.load_traces(csv_file_path, MAX_REQUESTS)

    if ENABLE_LOGS:
        print(f"Loaded {len(traces)} traces, now preprocessing")

    # characterize individual functions (make sure every trace has an assigned function)
    preprocess.characterize_traces(CHARACTERIZED_FUNCTIONS, traces)

    # on list of traces in original order, apply arrival policy (i.e. re-order based on priority or other metric)
    traces = preprocess.apply_arrival_policy(traces, ARRIVAL_POLICY, CHARACTERIZED_FUNCTIONS)

    if ENABLE_LOGS:
        print("Preprocessed traces")

    previous_request_timestamp = {
        'start': None,
        'end': None
    }

    recently_used_nodes = {}

    node_timer = dict()
    for i in range(NUM_NODES):
        node_timer[i] = {
            "time": None
        }

    waiting = deque()

    num_traces = len(traces)
    while True:
        if len(traces) == 0 and len(waiting) == 0:
            break

        waiting_req = waiting.popleft() if len(waiting) > 0 else None
        if waiting_req is None:
            # "pull" next available request
            fntype, row, end_timestamp = traces.popleft()
        else:
            fntype, row, end_timestamp = waiting_req

        characterized_function = CHARACTERIZED_FUNCTIONS.get(fntype)

        def add_to_wait():
            waiting.appendleft((fntype, row, end_timestamp))

        # every 0.2% of max requests, record function trace (so we end up with 500 traces)
        if num_traces > 500 and metrics['requests'] % (num_traces // 500) == 0:
            with newrelic.agent.FunctionTrace(name="process_row"):
                newrelic.agent.add_custom_span_attribute("request_index", metrics['requests'])

                res = process_row(
                    row_is_traced=True,
                    nodes=nodes,
                    recently_used_nodes=recently_used_nodes,
                    functions=functions,
                    characterized_function=characterized_function,
                    row=row,
                    metrics=metrics,
                    previous_request_timestamp=previous_request_timestamp,
                    node_timer=node_timer,
                    add_to_wait=add_to_wait,
                    MAX_REQUESTS=MAX_REQUESTS,
                    FUNCTION_KEEPALIVE=FUNCTION_KEEPALIVE,
                    NUM_FPGA_SLOTS_PER_NODE=NUM_FPGA_SLOTS_PER_NODE,
                    ENABLE_LOGS=ENABLE_LOGS,
                    FPGA_RECONFIGURATION_TIME_MS=FPGA_RECONFIGURATION_TIME_MS,
                    ENABLE_PROGRESS_LOGS=ENABLE_PROGRESS_LOGS,
                    RECENT_FPGA_USAGE_TIME_WEIGHT=RECENT_FPGA_USAGE_TIME_WEIGHT,
                    RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                    FPGA_BITSTREAM_LOCALITY_WEIGHT=FPGA_BITSTREAM_LOCALITY_WEIGHT,
                    FUNCTION_PLACEMENT_IS_COLDSTART=FUNCTION_PLACEMENT_IS_COLDSTART,
                    FUNCTION_HOST_COLDSTART_TIME_MS=FUNCTION_HOST_COLDSTART_TIME_MS,
                    METRICS_TO_RECORD=METRICS_TO_RECORD,
                    RECORD_PRIORITY_LATENCIES=RECORD_PRIORITY_LATENCIES,
                    ARRIVAL_POLICY=ARRIVAL_POLICY,
                    ACCELERATE_REQUESTS=ACCELERATE_REQUESTS
                )
        else:
            res = process_row(
                row_is_traced=False,
                nodes=nodes,
                recently_used_nodes=recently_used_nodes,
                functions=functions,
                characterized_function=characterized_function,
                row=row,
                metrics=metrics,
                previous_request_timestamp=previous_request_timestamp,
                node_timer=node_timer,
                add_to_wait=add_to_wait,
                MAX_REQUESTS=MAX_REQUESTS,
                FUNCTION_KEEPALIVE=FUNCTION_KEEPALIVE,
                NUM_FPGA_SLOTS_PER_NODE=NUM_FPGA_SLOTS_PER_NODE,
                ENABLE_LOGS=ENABLE_LOGS,
                FPGA_RECONFIGURATION_TIME_MS=FPGA_RECONFIGURATION_TIME_MS,
                ENABLE_PROGRESS_LOGS=ENABLE_PROGRESS_LOGS,
                RECENT_FPGA_USAGE_TIME_WEIGHT=RECENT_FPGA_USAGE_TIME_WEIGHT,
                RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT=RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                FPGA_BITSTREAM_LOCALITY_WEIGHT=FPGA_BITSTREAM_LOCALITY_WEIGHT,
                FUNCTION_PLACEMENT_IS_COLDSTART=FUNCTION_PLACEMENT_IS_COLDSTART,
                FUNCTION_HOST_COLDSTART_TIME_MS=FUNCTION_HOST_COLDSTART_TIME_MS,
                METRICS_TO_RECORD=METRICS_TO_RECORD,
                RECORD_PRIORITY_LATENCIES=RECORD_PRIORITY_LATENCIES,
                ARRIVAL_POLICY=ARRIVAL_POLICY,
                ACCELERATE_REQUESTS=ACCELERATE_REQUESTS
            )

        if res is False:
            break

    # post-processing: compute makespan
    metrics["makespan"] = compute_makespan(metrics['latencies'])

    if "coldstarts" not in METRICS_TO_RECORD:
        print(
            "Warning: coldstarts not recorded in metrics, coldstart_percent, time_spent_on_cold_starts will be incorrect")

    coldstart_percent = round((metrics['coldstarts'] / metrics['requests']) * 100, 2)

    if ENABLE_PRINT_RESULTS:
        print("Coldstarts: {} ({}%), Nodes: {}".format(metrics['coldstarts'], coldstart_percent, len(nodes)))

    time_spent_on_cold_starts = round((metrics['coldstarts'] * FPGA_RECONFIGURATION_TIME) / 60 / 60, 2)

    if "request_duration" not in METRICS_TO_RECORD:
        print(
            "Warning: request_duration not recorded in metrics, time_spent_processing will be incorrect")

    time_spent_processing = round(metrics['request_duration'] / 60 / 60, 2)

    if ENABLE_PRINT_RESULTS:
        print("Time spent on coldstarts {}h, time spent processing {}h".format(time_spent_on_cold_starts,
                                                                               time_spent_processing))

    print(
        f"Finishing run, num nodes: {NUM_NODES}, num FPGA slots: {NUM_FPGA_SLOTS_PER_NODE}, recent FPGA usage time weight: {RECENT_FPGA_USAGE_TIME_WEIGHT}, recent FPGA reconfiguration time weight: {RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT}, FPGA bitstream locality weight: {FPGA_BITSTREAM_LOCALITY_WEIGHT}, arrival policy: {ARRIVAL_POLICY}, characterized functions label: {CHARACTERIZED_FUNCTIONS_LABEL}")

    newrelic.agent.add_custom_attributes([
        ("coldstarts", metrics['coldstarts']),
        ("coldstart_percent", coldstart_percent),
        ("time_spent_on_cold_starts", time_spent_on_cold_starts),
        ("time_spent_processing", time_spent_processing),
        ("nodes", len(nodes)),
        ("apps", len(functions)),
        ("makespan", metrics["makespan"]),
    ])

    return nodes, functions, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing


def compute_makespan(latencies: dict):
    # Step 1: Extract and sort intervals
    intervals = [
        # (processing_start_timestamp, response_timestamp)
        (data[1], data[2]) for data in latencies.values()
    ]
    intervals.sort(key=lambda x: x[0])

    # Step 2: Merge intervals
    merged_intervals = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end:  # Overlapping intervals
            current_end = max(current_end, end)
        else:  # Non-overlapping interval, push current interval to merged_intervals
            merged_intervals.append((current_start, current_end))
            current_start, current_end = start, end

    # Add the last interval
    merged_intervals.append((current_start, current_end))

    # Step 3: Calculate makespan
    makespan = sum((end - start).total_seconds() for start, end in merged_intervals)

    makespan_ms = makespan * 1000

    return makespan_ms
