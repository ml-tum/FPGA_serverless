import csv
import datetime
import random
import preprocess

import fpga_utilization
import baseline_utilization


# alternative strategy to LRU/JIT eviction: keep functions/bitstreams around until timeout, then evict
def decay(nodes, functions, current_ts, FUNCTION_KEEPALIVE):
    # remove bitstreams that have expired
    for nodeIdx in nodes:
        node = nodes[nodeIdx]

        # remove functions that have expired
        nextBitstreams = set()
        nextFunctions = set()
        for functionName in node['functions']:
            function = functions.get(functionName)

            functionAge = (current_ts - function['last_invoked_at']).total_seconds()

            if functionAge <= FUNCTION_KEEPALIVE:
                # print("Function removed: {}".format(function['name']))
                nextFunctions.add(functionName)

            if functionName in node['bitstreams']:
                bitstreamAge = (current_ts - function['bitstream_last_invoked_at']).total_seconds()
                if bitstreamAge <= FUNCTION_KEEPALIVE:
                    nextBitstreams.add(functionName)

        node['bitstreams'] = nextBitstreams
        node['functions'] = nextFunctions
    pass


def create_node(nodes: dict):
    nextId = len(nodes)
    new_node = {
        'id': nextId,
        'functions': set(),
        'bitstreams': set(),
        'recent_baseline_utilization': baseline_utilization.BaselineUtilizationTracker(),
        'recent_fpga_usage_time': fpga_utilization.FPGAUsageTimeTracker(),
        'recent_fpga_reconfiguration_time': fpga_utilization.FPGAReconfigurationTimeTracker(),
        'recent_fpga_reconfiguration_count': fpga_utilization.FPGAReconfigurationCountTracker(),
    }
    nodes[len(nodes)] = new_node
    return new_node


