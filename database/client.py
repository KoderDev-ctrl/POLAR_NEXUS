import os
from supabase import create_client, Client, ClientOptions
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")

opts = ClientOptions(postgrest_client_timeout=15)
supabase: Client = create_client(url, key, options=opts)
