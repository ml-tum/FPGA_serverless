import newrelic.agent
import datetime
from collections import deque

class GenericUsageTimeTracker:
    def __init__(self, retention_period=datetime.timedelta(minutes=5)):
        self.window = deque()
        self.last_decay = None
        self.window_value = 0
        self.retention_period = retention_period

    def add(self, ts, value):
        if len(self.window) > 0 and (self.last_decay is None or (ts - self.last_decay).total_seconds() > self.retention_period.total_seconds()):
            self.decay(ts)

        self.window.append((ts, value))
        self.window_value += value

    def decay(self, newest_ts):
        self.last_decay = newest_ts
        while True:
            if len(self.window) == 0:
                break

            ts, value = self.window[0]

            if ts > newest_ts - self.retention_period:
                break

            self.window_value -= value
            self.window.popleft()

    def get_window_value(self):
        return self.window_value

class FPGAUsageTimeTracker(GenericUsageTimeTracker):
    pass


# we track both time and count but time is more important as it respects varying reconfiguration times
# (e.g. on devices with smaller slots, reconfigurations are expected to take less time)
class FPGAReconfigurationTimeTracker(GenericUsageTimeTracker):
    pass

class FPGAReconfigurationCountTracker(GenericUsageTimeTracker):
    pass

class BaselineUtilizationTracker(GenericUsageTimeTracker):
    pass