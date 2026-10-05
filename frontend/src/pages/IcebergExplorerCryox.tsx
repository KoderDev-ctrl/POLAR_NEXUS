import React, { useState, useEffect } from 'react';
import { MapComponent } from '../components/MapComponent';
import { fetchIcebergs, fetchIcebergTrajectory } from '../api/client';
import { CircleMarker, Polyline, Polygon, useMap, Tooltip } from 'react-leaflet';

// Component to handle auto-panning the map when an iceberg is selected
function MapController({ selectedCoords }: { selectedCoords: [number, number] | null }) {
  const map = useMap();
  useEffect(() => {
    if (selectedCoords) {
      map.flyTo(selectedCoords, 7, { animate: true, duration: 1 });
    }
  }, [selectedCoords, map]);
  return null;
}

export default function IcebergExplorerCryox() {
  const [icebergs, setIcebergs] = useState<any[]>([]);
  const [icebergId, setIcebergId] = useState('');
  const [trajectoryData, setTrajectoryData] = useState<any>(null);
  
  const [loading, setLoading] = useState(true);
  const [loadingTrajectory, setLoadingTrajectory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load all icebergs on mount
  useEffect(() => {
    const loadIcebergs = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchIcebergs();
        if (res && res.icebergs) {
          setIcebergs(res.icebergs);
        }
      } catch (err) {
        // Fallback for demo
        import('../demo/prototypeData').then((m: any) => {
          if (m.demoIcebergsFallback) {
             setIcebergs(m.demoIcebergsFallback);
             setIcebergs(m.demoIcebergsFallback || []);
          }
        }).catch(() => setError("Failed to load icebergs"));
      } finally {
        setLoading(false);
      }
    };
    loadIcebergs();
  }, []);

  // When selected iceberg changes, load its trajectory
  useEffect(() => {
    if (!icebergId) {
      setTrajectoryData(null);
      return;
    }
    
    const loadTrajectory = async () => {
      setLoadingTrajectory(true);
      try {
        const res = await fetchIcebergTrajectory(icebergId);
        setTrajectoryData(res);
      } catch (err) {
        // Fallback demo hazard
        import('../demo/prototypeData').then(m => {
          setTrajectoryData((prev: any) => {
            const selected = icebergs.find(i => i.id === icebergId);
            if (selected && m.getDemoHazardFallback) {
              return {
                id: icebergId,
                historical: [
                  { latitude: selected.latitude - 0.05, longitude: selected.longitude - 0.05, observedAt: '2025-12-30T12:00:00Z' },
                  { latitude: selected.latitude, longitude: selected.longitude, observedAt: '2025-12-31T00:00:00Z' }
                ],
                hazard_assessment: m.getDemoHazardFallback(icebergId, selected.latitude, selected.longitude),
                status: 'REPLAY'
              };
            }
            return {
              id: icebergId,
              historical: [],
              hazard_assessment: m.demoHazardFallback,
              status: 'REPLAY'
            };
          });
        });
      } finally {
        setLoadingTrajectory(false);
      }
    };
    loadTrajectory();
  }, [icebergId]);

  const handleSelectIceberg = (id: string) => {
    if (id !== icebergId) {
      setIcebergId(id);
    }
  };

  const selectedIceberg = icebergs.find(i => i.id === icebergId);
  const selectedCoords: [number, number] | null = selectedIceberg ? [selectedIceberg.latitude, selectedIceberg.longitude] : null;

  return (
    <main className="w-full min-h-[calc(100vh-64px)] p-4 md:p-8 bg-surface flex justify-center">
      <div className="max-w-[1400px] w-full flex flex-col h-full bg-surface shadow-sm rounded-2xl border border-surface-variant p-6 space-y-6">
        <div className="flex items-center gap-2 border-b border-surface-variant pb-4">
          <span className="material-symbols-outlined text-primary text-[28px]">search</span>
          <h2 className="font-headline-lg text-primary uppercase tracking-wide text-2xl">Iceberg Tracking</h2>
        </div>

        {error && (
          <div className="bg-error-container/20 border border-error/30 p-4 rounded-lg flex items-center gap-3">
            <span className="material-symbols-outlined text-error">warning</span>
            <p className="font-body-md text-error-800">{error}</p>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Map Area */}
          <div className="flex-1 flex flex-col space-y-4">
            
            {/* Searchable Dropdown */}
            <div className="flex flex-col space-y-2">
              <label className="font-label-caps text-label-caps uppercase text-secondary">Select Iceberg</label>
              <div className="relative">
                <select 
                  value={icebergId}
                  onChange={(e) => handleSelectIceberg(e.target.value)}
                  className="w-full bg-surface-container-low border border-surface-variant rounded p-3 font-telemetry-sm text-primary focus:outline-none focus:border-primary appearance-none cursor-pointer"
                  disabled={loading}
                >
                  <option value="">{loading ? "Loading icebergs..." : "-- Select an Iceberg --"}</option>
                  {icebergs.map(ice => (
                    <option key={ice.id} value={ice.id}>
                      Iceberg {ice.id.toUpperCase()} 
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-secondary">
                  <span className="material-symbols-outlined text-[20px]">expand_more</span>
                </div>
              </div>
            </div>

            {/* Map */}
            <div className="w-full h-[600px] rounded-xl overflow-hidden border border-surface-variant relative z-0">
              {icebergs.length > 0 && (
                <MapComponent center={[-64.5, -63.2]} zoom={5}>
                  <MapController selectedCoords={selectedCoords} />
                  
                  {/* Trajectory / Hazard for selected iceberg */}
                  {trajectoryData && trajectoryData.hazard_assessment && trajectoryData.hazard_assessment.envelope && (
                    <Polygon positions={trajectoryData.hazard_assessment.envelope} color="#eab308" weight={2} fillColor="#eab308" fillOpacity={0.2} />
                  )}
                  {trajectoryData && trajectoryData.historical && trajectoryData.historical.length > 1 && (
                    <Polyline positions={trajectoryData.historical.map((p: any) => [p.latitude, p.longitude])} color="#475569" weight={2} opacity={0.6} />
                  )}
                  {trajectoryData && trajectoryData.hazard_assessment && trajectoryData.hazard_assessment.points && (
                    <Polyline positions={trajectoryData.hazard_assessment.points.map((p: any) => [p.lat, p.lon])} color="#ef4444" weight={3} />
                  )}
                  {trajectoryData && trajectoryData.hazard_assessment && trajectoryData.hazard_assessment.points && (
                    trajectoryData.hazard_assessment.points.map((pt: any, i: number) => (
                      <CircleMarker 
                        key={`pred_${i}`}
                        center={[pt.lat, pt.lon]} 
                        color={'#ef4444'}
                        fillColor={'#ef4444'}
                        fillOpacity={1}
                        radius={5} 
                      >
                        <Tooltip>
                          <div className="font-telemetry-sm text-xs">
                            <strong className="block text-primary">{pt.role}</strong>
                            <span>Lat: {pt.lat?.toFixed(4)}°</span><br/>
                            <span>Lon: {pt.lon?.toFixed(4)}°</span><br/>
                            <span>Valid: +{pt.horizon_h}h</span>
                          </div>
                        </Tooltip>
                      </CircleMarker>
                    ))
                  )}

                  {/* Render all icebergs as lightweight markers */}
                  {icebergs.map(ice => {
                    const isSelected = ice.id === icebergId;
                    return (
                      <CircleMarker
                        key={ice.id}
                        center={[ice.latitude, ice.longitude]}
                        radius={isSelected ? 8 : 4}
                        color={isSelected ? '#ef4444' : '#1d4ed8'}
                        fillColor={isSelected ? '#ef4444' : '#3b82f6'}
                        fillOpacity={isSelected ? 1 : 0.6}
                        weight={isSelected ? 3 : 1}
                        eventHandlers={{
                          click: () => handleSelectIceberg(ice.id)
                        }}
                        className="cursor-pointer"
                      />
                    );
                  })}
                </MapComponent>
              )}
            </div>
            
            <div className="flex flex-col gap-2 mb-2">
              <h4 className="font-label-caps text-label-caps uppercase text-secondary">Map Legend</h4>
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-blue-500"></span><span className="font-telemetry-xs text-secondary">Observed Iceberg</span></div>
                <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-500 border border-red-600"></span><span className="font-telemetry-xs text-primary font-bold">Selected / Prediction Point</span></div>
                <div className="flex items-center gap-1.5"><span className="w-4 h-0.5 bg-slate-600"></span><span className="font-telemetry-xs text-secondary">Historical Track</span></div>
                <div className="flex items-center gap-1.5"><span className="w-4 h-0.5 bg-red-500"></span><span className="font-telemetry-xs text-secondary">Prediction Trajectory</span></div>
                <div className="flex items-center gap-1.5"><span className="w-4 h-4 bg-yellow-500/20 border border-yellow-500/50"></span><span className="font-telemetry-xs text-secondary">Hazard Envelope</span></div>
              </div>
            </div>
          </div>

          {/* Side Info Panel */}
          <div className="w-full lg:w-80 flex flex-col space-y-4">
            <h3 className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">Iceberg Details</h3>
            
            {icebergId ? (
              <div className="bg-surface-container-low rounded-xl border border-surface-variant p-4 flex flex-col space-y-4 shadow-sm h-full">
                <div className="flex justify-between items-start">
                  <h4 className="font-headline-sm text-primary text-xl uppercase tracking-wider">{icebergId}</h4>
                  {selectedIceberg?.status === 'REPLAY' || selectedIceberg?.source === 'DEMO/REPLAY' ? (
                    <span className="bg-amber-100 text-amber-800 font-telemetry-xs px-2 py-1 rounded-sm tracking-widest uppercase">DEMO DATA</span>
                  ) : (
                    <span className="bg-emerald-100 text-emerald-800 font-telemetry-xs px-2 py-1 rounded-sm tracking-widest uppercase">LIVE</span>
                  )}
                </div>
                
                <div className="flex flex-col space-y-3">
                  <div className="flex justify-between border-b border-surface-variant pb-2">
                    <span className="text-xs text-secondary font-label-caps uppercase">Source</span>
                    <span className="font-telemetry-sm text-primary text-xs text-right max-w-[120px] truncate">{selectedIceberg?.source || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between border-b border-surface-variant pb-2">
                    <span className="text-xs text-secondary font-label-caps uppercase">Last Lat</span>
                    <span className="font-telemetry-sm text-primary text-sm">{selectedIceberg?.latitude?.toFixed(4) || 'N/A'}°</span>
                  </div>
                  <div className="flex justify-between border-b border-surface-variant pb-2">
                    <span className="text-xs text-secondary font-label-caps uppercase">Last Lon</span>
                    <span className="font-telemetry-sm text-primary text-sm">{selectedIceberg?.longitude?.toFixed(4) || 'N/A'}°</span>
                  </div>
                  <div className="flex justify-between border-b border-surface-variant pb-2">
                    <span className="text-xs text-secondary font-label-caps uppercase">Observed</span>
                    <span className="font-telemetry-sm text-primary text-xs">{selectedIceberg?.observedAt ? new Date(selectedIceberg.observedAt).toLocaleString() : 'N/A'}</span>
                  </div>
                </div>

                {loadingTrajectory ? (
                  <div className="flex items-center justify-center p-6 text-secondary animate-pulse">
                    <span className="font-telemetry-sm text-xs">Loading trajectory...</span>
                  </div>
                ) : (
                  trajectoryData && trajectoryData.hazard_assessment && trajectoryData.hazard_assessment.points && (
                    <div className="mt-4 flex flex-col space-y-4">
                      <h4 className="font-label-caps text-[10px] uppercase text-secondary tracking-widest bg-surface-variant px-2 py-1 rounded-sm">Operational Models</h4>
                      <div className="flex flex-col space-y-3">
                        {trajectoryData.hazard_assessment.points.map((pt: any, idx: number) => (
                          <div key={pt.role} className="flex flex-col text-xs border-b border-surface-variant/50 pb-2 last:border-0 last:pb-0">
                            <div className="flex justify-between items-center mb-1">
                              <span className="font-telemetry-sm font-bold text-primary">{pt.role}</span>
                              <span className="font-telemetry-sm text-secondary">+{pt.horizon_h}h</span>
                            </div>
                            <span className="font-telemetry-sm text-secondary">{pt.lat?.toFixed(4)}°, {pt.lon?.toFixed(4)}°</span>
                          </div>
                        ))}
                        {(() => {
                          const p4 = trajectoryData.hazard_assessment.points.find((p:any) => p.role === 'P4');
                          const pFinal = trajectoryData.hazard_assessment.points.find((p:any) => p.role === 'P6' || p.role === 'P_kin24');
                          if (p4 && pFinal && p4 !== pFinal) {
                            return (
                              <div className="mt-2 bg-surface-variant/30 rounded p-2 text-[10px] font-telemetry-sm text-secondary">
                                <span className="block font-bold text-primary mb-1">Current → Predicted</span>
                                <div className="flex justify-between">
                                  <span>Δ Lat: {(pFinal.lat - p4.lat).toFixed(4)}°</span>
                                  <span>Δ Lon: {(pFinal.lon - p4.lon).toFixed(4)}°</span>
                                </div>
                              </div>
                            );
                          }
                          return null;
                        })()}
                      </div>
                      <div className="pt-2">
                        <div className="flex items-center text-xs text-secondary font-telemetry-sm mb-2">
                          <span className="font-label-caps text-[10px] uppercase text-secondary tracking-widest w-full">Prediction</span>
                        </div>
                        <div className="flex items-center font-telemetry-sm text-[10px] text-primary">
                          {trajectoryData.hazard_assessment.points.map((pt: any, idx: number) => (
                            <React.Fragment key={`path_${pt.role}`}>
                              <span>{pt.role}</span>
                              {idx < trajectoryData.hazard_assessment.points.length - 1 && (
                                <span className="mx-1 text-red-500">───</span>
                              )}
                            </React.Fragment>
                          ))}
                        </div>
                      </div>
                      <div className="pt-2">
                        <div className="flex items-center text-xs text-secondary font-telemetry-sm">
                          <span className="font-label-caps text-[10px] uppercase text-secondary tracking-widest w-full mb-1">Hazard</span>
                        </div>
                        <div className="flex items-center gap-1.5 font-telemetry-sm text-xs text-primary">
                           <span className="w-2 h-2 rounded-full bg-yellow-500"></span> Operational envelope available
                        </div>
                      </div>
                    </div>
                  )
                )}
                
                {trajectoryData && (!trajectoryData.hazard_assessment || trajectoryData.status === 'INSUFFICIENT_DATA') && (
                  <div className="mt-4 bg-error-container/20 border border-error/30 p-3 rounded text-xs text-error-800 font-telemetry-sm flex items-start gap-2">
                    <span className="material-symbols-outlined text-[16px]">warning</span>
                    <span>Insufficient data for operational forecast hazard generation.</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-surface-container-lowest rounded-xl border border-surface-variant border-dashed p-8 flex flex-col items-center justify-center h-[300px] text-center text-secondary opacity-60">
                <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">touch_app</span>
                <p className="font-body-md">Select an iceberg from the map or dropdown to view details.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
