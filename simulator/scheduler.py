import random


# determine the best node to place a function on
# this function simulates the Kubernetes scheduler
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
