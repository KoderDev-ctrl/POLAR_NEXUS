import React from 'react';
import { MapComponent } from '../components/MapComponent';

export default function CryoxRoutex16AntarcticMaritimeNavigation() {
  return (
    <>
      <header className="fixed top-0 w-full z-50 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]"><div className="h-20 px-space-md flex flex-col justify-center gap-space-xs"><div className="flex items-center justify-between"><div className="flex items-center gap-space-sm"><div className="flex flex-col"><span className="font-headline-sm text-headline-sm uppercase text-primary tracking-wide">CRYOX | RouteX16</span><span className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">ANTARCTIC MARITIME COMMAND</span></div></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span><span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium tracking-tight">API: CONNECTED</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div><div className="flex items-center justify-between"><div className="flex items-center gap-space-xs"><span className="font-headline-sm text-headline-sm text-primary">Dashboard</span></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="font-label-caps text-label-caps text-secondary">MODE:</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">LOW-BW</span></div><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="material-symbols-outlined text-[14px] text-secondary">schedule</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">14:22:08 UTC</span></div></div></div></div></header><main className="flex-1 w-full bg-surface pt-20 pb-safe"><div className="flex flex-col w-full pb-8 space-y-space-md">
{/* Core Mission Banner */}
<section className="bg-surface-container-lowest rounded-lg p-space-md shadow-sm">
<div className="flex flex-col gap-space-sm">
<div className="flex items-start justify-between gap-space-sm">
<div className="flex flex-col min-w-0">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[18px] text-primary" style={{ /* font-variation-settings: 'FILL' 1; */ }}>directions_boat</span>
<h1 className="font-headline-md text-headline-md text-primary tracking-tight truncate">R/V POLARIS V</h1>
</div>
<p className="font-label-caps text-label-caps text-secondary uppercase tracking-widest mt-0.5">TRANSIT IN PROGRESS • ICE CLASS PC5</p>
</div>
<div className="inline-flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-emerald-50 text-emerald-800">
<span className="w-2 h-2 rounded-full bg-emerald-600"></span>
<span className="font-telemetry-xs text-telemetry-xs font-semibold tracking-wide">FEASIBLE</span>
</div>
</div>
<div className="grid grid-cols-2 gap-space-xs pt-space-xs">
<div className="bg-surface-container-low p-space-xs rounded flex flex-col justify-center">
<span className="font-label-caps text-label-caps text-secondary uppercase">POS (GERLACHE)</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold tracking-tight">64°48′S, 63°30′W</span>
</div>
<div className="bg-surface-container-low p-space-xs rounded flex flex-col justify-center">
<span className="font-label-caps text-label-caps text-secondary uppercase">DESTINATION / ETA</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold tracking-tight truncate">Palmer Pier • 03-24 14:30z</span>
</div>
</div>
</div>
</section>
{/* Architectural Thesis Callout Box */}
<section className="bg-surface-container-lowest rounded-lg p-space-md shadow-sm relative overflow-hidden">
<div className="absolute left-0 top-0 bottom-0 w-1 bg-secondary-container"></div>
<div className="flex items-start gap-space-sm pl-1">
<div className="w-8 h-8 rounded bg-surface-container-low flex items-center justify-center shrink-0">
<span className="material-symbols-outlined text-primary text-[20px]">reorder</span>
</div>
<div className="flex flex-col">
<span className="font-headline-sm text-headline-sm text-primary uppercase tracking-wider">Dynamic Routing</span>
<p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 leading-relaxed">
          As the vessel moves and environmental conditions change, CRYOX updates the time-aware hazard field and RouteX16 re-optimizes the remaining voyage.
        </p>
</div>
</div>
</section>
{/* Tactical Map & Chart Card */}
<section className="bg-surface-container-lowest rounded-lg overflow-hidden shadow-sm flex flex-col">
{/* Map Control Header */}
<div className="p-space-sm bg-surface-container-low flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[18px] text-secondary">explore</span>
<span className="font-label-caps text-label-caps text-secondary uppercase tracking-widest">TACTICAL ECDIS // PALMER ARCHIPELAGO</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">PROJ: POLAR STEREOGRAPHIC</span>
</div>
{/* Map Canvas Viewport with Vector Overlay */}
<div className="relative w-full h-80 bg-surface-container-highest overflow-hidden select-none">
{/* Background Map Texture via data-location */}
<div className="w-full h-full bg-cover bg-center absolute inset-0 opacity-80" data-location="Gerlache Strait Antarctica" style={{ /* background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuBdZkOY50NAJ3GtF6njPFTbe75025CBh078QY63-__5oQatbtU8hxCyCjR8nX6xEpK38Pc8yzsqGIV9FbUJsRQzL_GtXNKGw5AgDLROBKz0MYPaodvXcpP3fY-XIZcLQC0CAoqjwftYPajgw1Vg254t8T5T_aBaReIGK7KiA3D9r57AS4S1WyQEfJZzHgfL_2DndEe92XTses01V3YcXodUZh_scfqYj-GqWyx_JLXm3j3MGug822ek') */ }}></div>
{/* Tactical SVG Overlays: Coastlines, Waypoints, Isobars, and Routes */}
<svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none" viewBox="0 0 360 320">
<defs>
<pattern height="40" id="polarGrid" patternUnits="userSpaceOnUse" width="40">
<path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(75, 96, 118, 0.15)" strokeWidth="0.5" />
</pattern>
<filter height="140%" id="hazardGlow" width="140%" x="-20%" y="-20%">
<feGaussianBlur in="SourceGraphic" stdDeviation="4"></feGaussianBlur>
</filter>
</defs>
{/* Coordinate Grid Lines */}
<rect fill="url(#polarGrid)" height="100%" width="100%" />
{/* Sub-surface bathymetry contour lines */}
<path d="M-20,120 Q80,140 180,100 T380,160" fill="none" opacity="0.4" stroke="#7a92b0" strokeDasharray="3,3" strokeWidth="0.75" />
<path d="M-20,180 Q100,210 220,170 T380,220" fill="none" opacity="0.4" stroke="#7a92b0" strokeDasharray="3,3" strokeWidth="0.75" />
{/* Hazard Envelope A-76A Iceberg (Subtle Red Contour + Uncertainty Buffer) */}
<g id="hazard-a76a">
{/* Uncertainty Buffer */}
<ellipse cx="230" cy="140" fill="rgba(186, 26, 26, 0.08)" rx="38" ry="24" stroke="#ba1a1a" strokeDasharray="2,2" strokeWidth="0.75" />
{/* Core Hazard Footprint */}
<ellipse cx="230" cy="140" fill="rgba(186, 26, 26, 0.18)" rx="22" ry="14" stroke="#ba1a1a" strokeWidth="1.2" />
{/* Drift vector */}
<line stroke="#ba1a1a" strokeWidth="1.2" x1="230" x2="250" y1="140" y2="155" />
<polygon fill="#ba1a1a" points="250,155 244,151 247,147" />
{/* Hazard Annotation */}
<text fill="#93000a" fontFamily="'JetBrains Mono', monospace" fontSize="8" fontWeight="600" x="210" y="116">IB-A76A [1.8kt 142°]</text>
</g>
{/* Alternative Feasible Route RX16-BETA-02 (Dashed Slate) */}
<path d="M70,50 L120,95 L170,160 L240,240 L280,285" fill="none" stroke="#50657b" strokeDasharray="4,4" strokeWidth="1.75" />
{/* Primary Active Route RX16-ALPHA-04 (Bold Navy) */}
<path d="M70,50 L140,110 L195,175 L230,225 L280,285" fill="none" id="active-route" stroke="#00152a" strokeLinecap="round" strokeWidth="2.75" />
{/* Waypoint Nodes on Active Route */}
<circle cx="70" cy="50" fill="#ffffff" r="3.5" stroke="#00152a" strokeWidth="2" />
<circle cx="140" cy="110" fill="#ffffff" r="2.5" stroke="#00152a" strokeWidth="1.5" />
<circle cx="195" cy="175" fill="#ffffff" r="2.5" stroke="#00152a" strokeWidth="1.5" />
<circle cx="230" cy="225" fill="#ffffff" r="2.5" stroke="#00152a" strokeWidth="1.5" />
<circle cx="280" cy="285" fill="#00152a" r="4" />
{/* Closest Point of Approach Line (CPA Vector) */}
<line stroke="#ba1a1a" strokeDasharray="2,2" strokeWidth="1" x1="195" x2="230" y1="175" y2="140" />
<text fill="#ba1a1a" fontFamily="'JetBrains Mono', monospace" fontSize="7.5" fontWeight="600" x="180" y="152">CPA 2.84 NM</text>
{/* Vessel Marker (R/V POLARIS V) at WP1 */}
<g transform="translate(70, 50) rotate(184)">
{/* Ship Icon Vector */}
<path d="M0,-8 L5,5 L0,3 L-5,5 Z" fill="#00152a" stroke="#ffffff" strokeWidth="1" />
{/* Heading Vector Projection */}
<line stroke="#00152a" strokeDasharray="2,2" strokeWidth="1.2" x1="0" x2="0" y1="3" y2="28" />
</g>
</svg>
{/* Tactical Overlay Pills & Scale Bar */}
<div className="absolute top-2 left-2 flex flex-col gap-1">
<span className="px-space-xs py-0.5 rounded bg-surface-container-lowest/90 font-telemetry-xs text-telemetry-xs text-primary font-medium shadow-xs">
          LAT 64°48.12'S
        </span>
<span className="px-space-xs py-0.5 rounded bg-surface-container-lowest/90 font-telemetry-xs text-telemetry-xs text-primary font-medium shadow-xs">
          LON 063°30.05'W
        </span>
</div>
<div className="absolute bottom-2 left-2 flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-surface-container-lowest/90 shadow-xs">
<div className="flex flex-col">
<div className="flex items-center gap-1">
<span className="w-8 h-1 bg-primary inline-block"></span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-bold">10 NM</span>
</div>
<span className="font-label-caps text-[8px] text-secondary">BATHY: 340-780M</span>
</div>
</div>
{/* Quick Interactive Layer Toggles */}
<div className="absolute bottom-2 right-2 flex items-center gap-1">
<button className="px-2 py-1 bg-surface-container-lowest/90 rounded text-primary hover:bg-surface-container-low transition-colors font-label-caps text-label-caps font-semibold shadow-xs" type="button">
          FIT VESSEL
        </button>
<button className="px-2 py-1 bg-surface-container-lowest/90 rounded text-primary hover:bg-surface-container-low transition-colors font-label-caps text-label-caps font-semibold shadow-xs" type="button">
          LAYERS
        </button>
<button className="px-2 py-1 bg-primary text-on-primary rounded font-label-caps text-label-caps font-semibold shadow-xs" type="button">
          LOW-BW
        </button>
</div>
</div>
</section>
{/* Real Telemetry & Route Metrics Grid */}
<section className="grid grid-cols-2 gap-space-sm">
{/* Distance to Go */}
<div className="bg-surface-container-lowest p-space-sm rounded-lg shadow-sm flex flex-col justify-between">
<span className="font-label-caps text-label-caps text-secondary uppercase">DISTANCE TO GO</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-lg text-telemetry-lg text-primary font-semibold">84.2</span>
<span className="font-telemetry-sm text-telemetry-sm text-secondary">NM</span>
</div>
<div className="w-full bg-surface-container-low h-1 rounded-full overflow-hidden mt-2">
<div className="bg-primary h-full w-[68%]"></div>
</div>
</div>
{/* SOG & COG */}
<div className="bg-surface-container-lowest p-space-sm rounded-lg shadow-sm flex flex-col justify-between">
<span className="font-label-caps text-label-caps text-secondary uppercase">SPEED • COURSE</span>
<div className="flex items-baseline justify-between mt-1">
<div>
<span className="font-telemetry-lg text-telemetry-lg text-primary font-semibold">11.4</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary ml-0.5">KN</span>
</div>
<div className="text-right">
<span className="font-telemetry-md text-telemetry-md text-primary font-medium">184°</span>
<span className="font-label-caps text-label-caps text-secondary block">TRUE</span>
</div>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-emerald-700 mt-2 font-medium">STABLE CRUISE</span>
</div>
{/* Closest Point of Approach (CPA) */}
<div className="bg-surface-container-lowest p-space-sm rounded-lg shadow-sm flex flex-col justify-between">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps text-secondary uppercase">CPA TARGET A-76A</span>
<span className="w-2 h-2 rounded-full bg-amber-500"></span>
</div>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-lg text-telemetry-lg text-primary font-semibold">2.84</span>
<span className="font-telemetry-sm text-telemetry-sm text-secondary">NM</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-on-surface-variant mt-2 font-medium">SAFETY BUFFER: &gt;2.0 NM</span>
</div>
{/* Time to CPA (TCPA) */}
<div className="bg-surface-container-lowest p-space-sm rounded-lg shadow-sm flex flex-col justify-between">
<span className="font-label-caps text-label-caps text-secondary uppercase">TIME TO CPA (TCPA)</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-lg text-telemetry-lg text-primary font-semibold">01:42</span>
<span className="font-telemetry-sm text-telemetry-sm text-secondary">HR:MN</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary mt-2">INTERCEPT: 16:04 UTC</span>
</div>
</section>
{/* Ice Corridor Concentration Gauge */}
<section className="bg-surface-container-lowest p-space-md rounded-lg shadow-sm">
<div className="flex items-center justify-between mb-1.5">
<span className="font-label-caps text-label-caps text-secondary uppercase">SEA-ICE CONCENTRATION (CORRIDOR)</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold">18% <span className="font-label-caps text-secondary font-normal">/ 30% LIMIT</span></span>
</div>
<div className="relative w-full h-3 bg-surface-container-low rounded-sm overflow-hidden flex">
<div className="h-full bg-primary" style={{ /* width: 18%; */ }}></div>
<div className="h-full bg-transparent border-r-2 border-dashed border-red-500" style={{ /* width: 12%; */ }}></div>
<div className="h-full bg-surface-container-highest" style={{ /* width: 70%; */ }}></div>
</div>
<div className="flex items-center justify-between mt-1.5 font-telemetry-xs text-telemetry-xs text-secondary">
<span>0% OPEN WATER</span>
<span className="text-red-700 font-medium">CRITICAL LIMIT (30%)</span>
<span>100% PACK ICE</span>
</div>
</section>
{/* Route Alternatives Operational Card */}
<section className="bg-surface-container-lowest rounded-lg p-space-md shadow-sm space-y-space-sm">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[18px] text-primary">route</span>
<h2 className="font-headline-sm text-headline-sm text-primary">Operational Route Candidates</h2>
</div>
<span className="font-label-caps text-label-caps text-secondary">RouteX16 OPT-V4</span>
</div>
{/* Active Route: Alpha-04 */}
<div className="p-space-sm rounded bg-surface-container-low flex flex-col gap-1.5 relative overflow-hidden">
<div className="absolute left-0 top-0 bottom-0 w-1 bg-primary"></div>
<div className="flex items-center justify-between">
<div className="flex items-center gap-1.5">
<span className="font-telemetry-sm text-telemetry-sm text-primary font-bold">RX16-ALPHA-04</span>
<span className="px-1.5 py-0.2 bg-primary text-on-primary rounded text-[9px] font-label-caps font-semibold tracking-wider">ACTIVE</span>
</div>
<span className="font-label-caps text-label-caps text-secondary font-medium">KINEMATIC OPTIMIZED</span>
</div>
<div className="grid grid-cols-3 gap-space-xs pt-1 text-center font-telemetry-xs text-telemetry-xs">
<div className="bg-surface-container-lowest p-1 rounded">
<span className="text-secondary block font-label-caps">FUEL</span>
<span className="font-semibold text-primary">4.8 tons</span>
</div>
<div className="bg-surface-container-lowest p-1 rounded">
<span className="text-secondary block font-label-caps">RISK INDEX</span>
<span className="font-semibold text-emerald-700">0.14 [LOW]</span>
</div>
<div className="bg-surface-container-lowest p-1 rounded">
<span className="text-secondary block font-label-caps">TOTAL NM</span>
<span className="font-semibold text-primary">142.6 NM</span>
</div>
</div>
</div>
{/* Alternative Route: Beta-02 */}
<div className="p-space-sm rounded bg-surface-container-lowest flex flex-col gap-1.5 relative">
<div className="flex items-center justify-between">
<div className="flex items-center gap-1.5">
<span className="font-telemetry-sm text-telemetry-sm text-on-surface-variant font-medium">RX16-BETA-02</span>
<span className="px-1.5 py-0.2 bg-surface-container-low text-secondary rounded text-[9px] font-label-caps font-medium tracking-wider">FEASIBLE</span>
</div>
<span className="font-label-caps text-label-caps text-secondary font-medium">STRAIT CLEARANCE OFFSET</span>
</div>
<div className="grid grid-cols-3 gap-space-xs pt-1 text-center font-telemetry-xs text-telemetry-xs">
<div className="bg-surface-container-low p-1 rounded">
<span className="text-secondary block font-label-caps">FUEL</span>
<span className="font-semibold text-primary">5.3 tons</span>
</div>
<div className="bg-surface-container-low p-1 rounded">
<span className="text-secondary block font-label-caps">RISK INDEX</span>
<span className="font-semibold text-emerald-800">0.08 [MIN]</span>
</div>
<div className="bg-surface-container-low p-1 rounded">
<span className="text-secondary block font-label-caps">TOTAL NM</span>
<span className="font-semibold text-primary">158.1 NM</span>
</div>
</div>
</div>
</section>
{/* Environmental Intelligence (CryoX Feed Status) */}
<section className="bg-surface-container-lowest rounded-lg p-space-md shadow-sm space-y-space-sm">
<div className="flex items-center justify-between">
<div className="flex items-center gap-space-xs">
<span className="material-symbols-outlined text-[18px] text-primary">sensors</span>
<h2 className="font-headline-sm text-headline-sm text-primary">CryoX Polar Ingestion Stack</h2>
</div>
<div className="flex items-center gap-1">
<span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium">SYNCHRONIZED</span>
</div>
</div>
{/* Feed Status List */}
<div className="divide-y divide-surface-container-low text-body-sm">
<div className="py-2 flex items-center justify-between">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-secondary text-[16px]">satellite_alt</span>
<span className="font-body-md text-body-md text-primary font-medium">Sentinel-1 SAR Mosaic</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">UPDATED 42m AGO • <span className="text-emerald-700 font-semibold">NOMINAL</span></span>
</div>
<div className="py-2 flex items-center justify-between">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-secondary text-[16px]">ac_unit</span>
<span className="font-body-md text-body-md text-primary font-medium">NIC Iceberg Registry</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">SYNCED • <span className="text-primary font-semibold">34 TRACKED</span></span>
</div>
<div className="py-2 flex items-center justify-between">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-secondary text-[16px]">grid_view</span>
<span className="font-body-md text-body-md text-primary font-medium">AMSR2 Sea-Ice Resolution</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">VALID • <span className="text-primary font-medium">0.05° GRID</span></span>
</div>
<div className="py-2 flex items-center justify-between">
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-secondary text-[16px]">air</span>
<span className="font-body-md text-body-md text-primary font-medium">GFS/ECMWF Polar Marine</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">24 kn SW • SEA STATE 4</span>
</div>
</div>
</section>
{/* Ice Hazard Advisory Strip */}
<div className="bg-amber-50 rounded-lg p-space-sm flex items-start gap-space-sm text-amber-900">
<span className="material-symbols-outlined text-[18px] text-amber-700 shrink-0 mt-0.5">warning</span>
<div className="flex flex-col">
<span className="font-label-caps text-label-caps uppercase tracking-wider text-amber-900 font-semibold">MARITIME ADVISORY: BERGY WATER ZONE</span>
<p className="font-body-sm text-body-sm text-amber-800 mt-0.5">
        Target IB-A76A calved fragment drift accelerated by 0.3 kn due to Katabatic gusts in Neumayer Channel approach. Maintain active sonar watch.
      </p>
</div>
</div>
</div></main><nav className="fixed bottom-0 w-full z-50 pb-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_-1px_8px_rgba(0,0,0,0.04)]" data-activeClasses="text-primary-container font-semibold bg-secondary-container/40"><div className="flex justify-around items-center h-16 px-space-xs"><a aria-current="page" className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded transition-colors text-primary-container font-semibold bg-secondary-container/40" data-path="dashboard" href="#"><span className="material-symbols-outlined text-[20px]">radar</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Dashboard</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="explorer" href="#"><span className="material-symbols-outlined text-[20px]">explore</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Explorer</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="planner" href="#"><span className="material-symbols-outlined text-[20px]">alt_route</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Planner</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="navigation" href="#"><span className="material-symbols-outlined text-[20px]">navigation</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Navigation</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="system" href="#"><span className="material-symbols-outlined text-[20px]">hub</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">System</span></a></div></nav>
    </>
  );
}
