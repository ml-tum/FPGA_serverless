import os

import newrelic.agent
import csv
import datetime
import random
import preprocess
from collections import deque

import usage


# Remove functions that are past the keepalive, keep bitstreams configured (no benefit in removing them)
def evict_inactive_functions(recently_used_nodes, functions, current_ts, FUNCTION_KEEPALIVE):
    for nodeIdx in recently_used_nodes:
        node = recently_used_nodes[nodeIdx]

        # remove functions that have expired
        nextFunctions = set()
        for functionName in node['functions']:
            function = functions.get(functionName)

            functionAge = (current_ts - function['last_invoked_at']).total_seconds()

            if functionAge <= FUNCTION_KEEPALIVE:
                # print("Function removed: {}".format(function['name']))
                nextFunctions.add(functionName)
            # TODO Make sure this works as expected
            else:
                function['last_node'] = None

        node['functions'] = nextFunctions
    pass


def create_node(nodes: dict, NUM_FPGA_SLOTS_PER_NODE=2):
    nextId = len(nodes)

    slots = {}
    for i in range(NUM_FPGA_SLOTS_PER_NODE):
        slots[i] = {
            'current_bitstream': None,
            'earliest_start_date': None,
        }

    new_node = {
        'id': nextId,
        'functions': set(),

        'bitstreams': set(),
        'fpga_slots': slots,

        'recent_baseline_utilization': usage.BaselineUtilizationTracker(),
        'recent_fpga_usage_time': usage.FPGAUsageTimeTracker(),
        'recent_fpga_reconfiguration_time': usage.FPGAReconfigurationTimeTracker(),
        'recent_fpga_reconfiguration_count': usage.FPGAReconfigurationCountTracker(),
    }
    nodes[len(nodes)] = new_node
    return new_node


# determine the best node to place a function on
# this function simulates the Kubernetes schedulers
def next_best_node(nodes: dict, functionName: str, recent_fpga_usage_time_weight,
                   recent_fpga_reconfiguration_time_weight, fpga_bitstream_locality_weight):
    if len(nodes) == 0:
        return None

    # if we have more than 100 nodes, take a random sample of 100 nodes
    if len(nodes) > 100:
        nodes_to_select_from = random.sample(list(nodes.keys()), 100)
    else:
        nodes_to_select_from = list(nodes.keys())

    prescored = []
    for nodeKey in nodes_to_select_from:
        node = nodes.get(nodeKey)

        # collect relevant criteria
        baseline_utilization = node['recent_baseline_utilization'].get_window_value()

        # recent FPGA utilization in seconds
        recent_utilization = node['recent_fpga_usage_time'].get_window_value()

        # recent reconfiguration times in seconds
        recent_reconfiguration_times = node['recent_fpga_reconfiguration_time'].get_window_value()

        has_fitting_bitstream = 0
        if functionName in node['bitstreams']:
            has_fitting_bitstream = 1

        score = (nodeKey, recent_utilization, recent_reconfiguration_times, has_fitting_bitstream, baseline_utilization)

        prescored.append(score)

    # sort utilization scores of all nodes in ascending order
    sorted_usage_time = prescored.copy()
    sorted_usage_time.sort(key=lambda x: x[1])

    # sort reconfiguration scores of all nodes in ascending order
    sorted_reconfiguration_time = prescored.copy()
    sorted_reconfiguration_time.sort(key=lambda x: x[2])

    sorted_baseline_utilization = prescored.copy()
    sorted_baseline_utilization.sort(key=lambda x: x[4])

    # calculate normalized to best scores
    scored = []
    for nodeKey, _, _, has_fitting_bitstream, _ in prescored:
        scored.append((nodeKey,
                       score_node(sorted_usage_time, sorted_reconfiguration_time, sorted_baseline_utilization, nodeKey,
                                  has_fitting_bitstream, recent_fpga_usage_time_weight,
                                  recent_fpga_reconfiguration_time_weight, fpga_bitstream_locality_weight)))

    # sort by score, highest first
    scored.sort(key=lambda x: x[1], reverse=True)
    # best node is first element
    best_node = scored[0][0]

    return nodes.get(best_node)


