import simulator
import unittest

class TestScoreNode(unittest.TestCase):
    def test_score_simple(self):
        nodes = [
            # node id, utilization, reconfigurations, has_fitting_bitstream, baseline_utilization
            (0, 0, 0, 1, 1),
            (1, 1, 0, 1, 1),
            (2, 0, 1, 1, 1),
            (3, 1, 1, 1, 1)
        ]

        sortedByUtilizations = nodes.copy()
        sortedByUtilizations.sort(key=lambda x: x[1])

        sortedByReconfigurations = nodes.copy()
        sortedByReconfigurations.sort(key=lambda x: x[2])

        sortedByBaselineUtilization = nodes.copy()
        sortedByBaselineUtilization.sort(key=lambda x: x[4])

        # (1 + 1 + 1) / 3 = 1
        self.assertEqual(simulator.score_node(
            sorted_fpga_usage_time=sortedByUtilizations,
            sorted_fpga_reconfiguration_time=sortedByReconfigurations,
            sorted_baseline_utilization=sortedByBaselineUtilization,
            nodeId=nodes[0][0],
            has_fitting_bitstream=nodes[0][3],
            baseline_utilization_weight=0,
        ), 1)

        # (0.5 + 0.75 + 1) / 3 = 0.75
        self.assertEqual(simulator.score_node(
            sorted_fpga_usage_time=sortedByUtilizations,
            sorted_fpga_reconfiguration_time=sortedByReconfigurations,
            sorted_baseline_utilization=sortedByBaselineUtilization,
            nodeId=nodes[1][0],
            has_fitting_bitstream=nodes[1][3],
            baseline_utilization_weight=0,
        ), 0.75)

        # (0.75 + 0.5 + 1) / 3 = 0.75
        self.assertEqual(simulator.score_node(
            sorted_fpga_usage_time=sortedByUtilizations,
            sorted_fpga_reconfiguration_time=sortedByReconfigurations,
            sorted_baseline_utilization=sortedByBaselineUtilization,
            nodeId=nodes[2][0],
            has_fitting_bitstream=nodes[2][3],
            baseline_utilization_weight=0,
        ), 0.75)

        # (0.25 + 0.25 + 1) / 3 = 0.5
        self.assertEqual(simulator.score_node(
            sorted_fpga_usage_time=sortedByUtilizations,
            sorted_fpga_reconfiguration_time=sortedByReconfigurations,
            sorted_baseline_utilization=sortedByBaselineUtilization,
            nodeId=nodes[3][0],
            has_fitting_bitstream=nodes[3][3],
            baseline_utilization_weight=0,
        ), 0.5)

