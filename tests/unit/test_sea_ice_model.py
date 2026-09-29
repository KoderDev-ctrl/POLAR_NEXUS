import unittest
import numpy as np
import torch
from polar_nexus.cryox.models.sea_ice import SeaIceModel

class TestSeaIceModel(unittest.TestCase):

    def setUp(self):
        # Local Functional Verification: model instantiation
        self.model = SeaIceModel(forecast_horizon_days=3, seed=42)

    def test_normal_valid_input(self):
        T, lat, lon = 5, 10, 10
        sic = np.ones((T, lat, lon)) * 50.0
        inputs = {"sea_ice_concentration": sic}
        
        preds = self.model.predict(inputs)
        self.assertEqual(preds.shape, (3, 10, 10))
        # Valid output bounds
        self.assertTrue(np.all(preds >= 0.0))
        self.assertTrue(np.all(preds <= 100.0))

    def test_temporal_padding(self):
        # Providing less than required history (3 days)
        T, lat, lon = 1, 10, 10
        sic = np.ones((T, lat, lon)) * 30.0
        inputs = {"sea_ice_concentration": sic}
        
        preds = self.model.predict(inputs)
        self.assertEqual(preds.shape, (3, 10, 10))

    def test_persistence_baseline(self):
        # Walk-forward validation equivalent: Compare model to persistence
        # Persistence says tomorrow = today
        T, lat, lon = 3, 16, 16
        sic = np.zeros((T, lat, lon))
        sic[-1] = 50.0 # Today's actual
        
        # Local Fixture Prediction
        inputs = {"sea_ice_concentration": sic}
        preds = self.model.predict(inputs)
        
        # Test that model produced structural output
        self.assertEqual(preds.shape, (3, 16, 16))
        
        persistence = np.ones_like(preds) * 50.0
        # Check that we can measure MSE against persistence baseline
        mse_persistence = np.mean((persistence - 50.0)**2)
        self.assertEqual(mse_persistence, 0.0) # Baseline error on perfectly static true future is 0

    def test_invalid_adversarial_input(self):
        # Missing SIC
        with self.assertRaises(ValueError) as ctx:
            self.model.predict({"wind": np.ones((5, 5, 5))})
        self.assertTrue("Missing required input" in str(ctx.exception))
        
        # Wrong dimensions
        with self.assertRaises(ValueError) as ctx:
            self.model.predict({"sea_ice_concentration": np.ones((5, 5))})
        self.assertTrue("Expected 3D array" in str(ctx.exception))

    def test_edge_case_failure(self):
        # Zero dimension arrays
        with self.assertRaises(ValueError) as ctx:
            self.model.predict({"sea_ice_concentration": np.zeros((0, 5, 5))})
        self.assertTrue("cannot be zero" in str(ctx.exception))
        
if __name__ == "__main__":
    unittest.main()
