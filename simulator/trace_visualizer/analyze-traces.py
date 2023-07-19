# stream csv
# the schema is as follows: app,func,end_timestamp,duration

import csv
import datetime
import random

import simulator

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

input_file = "../AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt"


apps = set()
funcs = set()
requests = []
app_requests = {}
app_durations = {}
func_requests = {}
funcs_per_app = {}
func_durations = {}


with open(input_file, "r") as csv_file:
    custom_epoch = datetime.datetime(2021, 1, 31)
    unix_epoch = datetime.datetime(1970, 1, 1)
    epoch_difference = custom_epoch - unix_epoch

    csv_reader = csv.reader(csv_file, delimiter=',')
    num_requests = 0

    for row in csv_reader:
        if num_requests == 0:
            print(f'Column names are {", ".join(row)}')
            print(row)
            num_requests += 1
        else:
            app, func, end_timestamp, duration = row

            end_timestamp = simulator.convert_end_timestamp_to_datetime(epoch_difference, end_timestamp)

            start_timestamp = end_timestamp - datetime.timedelta(seconds=float(duration))

            requests.append((app, func, start_timestamp, end_timestamp, duration))

            num_requests += 1
            apps.add(row[0])
            funcs.add(row[1])

            if app in app_requests:
                app_requests[app] += 1
            else:
                app_requests[app] = 1

            if func in func_requests:
                func_requests[func] += 1
            else:
                func_requests[func] = 1

            if app in funcs_per_app:
                funcs_per_app[app].add(func)
            else:
                funcs_per_app[app] = {func}

            if func in func_durations:
                func_durations[func].append(float(duration))
            else:
                func_durations[func] = [float(duration)]

            if app in app_durations:
                app_durations[app].append(float(duration))
            else:
                app_durations[app] = [float(duration)]
    num_requests -= 1
    print(f'Processed {num_requests} lines.')
    print(f'Total {num_requests} requests, {len(apps)} distinct apps, {len(funcs)} distinct functions.')

    # Calculate the average duration per function
    avg_func_durations = {}
    for func, durations in func_durations.items():
        avg_func_durations[func] = sum(durations) / len(durations)

    # Calculate the average duration per app
    avg_app_durations = {}
    for app, durations in app_durations.items():
        avg_app_durations[app] = sum(durations) / len(durations)

    print("Requests per app")
    s = pd.Series(list(app_requests.values()))
    print(s.describe())

    print("Requests per function")
    s = pd.Series(list(func_requests.values()))
    print(s.describe())

    print("Functions per app")
    s = pd.Series([len(funcs) for funcs in funcs_per_app.values()])
    print(s.describe())

    print("Average duration per function")
    s = pd.Series(list(avg_func_durations.values()))
    print(s.describe())

    print("Average duration per app")
    s = pd.Series(list(avg_app_durations.values()))
    print(s.describe())

# Load the data from the CSV file
df = pd.read_csv(input_file)

# Convert the end_timestamp to a datetime object
df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], unit='s')

# Resample the data to a per-minute basis
df_resampled_minute = df.set_index('end_timestamp').resample('1T')

# Count the number of requests per minute for each function
invocation_rate_per_min = df_resampled_minute['func'].value_counts()

df_resampled_hour = df.set_index('end_timestamp').resample('1H')
invocation_rate_per_hour = df_resampled_hour['func'].value_counts()


# plot request timeline
def plot_requests():
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))

    axs[0].hist(invocation_rate_per_min, bins=100, color='blue', alpha=0.7)
    axs[0].set_title('Invocation Rate per Minute')
    axs[0].set_xlabel('Number of Invocations')
    axs[0].set_ylabel('Number of Minutes')
    axs[0].grid(axis='y', alpha=0.75)
    # limit to 1000
    axs[0].set_xlim(0, 1000)

    axs[1].hist(invocation_rate_per_hour, bins=100, color='blue', alpha=0.7)
    axs[1].set_title('Invocation Rate per Hour')
    axs[1].set_xlabel('Number of Invocations')
    axs[1].set_ylabel('Number of Hours')
    axs[1].grid(axis='y', alpha=0.75)
    # limit to 1000
    axs[1].set_xlim(0, 1000)

    plt.tight_layout()
    plt.show()

plot_requests()