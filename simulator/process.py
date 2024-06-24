import datetime
import random
import newrelic.agent

from fpga import acquire_fpga_slot
from util import evict_inactive_functions, place_function, update_trackers


# Function to process each row of the CSV file
def process_row(
        # internal state
        nodes,
        recently_used_nodes,
        functions,
        characterized_function,
        row,
        metrics: dict,
        previous_request_timestamp,
        node_timer: dict,
        add_to_wait: callable,
        row_is_traced: bool,

        # run options
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
        METRICS_TO_RECORD: set,
        RECORD_PRIORITY_LATENCIES: bool,
        ARRIVAL_POLICY: str,
        ACCELERATE_REQUESTS: float
):
    app, func, orig_end_timestamp, duration_ms = row

    priority = False
    if ARRIVAL_POLICY == "PRIORITY" and characterized_function["priority"]:
        priority = characterized_function["priority"]
        # if priority is number and not 0, set to true
        if not isinstance(priority, bool):
            print(f"Warning: Priority should be supplied as boolean value")
            priority = priority != 0

    # get original start timestamp (end_timestamp: function invocation end timestamp in millisecond)
    arrival_timestamp = orig_end_timestamp - datetime.timedelta(milliseconds=float(duration_ms))

    req_id = f"{metrics.get('requests')}-{app}-{func}-{arrival_timestamp}"

    # ACCELERATE_REQUESTS is a probability between 0 and 1, generate the chance we should accelerate this request
    should_accelerate = random.random() < ACCELERATE_REQUESTS

    # adjust duration by expected acceleration
    if should_accelerate:
        duration_ms = round(duration_ms / characterized_function["mean_speedup"], 2)

    run_on_fpga = characterized_function["run_on_fpga"] and should_accelerate
    if NUM_FPGA_SLOTS_PER_NODE == 0:
        run_on_fpga = False

    # update utilization metrics
    fpga_ratio = characterized_function["fpga_ratio"] if run_on_fpga else 0
    time_spent_on_cpu = (1 - fpga_ratio) * duration_ms
    time_spent_on_fpga = fpga_ratio * duration_ms

    # attempt to place function
    # there is a chance that this invocation has already been placed and is waiting to get CPU/FPGA access,
    # in which case we don't need to place it again
    if row_is_traced:
        with newrelic.agent.FunctionTrace("place_function"):
            deployed_on, is_function_placement = place_function(func, functions, nodes,
                                                                NUM_FPGA_SLOTS_PER_NODE,
                                                                ENABLE_LOGS, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                                                RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                                                                FPGA_BITSTREAM_LOCALITY_WEIGHT)  # TODO Check if this needs to run always
    else:
        deployed_on, is_function_placement = place_function(func, functions, nodes,
                                                            NUM_FPGA_SLOTS_PER_NODE,
                                                            ENABLE_LOGS, RECENT_FPGA_USAGE_TIME_WEIGHT,
                                                            RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                                                            FPGA_BITSTREAM_LOCALITY_WEIGHT)  # TODO Check if this needs to run always

    if recently_used_nodes.get(deployed_on['id']) is None:
        recently_used_nodes[deployed_on['id']] = deployed_on

    # retrieve node-specific timer
    timer = node_timer[deployed_on['id']]

    # by default, requests start on arrival (if not waiting)
    processing_start_timestamp = arrival_timestamp

    # if request is waiting, it can only end after the previous request + its own duration
    # if timer["time"] is greater than current request, we have moved the time forward by processing work
    delay = 0.0
    request_is_waiting = timer["time"] is not None and arrival_timestamp < timer["time"]
    if request_is_waiting:
        processing_start_timestamp = timer["time"]  # start on earliest slot availability
        delay = (processing_start_timestamp - arrival_timestamp) / datetime.timedelta(milliseconds=1)

    def time_elapsed_since_previous_request(delta_seconds: int):
        return previous_request_timestamp['start'] is None or (
                processing_start_timestamp - previous_request_timestamp['start']).total_seconds() > delta_seconds

    # decay utilization trackers every 30s
    if time_elapsed_since_previous_request(30):
        if row_is_traced:
            with newrelic.agent.FunctionTrace("update_trackers"):
                update_trackers(recently_used_nodes, processing_start_timestamp, ENABLE_LOGS, True)
        else:
            update_trackers(recently_used_nodes, processing_start_timestamp, ENABLE_LOGS, False)

    # limit requests to max for simulation
    if MAX_REQUESTS is not None and MAX_REQUESTS > 0 and metrics['requests'] > MAX_REQUESTS:
        print(f"Reached max requests ({metrics['requests']}), exiting")
        return False
    is_last_request = metrics['requests'] == MAX_REQUESTS

    # Check if CPU slot is available
    if deployed_on['cpu']['earliest_start_date'] is not None and deployed_on['cpu'][
        'earliest_start_date'] > processing_start_timestamp:
        add_to_wait()

        # all requests must wait until earliest_start_date of the earliest available slot
        node_timer[deployed_on['id']]["time"] = deployed_on['cpu']['earliest_start_date']

        return None

    # Only advance CPU earliest start date by time spent on CPU
    deployed_on['cpu']['earliest_start_date'] = processing_start_timestamp + datetime.timedelta(
        milliseconds=float(time_spent_on_cpu))  # TODO Check if this is far enough into the future
    deployed_on['cpu']['current_invocation'] = req_id

    needs_reconfiguration = False
    if run_on_fpga:
        next_earliest_fpga = processing_start_timestamp + datetime.timedelta(
            milliseconds=float(time_spent_on_fpga))

        # keep processing request on fpga
        if row_is_traced:
            with newrelic.agent.FunctionTrace("acquire_fpga_slot"):
                needs_wait, needs_reconfiguration, slot_key = acquire_fpga_slot(functions, nodes, metrics, deployed_on,
                                                                                func,
                                                                                processing_start_timestamp,
                                                                                next_earliest_fpga,
                                                                                priority,
                                                                                timer,
                                                                                add_to_wait,
                                                                                NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS,
                                                                                FPGA_RECONFIGURATION_TIME_MS,
                                                                                METRICS_TO_RECORD)  # TODO Check if this needs to run always
        else:
            needs_wait, needs_reconfiguration, slot_key = acquire_fpga_slot(functions, nodes, metrics, deployed_on,
                                                                            func,
                                                                            processing_start_timestamp,
                                                                            next_earliest_fpga,
                                                                            priority, timer,
                                                                            add_to_wait,
                                                                            NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS,
                                                                            FPGA_RECONFIGURATION_TIME_MS,
                                                                            METRICS_TO_RECORD)  # TODO Check if this needs to run always

        if needs_wait:
            return None

        if (FUNCTION_PLACEMENT_IS_COLDSTART and is_function_placement) or needs_reconfiguration:
            if "coldstarts" in METRICS_TO_RECORD:
                metrics['coldstarts'] += 1
    else:
        if FUNCTION_PLACEMENT_IS_COLDSTART and is_function_placement:
            if "coldstarts" in METRICS_TO_RECORD:
                metrics['coldstarts'] += 1

    functions[func] = {
        'name': func,
        'last_invoked_at': processing_start_timestamp,
        'last_node': deployed_on['id'],
    }

    # finalize latency
    invocation_latency = delay + (FPGA_RECONFIGURATION_TIME_MS if needs_reconfiguration else 0) + duration_ms

    response_timestamp = arrival_timestamp + datetime.timedelta(
        milliseconds=float(invocation_latency))

    # update system utilization
    deployed_on['recent_baseline_utilization'].add(response_timestamp,
                                                   time_spent_on_cpu)  # TODO Check if this needs to run always

    if run_on_fpga:
        deployed_on['recent_fpga_usage_time'].add(response_timestamp,
                                                  time_spent_on_fpga)  # TODO Check if this needs to run always

        if "fpga_usage_per_node" in METRICS_TO_RECORD:
            if metrics['fpga_usage_per_node'].get(deployed_on['id']) is None:
                metrics['fpga_usage_per_node'][deployed_on['id']] = time_spent_on_fpga
            else:
                metrics['fpga_usage_per_node'][deployed_on['id']] += time_spent_on_fpga

    # update metrics
    metrics['requests'] += 1
    if "request_duration" in METRICS_TO_RECORD:
        metrics['request_duration'] += duration_ms

    # we don't know how much time passed since last request so update host/slot occupancy (optimization: after 5s of last request)
    if FUNCTION_KEEPALIVE is not None and time_elapsed_since_previous_request(5):
        if row_is_traced:
            with newrelic.agent.FunctionTrace("evict_inactive_functions"):
                evict_inactive_functions(recently_used_nodes, functions, processing_start_timestamp,
                                         FUNCTION_KEEPALIVE)
        else:
            evict_inactive_functions(recently_used_nodes, functions, processing_start_timestamp,
                                     FUNCTION_KEEPALIVE)  # TODO Check if this needs to run always

    # if ENABLE_LOGS:
    #     time_spent_since_previous_request = 0
    #     if previous_request_timestamp is not None and previous_request_timestamp["end"] is not None:
    #         time_spent_since_previous_request = (start_timestamp - previous_request_timestamp["end"]).total_seconds()
    #     print("-- req; (+{}s) App: {}, Function: {}, Start Timestamp: {}, End Timestamp: {}, Duration: {}".format(
    #         time_spent_since_previous_request, app, func, start_timestamp, end_timestamp, duration))

    if ENABLE_PROGRESS_LOGS and metrics['requests'] % 1000 == 0:
        print("Requests: {}".format(metrics['requests']))

    # update metrics
    if is_function_placement:
        # only count placement toward latency if it should be understood as cold start
        if FUNCTION_PLACEMENT_IS_COLDSTART:
            invocation_latency += FUNCTION_HOST_COLDSTART_TIME_MS

        if "function_placements_per_node" in METRICS_TO_RECORD:
            if metrics['function_placements_per_node'].get(deployed_on['id']) is None:
                metrics['function_placements_per_node'][deployed_on['id']] = [processing_start_timestamp]
            else:
                metrics['function_placements_per_node'][deployed_on['id']].append(processing_start_timestamp)

    if "requests_per_node" in METRICS_TO_RECORD:
        if metrics['requests_per_node'].get(deployed_on['id']) is None:
            metrics['requests_per_node'][deployed_on['id']] = 1
        else:
            metrics['requests_per_node'][deployed_on['id']] += 1

    if "request_duration_per_node" in METRICS_TO_RECORD:
        if metrics['request_duration_per_node'].get(deployed_on['id']) is None:
            metrics['request_duration_per_node'][deployed_on['id']] = duration_ms
        else:
            metrics['request_duration_per_node'][deployed_on['id']] += duration_ms

    # only trigger this if 30 seconds have passed to avoid recording way too many data points
    if "metrics_per_node_over_time" in METRICS_TO_RECORD and (
            is_last_request or time_elapsed_since_previous_request(
        60 * 30)):  # TODO Check if this arbitrary number is correct
        fpga_reconfiguration_times = [node['recent_fpga_reconfiguration_time'].get_window_value() for
                                      node in nodes.values()]
        fpga_usage_times = [node['recent_fpga_usage_time'].get_window_value() for node in nodes.values()]
        baseline_utilization_times = [node['recent_baseline_utilization'].get_window_value() for node in
                                      nodes.values()]

        metrics['metrics_per_node_over_time'].append({
            'timestamp': processing_start_timestamp,
            'baseline_utilization_time': baseline_utilization_times,
            'fpga_reconfiguration_time': fpga_reconfiguration_times,
            'fpga_usage_time': fpga_usage_times,
        })
        previous_request_timestamp['start'] = processing_start_timestamp
        previous_request_timestamp['end'] = response_timestamp

    # Immediately releasing means we have to coldstart for every request
    # release_fpga_slot(functions, nodes, deployed_on, function, end_timestamp, ENABLE_LOGS)

    if "latencies" in METRICS_TO_RECORD and (
            ARRIVAL_POLICY != "PRIORITY" or (
            not RECORD_PRIORITY_LATENCIES or (RECORD_PRIORITY_LATENCIES and priority))):
        metrics['latencies'][req_id] = (
            arrival_timestamp, processing_start_timestamp, response_timestamp, invocation_latency, duration_ms, delay)

    return True
