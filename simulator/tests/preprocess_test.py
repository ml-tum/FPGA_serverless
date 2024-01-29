import collections
from unittest import TestCase
from datetime import datetime
import preprocess


class TestPreprocess(TestCase):
    def test_group_requests_by_time(self):
        queue = collections.deque()

        # create requests within 10ms
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 5)))

        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 10)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 15)))

        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 20)))

        grouped = preprocess.group_requests_by_time(queue)

        self.assertEqual(len(grouped), 3)
        self.assertEqual(len(grouped[datetime(2023, 5, 12, 9, 0, 0)]), 2)
        self.assertEqual(len(grouped[datetime(2023, 5, 12, 9, 0, 0, 1000 * 10)]), 2)
        self.assertEqual(len(grouped[datetime(2023, 5, 12, 9, 0, 0, 1000 * 20)]), 1)

        # create requests within 10ms
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 5)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 9)))

        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 10)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 15)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 19)))

        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 20)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 26)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 26)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 28)))
        queue.append((1, 1, datetime(2023, 5, 12, 9, 0, 0, 1000 * 29)))

        grouped = preprocess.group_requests_by_time(queue)

        self.assertEqual(len(grouped), 3)
        self.assertEqual(len(grouped[datetime(2023, 5, 12, 9, 0, 0)]), 3)
        self.assertEqual(len(grouped[datetime(2023, 5, 12, 9, 0, 0, 1000 * 10)]), 3)
        self.assertEqual(len(grouped[datetime(2023, 5, 12, 9, 0, 0, 1000 * 20)]), 5)

    def test_characterize_func(self):
        CHARACTERIZED_FUNCTIONS = {
            # these are characterized functions
            1: {
                # an average function that benefits somewhat from being on the FPGA
                "label": "f1",
                "mean_speedup": 0.8,  # 80% of original duration
                "run_on_fpga": True,
                "fpga_ratio": 0.5,
                "characterization": {
                    "avg_req_per_sec": 1,
                    "avg_req_duration": 50,
                }
            },
            2: {
                # a frequently-called function that somewhat benefits from being on the FPGA
                "label": "f2",
                "mean_speedup": 0.95,  # 95% of original duration
                "run_on_fpga": True,
                "fpga_ratio": 0.5,
                "characterization": {
                    "avg_req_per_sec": 2,
                    "avg_req_duration": 10,
                }
            },
            3: {
                # a slow-running function that benefits strongly from being run on the FPGA
                "label": "f3",
                "mean_speedup": 0.5,  # 50% of original duration
                "run_on_fpga": True,
                "fpga_ratio": 0.8,
                "characterization": {
                    "avg_req_per_sec": 1,
                    "avg_req_duration": 1000,
                }
            }
        }

        queue = collections.deque()

        # create requests within 10ms
        duration_s = 10 / 1000
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 0, 1000 * 5), duration_s))
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 0, 1000 * 5), duration_s))
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 0, 1000 * 20), duration_s))
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 0, 1000 * 20), duration_s))

        self.assertEqual(2, preprocess.characterize_func("func1", CHARACTERIZED_FUNCTIONS, list(queue)))

        queue = collections.deque()
        duration_s = 50 / 1000
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 0, 1000 * 5), duration_s))
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 2, 1000 * 20), duration_s))
        self.assertEqual(1, preprocess.characterize_func("func1", CHARACTERIZED_FUNCTIONS, list(queue)))

        queue = collections.deque()
        duration_s = 1000 / 1000
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 0, 1000 * 5), duration_s))
        queue.append(("app1", "func1", datetime(2023, 5, 12, 9, 0, 2, 1000 * 20), duration_s))
        self.assertEqual(3, preprocess.characterize_func("func1", CHARACTERIZED_FUNCTIONS, list(queue)))
