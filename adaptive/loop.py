from typing import Dict, Any, List, Optional
from polar_nexus.feasibility.gate import HardFeasibilityGate

class AdaptiveNavigationLoop:
    """
    Handles Category Locking and Risk-Triggered Adaptive Updates during active navigation.
    (Items 17 & 18)
    """
    def __init__(self, engines: Dict[str, Any], feasibility_gate: HardFeasibilityGate):
        # engines = {'TIME': time_engine, 'FUEL': fuel_engine, ...}
        self.engines = engines
        self.feasibility_gate = feasibility_gate
        self.locked_category = None
        self.active_route = None
        self.vessel_profile = None

    def lock_category(self, category: str, initial_route: Dict[str, Any], vessel_profile: Dict[str, Any]):
        """
        Locks the navigation loop to a specific category (e.g. 'TIME_RISK').
        """
        if category not in self.engines:
            raise ValueError(f"Invalid category: {category}")
        self.locked_category = category
        self.active_route = initial_route
        self.vessel_profile = vessel_profile

    def trigger_update(self, current_pos: tuple, new_env_data: Dict[str, Any], risk_delta: float, risk_threshold: float = 10.0) -> Dict[str, Any]:
        """
        Evaluates the update trigger (e.g., Risk Delta).
        If triggered, re-runs ONLY the locked engine.
        Returns a dictionary with status and updated routes if applicable.
        """
        if not self.locked_category:
            return {'status': 'ERROR', 'message': 'No category locked.'}

        # Trigger logic: Only replan if risk increases significantly or periodically (simulated here via delta)
        if risk_delta < risk_threshold:
            return {'status': 'CONTINUE', 'route': self.active_route, 'message': 'Risk delta below threshold. Continuing.'}

        # Triggered! Run ONLY the locked engine
        engine = self.engines[self.locked_category]
        dest = self.active_route['waypoints'][-1] if self.active_route and 'waypoints' in self.active_route else (0,0)
        
        candidates = engine.generate_candidates(current_pos, dest, new_env_data.get('ice_grid', None))
        
        # Convert raw paths to standard candidate dict format
        candidate_dicts = []
        for i, path in enumerate(candidates):
            candidate_dicts.append({
                'id': f'adaptive_{i}',
                'waypoints': path,
                'engine': self.locked_category
            })

        # Hard Feasibility Check on new candidates
        feasible_routes = self.feasibility_gate.filter_feasible_routes(candidate_dicts, self.vessel_profile, new_env_data)

        if not feasible_routes:
            return {
                'status': 'NO_FEASIBLE_ROUTE',
                'route': None,
                'message': 'Blocking conditions encountered. No feasible route available.'
            }

        # Compare with active route
        # If active route is still feasible (simulated by checking if it's in the set, or just taking the best new one)
        # For simplicity in this architectural implementation, we just select the first feasible new one as a "REROUTE"
        new_route = feasible_routes[0]
        self.active_route = new_route
        
        return {
            'status': 'REROUTE',
            'route': new_route,
            'message': 'Rerouted due to risk trigger.'
        }
