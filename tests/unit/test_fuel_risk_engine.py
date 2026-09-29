import unittest
import numpy as np
from polar_nexus.routex16.engines.fuel_risk_engine import FuelRiskEngine
from polar_nexus.routex16.cost_layer import RouteCostLayer

class TestFuelRiskEngine(unittest.TestCase):

    def setUp(self):
        env_data = {'current_u': np.zeros((100,100)), 'current_v': np.zeros((100,100)), 'ice_conc': np.zeros((100,100)), 'hazard_field': np.zeros((100,100))}
        vessel_profile = {'base_speed_kts': 10.0, 'base_fuel_consumption_kg_h': 100.0}
        self.cost_engine = RouteCostLayer(env_data, vessel_profile)
        self.engine = FuelRiskEngine(self.cost_engine)
        self.start = (0.0, 0.0)
        self.dest = (10.0, 10.0)
        self.grid = np.zeros((20, 20))

    # TEST 1 - Normal valid input & Algorithm Diversity Check
    def test_normal_valid_input_and_diversity(self):
        candidates = self.engine.generate_candidates(self.start, self.dest, self.grid)
        self.assertEqual(len(candidates), 4)
        
        # Ensure all 4 algorithms produce measurably different candidate outputs
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                self.assertNotEqual(candidates[i], candidates[j], 
                                    f"Algorithms {i} and {j} produced identical paths! Architecture violation.")
        
        for path in candidates:
            self.assertEqual(path.geometry[0], self.start)
            self.assertEqual(path.geometry[-1], self.dest)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        start2 = (5.0, 5.0)
        dest2 = (15.0, 5.0)
        candidates = self.engine.generate_candidates(start2, dest2, self.grid)
        self.assertEqual(len(candidates), 4)

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Start equals destination
        candidates = self.engine.generate_candidates(self.start, self.start, self.grid)
        for path in candidates:
            self.assertEqual(path.geometry[-1], self.start)

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        candidates = self.engine.generate_candidates((-9999.0, -9999.0), (9999.0, 9999.0), self.grid)
        self.assertEqual(len(candidates), 4)

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        candidates = self.engine.generate_candidates((-5.0, -5.0), (-1.0, -1.0), self.grid)
        self.assertEqual(len(candidates), 4)

    # TEST 6 - NSGA-II Pareto Front Diversity
    def test_nsga2_pareto_front_diversity(self):
        # Create a cost engine where risk varies spatially to force a trade-off
        env_data = {'current_u': np.zeros((100,100)), 'current_v': np.zeros((100,100)), 'ice_conc': np.zeros((100,100)), 'hazard_field': np.zeros((100,100))}
        
        # Place hazard in a large block in the middle of the path
        # start=(0,0) -> ix=50, iy=50
        # dest=(10,10) -> ix=52, iy=55
        env_data['hazard_field'][50:56, 50:54] = 100.0 
        
        
        vessel_profile = {'base_speed_kts': 10.0, 'base_fuel_consumption_kg_h': 100.0}
        custom_cost_engine = RouteCostLayer(env_data, vessel_profile)
        custom_engine = FuelRiskEngine(custom_cost_engine)
        
        # Confirm different seeds produce different Pareto fronts containing multiple non-dominated solutions
        X1, F1 = custom_engine.get_nsga2_pareto_front(self.start, self.dest, seed=42)
        X2, F2 = custom_engine.get_nsga2_pareto_front(self.start, self.dest, seed=123)
        
        # In pymoo, if multiple non-dominated points exist, res.F is 2D.
        # If it's a single point, it's 1D. Let's make sure it's 2D and has >1 rows.
        self.assertTrue(F1.ndim == 2 and len(F1) > 1, f"Pareto front 1 should contain multiple non-dominated solutions, got {F1}")
        self.assertTrue(F2.ndim == 2 and len(F2) > 1, f"Pareto front 2 should contain multiple non-dominated solutions, got {F2}")
        
        # Verify diversity between seeds
        if len(F1) == len(F2):
            self.assertFalse(np.allclose(F1, F2), "Different seeds produced identical Pareto fronts!")

if __name__ == "__main__":
    unittest.main()
