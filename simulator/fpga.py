# acquire an FPGA slot for a function (place bitstream on node FPGA)
import datetime


def acquire_fpga_slot(functions, nodes, metrics, node, functionName, processing_start_timestamp: datetime.datetime,
                      next_invocation_earliest_start_date,
                      priority,
                      timer, add_to_wait,
                      NUM_FPGA_SLOTS_PER_NODE, ENABLE_LOGS, FPGA_RECONFIGURATION_TIME, METRICS_TO_RECORD):
    if NUM_FPGA_SLOTS_PER_NODE == 0:
        return False, False, None

    # check if function is deployed on any FPGA slot, update last_invoked_at
    function = functions.get(functionName)

    slot = None
    slot_key = None

    earliest_start_date = None

    needs_reconfiguration = functionName not in node['bitstreams']

    for slotIdx in node['fpga_slots']:
        current_slot = node['fpga_slots'][slotIdx]

        # if we have a slot with a matching bitstream, pick that
        if not needs_reconfiguration:
            if current_slot['current_bitstream'] != functionName:
                continue

            slot_key = slotIdx
            slot = current_slot
            break

        # otherwise the priority must match
        if priority != current_slot['priority']:
            continue

        # and then it must be empty
        if current_slot['current_bitstream'] is None:
            slot = current_slot
            slot_key = slotIdx
            break

        # or at least not working
        if earliest_start_date is None or current_slot['earliest_start_date'] is None:
            slot = current_slot
            slot_key = slotIdx
            earliest_start_date = current_slot['earliest_start_date']

        # or having completed its work before
        if current_slot['earliest_start_date'] < earliest_start_date:
            slot = current_slot
            slot_key = slotIdx
            earliest_start_date = current_slot['earliest_start_date']

    if slot is None:
        raise Exception(f"No slot found for priority {priority}")

    if needs_reconfiguration:
        # If slot is not available at current time, wait until it is
        required_wait = (
                                earliest_start_date - processing_start_timestamp) / datetime.timedelta(
            milliseconds=1) if earliest_start_date is not None else 0
        can_run_on_slot = required_wait <= 0
        if not can_run_on_slot:
            add_to_wait()

            # all requests must wait until earliest_start_date of the earliest available slot
            timer["time"] = earliest_start_date

            # can't do any work yet, so we'll return and let the slot "run"
            return True, None, None

        if slot['current_bitstream'] is not None:
            node["bitstreams"].remove(slot["current_bitstream"])
            slot["current_bitstream"] = None
            slot["earliest_start_date"] = None

    # deploy function on next best FPGA slot
    node['bitstreams'].add(functionName)

    function['bitstream_started_at'] = processing_start_timestamp
    slot['current_bitstream'] = functionName

    slot['earliest_start_date'] = next_invocation_earliest_start_date + datetime.timedelta(
        milliseconds=FPGA_RECONFIGURATION_TIME) if needs_reconfiguration else next_invocation_earliest_start_date

    if "fpga_reconfigurations_per_node" in METRICS_TO_RECORD:
        if metrics['fpga_reconfigurations_per_node'].get(node['id']) is None:
            metrics['fpga_reconfigurations_per_node'][node['id']] = [processing_start_timestamp]
        else:
            metrics['fpga_reconfigurations_per_node'][node['id']].append(processing_start_timestamp)

    node['recent_fpga_reconfiguration_count'].add(processing_start_timestamp, 1)
    node['recent_fpga_reconfiguration_time'].add(processing_start_timestamp, FPGA_RECONFIGURATION_TIME)

    nodes[node['id']] = node

    return False, needs_reconfiguration, slot_key
