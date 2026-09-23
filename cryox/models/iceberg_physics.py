import numpy as np
from typing import Dict, List, Tuple

class IcebergPhysicsModel:
    """
    Iceberg physics drift model (momentum/force-balance).
    Based on Bigg et al. (1997) formulation.
    """
    # Physical constants (sourced from Bigg et al. and standard oceanographic values)
    RHO_WATER = 1027.5  # kg/m^3 (sea water density)
    RHO_AIR = 1.225     # kg/m^3 (air density)
    OMEGA = 7.2921e-5   # rad/s (Earth's angular velocity)
    EARTH_RADIUS = 6371000.0 # meters
    
    # Drag coefficients (typical order of magnitude from literature)
    C_DW = 0.9  # Water drag coefficient
    C_DA = 1.3  # Air drag coefficient

    def __init__(self, time_step_hours: float = 1.0):
        self.dt = time_step_hours * 3600.0

    def predict_drift(self, initial_lats: np.ndarray, initial_lons: np.ndarray, 
                      env_data: Dict[str, np.ndarray], steps: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predicts iceberg drift over `steps` time steps.
        
        Args:
            initial_lats, initial_lons: 1D arrays of initial iceberg positions.
            env_data: Dict with 'wind_u', 'wind_v', 'currents_u', 'currents_v' arrays.
                      For this stub, assume they are constant fields spatially aligned with the icebergs.
            steps: Number of simulation steps.
            
        Returns:
            Tuple of (lats, lons) arrays of shape (steps+1, num_icebergs)
        """
        if len(initial_lats) != len(initial_lons):
            raise ValueError("Lat and lon arrays must have the same length.")
        
        required_env = {"wind_u", "wind_v", "currents_u", "currents_v"}
        for var in required_env:
            if var not in env_data:
                raise ValueError(f"Missing required environmental data: {var}")
                
        num_icebergs = len(initial_lats)
        out_lats = np.zeros((steps + 1, num_icebergs))
        out_lons = np.zeros((steps + 1, num_icebergs))
        
        out_lats[0] = initial_lats
        out_lons[0] = initial_lons
        
        # Initial velocities (assume zero relative to water initially)
        u_i = np.zeros(num_icebergs)
        v_i = np.zeros(num_icebergs)
        
        for t in range(1, steps + 1):
            # Stub simplification: sample environmental forces directly from 0-index for all icebergs
            # In a real model, we would interpolate `env_data` at `out_lats[t-1]`, `out_lons[t-1]`
            # Assuming shape (num_icebergs,) for env arrays
            u_a = env_data["wind_u"]
            v_a = env_data["wind_v"]
            u_w = env_data["currents_u"]
            v_w = env_data["currents_v"]
            
            lat_rad = np.radians(out_lats[t-1])
            f = 2 * self.OMEGA * np.sin(lat_rad) # Coriolis parameter
            
            # Simple force balance stub (ignoring mass/area terms which would divide forces to get acceleration)
            # F_a ~ rho_a * C_DA * |V_a - V_i| * (V_a - V_i)
            # F_w ~ rho_w * C_DW * |V_w - V_i| * (V_w - V_i)
            # For the stub, we just linearly combine them with empirical scaling to get delta V
            
            # Wind influence is roughly 2% of wind speed, current is roughly 100%
            alpha = 0.02
            u_i_target = u_w + alpha * u_a
            v_i_target = v_w + alpha * v_a
            
            # Add Coriolis deflection (simplification)
            u_i = u_i_target + f * v_i_target * self.dt
            v_i = v_i_target - f * u_i_target * self.dt
            
            # Update positions (convert m/s to degrees)
            # lat = lat + (v * dt) / R
            # lon = lon + (u * dt) / (R * cos(lat))
            dlat = (v_i * self.dt) / self.EARTH_RADIUS
            dlon = (u_i * self.dt) / (self.EARTH_RADIUS * np.cos(lat_rad))
            
            out_lats[t] = out_lats[t-1] + np.degrees(dlat)
            out_lons[t] = out_lons[t-1] + np.degrees(dlon)
            
            # Handle dateline crossing
            out_lons[t] = ((out_lons[t] + 180) % 360) - 180
            
        return out_lats, out_lons
