import numpy as np
from typing import Dict, Optional

class HazardFieldBuilder:
    """
    Consolidated environmental hazard field builder.
    Maps sea ice concentration, uncertainty, and iceberg presence to a 0-1 cost grid.
    Does NOT include route-specific CPA/TCPA (per architecture fix in Item 15).
    """
    def __init__(self, ice_weight: float = 0.5, uncertainty_weight: float = 0.2, iceberg_weight: float = 0.3):
        self.weights = np.array([ice_weight, uncertainty_weight, iceberg_weight])
        self.weights = self.weights / np.sum(self.weights) # normalize

    def build_field(self, 
                    sea_ice_mean: np.ndarray, 
                    sea_ice_var: np.ndarray,
                    iceberg_density: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Builds the static hazard field.
        
        Args:
            sea_ice_mean: 2D or 3D array of predicted sea ice concentration (0-100).
            sea_ice_var: 2D or 3D array of uncertainty variance.
            iceberg_density: Grid of iceberg density matching the spatial dims.
                             If None, assumed zero.
                             
        Returns:
            np.ndarray: Hazard field grid (0.0 to 1.0).
        """
        if sea_ice_mean.shape != sea_ice_var.shape:
            raise ValueError("Sea ice mean and variance must have the same shape.")
            
        if iceberg_density is None:
            iceberg_density = np.zeros_like(sea_ice_mean)
        elif iceberg_density.shape != sea_ice_mean.shape:
            raise ValueError("Iceberg density must have the same shape as sea ice fields.")
            
        if sea_ice_mean.size == 0:
            raise ValueError("Empty input fields.")

        # Normalize features to 0-1
        # Sea ice is 0-100
        norm_ice = np.clip(sea_ice_mean / 100.0, 0.0, 1.0)
        
        # Variance normalization (heuristic max variance)
        max_var = np.max(sea_ice_var) if np.max(sea_ice_var) > 0 else 1.0
        norm_var = np.clip(sea_ice_var / max_var, 0.0, 1.0)
        
        # Iceberg density normalization (heuristic max density)
        max_dens = np.max(iceberg_density) if np.max(iceberg_density) > 0 else 1.0
        norm_bergs = np.clip(iceberg_density / max_dens, 0.0, 1.0)
        
        # Combine
        hazard = (norm_ice * self.weights[0] + 
                  norm_var * self.weights[1] + 
                  norm_bergs * self.weights[2])
                  
        return np.clip(hazard, 0.0, 1.0)
