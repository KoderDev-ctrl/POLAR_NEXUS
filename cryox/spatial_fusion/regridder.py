import numpy as np
from scipy.interpolate import RegularGridInterpolator
from typing import Dict, Tuple, Any

class SpatialRegridder:
    """
    Regrids data from various sources (NSIDC, Copernicus, ERA5) onto a single analysis grid.
    Distinguishes between flux/area variables (conservative) and point variables (bilinear).
    """
    
    # Variables that are flux/area quantities requiring conservative regridding
    CONSERVATIVE_VARS = {"sea_ice_concentration", "sea_ice_conc"}
    
    # Variables that are point quantities requiring bilinear interpolation
    BILINEAR_VARS = {"currents_u", "currents_v", "wind_u", "wind_v", "sst", "ssh", "pressure", "waves", "sea_ice_velocity", "sea_ice_thickness", "depth"}

    def __init__(self, target_lats: np.ndarray, target_lons: np.ndarray):
        """
        Initializes the regridder with the common analysis grid.
        target_lats and target_lons should be 1D arrays defining the grid.
        """
        self.target_lats = target_lats
        self.target_lons = target_lons
        # Create meshgrid for target points to evaluate
        self.target_mesh = np.meshgrid(self.target_lats, self.target_lons, indexing='ij')

    def regrid(self, source_lats: np.ndarray, source_lons: np.ndarray, data: Dict[str, np.ndarray]) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Regrids the dictionary of variables onto the target grid.
        Returns a tuple of (regridded_data, metadata).
        """
        regridded = {}
        metadata = {}
        
        for var, arr in data.items():
            if var in self.CONSERVATIVE_VARS:
                # IMPLEMENTATION FIX (Item 1): xESMF unavailable. Using documented bilinear fallback.
                regridded[var] = self._interpolate_bilinear(source_lats, source_lons, arr)
                metadata[var] = {
                    "method": "bilinear_fallback", 
                    "accuracy_note": "Approximation due to xESMF unavailability"
                }
            elif var in self.BILINEAR_VARS:
                regridded[var] = self._interpolate_bilinear(source_lats, source_lons, arr)
                metadata[var] = {"method": "bilinear"}
            else:
                # If variable type is unknown, raise error per strict ambiguity handling
                raise ValueError(f"Interpolation method for variable '{var}' is not defined.")
        return regridded, metadata

    def _interpolate_bilinear(self, src_lats: np.ndarray, src_lons: np.ndarray, arr: np.ndarray) -> np.ndarray:
        # Check dimensions
        if arr.shape != (len(src_lats), len(src_lons)):
            raise ValueError(f"Array shape {arr.shape} does not match lat/lon dims ({len(src_lats)}, {len(src_lons)})")
            
        interp = RegularGridInterpolator((src_lats, src_lons), arr, method='linear', bounds_error=False, fill_value=np.nan)
        # Reshape the target mesh points for the interpolator
        pts = np.stack([self.target_mesh[0].flatten(), self.target_mesh[1].flatten()], axis=1)
        res = interp(pts)
        return res.reshape((len(self.target_lats), len(self.target_lons)))


