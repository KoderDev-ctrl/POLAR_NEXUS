from abc import ABC, abstractmethod
import pandas as pd
from datetime import timezone

class NotConfigured(Exception):
    pass

class IcebergFixSource(ABC):
    @abstractmethod
    def fetch_track(self, iceberg_id: str) -> pd.DataFrame:
        pass

class ReplayParquetSource(IcebergFixSource):
    def __init__(self, parquet_path: str = "data/derived/d4.parquet"):
        self.parquet_path = parquet_path
    
    def fetch_track(self, iceberg_id: str) -> pd.DataFrame:
        df = pd.read_parquet(self.parquet_path)
        # Note: this reads the parquet, explicitly labelled replay/reference data
        return df[df.iceberg_id == iceberg_id].copy()

class LiveSource(IcebergFixSource):
    def fetch_track(self, iceberg_id: str) -> pd.DataFrame:
        raise NotConfigured("live D4 source not provided")

def load_track(iceberg_id: str) -> pd.DataFrame:
    """
    Reads the operational/replay track from Supabase.
    """
    from polar_nexus.database.client import supabase
    
    all_data = []
    limit = 1000
    offset = 0
    while True:
        res = supabase.table("pn_iceberg_fixes").select("*").eq("iceberg_id", iceberg_id).order("observed_at").range(offset, offset + limit - 1).execute()
        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < limit:
            break
        offset += limit
    
    if not all_data:
        # Return empty DataFrame with correct columns if none found
        return pd.DataFrame(columns=['iceberg_id', 'datetime_utc', 'latitude', 'longitude', 'source_quality', 'source'])
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    # Rename columns to match core expectations
    df = df.rename(columns={'observed_at': 'datetime_utc'})
    # Ensure datetime is parsed correctly
    df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])
    # Convert naive to UTC if necessary, though Supabase returns strings that parse to timezone aware
    if df['datetime_utc'].dt.tz is None:
        df['datetime_utc'] = df['datetime_utc'].dt.tz_localize('UTC')
    
    return df

def get_watermark(source_name: str) -> pd.Timestamp:
    """Gets the latest watermark from Supabase."""
    from polar_nexus.database.client import supabase
    res = supabase.table("pn_ingest_watermark").select("*").eq("source", source_name).execute()
    if not res.data:
        return None
    return pd.to_datetime(res.data[0]['watermark'])
