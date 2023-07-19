import os

import simulator
import unittest


class TestPlacement(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        try:
            os.remove("/tmp/test_placement_basic.csv")
        except:
            pass
        try:
            os.remove("/tmp/test_placement_multi.csv")
        except:
            pass
        try:
            os.remove("/tmp/test_placement_2.csv")
        except:
            pass

    def test_placement_basic(self):
        # create temporary file in /tmp
        tmpFile = open("/tmp/test_placement_basic.csv", "w+")
        tmpFile.write("app,func,end_timestamp,duration\n")
        tmpFile.write("app1,func1,1,1\n")

        tmpFile.close()

        nodes, apps, metrics, coldstart_percent, time_spent_on_cold_starts, _ = simulator.run_on_file(
            csv_file_path="/tmp/test_placement_basic.csv",
            NUM_NODES=0, # auto-scale
            MAX_REQUESTS=0, # all requests
            FUNCTION_KEEPALIVE=1,
        )

        self.assertEqual(metrics['coldstarts'], 1)

    def test_placement_multi(self):
        # create temporary file in /tmp
        tmpFile = open("/tmp/test_placement_multi.csv", "w+")
        tmpFile.write("app,func,end_timestamp,duration\n")
        tmpFile.write("app1,func1,1,1\n")
        tmpFile.write("app2,func2,2,1\n")
        tmpFile.write("app1,func1,3,1\n")
        tmpFile.write("app2,func2,4,1\n")

        tmpFile.close()

        nodes, apps, metrics, coldstart_percent, time_spent_on_cold_starts, _ = simulator.run_on_file(
            csv_file_path="/tmp/test_placement_multi.csv",
            NUM_NODES=0, # auto-scale
            MAX_REQUESTS=0, # all requests
            FUNCTION_KEEPALIVE=1,
        )

        self.assertEqual(metrics['coldstarts'], 2)

    def test_placement_inefficient_lru(self):
        # create temporary file in /tmp
        tmpFile = open("/tmp/test_placement_2.csv", "w+")
        tmpFile.write("app,func,end_timestamp,duration\n")
        tmpFile.write("app1,func1,1,1\n")
        tmpFile.write("app2,func2,2,1\n")
        tmpFile.write("app3,func3,3,1\n")
        tmpFile.write("app1,func1,4,1\n")
        tmpFile.write("app2,func2,5,1\n")

        tmpFile.close()

        nodes, apps, metrics, coldstart_percent, time_spent_on_cold_starts, _ = simulator.run_on_file(
            csv_file_path="/tmp/test_placement_2.csv",
            NUM_NODES=0, # auto-scale
            MAX_REQUESTS=0, # all requests
            FUNCTION_KEEPALIVE=1,
            NUM_FPGA_SLOTS_PER_NODE=4,
            ENABLE_LOGS=True,
        )

        self.assertEqual(len(nodes), 1)
        self.assertEqual(metrics['coldstarts'], 5)