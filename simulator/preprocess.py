import newrelic.agent
import queue
from collections import deque
from datetime import timedelta, datetime
from csv import reader
import numpy as np
import pandas as pd

def convert_end_timestamp_to_datetime(end_timestamp):
    custom_epoch = datetime(2021, 1, 31)
    unix_epoch = datetime(1970, 1, 1)
    epoch_difference = custom_epoch - unix_epoch

    dt = datetime.fromtimestamp(float(end_timestamp) + epoch_difference.total_seconds())
    return dt


@newrelic.agent.function_trace()
def load_traces(csv_file_path: str, MAX_REQUESTS: int = 0):
    # create request queue
    queue = deque()

    # Read the CSV file in a streaming manner
    num=0
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            if MAX_REQUESTS is not None and MAX_REQUESTS > 0 and num > MAX_REQUESTS:
                return queue

            num += 1

            end_timestamp = convert_end_timestamp_to_datetime(row[2])
            row[2] = end_timestamp

            # convert duration to float
            row[3] = float(row[3])

            queue.append((row, end_timestamp))

    # overhead: 1.69GB -> 5.3GB (3.1x)
    return queue


@newrelic.agent.function_trace()
def characterize_traces(CHARACTERIZED_FUNCTIONS: dict, traces: deque):
    # optimization: compute characterization values ahead of time
    characterizations = CHARACTERIZED_FUNCTIONS.values()
    max_req_per_sec = max([characterization["characterization"]["avg_req_per_sec"] for characterization in
                           characterizations])
    min_req_per_sec = min([characterization["characterization"]["avg_req_per_sec"] for characterization in
                           characterizations])
    max_req_duration = max([characterization["characterization"]["avg_req_duration"] for characterization in
                            characterizations])
    min_req_duration = min([characterization["characterization"]["avg_req_duration"] for characterization in
                            characterizations])

    currentCount = len(traces)

    # optimization: compute rows for function ahead of time, store in cache (dict)
    full_traces_list = list(traces)
    rows_for_function = dict()
    for row in full_traces_list:
        row = row[0]

        func = row[1]

        if func not in rows_for_function:
            rows_for_function[func] = []
        rows_for_function[func].append(row)

    previouslyCharacterized = dict()

    # overhead: loops over 10m rows
    for i in range(currentCount):
        request = traces.popleft()
        row, end_timestamp = request

        app, func = row[0], row[1]

        # Characterize traces using information from CHARACTERIZED_FUNCTIONS
        # Do this once for every function (find all rows with the same function name, then characterize them, then move on to the next function)
        if func in previouslyCharacterized:
            fntype = previouslyCharacterized[func]
        else:
            fntype = characterize_func(CHARACTERIZED_FUNCTIONS, rows_for_function[func], max_req_per_sec,
                                       min_req_per_sec, max_req_duration, min_req_duration)
            previouslyCharacterized[func] = fntype

        traces.append((fntype, row, end_timestamp))

    return


def calculate_avg_req_per_s(rows: list):
    # Create a DataFrame from the rows
    df = pd.DataFrame(rows, columns=['app', 'func', 'end_timestamp', 'duration'])

    # Convert 'duration' from string to float
    df['duration'] = df['duration'].astype('float32')

    # Convert duration to milliseconds
    df['duration_ms'] = df['duration'] * 1000

    # Calculate start times
    df['start_timestamp'] = df['end_timestamp'] - pd.to_timedelta(df['duration_ms'], unit='ms')

    # Calculate total duration
    total_duration = df['duration_ms'].sum()

    # Calculate the time range in milliseconds
    time_range = (df['end_timestamp'].max() - df['start_timestamp'].min()).total_seconds() * 1000

    # Calculate average requests per second
    avg_req_per_sec = total_duration / time_range if time_range > 0 else 0

    return avg_req_per_sec


def calculate_avg_req_duration(rows: list):
    # Convert just the durations to a NumPy array
    durations = np.array([row[3] for row in rows])

    # Multiply all durations by 1000 in a vectorized operation
    durations_ms = durations * 1000

    # Calculate the mean using NumPy's mean function
    return np.mean(durations_ms)

def characterize_func(CHARACTERIZED_FUNCTIONS: dict, rows_for_function: list, max_req_per_sec: float, min_req_per_sec: float, max_req_duration: float, min_req_duration: float):
    avg_req_per_sec: float = calculate_avg_req_per_s(rows_for_function)
    avg_req_duration: float = calculate_avg_req_duration(rows_for_function)

    req_per_sec_range = max_req_per_sec - min_req_per_sec
    req_duration_range = max_req_duration - min_req_duration

    # Initialize normalized values
    normalized_req_per_sec = 0
    normalized_req_duration = 0

    # Normalize avg_req_per_sec, checking for division by zero
    if req_per_sec_range != 0:
        normalized_req_per_sec = (avg_req_per_sec - min_req_per_sec) / req_per_sec_range

    # Normalize avg_req_duration, checking for division by zero
    if req_duration_range != 0:
        normalized_req_duration = (avg_req_duration - min_req_duration) / req_duration_range

    normalized_metrics = np.array([normalized_req_per_sec, normalized_req_duration])

    # Extract characteristics from CHARACTERIZED_FUNCTIONS and normalize them
    characteristics = []
    for char in CHARACTERIZED_FUNCTIONS.values():
        char_avg_req_per_sec = char["characterization"]["avg_req_per_sec"]
        char_avg_req_duration = char["characterization"]["avg_req_duration"]

        # Handle division by zero
        normalized_char_req_per_sec = 0 if req_per_sec_range == 0 else (
                                                                                   char_avg_req_per_sec - min_req_per_sec) / req_per_sec_range
        normalized_char_req_duration = 0 if req_duration_range == 0 else (
                                                                                     char_avg_req_duration - min_req_duration) / req_duration_range

        characteristics.append([normalized_char_req_per_sec, normalized_char_req_duration])

    characteristics = np.array(characteristics)

    # Calculate Euclidean distances in a vectorized way
    distances = np.linalg.norm(characteristics - normalized_metrics, axis=1)

    # Find the index of the minimum distance
    closest_match_idx = np.argmin(distances)

    # Return the corresponding function type
    return list(CHARACTERIZED_FUNCTIONS.keys())[closest_match_idx]


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


@newrelic.agent.function_trace()
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
