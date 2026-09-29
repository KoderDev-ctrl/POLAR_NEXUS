import os
from datetime import datetime
from typing import Tuple, Optional
import numpy as np
from .base import DatasetFetcher, RawDataset, CachedDataset

class CryoXDataError(Exception):
    """Structured exception for CryoX data ingestion errors."""
    pass

class BaseRealFetcher(DatasetFetcher):
    """
    Base class for fetchers that handles mode switching between REAL_DATA and LOCAL_FIXTURE.
    """
    def __init__(self, dataset_name: str, expected_vars: list, mode: str = "REAL_DATA"):
        super().__init__(dataset_name)
        self.expected_vars = expected_vars
        self.mode = mode
        
        if self.mode not in ["REAL_DATA", "LOCAL_FIXTURE"]:
            raise ValueError(f"Invalid mode: {self.mode}. Must be REAL_DATA or LOCAL_FIXTURE.")

    def fetch(self, time_range: Tuple[datetime, datetime], bbox: Tuple[float, float, float, float]) -> RawDataset:
        if time_range[0] > time_range[1]:
            raise ValueError("Start time cannot be after end time.")
            
        if bbox[0] >= bbox[2]:
            raise ValueError("Invalid bbox: minimum latitude must be less than maximum latitude.")
        if not (-90.0 <= bbox[0] <= 90.0) or not (-90.0 <= bbox[2] <= 90.0):
            raise ValueError("Invalid bbox: latitude values must be between -90 and 90.")
            
        if self.mode == "REAL_DATA":
            return self._fetch_real(time_range, bbox)
        elif self.mode == "LOCAL_FIXTURE":
            return self._fetch_fixture(time_range, bbox)
        
    def _fetch_real(self, time_range: Tuple[datetime, datetime], bbox: Tuple[float, float, float, float]) -> RawDataset:
        # We explicitly block real data fetching when credentials/network is absent.
        self.is_blocked_by_data_dependency = True
        raise CryoXDataError(f"BLOCKED: Real data unavailable for {self.dataset_name}. Credentials/network missing. Use LOCAL_FIXTURE mode for development.")

    def _fetch_fixture(self, time_range: Tuple[datetime, datetime], bbox: Tuple[float, float, float, float]) -> RawDataset:
        # Load from tests/fixtures
        # For functional verification, we return structural mock arrays.
        fixture_data = {}
        for var in self.expected_vars:
            fixture_data[var] = np.zeros((1, 10, 10)) # Deterministic structural stub
            
        return RawDataset(
            dataset_name=self.dataset_name,
            data=fixture_data,
            fetch_time=datetime.now(),
            metadata={"source": "LOCAL_FIXTURE", "bbox": bbox, "time_range": time_range}
        )

    def validate_response(self, raw: RawDataset) -> bool:
        if not raw.data:
            return False
        for var in self.expected_vars:
            if var not in raw.data:
                return False
        return True

    def cache(self, raw: RawDataset) -> CachedDataset:
        cache_path = f"/tmp/cache/{self.dataset_name}.nc"
        return CachedDataset(
            dataset_name=self.dataset_name,
            file_path=cache_path,
            cache_time=datetime.now()
        )

class NSIDCFetcher(BaseRealFetcher):
    """NSIDC Sea Ice CDR (G02202) Fetcher."""
    def __init__(self, mode: str = "REAL_DATA"):
        super().__init__("nsidc_sea_ice", ["sea_ice_concentration"], mode=mode)

class CopernicusMarineFetcher(BaseRealFetcher):
    """Copernicus Marine (CMEMS) Fetcher."""
    def __init__(self, mode: str = "REAL_DATA"):
        super().__init__("copernicus_marine", ["currents_u", "currents_v", "sst", "ssh", "sea_ice_conc", "sea_ice_thickness", "sea_ice_velocity"], mode=mode)

class ERA5Fetcher(BaseRealFetcher):
    """ERA5 Fetcher via ECMWF/CDS."""
    def __init__(self, mode: str = "REAL_DATA"):
        super().__init__("era5", ["wind_u", "wind_v", "waves", "pressure"], mode=mode)

class IcebergDBFetcher(BaseRealFetcher):
    """Circum-Antarctic Iceberg DB Fetcher."""
    def __init__(self, mode: str = "REAL_DATA"):
        super().__init__("iceberg_db", ["position", "size", "time"], mode=mode)

class GEBCOFetcher(BaseRealFetcher):
    """GEBCO Bathymetry Fetcher."""
    def __init__(self, mode: str = "REAL_DATA"):
        super().__init__("gebco", ["depth"], mode=mode)
