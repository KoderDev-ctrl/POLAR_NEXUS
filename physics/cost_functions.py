import numpy as np
from typing import Tuple, Dict

class PhysicsCostEngine:
    """
    Translates environmental data (CryoX output) into navigable costs for RouteX16.
    """
    def __init__(self, vessel_speed_knots: float, fuel_consumption_rate: float):
        """
        Args:
            vessel_speed_knots: Nominal speed of the vessel in knots.
            fuel_consumption_rate: Nominal fuel burned per hour at nominal speed.
        """
        self.nominal_speed = vessel_speed_knots
        self.fuel_rate = fuel_consumption_rate
        # 1 knot = 1.852 km/h
        self.nominal_speed_kmh = vessel_speed_knots * 1.852

    def compute_time_cost(self, distance_km: float, speed_modifier: float = 1.0) -> float:
        """
        Computes travel time in hours.
        Args:
            distance_km: Distance to travel.
            speed_modifier: Multiplier for speed (e.g. 0.5 if slowed by ice).
        """
        if distance_km < 0:
            raise ValueError("Distance cannot be negative.")
        if speed_modifier <= 0:
            raise ValueError("Speed modifier must be strictly positive.")
            
        effective_speed = self.nominal_speed_kmh * speed_modifier
        return distance_km / effective_speed

    def compute_fuel_cost(self, time_hours: float, engine_load_modifier: float = 1.0) -> float:
        """
        Computes fuel consumed.
        """
        if time_hours < 0:
            raise ValueError("Time cannot be negative.")
        if engine_load_modifier < 0:
            raise ValueError("Engine load modifier cannot be negative.")
            
        return time_hours * self.fuel_rate * engine_load_modifier

    def compute_risk_cost(self, distance_km: float, hazard_score: float) -> float:
        """
        Computes integrated risk over the segment.
        Strictly excludes CPA/TCPA (route-specific tracking) per architecture constraint.
        Args:
            hazard_score: The 0.0 to 1.0 value from the CryoX HazardFieldBuilder.
        """
        if distance_km < 0:
            raise ValueError("Distance cannot be negative.")
        if not (0.0 <= hazard_score <= 1.0):
            raise ValueError("Hazard score must be normalized between 0.0 and 1.0.")
            
        # Risk is proportional to the distance traveled through the hazard
        return distance_km * hazard_score

    def evaluate_edge(self, distance_km: float, hazard_score: float, ice_concentration: float) -> Dict[str, float]:
        """
        Helper to evaluate a full edge cost profile based on physical heuristics.
        """
        # Heuristic: dense ice slows the ship and increases engine load
        speed_mod = 1.0
        load_mod = 1.0
        
        if ice_concentration > 80.0:
            speed_mod = 0.3
            load_mod = 1.8
        elif ice_concentration > 40.0:
            speed_mod = 0.6
            load_mod = 1.4
        elif ice_concentration > 10.0:
            speed_mod = 0.8
            load_mod = 1.1
            
        t_cost = self.compute_time_cost(distance_km, speed_mod)
        f_cost = self.compute_fuel_cost(t_cost, load_mod)
        r_cost = self.compute_risk_cost(distance_km, hazard_score)
        
        return {
            "time_hours": t_cost,
            "fuel_units": f_cost,
            "risk_score": r_cost
        }
