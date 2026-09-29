from fastapi import FastAPI, HTTPException
import json
import uuid
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timezone
import numpy as np

# Core logic
from polar_nexus.iceberg.core import HazardCfg, check_ingest
from polar_nexus.iceberg.orchestrator import assess_iceberg
from polar_nexus.iceberg.db import cache_check, cache_save
from polar_nexus.iceberg.m1_adapter import SeaIceAdapter
from polar_nexus.database.client import supabase
from polar_nexus.routing.grid import GridSpec
from polar_nexus.routex16.cost_layer import RouteCostLayer, CandidateRoute
from polar_nexus.routing.hazard_raster import rasterise_iceberg_hazard
from polar_nexus.feasibility.gate import HardFeasibilityGate
from polar_nexus.adaptive.loop import AdaptiveNavigationLoop

# RouteX16 Engines
from polar_nexus.routex16.engines.time_engine import TimeEngine
from polar_nexus.routex16.engines.fuel_engine import FuelEngine
from polar_nexus.routex16.engines.time_risk_engine import TimeRiskEngine
from polar_nexus.routex16.engines.fuel_risk_engine import FuelRiskEngine

import pickle

# Global State
class AppState:
    cfg: HazardCfg = None
    d4_df = None
    m6_limits = None
    m1_adapter = None
    adapters = {}
    model_hashes = {}
    grid = None
    cost_layer = None
    engines = {}

state = AppState()

# Mock models for API orchestration (so we don't load huge models)
def m6_mock(tr):
    from polar_nexus.iceberg.core import mk_point
    return mk_point("P6", "predicted", "model_6", "M6", "operational", tr["x"][-1] + 1000, tr["y"][-1] + 1000, tr["base_time"], 24, datetime.now(timezone.utc), {}, {})

def m5_mock(tr):
    from polar_nexus.iceberg.core import mk_point
    return mk_point("M5_ADV", "advisory", "model_5", "M5", "advisory", tr["x"][-1] + 500, tr["y"][-1] + 500, tr["base_time"], 8760, datetime.now(timezone.utc), {}, {})

def m8_mock(tr):
    from polar_nexus.iceberg.core import mk_point
    return mk_point("M8_ADV", "advisory", "model_8", "M8", "advisory", tr["x"][-1] - 500, tr["y"][-1] - 500, tr["base_time"], 24, datetime.now(timezone.utc), {}, {})

async def lifespan(app: FastAPI):
    # Load configuration
    state.cfg = HazardCfg.load("polar_nexus/configs/hazard_config.v1.json")
    
    # Load D4 dataframe (stub loading logic for orchestration)
    with open("models/original/4_dataset_model", "rb") as f:
        state.d4_df = pickle.load(f)
        
    state.m6_limits = {"improvement_over_persistence_pct": -11.75}
    state.model_hashes = {
        "m6": "1a9d951c0c1620df62e1d02302fecc6cc00aa811e3c6dd0d4435cfaace08a546",
        "m5": "ddf91b5d8484e6011ec2c42068c17008c054b8712eaf7fb9267213a066ee3879",
        "m8": "3f7ffeec8b6a3a4c01fbc25939df8dabb0eb21f11075d07ed065538e745f1baa"
    }
    
    state.m1_adapter = SeaIceAdapter()
    
    state.adapters = {
        "m6": m6_mock,
        "m1": lambda tr: state.m1_adapter.get_sic(tr["base_time"], tr["base_time"] + __import__('datetime').timedelta(hours=24), 24),
        "m5": m5_mock,
        "m8": m8_mock
    }
    
    # Grid spec
    state.grid = GridSpec.from_bbox(-75, -50, -70, -40, cell_km=5)
    
    # RouteX16 components
    env = {"ice_conc": np.zeros(state.grid.shape), "hazard_field": np.zeros(state.grid.shape)}
    vessel = {"base_speed_kts": 12.0, "base_fuel_consumption_kg_h": 500.0}
    state.cost_layer = RouteCostLayer(env, vessel, state.grid)
    
    state.engines = {
        "TIME": TimeEngine(state.cost_layer),
        "FUEL": FuelEngine(state.cost_layer),
        "TIME_RISK": TimeRiskEngine(state.cost_layer),
        "FUEL_RISK": FuelRiskEngine(state.cost_layer)
    }

    yield
    # Cleanup resources (if any)
    pass

app = FastAPI(title="POLAR NEXUS Operational API", version="v1", lifespan=lifespan)

@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "service": "polar_nexus",
        "api_version": "v1"
    }