# create a normalized score for a node based on its utilization and reconfiguration times
def score_node(sorted_fpga_usage_time, sorted_fpga_reconfiguration_time, sorted_baseline_utilization, nodeId,
               has_fitting_bitstream, recent_fpga_usage_time_weight=1, recent_fpga_reconfiguration_time_weight=1,
               fpga_bitstream_locality_weight=1, baseline_utilization_weight=1):
    baseline_utilization_pos = None
    for i in range(len(sorted_baseline_utilization)):
        if sorted_baseline_utilization[i][0] == nodeId:
            baseline_utilization_pos = i
            break
    if baseline_utilization_pos is None:
        raise Exception("Node not found in sorted list")

    baseline_utilization_score = (len(sorted_baseline_utilization) - baseline_utilization_pos) / len(
        sorted_baseline_utilization)

    # find index of node in sorted list
    recent_fpga_usage_time_pos = None
    for i in range(len(sorted_fpga_usage_time)):
        if sorted_fpga_usage_time[i][0] == nodeId:
            recent_fpga_usage_time_pos = i
            break
    if recent_fpga_usage_time_pos is None:
        raise Exception("Node not found in sorted list")

    recent_fpga_usage_time_score = (len(sorted_fpga_reconfiguration_time) - recent_fpga_usage_time_pos) / len(
        sorted_fpga_usage_time)

    # find index of node in sorted list
    recent_fpga_reconfiguration_time_pos = None
    for i in range(len(sorted_fpga_reconfiguration_time)):
        if sorted_fpga_reconfiguration_time[i][0] == nodeId:
            recent_fpga_reconfiguration_time_pos = i
            break
    if recent_fpga_reconfiguration_time_pos is None:
        raise Exception("Node not found in sorted list")

    recent_fpga_reconfiguration_score = (
                                                len(sorted_fpga_reconfiguration_time) - recent_fpga_reconfiguration_time_pos) / len(
        sorted_fpga_reconfiguration_time)

    if recent_fpga_usage_time_weight + recent_fpga_reconfiguration_time_weight + fpga_bitstream_locality_weight == 0:
        return baseline_utilization_score

    # equally weigh normalized (between 0-1) criteria
    fpga_weight = (
                          recent_fpga_usage_time_weight + recent_fpga_reconfiguration_time_weight + fpga_bitstream_locality_weight) / 3
    fpga_score = (
                         recent_fpga_usage_time_weight * recent_fpga_usage_time_score + recent_fpga_reconfiguration_time_weight * recent_fpga_reconfiguration_score + fpga_bitstream_locality_weight * has_fitting_bitstream) / (
                         recent_fpga_usage_time_weight + recent_fpga_reconfiguration_time_weight + fpga_bitstream_locality_weight)

    weighted_score = (baseline_utilization_weight * baseline_utilization_score + fpga_weight * fpga_score) / (
            baseline_utilization_weight + fpga_weight)

    return weighted_score


# place a function on a node
def place_function(function, end_timestamp, functions, nodes, NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS,
                   RECENT_FPGA_USAGE_TIME_WEIGHT, RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                   FPGA_BITSTREAM_LOCALITY_WEIGHT):
    # lazily add function to state if not known (first invocation)
    if functions.get(function) is None:
        functions[function] = {
            'name': function,
            'last_invoked_at': end_timestamp,
            'last_node': None,
        }

    # check if function is deployed on any node
    deployed_on = None
    if functions[function]['last_node'] is not None:
        deployed_on = nodes.get(functions[function]['last_node'])

    is_function_placement = deployed_on is None

    if is_function_placement:
        # deploy function on next best node (run scheduler)
        deployed_on = next_best_node(nodes, function, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                     RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT, FPGA_BITSTREAM_LOCALITY_WEIGHT)
        if deployed_on is None:
            # no node has enough space, create new node
            deployed_on = create_node(nodes, NUM_FPGA_SLOTS_PER_NODE)

            if ENABLE_LOGS:
                print("New node created: {}".format(deployed_on['id']))

        deployed_on['functions'].add(function)
        functions[function]['last_node'] = deployed_on['id']
        # if ENABLE_LOGS:
        #     print("Function deployed on node: {}".format(deployed_on['id']))

    return deployed_on, is_function_placement


