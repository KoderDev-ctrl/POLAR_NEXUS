from typing import Dict, Any, List, Optional
from polar_nexus.feasibility.gate import HardFeasibilityGate
from polar_nexus.routex16.cost_layer import CandidateRoute
from polar_nexus.routing.grid import GridSpec

class AdaptiveNavigationLoop:
    """
    Handles Category Locking and Risk-Triggered Adaptive Updates during active navigation.
    (Items 17 & 18)
    """
    def __init__(self, engines: Dict[str, Any], feasibility_gate: HardFeasibilityGate, config: Dict[str, Any]):
        # engines = {'TIME': time_engine, 'FUEL': fuel_engine, ...}
        self.engines = engines
        self.feasibility_gate = feasibility_gate
        self.config = config
        self.locked_category = None
        self.active_route: Optional[CandidateRoute] = None
        self.vessel_profile = None

    def lock_category(self, category: str, initial_route: CandidateRoute, vessel_profile: Dict[str, Any]):
        """
        Locks the navigation loop to a specific category (e.g. 'TIME_RISK').
        """
        if category not in self.engines:
            raise ValueError(f"Invalid category: {category}")
        self.locked_category = category
        self.active_route = initial_route
        self.vessel_profile = vessel_profile

    def trigger_update(self, current_pos: tuple, new_env_data: Dict[str, Any], refreshed_risk: float) -> Dict[str, Any]:
        """
        Evaluates the update trigger (Risk Delta).
        If triggered, re-runs ONLY the locked engine.
        Returns a dictionary with status and updated routes if applicable.
        """
        if not self.locked_category:
            return {'status': 'ERROR', 'message': 'No category locked.'}
            
        previous_risk = self.active_route.environmental_risk + self.active_route.metadata.get("route_risk_score", 0.0)
        risk_delta = refreshed_risk - previous_risk
        
        # Uncalibrated policy parameter threshold from config
        risk_threshold = self.config.get('adaptive_risk_delta_threshold', 10.0)

        if risk_delta < risk_threshold:
            return {'status': 'ADAPTIVE_CONTINUE', 'route': self.active_route, 'message': 'Risk delta below threshold. Continuing.', 'risk_delta': risk_delta, 'threshold': risk_threshold}

        # Triggered! Run ONLY the locked engine
        engine = self.engines[self.locked_category]
        dest = self.active_route.geometry[-1][:2]
        
        candidates = engine.generate_candidates(current_pos, dest, new_env_data.get("ice_conc", None))
        
        feasible_routes = self.feasibility_gate.filter_feasible_routes(candidates, self.vessel_profile, new_env_data)

        if not feasible_routes:
            return {
                'status': 'NO_FEASIBLE_ROUTE',
                'route': None,
                'message': 'Blocking conditions encountered. No feasible route available.'
            }

        # Simple mock scoring logic: select the best according to engine criteria
        # Assuming engines output sorted or we just pick [0]
        new_route = feasible_routes[0]
        self.active_route = new_route
        
        return {
            'status': 'ADAPTIVE_REROUTE',
            'route': new_route,
            'message': 'Rerouted due to risk trigger.',
            'risk_delta': risk_delta,
            'threshold': risk_threshold
        }
