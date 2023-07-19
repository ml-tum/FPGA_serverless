import datetime
from queue import PriorityQueue


class FPGAUsageTimeTracker:
    def __init__(self):
        self.node_data = {'recent_usage_time': 0, 'timestamps': PriorityQueue()}

    def capture_request(self, end_timestamp: datetime.datetime, fpga_duration: float):
        prev_usage_time = round(self.node_data['recent_usage_time'],2)
        self.node_data['recent_usage_time'] = round(prev_usage_time + fpga_duration, 2)
        self.node_data['timestamps'].put((end_timestamp, round(fpga_duration, 2)))

    def decay(self, current_time: datetime.datetime):
        while True:
            if self.node_data['timestamps'].empty():
                break

            oldest_request = self.node_data['timestamps'].queue[0][0]
            delta = current_time - oldest_request
            if delta.seconds < 60 * 5:
                break

            _, processing_time = self.node_data['timestamps'].get()
            prev_usage_time = round(self.node_data['recent_usage_time'],2)
            self.node_data['recent_usage_time'] = round(prev_usage_time - processing_time, 2)
            if self.node_data['recent_usage_time'] < 0:
                self.node_data['recent_usage_time'] = 0

    def get_recent_usage_time(self):
        return self.node_data['recent_usage_time']


# we track both time and count but time is more important as it respects varying reconfiguration times
# (e.g. on devices with smaller slots, reconfigurations are expected to take less time)
class FPGAReconfigurationTimeTracker:
    def __init__(self, cutoff_delay = 60 * 5):
        self.node_data = {'recent_reconfiguration_time': 0, 'timestamps': PriorityQueue()}
        self.cutoff_delay = cutoff_delay

    def add_reconfiguration(self, end_timestamp: datetime.datetime, reconfiguration_duration: float):
        prev_reconfiguration_time = round(self.node_data['recent_reconfiguration_time'], 2)
        self.node_data['recent_reconfiguration_time'] = round(prev_reconfiguration_time + reconfiguration_duration, 2)
        self.node_data['timestamps'].put((end_timestamp, round(reconfiguration_duration, 2)))

    def decay(self, current_time: datetime.datetime):
        while True:
            if self.node_data['timestamps'].empty():
                break

            oldest_request = self.node_data['timestamps'].queue[0][0]
            delta = current_time - oldest_request
            if delta.seconds < self.cutoff_delay:
                break

            _, processing_time = self.node_data['timestamps'].get()
            prev_reconfiguration_time = round(self.node_data['recent_reconfiguration_time'], 2)
            self.node_data['recent_reconfiguration_time'] = round(prev_reconfiguration_time - processing_time, 2)
            if self.node_data['recent_reconfiguration_time'] < 0:
                self.node_data['recent_reconfiguration_time'] = 0

    def get_recent_reconfiguration_time(self):
        return self.node_data['recent_reconfiguration_time']

class FPGAReconfigurationCountTracker:
    def __init__(self, cutoff_delay = 60 * 5):
        self.node_data = {'recent_reconfigurations': 0, 'timestamps': PriorityQueue()}
        self.cutoff_delay = cutoff_delay

    def add_reconfiguration(self, end_timestamp: datetime.datetime):
        self.node_data['recent_reconfigurations'] += 1
        self.node_data['timestamps'].put(end_timestamp)

    def decay(self, current_time: datetime.datetime):
        while True:
            if self.node_data['timestamps'].empty():
                break

            oldest_request = self.node_data['timestamps'].queue[0]
            delta = current_time - oldest_request
            if delta.seconds < self.cutoff_delay:
                break

            _ = self.node_data['timestamps'].get()
            self.node_data['recent_reconfigurations'] -= 1
            if self.node_data['recent_reconfigurations'] < 0:
                self.node_data['recent_reconfigurations'] = 0

    def get_recent_reconfiguration_count(self):
        return self.node_data['recent_reconfigurations']