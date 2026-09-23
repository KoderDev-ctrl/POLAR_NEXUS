import unittest
from polar_nexus.recommendation.scorer import RecommendationScorer

class TestRecommendationScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = RecommendationScorer()
        self.routes = [
            {'id': 1, 'estimated_time': 10, 'estimated_fuel': 100, 'total_route_risk': 50},
            {'id': 2, 'estimated_time': 20, 'estimated_fuel': 50,  'total_route_risk': 10},
            {'id': 3, 'estimated_time': 5,  'estimated_fuel': 200, 'total_route_risk': 90}
        ]

    # TEST 1 - Normal valid input (Balanced default)
    def test_normal_valid_input(self):
        vessel = {'voyage_priority': 'balanced'}
        best = self.scorer.recommend_route(self.routes, vessel)
        # With balanced, extreme routes (like id 3) usually score worse than balanced routes like 1 or 2
        self.assertIsNotNone(best)
        self.assertIn('recommendation_score', best)

    # TEST 2 - Different valid input (Time Critical)
    def test_different_valid_input(self):
        vessel = {'voyage_priority': 'time_critical'}
        best = self.scorer.recommend_route(self.routes, vessel)
        # Route 3 is the fastest
        self.assertEqual(best['id'], 3)

    # TEST 3 - Boundary condition (Only one route)
    def test_boundary_condition(self):
        vessel = {'voyage_priority': 'safety_priority'}
        best = self.scorer.recommend_route([self.routes[1]], vessel)
        self.assertEqual(best['id'], 2)
        self.assertEqual(best['recommendation_score'], 0.0)

    # TEST 4 - Adversarial input (Empty list)
    def test_invalid_adversarial_input(self):
        best = self.scorer.recommend_route([], {})
        self.assertIsNone(best)

    # TEST 5 - Edge case / failure condition (All identical costs)
    def test_edge_case_failure(self):
        routes = [
            {'id': 1, 'estimated_time': 10, 'estimated_fuel': 10, 'total_route_risk': 10},
            {'id': 2, 'estimated_time': 10, 'estimated_fuel': 10, 'total_route_risk': 10}
        ]
        best = self.scorer.recommend_route(routes, {'voyage_priority': 'safety_priority'})
        # Normalization handles vmax==vmin by returning 0, so both score 0.0. Picks first.
        self.assertEqual(best['id'], 1)
        self.assertEqual(best['recommendation_score'], 0.0)

if __name__ == "__main__":
    unittest.main()
