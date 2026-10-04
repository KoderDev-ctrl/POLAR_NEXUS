import React, { useState, useEffect, useRef } from 'react';
import { MapComponent } from '../components/MapComponent';
import { planVoyage, fetchHazard } from '../api/client';
import { Polyline, CircleMarker, Polygon, Marker } from 'react-leaflet';
import { demoRouteAlternatives, demoRouteAlternativesFallback } from '../demo/prototypeData';
import L from 'leaflet';
import { useChatbotStore } from '../store/chatbotStore';

const vesselIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color:#1E40AF; width:16px; height:16px; border-radius:50%; border:2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8]
});

const getInterpolatedPoint = (geometry: number[][], progress: number) => {
  if (!geometry || geometry.length === 0) return null;
  if (progress <= 0) return geometry[0];
  if (progress >= 1) return geometry[geometry.length - 1];
  
  let totalLength = 0;
  const segments = [];
  for(let i=0; i<geometry.length-1; i++) {
    const p1 = geometry[i];
    const p2 = geometry[i+1];
    // Simple euclidian for demo interpolation is fine for small segments
    const dist = Math.hypot(p2[0]-p1[0], p2[1]-p1[1]);
    totalLength += dist;
    segments.push({dist, p1, p2});
  }
  
  const targetDist = totalLength * progress;
  let currentDist = 0;
  for(const seg of segments) {
    if (currentDist + seg.dist >= targetDist) {
      const segProgress = seg.dist === 0 ? 0 : (targetDist - currentDist) / seg.dist;
      return [
        seg.p1[0] + (seg.p2[0] - seg.p1[0]) * segProgress,
        seg.p1[1] + (seg.p2[1] - seg.p1[1]) * segProgress,
      ];
    }
    currentDist += seg.dist;
  }
  return geometry[geometry.length - 1];
};

