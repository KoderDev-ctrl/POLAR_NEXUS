import numpy as np
from typing import Dict

class SeaIceModel:
    """
    Sea-Ice Concentration Spatiotemporal network (ConvLSTM/U-Net).
    Currently implemented as a structural stub for integration.
    """
    def __init__(self, forecast_horizon_days: int = 1):
        self.forecast_horizon_days = forecast_horizon_days

    def predict(self, temporal_window: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Predicts sea-ice concentration for the next `forecast_horizon_days`.
        
        Args:
            temporal_window: Dict of variables. Expects "sea_ice_concentration" 
                             of shape (T, lat, lon).
                             
        Returns:
            np.ndarray: Predicted sea-ice concentration of shape (forecast_horizon_days, lat, lon).
        """
        if "sea_ice_concentration" not in temporal_window:
            raise ValueError("Missing required input: 'sea_ice_concentration'")
            
        sic = temporal_window["sea_ice_concentration"]
        
        if sic.ndim != 3:
            raise ValueError(f"Expected 3D array (T, lat, lon), got {sic.ndim}D")
            
        T, lat, lon = sic.shape
        if T == 0 or lat == 0 or lon == 0:
            raise ValueError("Input dimensions cannot be zero.")
            
        # Stub logic: 
        # In a real model, this would be `return self.unet.forward(temporal_window)`
        # Here we simulate prediction by taking the most recent timestep and adding slight noise/decay.
        
        latest_sic = sic[-1]
        
        predictions = np.zeros((self.forecast_horizon_days, lat, lon))
        for d in range(self.forecast_horizon_days):
            # Simulate a 1% decay per day + random noise
            noise = np.random.normal(0, 0.05, size=(lat, lon))
            pred = latest_sic * (0.99 ** (d + 1)) + noise
            predictions[d] = np.clip(pred, 0.0, 100.0)
            
        return predictions
