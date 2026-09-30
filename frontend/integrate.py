import os
import re

out_dir = r"c:\Users\Dev Jayswal\Desktop\Final_application\POLAR_NEXUS\polar_nexus\frontend\src\pages"

def patch_file(filename, patches):
    filepath = os.path.join(out_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in patches:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Mission Dashboard
patch_file('MissionDashboardCryoxRoutex16.tsx', [
    (
        "export default function MissionDashboardCryoxRoutex16() {",
        """import { useEffect, useState } from 'react';
import { fetchHealth, fetchStatus, fetchModels } from '../api/client';
import { MapContainer, TileLayer } from 'react-leaflet';

export default function MissionDashboardCryoxRoutex16() {
  const [health, setHealth] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [models, setModels] = useState<any>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.error);
    fetchStatus().then(setStatus).catch(console.error);
    fetchModels().then(setModels).catch(console.error);
  }, []);
"""
    ),
    (
        '<span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium tracking-tight">API: CONNECTED</span>',
        '<span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium tracking-tight">{health ? "API: CONNECTED" : "API: ERROR"}</span>'
    ),
    (
        '<div className="relative w-full h-80 bg-surface-container-highest overflow-hidden select-none">',
        '<div className="relative w-full h-80 bg-surface-container-highest overflow-hidden select-none z-0"><MapComponent />'
    ),
    (
        '<div className="w-full h-full bg-cover bg-center absolute inset-0 opacity-80" data-location="Gerlache Strait Antarctica" style={{ /* background-image: url(\'https://lh3.googleusercontent.com/aida-public/AB6AXuBdZkOY50NAJ3GtF6njPFTbe75025CBh078QY63-__5oQatbtU8hxCyCjR8nX6xEpK38Pc8yzsqGIV9FbUJsRQzL_GtXNKGw5AgDLROBKz0MYPaodvXcpP3fY-XIZcLQC0CAoqjwftYPajgw1Vg254t8T5T_aBaReIGK7KiA3D9r57AS4S1WyQEfJZzHgfL_2DndEe92XTses01V3YcXodUZh_scfqYj-GqWyx_JLXm3j3MGug822ek\') */ }}></div>',
        ''
    ),
    (
        '<span className="font-telemetry-sm text-telemetry-sm text-primary font-medium">AVAILABLE</span>',
        '<span className="font-telemetry-sm text-telemetry-sm text-primary font-medium">{models?.m5?.status || "AVAILABLE"}</span>'
    ),
    (
        '<span className="font-telemetry-sm text-telemetry-sm text-primary font-medium truncate">UNRESOLVED feature provenance</span>',
        '<span className="font-telemetry-sm text-telemetry-sm text-primary font-medium truncate">{models?.m6?.feature_provenance || "UNRESOLVED feature provenance"}</span>'
    ),
    (
        '<span className="font-telemetry-sm text-telemetry-sm text-error font-medium truncate">UNAVAILABLE operationally</span>',
        '<span className="font-telemetry-sm text-telemetry-sm text-error font-medium truncate">{models?.m1?.status || "UNAVAILABLE operationally"}</span>'
    )
])

# 2. Voyage Planner
patch_file('VoyagePlannerRoutex16.tsx', [
    (
        "export default function VoyagePlannerRoutex16() {",
        """import { useState } from 'react';
import { planVoyage } from '../api/client';
import { Polyline } from 'react-leaflet';

export default function VoyagePlannerRoutex16() {
  const [route, setRoute] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handlePlan = (e: any) => {
    e.preventDefault();
    setLoading(true);
    planVoyage({
      origin: [-62.2, -58.9],
      destination: [-64.77, -64.05],
      departure_time_utc: "2025-03-24T16:00:00Z",
      vessel: { max_ice_concentration: 30, draft: 10, depth_clearance: 2 },
      mode: 'operational'
    }).then(res => {
        setRoute(res);
        setLoading(false);
    }).catch(e => {
        console.error(e);
        setLoading(false);
    });
  };
"""
    ),
    (
        '<button className="w-full py-2.5 px-space-md bg-primary text-on-primary rounded-lg font-headline-sm text-headline-sm flex items-center justify-center gap-2 hover:bg-primary-container transition-colors shadow-sm" id="plan-btn" type="submit">',
        '<button onClick={handlePlan} className="w-full py-2.5 px-space-md bg-primary text-on-primary rounded-lg font-headline-sm text-headline-sm flex items-center justify-center gap-2 hover:bg-primary-container transition-colors shadow-sm" id="plan-btn" type="button">'
    ),
    (
        '<span>Calculate RouteX16 Alternatives</span>',
        '<span>{loading ? "Calculating..." : "Calculate RouteX16 Alternatives"}</span>'
    ),
    (
        '<div className="relative w-full h-48 bg-surface-container-low overflow-hidden">',
        '<div className="relative w-full h-48 bg-surface-container-low overflow-hidden z-0"><MapComponent />{route?.selected_route?.geometry && <div style={{position:"absolute", top:10, left:10, zIndex:1000}}>Route Ready</div>}'
    ),
    (
        '<svg className="w-full h-full" fill="none" viewBox="0 0 380 200" xmlns="http://www.w3.org/2000/svg">',
        '<svg className="w-full h-full hidden" fill="none" viewBox="0 0 380 200" xmlns="http://www.w3.org/2000/svg">'
    )
])

# 3. Iceberg Explorer
patch_file('IcebergExplorerCryox.tsx', [
    (
        "export default function IcebergExplorerCryox() {",
        """import { useState, useEffect } from 'react';
import { fetchHazard } from '../api/client';

export default function IcebergExplorerCryox() {
  const [hazard, setHazard] = useState<any>(null);

  useEffect(() => {
    fetchHazard("IB-A76A", "operational").then(setHazard).catch(console.error);
  }, []);
"""
    ),
    (
        '<div className="relative w-full h-[400px] bg-surface-container-highest overflow-hidden select-none">',
        '<div className="relative w-full h-[400px] bg-surface-container-highest overflow-hidden select-none z-0"><MapComponent />'
    ),
    (
        '<div className="w-full h-full bg-cover bg-center absolute inset-0 opacity-70" data-location="Weddell Sea Antarctica" style={{ /* background-image: url(\'https://lh3.googleusercontent.com/aida-public/AB6AXuABR7fRz3-U7d24o5o1J8Qc2NqY8c4w4x9w0x8y0k4_Kx5aR5y7b0_1X9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9\') */ }}></div>',
        ''
    ),
    (
        '<svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none" viewBox="0 0 400 400">',
        '<svg className="absolute inset-0 w-full h-full pointer-events-none hidden" preserveAspectRatio="none" viewBox="0 0 400 400">'
    )
])

print("Patched all pages")
