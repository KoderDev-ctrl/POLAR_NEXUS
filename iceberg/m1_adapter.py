from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timezone

@dataclass
class SICResult:
    available: bool
    status: str # 'AVAILABLE' | 'UNAVAILABLE' | 'DEGRADED' | 'INSUFFICIENT_DATA' | 'REPLAY_NOT_OPERATIONAL'
    source: Optional[str]
    base_time: Optional[datetime]
    valid_at: Optional[datetime]
    computed_at: Optional[datetime]
    coverage: Optional[Dict[str, Any]]
    reason: str
    replay_only: bool

class SeaIceAdapter:
    def __init__(self, artifact_path: Optional[str] = None):
        self.artifact_path = artifact_path
        
    def get_sic(self, base_time: datetime, valid_at: datetime, horizon_h: int) -> SICResult:
        if base_time.tzinfo is None or valid_at.tzinfo is None:
            raise ValueError("Naive timestamps rejected")
        
        expected_valid_at = base_time + __import__('datetime').timedelta(hours=horizon_h)
        if valid_at != expected_valid_at:
            raise ValueError("Mismatched temporal semantics: valid_at does not match horizon")
            
        if horizon_h < 0:
            raise ValueError("Invalid horizon")
            
        # Model 1 is absent in operational mode
        return SICResult(
            available=False,
            status="INSUFFICIENT_DATA",
            source=None,
            base_time=base_time,
            valid_at=valid_at,
            computed_at=datetime.now(timezone.utc),
            coverage=None,
            reason="SIC_UNAVAILABLE",
            replay_only=False
        )

class ReplaySICFixture(SeaIceAdapter):
    def get_sic(self, base_time: datetime, valid_at: datetime, horizon_h: int) -> SICResult:
        if base_time.tzinfo is None or valid_at.tzinfo is None:
            raise ValueError("Naive timestamps rejected")
            
        expected_valid_at = base_time + __import__('datetime').timedelta(hours=horizon_h)
        if valid_at != expected_valid_at:
            raise ValueError("Mismatched temporal semantics: valid_at does not match horizon")
            
        if horizon_h < 0:
            raise ValueError("Invalid horizon")
            
        return SICResult(
            available=True,
            status="REPLAY_NOT_OPERATIONAL",
            source="TEST_FIXTURE",
            base_time=base_time,
            valid_at=valid_at,
            computed_at=datetime.now(timezone.utc),
            coverage={
                "grid_crs": "EPSG:3031",
                "grid_extent": [-3000000, -3000000, 3000000, 3000000],
                "grid_resolution": 10000,
                "nodata_mask": -9999,
                "values": [] # Dummy empty fixture values
            },
            reason="TEST_FIXTURE",
            replay_only=True
        )

def assess_route_x16_policy(sic_result: SICResult) -> str:
    if sic_result.replay_only:
        return "REPLAY_NOT_OPERATIONAL"
    if not sic_result.available:
        return "INSUFFICIENT_DATA"
    return "OPERATIONAL_OK"
