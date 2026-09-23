import unittest
import numpy as np
from polar_nexus.cryox.preprocessing.pipeline import PreprocessingPipeline

class TestPreprocessingPipeline(unittest.TestCase):
    
    def setUp(self):
        # Default missing_gap_threshold = 3, z_threshold = 3.0
        self.pipeline = PreprocessingPipeline(z_threshold=3.0, missing_gap_threshold=3)
        self.limits = {"sea_ice_concentration": (0.0, 100.0)}

    # TEST 1: Normal valid input (with short missing gap)
    def test_normal_valid_input(self):
        data = {
            "sea_ice_concentration": np.array([10.0, 20.0, np.nan, np.nan, 50.0])
        }
        res = self.pipeline.process(data, self.limits)
        processed = res["sea_ice_concentration"]
        # The NaNs should be interpolated
        self.assertFalse(np.isnan(processed).any())
        self.assertAlmostEqual(processed[2], 30.0)
        self.assertAlmostEqual(processed[3], 40.0)

    # TEST 2: Different valid input (no missing values, no outliers)
    def test_different_valid_input(self):
        data = {
            "sea_ice_concentration": np.array([50.0, 50.0, 50.0, 50.0])
        }
        res = self.pipeline.process(data, self.limits)
        processed = res["sea_ice_concentration"]
        self.assertTrue(np.all(processed == 50.0))

    # TEST 3: Boundary condition (long gap, exactly at threshold and above)
    def test_boundary_condition(self):
        data = {
            # Gap of 3 (should interpolate)
            "var_short": np.array([0.0, np.nan, np.nan, np.nan, 40.0]),
            # Gap of 4 (should NOT interpolate)
            "var_long": np.array([0.0, np.nan, np.nan, np.nan, np.nan, 50.0])
        }
        res = self.pipeline.process(data, {})
        
        self.assertFalse(np.isnan(res["var_short"]).any(), "Gap of 3 should be interpolated")
        self.assertTrue(np.isnan(res["var_long"][1:5]).all(), "Gap of 4 should remain NaN")

    # TEST 4: Invalid/adversarial input (out of physical bounds)
    def test_invalid_adversarial_input(self):
        data = {
            # 110 and -10 are out of bounds (0-100) and at the edges
            "sea_ice_concentration": np.array([110.0, 50.0, 50.0, -10.0])
        }
        res = self.pipeline.process(data, self.limits)
        processed = res["sea_ice_concentration"]
        # They become NaN, then because they are edge gaps, they are NOT extrapolated
        self.assertTrue(np.isnan(processed[0]))
        self.assertTrue(np.isnan(processed[3]))

    # TEST 5: Edge case / failure condition (all NaNs or single element, extreme outliers)
    def test_edge_case_failure(self):
        data = {
            "all_nans": np.array([np.nan, np.nan, np.nan]),
            # Array needs to be large enough for a single outlier to reach z-score > 3.0 (N > 10)
            "outlier_test": np.array([10.0]*12 + [1000.0] + [10.0]*12)
        }
        res = self.pipeline.process(data, {})
        self.assertTrue(np.isnan(res["all_nans"]).all())
        
        # 1000 is an outlier and should be replaced. Since gap=1, it gets interpolated back to 10.0
        self.assertAlmostEqual(res["outlier_test"][12], 10.0)

    # NEW TEST: multi-dimensional interpolation (dimension conflation bug fix)
    def test_multidimensional_interpolation_axis(self):
        # 3x4 array: time (axis 0) = 3, space = 4
        # Column 0: gap in time
        # Row 1: gap in space (but we interpolate along time axis 0!)
        arr = np.array([
            [10.0, 50.0, 20.0, 30.0],
            [np.nan, np.nan, np.nan, np.nan],
            [30.0, 50.0, 40.0, 70.0]
        ])
        data = {"multi_dim": arr}
        res = self.pipeline.process(data, {})
        processed = res["multi_dim"]
        
        # We expect interpolation ALONG axis 0 (time).
        # arr[:, 0] was [10.0, nan, 30.0] -> should become [10.0, 20.0, 30.0]
        self.assertAlmostEqual(processed[1, 0], 20.0)
        # arr[:, 1] was [50.0, nan, 50.0] -> should become [50.0, 50.0, 50.0]
        self.assertAlmostEqual(processed[1, 1], 50.0)
        
        # Crucially, check it did NOT flatten and interpolate across space!
        # If it flattened: [..., 30.0, nan, nan, nan, nan, 30.0, ...]
        # The values would be completely conflated.
        self.assertEqual(processed.shape, (3, 4))

if __name__ == "__main__":
    unittest.main()
