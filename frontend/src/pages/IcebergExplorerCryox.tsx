import React, { useState } from 'react';
import { MapComponent } from '../components/MapComponent';
import { fetchHazard } from '../api/client';
import { CircleMarker, Polyline, Polygon } from 'react-leaflet';

export default function IcebergExplorerCryox() {
  const [icebergId, setIcebergId] = useState('a23a');
  const [hazard, setHazard] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setHazard(null);
    try {
      const res = await fetchHazard(icebergId, "replay");
      if (res && res.status === 'SUCCESS') {
        setHazard(res);
      } else {
        // PROTOTYPE DEMONSTRATION FALLBACK
        const m = await import('../demo/prototypeData');
        setHazard(m.demoHazardFallback);
      }
    } catch (err) {
      // PROTOTYPE DEMONSTRATION FALLBACK
      const m = await import('../demo/prototypeData');
      setHazard(m.demoHazardFallback);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="w-full min-h-[calc(100vh-64px)] p-4 md:p-8 bg-surface flex justify-center">
      <div className="max-w-[1200px] w-full flex flex-col h-full bg-surface shadow-sm rounded-2xl border border-surface-variant p-6 space-y-6">
        <div className="flex items-center gap-2 border-b border-surface-variant pb-4">
          <span className="material-symbols-outlined text-primary text-[28px]">search</span>
          <h2 className="font-headline-lg text-primary uppercase tracking-wide text-2xl">Iceberg Tracking</h2>
        </div>

      <form onSubmit={handlePredict} className="flex flex-col space-y-4">
        <div className="flex flex-col space-y-2">
          <label className="font-label-caps text-label-caps uppercase text-secondary">Iceberg ID</label>
          <input 
            type="text" 
            value={icebergId} 
            onChange={(e) => setIcebergId(e.target.value)}
            className="w-full md:w-1/2 bg-surface-container-low border border-surface-variant rounded p-3 font-telemetry-sm text-primary focus:outline-none focus:border-primary"
            placeholder="e.g. a23a"
            required
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="w-full md:w-1/2 bg-primary text-on-primary hover:bg-[#17324D] py-3 px-6 rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-2 shadow-sm transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-[20px]">radar</span>
          {loading ? "Predicting..." : "Predict Trajectory"}
        </button>
      </form>

      {error && (
        <div className="bg-error-container/20 border border-error/30 p-4 rounded-lg flex items-center gap-3">
          <span className="material-symbols-outlined text-error">warning</span>
          <p className="font-body-md text-error-800">{error}</p>
        </div>
      )}

      {hazard && hazard.points && (
        <div className="flex flex-col space-y-4 pt-4 border-t border-surface-variant">
          <h3 className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">Prediction Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {hazard.points.map((pt: any) => (
              <div key={pt.role} className="bg-surface-container-low p-4 rounded-lg shadow-sm flex flex-col">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-telemetry-sm font-bold text-primary">{pt.role}</span>
                  <span className="bg-emerald-100 text-emerald-800 font-telemetry-xs px-2 py-0.5 rounded uppercase tracking-wider">{pt.horizon_h}h</span>
                </div>
                <span className="font-telemetry-sm text-secondary mb-1">{pt.lat?.toFixed(4)}°, {pt.lon?.toFixed(4)}°</span>
                <span className="font-body-sm text-on-surface-variant text-[11px] truncate">{pt.source}</span>
              </div>
            ))}
            {hazard.advisories?.map((pt: any) => (
              <div key={pt.role} className="bg-surface-container-low p-4 rounded-lg shadow-sm flex flex-col opacity-80">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-telemetry-sm font-bold text-primary">{pt.role}</span>
                  <span className="bg-amber-100 text-amber-800 font-telemetry-xs px-2 py-0.5 rounded uppercase tracking-wider">ADVISORY</span>
                </div>
                <span className="font-telemetry-sm text-secondary mb-1">{pt.lat?.toFixed(4)}°, {pt.lon?.toFixed(4)}°</span>
                <span className="font-body-sm text-on-surface-variant text-[11px] truncate">{pt.source}</span>
              </div>
            ))}
          </div>

          <div className="flex flex-col gap-2 mb-2">
            <h4 className="font-label-caps text-label-caps uppercase text-secondary">Map Legend</h4>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-600"></span><span className="font-telemetry-xs">Current Iceberg</span></div>
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-orange-500"></span><span className="font-telemetry-xs">Predicted Position</span></div>
              <div className="flex items-center gap-1.5"><span className="w-4 h-1 bg-orange-500"></span><span className="font-telemetry-xs">Trajectory</span></div>
              <div className="flex items-center gap-1.5"><span className="w-4 h-4 bg-orange-500/30 border border-orange-500/50"></span><span className="font-telemetry-xs">Uncertainty Area</span></div>
            </div>
          </div>

          <div className="w-full h-[400px] mt-4 rounded-xl overflow-hidden border border-surface-variant relative z-0">
            <MapComponent center={[hazard.points[0]?.lat || -64.5, hazard.points[0]?.lon || -63.2]} zoom={6}>
              {hazard.envelope && hazard.envelope.length > 0 && (
                <Polygon positions={hazard.envelope} color="orange" weight={1} fillColor="orange" fillOpacity={0.2} />
              )}
              {hazard.points && hazard.points.length > 1 && (
                <Polyline positions={hazard.points.map((p: any) => [p.lat, p.lon])} color="orange" weight={3} />
              )}
              {hazard.points?.map((pt: any, i: number) => (
                <CircleMarker 
                  key={pt.role} 
                  center={[pt.lat, pt.lon]} 
                  color={i === 0 ? 'red' : 'orange'}
                  fillColor={i === 0 ? 'red' : 'orange'}
                  fillOpacity={1}
                  radius={6} 
                />
              ))}
            </MapComponent>
          </div>
        </div>
      )}
      </div>
    </main>
  );
}
