from typing import Dict, Any, List, Tuple
from polar_nexus.routex16.cost_layer import CandidateRoute

def candidate_to_dict(cand: CandidateRoute) -> Dict[str, Any]:
    # Canonical waypoint representation: (lat, lon, hours_since_departure)
    waypoints = [list(wp) for wp in cand.geometry]
    return {
        "candidate_id": cand.route_id,
        "engine": cand.engine_category,
        "algorithm": cand.algorithm_name,
        "waypoints": waypoints,
        "estimated_time": cand.estimated_time_hours,
        "estimated_fuel": cand.estimated_fuel_kg,
        "environmental_risk": cand.environmental_risk,
        "route_risk_score": cand.metadata.get("route_risk_score", 0.0),
        "total_route_risk": cand.environmental_risk + cand.metadata.get("route_risk_score", 0.0),
        "feasible": cand.feasibility_status == "FEASIBLE",
        "feasibility_status": cand.feasibility_status,
        "feasibility_violations": cand.metadata.get("feasibility_violations", []),
        "cpa": cand.metadata.get("cpa", None),
        "tcpa": cand.metadata.get("tcpa", None),
        "layers_missing": cand.metadata.get("layers_missing", []),
        "metadata": cand.metadata
    }

def dict_to_candidate(d: Dict[str, Any]) -> CandidateRoute:
    waypoints = [tuple(wp) for wp in d["waypoints"]]
    return CandidateRoute(
        route_id=d.get("candidate_id", ""),
        algorithm_name=d.get("algorithm", ""),
        engine_category=d.get("engine", ""),
        geometry=waypoints,
        distance_nm=d.get("metadata", {}).get("dist_nm", 0.0),
        estimated_time_hours=d.get("estimated_time", 0.0),
        estimated_fuel_kg=d.get("estimated_fuel", 0.0),
        environmental_risk=d.get("environmental_risk", 0.0),
        metadata=d.get("metadata", {}),
        feasibility_status=d.get("feasibility_status", "PENDING")
    )