# determine the best node to place a function on
# this function simulates the Kubernetes schedulers
def next_best_node(nodes: dict, functionName: str, recent_fpga_usage_time_weight,
                   recent_fpga_reconfiguration_time_weight, fpga_bitstream_locality_weight):
    if len(nodes) == 0:
        return None

    prescored = []
    for nodeIdx in nodes:
        node = nodes[nodeIdx]

        # collect relevant criteria
        baseline_utilization = node['recent_baseline_utilization'].get_recent_compute_time()

        # recent FPGA utilization in seconds
        recent_utilization = node['recent_fpga_usage_time'].get_recent_usage_time()

        # recent reconfiguration times in seconds
        recent_reconfiguration_times = node['recent_fpga_reconfiguration_time'].get_recent_reconfiguration_time()

        has_fitting_bitstream = 0
        if functionName in node['bitstreams']:
            has_fitting_bitstream = 1

        score = (nodeIdx, recent_utilization, recent_reconfiguration_times, has_fitting_bitstream, baseline_utilization)

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
    for nodeIdx, _, _, has_fitting_bitstream, _ in prescored:
        scored.append((nodeIdx,
                       score_node(sorted_usage_time, sorted_reconfiguration_time, sorted_baseline_utilization, nodeIdx,
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
        }

    # check if function is deployed on any node
    deployed_on = None
    for nodeIdx in nodes:
        node = nodes.get(nodeIdx)
        if function in node['functions']:
            deployed_on = node
            break

    is_function_placement = deployed_on is None

    if is_function_placement:
        # deploy function on next best node (run scheduler)
        deployed_on = next_best_node(nodes, function, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                     RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT, FPGA_BITSTREAM_LOCALITY_WEIGHT)
        if deployed_on is None:
            # no node has enough space, create new node
            deployed_on = create_node(nodes)

            if ENABLE_LOGS:
                print("New node created: {}".format(deployed_on['id']))

        deployed_on['functions'].add(function)
        if ENABLE_LOGS:
            print("Function deployed on node: {}".format(deployed_on['id']))

    return deployed_on, is_function_placement


# evict a function from a node
def evict_bitstream(functions, node, ENABLE_LOGS):
    # find least recently used bitstream
    lru_bitstream = None
    for bitstream in node['bitstreams']:
        if lru_bitstream is None or functions[bitstream]['bitstream_last_invoked_at'] < functions[lru_bitstream][
            'bitstream_last_invoked_at']:
            lru_bitstream = bitstream

    node['bitstreams'].remove(lru_bitstream)

    if ENABLE_LOGS:
        print("Evicted bitstream: {}, remaining: {}".format(lru_bitstream, node['bitstreams']))


# acquire an FPGA slot for a function (place bitstream on node FPGA)
def acquire_fpga_slot(functions, nodes, metrics, node, functionName, start_timestamp, end_timestamp,
                      NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS, FPGA_RECONFIGURATION_TIME):
    # check if function is deployed on any FPGA slot, update last_invoked_at
    function = functions.get(functionName)

    # otherwise deploy
    needs_reconfiguration = functionName not in node['bitstreams']
    if needs_reconfiguration:
        if len(node['bitstreams']) >= NUM_FPGA_SLOTS_PER_NODE:
            # Primary: Evict least recently used bitstream
            evict_bitstream(functions, node, ENABLE_LOGS)

            # Other approach: Find another node with space
            # node = handle_slot_overflow(function, nodes, metrics, NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS, UTILIZATION_WEIGHT, RECONFIGURATION_WEIGHT, BITSTREAM_WEIGHT)

        # deploy function on next best FPGA slot
        node['bitstreams'].add(functionName)
        function['bitstream_started_at'] = start_timestamp

        # coldstart if bitstream was not placed on this FPGA before
        if ENABLE_LOGS:
            print("Added bitstream: {}, now at {}/{}: {}".format(functionName, len(node['bitstreams']),
                                                                 NUM_FPGA_SLOTS_PER_NODE, node['bitstreams']))

        if metrics['fpga_reconfigurations_per_node'].get(node['id']) is None:
            metrics['fpga_reconfigurations_per_node'][node['id']] = [start_timestamp]
        else:
            metrics['fpga_reconfigurations_per_node'][node['id']].append(start_timestamp)

        node['recent_fpga_reconfiguration_count'].add_reconfiguration(end_timestamp)
        node['recent_fpga_reconfiguration_time'].add_reconfiguration(end_timestamp, FPGA_RECONFIGURATION_TIME)

        if ENABLE_LOGS:
            print("Coldstart for function {}, total {}".format(functionName, metrics['coldstarts']))

    function['bitstream_last_invoked_at'] = end_timestamp
    nodes[node['id']] = node

    return needs_reconfiguration


# release an FPGA slot for a function (remove bitstream from node FPGA)
def release_fpga_slot(functions, nodes, node, functionName, end_timestamp, ENABLE_LOGS):
    # check if function is deployed on any FPGA slot, update last_invoked_at
    function = functions.get(functionName)

    # otherwise deploy
    if functionName in node['bitstreams']:
        node['bitstreams'].remove(functionName)
        function['bitstream_last_invoked_at'] = end_timestamp
        nodes[node['id']] = node

    if ENABLE_LOGS:
        print("Released FPGA slot for {}".format(functionName))


# handle_slot_overflow provides alternative strategy to handling the case where no
# more slots are available by creating new node just in time and migrating workload
def handle_slot_overflow(function, nodes, metrics, ENABLE_LOGS, UTILIZATION_WEIGHT, RECONFIGURATION_WEIGHT,
                         BITSTREAM_LOCALITY_WEIGHT):
    functionName = function['name']
    # no FPGA slots available, deploy on next best node
    node = next_best_node(nodes, functionName, UTILIZATION_WEIGHT, RECONFIGURATION_WEIGHT, BITSTREAM_LOCALITY_WEIGHT)
    if node is None:
        # no node has enough space, create new node
        node['functions'].remove(functionName)
        node = create_node(nodes)
        node['functions'].add(functionName)
        metrics['slot_overflows'] += 1
        if ENABLE_LOGS:
            print("Slot overflow, new node created: {}".format(node['id']))

    return node


# Function to process each row of the CSV file
def process_row(
        nodes,
        functions,
        characterized_function,
        row,
        metrics,
        MAX_REQUESTS: int,
        FUNCTION_KEEPALIVE: float,
        NUM_FPGA_SLOTS_PER_NODE: int,
        ENABLE_LOGS: bool,
        FPGA_RECONFIGURATION_TIME: float,
        ENABLE_PROGRESS_LOGS: bool,
        RECENT_FPGA_USAGE_TIME_WEIGHT: float,
        RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT: float,
        FPGA_BITSTREAM_LOCALITY_WEIGHT: float,
        FUNCTION_PLACEMENT_IS_COLDSTART: bool,
        FUNCTION_HOST_COLDSTART_TIME_MS: float,
        last_request_timestamp,
):
    app, func, end_timestamp, duration = row

    # convert duration (seconds) to float
    duration = float(duration)
    if duration < 0:
        print("Invalid duration: {}".format(duration))
        return False

    # convert duration (seconds) to milliseconds
    duration = duration * 1000

    # get original start timestamp
    start_timestamp = end_timestamp - datetime.timedelta(milliseconds=float(duration))

    # adjust duration by expected acceleration
    duration = duration * characterized_function["mean_speedup"]

    # compute adjusted end timestamp
    end_timestamp = start_timestamp + datetime.timedelta(milliseconds=float(duration))

    # we don't know how much time passed since last request so update host/slot occupancy
    if FUNCTION_KEEPALIVE is not None:
        decay(nodes, functions, start_timestamp, FUNCTION_KEEPALIVE)

    update_trackers(nodes, end_timestamp, ENABLE_LOGS)

    # limit requests to max for simulation
    if MAX_REQUESTS is not None and MAX_REQUESTS > 0 and metrics['requests'] > MAX_REQUESTS:
        print(f"Reached max requests ({metrics['requests']}), exiting")
        return False
    is_last_request = metrics['requests'] == MAX_REQUESTS

    metrics['requests'] += 1
    metrics['request_duration'] += duration

    if ENABLE_LOGS:
        time_spent_since_last_request = 0
        if last_request_timestamp is not None and last_request_timestamp["end"] is not None:
            time_spent_since_last_request = (start_timestamp - last_request_timestamp["end"]).total_seconds()
        print("-- req; (+{}s) App: {}, Function: {}, Start Timestamp: {}, End Timestamp: {}, Duration: {}".format(
            time_spent_since_last_request, app, func, start_timestamp, end_timestamp, duration))

    if ENABLE_PROGRESS_LOGS and metrics['requests'] % 1000 == 0:
        print("Requests: {}".format(metrics['requests']))

    deployed_on, is_function_placement = place_function(func, end_timestamp, functions, nodes, NUM_FPGA_SLOTS_PER_NODE,
                                                        ENABLE_LOGS, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                                        RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                                                        FPGA_BITSTREAM_LOCALITY_WEIGHT)

    # update metrics
    if is_function_placement:
        metrics['makespan'] += FUNCTION_HOST_COLDSTART_TIME_MS
        if metrics['function_placements_per_node'].get(deployed_on['id']) is None:
            metrics['function_placements_per_node'][deployed_on['id']] = [start_timestamp]
        else:
            metrics['function_placements_per_node'][deployed_on['id']].append(start_timestamp)

    if metrics['requests_per_node'].get(deployed_on['id']) is None:
        metrics['requests_per_node'][deployed_on['id']] = 1
    else:
        metrics['requests_per_node'][deployed_on['id']] += 1

    if metrics['request_duration_per_node'].get(deployed_on['id']) is None:
        metrics['request_duration_per_node'][deployed_on['id']] = duration
    else:
        metrics['request_duration_per_node'][deployed_on['id']] += duration

    run_on_fpga = characterized_function["run_on_fpga"]

    if run_on_fpga:
        # keep processing request on fpga
        needs_reconfiguration = acquire_fpga_slot(functions, nodes, metrics, deployed_on, func, start_timestamp,
                                                  end_timestamp,
                                                  NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS, FPGA_RECONFIGURATION_TIME)
        if needs_reconfiguration:
            metrics['makespan'] += round(FPGA_RECONFIGURATION_TIME * 1000, 2)

        if (FUNCTION_PLACEMENT_IS_COLDSTART and is_function_placement) or needs_reconfiguration:
            metrics['coldstarts'] += 1
    else:
        if FUNCTION_PLACEMENT_IS_COLDSTART and is_function_placement:
            metrics['coldstarts'] += 1

    # update utilization metrics
    fpga_ratio = characterized_function["fpga_ratio"] if run_on_fpga else 0
    time_spent_on_cpu = (1 - fpga_ratio) * duration
    time_spent_on_fpga = fpga_ratio * duration

    metrics['makespan'] += round(time_spent_on_cpu + time_spent_on_fpga, 2)

    deployed_on['recent_baseline_utilization'].capture_request(end_timestamp, time_spent_on_cpu)

    if run_on_fpga:
        deployed_on['recent_fpga_usage_time'].capture_request(end_timestamp, time_spent_on_fpga)

        if metrics['fpga_usage_per_node'].get(deployed_on['id']) is None:
            metrics['fpga_usage_per_node'][deployed_on['id']] = time_spent_on_fpga
        else:
            metrics['fpga_usage_per_node'][deployed_on['id']] += time_spent_on_fpga

    # only trigger this if 30 seconds have passed to avoid recording way too many data points
    if is_last_request or last_request_timestamp['start'] is None or (
            start_timestamp - last_request_timestamp['start']).total_seconds() > 60 * 30:
        fpga_reconfiguration_times = [node['recent_fpga_reconfiguration_time'].get_recent_reconfiguration_time() for
                                      node in nodes.values()]
        fpga_usage_times = [node['recent_fpga_usage_time'].get_recent_usage_time() for node in nodes.values()]
        baseline_utilization_times = [node['recent_baseline_utilization'].get_recent_compute_time() for node in
                                      nodes.values()]

        metrics['metrics_per_node_over_time'].append({
            'timestamp': start_timestamp,
            'baseline_utilization_time': baseline_utilization_times,
            'fpga_reconfiguration_time': fpga_reconfiguration_times,
            'fpga_usage_time': fpga_usage_times,
        })
        last_request_timestamp['start'] = start_timestamp
        last_request_timestamp['end'] = end_timestamp

    # Immediately releasing means we have to coldstart for every request
    # release_fpga_slot(functions, nodes, deployed_on, function, end_timestamp, ENABLE_LOGS)

    return True


def update_trackers(nodes, end_timestamp, ENABLE_LOGS):
    out = ""
    for node in nodes.values():
        node['recent_baseline_utilization'].decay(end_timestamp)

        node['recent_fpga_usage_time'].decay(end_timestamp)
        node['recent_fpga_reconfiguration_count'].decay(end_timestamp)
        node['recent_fpga_reconfiguration_time'].decay(end_timestamp)

        if ENABLE_LOGS:
            out += "{}: [{}, {}] ".format(node['id'], node['recent_fpga_usage_time'].get_recent_usage_time(),
                                          node['recent_fpga_reconfiguration_count'].get_recent_reconfiguration_count())

    if ENABLE_LOGS:
        print(out)


def run_on_file(
        csv_file_path='AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt',

        CHARACTERIZED_FUNCTIONS=None,

        # system parameters
        NUM_NODES=10, NUM_FPGA_SLOTS_PER_NODE=2, FPGA_RECONFIGURATION_TIME=0.01,
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
    }

    for i in range(NUM_NODES):
        created_node = create_node(nodes)

        # initialize per-node metrics
        metrics['fpga_reconfigurations_per_node'][created_node['id']] = []
        metrics['fpga_usage_per_node'][created_node['id']] = 0
        metrics['requests_per_node'][created_node['id']] = 0
        metrics['request_duration_per_node'][created_node['id']] = 0
        metrics['function_placements_per_node'][created_node['id']] = []

    if ENABLE_LOGS:
        print("Loading traces")

    # load traces from disk
    traces = preprocess.load_traces(csv_file_path)

    if ENABLE_LOGS:
        print(f"Loaded {len(traces)} traces, now preprocessing")

    # characterize individual functions (make sure every trace has an assigned function)
    preprocess.characterize_traces(CHARACTERIZED_FUNCTIONS, traces)

    # on list of traces in original order, apply arrival policy (i.e. re-order based on priority or other metric)
    traces = preprocess.apply_arrival_policy(traces, ARRIVAL_POLICY, CHARACTERIZED_FUNCTIONS)

    if ENABLE_LOGS:
        print("Preprocessed traces")

    last_request_timestamp = {
        'start': None,
        'end': None
    }

    for fntype, row, _ in traces:
        characterized_function = CHARACTERIZED_FUNCTIONS.get(fntype)
        if process_row(
                nodes,
                functions,
                characterized_function,
                row,
                metrics,
                MAX_REQUESTS,
                FUNCTION_KEEPALIVE,
                NUM_FPGA_SLOTS_PER_NODE,
                ENABLE_LOGS,
                FPGA_RECONFIGURATION_TIME,
                ENABLE_PROGRESS_LOGS,
                RECENT_FPGA_USAGE_TIME_WEIGHT,
                RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                FPGA_BITSTREAM_LOCALITY_WEIGHT,
                FUNCTION_PLACEMENT_IS_COLDSTART,
                FUNCTION_HOST_COLDSTART_TIME_MS,
                last_request_timestamp
        ) is False:
            break

    coldstart_percent = round((metrics['coldstarts'] / metrics['requests']) * 100, 2)

    if ENABLE_PRINT_RESULTS:
        print("Coldstarts: {} ({}%), Nodes: {}".format(metrics['coldstarts'], coldstart_percent, len(nodes)))

    time_spent_on_cold_starts = round((metrics['coldstarts'] * FPGA_RECONFIGURATION_TIME) / 60 / 60, 2)
    time_spent_processing = round(metrics['request_duration'] / 60 / 60, 2)

    if ENABLE_PRINT_RESULTS:
        print("Time spent on coldstarts {}h, time spent processing {}h".format(time_spent_on_cold_starts,
                                                                               time_spent_processing))

    return nodes, functions, metrics, coldstart_percent, time_spent_on_cold_starts, time_spent_processing
