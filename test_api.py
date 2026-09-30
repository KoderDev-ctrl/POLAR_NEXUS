import requests
import json

base = "http://localhost:8000/api/v1"

def test_api():
    print("--- HEALTH ---")
    res = requests.get(f"{base}/health")
    print(res.status_code, res.json())
    
    print("\n--- STATUS ---")
    res = requests.get(f"{base}/status")
    print(res.status_code, res.json())
    
    print("\n--- MODELS ---")
    res = requests.get(f"{base}/models")
    print(res.status_code, res.json())

    print("\n--- ICEBERG ---")
    res = requests.get(f"{base}/hazard/IB-A76A?mode=replay")
    print(res.status_code, "Keys:", res.json().keys() if res.status_code == 200 else res.text)
    
    print("\n--- VOYAGE ---")
    payload = {
      "origin": [-62.2, -58.9],
      "destination": [-64.77, -64.05],
      "departure_time_utc": "2025-03-24T16:00:00Z",
      "vessel": {
        "max_ice_concentration": 30,
        "draft": 10,
        "depth_clearance": 2,
        "max_acceptable_risk": 100.0
      },
      "mode": "replay",
      "iceberg_id": "a23a"
    }
    res = requests.post(f"{base}/voyage/plan", json=payload)
    print(res.status_code)
    try:
        data = res.json()
        print("Keys:", data.keys())
        if 'selected_route' in data:
            print("Selected Route Geometry length:", len(data['selected_route'].get('geometry', [])))
        elif 'status' in data:
            print("Status:", data['status'], data.get('reason'))
    except Exception as e:
        print("Failed to parse json:", res.text)

if __name__ == "__main__":
    test_api()
