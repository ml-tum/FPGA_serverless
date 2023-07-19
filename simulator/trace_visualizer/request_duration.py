import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

input_file = "../AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt"

# Load the data from the CSV file
df = pd.read_csv(input_file)

# Convert the end_timestamp to a datetime object
df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], unit='s')

print(df['duration'].describe())

df = df[df['duration'] > 0]

print(df['duration'].describe())


median_duration_rounded = round(df['duration'].median(), 2)
p95_duration_rounded = round(df['duration'].quantile(0.95), 2)
p99_duration_rounded = round(df['duration'].quantile(0.99), 2)

print("Min duration: {}s".format(df['duration'].min()))
print("Max duration: {}s".format(df['duration'].max()))
print("p10 duration: {}ms".format((df['duration'].quantile(0.1)) * 1000))
print("p25 duration: {}ms".format((df['duration'].quantile(0.25)) * 1000))
print("p50 duration: {}ms".format((df['duration'].quantile(0.5)) * 1000))
print("p75 duration: {}ms".format((df['duration'].quantile(0.75)) * 1000))
print("p95 duration: {}ms".format(df['duration'].quantile(0.95) * 1000))

# plot sub-second requests as cdf line
print(df['duration'].describe())
hist, bins = np.histogram(df['duration'], bins="auto", density=True)
cdf = np.cumsum(hist)
cdf = cdf / cdf[-1]

# get example values
testMedianBin = round(bins[np.where(cdf > 0.5)][0],3)
print("40% of requests are faster than {}s".format(round(bins[np.where(cdf >= 0.4)][0],3)))
print("50% of requests are faster than {}s".format(round(testMedianBin,3)))
print("60% of requests are faster than {}s".format(round(bins[np.where(cdf >= 0.6)][0],3)))
print("80% of requests are faster than {}s".format(round(bins[np.where(cdf >= 0.8)][0],3)))
print("90% of requests are faster than {}s".format(round(bins[np.where(cdf >= 0.9)][0],3)))
print("95% of requests are faster than {}s".format(round(bins[np.where(cdf >= 0.95)][0],3)))
print("99% of requests are faster than {}s".format(round(bins[np.where(cdf >= 0.99)][0],3)))

# plot request timeline
def plot_requests():
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    # plot request duration as histogram, but instead of number of requests, show percentage of requests
    weights = np.ones_like(df['duration']) / len(df['duration'])
    axs[0].hist(df['duration'], weights=weights, bins=20, color='blue', alpha=0.7, range=(0, 80))

    # capture all values > 80
    greater_than_80 = df['duration'] > 80
    cumul_value = greater_than_80.sum() / len(df['duration'])
    axs[0].bar(86, cumul_value, color='gray', hatch='/', edgecolor='black', width=3.5)

    axs[0].set_xlabel('Request duration (s)')
    axs[0].set_ylabel('% of requests')
    axs[0].set_title('Request duration')

    # limit x range to 0 - 100s
    axs[0].set_xlim(0, 90)  # Adjust xlim to fit in the extra bar

    # set ticks and labels to include >80
    ticks = list(range(0, 81, 10)) + [86]
    labels = [str(tick) for tick in ticks[:-1]] + ['80+']
    axs[0].set_xticks(ticks)
    axs[0].set_xticklabels(labels)


    axs[0].set_yscale('function', functions=(lambda x: x ** 0.5, lambda x: x ** 2))
    axs[0].yaxis.set_major_formatter(PercentFormatter(xmax=1))

    axs[0].set_yticks([0.01, 0.05, 0.1, 0.2, 0.4,0.6,0.8,1])

    axs[0].axvline(x=df['duration'].median(), color='red', linestyle='dashed', linewidth=2,
                   label='median ({}s)'.format(median_duration_rounded))
    axs[0].axvline(x=df['duration'].quantile(0.95), color='orange', linestyle='dashed', linewidth=2,
                   label='p95 ({}s)'.format(p95_duration_rounded))
    axs[0].axvline(x=df['duration'].quantile(0.99), color='green', linestyle='dashed', linewidth=2,
                   label='p99 ({}s)'.format(p99_duration_rounded))

    # show legend in center top
    axs[0].legend(loc='upper center')





    axs[1].plot(bins[1:], cdf, color='blue', alpha=0.7, linewidth=2)
    axs[1].set_xlabel('Request duration (s)')
    axs[1].set_ylabel('Cumulative Distribution Function (CDF)')
    axs[1].set_xticks(np.arange(0, 1.1, 0.1))
    axs[1].set_title('Request duration < 1s')
    axs[1].fill_between(bins[1:], cdf, alpha=0)
    axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))

    # add median line just until cdf reaches 0.5
    data_median = df['duration'].median()
    data_p75 = df['duration'].quantile(0.75)

    axs[1].plot([0, data_median], [0.5, 0.5], color='red',alpha=0.5, linewidth=2, linestyle='dashed')  # Horizontal line
    axs[1].plot([data_median, data_median], [0, 0.5], color='red',alpha=0.5, linewidth=2, linestyle='dashed',
                label='median ({}s)'.format(round(data_median, 2)))  # Vertical line

    axs[1].plot([0, data_p75], [0.75, 0.75], color='purple', alpha=0.5, linewidth=2,
                linestyle='dashed')  # Horizontal line
    axs[1].plot([data_p75, data_p75], [0, 0.75], color='purple', alpha=0.5, linewidth=2, linestyle='dashed',
                label='p75 ({}s)'.format(round(data_p75, 2)))  # Vertical line


    axs[1].legend()

    # limit x range to 0 - 1s
    axs[1].set_xlim(0, 1)
    axs[1].set_ylim(0, 1)


    fig.suptitle('Request duration distribution', fontsize=16)

    plt.tight_layout()

plot_requests()
plt.show()

plot_requests()
plt.savefig('../../../figures/traces_request_duration.png')
