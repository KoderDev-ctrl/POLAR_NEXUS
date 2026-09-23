from datetime import datetime, timezone
from typing import Dict, Any

class StaleTimestampError(ValueError):
    pass

class InvalidCoordinateError(ValueError):
    pass

def validate_position_update(payload: Dict[str, Any]) -> bool:
    """
    Validates a raw position update payload.
    - Rejects missing/invalid coordinates
    - Rejects stale timestamps
    """
    # Check for required fields
    if "lat" not in payload or "lon" not in payload or "timestamp" not in payload:
        raise ValueError("Missing required fields (lat, lon, timestamp)")
        
    lat = payload["lat"]
    lon = payload["lon"]
    
    # Validate coordinate ranges
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise InvalidCoordinateError("Coordinates must be numeric")
        
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        raise InvalidCoordinateError("Coordinates out of valid global bounds")
        
    # Validate timestamp
    timestamp = payload["timestamp"]
    if not isinstance(timestamp, datetime):
        try:
            # simple parse for stub
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            raise ValueError("Timestamp must be a valid ISO format string or datetime object")
            
    # Ensure it's not stale (e.g. older than 24 hours for this stub validation)
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        # Assuming UTC if naive
        timestamp = timestamp.replace(tzinfo=timezone.utc)
        
    if (now - timestamp).total_seconds() > 86400: # 24 hours
        raise StaleTimestampError("Position update is too stale (older than 24h)")
        
    # Future timestamp check
    if timestamp > now:
        raise ValueError("Timestamp cannot be in the future")
        
    return True

# API Stub - framework agnostic for now
class VesselsAPI:
    def __init__(self):
        # Local stub/mock store only, no real persistence
        self._local_store = {}
        
    def post_vessel_position(self, vessel_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /vessels/{vessel_id}/position stub
        """
        validate_position_update(payload)
        
        # In a real app this would store to DB and trigger SSE broadcast
        self._local_store[vessel_id] = payload
        
        # Hookup to RouteX16 adaptive-planner (Stub method signature only)
        # self._trigger_adaptive_replanning(vessel_id, payload)
        
        return {"status": "success", "stored": True}
        
    def _trigger_adaptive_replanning(self, vessel_id: str, latest_position: Dict[str, Any]):
        """
        Stub signature showing where latest_position feeds into §29 Adaptive Navigation.
        IMPLEMENTATION BLOCKED - Adaptive Navigation handles the actual replanning trigger logic.
        TODO: Wire to item 18 (adaptive loop)
        """
        pass
