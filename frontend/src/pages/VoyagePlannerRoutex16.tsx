import React from 'react';
import { MapComponent } from '../components/MapComponent';

import { useState } from 'react';
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

  return (
    <>
      <header className="fixed top-0 w-full z-50 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]"><div className="h-20 px-space-md flex flex-col justify-center gap-space-xs"><div className="flex items-center justify-between"><div className="flex items-center gap-space-sm"><div className="flex flex-col"><span className="font-headline-sm text-headline-sm uppercase text-primary tracking-wide">CRYOX | RouteX16</span><span className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">ANTARCTIC MARITIME COMMAND</span></div></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span><span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium tracking-tight">API: CONNECTED</span></div><div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0"><span className="material-symbols-outlined text-on-primary text-[18px]">person</span></div></div></div><div className="flex items-center justify-between"><div className="flex items-center gap-space-xs"><span className="font-headline-sm text-headline-sm text-primary">Planner</span></div><div className="flex items-center gap-space-sm"><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="font-label-caps text-label-caps text-secondary">MODE:</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-semibold">LOW-BW</span></div><div className="flex items-center gap-1 px-space-xs py-0.5 rounded bg-surface-container-low"><span className="material-symbols-outlined text-[14px] text-secondary">schedule</span><span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">14:22:08 UTC</span></div></div></div></div></header><main className="flex-1 w-full bg-surface pt-20 pb-safe"><div className="flex flex-col w-full px-space-md py-space-sm space-y-space-md">
{/* Header & Planning Mode Section */}
<div className="flex flex-col space-y-space-xs bg-surface-container-lowest p-space-md rounded-xl shadow-sm">
<div className="flex items-center justify-between">
<span className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">CRYOX OPTIMIZATION ENGINE</span>
<div className="flex items-center gap-1.5 px-space-xs py-0.5 rounded bg-surface-container-low text-secondary">
<span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium">BACKEND: READY (v1.4-polar)</span>
</div>
</div>
<div className="flex items-center justify-between pt-0.5">
<h2 className="font-headline-md text-headline-md text-primary tracking-tight">Voyage Planner &amp; RouteX16</h2>
<span className="material-symbols-outlined text-secondary text-[20px]">tune</span>
</div>
{/* Mode Selector Pills */}
<div className="grid grid-cols-3 gap-1 p-1 bg-surface-container rounded-lg mt-space-xs">
<button className="mode-tab py-1.5 px-space-xs rounded font-label-caps text-label-caps text-center transition-all bg-surface-container-lowest text-primary shadow-sm font-semibold" id="mode-safety"  type="button">
        SAFETY-FIRST
      </button>
<button className="mode-tab py-1.5 px-space-xs rounded font-label-caps text-label-caps text-center transition-all text-secondary hover:text-primary" id="mode-fuel"  type="button">
        FUEL-OPTIM
      </button>
<button className="mode-tab py-1.5 px-space-xs rounded font-label-caps text-label-caps text-center transition-all text-secondary hover:text-primary" id="mode-ice"  type="button">
        ICE-MAX PC5
      </button>
</div>
<div className="flex items-center justify-between text-secondary pt-1 px-0.5">
<span className="font-telemetry-xs text-telemetry-xs">Objective Profile: Zero Hazard Penetration</span>
<span className="font-telemetry-xs text-telemetry-xs">SIC Threshold ≤ 30%</span>
</div>
</div>
{/* Mission Configuration Form */}
<form className="flex flex-col space-y-space-md bg-surface-container-lowest p-space-md rounded-xl shadow-sm" id="voyage-form" >
<div className="flex items-center justify-between border-b border-surface-container pb-2">
<div className="flex items-center gap-1.5">
<span className="material-symbols-outlined text-secondary text-[18px]">alt_route</span>
<span className="font-label-caps text-label-caps uppercase text-primary font-semibold">Mission Waypoint Setup</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">POST /api/v1/voyage/plan</span>
</div>
{/* Origin & Destination Inputs */}
<div className="flex flex-col space-y-space-xs">
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col space-y-1">
<div className="flex justify-between items-center">
<span className="font-label-caps text-label-caps text-secondary uppercase">Origin Point (Port / Anchorage)</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary-container bg-primary-container px-1 rounded text-on-primary">WPT-ORIGIN</span>
</div>
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[16px] text-secondary">anchor</span>
<input className="bg-transparent font-body-sm text-body-sm text-primary w-full outline-none font-medium" type="text" value="King George Island (Maxwell Bay) [-62.2, -58.9]"/>
</div>
</div>
<div className="flex justify-center -my-2 z-10">
<div className="w-6 h-6 rounded-full bg-surface-container-lowest shadow-sm flex items-center justify-center text-secondary">
<span className="material-symbols-outlined text-[14px]">arrow_downward</span>
</div>
</div>
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col space-y-1">
<div className="flex justify-between items-center">
<span className="font-label-caps text-label-caps text-secondary uppercase">Destination (Polar Research Station)</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary-container bg-primary-container px-1 rounded text-on-primary">WPT-TERM</span>
</div>
<div className="flex items-center gap-2">
<span className="material-symbols-outlined text-[16px] text-secondary">flag</span>
<input className="bg-transparent font-body-sm text-body-sm text-primary w-full outline-none font-medium" type="text" value="Palmer Station, Anvers Island [-64.77, -64.05]"/>
</div>
</div>
</div>
{/* Departure & Vessel Spec Grid */}
<div className="grid grid-cols-2 gap-space-sm">
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col">
<span className="font-label-caps text-label-caps text-secondary uppercase">Departure Time</span>
<div className="flex items-center gap-1.5 mt-1">
<span className="material-symbols-outlined text-[14px] text-secondary">calendar_today</span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">2025-03-24 16:00 UTC</span>
</div>
</div>
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col">
<span className="font-label-caps text-label-caps text-secondary uppercase">Vessel Hull Spec</span>
<div className="flex items-center gap-1.5 mt-1">
<span className="material-symbols-outlined text-[14px] text-secondary">directions_boat</span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-medium truncate">R/V Polaris V (PC-5)</span>
</div>
</div>
</div>
{/* Constraints Interactive Sliders */}
<div className="flex flex-col space-y-space-sm pt-1">
<span className="font-label-caps text-label-caps text-secondary uppercase">Dynamic Safety Constraints</span>
{/* Slider 1 */}
<div className="flex flex-col space-y-1 bg-surface-container-low p-space-sm rounded-lg">
<div className="flex justify-between items-center">
<span className="font-body-sm text-body-sm text-primary">Max Sea-Ice Concentration (SIC)</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold" id="sic-val">30%</span>
</div>
<input className="w-full h-1 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary" max="60" min="10"  type="range" value="30"/>
<div className="flex justify-between text-secondary">
<span className="font-telemetry-xs text-telemetry-xs">10% Open Water</span>
<span className="font-telemetry-xs text-telemetry-xs">60% Heavy Pack</span>
</div>
</div>
{/* Slider 2 */}
<div className="flex flex-col space-y-1 bg-surface-container-low p-space-sm rounded-lg">
<div className="flex justify-between items-center">
<span className="font-body-sm text-body-sm text-primary">Min Iceberg Hazard CPA</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold" id="cpa-val">2.5 NM</span>
</div>
<input className="w-full h-1 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary" max="5.0" min="0.5"  step="0.1" type="range" value="2.5"/>
<div className="flex justify-between text-secondary">
<span className="font-telemetry-xs text-telemetry-xs">0.5 NM Close Pass</span>
<span className="font-telemetry-xs text-telemetry-xs">5.0 NM Conservative</span>
</div>
</div>
{/* Dual Metrics Grid */}
<div className="grid grid-cols-2 gap-space-sm">
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col justify-between">
<span className="font-label-caps text-label-caps text-secondary uppercase">Max Sea State Limit</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold">SS 5 (Hs 4.0m)</span>
<span className="material-symbols-outlined text-[14px] text-secondary">tsunami</span>
</div>
</div>
<div className="bg-surface-container-low p-space-sm rounded-lg flex flex-col justify-between">
<span className="font-label-caps text-label-caps text-secondary uppercase">Turn Radius Limit</span>
<div className="flex items-baseline justify-between mt-1">
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold">0.8 NM Radius</span>
<span className="material-symbols-outlined text-[14px] text-secondary">sync</span>
</div>
</div>
</div>
</div>
{/* Compute CTA Button */}
<button onClick={handlePlan} className="w-full py-2.5 px-space-md bg-primary text-on-primary rounded-lg font-headline-sm text-headline-sm flex items-center justify-center gap-2 hover:bg-primary-container transition-colors shadow-sm" id="plan-btn" type="button">
<span className="material-symbols-outlined text-[18px]">model_training</span>
<span>{loading ? "Calculating..." : "Calculate RouteX16 Alternatives"}</span>
</button>
</form>
{/* Interactive Map Preview Corridor */}
<div className="flex flex-col bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm">
<div className="p-space-sm flex items-center justify-between border-b border-surface-container">
<div className="flex items-center gap-1.5">
<span className="material-symbols-outlined text-secondary text-[16px]">map</span>
<span className="font-label-caps text-label-caps uppercase text-primary font-semibold">Corridor Vector Topology</span>
</div>
<div className="flex items-center gap-2">
<span className="font-telemetry-xs text-telemetry-xs text-secondary">SAR RADARSAT-2 / 12.5km</span>
<span className="w-2 h-2 rounded-full bg-secondary-container"></span>
</div>
</div>
{/* Geospatial Canvas Frame with SVG Vectors */}
<div className="relative w-full h-48 bg-surface-container-low overflow-hidden z-0"><MapComponent />{route?.selected_route?.geometry && <div style={{position:"absolute", top:10, left:10, zIndex:1000}}>Route Ready</div>}
{/* Bathymetric Water Background */}
<svg className="w-full h-full hidden" fill="none" viewBox="0 0 380 200" xmlns="http://www.w3.org/2000/svg">
{/* Graticule lines */}
<line stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" x1="20" x2="20" y1="0" y2="200" />
<line stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" x1="120" x2="120" y1="0" y2="200" />
<line stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" x1="220" x2="220" y1="0" y2="200" />
<line stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" x1="320" x2="320" y1="0" y2="200" />
<line stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" x1="0" x2="380" y1="60" y2="60" />
<line stroke="#CBD5E1" strokeDasharray="2 2" strokeWidth="0.5" x1="0" x2="380" y1="130" y2="130" />
{/* Landmass Shapes (Antarctic Peninsula segments) */}
<path d="M-10 170 C40 160, 60 180, 110 160 C150 145, 180 165, 230 190 L230 210 L-10 210 Z" fill="#E2E8F0" />
<path d="M280 20 C300 25, 330 15, 360 30 C370 45, 350 70, 320 60 C290 50, 275 35, 280 20 Z" fill="#E2E8F0" />
<text className="font-telemetry-xs text-[8px] fill-secondary" x="290" y="32">KGI Maxwell</text>
<path d="M40 110 C50 100, 80 105, 90 125 C85 140, 60 145, 45 130 Z" fill="#CBD5E1" />
<text className="font-telemetry-xs text-[8px] fill-secondary" x="45" y="142">Anvers Isl</text>
{/* Red Restricted High Ice Concentration Hazard Polygon (Lemaire Corridor) */}
<polygon fill="#FEE2E2" fillOpacity="0.85" points="120,80 180,70 195,110 145,125" />
<polygon fill="none" points="120,80 180,70 195,110 145,125" stroke="#EF4444" strokeDasharray="3 2" strokeWidth="1.2" />
<text className="font-label-caps text-[7.5px] fill-error font-semibold" x="135" y="98">SIC 55% RESTRICTED</text>
{/* Route 3: Infeasible Trajectory Penetrating Ice Zone (Dotted Red) */}
<path d="M305 45 Q 210 80 75 125" fill="none" stroke="#C23B38" strokeDasharray="3 3" strokeWidth="1.5" />
{/* Route 2: Feasible Alternative Beta-02 (Blue Cyan Wide Western Ocean arc) */}
<path d="M305 45 C 220 20, 110 40, 75 125" fill="none" stroke="#4B6076" strokeDasharray="4 2" strokeWidth="2" />
{/* Route 1: Selected Feasible Alpha-04 (High-contrast Navy Blue Channeling Safe Water) */}
<path d="M305 45 C 240 60, 190 55, 140 65 C 105 75, 85 95, 75 125" fill="none" stroke="#00152A" strokeWidth="2.5" />
{/* Origin Node Marker */}
<circle cx="305" cy="45" fill="#00152A" r="4" />
<circle cx="305" cy="45" fill="none" r="7" stroke="#00152A" strokeWidth="1" />
{/* Destination Node Marker */}
<circle cx="75" cy="125" fill="#1E7B68" r="4" />
<circle cx="75" cy="125" fill="none" r="7" stroke="#1E7B68" strokeWidth="1" />
</svg>
{/* Map Legend Overlay */}
<div className="absolute bottom-2 left-2 bg-surface-container-lowest/95 p-1.5 rounded flex items-center gap-3 shadow-sm">
<div className="flex items-center gap-1">
<span className="w-3 h-0.5 bg-primary"></span>
<span className="font-telemetry-xs text-telemetry-xs text-primary font-medium">RX16-ALPHA</span>
</div>
<div className="flex items-center gap-1">
<span className="w-3 h-0.5 bg-secondary border-t border-dashed"></span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary font-medium">RX16-BETA</span>
</div>
<div className="flex items-center gap-1">
<span className="w-2.5 h-2.5 bg-error-container/50 border border-error"></span>
<span className="font-telemetry-xs text-telemetry-xs text-error font-medium">&gt;30% Pack</span>
</div>
</div>
</div>
</div>
{/* Route Alternatives Results (Backend Feasibility Schema) */}
<div className="flex flex-col space-y-space-sm">
<div className="flex items-center justify-between px-0.5">
<span className="font-label-caps text-label-caps uppercase text-secondary tracking-wider">Generated Route Feasibility (3)</span>
<span className="font-telemetry-xs text-telemetry-xs text-secondary">A* Bathymetric Solver</span>
</div>
{/* CARD 1: Selected & Feasible */}
<div className="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col space-y-space-sm">
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-primary">ROUTE 1 — RX16-ALPHA-04</span>
</div>
<span className="font-label-caps text-label-caps text-secondary mt-0.5">ENGINE: MULTI-OBJECTIVE A* + BATHYMETRIC CONSTRAINTS</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded font-semibold tracking-tight">SELECTED &amp; FEASIBLE</span>
</div>
{/* Telemetry Matrix */}
<div className="grid grid-cols-4 gap-1.5 py-1">
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">TRANSIT</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">18h 45m</span>
</div>
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">LENGTH</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">164.2 NM</span>
</div>
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">EST. FUEL</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">4.82 MT</span>
</div>
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">MIN CPA</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">2.84 NM</span>
</div>
</div>
{/* Risk and Compliance Index */}
<div className="flex items-center justify-between text-secondary pt-0.5">
<div className="flex items-center gap-1">
<span className="material-symbols-outlined text-[14px] text-emerald-700">verified_user</span>
<span className="font-telemetry-xs text-telemetry-xs">Env Risk: <strong className="text-primary font-semibold">0.12 (Low)</strong></span>
</div>
<div className="flex items-center gap-1">
<span className="font-telemetry-xs text-telemetry-xs">Constraint Violations: <strong className="text-primary font-semibold">0</strong></span>
</div>
</div>
{/* Action */}
<button className="w-full py-2 bg-primary text-on-primary rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-1.5 hover:bg-primary-container transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">navigation</span>
<span>Active on Bridge Navigation</span>
</button>
</div>
{/* CARD 2: Feasible Alternative */}
<div className="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col space-y-space-sm opacity-95">
<div className="flex items-start justify-between">
<div className="flex flex-col">
<div className="flex items-center gap-1.5">
<span className="font-headline-sm text-headline-sm text-primary">ROUTE 2 — RX16-BETA-02</span>
</div>
<span className="font-label-caps text-label-caps text-secondary mt-0.5">PROFILE: WIDE WESTERN DRAKE CLEARANCE</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs bg-surface-container text-secondary px-2 py-0.5 rounded font-medium">FEASIBLE ALTERNATIVE</span>
</div>
{/* Telemetry Matrix */}
<div className="grid grid-cols-4 gap-1.5 py-1">
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">TRANSIT</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">20h 10m</span>
</div>
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">LENGTH</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">178.6 NM</span>
</div>
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">EST. FUEL</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">5.31 MT</span>
</div>
<div className="bg-surface-container-low p-1.5 rounded flex flex-col">
<span className="font-label-caps text-[9px] text-secondary">MIN CPA</span>
<span className="font-telemetry-sm text-telemetry-sm text-primary font-semibold mt-0.5">5.10 NM</span>
</div>
</div>
{/* Risk Footprint */}
<div className="flex items-center justify-between text-secondary pt-0.5">
<div className="flex items-center gap-1">
<span className="material-symbols-outlined text-[14px] text-emerald-700">shield</span>
<span className="font-telemetry-xs text-telemetry-xs">Env Risk: <strong className="text-primary font-semibold">0.06 (Minimal)</strong></span>
</div>
<div className="flex items-center gap-1">
<span className="font-telemetry-xs text-telemetry-xs">Violations: <strong className="text-primary font-semibold">0</strong></span>
</div>
</div>
{/* Action */}
<button className="w-full py-2 bg-surface-container-low text-primary rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-1.5 hover:bg-surface-container transition-colors" type="button">
<span className="material-symbols-outlined text-[16px]">compare_arrows</span>
<span>Compare Track on Map</span>
</button>
</div>
{/* CARD 3: Infeasible Route Rejected by Engine */}
<div className="bg-error-container/20 p-space-md rounded-xl shadow-sm flex flex-col space-y-space-xs">
<div className="flex items-start justify-between">
<div className="flex flex-col">
<span className="font-headline-sm text-headline-sm text-error">ROUTE 3 — DIRECT-COASTAL</span>
<span className="font-label-caps text-label-caps text-on-error-container mt-0.5">LEMAIRE CHANNEL INSHORE PASS</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs bg-error-container text-on-error-container px-2 py-0.5 rounded font-bold">INFEASIBLE</span>
</div>
<div className="bg-surface-container-lowest p-2 rounded flex flex-col space-y-1">
<div className="flex items-center gap-1.5 text-error">
<span className="material-symbols-outlined text-[16px]">warning</span>
<span className="font-telemetry-xs text-telemetry-xs font-semibold">CONSTRAINT VIOLATION:</span>
</div>
<p className="font-body-sm text-body-sm text-primary">
          Sea-Ice Concentration exceeds 30% in Lemaire Channel (Observed 55% multispectral SAR). Hull structural stress prediction exceeds PC-5 threshold.
        </p>
</div>
<div className="flex items-center justify-between text-secondary pt-1 px-1">
<span className="font-telemetry-xs text-telemetry-xs">Calculated Hazard Risk: <strong className="text-error font-semibold">0.78 (Severe)</strong></span>
<span className="font-telemetry-xs text-telemetry-xs text-error font-medium">REJECTED BY SAFETY FILTER</span>
</div>
</div>
</div>
{/* Operational Footer Context Notice */}
<div className="p-space-sm bg-surface-container-low rounded-lg flex items-center justify-between text-secondary">
<div className="flex items-center gap-1.5">
<span className="material-symbols-outlined text-[16px]">info</span>
<span className="font-telemetry-xs text-telemetry-xs">IHO Polar Code Chapter 11 Compliance Verified</span>
</div>
<span className="font-telemetry-xs text-telemetry-xs">SOLAS V/34</span>
</div>
</div>
</main><nav className="fixed bottom-0 w-full z-50 pb-safe bg-surface-container-lowest/90 backdrop-blur-xl shadow-[0_-1px_8px_rgba(0,0,0,0.04)]" data-activeClasses="text-primary-container font-semibold bg-secondary-container/40"><div className="flex justify-around items-center h-16 px-space-xs"><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="dashboard" href="#"><span className="material-symbols-outlined text-[20px]">radar</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Dashboard</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="explorer" href="#"><span className="material-symbols-outlined text-[20px]">explore</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Explorer</span></a><a aria-current="page" className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded transition-colors text-primary-container font-semibold bg-secondary-container/40" data-path="planner" href="#"><span className="material-symbols-outlined text-[20px]">alt_route</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Planner</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="navigation" href="#"><span className="material-symbols-outlined text-[20px]">navigation</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">Navigation</span></a><a className="flex flex-col items-center justify-center min-w-[56px] h-12 px-space-xs rounded text-secondary hover:text-primary transition-colors" data-path="system" href="#"><span className="material-symbols-outlined text-[20px]">hub</span><span className="font-label-caps text-label-caps mt-0.5 uppercase tracking-tight">System</span></a></div></nav>
    </>
  );
}
