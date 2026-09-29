import math
import numpy as np
from typing import Tuple, Optional
import yaml
import os

from polar_nexus.iceberg.core import to_xy, to_latlon

class GridSpec:
    """
    Authoritative grid abstraction for RouteX16.
    Converts between (row, col), (x, y) projected, and (lat, lon).
    EPSG:3031 is strictly used via core implementations.
    """
    CRS = "EPSG:3031"
    
    def __init__(self, origin_x: float, origin_y: float, cell_km: float, shape: Tuple[int, int]):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.cell_km = cell_km
        self.cell_m = cell_km * 1000.0
        self.shape = shape # (rows, cols)
        
    @classmethod
    def from_bbox(cls, min_lat: float, min_lon: float, max_lat: float, max_lon: float, cell_km: float = 5.0, max_size: int = 300) -> 'GridSpec':
        xs, ys = [], []
        for lat in np.linspace(min_lat, max_lat, 10):
            for lon in np.linspace(min_lon, max_lon, 10):
                x, y = to_xy(lat, lon)
                xs.append(x)
                ys.append(y)
                
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        width_m = max_x - min_x
        height_m = max_y - min_y
        
        # We want the final grid (including 10% buffer) to be at most max_size
        # The unbuffered size can be at most max_size / 1.2
        target_max_size = int(max_size / 1.2)
        
        cols = int(math.ceil(width_m / (cell_km * 1000.0)))
        rows = int(math.ceil(height_m / (cell_km * 1000.0)))
        
        if cols > target_max_size or rows > target_max_size:
            ratio = max(cols / target_max_size, rows / target_max_size)
            cell_km = cell_km * ratio
            cols = int(math.ceil(width_m / (cell_km * 1000.0)))
            rows = int(math.ceil(height_m / (cell_km * 1000.0)))
            
        buffer_cols = int(cols * 0.1)
        buffer_rows = int(rows * 0.1)
        
        final_rows = min(rows + 2*buffer_rows, max_size)
        final_cols = min(cols + 2*buffer_cols, max_size)
        
        origin_x = min_x - buffer_cols * (cell_km * 1000.0)
        origin_y = min_y - buffer_rows * (cell_km * 1000.0)
        
        return cls(origin_x, origin_y, cell_km, (final_rows, final_cols))

    def latlon_to_xy(self, lat: float, lon: float) -> Tuple[float, float]:
        # returns x, y
        return to_xy(lat, lon)
        
    def xy_to_latlon(self, x: float, y: float) -> Tuple[float, float]:
        # returns lat, lon
        return to_latlon(x, y)

    def xy_to_index(self, x: float, y: float) -> Tuple[int, int]:
        # returns row, col
        col = int((x - self.origin_x) // self.cell_m)
        row = int((y - self.origin_y) // self.cell_m)
        return row, col
        
    def index_to_xy(self, row: int, col: int, center: bool = True) -> Tuple[float, float]:
        offset = 0.5 if center else 0.0
        x = self.origin_x + (col + offset) * self.cell_m
        y = self.origin_y + (row + offset) * self.cell_m
        return x, y
        
    def latlon_to_index(self, lat: float, lon: float) -> Tuple[int, int]:
        x, y = self.latlon_to_xy(lat, lon)
        return self.xy_to_index(x, y)
        
    def index_to_latlon(self, row: int, col: int) -> Tuple[float, float]:
        x, y = self.index_to_xy(row, col)
        return self.xy_to_latlon(x, y)

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.shape[0] and 0 <= col < self.shape[1]