export default function VoyagePlannerRoutex16() {
  const [origin, setOrigin] = useState('-62.2, -58.9');
  const [destination, setDestination] = useState('-64.77, -64.05');
  const [icebergId, setIcebergId] = useState('a23a');
  
  const [vesselSpeed, setVesselSpeed] = useState('12');
  const [fuelCapacity, setFuelCapacity] = useState('5000');
  const [fuelConsumption, setFuelConsumption] = useState('250');
  const [fuelCost, setFuelCost] = useState('1.5');
  
  const [routes, setRoutes] = useState<any[]>([]);
  const [selectedRouteIdx, setSelectedRouteIdx] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hazard, setHazard] = useState<any>(null);

  const [isAnimating, setIsAnimating] = useState(false);
  const [animProgress, setAnimProgress] = useState(0);

  const updateChatContext = useChatbotStore(state => state.updateContext);

  useEffect(() => {
    let currentPos = null;
    if (routes[selectedRouteIdx] && routes[selectedRouteIdx].geometry) {
      currentPos = isAnimating || animProgress > 0 
        ? getInterpolatedPoint(routes[selectedRouteIdx].geometry, animProgress)
        : routes[selectedRouteIdx].geometry[0];
    }
    
    updateChatContext({
      iceberg_id: icebergId,
      vessel_speed: parseFloat(vesselSpeed || '0'),
      vessel_position: currentPos ? { lat: currentPos[0], lon: currentPos[1] } : undefined,
      candidate_routes: routes,
      selected_route: routes[selectedRouteIdx] || null,
      hazard: hazard,
      navigation_status: isAnimating ? 'Voyage in progress' : 'Planning phase'
    });
  }, [routes, selectedRouteIdx, hazard, icebergId, vesselSpeed, isAnimating, animProgress]);

  useEffect(() => {
    let frame: number;
    if (isAnimating && routes[selectedRouteIdx]) {
      const route = routes[selectedRouteIdx];
      // 1 hour = 100ms in simulation speed
      const totalHours = route.distance_nm / parseFloat(vesselSpeed || '12');
      const simulationDurationMs = Math.max(2000, totalHours * 100); 
      const startTime = performance.now();
      
      const animate = (time: number) => {
        const elapsed = time - startTime;
        const p = Math.min(1, elapsed / simulationDurationMs);
        setAnimProgress(p);
        if (p < 1) {
          frame = requestAnimationFrame(animate);
        } else {
          setIsAnimating(false);
        }
      };
      frame = requestAnimationFrame(animate);
    }
    return () => cancelAnimationFrame(frame);
  }, [isAnimating, routes, selectedRouteIdx, vesselSpeed]);

  const handlePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRoutes([]);
    setHazard(null);
    setIsAnimating(false);
    setAnimProgress(0);
    setSelectedRouteIdx(0);
    
    try {
      const origCoords = origin.split(',').map(s => parseFloat(s.trim()));
      const destCoords = destination.split(',').map(s => parseFloat(s.trim()));
      
      const voyageReq = planVoyage({
        origin: origCoords,
        destination: destCoords,
        departure_time_utc: new Date().toISOString(),
        vessel: { max_ice_concentration: 30, draft: 10, depth_clearance: 2 },
        mode: 'replay',
        iceberg_id: icebergId || undefined
      });
      const hazardReq = icebergId ? fetchHazard(icebergId, 'replay') : Promise.resolve(null);
      const [res, haz] = await Promise.all([voyageReq, hazardReq]);
      
      let finalRoutes = [];
      if (res && res.status === 'SUCCESS' && res.selected_route) {
        finalRoutes = demoRouteAlternatives(res.selected_route, origCoords, destCoords);
      } else {
        // PROTOTYPE DEMO DATA FALLBACK
        finalRoutes = demoRouteAlternativesFallback(origCoords, destCoords);
      }
      setRoutes(finalRoutes);
      
      if (haz && haz.status === 'SUCCESS') {
        setHazard(haz);
      } else if (icebergId) {
        // Fallback hazard
        import('../demo/prototypeData').then(m => setHazard(m.demoHazardFallback));
      }
    } catch (err) {
      // PROTOTYPE DEMO DATA FALLBACK on network error
      const origCoords = origin.split(',').map(s => parseFloat(s.trim()));
      const destCoords = destination.split(',').map(s => parseFloat(s.trim()));
      setRoutes(demoRouteAlternativesFallback(origCoords, destCoords));
      if (icebergId) import('../demo/prototypeData').then(m => setHazard(m.demoHazardFallback));
    } finally {
      setLoading(false);
    }
  };

  const selRoute = routes[selectedRouteIdx];
  const vesselPos = isAnimating || animProgress > 0 
    ? getInterpolatedPoint(selRoute?.geometry, animProgress) 
    : (selRoute?.geometry?.[0] || null);
    
  // Economic estimates
  const estTotalHours = selRoute ? selRoute.distance_nm / parseFloat(vesselSpeed || '12') : 0;
  const currentHours = estTotalHours * animProgress;
  const remHours = estTotalHours - currentHours;
  const remDist = selRoute ? selRoute.distance_nm * (1 - animProgress) : 0;
  const fuelUsed = currentHours * parseFloat(fuelConsumption || '250');
  const fuelRem = parseFloat(fuelCapacity || '5000') - fuelUsed;
  const estCost = estTotalHours * parseFloat(fuelConsumption || '250') * parseFloat(fuelCost || '0');

  return (
    <main className="w-full min-h-[calc(100vh-64px)] p-4 md:p-8 bg-surface flex justify-center">
      <div className="max-w-[1400px] w-full flex flex-col w-full h-full bg-surface shadow-sm rounded-2xl border border-surface-variant p-6 space-y-6">
        <div className="flex items-center gap-2 border-b border-surface-variant pb-4">
          <span className="material-symbols-outlined text-primary text-[28px]">alt_route</span>
          <h2 className="font-headline-lg text-primary uppercase tracking-wide text-2xl">Vessel Navigation</h2>
        </div>

      <form onSubmit={handlePlan} className="flex flex-col space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex flex-col space-y-2">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Origin (Lat, Lon)</label>
            <input type="text" value={origin} onChange={e => setOrigin(e.target.value)} className="bg-surface-container-low border border-surface-variant rounded p-2.5 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" required />
          </div>
          <div className="flex flex-col space-y-2">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Destination (Lat, Lon)</label>
            <input type="text" value={destination} onChange={e => setDestination(e.target.value)} className="bg-surface-container-low border border-surface-variant rounded p-2.5 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" required />
          </div>
          <div className="flex flex-col space-y-2">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Departure Time (UTC)</label>
            <input type="datetime-local" className="bg-surface-container-low border border-surface-variant rounded p-2.5 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" />
          </div>
          <div className="flex flex-col space-y-2">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Iceberg ID (Optional)</label>
            <input type="text" value={icebergId} onChange={e => setIcebergId(e.target.value)} className="bg-surface-container-low border border-surface-variant rounded p-2.5 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" />
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-surface-container-lowest p-4 rounded-lg border border-surface-variant">
          <div className="flex flex-col space-y-1">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Vessel Speed (kn)</label>
            <input type="number" value={vesselSpeed} onChange={e => setVesselSpeed(e.target.value)} className="bg-transparent border-b border-surface-variant p-1 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" />
          </div>
          <div className="flex flex-col space-y-1">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Fuel Cap. (L)</label>
            <input type="number" value={fuelCapacity} onChange={e => setFuelCapacity(e.target.value)} className="bg-transparent border-b border-surface-variant p-1 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" />
          </div>
          <div className="flex flex-col space-y-1">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Fuel Burn (L/h)</label>
            <input type="number" value={fuelConsumption} onChange={e => setFuelConsumption(e.target.value)} className="bg-transparent border-b border-surface-variant p-1 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" />
          </div>
          <div className="flex flex-col space-y-1">
            <label className="font-label-caps text-[10px] uppercase text-secondary">Cost ($/L)</label>
            <input type="number" step="0.1" value={fuelCost} onChange={e => setFuelCost(e.target.value)} className="bg-transparent border-b border-surface-variant p-1 font-telemetry-sm text-primary text-sm focus:outline-none focus:border-primary" />
          </div>
        </div>

        <button type="submit" disabled={loading} className="w-full md:w-64 bg-primary text-on-primary hover:bg-[#17324D] py-3 px-6 rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-2 shadow-sm transition-colors mt-2 disabled:opacity-50">
          <span className="material-symbols-outlined text-[20px]">explore</span>
          {loading ? "Planning..." : "Plan Voyage"}
        </button>
      </form>

      {error && (
        <div className="bg-error-container/20 border border-error/30 p-4 rounded-lg flex items-center gap-3">
          <span className="material-symbols-outlined text-error">warning</span>
          <p className="font-body-md text-error-800">{error}</p>
        </div>
      )}

      {routes.length > 0 && (
        <div className="flex flex-col space-y-6 pt-4 border-t border-surface-variant">
          <h3 className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">Route Alternatives</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {routes.map((rt, idx) => (
              <div 
                key={rt.route_id} 
                onClick={() => { if (!isAnimating) { setSelectedRouteIdx(idx); setAnimProgress(0); } }}
                className={`flex flex-col p-4 rounded-xl border cursor-pointer transition-all ${selectedRouteIdx === idx ? 'border-primary ring-2 ring-primary/20 shadow-md' : 'border-surface-variant hover:border-primary/50'} ${!rt.feasible ? 'bg-error-container/10 border-error/30' : 'bg-surface-container-lowest'}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`font-label-caps font-bold ${!rt.feasible ? 'text-error' : 'text-primary'}`}>{rt.route_id}</span>
                  {!rt.feasible && <span className="material-symbols-outlined text-error text-[18px]">warning</span>}
                </div>
                {!rt.feasible && (
                  <span className="text-[10px] text-error font-bold mb-2 leading-tight uppercase">NOT FEASIBLE: {rt.violation_reason}</span>
                )}
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-secondary">Distance</span>
                  <span className="font-telemetry-sm text-primary">{rt.distance_nm.toFixed(1)} NM</span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-secondary">Est. Time</span>
                  <span className="font-telemetry-sm text-primary">{(rt.distance_nm / parseFloat(vesselSpeed || '12')).toFixed(1)} h</span>
                </div>
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-secondary">Est. Cost</span>
                  <span className="font-telemetry-sm text-emerald-600 font-bold">${((rt.distance_nm / parseFloat(vesselSpeed || '12')) * parseFloat(fuelConsumption) * parseFloat(fuelCost)).toFixed(0)}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            <div className="flex-1 min-h-[500px] rounded-xl overflow-hidden border border-surface-variant relative z-0">
              <MapComponent center={selRoute.geometry[Math.floor(selRoute.geometry.length / 2)] || [-63.5, -61.0]} zoom={6}>
                {/* Render Unselected Routes */}
                {routes.map((rt, idx) => {
                  if (idx === selectedRouteIdx) return null;
                  const routeColors = ['#0284C7', '#059669', '#F97316', '#9333EA'];
                  const color = rt.feasible ? routeColors[idx % 4] : '#EF4444';
                  return (
                    <Polyline 
                      key={rt.route_id} 
                      positions={rt.geometry} 
                      color={color} 
                      weight={2} 
                      opacity={0.4} 
                      dashArray={rt.feasible ? '' : '5,5'}
                    />
                  );
                })}

                {/* Selected Route */}
                <Polyline 
                  positions={selRoute.geometry} 
                  color={selRoute.feasible ? ['#0284C7', '#059669', '#F97316', '#9333EA'][selectedRouteIdx % 4] : '#EF4444'} 
                  weight={5} 
                  opacity={1}
                />

                {/* Start and End Markers */}
                {selRoute.geometry.length > 0 && (
                  <>
                    <CircleMarker center={selRoute.geometry[0]} color="white" fillColor="#059669" fillOpacity={1} weight={2} radius={5} />
                    <CircleMarker center={selRoute.geometry[selRoute.geometry.length - 1]} color="white" fillColor="#059669" fillOpacity={1} weight={2} radius={5} />
                  </>
                )}
                
                {/* Hazard Visualizations */}
                {hazard && hazard.envelope && hazard.envelope.length > 0 && (
                  <Polygon positions={hazard.envelope} color="orange" weight={1} fillColor="orange" fillOpacity={0.2} />
                )}
                {hazard && hazard.points && hazard.points.length > 1 && (
                  <Polyline positions={hazard.points.map((p: any) => [p.lat, p.lon])} color="orange" weight={3} />
                )}
                {hazard && hazard.points?.map((pt: any, i: number) => (
                  <CircleMarker key={pt.role} center={[pt.lat, pt.lon]} color={i === 0 ? 'red' : 'orange'} fillColor={i === 0 ? 'red' : 'orange'} fillOpacity={1} radius={5} />
                ))}

                {/* Vessel Marker */}
                {vesselPos && (
                  <Marker position={[vesselPos[0], vesselPos[1]]} icon={vesselIcon} />
                )}
              </MapComponent>
            </div>
            
            {/* Playback & Telemetry Panel */}
            <div className="w-full lg:w-80 flex flex-col gap-4">
              <div className="bg-surface-container-low p-5 rounded-xl border border-surface-variant flex flex-col gap-4">
                <button 
                  onClick={() => {
                    if (isAnimating) { setIsAnimating(false); }
                    else {
                      if (animProgress >= 1) setAnimProgress(0);
                      setIsAnimating(true);
                    }
                  }}
                  disabled={!selRoute.feasible}
                  className="w-full bg-[#1E40AF] text-white hover:bg-[#1e3a8a] py-3 rounded font-label-caps text-sm tracking-wider flex items-center justify-center gap-2 shadow disabled:opacity-50"
                >
                  <span className="material-symbols-outlined">{isAnimating ? 'pause' : 'play_arrow'}</span>
                  {isAnimating ? 'PAUSE VOYAGE' : 'START VOYAGE'}
                </button>
                {!selRoute.feasible && <span className="text-error text-xs text-center">Cannot start infeasible route</span>}
                <div className="flex flex-col gap-1 mt-2">
                  <span className="font-label-caps text-[10px] text-secondary">VOYAGE PROGRESS</span>
                  <div className="w-full h-2 bg-surface-variant rounded-full overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${animProgress * 100}%` }}></div>
                  </div>
                </div>
              </div>

              <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-variant flex flex-col gap-4 shadow-sm">
                <h4 className="font-label-caps text-label-caps uppercase text-secondary tracking-widest border-b border-surface-variant pb-2">Live Telemetry</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-secondary uppercase">Speed</span>
                    <span className="font-telemetry-md text-primary font-bold">{vesselSpeed} kn</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-secondary uppercase">Dist. Rem</span>
                    <span className="font-telemetry-md text-primary font-bold">{remDist.toFixed(1)} NM</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-secondary uppercase">Time Rem</span>
                    <span className="font-telemetry-md text-primary font-bold">{remHours.toFixed(1)} h</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-secondary uppercase">Fuel Rem</span>
                    <span className={`font-telemetry-md font-bold ${fuelRem < 0 ? 'text-error' : 'text-primary'}`}>{fuelRem.toFixed(0)} L</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center mt-2 p-3 bg-surface-container-low rounded">
                  <span className="text-xs font-bold text-secondary uppercase">Fuel Used</span>
                  <span className="font-telemetry-md text-emerald-600 font-bold">{fuelUsed.toFixed(0)} L</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </main>
  );
}
