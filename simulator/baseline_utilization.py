import datetime
from queue import PriorityQueue


class BaselineUtilizationTracker:
    def __init__(self):
        self.node_data = {'recent_compute_time': 0, 'timestamps': PriorityQueue()}

    def capture_request(self, end_timestamp: datetime.datetime, fpga_duration: float):
        prev_compute_time = round(self.node_data['recent_compute_time'], 2)
        self.node_data['recent_compute_time'] = round(prev_compute_time + fpga_duration, 2)
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
            prev_compute_time = round(self.node_data['recent_compute_time'], 2)
            self.node_data['recent_compute_time'] = round(prev_compute_time - processing_time, 2)
            if self.node_data['recent_compute_time'] < 0:
                self.node_data['recent_compute_time'] = 0

    def get_recent_compute_time(self):
        return self.node_data['recent_compute_time']


