import unittest
from datetime import datetime, timedelta
from polar_nexus.cryox.data_ingestion.fetchers import (
    NSIDCFetcher,
    CopernicusMarineFetcher,
    ERA5Fetcher,
    IcebergDBFetcher,
    GEBCOFetcher,
    CryoXDataError
)

class TestDatasetFetchers(unittest.TestCase):

    def setUp(self):
        self.fetchers = [
            NSIDCFetcher(mode="LOCAL_FIXTURE"),
            CopernicusMarineFetcher(mode="LOCAL_FIXTURE"),
            ERA5Fetcher(mode="LOCAL_FIXTURE"),
            IcebergDBFetcher(mode="LOCAL_FIXTURE"),
            GEBCOFetcher(mode="LOCAL_FIXTURE")
        ]
        self.normal_time = (datetime(2024, 1, 1), datetime(2024, 1, 2))
        self.different_time = (datetime(2024, 2, 1), datetime(2024, 2, 2))
        self.normal_bbox = (-75.0, -180.0, -60.0, 180.0) # Southern hemisphere (Antarctica)
        
    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        for fetcher in self.fetchers:
            raw = fetcher.fetch(self.normal_time, self.normal_bbox)
            self.assertTrue(fetcher.validate_response(raw))
            self.assertEqual(raw.dataset_name, fetcher.dataset_name)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        different_bbox = (-80.0, -100.0, -70.0, -50.0)
        for fetcher in self.fetchers:
            raw = fetcher.fetch(self.different_time, different_bbox)
            self.assertTrue(fetcher.validate_response(raw))
            cached = fetcher.cache(raw)
            self.assertIn(fetcher.dataset_name, cached.file_path)

    # TEST 3 - Boundary condition & BBox coverage (Item 23)
    def test_boundary_condition_bboxes(self):
        # 1. Valid Southern Hemisphere bbox
        south_bbox = (-80.0, -100.0, -60.0, 100.0)
        
        # 2. Valid equator-crossing bbox
        equator_bbox = (-10.0, -50.0, 10.0, 50.0)
        
        # 3. Valid Northern Hemisphere bbox
        north_bbox = (60.0, -100.0, 80.0, 100.0)
        
        for fetcher in self.fetchers:
            raw_s = fetcher.fetch(self.normal_time, south_bbox)
            self.assertTrue(fetcher.validate_response(raw_s))
            
            raw_e = fetcher.fetch(self.normal_time, equator_bbox)
            self.assertTrue(fetcher.validate_response(raw_e))
            
            raw_n = fetcher.fetch(self.normal_time, north_bbox)
            self.assertTrue(fetcher.validate_response(raw_n))
            
        # 4. Invalid reversed latitude bounds (min > max)
        reversed_bbox = (-60.0, -100.0, -80.0, 100.0)
        
        # 5. Invalid out-of-range latitude values
        out_of_range_bbox = (-95.0, -100.0, -60.0, 100.0)
        
        for fetcher in self.fetchers:
            with self.assertRaises(ValueError) as ctx1:
                fetcher.fetch(self.normal_time, reversed_bbox)
            self.assertTrue("less than maximum" in str(ctx1.exception))
            
            with self.assertRaises(ValueError) as ctx2:
                fetcher.fetch(self.normal_time, out_of_range_bbox)
            self.assertTrue("between -90 and 90" in str(ctx2.exception))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Start time after end time
        invalid_time = (datetime(2024, 1, 2), datetime(2024, 1, 1))
        for fetcher in self.fetchers:
            with self.assertRaises(ValueError):
                fetcher.fetch(invalid_time, self.normal_bbox)

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Trigger simulated network failure
        real_fetcher = NSIDCFetcher(mode="REAL_DATA")
        with self.assertRaises(CryoXDataError):
            real_fetcher.fetch(self.normal_time, self.normal_bbox)

if __name__ == "__main__":
    unittest.main()
