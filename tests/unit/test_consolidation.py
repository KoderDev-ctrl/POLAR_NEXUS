import unittest
from polar_nexus.routex16.consolidation.filter import RouteConsolidator

class TestRouteConsolidator(unittest.TestCase):
    def setUp(self):
        self.consolidator = RouteConsolidator(duplicate_threshold_km=5.0)

    # TEST 1 - Normal valid input (Distinct optimal routes)
    def test_normal_valid_input(self):
        candidates = [
            {'waypoints': [(0,0), (1,1)], 'estimated_time': 10, 'estimated_fuel': 100, 'total_route_risk': 5},
            {'waypoints': [(0,0), (2,0)], 'estimated_time': 20, 'estimated_fuel': 50, 'total_route_risk': 10}
        ]
        # Both are non-dominated and geometrically distinct (distance approx 111km)
        final = self.consolidator.consolidate_routes(candidates)
        self.assertEqual(len(final), 2)

    # TEST 2 - Different valid input (Duplicate detection)
    def test_different_valid_input(self):
        candidates = [
            {'waypoints': [(0,0), (1,1)], 'estimated_time': 10, 'estimated_fuel': 100, 'total_route_risk': 5},
            {'waypoints': [(0,0), (1.0001, 1.0001)], 'estimated_time': 11, 'estimated_fuel': 101, 'total_route_risk': 6}
        ]
        # Second route is geometrically identical and dominated
        final = self.consolidator.consolidate_routes(candidates)
        self.assertEqual(len(final), 1)
        self.assertEqual(final[0]['estimated_time'], 10)

    # TEST 3 - Boundary condition (Pareto identical but physically distinct)
    def test_boundary_condition(self):
        candidates = [
            {'waypoints': [(0,0), (1,1)], 'estimated_time': 10, 'estimated_fuel': 100, 'total_route_risk': 5},
            {'waypoints': [(0,0), (2,0)], 'estimated_time': 10, 'estimated_fuel': 100, 'total_route_risk': 5}
        ]
        # Identical costs, distinct paths. Both should survive as alternatives.
        final = self.consolidator.consolidate_routes(candidates)
        self.assertEqual(len(final), 2)

    # TEST 4 - Adversarial input
    def test_invalid_adversarial_input(self):
        # Empty list, empty waypoints
        res1 = self.consolidator.consolidate_routes([])
        res2 = self.consolidator.consolidate_routes([{}, {'waypoints': []}])
        self.assertEqual(len(res1), 0)
        self.assertEqual(len(res2), 0) # Missing waypoints filtered out as invalid

    # TEST 5 - Edge case / failure condition (Missing costs default to 0)
    def test_edge_case_failure(self):
        candidates = [
            {'waypoints': [(0,0), (1,1)]}, # Costs default to 0
            {'waypoints': [(0,0), (5,5)], 'estimated_time': 100} # One cost is high
        ]
        final = self.consolidator.consolidate_routes(candidates)
        # 1st dominates 2nd. 2nd is physically distant. But 2nd gets pushed to lower Pareto front.
        # It still survives because it's not a duplicate.
        self.assertEqual(len(final), 2)

if __name__ == "__main__":
    unittest.main()
