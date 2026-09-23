import unittest
from datetime import datetime, timedelta, timezone
from polar_nexus.api.vessels import VesselsAPI, validate_position_update, StaleTimestampError, InvalidCoordinateError
from polar_nexus.data.position_feed import SimulatedPositionFeed, PositionUpdate

class TestShipPositionIngestion(unittest.TestCase):
    
    def setUp(self):
        self.api = VesselsAPI()
        self.now = datetime.now(timezone.utc)
        self.valid_payload = {
            "lat": -75.0,
            "lon": 45.0,
            "timestamp": self.now.isoformat()
        }
        
        self.sim_feed = SimulatedPositionFeed([
            PositionUpdate("vessel1", -70.0, 10.0, self.now),
            PositionUpdate("vessel1", -71.0, 11.0, self.now + timedelta(hours=1))
        ])

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        # API test
        res = self.api.post_vessel_position("vessel1", self.valid_payload)
        self.assertTrue(res["stored"])
        
        # Sim feed test
        update = self.sim_feed.fetch_latest("vessel1")
        self.assertEqual(update.lat, -70.0)
        self.assertEqual(update.source, "simulated")

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        diff_payload = {
            "lat": 0.0, # Equator
            "lon": -180.0, # Dateline
            "timestamp": (self.now - timedelta(hours=5)).isoformat()
        }
        res = self.api.post_vessel_position("vessel2", diff_payload)
        self.assertTrue(res["stored"])
        
        # Sim feed advance
        _ = self.sim_feed.fetch_latest("vessel1")
        update2 = self.sim_feed.fetch_latest("vessel1")
        self.assertEqual(update2.lat, -71.0)

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        boundary_payload = {
            "lat": -90.0, # Exact South Pole
            "lon": 180.0, 
            "timestamp": (self.now - timedelta(hours=23, minutes=59)).isoformat() # Barely not stale
        }
        res = self.api.post_vessel_position("vessel3", boundary_payload)
        self.assertTrue(res["stored"])
        
        # Sim feed boundary: fetch beyond route length just returns the last point
        _ = self.sim_feed.fetch_latest("vessel1")
        _ = self.sim_feed.fetch_latest("vessel1")
        update3 = self.sim_feed.fetch_latest("vessel1")
        self.assertEqual(update3.lat, -71.0)

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Missing fields
        with self.assertRaises(ValueError):
            self.api.post_vessel_position("vessel4", {"lat": -70.0})
            
        # Invalid coordinates
        bad_coord_payload = {"lat": "south", "lon": 45.0, "timestamp": self.now.isoformat()}
        with self.assertRaises(InvalidCoordinateError):
            self.api.post_vessel_position("vessel4", bad_coord_payload)
            
        out_of_bounds = {"lat": -91.0, "lon": 45.0, "timestamp": self.now.isoformat()}
        with self.assertRaises(InvalidCoordinateError):
            self.api.post_vessel_position("vessel4", out_of_bounds)
            
    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Stale timestamp > 24 hours
        stale_payload = {
            "lat": -75.0,
            "lon": 45.0,
            "timestamp": (self.now - timedelta(hours=25)).isoformat()
        }
        with self.assertRaises(StaleTimestampError):
            self.api.post_vessel_position("vessel5", stale_payload)
            
        # Future timestamp
        future_payload = {
            "lat": -75.0,
            "lon": 45.0,
            "timestamp": (self.now + timedelta(hours=1)).isoformat()
        }
        with self.assertRaises(ValueError):
            self.api.post_vessel_position("vessel5", future_payload)
            
        # Sim feed empty failure
        empty_feed = SimulatedPositionFeed([])
        with self.assertRaises(ValueError):
            empty_feed.fetch_latest("vessel_empty")

if __name__ == "__main__":
    unittest.main()
