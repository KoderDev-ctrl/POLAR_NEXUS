import React, { useState, useEffect } from 'react';
import { MapComponent } from '../components/MapComponent';
import { fetchIcebergs, fetchIcebergTrajectory } from '../api/client';
import { CircleMarker, Polyline, Polygon, useMap } from 'react-leaflet';

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
          } else {
             // Generate synthetic fallback to ensure many icebergs are visible
             const fakeIcebergs = Array.from({length: 30}).map((_, i) => ({
               id: `synthetic_${i}`,
               latitude: -64.5 + (Math.random() * 4 - 2),
               longitude: -63.2 + (Math.random() * 8 - 4),
               observedAt: new Date().toISOString(),
               source: 'DEMO/REPLAY',
               status: 'Observed'
             }));
             fakeIcebergs.push({
               id: 'a23a', latitude: -64.5, longitude: -63.2, observedAt: new Date().toISOString(), source: 'DEMO/REPLAY', status: 'Observed'
             });
             setIcebergs(fakeIcebergs);
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
          setTrajectoryData({
            id: icebergId,
            historical: [
              { latitude: -65.0, longitude: -63.5, observedAt: '2025-12-30T12:00:00Z' },
              { latitude: -64.8, longitude: -63.3, observedAt: '2025-12-31T00:00:00Z' }
            ],
            hazard_assessment: m.demoHazardFallback,
            status: 'REPLAY'
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
                    <Polygon positions={trajectoryData.hazard_assessment.envelope} color="orange" weight={1} fillColor="orange" fillOpacity={0.2} />
                  )}
                  {trajectoryData && trajectoryData.historical && trajectoryData.historical.length > 1 && (
                    <Polyline positions={trajectoryData.historical.map((p: any) => [p.latitude, p.longitude])} color="#475569" weight={2} opacity={0.6} />
                  )}
                  {trajectoryData && trajectoryData.hazard_assessment && trajectoryData.hazard_assessment.points && (
                    <Polyline positions={trajectoryData.hazard_assessment.points.map((p: any) => [p.lat, p.lon])} color="orange" weight={3} dashArray="5, 10" />
                  )}
                  {trajectoryData && trajectoryData.hazard_assessment && trajectoryData.hazard_assessment.points && (
                    trajectoryData.hazard_assessment.points.map((pt: any, i: number) => (
                      <CircleMarker 
                        key={`pred_${i}`}
                        center={[pt.lat, pt.lon]} 
                        color={'orange'}
                        fillColor={'orange'}
                        fillOpacity={1}
                        radius={6} 
                      />
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
                <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-500 border border-red-600"></span><span className="font-telemetry-xs text-primary font-bold">Selected</span></div>
                <div className="flex items-center gap-1.5"><span className="w-4 h-0.5 bg-slate-600"></span><span className="font-telemetry-xs text-secondary">Historical Track</span></div>
                <div className="flex items-center gap-1.5"><span className="w-4 h-0.5 bg-orange-500 border-dashed border-b-2"></span><span className="font-telemetry-xs text-secondary">Forecast</span></div>
                <div className="flex items-center gap-1.5"><span className="w-4 h-4 bg-orange-500/20 border border-orange-500/50"></span><span className="font-telemetry-xs text-secondary">Exclusion Zone</span></div>
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
                    <div className="mt-4 flex flex-col space-y-3">
                      <h4 className="font-label-caps text-[10px] uppercase text-secondary tracking-widest bg-surface-variant px-2 py-1 rounded-sm">Operational Models</h4>
                      {trajectoryData.hazard_assessment.points.map((pt: any) => (
                        <div key={pt.role} className="flex justify-between items-center text-xs">
                          <span className="font-telemetry-sm font-bold text-primary">{pt.role}</span>
                          <span className="font-telemetry-sm text-secondary bg-surface-variant px-1 rounded">+{pt.horizon_h}h</span>
                        </div>
                      ))}
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