# acquire an FPGA slot for a function (place bitstream on node FPGA)
def acquire_fpga_slot(functions, nodes, metrics, node, functionName, processing_start_timestamp, response_timestamp,
                      global_timer, add_to_wait,
                      NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS, FPGA_RECONFIGURATION_TIME):
    # check if function is deployed on any FPGA slot, update last_invoked_at
    function = functions.get(functionName)

    slot = None
    slot_key = None

    # otherwise deploy
    needs_reconfiguration = functionName not in node['bitstreams']
    if needs_reconfiguration:
        # If all slots are occupied
        if len(node['bitstreams']) >= NUM_FPGA_SLOTS_PER_NODE:
            # Find slot with earliest done date
            earliest_start_date = None
            for slotIdx in node['fpga_slots']:
                current_slot = node['fpga_slots'][slotIdx]
                if earliest_start_date is None or earliest_start_date > current_slot['earliest_start_date']:
                    slot = current_slot
                    slot_key = slotIdx
                    earliest_start_date = current_slot['earliest_start_date']

            # If slot is not available at current time, wait until it is
            can_run_on_slot = earliest_start_date is None or earliest_start_date <= processing_start_timestamp
            if not can_run_on_slot:
                add_to_wait()

                # all requests must wait until earliest_start_date of the earliest available slot
                global_timer["time"] = earliest_start_date

                return None, None

            # "evict" previous bitstream from node
            if slot["current_bitstream"] is not None:
                node["bitstreams"].remove(slot["current_bitstream"])
                slot["current_bitstream"] = None
            slot["earliest_start_date"] = None
        else:
            # Find empty slot
            for slotIdx in node['fpga_slots']:
                if node['fpga_slots'][slotIdx]['current_bitstream'] is None:
                    slot = node['fpga_slots'][slotIdx]
                    slot_key = slotIdx
                    break

        # deploy function on next best FPGA slot
        node['bitstreams'].add(functionName)
        function['bitstream_started_at'] = processing_start_timestamp
        slot['current_bitstream'] = functionName
        slot['earliest_start_date'] = response_timestamp

        # coldstart if bitstream was not placed on this FPGA before
        # if ENABLE_LOGS:
        #     print("Added bitstream: {}, now at {}/{}: {}".format(functionName, len(node['bitstreams']),
        #                                                          NUM_FPGA_SLOTS_PER_NODE, node['bitstreams']))

        if metrics['fpga_reconfigurations_per_node'].get(node['id']) is None:
            metrics['fpga_reconfigurations_per_node'][node['id']] = [processing_start_timestamp]
        else:
            metrics['fpga_reconfigurations_per_node'][node['id']].append(processing_start_timestamp)

        node['recent_fpga_reconfiguration_count'].add(response_timestamp, 1)
        node['recent_fpga_reconfiguration_time'].add(response_timestamp, FPGA_RECONFIGURATION_TIME)

        # if ENABLE_LOGS:
        #     print("Coldstart for function {}, total {}".format(functionName, metrics['coldstarts']))
    else:
        # find slot
        for slotIdx in node['fpga_slots']:
            if node['fpga_slots'][slotIdx]['current_bitstream'] == functionName:
                slot_key = slotIdx
                break

    function['bitstream_last_invoked_at'] = response_timestamp
    nodes[node['id']] = node

    return needs_reconfiguration, slot_key


