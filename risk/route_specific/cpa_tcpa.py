import numpy as np
from typing import List, Tuple, Dict, Any

class RouteRiskCalculator:
    """
    Calculates Route-Specific Risk factors, primarily CPA (Closest Point of Approach)
    and TCPA (Time to Closest Point of Approach) for moving hazards like icebergs.
    This must happen AFTER the candidate route is generated.
    """
    def __init__(self, safe_distance_threshold: float = 2.0):
        self.safe_distance_threshold = safe_distance_threshold

    def compute_cpa_tcpa(self, route: List[Tuple[float, float]], vessel_speed: float, icebergs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes CPA and TCPA for a route against a list of predicted iceberg trajectories.
        `icebergs` format: [{'trajectory': [(x0, y0), (x1, y1), ...], 'speed': float}]
        
        Returns a risk dictionary containing max route-specific risk and CPA/TCPA details.
        """
        min_cpa = float('inf')
        min_tcpa = float('inf')
        risk_score = 0.0

        if not route or not icebergs:
            return {'min_cpa': min_cpa, 'min_tcpa': min_tcpa, 'route_risk_score': 0.0}

        # Simulated discrete time-step CPA calculation
        for iceberg in icebergs:
            traj = iceberg.get('trajectory', [])
            if not traj:
                continue
                
            # Compare point-by-point (simulating concurrent time-steps)
            for t in range(min(len(route), len(traj))):
                vessel_pos = np.array(route[t])
                berg_pos = np.array(traj[t])
                
                dist = np.linalg.norm(vessel_pos - berg_pos)
                if dist < min_cpa:
                    min_cpa = dist
                    min_tcpa = t * (1.0 / max(vessel_speed, 0.1)) # simulated time

        # Compute risk score inversely proportional to CPA if within threshold
        if min_cpa < self.safe_distance_threshold:
            # Dangerously close
            risk_score = (self.safe_distance_threshold - min_cpa) / self.safe_distance_threshold * 100.0
        
        return {
            'min_cpa': float(min_cpa),
            'min_tcpa': float(min_tcpa),
            'route_risk_score': float(risk_score)
        }

    def append_route_risk(self, candidate: Dict[str, Any], vessel_speed: float, icebergs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Updates a candidate route dictionary with calculated CPA/TCPA risk.
        """
        route = candidate.get('waypoints', [])
        risk_data = self.compute_cpa_tcpa(route, vessel_speed, icebergs)
        
        candidate['cpa_tcpa'] = risk_data
        
        # Add to any existing environmental risk
        existing_risk = candidate.get('environmental_risk', 0.0)
        candidate['total_route_risk'] = existing_risk + risk_data['route_risk_score']
        
        return candidate
