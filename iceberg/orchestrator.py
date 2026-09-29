"""14. Parallelise ONLY independent stages. Stage 0 (gates) -> Stage 1 (parallel) -> Stage 2 (hazard) -> route."""
import asyncio, time
from datetime import datetime, timezone
from polar_nexus.iceberg.core import *

import concurrent.futures
_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
# Warm up the thread pool
list(_thread_pool.map(lambda x: x, range(4)))
_semaphores = {}
def _get_sem():
    loop = asyncio.get_running_loop()
    if loop not in _semaphores:
        _semaphores[loop] = asyncio.Semaphore(4)
    return _semaphores[loop]

async def _timed(name, fn, timeout_s, timings):
    t = time.perf_counter()
    try: 
        async with _get_sem():
            loop = asyncio.get_running_loop()
            return await asyncio.wait_for(loop.run_in_executor(_thread_pool, fn), timeout_s)
    finally: timings[name] = round((time.perf_counter() - t) * 1000, 1)

async def assess_iceberg(iceberg_id, d4_df, watermark, now, cfg, adapters, m6_limits, mode=None, timeout_s=10.0, cache_check=None, cache_save=None, model_hashes=None):
    """adapters: dict of zero-arg-callable factories taking (track) -> callable returning Point/dict, or None to skip.
       keys: m6(track)->P6 Point, m1(track)->dict, m5(track)->Point|None, m8(track)->Point|None"""
    mode = mode or cfg.mode_default; timings = {}; t0 = time.perf_counter()
    # ---- Stage 0: sequential, mandatory, no models ----
    try:
        lag = check_ingest(watermark, now, cfg, mode)
        tr = d4_clean_track(d4_df, iceberg_id, now, cfg)
    except InsufficientData as e:
        return dict(status=INSUFFICIENT, reason=str(e), iceberg_id=iceberg_id, **cfg.stamp())
    base = tr["base_time"]; vx, vy = kinematic_velocity(tr["t_h"], tr["x"], tr["y"])
    p4 = mk_point("P4", "observed", "dataset_4", "D4", "operational", tr["x"][-1], tr["y"][-1], base, 0.0, now,
                  {"age_h": tr["age_h"], "n_fixes_used": tr["n_clean"], "n_fixes_dropped": tr["n_raw"] - tr["n_clean"], "q_dist": tr.get("q_dist", {})})
    pk = mk_point("P_kin24", "derived", "persistence_baseline", "kin-v1", "baseline", tr["x"][-1] + vx * cfg.horizon_h, tr["y"][-1] + vy * cfg.horizon_h,
                  base, cfg.horizon_h, now, {"speed_km_day": math.hypot(vx, vy) * 24 / 1000}, kin_baseline_limitation(cfg))
    
    if cache_check:
        cached = await cache_check(iceberg_id, base, cfg.sha256, mode)
        if cached:
            cached["timings_ms"] = {"cache_hit": True}
            cached["wall_ms"] = round((time.perf_counter() - t0) * 1000, 1)
            return cached

    # ---- Stage 1: independent -> concurrent (each needs only the D4 track) ----
    names = [k for k in ("m6", "m1", "m5", "m8", "m4") if adapters.get(k)]
    res = await asyncio.gather(*[_timed(k, (lambda k=k: adapters[k](tr)), timeout_s, timings) for k in names], return_exceptions=True)
    out = dict(zip(names, res)); missing = [k for k, v in out.items() if isinstance(v, Exception) or v is None]
    p6 = out.get("m6") if not isinstance(out.get("m6"), Exception) else None
    p_m4 = out.get("m4") if not isinstance(out.get("m4"), Exception) else None
    adv = [v for k, v in out.items() if k in ("m5", "m8", "m4") and not isinstance(v, Exception) and v is not None and getattr(v, "status", None) == "OK" and hasattr(v, "kind") and v.kind == "advisory"]
    
    # If M4 output is a raw dict (like from adapter directly), handle it
    m4_metrics = {"m4_forecast_available": False}
    if p_m4 and isinstance(p_m4, dict) and p_m4.get("status") == "OK":
        m4_metrics = {
            "m4_forecast_available": True,
            "m4_valid_at": p_m4.get("valid_at"),
            "m4_displacement_north_km": p_m4.get("north_km"),
            "m4_displacement_east_km": p_m4.get("east_km")
        }
        if p6:
            m4_metrics["m4_vs_m6_km"] = math.hypot(p_m4.get("x_m", 0) - p6.x_m, p_m4.get("y_m", 0) - p6.y_m) / 1000.0
            m4_metrics["m6_vs_persistence_km"] = math.hypot(p6.x_m - pk.x_m, p6.y_m - pk.y_m) / 1000.0
        m4_metrics["m4_vs_persistence_km"] = math.hypot(p_m4.get("x_m", 0) - pk.x_m, p_m4.get("y_m", 0) - pk.y_m) / 1000.0
        
    # ---- Stage 2: dependent (needs P4 + kin + P6) ----
    rh = build_route_hazard([p4, pk] + ([p6] if p6 else []), cfg)
    missing_layers = missing[:]
    if out.get("m1") and getattr(out["m1"], "status", None) in ("INSUFFICIENT_DATA", "UNAVAILABLE"):
        missing_layers.append("SIC_UNAVAILABLE")
        
    status = REPLAY if mode == "replay" else (DEGRADED if (missing or rh.degraded) else OK)
    result = dict(status=status, mode=mode, iceberg_id=iceberg_id, missing=missing_layers, ingest_lag_h=lag, **cfg.stamp(),
                points=[p.to_dict() for p in rh.hazard.points], advisories=[p.to_dict() if hasattr(p, "to_dict") else p for p in adv],
                envelope=rh.hazard.envelope(), route_hazard=rh, sic=out.get("m1") if "m1" not in missing else None,
                m4_metrics=m4_metrics,
                model_limitations={"model_6": m6_limits}, model_hashes=model_hashes or {}, timings_ms=timings, wall_ms=round((time.perf_counter() - t0) * 1000, 1),
                cache_key=(iceberg_id, base.isoformat(), cfg.sha256, mode))
                
    if cache_save:
        await cache_save(result)
        
    return result