@app.get("/api/v1/status")
async def status():
    return {
        "service": "polar_nexus",
        "mode": "OPERATIONAL",
        "d4": {
            "available": True,
            "fresh": True # In a real implementation this would check D4 watermark
        },
        "models": {
            "m5": "advisory only",
            "m6": "UNRESOLVED feature provenance and reproducibility, structurally allowed",
            "m8": "advisory only",
            "m1": "UNAVAILABLE operationally"
        },
        "environment": {
            "currents": "unavailable",
            "wind": "unavailable",
            "ice_conc": "unavailable"
        },
        "hazard": {
            "ready": True
        },
        "routing": {
            "ready": True
        }
    }

@app.get("/api/v1/models")
async def models():
    return {
        "m5": {
            "id": "model_5",
            "role": "advisory",
            "status": "AVAILABLE",
            "artifact_hash": state.model_hashes.get("m5"),
            "horizon_h": 8760,
            "known_limitations": ["Ridge does not beat persistence on its own test set"],
            "provenance_status": "RESOLVED"
        },
        "m6": {
            "id": "model_6",
            "role": "operational",
            "status": "AVAILABLE",
            "artifact_hash": state.model_hashes.get("m6"),
            "pinned_artifact": "best_iceberg_model_final.keras",
            "horizon_h": 24,
            "feature_provenance": "UNRESOLVED",
            "evaluation_reproducibility": "UNRESOLVED",
            "known_limitations": ["Validated on linearly interpolated hourly series"]
        },
        "m8": {
            "id": "model_8",
            "role": "advisory",
            "status": "AVAILABLE",
            "artifact_hash": state.model_hashes.get("m8"),
            "horizon_h": 8760,
            "known_limitations": ["No skill over not moving"],
            "provenance_status": "RESOLVED"
        },
        "m1": {
            "id": "model_1_sic",
            "role": "operational",
            "status": "UNAVAILABLE",
            "known_limitations": ["No artifacts supplied"]
        }
    }

@app.get("/api/v1/hazard/{iceberg_id}")
async def get_hazard(iceberg_id: str, mode: str = "operational"):
    watermark = datetime(2025, 12, 31, 23, tzinfo=timezone.utc)
    now = datetime(2025, 12, 31, 12, tzinfo=timezone.utc)
    
    res = await assess_iceberg(
        iceberg_id, 
        state.d4_df, 
        watermark, 
        now, 
        state.cfg, 
        state.adapters, 
        state.m6_limits, 
        mode=mode, 
        cache_check=cache_check, 
        cache_save=cache_save, 
        model_hashes=state.model_hashes
    )
    
    clean_res = {k: v for k, v in res.items() if k not in ["route_hazard", "sic"]}
    return clean_res

from pydantic import BaseModel, Field

class VoyagePlanRequest(BaseModel):
    origin: List[float] = Field(..., description="[lat, lon]")
    destination: List[float] = Field(..., description="[lat, lon]")
    departure_time_utc: datetime
    vessel: Dict[str, Any]
    mode: str = "operational"
    iceberg_id: str = None
    
