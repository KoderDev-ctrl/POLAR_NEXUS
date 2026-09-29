import numpy as np
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class CandidateRoute:
    """Standardized output structure for all RouteX16 algorithms."""
    route_id: str
    algorithm_name: str
    engine_category: str
    geometry: List[Tuple[float, float]] # List of (lat, lon)
    distance_nm: float
    estimated_time_hours: float
    estimated_fuel_kg: float
    environmental_risk: float
    metadata: Dict[str, Any]
    feasibility_status: str = "PENDING"


class RouteCostLayer:
    """
    Central cost/physics layer for RouteX16.
    Ensures all algorithms evaluate time, fuel, and risk uniformly.
    """
    def __init__(self, env_data: Dict[str, np.ndarray], vessel_profile: Dict[str, Any], grid_spec):
        """
        env_data requires: 'current_u', 'current_v', 'wind_u', 'wind_v', 'ice_conc', 'hazard_field'
        vessel_profile requires: 'base_speed_kts', 'ice_class', 'base_fuel_consumption_kg_h'
        """
        self.env = env_data
        self.vessel = vessel_profile
        self.grid = grid_spec
        
        self.layers_available = []
        self.layers_missing = []
        expected_layers = ["current_u", "current_v", "wind_u", "wind_v", "ice_conc", "hazard_field"]
        for layer in expected_layers:
            if layer in self.env and self.env[layer] is not None:
                self.layers_available.append(layer)
            else:
                self.layers_missing.append(layer)
        
    def evaluate_edge(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> Dict[str, float]:
        """
        Evaluates a single edge between two (lat, lon) points.
        Returns time (hours), fuel (kg), risk (normalized score).
        """
        lat1, lon1 = p1
        lat2, lon2 = p2
        
        # Distance (Haversine approx in nautical miles)
        R_nm = 3440.065
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance_nm = R_nm * c
        
        if distance_nm < 1e-6:
            return {"time_h": 0.0, "fuel_kg": 0.0, "risk": 0.0, "dist_nm": 0.0}

        # For this functional verification layer, we'll sample the env field at p1.
        # A full production implementation interpolates between p1 and p2.
        
        row, col = self.grid.latlon_to_index(lat1, lon1)
        
        try:
            if not self.grid.in_bounds(row, col):
                raise IndexError
                
            curr_u = self.env["current_u"][row, col] if "current_u" in self.layers_available else 0.0
            curr_v = self.env["current_v"][row, col] if "current_v" in self.layers_available else 0.0
            ice_c = self.env["ice_conc"][row, col] if "ice_conc" in self.layers_available else 0.0
            risk_val = self.env["hazard_field"][row, col] if "hazard_field" in self.layers_available else 0.0
        except IndexError:
            curr_u, curr_v, ice_c, risk_val = 0.0, 0.0, 0.0, 0.0

        # Calculate effective speed
        # Vessel heading vector
        heading_u = lon2 - lon1
        heading_v = lat2 - lat1
        norm = np.sqrt(heading_u**2 + heading_v**2) + 1e-6
        hu, hv = heading_u / norm, heading_v / norm
        
        # Current tailwind effect (dot product)
        current_boost_kts = (curr_u * hu + curr_v * hv) * 1.94384 # m/s to kts
        
        # Ice resistance penalty (heuristic: 1% speed loss per 1% ice conc above 10%)
        ice_penalty = max(0.0, (ice_c - 10.0) / 100.0)
        base_speed = self.vessel.get("base_speed_kts", 12.0)
        
        effective_speed = (base_speed - base_speed * ice_penalty) + current_boost_kts
        
        # Prevent division by zero or negative speed (vessel stuck)
        effective_speed = max(effective_speed, 0.5) 
        
        time_h = distance_nm / effective_speed
        
        # Fuel consumption
        base_fuel_rate = self.vessel.get("base_fuel_consumption_kg_h", 500.0)
        # Fuel burns higher if ice penalty is high (more engine load)
        fuel_rate = base_fuel_rate * (1.0 + ice_penalty * 2.0)
        fuel_kg = fuel_rate * time_h
        
        # Risk integrated over distance
        risk_total = risk_val * distance_nm
        
        return {
            "time_h": time_h,
            "fuel_kg": fuel_kg,
            "risk": risk_total,
            "dist_nm": distance_nm
        }

    def evaluate_route(self, route: List[Tuple[float, float]]) -> Dict[str, float]:
        """
        Evaluates a complete route path.
        """
        total_time = 0.0
        total_fuel = 0.0
        total_risk = 0.0
        total_dist = 0.0
        
        for i in range(len(route) - 1):
            edge_metrics = self.evaluate_edge(route[i], route[i+1])
            total_time += edge_metrics["time_h"]
            total_fuel += edge_metrics["fuel_kg"]
            total_risk += edge_metrics["risk"]
            total_dist += edge_metrics["dist_nm"]
            
        return {
            "time_h": total_time,
            "fuel_kg": total_fuel,
            "risk": total_risk,
            "dist_nm": total_dist
        }
