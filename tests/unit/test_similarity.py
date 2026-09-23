import unittest
from polar_nexus.routex16.consolidation.similarity import discrete_frechet_distance, haversine_distance

class TestSimilarityMetric(unittest.TestCase):

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        # Two identical routes should have 0 distance
        route_a = [(-70.0, 10.0), (-71.0, 11.0), (-72.0, 12.0)]
        route_b = [(-70.0, 10.0), (-71.0, 11.0), (-72.0, 12.0)]
        dist = discrete_frechet_distance(route_a, route_b)
        self.assertAlmostEqual(dist, 0.0)

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        # Two parallel routes separated by 1 degree longitude at equator (~111km)
        route_a = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
        route_b = [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0)]
        dist = discrete_frechet_distance(route_a, route_b)
        # Distance should be approx 111km
        self.assertTrue(110 < dist < 112)

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Routes of different lengths
        route_a = [(0.0, 0.0)]
        route_b = [(0.0, 0.0), (0.0, 1.0)]
        dist = discrete_frechet_distance(route_a, route_b)
        # Distance should be the distance between (0,0) and (0,1)
        expected = haversine_distance((0.0, 0.0), (0.0, 1.0))
        self.assertAlmostEqual(dist, expected)

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Extremely long coordinate out of physical bounds (just testing math resilience)
        route_a = [(0.0, 0.0)]
        route_b = [(0.0, 720.0)] # Modulo math in haversine might do weird things, but Python math handles it
        # Actually haversine uses radians, so sin/cos will periodic wrap
        dist = discrete_frechet_distance(route_a, route_b)
        self.assertAlmostEqual(dist, 0.0) # 720 deg == 0 deg
        
    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Empty route raises ValueError
        with self.assertRaises(ValueError):
            discrete_frechet_distance([], [(0.0, 0.0)])
            
        with self.assertRaises(ValueError):
            discrete_frechet_distance([(0.0, 0.0)], [])

if __name__ == "__main__":
    unittest.main()
