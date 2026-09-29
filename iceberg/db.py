import asyncio
from datetime import datetime
from polar_nexus.database.client import supabase

async def cache_check(iceberg_id: str, base_time: datetime, cfg_sha256: str, mode: str):
    # Assessment identity/cache key: (iceberg_id, base_time, cfg_sha256, mode)
    # Supabase uses async or sync? The python client is mostly sync, but we can wrap it if needed.
    # Actually, postgrest is sync by default in supabase-py, so we run it in a thread.
    loop = asyncio.get_running_loop()
    
    def fetch():
        res = supabase.table("pn_iceberg_assessments").select("*").eq("iceberg_id", iceberg_id).eq("base_time", base_time.isoformat()).eq("cfg_sha256", cfg_sha256).eq("mode", mode).execute()
        if not res.data:
            return None
            
        ass = res.data[0]
        pts_res = supabase.table("pn_hazard_points").select("*").eq("assessment_id", ass["id"]).execute()
        
        # reconstruct the result dictionary
        result = dict(
            status=ass["status"],
            mode=ass["mode"],
            iceberg_id=ass["iceberg_id"],
            missing=[], # will reconstruct if needed or omitted for brevity since status determines it
            version="cached",
            sha256=ass["cfg_sha256"],
            points=[p for p in pts_res.data if p["role_in_hazard"] != "advisory"],
            advisories=[p for p in pts_res.data if p["role_in_hazard"] == "advisory"],
            envelope=ass.get("envelope"),
            model_limitations=ass.get("m6_limitations", {}),
            model_hashes=ass.get("model_hashes", {}),
            timings_ms=ass.get("timings_ms", {}),
            route_hazard=None,
            sic=None,
            cache_key=(iceberg_id, base_time.isoformat(), cfg_sha256, mode)
        )
        return result
        
    return await loop.run_in_executor(None, fetch)

async def cache_save(result: dict):
    loop = asyncio.get_running_loop()
    
    def save():
        # Persist the assessment
        ass_data = {
            "iceberg_id": result["iceberg_id"],
            "base_time": result["cache_key"][1],
            "cfg_sha256": result["cache_key"][2],
            "mode": result["cache_key"][3],
            "status": result["status"],
            "reason": "Missing: " + ", ".join(result.get("missing", [])) if result.get("missing") else None,
            "metrics": result["route_hazard"].hazard.metrics() if result.get("route_hazard") and result["route_hazard"].hazard else {},
            "envelope": result.get("envelope"),
            "m6_limitations": result.get("model_limitations", {}).get("model_6", {}),
            "model_hashes": result.get("model_hashes", {}),
            "timings_ms": result.get("timings_ms", {})
        }
        
        res = supabase.table("pn_iceberg_assessments").upsert(ass_data, on_conflict="iceberg_id,base_time,cfg_sha256,mode").execute()
        ass_id = res.data[0]["id"]
        
        points = result.get("points", []) + result.get("advisories", [])
        pts_data = []
        for p in points:
            pts_data.append({
                "assessment_id": ass_id,
                "role": p["role"],
                "kind": p["kind"],
                "source": p["source"],
                "artifact_version": p.get("artifact_version"),
                "role_in_hazard": p["role_in_hazard"],
                "base_time": p["base_time"],
                "valid_at": p["valid_at"],
                "computed_at": p["computed_at"],
                "horizon_h": p["horizon_h"],
                "x_m": p["x_m"],
                "y_m": p["y_m"],
                "lat": p["lat"],
                "lon": p["lon"],
                "quality": p.get("quality"),
                "limitations": p.get("limitations")
            })
            
        if pts_data:
            supabase.table("pn_hazard_points").delete().eq("assessment_id", ass_id).execute()
            supabase.table("pn_hazard_points").insert(pts_data).execute()
            
    await loop.run_in_executor(None, save)
