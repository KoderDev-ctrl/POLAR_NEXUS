import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from polar_nexus.routing.grid import GridSpec
from polar_nexus.iceberg.core import Hazard

class HazardFieldBuilder:
    @staticmethod
    def build_field(assessments: List[Dict[str, Any]], grid: GridSpec, t0: datetime, t1: datetime) -> np.ndarray:
        return rasterise_iceberg_hazard(assessments, grid, t0, t1)

def rasterise_iceberg_hazard(assessments: List[Dict[str, Any]], grid: GridSpec, t0: datetime, t1: datetime) -> np.ndarray:
    """
    Creates a conservative STATIC SEARCH/PRUNING raster representation of hazards.
    This sweeps the hazard over the voyage time window [t0, t1] and unions the occupied grid cells.
    """
    field = np.zeros(grid.shape, dtype=np.float32)
    
    # Generate points across the grid
    # We will check if the center of each grid cell is within the swept envelope
    rows, cols = grid.shape
    y_coords = grid.origin_y + (np.arange(rows) + 0.5) * grid.cell_m
    x_coords = grid.origin_x + (np.arange(cols) + 0.5) * grid.cell_m
    xx, yy = np.meshgrid(x_coords, y_coords)
    
    # We sample the time window with enough resolution to capture the sweep
    # Max time is t1 - t0. Let's do 1-hour steps.
    total_hours = max(0, (t1 - t0).total_seconds() / 3600.0)
    steps = max(1, int(total_hours))
    times_h = np.linspace(0, total_hours, steps + 1)
    
    for ass in assessments:
        # Reconstruct RouteHazardInput or just Hazard
        rh = ass.get("route_hazard")
        if not rh:
            continue
        hz = rh.hazard
        
        # Calculate time offset from hazard base_time to voyage t0
        offset_h = (t0 - hz.base_time).total_seconds() / 3600.0
        
        for h in times_h:
            hz_time_h = offset_h + h
            # if hz_time_h < 0, it means it's before the hazard observation, we just use h=0 behavior conservatively or ignore
            hz_time_h = max(0.0, hz_time_h)
            
            c1, c2 = hz.centres(hz_time_h)
            r = hz.radius_grid_m(hz_time_h)
            
            # Unbounded hazard? Max radius is 60km.
            if hz.unbounded(hz_time_h):
                # Mark a very large area or just mark the 60km radius + flag
                pass # the radius function already caps or continues, but unbounded status is meant to just be a large flag.
                # Actually, radius_grid_m returns the radius, we just apply it.
                
            dist1 = np.hypot(xx - c1[0], yy - c1[1])
            dist2 = np.hypot(xx - c2[0], yy - c2[1])
            
            # Simple union of two circles (kinematic and m6 centres)
            mask = (dist1 <= r) | (dist2 <= r)
            
            # A more precise swept envelope would include the hull between c1 and c2,
            # but since they both start at p4 and diverge, the union of circles over time
            # effectively covers the swept area if time steps are fine enough.
            # To handle collinear interpolation at a single time step:
            # Distance from point to line segment c1-c2
            # Vector c1 to c2
            v = c2 - c1
            l2 = v[0]**2 + v[1]**2
            if l2 > 0:
                t = np.clip(((xx - c1[0])*v[0] + (yy - c1[1])*v[1]) / l2, 0, 1)
                proj_x = c1[0] + t * v[0]
                proj_y = c1[1] + t * v[1]
                dist_seg = np.hypot(xx - proj_x, yy - proj_y)
                mask |= (dist_seg <= r)
                
            field[mask] = 1.0
            
    return field
