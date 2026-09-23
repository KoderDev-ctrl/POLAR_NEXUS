import unittest
import numpy as np
from polar_nexus.cryox.spatial_fusion.regridder import SpatialRegridder
from polar_nexus.cryox.temporal_alignment.aligner import TemporalAligner

class TestAlignment(unittest.TestCase):
    
    def setUp(self):
        # Target grid: 10x10
        self.target_lats = np.linspace(-90, -60, 10)
        self.target_lons = np.linspace(-180, 180, 10)
        self.regridder = SpatialRegridder(self.target_lats, self.target_lons)
        
        # Source grid: 5x5
        self.source_lats = np.linspace(-90, -60, 5)
        self.source_lons = np.linspace(-180, 180, 5)

        self.aligner = TemporalAligner(window_size_days=3)

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        # Spatial Regridding (only bilinear since conservative is blocked)
        mock_wind = np.ones((5, 5)) * 10.0
        data = {"wind_u": mock_wind}
        
        regridded, metadata = self.regridder.regrid(self.source_lats, self.source_lons, data)
        self.assertEqual(regridded["wind_u"].shape, (10, 10))
        self.assertEqual(metadata["wind_u"]["method"], "bilinear")
        
        # Test conservative now falls back to bilinear and flags it in metadata (Item 1)
        cons_regridded, cons_metadata = self.regridder.regrid(self.source_lats, self.source_lons, {"sea_ice_concentration": np.ones((5, 5))})
        self.assertEqual(cons_metadata["sea_ice_concentration"]["method"], "bilinear_fallback")
        self.assertTrue("Approximation" in cons_metadata["sea_ice_concentration"]["accuracy_note"])
        
        # Temporal Alignment
        ts_data = {"sea_ice": np.random.rand(5, 10, 10)}
        timestamps = np.arange(5)
        aligned = self.aligner.align(ts_data, timestamps)
        # 5 days, window=3 -> 3 windows of shape (3, 10, 10)
        self.assertEqual(aligned["sea_ice"].shape, (3, 3, 10, 10))

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        # Temporal Aligner with different window
        aligner2 = TemporalAligner(window_size_days=5)
        ts_data = {"var": np.random.rand(10, 2, 2)}
        timestamps = np.arange(10)
        aligned = aligner2.align(ts_data, timestamps)
        # 10 days, window=5 -> 6 windows
        self.assertEqual(aligned["var"].shape, (6, 5, 2, 2))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Regridder: source data only partially overlaps target grid
        small_src_lats = np.linspace(-90, -80, 5)
        small_src_lons = np.linspace(-180, 0, 5)
        data = {"wind_v": np.ones((5, 5))}
        regridded, metadata = self.regridder.regrid(small_src_lats, small_src_lons, data)
        
        # Points outside the small source grid should be NaN
        # -60 lat is outside -90 to -80. Target index 9 (-60) should be all NaN
        self.assertTrue(np.isnan(regridded["wind_v"][-1, :]).all())

        # Temporal aligner boundary: exact length
        ts_data = {"var": np.ones((3, 2, 2))}
        aligned = self.aligner.align(ts_data, np.arange(3))
        self.assertEqual(aligned["var"].shape, (1, 3, 2, 2))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Unknown variable type for regridding
        data = {"unknown_variable": np.ones((5, 5))}
        with self.assertRaises(ValueError) as ctx:
            self.regridder.regrid(self.source_lats, self.source_lons, data)
        self.assertTrue("not defined" in str(ctx.exception))

        # Mismatched dimensions for regridding
        bad_data = {"wind_u": np.ones((4, 5))}
        with self.assertRaises(ValueError):
            self.regridder.regrid(self.source_lats, self.source_lons, bad_data)

    # TEST 5 - Edge case/failure condition
    def test_edge_case_failure(self):
        # Temporal aligner: not enough data
        ts_data = {"var": np.ones((2, 2, 2))}
        with self.assertRaises(ValueError) as ctx:
            self.aligner.align(ts_data, np.arange(2))
        self.assertTrue("Insufficient data" in str(ctx.exception))
        
        # Temporal aligner: mismatched timestamps vs data length
        ts_data = {"var": np.ones((5, 2, 2))}
        with self.assertRaises(ValueError) as ctx:
            # 6 timestamps but 5 data points
            self.aligner.align(ts_data, np.arange(6))
        self.assertTrue("does not match timestamps" in str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
