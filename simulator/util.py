import usage
from scheduler import next_best_node
import newrelic.agent


# Remove functions that are past the keepalive, keep bitstreams configured (no benefit in removing them)
def evict_inactive_functions(recently_used_nodes, functions, current_ts, FUNCTION_KEEPALIVE):
    for nodeIdx in recently_used_nodes:
        node = recently_used_nodes[nodeIdx]

        # remove functions that have expired
        nextFunctions = set()
        for functionName in node['functions']:
            function = functions.get(functionName)
            if function['last_invoked_at'] is None:
                continue

            functionAge = (current_ts - function['last_invoked_at']).total_seconds()

            if functionAge <= FUNCTION_KEEPALIVE:
                # print("Function removed: {}".format(function['name']))
                nextFunctions.add(functionName)
            # TODO Make sure this works as expected
            else:
                function['last_node'] = None

        node['functions'] = nextFunctions
    pass


def create_node(nodes: dict, NUM_FPGA_SLOTS_PER_NODE=2, ARRIVAL_POLICY: str = "FIFO"):
    nextId = len(nodes)

    slots = {}
    for i in range(NUM_FPGA_SLOTS_PER_NODE):
        slots[i] = {
            'current_bitstream': None,
            'earliest_start_date': None,
            'priority': (ARRIVAL_POLICY == "PRIORITY") and (i == (NUM_FPGA_SLOTS_PER_NODE - 1)),
        }

        # sanity check slots[i]["priority"] is boolean value
        if not isinstance(slots[i]["priority"], bool):
            raise Exception(f"Slot Priority should be supplied as boolean value")

    # sanity check: if ARRIVAL_POLICY = "PRIORITY", there must be at least one slot with priority = True and at least one slot with priority = False
    if ARRIVAL_POLICY == "PRIORITY":
        if not any(slot["priority"] for slot in slots.values()):
            raise Exception(f"ARRIVAL_POLICY = 'PRIORITY' requires at least one slot with priority = True")
        if not any(not slot["priority"] for slot in slots.values()):
            raise Exception(f"ARRIVAL_POLICY = 'PRIORITY' requires at least one slot with priority = False")

    new_node = {
        'id': nextId,
        'functions': set(),

        'bitstreams': set(),
        'fpga_slots': slots,

        'cpu': {
            'current_invocation': None,
            'earliest_start_date': None,
        },

        'recent_baseline_utilization': usage.BaselineUtilizationTracker(),
        'recent_fpga_usage_time': usage.FPGAUsageTimeTracker(),
        'recent_fpga_reconfiguration_time': usage.FPGAReconfigurationTimeTracker(),
        'recent_fpga_reconfiguration_count': usage.FPGAReconfigurationCountTracker(),
    }
    nodes[len(nodes)] = new_node
    return new_node


# place a function on a node
def place_function(function, processing_start_timestamp, functions, nodes, NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS,
                   RECENT_FPGA_USAGE_TIME_WEIGHT, RECENT_FPGA_RECONFIGURATION_TIME_WEIGHT,
                   FPGA_BITSTREAM_LOCALITY_WEIGHT):
    # lazily add function to state if not known (first invocation)
    if functions.get(function) is None:
        functions[function] = {
            'name': function,
            'last_invoked_at': None,
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


def update_trackers(recently_used_nodes, arrival_timestamp, ENABLE_LOGS, row_is_traced: bool):
    if row_is_traced:
        newrelic.agent.add_custom_span_attribute("recently_used_nodes", len(recently_used_nodes))

    # instead of decaying all nodes, decay nodes that have recent usage and reset after this
    for node in recently_used_nodes.values():
        node['recent_baseline_utilization'].decay(arrival_timestamp)

        node['recent_fpga_usage_time'].decay(arrival_timestamp)
        node['recent_fpga_reconfiguration_count'].decay(arrival_timestamp)
        node['recent_fpga_reconfiguration_time'].decay(arrival_timestamp)

    recently_used_nodes.clear()
