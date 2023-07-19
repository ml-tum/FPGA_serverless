import datetime

import simulator
import unittest

class TestNextBestNode(unittest.TestCase):
    def test_next_best_node(self):
        nodes = {}

        node0 = simulator.create_node(nodes)
        node0['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 40)
        node0['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)


        node1 = simulator.create_node(nodes)
        node1['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 20)
        node1['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node1['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)

        node2 = simulator.create_node(nodes)
        node2['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 60)
        node2['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node2['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node2['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)

        best = simulator.next_best_node(nodes, 'test', 1, 1, 1)

        self.assertEqual(best['id'], node0['id'])

    def test_next_best_node_only_one(self):
        nodes = {}

        node0 = simulator.create_node(nodes)
        node0['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 40)
        node0['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)

        best = simulator.next_best_node(nodes, 'test', 1, 1, 1)

        self.assertEqual(best['id'], node0['id'])



    def test_next_best_node_bitstream(self):
        nodes = {}

        node0 = simulator.create_node(nodes)
        node0['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 40)
        node0['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node0['recent_baseline_utilization'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 40)
        node0['bitstreams'] = set()

        node1 = simulator.create_node(nodes)
        node1['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 20)
        node1['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node1['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node1['recent_baseline_utilization'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 20)
        node1['bitstreams'] = {'test'}

        node2 = simulator.create_node(nodes)
        node2['recent_fpga_usage_time'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 60)
        node2['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node2['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node2['recent_fpga_reconfiguration_time'].add_reconfiguration(datetime.datetime(2023, 5, 12, 9, 0, 0), 3)
        node2['recent_baseline_utilization'].capture_request(datetime.datetime(2023, 5, 12, 9, 0, 0), 60)
        node2['bitstreams'] = set()

        best = simulator.next_best_node(nodes, 'test', 1, 1, 1)

        self.assertEqual(best['id'], node1['id'])