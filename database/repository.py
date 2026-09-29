from .client import supabase

def upsert(table_name: str, data: dict | list[dict], returning: bool = False):
    res = supabase.table(table_name).upsert(data).execute()
    return res.data if returning else None

def insert(table_name: str, data: dict | list[dict], returning: bool = False):
    res = supabase.table(table_name).insert(data).execute()
    return res.data if returning else None

def select(table_name: str, match: dict):
    res = supabase.table(table_name).select("*").match(match).execute()
    return res.data

def delete(table_name: str, match: dict):
    res = supabase.table(table_name).delete().match(match).execute()
    return res.data
