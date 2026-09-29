import argparse
import json
import math
import sys
import os
import pandas as pd
from datetime import datetime, timezone

from polar_nexus.iceberg.core import to_xy, mk_point, build_route_hazard, HazardCfg
from polar_nexus.models.model4_refined_adapter import RefinedModel4Adapter

def run_mode_a(lat, lon, obs_time, dest_lat, dest_lon):
    # This is a mock to show the dry-run logic
    # P4 is constructed from the input lat/lon
    now = datetime.now(timezone.utc)
    x, y = to_xy(lat, lon)
    
    # Mocking P4 and P_kin24 based on a zero-velocity assumption if no other data
    p4 = mk_point("P4", "observed", "dataset_4", "D4", "operational", x, y, obs_time, 0.0, now)
    p_kin24 = mk_point("P_kin24", "derived", "persistence_baseline", "kin-v1", "baseline", x, y, obs_time, 24.0, now)
    
    # M6 would normally be called, let's mock its failure or absence for coordinate-only dry run
    p6 = None 
    
    cfg = HazardCfg.load(os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'hazard_config.v1.json'))
    
    rh = build_route_hazard([p4, p_kin24], cfg)
    
    print("============================================================")
    print("POLAR NEXUS DRY RUN")
    print("============================================================")
    print("CASE: A")
    print("MODE: OPERATIONAL")
    print("STATUS: INSUFFICIENT_DATA (No live M6, M4, or route calculation mock implemented fully)")
    print("")
    print("INPUT:")
    print(f"lat: {lat}")
    print(f"lon: {lon}")
    print(f"observation_time: {obs_time.isoformat()}")
    print(f"destination_lat: {dest_lat}")
    print(f"destination_lon: {dest_lon}")
    print("")
    print("MODEL 4:")
    print("status: INSUFFICIENT_DATA")
    print("reason: M4_INPUT_SEQUENCE_UNAVAILABLE")
    print("")
    print("PERSISTENCE:")
    print("status: OK")
    print(f"P_kin24: lat={p_kin24.lat:.6f}, lon={p_kin24.lon:.6f}")
    print("")
    print("MODEL 6:")
    print("status: DEGRADED")
    print("P6: unavailable")
    print("")
    print("HAZARD:")
    m = rh.hazard.metrics()
    print(f"triangle_available: {m['triangle_available']}")
    print(f"radius_km_at_0h: {rh.hazard.radius_km(0):.3f}")
    print(f"radius_km_at_24h: {rh.hazard.radius_km(24):.3f}")
    
def run_mode_b(sequence_path):
    print("============================================================")
    print("POLAR NEXUS DRY RUN - MODEL 4 REPLAY")
    print("============================================================")
    
    # Load sequence (assuming CSV with 30 rows)
    import numpy as np
    
    try:
        df = pd.read_csv(sequence_path)
        # We need 24 features for 30 days
        adapter = RefinedModel4Adapter(os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'model4_updated'))
        features = adapter.metadata['features']
        
        if len(df) != 30:
            print(f"ERROR: Expected 30 rows, got {len(df)}")
            return
            
        seq = df[features].to_numpy(dtype=np.float32).reshape(1, 30, 24)
        
        # Determine base_time and current lat/lon from the last row
        base_time = pd.to_datetime(df['time'].iloc[-1]).to_pydatetime()
        if base_time.tzinfo is None:
            base_time = base_time.replace(tzinfo=timezone.utc)
            
        current_lat = df['latitude'].iloc[-1]
        current_lon = df['longitude'].iloc[-1]
        
        res = adapter.predict(seq, base_time, current_lat, current_lon, mode="replay")
        
        print("MODEL 4")
        print("-------")
        print(f"status: {res['status']}")
        print(f"artifact_sha256: {res['artifact_sha256']}")
        print(f"base_time: {res['base_time']}")
        print(f"valid_at: {res['valid_at']}")
        print(f"horizon_h: {res['horizon_h']}")
        print(f"sequence_length: {res['input_sequence_length']}")
        print(f"feature_count: {res['feature_count']}")
        print("")
        print("prediction:")
        if "north_km" in res:
            print(f"north_km: {res['north_km']:.6f}")
            print(f"east_km: {res['east_km']:.6f}")
        print("")
        print("P_M4_24:")
        if "latitude" in res:
            print(f"latitude: {res['latitude']:.6f}")
            print(f"longitude: {res['longitude']:.6f}")
            
    except Exception as e:
        print(f"Error running Mode B: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence", help="Path to 30-day feature sequence for M4")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--obs-time")
    parser.add_argument("--dest-lat", type=float)
    parser.add_argument("--dest-lon", type=float)
    
    args = parser.parse_args()
    
    if args.sequence:
        run_mode_b(args.sequence)
    elif args.lat is not None and args.lon is not None:
        try:
            obs_time = datetime.fromisoformat(args.obs_time.replace('Z', '+00:00'))
        except:
            obs_time = datetime.now(timezone.utc)
        run_mode_a(args.lat, args.lon, obs_time, args.dest_lat, args.dest_lon)
    else:
        print("Please provide either --sequence OR --lat/--lon/--dest-lat/--dest-lon")

if __name__ == "__main__":
    main()
