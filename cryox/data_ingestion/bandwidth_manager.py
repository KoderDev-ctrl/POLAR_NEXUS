from typing import Dict, Any, List
import numpy as np

class BandwidthManager:
    """
    Handles bandwidth-aware data ingestion. 
    In LOW bandwidth mode, it aggressively downsamples data grids and drops secondary variables
    to save satellite bandwidth.
    """
    def __init__(self, mode: str = "HIGH"):
        self.mode = mode.upper()

    def process_incoming_env_data(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes incoming environmental data based on bandwidth mode.
        """
        if self.mode != "LOW":
            return env_data # Pass through untouched

        processed = {}
        
        # In LOW mode, keep only essential variables
        essential_vars = ['ice_grid', 'risk_grid', 'depth_grid']
        
        for key in essential_vars:
            if key in env_data:
                grid = env_data[key]
                if isinstance(grid, np.ndarray):
                    # Downsample by taking every 5th element (simulating 50km vs 10km)
                    processed[key] = grid[::5, ::5]
                else:
                    processed[key] = grid

        # We drop non-essential variables like 'iceberg_drift_vectors', 'thickness_variance', etc.
        return processed
