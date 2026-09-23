import unittest
from polar_nexus.api.vessels import validate_vessel_profile

class TestVesselProfileSchema(unittest.TestCase):
    def setUp(self):
        self.valid_profile = {
            "voyage_priority": "time_critical",
            "turning_radius": 15.0,
            "draft": 10.5,
            "depth_clearance": 2.0,
            "max_ice_concentration": 0.8,
            "max_acceptable_risk": 50.0
        }

    def test_normal_valid_input(self):
        self.assertTrue(validate_vessel_profile(self.valid_profile))

    def test_different_valid_input(self):
        diff_profile = self.valid_profile.copy()
        diff_profile["voyage_priority"] = "safety_priority"
        diff_profile["draft"] = 5.0
        self.assertTrue(validate_vessel_profile(diff_profile))

    def test_boundary_condition(self):
        boundary = self.valid_profile.copy()
        boundary["turning_radius"] = 0.0 # Valid
        boundary["max_ice_concentration"] = 1.0 # Valid max
        boundary["max_acceptable_risk"] = 0.0 # Valid min
        self.assertTrue(validate_vessel_profile(boundary))

    def test_invalid_adversarial_input(self):
        # Missing required field
        invalid1 = self.valid_profile.copy()
        del invalid1["draft"]
        with self.assertRaises(ValueError):
            validate_vessel_profile(invalid1)

        # Invalid type
        invalid2 = self.valid_profile.copy()
        invalid2["turning_radius"] = "large"
        with self.assertRaises(ValueError):
            validate_vessel_profile(invalid2)

        # Invalid priority enum
        invalid3 = self.valid_profile.copy()
        invalid3["voyage_priority"] = "random"
        with self.assertRaises(ValueError):
            validate_vessel_profile(invalid3)

    def test_edge_case_failure(self):
        # Negative physics constraints
        edge = self.valid_profile.copy()
        edge["draft"] = -1.0
        with self.assertRaises(ValueError):
            validate_vessel_profile(edge)
            
        edge2 = self.valid_profile.copy()
        edge2["max_ice_concentration"] = 1.5
        with self.assertRaises(ValueError):
            validate_vessel_profile(edge2)

if __name__ == "__main__":
    unittest.main()
