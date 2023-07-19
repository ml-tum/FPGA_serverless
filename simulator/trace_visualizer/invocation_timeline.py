import datetime
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import simulator

register_matplotlib_converters()


input_file = "../AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt"

# Load the data from the CSV file
df = pd.read_csv(input_file)

sample_size = 20

unique_functions = df['func'].unique()

random.seed(42)
np.random.seed(42)

# Check if there are at least {sample_size} unique functions
if len(unique_functions) < sample_size:
    print(f"There are only {len(unique_functions)} unique functions. Cannot sample {sample_size}.")
else:
    # Randomly sample sample_size of them
    sample_functions_to_keep = np.random.choice(unique_functions, size=sample_size, replace=False)

    # Filter the DataFrame
    df = df[df['func'].isin(sample_functions_to_keep)]

    print(len(df['func'].unique()))  # should print {sample_size}


custom_epoch = datetime.datetime(2021, 1, 31)
unix_epoch = datetime.datetime(1970, 1, 1)
epoch_difference = custom_epoch - unix_epoch

df['end_timestamp'] = df['end_timestamp'].apply(lambda x: simulator.convert_end_timestamp_to_datetime(epoch_difference, x))
df['start_timestamp'] = df['end_timestamp'] - pd.to_timedelta(df['duration'], unit='s')

df = df.sort_values('start_timestamp', ascending=False)

def plot_timeline():
    plt.figure(figsize=(10, 5))

    # Create a list of functions
    functions = df['func'].unique()

    for i, function in enumerate(functions):
        function_data = df[df['func'] == function]
        plt.plot(function_data['start_timestamp'], [i] * len(function_data), label=function, marker='o')

    plt.yticks(range(len(functions)), functions)
    plt.xlabel('Time')
    plt.ylabel('Function')
    plt.title('Function Invocation Timeline')
    # make sure x axis is nice
    plt.gcf().autofmt_xdate()
    # only keep first 6 characters of each y tick label, use tick formatter
    plt.gca().yaxis.set_major_formatter(lambda x, pos: functions[int(x)][:6])



plot_timeline()
plt.show()

plot_timeline()
plt.savefig('../../../figures/traces_invocation_timeline.png')

