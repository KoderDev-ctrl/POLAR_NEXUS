from typing import List, Tuple, Dict, Any
import numpy as np

class HardFeasibilityGate:
    """
    Validates candidate routes against hard constraints.
    Candidates failing any constraint are discarded.
    """
    def __init__(self):
        pass

    def filter_feasible_routes(self, candidates: List[Dict[str, Any]], vessel_profile: Dict[str, Any], env_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filters a list of candidates, returning only those that pass all hard constraints.
        """
        feasible = []
        for candidate in candidates:
            if self._is_feasible(candidate, vessel_profile, env_data):
                feasible.append(candidate)
        return feasible

    def _is_feasible(self, candidate: Dict[str, Any], vessel_profile: Dict[str, Any], env_data: Dict[str, Any]) -> bool:
        """
        Checks a single candidate against all hard constraints.
        Returns True if feasible, False if infeasible.
        """
        path = candidate.get('waypoints', [])
        if not path:
            return False

        # 1. Geographic restrictions & Minimum depth (mocked via env_data grid)
        # 2. Maximum acceptable ice concentration & thickness
        # 3. Maximum risk threshold
        max_ice_conc = vessel_profile.get('max_ice_concentration', 1.0)
        max_risk = vessel_profile.get('max_acceptable_risk', 100.0)
        min_depth = vessel_profile.get('draft', 0.0) + vessel_profile.get('depth_clearance', 2.0)

        grid_shape = env_data.get('ice_grid', np.zeros((10,10))).shape
        ice_grid = env_data.get('ice_grid', np.zeros(grid_shape))
        risk_grid = env_data.get('risk_grid', np.zeros(grid_shape))
        depth_grid = env_data.get('depth_grid', np.full(grid_shape, 100.0))

        for pt in path:
            x, y = int(pt[0]), int(pt[1])
            if 0 <= x < grid_shape[0] and 0 <= y < grid_shape[1]:
                # Depth check
                if depth_grid[x, y] < min_depth:
                    return False
                # Ice concentration check
                if ice_grid[x, y] > max_ice_conc:
                    return False
                # Hazard/Risk check
                if risk_grid[x, y] > max_risk:
                    return False

        # 4. Turning radius / maneuverability
        turning_radius = vessel_profile.get('turning_radius', 0.0)
        if turning_radius > 0.0 and len(path) >= 3:
            for i in range(len(path) - 2):
                p1 = np.array(path[i])
                p2 = np.array(path[i+1])
                p3 = np.array(path[i+2])
                v1 = p2 - p1
                v2 = p3 - p2
                n1 = np.linalg.norm(v1)
                n2 = np.linalg.norm(v2)
                if n1 > 0 and n2 > 0:
                    # Calculate angle
                    cos_theta = np.dot(v1, v2) / (n1 * n2)
                    cos_theta = np.clip(cos_theta, -1.0, 1.0)
                    angle = np.arccos(cos_theta)
                    # Simple heuristic: sharp turns (e.g. > 90 deg or 1.57 rad) violate large turning radii
                    if turning_radius > 10.0 and angle > 1.57:
                        return False

        return True
