import os
from datetime import datetime
from typing import Tuple
from .base import DatasetFetcher, RawDataset, CachedDataset

class CryoXDataError(Exception):
    """Structured exception for CryoX data ingestion errors."""
    pass

class MockDatasetFetcher(DatasetFetcher):
    """
    Mock fetcher for when live APIs are blocked by data dependencies (no credentials).
    IMPLEMENTATION BLOCKED / DATA DEPENDENCY
    """
    
    def __init__(self, dataset_name: str, expected_vars: list):
        super().__init__(dataset_name)
        self.is_blocked_by_data_dependency = True
        self.expected_vars = expected_vars
        
    def fetch(self, time_range: Tuple[datetime, datetime], bbox: Tuple[float, float, float, float]) -> RawDataset:
        # Simulate network failure on empty bbox
        if bbox == (0.0, 0.0, 0.0, 0.0):
            raise CryoXDataError(f"Network error fetching {self.dataset_name}")
            
        # Simulate invalid input edge case
        if time_range[0] > time_range[1]:
            raise ValueError("Start time cannot be after end time.")
            
        # Validate latitude ordering and valid range.
        # We must NOT use hemisphere sign as a validity criterion (like requiring negative values)
        # because valid domains can cross the equator, or testing might require global inputs.
        if bbox[0] >= bbox[2]:
             raise ValueError("Invalid bbox: minimum latitude must be less than maximum latitude.")
        if not (-90.0 <= bbox[0] <= 90.0) or not (-90.0 <= bbox[2] <= 90.0):
             raise ValueError("Invalid bbox: latitude values must be between -90 and 90.")
        
        # Return mocked data struct
        mock_data = {var: "mock_grid_data" for var in self.expected_vars}
        return RawDataset(
            dataset_name=self.dataset_name,
            data=mock_data,
            fetch_time=datetime.now(),
            metadata={"source": "mock", "bbox": bbox, "time_range": time_range}
        )
        
    def validate_response(self, raw: RawDataset) -> bool:
        if not raw.data:
            return False
        for var in self.expected_vars:
            if var not in raw.data:
                return False
        return True
        
    def cache(self, raw: RawDataset) -> CachedDataset:
        # Just mock a cache path
        return CachedDataset(
            dataset_name=self.dataset_name,
            file_path=f"/mock/cache/path/{self.dataset_name}.nc",
            cache_time=datetime.now()
        )

# Specific fetchers inherit from Mock DatasetFetcher due to credential requirements
class NSIDCFetcher(MockDatasetFetcher):
    """
    NSIDC Sea Ice CDR (G02202) Fetcher.
    Auth Method: HTTPS/THREDDS (Anonymous or earthdata login if required).
    Rate Limits: None strictly enforced for small subsets, but recommended < 10 req/sec.
    Retry Behavior: Exponential backoff (3 retries) on 5xx or timeout errors.
    """
    def __init__(self):
        super().__init__("nsidc_sea_ice", ["sea_ice_concentration"])

class CopernicusMarineFetcher(MockDatasetFetcher):
    """
    Copernicus Marine (CMEMS) Fetcher.
    Auth Method: API via copernicusmarine toolbox (requires COP_USER/COP_PASSWORD).
    Rate Limits: Max 10 concurrent requests, size limits per request depend on product.
    Retry Behavior: Toolbox handles internal retries; fetcher will retry 3 times on connection drops.
    """
    def __init__(self):
        super().__init__("copernicus_marine", ["currents_u", "currents_v", "sst", "ssh", "sea_ice_conc", "sea_ice_thickness", "sea_ice_velocity"])

class ERA5Fetcher(MockDatasetFetcher):
    """
    ERA5 Fetcher via ECMWF/CDS.
    Auth Method: CDS API (requires CDSAPI_URL and CDSAPI_KEY).
    Rate Limits: Controlled by CDS queuing system; request size limits apply (e.g. max 120,000 items per request).
    Retry Behavior: Built into cdsapi client; script will wait and poll until QUEUED -> COMPLETED.
    """
    def __init__(self):
        super().__init__("era5", ["wind_u", "wind_v", "waves", "pressure"])

class IcebergDBFetcher(MockDatasetFetcher):
    """
    Circum-Antarctic Iceberg DB Fetcher (BYU/Scripps).
    Auth Method: Open HTTP Download of static files (e.g., BYU ASCAT iceberg database).
    Rate Limits: Standard web server limits.
    Retry Behavior: Simple retry on 404 (if update delayed) or network timeout.
    """
    def __init__(self):
        super().__init__("iceberg_db", ["position", "size", "time"])

class GEBCOFetcher(MockDatasetFetcher):
    """
    GEBCO Bathymetry Fetcher.
    Auth Method: Direct netCDF download via portal link.
    Rate Limits: Generally downloaded once and cached statically; no strict rate limit.
    Retry Behavior: Resume on partial download failure.
    """
    def __init__(self):
        super().__init__("gebco", ["depth"])
