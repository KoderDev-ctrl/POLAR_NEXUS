import unittest
from polar_nexus.physics.cost_functions import PhysicsCostEngine

class TestCostFunctions(unittest.TestCase):

    def setUp(self):
        # 10 knots, 100 units of fuel/hr
        self.engine = PhysicsCostEngine(vessel_speed_knots=10.0, fuel_consumption_rate=100.0)

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        res = self.engine.evaluate_edge(distance_km=18.52, hazard_score=0.5, ice_concentration=0.0)
        # 10 knots = 18.52 km/h. Distance 18.52km -> 1 hour.
        self.assertAlmostEqual(res["time_hours"], 1.0)
        self.assertAlmostEqual(res["fuel_units"], 100.0)
        self.assertAlmostEqual(res["risk_score"], 9.26)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        # Heavy ice slows the ship and burns more fuel
        res = self.engine.evaluate_edge(distance_km=18.52, hazard_score=0.8, ice_concentration=85.0)
        # speed_mod = 0.3 -> time = 1.0 / 0.3 = 3.33 hours
        self.assertAlmostEqual(res["time_hours"], 1.0 / 0.3)
        # load_mod = 1.8 -> fuel = 3.33 * 100 * 1.8 = 600
        self.assertAlmostEqual(res["fuel_units"], (1.0 / 0.3) * 100.0 * 1.8)
        self.assertAlmostEqual(res["risk_score"], 18.52 * 0.8)

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Zero distance
        res = self.engine.evaluate_edge(distance_km=0.0, hazard_score=1.0, ice_concentration=100.0)
        self.assertAlmostEqual(res["time_hours"], 0.0)
        self.assertAlmostEqual(res["fuel_units"], 0.0)
        self.assertAlmostEqual(res["risk_score"], 0.0)

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Negative distance
        with self.assertRaises(ValueError):
            self.engine.compute_time_cost(-5.0)
            
        # Out of bounds hazard score
        with self.assertRaises(ValueError):
            self.engine.compute_risk_cost(10.0, 1.5)
            
        with self.assertRaises(ValueError):
            self.engine.compute_risk_cost(10.0, -0.1)

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Zero or negative speed modifier
        with self.assertRaises(ValueError) as ctx:
            self.engine.compute_time_cost(10.0, speed_modifier=0.0)
        self.assertTrue("strictly positive" in str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx:
            self.engine.compute_time_cost(10.0, speed_modifier=-1.0)

if __name__ == "__main__":
    unittest.main()
