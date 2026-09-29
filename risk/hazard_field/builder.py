import numpy as np
from typing import Optional, Dict, Any
import logging

class HazardFieldBuilder:
    """
    Consolidates multiple environmental inputs into a unified time-indexed hazard grid (0.0 to 1.0).
    Explicitly excludes CPA/TCPA routing risks per architecture specification.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def build_field(
        self, 
        sic: np.ndarray, 
        variance: np.ndarray, 
        bergs: Optional[np.ndarray] = None,
        wave_height: Optional[np.ndarray] = None,
        current_strength: Optional[np.ndarray] = None,
        bathymetry: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Builds the hazard field grid.
        All inputs must have the same shape.
        """
        if sic.size == 0 or variance.size == 0:
            raise ValueError("Empty input arrays provided.")
            
        if sic.shape != variance.shape:
            raise ValueError(f"Shape mismatch: sic {sic.shape} vs variance {variance.shape} must have same shape.")
            
        hazard = np.zeros_like(sic, dtype=float)
        
        # 1. Sea Ice Concentration (normalized 0-100 to 0-1)
        # Assuming sic is 0 to 100.
        hazard += np.clip(sic / 100.0, 0.0, 1.0) * 0.4
        
        # 2. Prediction Uncertainty (variance)
        # Assume max variance is around 50
        hazard += np.clip(variance / 50.0, 0.0, 1.0) * 0.2
        
        # 3. Icebergs (Density/Probability)
        if bergs is not None:
            if bergs.shape != sic.shape:
                raise ValueError(f"Shape mismatch: bergs {bergs.shape} vs sic {sic.shape}")
            hazard += np.clip(bergs, 0.0, 1.0) * 0.3
        else:
            self.logger.info("using mock iceberg input because Item 4 data not provided.")
            
        # 4. Wave Height / Current Strength (from ERA5/Copernicus)
        if wave_height is not None:
            if wave_height.shape != sic.shape:
                raise ValueError("Shape mismatch in wave_height")
            hazard += np.clip(wave_height / 10.0, 0.0, 1.0) * 0.05
        else:
            self.logger.info("using mock wave input because ERA5 data not provided.")
            
        if current_strength is not None:
            if current_strength.shape != sic.shape:
                raise ValueError("Shape mismatch in current_strength")
            hazard += np.clip(current_strength / 2.0, 0.0, 1.0) * 0.05
        else:
            self.logger.info("using mock current input because Copernicus data not provided.")
            
        # 5. Bathymetric Hazards (e.g. shallow waters)
        if bathymetry is not None:
            if bathymetry.shape != sic.shape:
                raise ValueError("Shape mismatch in bathymetry")
            # If depth < 20m, add hazard
            shallow_mask = (bathymetry < 20.0) & (bathymetry > 0.0)
            hazard[shallow_mask] += 0.5
            # If land (depth <= 0)
            land_mask = bathymetry <= 0.0
            hazard[land_mask] = 1.0
            
        return np.clip(hazard, 0.0, 1.0)
