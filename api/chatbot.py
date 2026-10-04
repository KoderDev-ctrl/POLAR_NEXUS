from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import datetime

router = APIRouter()

# In-memory session store
SESSIONS = {}

class ChatbotSessionRequest(BaseModel):
    voyage_plan_id: Optional[str] = None
    navigation_session_id: Optional[str] = None

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ContextData(BaseModel):
    vessel_position: Optional[Dict[str, float]] = None
    vessel_speed: Optional[float] = None
    selected_route: Optional[Dict[str, Any]] = None
    candidate_routes: Optional[List[Dict[str, Any]]] = None
    iceberg_id: Optional[str] = None
    hazard: Optional[Dict[str, Any]] = None
    navigation_status: Optional[str] = "Underway"

class ChatbotMessageRequest(BaseModel):
    message: str
    context: Optional[ContextData] = None

@router.post("/api/v1/chatbot/sessions")
async def create_session(req: ChatbotSessionRequest):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "voyage_plan_id": req.voyage_plan_id,
        "navigation_session_id": req.navigation_session_id,
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "messages": [
            {"role": "assistant", "content": "Captain Voyage Assistant initialized. DEMO ASSISTANT mode active. How can I assist you with the current voyage?", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        ]
    }
    return {"session_id": session_id, "started_at": SESSIONS[session_id]["started_at"]}

@router.get("/api/v1/chatbot/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"messages": SESSIONS[session_id]["messages"]}

def generate_demo_response(msg: str, context: ContextData) -> str:
    msg_lower = msg.lower()
    
    if "why" in msg_lower and "selected" in msg_lower:
        if context and context.selected_route:
            return "The selected route currently has the lowest available risk among the feasible alternatives, balancing time, fuel consumption, and safe distance from hazards."
        return "The recommended route balances risk, distance, and environmental conditions to provide the safest feasible passage."
        
    if "risk" in msg_lower:
        if context and context.selected_route and "environmental_risk" in context.selected_route:
            return f"The current displayed route risk is approximately {round(context.selected_route['environmental_risk'], 1)}%."
        return "The current displayed route risk is 28%."
        
    if "alternative" in msg_lower or "compare" in msg_lower or "four routes" in msg_lower:
        if context and context.candidate_routes:
            return f"We have {len(context.candidate_routes)} candidate routes. Each varies by distance and exposure to the predicted hazard region. Infeasible routes are rejected due to intersecting the exclusion zone."
        return "There are four evaluated routes. The selected route is optimal, while others may be shorter but carry higher risk or violate feasibility constraints."
        
    if "rejected" in msg_lower or "not feasible" in msg_lower:
        return "Route 3 is currently not feasible because the route violates the available feasibility constraint by passing too close to the predicted iceberg trajectory."
        
    if "status" in msg_lower and "navigation" in msg_lower:
        if context and context.navigation_status:
            return f"The current navigation status is: {context.navigation_status}."
        return "The vessel is currently operating normally according to the active route plan."
        
    if "reassessed" in msg_lower or "happen" in msg_lower:
        return "The route is being reassessed because the vessel position and environmental conditions have changed. The adaptive loop re-evaluates risk continually."
        
    if "iceberg" in msg_lower or "where is the iceberg" in msg_lower:
        if context and context.iceberg_id:
            return f"Iceberg {context.iceberg_id} is being tracked. Its predicted trajectory moves it along the local currents. An exclusion zone is enforced around it."
        return "The nearest iceberg is currently being tracked and a dynamic exclusion zone is applied."
        
    if "where are we" in msg_lower or "vessel position" in msg_lower:
        if context and context.vessel_position:
            lat = round(context.vessel_position.get("lat", 0), 4)
            lon = round(context.vessel_position.get("lon", 0), 4)
            return f"The vessel is currently at Latitude {lat}, Longitude {lon}."
        return "The vessel position is tracked in the navigation display."

    return "I am the Captain Voyage Assistant (DEMO). I am here to help you understand route selections, risk, and navigation status. (This is a deterministic fallback response)."

@router.post("/api/v1/chatbot/sessions/{session_id}/messages")
async def send_message(session_id: str, req: ChatbotMessageRequest):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Append user message
    user_msg = {
        "role": "user",
        "content": req.message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    SESSIONS[session_id]["messages"].append(user_msg)
    
    # Generate response
    response_text = generate_demo_response(req.message, req.context)
    
    # Append assistant message
    asst_msg = {
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "is_demo": True
    }
    SESSIONS[session_id]["messages"].append(asst_msg)
    
    return asst_msg
