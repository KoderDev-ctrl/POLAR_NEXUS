from typing import List, Tuple, Dict, Any
import numpy as np
from polar_nexus.routex16.cost_layer import CandidateRoute
from polar_nexus.iceberg.core import cpa_tcpa, Hazard
from polar_nexus.routing.grid import GridSpec

class HardFeasibilityGate:
    """
    Validates candidate routes against hard constraints.
    Candidates failing any constraint are marked INFEASIBLE and violations are recorded.
    """
    def __init__(self, hazard: Hazard, grid: GridSpec):
        self.hazard = hazard
        self.grid = grid

    def filter_feasible_routes(self, candidates: List[CandidateRoute], vessel_profile: Dict[str, Any], env_data: Dict[str, Any]) -> List[CandidateRoute]:
        for candidate in candidates:
            self._evaluate_feasibility(candidate, vessel_profile, env_data)
        
        return [c for c in candidates if c.feasibility_status == "FEASIBLE"]

    def _evaluate_feasibility(self, candidate: CandidateRoute, vessel_profile: Dict[str, Any], env_data: Dict[str, Any]):
        violations = []
        path = candidate.geometry
        if not path:
            candidate.feasibility_status = "INFEASIBLE"
            return

        max_ice_conc = vessel_profile.get('max_ice_concentration', 1.0)
        max_risk = vessel_profile.get('max_acceptable_risk', 100.0)
        min_depth = vessel_profile.get('draft', 0.0) + vessel_profile.get('depth_clearance', 2.0)

        grid_shape = self.grid.shape
        ice_grid = env_data.get('ice_conc')
        risk_grid = env_data.get('hazard_field')
        depth_grid = env_data.get('depth_grid', np.full(grid_shape, 100.0))

        # We assume path is [(lat, lon, hours), ...] based on L7 requirements
        route_xyh = []
        for pt in path:
            lat, lon = pt[0], pt[1]
            h = pt[2] if len(pt) > 2 else 0.0
            
            x, y = self.grid.latlon_to_xy(lat, lon)
            route_xyh.append([x, y, h])
            
            row, col = self.grid.xy_to_index(x, y)
            
            if not self.grid.in_bounds(row, col):
                violations.append({"candidate_id": candidate.route_id, "constraint_name": "grid_boundary", "constraint_value": f"({row},{col})", "limit": f"{grid_shape}", "status": "INFEASIBLE"})
                continue
                
            if depth_grid[row, col] < min_depth:
                violations.append({"candidate_id": candidate.route_id, "constraint_name": "draft", "constraint_value": float(depth_grid[row, col]), "limit": float(min_depth), "status": "INFEASIBLE"})
            
            if ice_grid is not None and ice_grid[row, col] > max_ice_conc:
                violations.append({"candidate_id": candidate.route_id, "constraint_name": "ice_concentration", "constraint_value": float(ice_grid[row, col]), "limit": float(max_ice_conc), "status": "INFEASIBLE"})
                
            if risk_grid is not None and risk_grid[row, col] > max_risk:
                violations.append({"candidate_id": candidate.route_id, "constraint_name": "risk_threshold", "constraint_value": float(risk_grid[row, col]), "limit": float(max_risk), "status": "INFEASIBLE"})

        # Turning radius
        turning_radius = vessel_profile.get('turning_radius', 0.0)
        if turning_radius > 0.0 and len(path) >= 3:
            for i in range(len(path) - 2):
                p1 = np.array([route_xyh[i][0], route_xyh[i][1]])
                p2 = np.array([route_xyh[i+1][0], route_xyh[i+1][1]])
                p3 = np.array([route_xyh[i+2][0], route_xyh[i+2][1]])
                v1 = p2 - p1
                v2 = p3 - p2
                n1 = np.linalg.norm(v1)
                n2 = np.linalg.norm(v2)
                if n1 > 0 and n2 > 0:
                    cos_theta = np.dot(v1, v2) / (n1 * n2)
                    cos_theta = np.clip(cos_theta, -1.0, 1.0)
                    angle = np.arccos(cos_theta)
                    if turning_radius > 10.0 and angle > 1.57:
                        violations.append({"candidate_id": candidate.route_id, "constraint_name": "turning_radius", "constraint_value": float(angle), "limit": 1.57, "status": "INFEASIBLE"})

        # Time-aware CPA/TCPA using Hazard
        if self.hazard:
            res = cpa_tcpa(route_xyh, self.hazard)
            min_c = res["min_clearance_grid_m"]
            candidate.metadata["cpa"] = res["cpa_grid_m"]
            candidate.metadata["tcpa"] = res["tcpa_h"]
            
            required_clearance = vessel_profile.get("min_clearance_m", 0.0)
            if min_c < required_clearance:
                violations.append({"candidate_id": candidate.route_id, "constraint_name": "clearance", "constraint_value": min_c, "limit": required_clearance, "status": "INFEASIBLE"})

        if violations:
            candidate.feasibility_status = "INFEASIBLE"
        else:
            candidate.feasibility_status = "FEASIBLE"
            
        candidate.metadata["feasibility_violations"] = violations
