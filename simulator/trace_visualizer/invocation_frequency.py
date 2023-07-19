import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

input_file = "../AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt"

# Load the data from the CSV file
df = pd.read_csv(input_file)

print("{} requests".format(df.count()))

df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], unit='s')
df.set_index('end_timestamp', inplace=True)

# Resample DataFrame to minute intervals and count number of function invocations
invocations_per_minute = df.resample('1T').count()

# Calculate the requests per minute
invocations_per_minute['requests_per_minute'] = invocations_per_minute['func'] / (60)

invocations_per_hour = df.resample('1H').count()
invocations_per_hour['requests_per_hour'] = invocations_per_hour['func'] / (60 * 60)

# Create a histogram of the invocation frequency, including apps with fewer than 1 request per minute
weights_min = np.ones_like(invocations_per_minute['requests_per_minute']) / len(invocations_per_minute['requests_per_minute'])

weights_hour = np.ones_like(invocations_per_hour['requests_per_hour']) / len(invocations_per_hour['requests_per_hour'])

invocations_per_minute_median = invocations_per_minute['requests_per_minute'].median()
invocations_per_minute_p75 = invocations_per_minute['requests_per_minute'].quantile(0.75)

invocations_per_hour_median = invocations_per_hour['requests_per_hour'].median()
invocations_per_hour_p75 = invocations_per_hour['requests_per_hour'].quantile(0.75)

def plot_requests():
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    n, bins, patches = axs[0].hist(invocations_per_minute['requests_per_minute'], bins=20, edgecolor='black',
                                   weights=weights_min, range=(0, 20), color='blue', alpha=0.7)
    # capture all values > 20
    greater_than_20 = invocations_per_minute['requests_per_minute'] > 20
    cumul_value = greater_than_20.sum() / len(invocations_per_minute['requests_per_minute'])
    axs[0].bar(22, cumul_value, color='gray', hatch='/', edgecolor='black')  # Add bar with cumulative values

    axs[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axs[0].set_xlabel('Invocations per minute')
    axs[0].set_ylabel('% of functions')
    axs[0].set_xlim(0, 23)  # Include extra bar

    ticks = list(range(0, 21, 2)) + [22]  # Include extra tick
    labels = [str(tick) for tick in ticks[:-1]] + ['20+']
    axs[0].set_xticks(ticks)
    axs[0].set_xticklabels(labels)

    axs[0].axvline(x=invocations_per_minute_median, color='red', linestyle='dashed', linewidth=2,
                   label='median ({})'.format(round(invocations_per_minute_median, 2)))
    axs[0].axvline(x=invocations_per_minute_p75, color='orange', linestyle='dashed', linewidth=2,
                   label='75th percentile ({})'.format(round(invocations_per_minute_p75, 2)))

    axs[0].legend()

    n, bins, patches = axs[1].hist(invocations_per_hour['requests_per_hour'], bins=20, edgecolor='black',
                                   weights=weights_hour, range=(0, 20), color='blue', alpha=0.7)
    # capture all values > 20
    greater_than_20 = invocations_per_hour['requests_per_hour'] > 20
    cumul_value = greater_than_20.sum() / len(invocations_per_hour['requests_per_hour'])
    axs[1].bar(22, cumul_value, color='gray', hatch='/', edgecolor='black')  # Add bar with cumulative values

    axs[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axs[1].set_xlabel('Invocations per hour')
    axs[1].set_ylabel('% of functions')
    axs[1].set_xlim(0, 23)  # Include extra bar

    ticks = list(range(0, 21, 2)) + [22]  # Include extra tick
    labels = [str(tick) for tick in ticks[:-1]] + ['20+']
    axs[1].set_xticks(ticks)
    axs[1].set_xticklabels(labels)

    axs[1].axvline(x=invocations_per_hour_median, color='red', linestyle='dashed', linewidth=2,
                   label='median ({})'.format(round(invocations_per_hour_median, 2)))
    axs[1].axvline(x=invocations_per_hour_p75, color='orange', linestyle='dashed', linewidth=2,
                   label='75th percentile ({})'.format(round(invocations_per_hour_p75, 2)))

    axs[1].legend()

    plt.suptitle('Invocation frequency distribution', fontsize=16)

    plt.tight_layout()

plot_requests()
plt.show()

plot_requests()
plt.savefig('../../../figures/traces_invocation_frequency_distribution.png', dpi=300)
