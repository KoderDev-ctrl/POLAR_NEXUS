import numpy as np
from typing import Dict, Tuple

class PreprocessingPipeline:
    """
    Pipeline for cleaning CryoX datasets.
    Steps:
    1. Physical validity/range checks
    2. Outlier detection (Z-score thresholding)
    3. Missing value handling (interpolation for short gaps, NaN for long gaps)
    """
    def __init__(self, z_threshold: float = 3.0, missing_gap_threshold: int = 3):
        self.z_threshold = z_threshold
        self.missing_gap_threshold = missing_gap_threshold
        
    def process(self, data: Dict[str, np.ndarray], var_limits: Dict[str, Tuple[float, float]]) -> Dict[str, np.ndarray]:
        processed = {}
        for var, arr in data.items():
            # Convert to float to allow NaNs
            arr_copy = np.array(arr, dtype=float)
            
            # 1. Range checks
            if var in var_limits:
                min_val, max_val = var_limits[var]
                arr_copy = np.where((arr_copy < min_val) | (arr_copy > max_val), np.nan, arr_copy)
                
            # 2. Outlier detection
            valid_mask = ~np.isnan(arr_copy)
            if np.any(valid_mask):
                mean = np.mean(arr_copy[valid_mask])
                std = np.std(arr_copy[valid_mask])
                if std > 1e-6:
                    z_scores = np.abs((arr_copy - mean) / std)
                    arr_copy[valid_mask] = np.where(z_scores[valid_mask] > self.z_threshold, np.nan, arr_copy[valid_mask])
                    
            # 3. Missing value handling (1D along last axis for simplicity)
            # Short gaps are interpolated, long gaps remain NaN.
            arr_copy = self._handle_missing_values(arr_copy)
            processed[var] = arr_copy
            
        return processed
        
    def _handle_missing_values(self, arr: np.ndarray, axis: int = 0) -> np.ndarray:
        """
        Linearly interpolates short gaps along the specified axis.
        Leaves gaps longer than self.missing_gap_threshold as NaN.
        """
        if not np.any(np.isnan(arr)) or np.all(np.isnan(arr)):
            return arr.copy()

        # Apply the 1D interpolation along the specified axis
        return np.apply_along_axis(self._interp_1d, axis=axis, arr=arr)

    def _interp_1d(self, line: np.ndarray) -> np.ndarray:
        """
        1D interpolation logic for a single slice (e.g. one time series for a grid cell).
        """
        nans = np.isnan(line)
        if not np.any(nans) or np.all(nans):
            return line.copy()

        valid_idx = np.where(~nans)[0]
        valid_vals = line[valid_idx]

        interp_line = np.interp(np.arange(len(line)), valid_idx, valid_vals)

        # Re-apply NaNs to long gaps
        import itertools
        current_idx = 0
        for is_nan, group in itertools.groupby(nans):
            length = sum(1 for _ in group)
            if is_nan and length > self.missing_gap_threshold:
                interp_line[current_idx : current_idx + length] = np.nan
            current_idx += length

        # Do not extrapolate edges
        first_valid = valid_idx[0]
        last_valid = valid_idx[-1]
        interp_line[:first_valid] = np.nan
        interp_line[last_valid + 1:] = np.nan

        return interp_line
