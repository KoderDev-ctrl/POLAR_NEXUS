import unittest
import numpy as np
from polar_nexus.routex16.engines.time_engine import TimeEngine
from polar_nexus.physics.cost_functions import PhysicsCostEngine

class TestTimeEngine(unittest.TestCase):

    def setUp(self):
        self.cost_engine = PhysicsCostEngine(10.0, 100.0)
        self.engine = TimeEngine(self.cost_engine)
        self.start = (0.0, 0.0)
        self.dest = (10.0, 10.0)
        self.grid = np.zeros((20, 20))

    # TEST 1 - Normal valid input & Algorithm Diversity Check (Master Prompt §5)
    def test_normal_valid_input_and_diversity(self):
        candidates = self.engine.generate_candidates(self.start, self.dest, self.grid)
        self.assertEqual(len(candidates), 4)
        
        # Ensure all 4 algorithms produce measurably different candidate outputs
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                # Paths should not be exactly identical
                self.assertNotEqual(candidates[i], candidates[j], 
                                    f"Algorithms {i} and {j} produced identical paths! Architecture violation.")
        
        # Verify starts and ends
        for path in candidates:
            self.assertEqual(path[0], self.start)
            self.assertEqual(path[-1], self.dest)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        start2 = (5.0, 5.0)
        dest2 = (15.0, 5.0)
        candidates = self.engine.generate_candidates(start2, dest2, self.grid)
        self.assertEqual(len(candidates), 4)
        self.assertEqual(candidates[0][0], start2)
        self.assertEqual(candidates[0][-1], dest2)

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Start equals destination (zero distance)
        candidates = self.engine.generate_candidates(self.start, self.start, self.grid)
        # Each algorithm should handle 0-distance gracefully 
        for path in candidates:
            self.assertEqual(path[-1], self.start)

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Extremely large coordinates (should still compute the geometric stubs)
        candidates = self.engine.generate_candidates((-9999.0, -9999.0), (9999.0, 9999.0), self.grid)
        self.assertEqual(len(candidates), 4)

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Negative grid inputs should not crash the spatial stubs
        candidates = self.engine.generate_candidates((-5.0, -5.0), (-1.0, -1.0), self.grid)
        self.assertEqual(len(candidates), 4)

if __name__ == "__main__":
    unittest.main()
