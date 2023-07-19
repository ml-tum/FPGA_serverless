from unittest import TestCase
from datetime import datetime
from fpga_utilization import FPGAUsageTimeTracker

class TestFpgaUtilization(TestCase):
    def test_fpga_utilization(self):
        fpga_utilization = FPGAUsageTimeTracker()

        # test cases
        dates = [
            (datetime(2023, 5, 12, 9, 0, 0), 1),
            (datetime(2023, 5, 12, 9, 1, 0),1),
            (datetime(2023, 5, 12, 9, 2, 0),1),
            (datetime(2023, 5, 12, 9, 3, 0),1),
            (datetime(2023, 5, 12, 9, 4, 0),1)
        ]
        for date, duration in dates:
            fpga_utilization.capture_request(date, duration)

        # Get EMA FPGA utilization
        self.assertEqual(fpga_utilization.get_recent_usage_time(), 5)

    def test_decay(self):
        fpga_utilization = FPGAUsageTimeTracker()

        # test cases
        dates = [
            (datetime(2023, 5, 12, 8, 0, 0), 1),
            (datetime(2023, 5, 12, 8, 1, 0), 1),
            (datetime(2023, 5, 12, 8, 2, 0), 1),
            (datetime(2023, 5, 12, 8, 3, 0), 1),
            (datetime(2023, 5, 12, 8, 4, 0), 1),

            (datetime(2023, 5, 12, 9, 0, 0), 1),
            (datetime(2023, 5, 12, 9, 1, 0), 1),
            (datetime(2023, 5, 12, 9, 2, 0), 1),
            (datetime(2023, 5, 12, 9, 3, 0), 1),
            (datetime(2023, 5, 12, 9, 4, 0), 1)
        ]
        for date, duration in dates:
            fpga_utilization.capture_request(date, duration)

        fpga_utilization.decay(datetime(2023, 5, 12, 9, 4, 0))

        # Get EMA FPGA utilization
        self.assertEqual(fpga_utilization.get_recent_usage_time(), 5)

    def test_decay_threshold(self):
        fpga_utilization = FPGAUsageTimeTracker()

        # test cases
        dates = [
            # decay
            (datetime(2023, 5, 12, 8, 4, 0), 1),
            (datetime(2023, 5, 12, 8, 5, 0), 1),

            # not decay
            (datetime(2023, 5, 12, 8, 6, 0), 1),
            (datetime(2023, 5, 12, 8, 9, 0), 1),
            (datetime(2023, 5, 12, 8, 10, 0), 1)
        ]
        for date, duration in dates:
            fpga_utilization.capture_request(date, duration)

        fpga_utilization.decay(datetime(2023, 5, 12, 8, 10, 0))

        # Get EMA FPGA utilization
        self.assertEqual(3, fpga_utilization.get_recent_usage_time())

    def test_decay_threshold_2(self):
        fpga_utilization = FPGAUsageTimeTracker()

        # test cases
        dates = [
            (datetime(2023, 5, 12, 8, 4, 0), 1),

            (datetime(2023, 5, 12, 9, 4, 0), 1)
        ]
        for date, duration in dates:
            fpga_utilization.capture_request(date, duration)

        fpga_utilization.decay(datetime(2023, 5, 12, 9, 4, 0))

        # Get EMA FPGA utilization
        self.assertEqual(fpga_utilization.get_recent_usage_time(), 1)