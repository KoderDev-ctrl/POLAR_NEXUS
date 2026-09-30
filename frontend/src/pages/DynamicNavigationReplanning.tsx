import React from 'react';
import { MapComponent } from '../components/MapComponent';

export default function DynamicNavigationReplanning() {
  return (
    <>
      <header className="fixed top-0 w-full z-50 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]"><div className="h-20 px-space-md flex flex-col justify-center gap-space-xs"><div className="flex items-center justify-between"><div className="flex items-center gap-space-sm"><div className="flex flex-col"><span className="font-headline-sm text-headline-sm uppercase text-primary tracking-wide">CRYOX | RouteX16</span><span className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">ANTARCTIC MARITIME COMMAND</span></div></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span><span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium tracking-tight">API: CONNECTED</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div><div className="flex items-center justify-between"><div className="flex items-center gap-space-xs"><span className="font-headline-sm text-headline-sm text-primary">Navigation</span></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="font-label-caps text-label-caps text-secondary">MODE:</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">LOW-BW</span></div><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="material-symbols-outlined text-[14px] text-secondary">schedule</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">14:22:08 UTC</span></div></div></div></div></header><main className="flex-1 w-full bg-surface pt-20 pb-safe"><div className="flex flex-col w-full px-space-md py-space-sm space-y-space-md">
{/* 1. DYNAMIC CLOSED-LOOP STATE STEPPER */}
<div className="bg-surface-container-lowest rounded-xl p-space-sm shadow-sm">
<div className="flex items-center justify-between pb-space-xs border-b border-surface-container mb-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-on-tertiary-container animate-spin" style={{ /* animation-duration: 4s; */ }}>sync</span>
<span className="font-label-caps text-label-caps text-secondary uppercase tracking-widest">Closed-Loop Trajectory Core</span>
</div>
<div className="flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-secondary-container/40">
<span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">CONTINUOUS MONITORING</span>
</div>
</div>
{/* Stepper Nodes Grid (Horizontally scrollable for tactical bridge glance) */}
<div className="grid grid-cols-4 gap-space-xs text-left">
{/* Step 1 */}
<div className="bg-surface-container-low rounded p-space-xs flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">01 POS</span>
<span className="material-symbols-outlined text-[12px] text-emerald-600">check_circle</span>
</div>
<div className="mt-1">
<div className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">64°48'S</div>
<div className="font-telemetry-xs text-telemetry-xs text-secondary">63°30'W</div>
</div>
<span className="font-label-caps text-[9px] text-on-secondary-container mt-1">VESSEL GPS</span>
</div>
{/* Step 2 */}
<div className="bg-surface-container-low rounded p-space-xs flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">02 CRYOX</span>
<span className="material-symbols-outlined text-[12px] text-emerald-600">check_circle</span>
</div>
<div className="mt-1">
<div className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">P6 MODEL</div>
<div className="font-telemetry-xs text-telemetry-xs text-on-tertiary-container">ACTIVE CALC</div>
</div>
<span className="font-label-caps text-[9px] text-on-secondary-container mt-1">AI DRIFT v4.2</span>
</div>
{/* Step 3 */}
<div className="bg-surface-container-low rounded p-space-xs flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">03 HAZARD</span>
<span className="material-symbols-outlined text-[12px] text-emerald-600">check_circle</span>
</div>
<div className="mt-1">
<div className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">ENVELOPE</div>
<div className="font-telemetry-xs text-telemetry-xs text-secondary">UPDATED 6m</div>
</div>
<span className="font-label-caps text-[9px] text-on-secondary-container mt-1">3.0 NM BUFFER</span>
</div>
{/* Step 4 */}
<div className="bg-surface-container-low rounded p-space-xs flex flex-col justify-between bg-secondary-container/20">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-primary">04 ROUTE</span>
<span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
</div>
<div className="mt-1">
<div className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">CURRENT</div>
<div className="font-telemetry-xs text-telemetry-xs text-emerald-700">OPTIMAL</div>
</div>
<span className="font-label-caps text-[9px] text-primary-container font-semibold mt-1">ROUTEX16 PASS</span>
</div>
</div>
</div>
{/* 2. DYNAMIC NAVIGATION MAP CANVAS */}
<div className="bg-surface-container-lowest rounded-xl shadow-sm overflow-hidden flex flex-col">
{/* Map Top HUD Bar */}
<div className="px-space-md py-space-xs bg-surface-container-low flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-secondary">explore</span>
<span className="font-label-caps text-label-caps text-primary font-bold">TACTICAL RADAR / SAR COMPOSITE</span>
</div>
<div className="flex items-center gap-space-xs">
<span className="font-telemetry-xs text-telemetry-xs text-secondary">ZOOM:</span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">1:25,000</span>
<span className="px-1.5 py-0.5 rounded bg-surface-container text-on-surface text-[10px] font-telemetry-xs">NORTH UP</span>
</div>
</div>
{/* Antarctic Map SVG Vector Canvas */}
<div className="relative w-full aspect-[4/3] bg-[#EBF2F7] overflow-hidden select-none">
{/* Latitude/Longitude Polar Grid Lines */}
<svg className="absolute inset-0 w-full h-full opacity-40 pointer-events-none" xmlns="http://www.w3.org/2000/svg">
<defs>
<pattern height="48" id="polarGrid" patternUnits="userSpaceOnUse" width="48">
<path d="M 48 0 L 0 0 0 48" fill="none" stroke="#7A92B0" strokeDasharray="2 3" strokeWidth="0.5" />
</pattern>
</defs>
<rect fill="url(#polarGrid)" height="100%" width="100%" />
</svg>
{/* Cartographic Coastal Geometry & Bathymetry Contours */}
<svg className="absolute inset-0 w-full h-full" preserveAspectRatio="xMidYMid meet" viewBox="0 0 400 300">
{/* Bathymetric Shallows (Neumayer Shoals) */}
<path d="M -10,40 Q 80,60 110,130 T 40,240 L -10,310 Z" fill="#D6E6F2" opacity="0.7" />
<path d="M 330,-10 Q 310,90 350,180 T 410,260 L 410,-10 Z" fill="#D6E6F2" opacity="0.7" />
{/* Coastline Contours */}
<path d="M -10,20 Q 70,40 90,110 T 20,210 L -10,290 Z" fill="#BACDD9" />
<path d="M 350,-10 Q 330,80 370,160 T 420,240 L 420,-10 Z" fill="#BACDD9" />
{/* Coastline Labels */}
<text className="font-label-caps" fill="#50657B" fontSize="8" letterSpacing="1" x="12" y="70">ANVERS ISLAND</text>
<text className="font-label-caps" fill="#50657B" fontSize="8" letterSpacing="1" x="315" y="100">WIENCKE ISL.</text>
<text className="font-telemetry-xs" fill="#7A92B0" fontSize="7" x="140" y="25">NEUMAYER CHANNEL DEEP SOUNDING [420m]</text>
{/* Replanning Trigger Zone Boundary Envelope */}
<polygon fill="#FFEAA7" fillOpacity="0.12" points="120,60 290,50 320,240 100,230" stroke="#E67E22" strokeDasharray="4 2" strokeWidth="0.75" />
<text className="font-label-caps" fill="#B98528" fontSize="7" x="125" y="72">REPLANNING TRIGGER ZONE (SEC-9)</text>
{/* Target IB-76A Hazard Buffer Zone (Authoritative 3.0 NM Perimeter) */}
{/* Center at approx (240, 140) */}
<circle cx="230" cy="130" fill="#C23B38" fillOpacity="0.08" r="54" stroke="#BA1A1A" strokeDasharray="3 3" strokeWidth="1.2" />
<circle cx="230" cy="130" fill="#C23B38" fillOpacity="0.12" r="30" stroke="#BA1A1A" strokeWidth="0.8" />
{/* Buffer Label */}
<text className="font-telemetry-xs" fill="#BA1A1A" fontSize="7.5" fontWeight="600" x="180" y="74">3.0 NM SAFETY BUFFER</text>
{/* Iceberg Trajectory Branches */}
{/* 1. P4 Observed History */}
<path d="M 275,80 Q 255,105 230,130" fill="none" stroke="#50657B" strokeWidth="1.5" />
<circle cx="275" cy="80" fill="#50657B" r="2.5" />
<text className="font-telemetry-xs" fill="#50657B" fontSize="6.5" x="282" y="82">P4 OBSERVED</text>
{/* 2. P_kin24 Kinematic Baseline (Yellowish Slate) */}
<path d="M 230,130 Q 210,165 195,210" fill="none" stroke="#B98528" strokeDasharray="3 3" strokeWidth="1.5" />
<text className="font-telemetry-xs" fill="#B98528" fontSize="6.5" x="160" y="215">P_kin24 KINEMATIC</text>
{/* 3. P6 24h AI Trajectory (Dashed Cyan / RouteX16 Primary) */}
<path d="M 230,130 Q 220,170 215,225" fill="none" stroke="#2F96DB" strokeDasharray="4 2" strokeWidth="2.2" />
<circle cx="215" cy="225" fill="#2F96DB" r="3" />
<text className="font-telemetry-xs" fill="#004B73" fontSize="7" fontWeight="600" x="222" y="228">P6 24h AI FORECAST</text>
{/* Iceberg Target Marker IB-76A */}
<g transform="translate(230, 130)">
{/* Iceberg diamond shape */}
<polygon fill="#BA1A1A" points="0,-7 7,0 0,7 -7,0" stroke="#FFFFFF" strokeWidth="1" />
<circle cx="0" cy="0" fill="#FFFFFF" r="1.5" />
<text className="font-telemetry-xs" fill="#102A43" fontSize="8" fontWeight="700" x="10" y="3">IB-76A (TABULAR)</text>
<text className="font-telemetry-xs" fill="#BA1A1A" fontSize="6.5" x="10" y="12">DRIFT: 145° @ 0.72 kts</text>
</g>
{/* Active Navigation Route: RX16 Pass outside 3.0 NM envelope */}
{/* Waypoint 3 -> Course -> Waypoint 4 */}
<path d="M 95,250 L 140,160 L 168,70" fill="none" stroke="#00152A" strokeWidth="3" />
{/* Route Safety Halo */}
<path d="M 95,250 L 140,160 L 168,70" fill="none" opacity="0.4" stroke="#CCE2FC" strokeWidth="8" />
{/* Waypoint 3 */}
<circle cx="95" cy="250" fill="#00152A" r="4.5" stroke="#FFFFFF" strokeWidth="1.5" />
<text className="font-telemetry-xs" fill="#00152A" fontSize="7.5" fontWeight="600" x="65" y="265">WP3 (PASSED)</text>
{/* Waypoint 4 */}
<circle cx="168" cy="70" fill="#00152A" r="4.5" stroke="#FFFFFF" strokeWidth="1.5" />
<text className="font-telemetry-xs" fill="#00152A" fontSize="7.5" fontWeight="600" x="175" y="70">WP4 (BISMARCK)</text>
{/* Closest Point of Approach (CPA) Measurement Vector */}
<line stroke="#7A92B0" strokeDasharray="2 2" strokeWidth="1" x1="140" x2="230" y1="160" y2="130" />
<text className="font-telemetry-xs" fill="#102A43" fontSize="7" fontWeight="600" x="155" y="140">CPA: 2.84 NM</text>
{/* Current Vessel Position & Velocity Vector */}
<g transform="translate(132, 175) rotate(-35)">
{/* Drift angle indicator */}
<line stroke="#00152A" strokeLinecap="round" strokeWidth="2" x1="0" x2="0" y1="0" y2="-24" />
<polygon fill="#00152A" points="0,-27 -3,-20 3,-20" />
{/* Vessel Hull Symbol */}
<polygon fill="#102A43" points="0,-10 5,6 0,4 -5,6" stroke="#FFFFFF" strokeWidth="1" />
{/* Speed Vector Length indicator */}
<circle cx="0" cy="0" fill="#2F96DB" r="2" />
</g>
{/* Vessel Callout */}
<rect fill="#FFFFFF" fillOpacity="0.9" height="24" rx="2" stroke="#CBD5E1" strokeWidth="0.5" width="85" x="75" y="185" />
<text className="font-telemetry-xs" fill="#00152A" fontSize="7" fontWeight="700" x="80" y="195">R/V POLARIS</text>
<text className="font-telemetry-xs" fill="#50657B" fontSize="6.5" x="80" y="204">COG: 032° | SOG: 9.4 kts</text>
</svg>
{/* Interactive Map Overlay Controls */}
<div className="absolute top-2 right-2 flex flex-col gap-1">
<button className="w-7 h-7 rounded bg-surface-container-lowest shadow-sm flex items-center justify-center text-primary active:bg-surface-container" title="Center on Vessel">
<span className="material-symbols-outlined text-[16px]">my_location</span>
</button>
<button className="w-7 h-7 rounded bg-surface-container-lowest shadow-sm flex items-center justify-center text-primary active:bg-surface-container" title="Layers">
<span className="material-symbols-outlined text-[16px]">layers</span>
</button>
<button className="w-7 h-7 rounded bg-surface-container-lowest shadow-sm flex items-center justify-center text-primary active:bg-surface-container" title="Distance Measure">
<span className="material-symbols-outlined text-[16px]">straighten</span>
</button>
</div>
{/* Tactical Legend Floating Strip */}
<div className="absolute bottom-2 left-2 right-2 bg-surface-container-lowest/95 backdrop-blur-sm rounded px-space-xs py-1 shadow-sm flex items-center justify-between text-[9px] font-telemetry-xs">
<div className="flex items-center gap-1">
<span className="w-2.5 h-0.5 bg-primary"></span>
<span className="text-secondary">ACTIVE ROUTE</span>
</div>
<div className="flex items-center gap-1">
<span className="w-2 h-0.5 bg-on-tertiary-container"></span>
<span className="text-secondary">P6 AI PREDICT</span>
</div>
<div className="flex items-center gap-1">
<span className="w-2 h-2 rounded-full bg-error/20 border border-error"></span>
<span className="text-error font-medium">3NM HAZARD</span>
</div>
</div>
</div>
</div>
{/* 3. DYNAMIC REPLANNING TRIGGER PANEL */}
<div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm space-y-space-sm">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<div className="w-2 h-2 rounded-full bg-emerald-600 animate-ping"></div>
<span className="font-headline-sm text-headline-sm text-primary uppercase">Dynamic Replanning Engine</span>
</div>
<div className="px-2 py-0.5 rounded bg-surface-container text-secondary font-label-caps text-[10px]">
        ACTIVE
      </div>
</div>
{/* Synced Status Well */}
<div className="p-space-xs bg-surface-container-low rounded flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-on-tertiary-container">satellite_alt</span>
<span className="font-body-sm text-body-sm text-on-surface font-medium">CRYOX: Time-aware hazard field synced</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">SYNC: 100%</span>
</div>
{/* Timer & Trigger Row */}
<div className="grid grid-cols-2 gap-space-sm items-center bg-surface-container rounded p-space-sm">
<div>
<div className="font-label-caps text-label-caps text-secondary uppercase">Next Automated Evaluation</div>
<div className="font-telemetry-lg text-telemetry-lg text-primary font-bold tracking-tight" id="replan-timer">00:14:22</div>
</div>
<div className="flex flex-col items-end justify-center">
<span className="font-label-caps text-label-caps text-secondary">CLEARANCE MARGIN</span>
<span className="font-telemetry-md text-telemetry-md text-emerald-700 font-semibold">+0.84 NM OVER SAFE</span>
</div>
</div>
{/* Live Vessel Stream Status Badge */}
<div className="flex items-center justify-between px-space-sm py-1.5 rounded bg-surface-container-low">
<div className="flex items-center gap-1.5">
<span className="w-2 h-2 rounded-full bg-emerald-600"></span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-medium tracking-tight">
          VESSEL NMEA STREAM: CONNECTED
        </span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-mono">10.0.12.44:10110</span>
</div>
{/* Action Buttons */}
<div className="grid grid-cols-1 gap-space-xs pt-space-xs">
<button className="w-full py-2 px-space-md bg-primary-container hover:bg-primary text-on-primary rounded font-label-caps uppercase tracking-wider text-center transition-colors flex items-center justify-center gap-space-xs active:scale-[0.99]" id="btn-reevaluate">
<span className="material-symbols-outlined text-[18px]">cached</span>
<span>Request Immediate RouteX16 Re-Evaluation</span>
</button>
<button className="w-full py-2 px-space-md bg-surface-container-low hover:bg-surface-container text-primary rounded font-label-caps uppercase tracking-wider text-center transition-colors flex items-center justify-center gap-space-xs">
<span className="material-symbols-outlined text-[18px]">tune</span>
<span>Adjust Safety Clearance (Current: 2.0 NM)</span>
</button>
</div>
</div>
{/* 4. NAVIGATION TELEMETRY GRID */}
<div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm space-y-space-sm">
<div className="flex items-center justify-between border-b border-surface-container pb-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-secondary">grid_view</span>
<span className="font-headline-sm text-headline-sm text-primary uppercase">Navigation Telemetry</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs px-2 py-0.5 rounded bg-surface-container text-primary font-semibold">RX16-PLN-20250324</span>
</div>
{/* Leg Banner */}
<div className="bg-surface-container-low p-space-xs rounded flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">ACTIVE LEG:</span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold text-right">WP3 (Neumayer) → WP4 (Bismarck)</span>
</div>
{/* High-density Metric Tiles (2 columns) */}
<div className="grid grid-cols-2 gap-space-xs">
{/* Min CPA */}
<div className="bg-surface-container-low p-space-xs rounded flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">MINIMUM CPA</span>
<span className="font-label-caps text-[9px] text-emerald-700 bg-emerald-50 px-1 rounded">SAFE</span>
</div>
<div className="my-1">
<span className="font-telemetry-lg text-telemetry-lg text-primary font-bold">2.84</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary ml-0.5">NM</span>
</div>
<span className="font-label-caps text-[9px] text-secondary">THRESHOLD: 2.0 NM</span>
</div>
{/* TCPA */}
<div className="bg-surface-container-low p-space-xs rounded flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">TIME TO CPA (TCPA)</span>
<span className="material-symbols-outlined text-[14px] text-secondary">timer</span>
</div>
<div className="my-1">
<span className="font-telemetry-lg text-telemetry-lg text-primary font-bold">+01h 42m</span>
</div>
<span className="font-label-caps text-[9px] text-secondary">T-CONVERGENCE</span>
</div>
{/* Estimated Fuel Burn */}
<div className="bg-surface-container-low p-space-xs rounded flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">EST. FUEL BURN</span>
<span className="font-label-caps text-[9px] text-on-tertiary-container">-4.2% OPT</span>
</div>
<div className="my-1">
<span className="font-telemetry-lg text-telemetry-lg text-primary font-bold">4.82</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary ml-0.5">MT MGO</span>
</div>
<span className="font-label-caps text-[9px] text-secondary">CONSUMPTION MODEL v3</span>
</div>
{/* Polar Code Compliance */}
<div className="bg-surface-container-low p-space-xs rounded flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary">POLAR CODE CLASS</span>
<span className="material-symbols-outlined text-[14px] text-emerald-700">verified</span>
</div>
<div className="my-1">
<span className="font-telemetry-md text-telemetry-md text-primary font-semibold">Category B</span>
</div>
<span className="font-label-caps text-[9px] text-emerald-700 font-semibold">LOW ICE HAZARD</span>
</div>
</div>
</div>
{/* 5. REAL-TIME EVENT LOG */}
<div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm space-y-space-xs mb-space-md">
<div className="flex items-center justify-between border-b border-surface-container pb-space-xs">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[16px] text-secondary">history</span>
<span className="font-headline-sm text-headline-sm text-primary uppercase">Dynamic Event Log</span>
</div>
<span className="font-label-caps text-label-caps text-secondary uppercase">UTC CHRONO</span>
</div>
{/* Sequential Monospace Timeline Rows */}
<div className="space-y-1 pt-space-xs">
{/* Item 1 */}
<div className="p-space-xs rounded bg-surface-container-low flex items-start gap-space-xs">
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-semibold shrink-0">14:18 UTC</span>
<div className="flex-1 min-w-0">
<div className="font-body-sm text-body-sm text-primary leading-tight">
            CRYOX updated P6 trajectory for target IB-76A
          </div>
<div className="font-telemetry-xs text-[10px] text-secondary">
            Drift revised 0.3 kn SE due to Antarctic Peninsular outflow.
          </div>
</div>
</div>
{/* Item 2 */}
<div className="p-space-xs rounded bg-surface-container-low flex items-start gap-space-xs">
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-semibold shrink-0">14:12 UTC</span>
<div className="flex-1 min-w-0">
<div className="font-body-sm text-body-sm text-primary leading-tight">
            RouteX16 verified corridor feasibility
          </div>
<div className="font-telemetry-xs text-[10px] text-emerald-700">
            Risk Index: 0.12 (Feasible) | 0 safety margin violations detected.
          </div>
</div>
</div>
{/* Item 3 */}
<div className="p-space-xs rounded bg-surface-container-low flex items-start gap-space-xs">
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-semibold shrink-0">13:45 UTC</span>
<div className="flex-1 min-w-0">
<div className="font-body-sm text-body-sm text-primary leading-tight">
            Waypoint WP2 traversed cleanly
          </div>
<div className="font-telemetry-xs text-[10px] text-secondary">
            Track deviation &lt; 0.05 NM | Hydro acoustic log locked.
          </div>
</div>
</div>
</div>
</div>
</div>
</main><nav className="fixed bottom-0 w-full z-50 pb-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_-1px_8px_rgba(0,0,0,0.04)]" data-activeClasses="text-primary-container font-semibold bg-secondary-container/40"><div className="flex justify-around items-center h-16 px-space-xs"><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="dashboard" href="#"><span className="material-symbols-outlined text-[20px]">radar</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Dashboard</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="explorer" href="#"><span className="material-symbols-outlined text-[20px]">explore</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Explorer</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="planner" href="#"><span className="material-symbols-outlined text-[20px]">alt_route</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Planner</span></a><a aria-current="page" className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded transition-colors text-primary-container font-semibold bg-secondary-container/40" data-path="navigation" href="#"><span className="material-symbols-outlined text-[20px]">navigation</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Navigation</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="system" href="#"><span className="material-symbols-outlined text-[20px]">hub</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">System</span></a></div></nav>
    </>
  );
}
