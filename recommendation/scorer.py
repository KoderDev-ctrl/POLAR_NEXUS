from typing import List, Dict, Any, Optional

class RecommendationScorer:
    """
    Computes a weighted score for each feasible route and recommends the best one.
    Score = w_time * normalized_time + w_fuel * normalized_fuel + w_risk * normalized_risk
    """
    def __init__(self):
        # Default priority weights if none specified
        self.default_weights = {'w_time': 0.33, 'w_fuel': 0.33, 'w_risk': 0.34}

    def _get_weights(self, priority: str) -> Dict[str, float]:
        priority = priority.lower().strip()
        if priority == "time_critical":
            return {'w_time': 0.7, 'w_fuel': 0.1, 'w_risk': 0.2}
        elif priority == "safety_priority":
            return {'w_time': 0.2, 'w_fuel': 0.1, 'w_risk': 0.7}
        elif priority == "fuel_economy":
            return {'w_time': 0.1, 'w_fuel': 0.7, 'w_risk': 0.2}
        else:
            return self.default_weights

    def recommend_route(self, feasible_routes: List[Dict[str, Any]], vessel_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Recommends a single route from a list of feasible routes based on user priorities.
        Returns None if no feasible routes exist.
        """
        if not feasible_routes:
            return None

        if len(feasible_routes) == 1:
            feasible_routes[0]['recommendation_score'] = 0.0
            return feasible_routes[0]

        priority = vessel_profile.get('voyage_priority', 'balanced')
        weights = self._get_weights(priority)

        # Extract costs
        times = [r.get('estimated_time', 0.0) for r in feasible_routes]
        fuels = [r.get('estimated_fuel', 0.0) for r in feasible_routes]
        risks = [r.get('total_route_risk', 0.0) for r in feasible_routes]

        # Min and Max for normalization
        min_time, max_time = min(times), max(times)
        min_fuel, max_fuel = min(fuels), max(fuels)
        min_risk, max_risk = min(risks), max(risks)

        def normalize(val, vmin, vmax):
            if vmax == vmin:
                return 0.0
            return (val - vmin) / (vmax - vmin)

        best_score = float('inf')
        best_route = None

        for route in feasible_routes:
            nt = normalize(route.get('estimated_time', 0.0), min_time, max_time)
            nf = normalize(route.get('estimated_fuel', 0.0), min_fuel, max_fuel)
            nr = normalize(route.get('total_route_risk', 0.0), min_risk, max_risk)

            # Lower score is better
            score = (weights['w_time'] * nt) + (weights['w_fuel'] * nf) + (weights['w_risk'] * nr)
            route['recommendation_score'] = score

            if score < best_score:
                best_score = score
                best_route = route

        return best_route
