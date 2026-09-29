import unittest
import numpy as np
import logging
from polar_nexus.risk.hazard_field.builder import HazardFieldBuilder

class TestHazardField(unittest.TestCase):

    def setUp(self):
        self.builder = HazardFieldBuilder()
        self.sic = np.array([[0.0, 50.0], [100.0, 20.0]])
        self.var = np.array([[0.0, 10.0], [20.0, 5.0]])
        self.bergs = np.array([[0.0, 0.0], [1.0, 2.0]])
        
        # Suppress logging during tests
        logging.getLogger("polar_nexus.risk.hazard_field.builder").setLevel(logging.CRITICAL)

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        wave = np.array([[1.0, 2.0], [3.0, 4.0]])
        current = np.array([[0.1, 0.5], [1.0, 1.5]])
        bathy = np.array([[100.0, 50.0], [15.0, -5.0]])
        
        hazard = self.builder.build_field(self.sic, self.var, self.bergs, wave, current, bathy)
        self.assertEqual(hazard.shape, (2, 2))
        self.assertTrue(np.all(hazard >= 0.0) and np.all(hazard <= 1.0))
        
        # Bottom right is land (bathy = -5.0), hazard must be 1.0
        self.assertAlmostEqual(hazard[1, 1], 1.0)

    # TEST 2 - Missing valid input (Different valid)
    def test_missing_valid_input(self):
        # Without iceberg density, wave, current, bathy (defaults to None, handled gracefully)
        hazard = self.builder.build_field(self.sic, self.var)
        self.assertEqual(hazard.shape, (2, 2))
        self.assertTrue(np.all(hazard >= 0.0) and np.all(hazard <= 1.0))
        self.assertAlmostEqual(hazard[0, 0], 0.0)

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # 3D temporal arrays with grid edge cases
        sic_3d = np.ones((5, 10, 10)) * 100.0
        var_3d = np.zeros((5, 10, 10))
        bathy_3d = np.ones((5, 10, 10)) * 15.0 # All shallow
        
        hazard = self.builder.build_field(sic_3d, var_3d, bathymetry=bathy_3d)
        self.assertEqual(hazard.shape, (5, 10, 10))
        self.assertTrue(np.all(hazard >= 0.5))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Mismatched shapes
        with self.assertRaises(ValueError) as ctx:
            self.builder.build_field(self.sic, np.zeros((3, 3)))
        self.assertTrue("Shape mismatch" in str(ctx.exception))
        
        with self.assertRaises(ValueError) as ctx:
            self.builder.build_field(self.sic, self.var, wave_height=np.zeros((2, 3)))
        self.assertTrue("Shape mismatch" in str(ctx.exception))

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Empty arrays (no data)
        with self.assertRaises(ValueError) as ctx:
            self.builder.build_field(np.zeros((0, 0)), np.zeros((0, 0)))
        self.assertTrue("Empty input" in str(ctx.exception))
        
        # All zero inputs should produce exact 0.0 hazard
        zero_grid = np.zeros((2,2))
        hazard = self.builder.build_field(zero_grid, zero_grid, zero_grid, zero_grid, zero_grid, np.ones((2,2))*100.0)
        self.assertTrue(np.all(hazard == 0.0))

if __name__ == "__main__":
    unittest.main()