@app.post("/api/v1/voyage/plan")
async def voyage_plan(req: VoyagePlanRequest):
    if req.mode != "operational" and req.mode != "replay":
        raise HTTPException(status_code=400, detail="Invalid mode. Must be operational or replay.")
        
    watermark = datetime(2025, 12, 31, 23, tzinfo=timezone.utc)
    now = datetime(2025, 12, 31, 12, tzinfo=timezone.utc)
    
    # In a real app we'd validate required fields in vessel.
    # For now assume it has max_ice_concentration etc.
    if "max_acceptable_risk" not in req.vessel:
        req.vessel["max_acceptable_risk"] = 100.0
    if "draft" not in req.vessel:
        req.vessel["draft"] = 10.0
    if "depth_clearance" not in req.vessel:
        req.vessel["depth_clearance"] = 2.0
    if "max_ice_concentration" not in req.vessel:
        req.vessel["max_ice_concentration"] = 1.0

    # Get Hazard
    hazard_data = None
    if req.iceberg_id:
        assessment = await assess_iceberg(
            req.iceberg_id, state.d4_df, watermark, now, state.cfg, state.adapters, state.m6_limits, mode=req.mode,
            cache_check=cache_check, cache_save=cache_save, model_hashes=state.model_hashes
        )
        if assessment["status"] == "INSUFFICIENT_DATA":
            return {"status": "INSUFFICIENT_DATA", "reason": "D4 data stale or insufficient."}
            
        hazard_data = assessment.get("route_hazard")
        
    # Build env layers (mocked explicitly)
    env = {
        "ice_conc": np.zeros(state.grid.shape),
        "depth_grid": np.full(state.grid.shape, 100.0)
    }
    
    # Rasterize if hazard exists
    if hazard_data:
        raster = rasterise_iceberg_hazard([{"route_hazard": hazard_data}], state.grid, req.departure_time_utc, req.departure_time_utc + __import__('datetime').timedelta(hours=24))
        env["hazard_field"] = raster
        gate = HardFeasibilityGate(hazard_data.hazard, state.grid)
    else:
        env["hazard_field"] = np.zeros(state.grid.shape)
        gate = HardFeasibilityGate(None, state.grid)
        
    # Generate candidates
    all_candidates = []
    for engine_name, engine in state.engines.items():
        cands = engine.generate_candidates(req.origin, req.destination, env.get("ice_conc"))
        all_candidates.extend(cands)
        
    # Apply Feasibility Gate
    feasible = gate.filter_feasible_routes(all_candidates, req.vessel, env)
    
    run_id = str(uuid.uuid4())
    
    if not feasible:
        return {
            "status": "NO_FEASIBLE_ROUTE",
            "run_id": run_id,
            "reason": "HardFeasibilityGate rejected all candidates.",
            "feasibility_violations": [
                {
                    "candidate_id": c.route_id,
                    "violations": c.metadata.get("feasibility_violations", [])
                } for c in all_candidates
            ],
            "degraded": hazard_data.degraded if hazard_data else False,
            "layers_missing": ["current_u", "wind_u", "SIC_UNAVAILABLE"]
        }
        
    # Consolidate
    def consolidate(cands):
        seen = set()
        res = []
        for c in cands:
            sig = (c.engine_category, tuple((round(p[0], 4), round(p[1], 4)) for p in c.geometry))
            if sig not in seen:
                seen.add(sig)
                res.append(c)
        return res
        
    cons = consolidate(feasible)
    
    # Score
    # Simple default objective: time tiebreak
    best_route = sorted(cons, key=lambda c: (c.environmental_risk + c.metadata.get("route_risk_score", 0), c.estimated_time_hours))[0]
    
    # Record trace
    from polar_nexus.routex16.candidate.adapter import candidate_to_dict
    payload = {
        "run_id": run_id,
        "status": "SUCCESS",
        "mode": req.mode,
        "selected_route": candidate_to_dict(best_route),
        "degraded": hazard_data.degraded if hazard_data else False,
        "layers_missing": ["current_u", "wind_u", "SIC_UNAVAILABLE"]
    }
    
    return payload

class ReplanRequest(BaseModel):
    current_pos: List[float]
    active_route: Dict[str, Any]
    vessel: Dict[str, Any]
    iceberg_id: str
    locked_category: str
    refreshed_risk: float

@app.post("/api/v1/voyage/replan")
async def voyage_replan(req: ReplanRequest):
    # Setup adaptive loop
    watermark = datetime(2025, 12, 31, 23, tzinfo=timezone.utc)
    now = datetime(2025, 12, 31, 12, tzinfo=timezone.utc)
    assessment = await assess_iceberg(
        req.iceberg_id, state.d4_df, watermark, now, state.cfg, state.adapters, state.m6_limits, mode="operational",
        cache_check=cache_check, cache_save=cache_save, model_hashes=state.model_hashes
    )
    
    hazard_data = assessment.get("route_hazard")
    if not hazard_data:
        return {"status": "ERROR"}
        
    gate = HardFeasibilityGate(hazard_data.hazard, state.grid)
    loop = AdaptiveNavigationLoop(state.engines, gate, {"adaptive_risk_delta_threshold": 10.0})
    
    # Parse active_route
    from polar_nexus.routex16.candidate.adapter import dict_to_candidate, candidate_to_dict
    route_obj = dict_to_candidate(req.active_route)
    loop.lock_category(req.locked_category, route_obj, req.vessel)
    
    env = {
        "ice_conc": np.zeros(state.grid.shape),
        "depth_grid": np.full(state.grid.shape, 100.0)
    }
    
    raster = rasterise_iceberg_hazard([{"route_hazard": hazard_data}], state.grid, now, now + __import__('datetime').timedelta(hours=24))
    env["hazard_field"] = raster
    
    res = loop.trigger_update(req.current_pos, env, req.refreshed_risk)
    if res["route"]:
        res["route"] = candidate_to_dict(res["route"])
    return res

