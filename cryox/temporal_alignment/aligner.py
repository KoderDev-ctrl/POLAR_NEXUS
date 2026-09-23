import numpy as np
from typing import Dict, List

class TemporalAligner:
    """
    Builds fixed-length sliding time windows per grid cell for model input,
    aligned to the coarsest-frequency input dataset (daily).
    """
    def __init__(self, window_size_days: int):
        self.window_size_days = window_size_days
        
    def align(self, time_series_data: Dict[str, np.ndarray], timestamps: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Converts sequence data (time, lat, lon) into sliding windows of (T_window, lat, lon).
        
        timestamps is expected to be an array of daily indices or datetime-like objects mapped to daily steps.
        For this mock implementation, we assume timestamps is an array of daily offsets.
        """
        num_timesteps = len(timestamps)
        
        if num_timesteps < self.window_size_days:
            raise ValueError(f"Insufficient data: {num_timesteps} days available, but window size is {self.window_size_days} days.")
            
        # We want to yield arrays of shape (num_windows, window_size_days, lat, lon)
        num_windows = num_timesteps - self.window_size_days + 1
        
        aligned_data = {}
        for var, arr in time_series_data.items():
            if arr.shape[0] != num_timesteps:
                raise ValueError(f"Variable '{var}' time dimension ({arr.shape[0]}) does not match timestamps ({num_timesteps})")
                
            # Create sliding windows efficiently using strides or simply loop
            # Simple loop implementation for readability and safety
            shape = (num_windows, self.window_size_days) + arr.shape[1:]
            windowed_arr = np.zeros(shape, dtype=arr.dtype)
            
            for i in range(num_windows):
                windowed_arr[i] = arr[i : i + self.window_size_days]
                
            aligned_data[var] = windowed_arr
            
        return aligned_data
