from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RawDataset:
    """Represents raw data fetched from a source."""
    dataset_name: str
    data: Any  # Could be xarray.Dataset, dict, etc.
    fetch_time: datetime
    metadata: Dict[str, Any]

@dataclass
class CachedDataset:
    """Represents a dataset that has been cached locally."""
    dataset_name: str
    file_path: str
    cache_time: datetime

class DatasetFetcher(ABC):
    """
    Base interface for all dataset fetchers.
    Each fetcher must document its auth method, rate limits, and failure/retry behavior.
    """
    
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.is_blocked_by_data_dependency = False # Set to True if live API cannot be accessed

    @abstractmethod
    def fetch(self, time_range: Tuple[datetime, datetime], bbox: Tuple[float, float, float, float]) -> RawDataset:
        """
        Fetches data for the given time range and bounding box (min_lat, min_lon, max_lat, max_lon).
        """
        pass

    @abstractmethod
    def validate_response(self, raw: RawDataset) -> bool:
        """
        Validates the raw response data (e.g. checks dimensions, missing data thresholds).
        """
        pass

    @abstractmethod
    def cache(self, raw: RawDataset) -> CachedDataset:
        """
        Saves the raw dataset to the local cache and returns a CachedDataset reference.
        """
        pass
