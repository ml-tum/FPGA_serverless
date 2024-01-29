import queue
from collections import deque
from datetime import timedelta, datetime
from csv import reader
import numpy as np


def convert_end_timestamp_to_datetime(end_timestamp):
    custom_epoch = datetime(2021, 1, 31)
    unix_epoch = datetime(1970, 1, 1)
    epoch_difference = custom_epoch - unix_epoch

    dt = datetime.fromtimestamp(float(end_timestamp) + epoch_difference.total_seconds())
    return dt


def load_traces(csv_file_path: str):
    # create request queue
    queue = deque()

    # Read the CSV file in a streaming manner
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            end_timestamp = convert_end_timestamp_to_datetime(row[2])
            row[2] = end_timestamp

            queue.append((row, end_timestamp))

    return queue


def characterize_traces(CHARACTERIZED_FUNCTIONS: dict, traces: deque):
    currentCount = len(traces)
    full_traces_list = list(traces.copy())

    previouslyCharacterized = dict()

    for i in range(currentCount):
        request = traces.popleft()
        row, end_timestamp = request

        app, func = row[0], row[1]

        # Characterize traces using information from CHARACTERIZED_FUNCTIONS
        # Do this once for every function (find all rows with the same function name, then characterize them, then move on to the next function)
        if func in previouslyCharacterized:
            fntype = previouslyCharacterized[func]
        else:
            fntype = characterize_func(func, CHARACTERIZED_FUNCTIONS, full_traces_list)
            previouslyCharacterized[func] = fntype

        traces.append((fntype, row, end_timestamp))


def calculate_avg_req_per_s(rows: list):
    # Extract end timestamps and durations
    end_timestamps = [row[2] for row in rows]
    durations = [float(row[3]) * 1000 for row in rows]

    # Calculate total duration
    total_duration = sum(durations)

    # Find the time range
    start_times = [end - timedelta(milliseconds=duration) for end, duration in zip(end_timestamps, durations)]
    time_range: float = ((max(end_timestamps) - min(start_times)).total_seconds()) * 1000

    # Calculate average requests per second
    avg_req_per_sec = total_duration / time_range if time_range > 0 else 0

    return avg_req_per_sec


def calculate_avg_req_duration(rows: list):
    return np.mean([row[3] * 1000 for row in rows])


def characterize_func(func: str, CHARACTERIZED_FUNCTIONS: dict, traces: list):
    # Find all rows with the same function name
    rows = [row for row in traces if row[1] == func]

    if len(rows) == 0:
        raise Exception(f"Could not find any rows with function name {func}")

    avg_req_per_sec = calculate_avg_req_per_s(rows)
    avg_req_duration = calculate_avg_req_duration(rows)

    # Extract ranges for normalization
    max_req_per_sec = max([characterization["characterization"]["avg_req_per_sec"] for characterization in
                           CHARACTERIZED_FUNCTIONS.values()])
    min_req_per_sec = min([characterization["characterization"]["avg_req_per_sec"] for characterization in
                           CHARACTERIZED_FUNCTIONS.values()])
    max_req_duration = max([characterization["characterization"]["avg_req_duration"] for characterization in
                            CHARACTERIZED_FUNCTIONS.values()])
    min_req_duration = min([characterization["characterization"]["avg_req_duration"] for characterization in
                            CHARACTERIZED_FUNCTIONS.values()])

    # Find the characterization that matches the closest
    best_match = None
    best_match_distance = float("inf")

    for fntype, characterization in CHARACTERIZED_FUNCTIONS.items():
        normalized_diff_req_per_sec = (characterization["characterization"]["avg_req_per_sec"] - avg_req_per_sec) / (
                max_req_per_sec - min_req_per_sec) if max_req_per_sec != min_req_per_sec else 0
        normalized_diff_req_duration = (characterization["characterization"]["avg_req_duration"] - avg_req_duration) / (
                max_req_duration - min_req_duration) if max_req_duration != min_req_duration else 0

        # Calculate the normalized distance
        distance = abs(normalized_diff_req_per_sec) + abs(normalized_diff_req_duration)

        if distance < best_match_distance:
            best_match = fntype
            best_match_distance = distance

    return best_match


def group_requests_by_time(queue, time_window_ms=10):
    grouped_requests = {}

    while queue:
        request = queue.popleft()
        fntype, row, end_timestamp = request
        window_start = end_timestamp
        window_end = end_timestamp + timedelta(milliseconds=time_window_ms)

        current_group = []
        current_group.append(request)

        while queue and queue[0][2] >= window_start and queue[0][2] < window_end:
            current_group.append(queue.popleft())

        grouped_requests[window_start] = current_group

    return grouped_requests


def apply_arrival_policy(queue: deque, ARRIVAL_POLICY: str, CHARACTERIZED_FUNCTIONS: dict):
    grouped_requests = group_requests_by_time(queue, time_window_ms=10)

    # Sort the time windows chronologically
    sorted_time_windows = sorted(grouped_requests.keys())

    # Create a final deque with sorted entries
    final_sorted_entries = deque()

    for time_window in sorted_time_windows:
        requests = grouped_requests[time_window]

        def sort_by_priority(request):
            fntype, row, end_timestamp = request
            return CHARACTERIZED_FUNCTIONS[fntype]["priority"]

        def sort_by_timestamp(request):
            fntype, row, end_timestamp = request
            return end_timestamp

        # Within each group, sort the requests according to the arrival policy
        if ARRIVAL_POLICY == "PRIORITY":
            sorted_requests = sorted(requests, key=sort_by_priority)
        elif ARRIVAL_POLICY == "FIFO":
            sorted_requests = sorted(requests, key=sort_by_timestamp)
        else:
            raise Exception(f"Unknown ARRIVAL_POLICY: {ARRIVAL_POLICY}")

        final_sorted_entries.extend(sorted_requests)

    return final_sorted_entries
