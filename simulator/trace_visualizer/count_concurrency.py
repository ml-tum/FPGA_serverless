import datetime

import preprocess
import simulator
import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from evaluation.data import characterized_collection


def group_and_plot(group_window_width_ms=1000):
    traces = preprocess.load_traces("../resampled.csv")

    preprocess.characterize_traces(characterized_collection(), traces)

    grouped_requests = preprocess.group_requests_by_time(traces, time_window_ms=group_window_width_ms)

    # draw aggregate bar chart of the number of concurrent requests (e.g. how many groups have 1 request, 2 requests, etc.)
    aggregate = [len(grouped_requests[time]) for time in grouped_requests]
    bin_edges = np.arange(0, max(aggregate) + 1.5) - 0.5

    fig, axs = plt.subplots(2, 2, figsize=(15, 15))

    fig.suptitle(
        f'Histogram of the number of concurrent requests (window group width={group_window_width_ms}ms)',
        fontsize=16)
    fig.tight_layout(pad=3.0)

    axs[0, 0].hist(aggregate, bins=bin_edges, edgecolor='black', linewidth=1.2)
    axs[0, 0].set_title("Request concurrency")
    axs[0, 0].set_xlabel("Number of concurrent requests")
    axs[0, 0].set_ylabel("Number of time windows")
    axs[0, 0].set_xlim(0, 100)

    axs[0, 1].hist(aggregate, bins=bin_edges, edgecolor='black', linewidth=1.2)
    axs[0, 1].set_title("Request concurrency (log)")
    axs[0, 1].set_xlabel("Number of concurrent requests")
    axs[0, 1].set_ylabel("Number of time windows (log)")
    axs[0, 1].set_yscale('log')
    axs[0, 1].set_xlim(0, 100)

    axs[1, 0].hist(aggregate, bins=bin_edges, edgecolor='black', linewidth=1.2)
    axs[1, 0].set_title("Request concurrency")
    axs[1, 0].set_xlabel("Number of concurrent requests")
    axs[1, 0].set_ylabel("Number of time windows")
    axs[1, 0].set_xlim(0, 25)
    axs[1, 0].set_xticks(np.arange(0, 26, 1))

    axs[1, 1].hist(aggregate, bins=bin_edges, edgecolor='black', linewidth=1.2)
    axs[1, 1].set_title("Request concurrency zoomed in (log)")
    axs[1, 1].set_xlabel("Number of concurrent requests")
    axs[1, 1].set_ylabel("Number of time windows (log)")
    axs[1, 1].set_yscale('log')
    axs[1, 1].set_xlim(0, 25)
    axs[1, 1].set_xticks(np.arange(0, 26, 1))


if __name__ == "__main__":
    group_and_plot(5)
    plt.savefig(f'concurrency_histogram_5ms.png')

    group_and_plot(10)
    plt.savefig(f'concurrency_histogram_10ms.png')

    group_and_plot(100)
    plt.savefig(f'concurrency_histogram_100ms.png')

    group_and_plot(1000)
    plt.savefig(f'concurrency_histogram_1000ms.png')
