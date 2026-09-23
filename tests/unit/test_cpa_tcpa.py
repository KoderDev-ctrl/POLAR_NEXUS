import unittest
from polar_nexus.risk.route_specific.cpa_tcpa import RouteRiskCalculator

class TestCPATCPA(unittest.TestCase):
    def setUp(self):
        self.calculator = RouteRiskCalculator(safe_distance_threshold=5.0)
        self.vessel_speed = 1.0

    # TEST 1 - Normal valid input (Safe distance)
    def test_normal_valid_input(self):
        route = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
        icebergs = [{'trajectory': [(10.0, 10.0), (11.0, 11.0), (12.0, 12.0)]}]
        
        result = self.calculator.compute_cpa_tcpa(route, self.vessel_speed, icebergs)
        self.assertGreater(result['min_cpa'], 5.0)
        self.assertEqual(result['route_risk_score'], 0.0)

    # TEST 2 - Different valid input (Collision course)
    def test_different_valid_input(self):
        route = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
        icebergs = [{'trajectory': [(2.0, 0.0), (1.0, 1.0), (0.0, 2.0)]}] # Intersects at (1,1) at t=1
        
        result = self.calculator.compute_cpa_tcpa(route, self.vessel_speed, icebergs)
        self.assertEqual(result['min_cpa'], 0.0)
        self.assertEqual(result['min_tcpa'], 1.0)
        self.assertEqual(result['route_risk_score'], 100.0) # Max risk for 0 CPA

    # TEST 3 - Boundary condition (Exactly on threshold)
    def test_boundary_condition(self):
        route = [(0.0, 0.0)]
        icebergs = [{'trajectory': [(5.0, 0.0)]}] # Dist = 5.0
        
        result = self.calculator.compute_cpa_tcpa(route, self.vessel_speed, icebergs)
        self.assertEqual(result['min_cpa'], 5.0)
        self.assertEqual(result['route_risk_score'], 0.0) # Threshold is strictly less than

    # TEST 4 - Adversarial input
    def test_invalid_adversarial_input(self):
        # Empty route or empty icebergs
        res1 = self.calculator.compute_cpa_tcpa([], self.vessel_speed, [{'trajectory': [(1,1)]}])
        res2 = self.calculator.compute_cpa_tcpa([(0,0)], self.vessel_speed, [])
        res3 = self.calculator.compute_cpa_tcpa([(0,0)], self.vessel_speed, [{}]) # Missing trajectory
        
        self.assertEqual(res1['min_cpa'], float('inf'))
        self.assertEqual(res2['min_cpa'], float('inf'))
        self.assertEqual(res3['min_cpa'], float('inf'))

    # TEST 5 - Edge case / Failure condition
    def test_edge_case_failure(self):
        # Iceberg trajectory is much shorter than route (should handle mismatched lengths gracefully)
        route = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
        icebergs = [{'trajectory': [(0.5, 0.5)]}] # Only 1 point
        
        result = self.calculator.compute_cpa_tcpa(route, self.vessel_speed, icebergs)
        # Should compare at t=0: dist((0,0), (0.5,0.5)) = sqrt(0.5) = 0.707
        self.assertAlmostEqual(result['min_cpa'], 0.707106, places=5)
        self.assertGreater(result['route_risk_score'], 0.0)

if __name__ == "__main__":
    unittest.main()
