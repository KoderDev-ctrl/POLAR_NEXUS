import unittest
import numpy as np
from polar_nexus.cryox.models.sea_ice import SeaIceModel

class TestSeaIceModel(unittest.TestCase):

    def setUp(self):
        self.model = SeaIceModel(forecast_horizon_days=3)

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        T, lat, lon = 5, 10, 10
        sic = np.ones((T, lat, lon)) * 50.0
        inputs = {"sea_ice_concentration": sic}
        
        preds = self.model.predict(inputs)
        self.assertEqual(preds.shape, (3, 10, 10))
        # Should be clipped properly, roughly around 50
        self.assertTrue(np.all(preds >= 0.0))
        self.assertTrue(np.all(preds <= 100.0))

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        model2 = SeaIceModel(forecast_horizon_days=1)
        sic = np.random.rand(2, 5, 5) * 100.0
        inputs = {"sea_ice_concentration": sic}
        
        preds = model2.predict(inputs)
        self.assertEqual(preds.shape, (1, 5, 5))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # 0% and 100% boundary check (clipping)
        sic = np.zeros((1, 5, 5))
        sic[0, 0, 0] = 100.0
        inputs = {"sea_ice_concentration": sic}
        preds = self.model.predict(inputs)
        self.assertTrue(np.all(preds >= 0.0))
        self.assertTrue(np.all(preds <= 100.0))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Missing SIC
        with self.assertRaises(ValueError) as ctx:
            self.model.predict({"wind": np.ones((5, 5, 5))})
        self.assertTrue("Missing required input" in str(ctx.exception))
        
        # Wrong dimensions
        with self.assertRaises(ValueError) as ctx:
            self.model.predict({"sea_ice_concentration": np.ones((5, 5))})
        self.assertTrue("Expected 3D array" in str(ctx.exception))

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Zero dimension arrays
        with self.assertRaises(ValueError) as ctx:
            self.model.predict({"sea_ice_concentration": np.zeros((0, 5, 5))})
        self.assertTrue("cannot be zero" in str(ctx.exception))
        
        # All NaNs
        sic = np.full((2, 2, 2), np.nan)
        preds = self.model.predict({"sea_ice_concentration": sic})
        # Output should be NaN
        self.assertTrue(np.isnan(preds).all())

if __name__ == "__main__":
    unittest.main()
