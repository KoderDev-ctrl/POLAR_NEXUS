import unittest
import numpy as np
from polar_nexus.cryox.models.hazard_field import HazardFieldBuilder

class TestHazardField(unittest.TestCase):

    def setUp(self):
        self.builder = HazardFieldBuilder()
        self.sic = np.array([[0.0, 50.0], [100.0, 20.0]])
        self.var = np.array([[0.0, 10.0], [20.0, 5.0]])
        self.bergs = np.array([[0.0, 0.0], [1.0, 2.0]])

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        hazard = self.builder.build_field(self.sic, self.var, self.bergs)
        self.assertEqual(hazard.shape, (2, 2))
        self.assertTrue(np.all(hazard >= 0.0) and np.all(hazard <= 1.0))
        # Top left should be 0 (no ice, no var, no bergs)
        self.assertAlmostEqual(hazard[0, 0], 0.0)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        # Without iceberg density (defaults to 0)
        hazard = self.builder.build_field(self.sic, self.var)
        self.assertEqual(hazard.shape, (2, 2))
        self.assertTrue(np.all(hazard >= 0.0) and np.all(hazard <= 1.0))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # 3D temporal arrays
        sic_3d = np.ones((5, 10, 10)) * 100.0
        var_3d = np.zeros((5, 10, 10))
        hazard = self.builder.build_field(sic_3d, var_3d)
        self.assertEqual(hazard.shape, (5, 10, 10))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Shape mismatch sic/var
        with self.assertRaises(ValueError) as ctx:
            self.builder.build_field(self.sic, np.zeros((3, 3)))
        self.assertTrue("same shape" in str(ctx.exception))
        
        # Shape mismatch bergs
        with self.assertRaises(ValueError):
            self.builder.build_field(self.sic, self.var, np.zeros((2, 3)))

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Empty arrays
        with self.assertRaises(ValueError) as ctx:
            self.builder.build_field(np.zeros((0, 0)), np.zeros((0, 0)))
        self.assertTrue("Empty input" in str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