# Function to process each row of the CSV file
def process_row(
        nodes,
        recently_used_nodes,
        functions,
        characterized_function,
        row,
        metrics,
        MAX_REQUESTS: int,
        FUNCTION_KEEPALIVE: float,
        NUM_FPGA_SLOTS_PER_NODE: int,
        ENABLE_LOGS: bool,
        FPGA_RECONFIGURATION_TIME_MS: float,
        ENABLE_PROGRESS_LOGS: bool,
        RECENT_FPGA_USAGE_TIME_WEIGHT: float,
        RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT: float,
        FPGA_BITSTREAM_LOCALITY_WEIGHT: float,
        FUNCTION_PLACEMENT_IS_COLDSTART: bool,
        FUNCTION_HOST_COLDSTART_TIME_MS: float,
        previous_request_timestamp,
        global_timer: dict,
        add_to_wait: callable,
        row_is_traced: bool
):
    app, func, response_timestamp, duration = row

    # convert duration (seconds) to float
    duration = float(duration)
    if duration < 0:
        print("Invalid duration: {}".format(duration))
        return False

    # convert duration (seconds) to milliseconds
    duration_ms = duration * 1000

    # get original start timestamp
    arrival_timestamp = response_timestamp - datetime.timedelta(milliseconds=float(duration_ms))

    # adjust duration by expected acceleration
    duration_ms = duration_ms / characterized_function["mean_speedup"]

    # compute adjusted end timestamp
    response_timestamp = arrival_timestamp + datetime.timedelta(milliseconds=float(duration_ms))

    # start with no latency (we ignore network-related latency)
    invocation_latency = 0

    # by default, requests start on arrival (if not waiting)
    processing_start_timestamp = arrival_timestamp
    delay = 0

    # if request is waiting, it can only end after the previous request + its own duration
    request_is_waiting = global_timer["time"] is not None and global_timer["time"] > arrival_timestamp
    if request_is_waiting:
        processing_start_timestamp = global_timer["time"]  # start on earliest slot availability
        delay = (processing_start_timestamp - arrival_timestamp).total_seconds() * 1000
        metrics['makespan'] += delay
        invocation_latency += delay
        # adjust end timestamp to account for waiting time
        response_timestamp = processing_start_timestamp + datetime.timedelta(milliseconds=float(
            duration_ms))  # could also write this as end_timestamp + datetime.timedelta(seconds=delay)

    req_id = f"{app}-{func}-{arrival_timestamp}"

    def time_elapsed_since_previous_request(delta_seconds: int):
        return previous_request_timestamp['start'] is None or (
                arrival_timestamp - previous_request_timestamp['start']).total_seconds() > delta_seconds

    # we don't know how much time passed since last request so update host/slot occupancy (optimization: after 5s of last request)
    if FUNCTION_KEEPALIVE is not None and time_elapsed_since_previous_request(5):
        if row_is_traced:
            with newrelic.agent.FunctionTrace("evict_inactive_functions"):
                evict_inactive_functions(recently_used_nodes, functions, arrival_timestamp, FUNCTION_KEEPALIVE)
        else:
            evict_inactive_functions(recently_used_nodes, functions, arrival_timestamp,
                                     FUNCTION_KEEPALIVE)  # TODO Check if this needs to run always

    # decay utilization trackers every 30s
    if time_elapsed_since_previous_request(30):
        if row_is_traced:
            with newrelic.agent.FunctionTrace("update_trackers"):
                update_trackers(recently_used_nodes, response_timestamp, ENABLE_LOGS, True)
        else:
            update_trackers(recently_used_nodes, response_timestamp, ENABLE_LOGS, False)

    # limit requests to max for simulation
    if MAX_REQUESTS is not None and MAX_REQUESTS > 0 and metrics['requests'] > MAX_REQUESTS:
        print(f"Reached max requests ({metrics['requests']}), exiting")
        return False
    is_last_request = metrics['requests'] == MAX_REQUESTS

    metrics['requests'] += 1
    metrics['request_duration'] += duration_ms

    # if ENABLE_LOGS:
    #     time_spent_since_previous_request = 0
    #     if previous_request_timestamp is not None and previous_request_timestamp["end"] is not None:
    #         time_spent_since_previous_request = (start_timestamp - previous_request_timestamp["end"]).total_seconds()
    #     print("-- req; (+{}s) App: {}, Function: {}, Start Timestamp: {}, End Timestamp: {}, Duration: {}".format(
    #         time_spent_since_previous_request, app, func, start_timestamp, end_timestamp, duration))

    if ENABLE_PROGRESS_LOGS and metrics['requests'] % 1000 == 0:
        print("Requests: {}".format(metrics['requests']))

    if row_is_traced:
        with newrelic.agent.FunctionTrace("place_function"):
            deployed_on, is_function_placement = place_function(func, response_timestamp, functions, nodes,
                                                                NUM_FPGA_SLOTS_PER_NODE,
                                                                ENABLE_LOGS, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                                                RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                                                                FPGA_BITSTREAM_LOCALITY_WEIGHT)  # TODO Check if this needs to run always
    else:
        deployed_on, is_function_placement = place_function(func, response_timestamp, functions, nodes,
                                                            NUM_FPGA_SLOTS_PER_NODE,
                                                            ENABLE_LOGS, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                                            RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                                                            FPGA_BITSTREAM_LOCALITY_WEIGHT)  # TODO Check if this needs to run always

    if recently_used_nodes.get(deployed_on['id']) is None:
        recently_used_nodes[deployed_on['id']] = deployed_on

    # update metrics
    if is_function_placement:
        metrics['makespan'] += FUNCTION_HOST_COLDSTART_TIME_MS
        invocation_latency += FUNCTION_HOST_COLDSTART_TIME_MS
        if metrics['function_placements_per_node'].get(deployed_on['id']) is None:
            metrics['function_placements_per_node'][deployed_on['id']] = [arrival_timestamp]
        else:
            metrics['function_placements_per_node'][deployed_on['id']].append(arrival_timestamp)

    if metrics['requests_per_node'].get(deployed_on['id']) is None:
        metrics['requests_per_node'][deployed_on['id']] = 1
    else:
        metrics['requests_per_node'][deployed_on['id']] += 1

    if metrics['request_duration_per_node'].get(deployed_on['id']) is None:
        metrics['request_duration_per_node'][deployed_on['id']] = duration_ms
    else:
        metrics['request_duration_per_node'][deployed_on['id']] += duration_ms

    run_on_fpga = characterized_function["run_on_fpga"]

    if run_on_fpga:
        # keep processing request on fpga
        if row_is_traced:
            with newrelic.agent.FunctionTrace("acquire_fpga_slot"):
                needs_reconfiguration, slot_key = acquire_fpga_slot(functions, nodes, metrics, deployed_on, func,
                                                                    processing_start_timestamp,
                                                                    response_timestamp, global_timer, add_to_wait,
                                                                    NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS,
                                                                    FPGA_RECONFIGURATION_TIME_MS)  # TODO Check if this needs to run always
        else:
            needs_reconfiguration, slot_key = acquire_fpga_slot(functions, nodes, metrics, deployed_on, func,
                                                                processing_start_timestamp,
                                                                response_timestamp, global_timer, add_to_wait,
                                                                NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS,
                                                                FPGA_RECONFIGURATION_TIME_MS)  # TODO Check if this needs to run always

        if needs_reconfiguration:
            metrics['makespan'] += FPGA_RECONFIGURATION_TIME_MS
            invocation_latency += FPGA_RECONFIGURATION_TIME_MS

        if (FUNCTION_PLACEMENT_IS_COLDSTART and is_function_placement) or needs_reconfiguration:
            metrics['coldstarts'] += 1
    else:
        if FUNCTION_PLACEMENT_IS_COLDSTART and is_function_placement:
            metrics['coldstarts'] += 1

    # update utilization metrics
    fpga_ratio = characterized_function["fpga_ratio"] if run_on_fpga else 0
    time_spent_on_cpu = (1 - fpga_ratio) * duration_ms
    time_spent_on_fpga = fpga_ratio * duration_ms

    metrics['makespan'] += round(time_spent_on_cpu + time_spent_on_fpga, 2)
    invocation_latency += round(time_spent_on_cpu + time_spent_on_fpga, 2)

    deployed_on['recent_baseline_utilization'].add(response_timestamp,
                                                   time_spent_on_cpu)  # TODO Check if this needs to run always

    if run_on_fpga:
        deployed_on['recent_fpga_usage_time'].add(response_timestamp,
                                                  time_spent_on_fpga)  # TODO Check if this needs to run always

        if metrics['fpga_usage_per_node'].get(deployed_on['id']) is None:
            metrics['fpga_usage_per_node'][deployed_on['id']] = time_spent_on_fpga
        else:
            metrics['fpga_usage_per_node'][deployed_on['id']] += time_spent_on_fpga

    # only trigger this if 30 seconds have passed to avoid recording way too many data points
    if is_last_request or time_elapsed_since_previous_request(
            60 * 30):  # TODO Check if this arbitrary number is correct
        fpga_reconfiguration_times = [node['recent_fpga_reconfiguration_time'].get_window_value() for
                                      node in nodes.values()]
        fpga_usage_times = [node['recent_fpga_usage_time'].get_window_value() for node in nodes.values()]
        baseline_utilization_times = [node['recent_baseline_utilization'].get_window_value() for node in
                                      nodes.values()]

        metrics['metrics_per_node_over_time'].append({
            'timestamp': arrival_timestamp,
            'baseline_utilization_time': baseline_utilization_times,
            'fpga_reconfiguration_time': fpga_reconfiguration_times,
            'fpga_usage_time': fpga_usage_times,
        })
        previous_request_timestamp['start'] = arrival_timestamp
        previous_request_timestamp['end'] = response_timestamp

    # Immediately releasing means we have to coldstart for every request
    # release_fpga_slot(functions, nodes, deployed_on, function, end_timestamp, ENABLE_LOGS)

    metrics['latencies'][req_id] = (
        arrival_timestamp, processing_start_timestamp, response_timestamp, invocation_latency, duration_ms, delay)

    return True


