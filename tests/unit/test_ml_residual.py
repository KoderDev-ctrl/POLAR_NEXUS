import unittest
import numpy as np
from polar_nexus.cryox.models.ml_residual import IcebergResidualCorrectionModel

class TestMLResidual(unittest.TestCase):

    def setUp(self):
        self.model = IcebergResidualCorrectionModel()
        self.base_lats = np.array([[-70.0], [-70.1], [-70.2]])
        self.base_lons = np.array([[10.0], [10.1], [10.2]])
        self.env_data = {
            "wind_u": np.array([5.0]),
            "wind_v": np.array([-2.0])
        }

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        c_lats, c_lons = self.model.correct_drift(self.base_lats, self.base_lons, self.env_data)
        self.assertEqual(c_lats.shape, self.base_lats.shape)
        # Check that it actually corrected step 1, but not step 0
        self.assertAlmostEqual(c_lats[0, 0], self.base_lats[0, 0])
        self.assertNotAlmostEqual(c_lats[1, 0], self.base_lats[1, 0])

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        # Empty env data shouldn't crash, just zero correction
        c_lats, c_lons = self.model.correct_drift(self.base_lats, self.base_lons, {})
        self.assertTrue(np.array_equal(c_lats, self.base_lats))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Single step trajectory (only step 0)
        short_lats = np.array([[-70.0]])
        short_lons = np.array([[10.0]])
        c_lats, c_lons = self.model.correct_drift(short_lats, short_lons, self.env_data)
        self.assertTrue(np.array_equal(c_lats, short_lats))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Enforce no standalone execution
        with self.assertRaises(ValueError) as ctx:
            self.model.correct_drift(None, None, self.env_data)
        self.assertTrue("MUST be provided" in str(ctx.exception))
        
        # Mismatched shapes
        with self.assertRaises(ValueError):
            self.model.correct_drift(self.base_lats, self.base_lons[:2], self.env_data)

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Empty arrays
        with self.assertRaises(ValueError) as ctx:
            self.model.correct_drift(np.zeros((0, 2)), np.zeros((0, 2)), self.env_data)
        self.assertTrue("cannot be empty" in str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
