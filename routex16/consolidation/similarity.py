import numpy as np
from typing import List, Tuple

# Threshold for duplicate route filtering (in kilometers)
DUPLICATE_ROUTE_THRESHOLD_KM = 10.0

def haversine_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1, lon1 = p1
    lat2, lon2 = p2
    
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371.0 # Radius of earth in kilometers
    return c * r

def discrete_frechet_distance(P: List[Tuple[float, float]], Q: List[Tuple[float, float]]) -> float:
    """
    Computes the discrete Fréchet distance between two polygonal curves (routes).
    P and Q are lists of (lat, lon) tuples.
    Returns distance in kilometers.
    """
    if not P or not Q:
        raise ValueError("Routes cannot be empty.")
        
    n = len(P)
    m = len(Q)
    
    # Memoization table
    ca = np.full((n, m), -1.0)
    
    def _c(i, j):
        if ca[i, j] > -1.0:
            return ca[i, j]
            
        dist = haversine_distance(P[i], Q[j])
        
        if i == 0 and j == 0:
            ca[i, j] = dist
        elif i > 0 and j == 0:
            ca[i, j] = max(_c(i-1, 0), dist)
        elif i == 0 and j > 0:
            ca[i, j] = max(_c(0, j-1), dist)
        elif i > 0 and j > 0:
            ca[i, j] = max(min(_c(i-1, j), _c(i-1, j-1), _c(i, j-1)), dist)
        else:
            ca[i, j] = float('inf')
            
        return ca[i, j]
        
    return _c(n - 1, m - 1)
