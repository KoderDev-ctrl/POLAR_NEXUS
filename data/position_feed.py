from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PositionUpdate:
    vessel_id: str
    lat: float
    lon: float
    timestamp: datetime
    speed_knots: Optional[float] = None
    heading_degrees: Optional[float] = None
    source: str = "unknown"
    quality: str = "unknown"

class PositionFeed(ABC):
    """
    Interface for live ship position feeds (e.g. onboard GPS, AIS).
    IMPLEMENTATION BLOCKED / DATA DEPENDENCY - Real providers not connected yet.
    """
    
    @abstractmethod
    def fetch_latest(self, vessel_id: str) -> PositionUpdate:
        """Fetch the most recent position for a vessel."""
        pass
        
    @abstractmethod
    def stream_updates(self, vessel_id: str):
        """
        WebSocket/SSE broadcast layer stub. 
        IMPLEMENTATION BLOCKED - external integration owned separately.
        """
        raise NotImplementedError("blocked - external integration owned separately")


class SimulatedPositionFeed(PositionFeed):
    """
    Simulated position feed that replays timed points for prototype/demo use.
    Produces simulated data only.
    """
    def __init__(self, predefined_route: List[PositionUpdate]):
        self.predefined_route = predefined_route
        self.current_index = 0
        
    def fetch_latest(self, vessel_id: str) -> PositionUpdate:
        if not self.predefined_route:
            raise ValueError(f"No simulated route configured for vessel {vessel_id}")
            
        update = self.predefined_route[self.current_index]
        self.current_index = min(self.current_index + 1, len(self.predefined_route) - 1)
        
        # Explicitly label as simulated data
        update.source = "simulated"
        return update
        
    def stream_updates(self, vessel_id: str):
        raise NotImplementedError("blocked - external integration owned separately")
