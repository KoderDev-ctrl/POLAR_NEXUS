from datetime import datetime, timezone
from typing import Dict, Any

class StaleTimestampError(ValueError):
    pass

class InvalidCoordinateError(ValueError):
    pass

def validate_vessel_profile(payload: Dict[str, Any]) -> bool:
    """
    Validates a vessel profile schema (Item 19).
    """
    required_fields = ["voyage_priority", "turning_radius", "draft", "depth_clearance", "max_ice_concentration", "max_acceptable_risk"]
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    # Validate priority
    valid_priorities = {"time_critical", "safety_priority", "fuel_economy", "balanced"}
    if payload["voyage_priority"] not in valid_priorities:
        raise ValueError(f"Invalid voyage_priority. Must be one of {valid_priorities}")

    # Validate numeric types and ranges
    for field in ["turning_radius", "draft", "depth_clearance", "max_ice_concentration", "max_acceptable_risk"]:
        if not isinstance(payload[field], (int, float)):
            raise ValueError(f"Field {field} must be numeric")

    if payload["turning_radius"] < 0:
        raise ValueError("turning_radius must be >= 0")
    if payload["draft"] <= 0:
        raise ValueError("draft must be > 0")
    if payload["depth_clearance"] < 0:
        raise ValueError("depth_clearance must be >= 0")
    if not (0.0 <= payload["max_ice_concentration"] <= 1.0):
        raise ValueError("max_ice_concentration must be between 0 and 1")
    if payload["max_acceptable_risk"] < 0:
        raise ValueError("max_acceptable_risk must be >= 0")

    return True

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
