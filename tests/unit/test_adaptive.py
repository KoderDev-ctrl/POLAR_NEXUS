import unittest
import numpy as np
from polar_nexus.adaptive.loop import AdaptiveNavigationLoop
from polar_nexus.feasibility.gate import HardFeasibilityGate

# Mock Engine
class MockEngine:
    def generate_candidates(self, start, dest, grid):
        return [
            [start, (1,1), dest],
            [start, (2,2), dest]
        ]

class TestAdaptiveNavigation(unittest.TestCase):
    def setUp(self):
        self.gate = HardFeasibilityGate()
        self.engines = {'TIME': MockEngine(), 'FUEL': MockEngine()}
        self.loop = AdaptiveNavigationLoop(self.engines, self.gate)
        
        self.vessel = {'draft': 10.0, 'depth_clearance': 2.0, 'max_ice_concentration': 1.0, 'max_acceptable_risk': 100.0}
        self.env = {
            'ice_grid': np.zeros((10,10)),
            'risk_grid': np.zeros((10,10)),
            'depth_grid': np.full((10,10), 50.0)
        }
        self.initial_route = {'waypoints': [(0,0), (0,1), (0,2)]}

    # TEST 1 - Normal valid input (Risk trigger, Reroute)
    def test_normal_valid_input_reroute(self):
        self.loop.lock_category('TIME', self.initial_route, self.vessel)
        result = self.loop.trigger_update((0,0), self.env, risk_delta=15.0, risk_threshold=10.0)
        self.assertEqual(result['status'], 'REROUTE')
        self.assertIsNotNone(result['route'])

    # TEST 2 - Different valid input (No trigger, Continue)
    def test_different_valid_input_continue(self):
        self.loop.lock_category('FUEL', self.initial_route, self.vessel)
        result = self.loop.trigger_update((0,0), self.env, risk_delta=5.0, risk_threshold=10.0)
        self.assertEqual(result['status'], 'CONTINUE')
        self.assertEqual(result['route'], self.initial_route)

    # TEST 3 - Boundary condition (Exactly on threshold)
    def test_boundary_condition(self):
        self.loop.lock_category('TIME', self.initial_route, self.vessel)
        # Assuming >= threshold triggers it, but logic is `< threshold` -> continue
        result = self.loop.trigger_update((0,0), self.env, risk_delta=10.0, risk_threshold=10.0)
        self.assertEqual(result['status'], 'REROUTE')

    # TEST 4 - Adversarial input (No category locked)
    def test_invalid_adversarial_input(self):
        result = self.loop.trigger_update((0,0), self.env, risk_delta=15.0)
        self.assertEqual(result['status'], 'ERROR')
        
        with self.assertRaises(ValueError):
            self.loop.lock_category('INVALID_ENGINE', self.initial_route, self.vessel)

    # TEST 5 - Edge case / Failure (No feasible route on replan)
    def test_edge_case_failure_zero_routes(self):
        self.loop.lock_category('TIME', self.initial_route, self.vessel)
        # Block the grid
        self.env['depth_grid'] = np.zeros((10,10)) # Extremely shallow, violates draft
        result = self.loop.trigger_update((0,0), self.env, risk_delta=20.0)
        self.assertEqual(result['status'], 'NO_FEASIBLE_ROUTE')
        self.assertIsNone(result['route'])

if __name__ == "__main__":
    unittest.main()
