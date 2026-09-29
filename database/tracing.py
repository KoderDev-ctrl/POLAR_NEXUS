from .repository import insert

def trace(request_id: str, hop: str, ok: bool, latency_ms: float, detail: dict = None, test_run_id: str = None):
    data = {
        "request_id": request_id,
        "hop": hop,
        "ok": ok,
        "latency_ms": latency_ms,
        "detail": detail or {}
    }
    if test_run_id:
        data["test_run_id"] = test_run_id
        
    return insert("pn_pipeline_trace", data, returning=True)
