import unittest
import numpy as np
from polar_nexus.cryox.models.iceberg_physics import IcebergPhysicsModel

class TestIcebergPhysics(unittest.TestCase):

    def setUp(self):
        self.model = IcebergPhysicsModel(time_step_hours=1.0)
        self.env_data = {
            "wind_u": np.array([10.0, -10.0]),
            "wind_v": np.array([0.0, 5.0]),
            "currents_u": np.array([0.5, -0.5]),
            "currents_v": np.array([0.0, 0.2])
        }
        self.lats = np.array([-70.0, -65.0])
        self.lons = np.array([0.0, 180.0])

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        lats, lons = self.model.predict_drift(self.lats, self.lons, self.env_data, steps=5)
        self.assertEqual(lats.shape, (6, 2))
        self.assertEqual(lons.shape, (6, 2))
        # First iceberg (index 0) has pos u_w and u_a, so longitude should increase
        self.assertTrue(lons[-1, 0] > 0.0)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        env2 = {k: v * 2 for k, v in self.env_data.items()}
        lats, lons = self.model.predict_drift(self.lats, self.lons, env2, steps=2)
        self.assertEqual(lats.shape, (3, 2))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Dateline crossing boundary
        lats_bound = np.array([-70.0])
        lons_bound = np.array([179.9])
        env_bound = {
            "wind_u": np.array([50.0]), # Strong eastward wind
            "wind_v": np.array([0.0]),
            "currents_u": np.array([2.0]), # Strong eastward current
            "currents_v": np.array([0.0])
        }
        lats, lons = self.model.predict_drift(lats_bound, lons_bound, env_bound, steps=10)
        # Should wrap around to negative longitude
        self.assertTrue(np.any(lons < 0))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Mismatched lengths
        with self.assertRaises(ValueError) as ctx:
            self.model.predict_drift(np.array([-70.0]), np.array([0.0, 1.0]), self.env_data, 5)
        self.assertTrue("same length" in str(ctx.exception))
        
        # Missing env variables
        bad_env = {"wind_u": np.array([10.0])}
        with self.assertRaises(ValueError) as ctx:
            self.model.predict_drift(np.array([-70.0]), np.array([0.0]), bad_env, 5)
        self.assertTrue("Missing required" in str(ctx.exception))

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Zero steps
        lats, lons = self.model.predict_drift(self.lats, self.lons, self.env_data, steps=0)
        self.assertEqual(lats.shape, (1, 2))
        self.assertTrue(np.array_equal(lats[0], self.lats))

if __name__ == "__main__":
    unittest.main()
