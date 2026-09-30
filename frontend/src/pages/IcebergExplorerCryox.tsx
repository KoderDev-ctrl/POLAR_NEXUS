import React from 'react';
import { MapComponent } from '../components/MapComponent';

import { useState, useEffect } from 'react';
import { fetchHazard } from '../api/client';

export default function IcebergExplorerCryox() {
  const [hazard, setHazard] = useState<any>(null);

  useEffect(() => {
    fetchHazard("IB-A76A", "operational").then(setHazard).catch(console.error);
  }, []);

  return (
    <>
      <header className="fixed top-0 w-full z-50 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]"><div className="h-20 px-space-md flex flex-col justify-center gap-space-xs"><div className="flex items-center justify-between"><div className="flex items-center gap-space-sm"><div className="flex flex-col"><span className="font-headline-sm text-headline-sm uppercase text-primary tracking-wide">CRYOX | RouteX16</span><span className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">ANTARCTIC MARITIME COMMAND</span></div></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span><span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium tracking-tight">API: CONNECTED</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div><div className="flex items-center justify-between"><div className="flex items-center gap-space-xs"><span className="font-headline-sm text-headline-sm text-primary">Explorer</span></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="font-label-caps text-label-caps text-secondary">MODE:</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">LOW-BW</span></div><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="material-symbols-outlined text-[14px] text-secondary">schedule</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">14:22:08 UTC</span></div></div></div></div></header><main className="flex-1 w-full bg-surface pt-20 pb-safe"><div className="flex flex-col w-full pb-8 space-y-3 px-3">
{/* Target Selection & Query Array */}
<div className="bg-surface-container-lowest p-3 rounded-lg shadow-sm flex flex-col gap-2.5">
<div className="flex items-center justify-between">
<div className="flex items-center gap-1.5">
<span className="material-symbols-outlined text-[18px] text-primary">radar</span>
<span className="font-label-caps text-label-caps uppercase text-secondary">TARGET TRACKING VECTOR</span>
</div>
<span className="bg-surface-container-low px-2 py-0.5 rounded font-telemetry-xs text-telemetry-xs text-secondary font-medium">NIC REF: A76A_2024</span>
</div>
{/* Dropdown / Search Trigger */}
<div className="relative bg-surface-container-low p-2 rounded flex items-center justify-between cursor-pointer">
<div className="flex items-center gap-2 min-w-0">
<span className="material-symbols-outlined text-[20px] text-primary shrink-0">ac_unit</span>
<div className="flex flex-col min-w-0">
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold truncate">IB-76A-FRAGMENT</span>
<span className="font-telemetry-xs text-telemetry-xs text-on-secondary-container truncate">NIC A76A_2024 • TABULAR CALVED UNIT</span>
</div>
</div>
<div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded shadow-sm">
<span className="font-label-caps text-label-caps text-primary">SELECT</span>
<span className="material-symbols-outlined text-[16px] text-secondary">unfold_more</span>
</div>
</div>
{/* Quick Target Selector Pills (Horizontal Scroll) */}
<div className="flex items-center gap-1.5 overflow-x-auto pb-0.5" id="target-pill-row">
<button className="target-pill active-pill whitespace-nowrap px-2.5 py-1 rounded font-telemetry-xs text-telemetry-xs font-semibold bg-primary text-on-primary flex items-center gap-1 shrink-0">
<span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
        IB-76A (Active)
      </button>
<button className="target-pill whitespace-nowrap px-2.5 py-1 rounded font-telemetry-xs text-telemetry-xs text-secondary bg-surface-container-low hover:bg-surface-container hover:text-primary transition-colors flex items-center gap-1 shrink-0">
        IB-B15K
      </button>
<button className="target-pill whitespace-nowrap px-2.5 py-1 rounded font-telemetry-xs text-telemetry-xs text-secondary bg-surface-container-low hover:bg-surface-container hover:text-primary transition-colors flex items-center gap-1 shrink-0">
        IB-D28
      </button>
<button className="target-pill whitespace-nowrap px-2.5 py-1 rounded font-telemetry-xs text-telemetry-xs text-error font-medium bg-error-container/40 hover:bg-error-container hover:text-on-error-container transition-colors flex items-center gap-1 shrink-0">
<span className="material-symbols-outlined text-[12px]">warning</span>
        UNTRACKED BERGY #12
      </button>
</div>
</div>
{/* Primary Tactical Map Canvas Container */}
<div className="bg-surface-container-lowest rounded-lg shadow-sm overflow-hidden flex flex-col">
{/* Map Control / Status Header */}
<div className="bg-surface-container-low px-3 py-2 flex items-center justify-between">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[16px] text-secondary">explore</span>
<span className="font-label-caps text-label-caps uppercase text-secondary">SECTOR 64°S TACTICAL PLOT</span>
</div>
<div className="flex items-center gap-2">
<span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold bg-surface-container-lowest px-1.5 py-0.5 rounded shadow-sm">64°52'S, 63°18'W</span>
<span className="bg-emerald-50 text-emerald-800 font-telemetry-xs text-telemetry-xs px-1.5 py-0.5 rounded">SAR: LATEST FIX</span>
</div>
</div>
{/* Inline Tactical Interactive Vector Plot */}
<div className="relative w-full aspect-[4/3] bg-[#EAF0F6] overflow-hidden select-none" id="tactical-plot">
{/* Bathymetry contour gradient bed */}
<svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none" viewBox="0 0 400 300">
<defs>
<radialgradient cx="80%" cy="85%" id="shoal" r="45%">
<stop offset="0%" stopColor="#DCE7F0" stopOpacity="0.9"></stop>
<stop offset="100%" stopColor="#EAF0F6" stopOpacity="0"></stop>
</radialgradient>
<pattern height="40" id="grid" patternUnits="userSpaceOnUse" width="40">
<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" />
</pattern>
</defs>
<rect fill="url(#grid)" height="100%" width="100%" />
<circle cx="320" cy="255" fill="url(#shoal)" r="110" />
{/* Shoal contour lines (Neumayer Shoals) */}
<path d="M 240 300 Q 280 220 370 210 Q 400 208 400 220" fill="none" stroke="#94A3B8" strokeDasharray="4 2" strokeWidth="0.8" />
<text fill="#64748B" fontFamily="JetBrains Mono" fontSize="8" letterSpacing="0.5" x="270" y="275">NEUMAYER SHALLOWS (140-190m)</text>
{/* RouteX16 Planned Vessel Corridor */}
<path d="M 30 260 L 160 180 L 290 80 L 370 20" fill="none" stroke="#314863" strokeDasharray="6 3" strokeWidth="2" />
<path d="M 30 260 L 160 180 L 290 80 L 370 20" fill="none" stroke="#93CCFF" strokeOpacity="0.18" strokeWidth="12" />
{/* Clearance corridor vector line */}
<line stroke="#004B73" strokeDasharray="2 2" strokeWidth="1.2" x1="160" x2="160" y1="180" y2="120" />
<circle cx="160" cy="180" fill="#102A43" r="3" />
<rect fill="#FFFFFF" fillOpacity="0.92" height="18" rx="2" width="130" x="80" y="185" />
<text fill="#00152A" fontFamily="JetBrains Mono" fontSize="8.5" fontWeight="600" x="85" y="197">VESSEL PASS: CPA 2.84 NM</text>
{/* Operational Safety Exclusion Zone (Translucent Buffer) */}
<ellipse cx="160" cy="120" fill="#FFE4E6" fillOpacity="0.45" rx="90" ry="75" stroke="#F43F5E" strokeDasharray="4 2" strokeWidth="1" />
<text fill="#E11D48" fontFamily="JetBrains Mono" fontSize="7.5" fontWeight="600" x="175" y="60">HAZARD EXCLUSION ZONE (3.50 NM)</text>
{/* P_kin24 Drift Trajectory (Kinematic straight extrapolation) */}
<line stroke="#64748B" strokeDasharray="3 3" strokeWidth="1.5" x1="160" x2="225" y1="120" y2="195" />
<circle cx="225" cy="195" fill="#64748B" r="3" />
<rect fill="#FFFFFF" fillOpacity="0.9" height="14" rx="2" width="70" x="230" y="190" />
<text fill="#475569" fontFamily="JetBrains Mono" fontSize="7.5" x="234" y="200">P_kin24 (0.8 kn)</text>
{/* P6 Deep Model 24h Prediction Trajectory (Hydrodynamic curve) */}
<path d="M 160 120 Q 200 160 255 230" fill="none" stroke="#0284C7" strokeWidth="2.5" />
{/* Directional ticks along P6 */}
<polygon fill="#0284C7" points="210,172 216,168 214,176" />
<polygon fill="#0284C7" points="255,230 252,222 247,227" />
<circle cx="255" cy="230" fill="#0284C7" r="4" />
<rect fill="#002B45" height="15" rx="2" width="95" x="262" y="224" />
<text fill="#FFFFFF" fontFamily="JetBrains Mono" fontSize="8" fontWeight="600" x="266" y="234">P6 24h: 94.2% CONF</text>
{/* P4 Latest Observed Iceberg Tabular Geometry */}
<g transform="translate(160,120) rotate(-22)">
{/* Tabular mass bounding polygon (3.2 NM x 1.1 NM relative scale) */}
<polygon fill="#FFFFFF" points="-32,-11 30,-14 34,10 -28,12" stroke="#00152A" strokeWidth="1.7" />
{/* Ice texture internal fracture fissures */}
<line stroke="#94A3B8" strokeWidth="0.75" x1="-12" x2="-8" y1="-10" y2="10" />
<line stroke="#94A3B8" strokeWidth="0.75" x1="8" x2="14" y1="-12" y2="9" />
<circle cx="0" cy="0" fill="#BA1A1A" r="2.5" />
</g>
<rect fill="#FFFFFF" fillOpacity="0.92" height="14" rx="2" width="62" x="100" y="98" />
<text fill="#BA1A1A" fontFamily="JetBrains Mono" fontSize="8" fontWeight="600" x="104" y="108">P4: SAR FIX</text>
</svg>
{/* Tactical Map Overlay Badge */}
<div className="absolute top-2 left-2 flex flex-col gap-1 pointer-events-none">
<div className="bg-surface-container-lowest/90 px-2 py-1 rounded shadow-sm flex items-center gap-1.5">
<span className="w-2 h-2 rounded-full bg-error"></span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-bold">RADAR TARGET: 3.2 x 1.1 NM</span>
</div>
</div>
{/* Map Scale & Bearing Legend */}
<div className="absolute bottom-2 right-2 bg-surface-container-lowest/90 px-2 py-1 rounded shadow-sm flex items-center gap-2 pointer-events-none">
<div className="flex items-center gap-1">
<div className="w-6 h-0.5 bg-primary"></div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium">1.0 NM</span>
</div>
<span className="text-outline-variant font-telemetry-xs">|</span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">DRIFT: 158° SSE</span>
</div>
</div>
{/* Map Legend Tray */}
<div className="bg-surface-container-low px-3 py-2 grid grid-cols-2 gap-2 text-secondary">
<div className="flex items-center gap-1.5">
<span className="w-3 h-1.5 rounded-sm bg-primary"></span>
<span className="font-telemetry-xs text-telemetry-xs truncate">Tabular Core Fix (13:00Z)</span>
</div>
<div className="flex items-center gap-1.5">
<span className="w-3 h-1 bg-[#0284C7] rounded"></span>
<span className="font-telemetry-xs text-telemetry-xs truncate">P6 Deep Drift (Geostrophic)</span>
</div>
<div className="flex items-center gap-1.5">
<span className="w-3 h-0.5 bg-slate-500 border-dashed"></span>
<span className="font-telemetry-xs text-telemetry-xs truncate">P_kin24 Persistence</span>
</div>
<div className="flex items-center gap-1.5">
<span className="w-3 h-2 rounded-sm bg-rose-200/80"></span>
<span className="font-telemetry-xs text-telemetry-xs truncate">Safety Exclusion Zone</span>
</div>
</div>
</div>
{/* Authoritative Prediction & Hazard Tabbed Interface */}
<div className="bg-surface-container-lowest rounded-lg shadow-sm p-3 flex flex-col gap-3">
{/* Tab Controls Header */}
<div className="bg-surface-container-low p-1 rounded flex items-center gap-1" id="tab-controls">
<button className="tab-btn flex-1 py-1.5 px-2 rounded font-label-caps text-label-caps uppercase text-center font-semibold bg-surface-container-lowest text-primary shadow-sm transition-all" data-tab="predictions">
        Predictions
      </button>
<button className="tab-btn flex-1 py-1.5 px-2 rounded font-label-caps text-label-caps uppercase text-center font-medium text-secondary hover:text-primary transition-all" data-tab="hazard">
        Hazard Metrics
      </button>
<button className="tab-btn flex-1 py-1.5 px-2 rounded font-label-caps text-label-caps uppercase text-center font-medium text-secondary hover:text-primary transition-all" data-tab="provenance">
        Provenance
      </button>
</div>
{/* TAB 1: OPERATIONAL PREDICTIONS */}
<div className="tab-pane flex flex-col space-y-2" id="tab-pane-predictions">
{/* P4 Ground Truth Fix */}
<div className="bg-surface-container-low p-2.5 rounded flex items-center justify-between">
<div className="flex flex-col min-w-0 pr-2">
<div className="flex items-center gap-1.5">
<span className="font-telemetry-sm text-telemetry-sm font-semibold text-primary">P4 (Observed Radar Fix)</span>
<span className="bg-emerald-100 text-emerald-800 font-telemetry-xs text-telemetry-xs px-1.5 rounded">TRUTH</span>
</div>
<span className="font-telemetry-sm text-telemetry-sm text-secondary mt-0.5">64°52.1'S, 63°18.4'W</span>
<span className="font-body-sm text-body-sm text-on-surface-variant text-[11px]">Synthetic Aperture Radar verified geometry</span>
</div>
<div className="text-right shrink-0">
<span className="font-telemetry-xs text-telemetry-xs text-secondary block uppercase">Error Residual</span>
<span className="font-telemetry-md text-telemetry-md font-bold text-primary">0.0 NM</span>
</div>
</div>
{/* P_kin24 Persistence Drift */}
<div className="bg-surface-container-low p-2.5 rounded flex items-center justify-between">
<div className="flex flex-col min-w-0 pr-2">
<div className="flex items-center gap-1.5">
<span className="font-telemetry-sm text-telemetry-sm font-semibold text-primary">P_kin24 (Kinematic Persistence)</span>
</div>
<span className="font-telemetry-sm text-telemetry-sm text-secondary mt-0.5">64°54.3'S, 63°15.1'W</span>
<span className="font-body-sm text-body-sm text-on-surface-variant text-[11px]">Uncorrected linear extrapolation</span>
</div>
<div className="text-right shrink-0">
<span className="font-telemetry-xs text-telemetry-xs text-secondary block uppercase">Projected Vel.</span>
<span className="font-telemetry-md text-telemetry-md font-semibold text-primary">0.8 kn</span>
</div>
</div>
{/* P6 CRYOX Deep Model Prediction */}
<div className="bg-surface-container-low p-2.5 rounded flex items-center justify-between">
<div className="flex flex-col min-w-0 pr-2">
<div className="flex items-center gap-1.5">
<span className="font-telemetry-sm text-telemetry-sm font-bold text-primary">P6 (CRYOX Deep 24h Model)</span>
<span className="bg-secondary-container text-on-secondary-fixed font-telemetry-xs text-telemetry-xs px-1.5 rounded font-semibold">COUPLED</span>
</div>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-medium mt-0.5">64°55.9'S, 63°12.8'W</span>
<span className="font-body-sm text-body-sm text-on-surface-variant text-[11px]">Coupled bathymetry + geostrophic drag</span>
</div>
<div className="text-right shrink-0">
<span className="font-telemetry-xs text-telemetry-xs text-secondary block uppercase">Confidence</span>
<span className="font-telemetry-md text-telemetry-md font-bold text-[#0284C7]">94.2%</span>
</div>
</div>
</div>
{/* TAB 2: HAZARD ENVELOPE METRICS */}
<div className="tab-pane hidden flex flex-col space-y-2" id="tab-pane-hazard">
<div className="grid grid-cols-2 gap-2">
{/* Hazard Buffer */}
<div className="bg-surface-container-low p-2.5 rounded flex flex-col">
<span className="font-label-caps text-label-caps uppercase text-secondary">Authoritative Radius</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-lg text-telemetry-lg font-bold text-error">3.50</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">NM</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant mt-1 text-[11px]">Calving fragment buffer</span>
</div>
{/* Drift Heading */}
<div className="bg-surface-container-low p-2.5 rounded flex flex-col">
<span className="font-label-caps text-label-caps uppercase text-secondary">Drift Heading</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-lg text-telemetry-lg font-bold text-primary">158°</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">SSE</span>
</div>
<span className="font-body-sm text-body-sm text-on-surface-variant mt-1 text-[11px]">Steady current push</span>
</div>
</div>
{/* Keel Depth and Grounding Risk Tile */}
<div className="bg-surface-container-low p-3 rounded flex flex-col gap-2">
<div className="flex items-center justify-between">
<div className="flex items-center gap-1.5">
<span className="material-symbols-outlined text-[18px] text-amber-700">water_voc</span>
<span className="font-label-caps text-label-caps uppercase text-primary">Keel Depth / Seabed Clearance</span>
</div>
<span className="bg-amber-100 text-amber-900 font-telemetry-xs text-telemetry-xs px-2 py-0.5 rounded font-semibold">GROUNDING ALERT</span>
</div>
<div className="flex items-baseline justify-between">
<div>
<span className="font-telemetry-lg text-telemetry-lg font-bold text-primary">185 m</span>
<span className="font-body-sm text-body-sm text-secondary ml-1">Draft Estimate</span>
</div>
<div className="text-right">
<span className="font-telemetry-sm text-telemetry-sm font-semibold text-amber-800">Neumayer Shoals: 165-190m</span>
</div>
</div>
<p className="font-body-sm text-body-sm text-on-surface-variant text-[11px] leading-snug">
          Iceberg mass expected to contact underwater plateau along 64°56'S corridor within 18h, causing erratic rotational yaw and fragmentation.
        </p>
</div>
{/* Route Clearance Stat */}
<div className="bg-secondary-container/30 p-2.5 rounded flex items-center justify-between">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[20px] text-primary">alt_route</span>
<div className="flex flex-col">
<span className="font-telemetry-xs text-telemetry-xs text-secondary uppercase">RouteX16 Planned Transit</span>
<span className="font-telemetry-sm text-telemetry-sm font-semibold text-primary">Min Vessel Clearance</span>
</div>
</div>
<span className="font-telemetry-md text-telemetry-md font-bold text-primary">2.84 NM</span>
</div>
</div>
{/* TAB 3: DATA PROVENANCE & FRESHNESS */}
<div className="tab-pane hidden flex flex-col space-y-2" id="tab-pane-provenance">
<div className="bg-surface-container-low p-2.5 rounded flex flex-col gap-1.5">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps uppercase text-secondary">Sensor Source</span>
<span className="font-telemetry-xs text-telemetry-xs font-semibold text-primary">POLARIS SAR CONSTELLATION</span>
</div>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-medium">Sentinel-1B Synthetic Aperture Radar (SAR)</span>
<span className="font-body-sm text-body-sm text-on-surface-variant text-[11px]">Interferometric Wide Swath Mode • 10m spatial resolution</span>
</div>
<div className="grid grid-cols-2 gap-2">
<div className="bg-surface-container-low p-2.5 rounded flex flex-col">
<span className="font-label-caps text-label-caps uppercase text-secondary">Downlink Earth Station</span>
<span className="font-telemetry-sm text-telemetry-sm font-semibold text-primary mt-1">TrollSat Station</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">Queen Maud Land (72°S)</span>
</div>
<div className="bg-surface-container-low p-2.5 rounded flex flex-col">
<span className="font-label-caps text-label-caps uppercase text-secondary">Latency / Model</span>
<div className="flex items-baseline gap-1 mt-1">
<span className="font-telemetry-md text-telemetry-md font-bold text-primary">41</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">min</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-mono">CRYOX-HAZARD-V1.4</span>
</div>
</div>
<div className="bg-surface-container-low p-2 rounded flex items-center justify-between text-secondary">
<div className="flex items-center gap-1.5">
<span className="material-symbols-outlined text-[16px] text-emerald-600">verified_user</span>
<span className="font-telemetry-xs text-telemetry-xs">Cryptographic Telemetry Signature</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs font-mono">SHA256: 9b2d...f4e1</span>
</div>
</div>
</div>
{/* Operational Decision Actions */}
<div className="flex flex-col gap-2">
{/* Primary navy action button */}
<button className="w-full bg-primary text-on-primary hover:bg-[#17324D] active:bg-[#0C2033] py-2.5 px-4 rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-2 shadow-sm transition-colors" id="send-buffer-btn">
<span className="material-symbols-outlined text-[18px]">publish</span>
      Send Hazard Buffer to RouteX16 Planner
    </button>
{/* Secondary Outline Action */}
<button className="w-full bg-surface-container-lowest text-primary hover:bg-surface-container-low py-2 px-4 rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-2 shadow-sm transition-colors" id="export-geojson-btn">
<span className="material-symbols-outlined text-[18px] text-secondary">file_download</span>
      Export GeoJSON Hazard Geometry (.json)
    </button>
</div>
{/* Toast Notification Container for Feedback */}
<div className="fixed bottom-20 left-4 right-4 bg-primary text-on-primary px-3 py-2 rounded shadow-md flex items-center justify-between opacity-0 pointer-events-none transition-opacity duration-200 z-50" id="toast-notify">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[18px] text-emerald-400">check_circle</span>
<span className="font-telemetry-xs text-telemetry-xs" id="toast-text">Buffer synchronized to RouteX16 Engine</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary-fixed">ACK 200</span>
</div>
</div>
</main><nav className="fixed bottom-0 w-full z-50 pb-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_-1px_8px_rgba(0,0,0,0.04)]" data-activeClasses="text-primary-container font-semibold bg-secondary-container/40"><div className="flex justify-around items-center h-16 px-space-xs"><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="dashboard" href="#"><span className="material-symbols-outlined text-[20px]">radar</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Dashboard</span></a><a aria-current="page" className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded transition-colors text-primary-container font-semibold bg-secondary-container/40" data-path="explorer" href="#"><span className="material-symbols-outlined text-[20px]">explore</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Explorer</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="planner" href="#"><span className="material-symbols-outlined text-[20px]">alt_route</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Planner</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="navigation" href="#"><span className="material-symbols-outlined text-[20px]">navigation</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Navigation</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="system" href="#"><span className="material-symbols-outlined text-[20px]">hub</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">System</span></a></div></nav>
    </>
  );
}