def update_trackers(recently_used_nodes, end_timestamp, ENABLE_LOGS, row_is_traced: bool):
    if row_is_traced:
        newrelic.agent.add_custom_span_attribute("recently_used_nodes", len(recently_used_nodes))

    # instead of decaying all nodes, decay nodes that have recent usage and reset after this
    for node in recently_used_nodes.values():
        node['recent_baseline_utilization'].decay(end_timestamp)

        node['recent_fpga_usage_time'].decay(end_timestamp)
        node['recent_fpga_reconfiguration_count'].decay(end_timestamp)
        node['recent_fpga_reconfiguration_time'].decay(end_timestamp)

    recently_used_nodes.clear()


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
        FUNCTION_PLACEMENT_IS_COLDSTART=False
):
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
    ])

    # stable random seed for reproducibility
    random.seed(42)

    nodes = {}
    functions = {}

    metrics = {
        'coldstarts': 0,
        'requests': 0,
        'makespan': 0,

        'request_duration': 0,
        'slot_overflows': 0,

        'fpga_reconfigurations_per_node': {},
        'fpga_usage_per_node': {},
        'requests_per_node': {},
        'request_duration_per_node': {},
        'function_placements_per_node': {},
        'metrics_per_node_over_time': [],

        'latencies': {}
    }

    for i in range(NUM_NODES):
        created_node = create_node(nodes, NUM_FPGA_SLOTS_PER_NODE)

        # initialize per-node metrics
        metrics['fpga_reconfigurations_per_node'][created_node['id']] = []
        metrics['fpga_usage_per_node'][created_node['id']] = 0
        metrics['requests_per_node'][created_node['id']] = 0
        metrics['request_duration_per_node'][created_node['id']] = 0
        metrics['function_placements_per_node'][created_node['id']] = []

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

    global_timer = {
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
                    nodes,
                    recently_used_nodes,
                    functions,
                    characterized_function,
                    row,
                    metrics,
                    MAX_REQUESTS,
                    FUNCTION_KEEPALIVE,
                    NUM_FPGA_SLOTS_PER_NODE,
                    ENABLE_LOGS,
                    FPGA_RECONFIGURATION_TIME_MS,
                    ENABLE_PROGRESS_LOGS,
                    RECENT_FPGA_USAGE_TIME_WEIGHT,
                    RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                    FPGA_BITSTREAM_LOCALITY_WEIGHT,
                    FUNCTION_PLACEMENT_IS_COLDSTART,
                    FUNCTION_HOST_COLDSTART_TIME_MS,
                    previous_request_timestamp,
                    global_timer,
                    add_to_wait,
                    True,
                )
        else:
            res = process_row(
                nodes,
                recently_used_nodes,
                functions,
                characterized_function,
                row,
                metrics,
                MAX_REQUESTS,
                FUNCTION_KEEPALIVE,
                NUM_FPGA_SLOTS_PER_NODE,
                ENABLE_LOGS,
                FPGA_RECONFIGURATION_TIME_MS,
                ENABLE_PROGRESS_LOGS,
                RECENT_FPGA_USAGE_TIME_WEIGHT,
                RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                FPGA_BITSTREAM_LOCALITY_WEIGHT,
                FUNCTION_PLACEMENT_IS_COLDSTART,
                FUNCTION_HOST_COLDSTART_TIME_MS,
                previous_request_timestamp,
                global_timer,
                add_to_wait,
                False,
            )

        if res is False:
            break

    coldstart_percent = round((metrics['coldstarts'] / metrics['requests']) * 100, 2)

    if ENABLE_PRINT_RESULTS:
        print("Coldstarts: {} ({}%), Nodes: {}".format(metrics['coldstarts'], coldstart_percent, len(nodes)))

    time_spent_on_cold_starts = round((metrics['coldstarts'] * FPGA_RECONFIGURATION_TIME) / 60 / 60, 2)
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
