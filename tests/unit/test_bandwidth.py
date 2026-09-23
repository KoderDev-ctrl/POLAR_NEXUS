import unittest
import numpy as np
from polar_nexus.cryox.data_ingestion.bandwidth_manager import BandwidthManager

class TestBandwidthManager(unittest.TestCase):
    def setUp(self):
        self.env_data = {
            'ice_grid': np.ones((100, 100)),
            'risk_grid': np.ones((100, 100)),
            'depth_grid': np.ones((100, 100)),
            'iceberg_drift_vectors': np.ones((100, 100, 2)), # Non-essential
            'thickness_variance': np.ones((100, 100)) # Non-essential
        }

    # TEST 1 - Normal valid input (LOW mode)
    def test_normal_valid_input_low_mode(self):
        mgr = BandwidthManager(mode="LOW")
        processed = mgr.process_incoming_env_data(self.env_data)
        
        # Should drop non-essentials
        self.assertNotIn('iceberg_drift_vectors', processed)
        self.assertNotIn('thickness_variance', processed)
        
        # Should downsample (100 -> 20)
        self.assertEqual(processed['ice_grid'].shape, (20, 20))

    # TEST 2 - Different valid input (HIGH mode)
    def test_different_valid_input_high_mode(self):
        mgr = BandwidthManager(mode="HIGH")
        processed = mgr.process_incoming_env_data(self.env_data)
        
        # Should pass through completely untouched
        self.assertIn('iceberg_drift_vectors', processed)
        self.assertEqual(processed['ice_grid'].shape, (100, 100))

    # TEST 3 - Boundary condition (Small grid in LOW mode)
    def test_boundary_condition(self):
        mgr = BandwidthManager(mode="LOW")
        small_data = {'ice_grid': np.ones((4, 4))}
        processed = mgr.process_incoming_env_data(small_data)
        # Should downsample to 1x1
        self.assertEqual(processed['ice_grid'].shape, (1, 1))

    # TEST 4 - Adversarial input (Missing essential vars)
    def test_invalid_adversarial_input(self):
        mgr = BandwidthManager(mode="LOW")
        # Empty dict or missing essentials
        res1 = mgr.process_incoming_env_data({})
        res2 = mgr.process_incoming_env_data({'random_data': np.ones((10,10))})
        
        self.assertEqual(res1, {})
        self.assertEqual(res2, {}) # random_data dropped

    # TEST 5 - Edge case (Non-ndarray values in essential keys)
    def test_edge_case_failure(self):
        mgr = BandwidthManager(mode="LOW")
        data = {'ice_grid': "not_an_array", 'risk_grid': None}
        # Should pass through non-arrays gracefully without crashing
        processed = mgr.process_incoming_env_data(data)
        self.assertEqual(processed['ice_grid'], "not_an_array")
        self.assertIsNone(processed['risk_grid'])

if __name__ == "__main__":
    unittest.main()
