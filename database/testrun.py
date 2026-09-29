from .client import supabase
from .repository import insert, select

def start(label: str) -> str:
    res = supabase.table("pn_test_runs").insert({"label": label, "status": "running"}).execute()
    return res.data[0]["id"]

def finish(run_id: str, status: str):
    res = supabase.table("pn_test_runs").update({"status": status, "finished_at": "now()"}).eq("id", run_id).execute()
    return res.data

def purge(run_id: str):
    res = supabase.rpc("pn_purge_test_run", {"p_run": run_id}).execute()
    return res.data

def leftovers():
    res = supabase.rpc("pn_test_leftovers").execute()
    return res.data
