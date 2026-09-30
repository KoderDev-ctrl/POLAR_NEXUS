import React, { useState } from 'react';
import { MapComponent } from '../components/MapComponent';
import { CircleMarker } from 'react-leaflet';

export default function SeaIce() {
  const [lat, setLat] = useState('-64.5');
  const [lon, setLon] = useState('-63.2');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    setResult(null);
    
    // Simulate network delay
    setTimeout(() => {
      setResult({
        concentration: 72,
        lat: parseFloat(lat),
        lon: parseFloat(lon)
      });
      setLoading(false);
    }, 1000);
  };

  return (
    <main className="w-full min-h-[calc(100vh-64px)] p-4 md:p-8 bg-surface flex justify-center">
      <div className="max-w-4xl w-full flex flex-col space-y-6">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary text-[32px]">severe_cold</span>
          <h1 className="text-3xl font-headline-lg text-primary tracking-tight">Sea Ice Prediction</h1>
        </div>

        <div className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-surface-variant flex flex-col space-y-6">
          <form onSubmit={handlePredict} className="flex flex-col space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="font-label-caps text-label-caps uppercase text-secondary">Latitude</label>
                <input 
                  type="text" 
                  value={lat} 
                  onChange={e => setLat(e.target.value)}
                  className="bg-surface-container-low border border-surface-variant rounded p-2.5 font-telemetry-sm text-primary focus:outline-none focus:border-primary"
                  placeholder="-64.5"
                />
              </div>
              <div className="flex flex-col space-y-1.5">
                <label className="font-label-caps text-label-caps uppercase text-secondary">Longitude</label>
                <input 
                  type="text" 
                  value={lon} 
                  onChange={e => setLon(e.target.value)}
                  className="bg-surface-container-low border border-surface-variant rounded p-2.5 font-telemetry-sm text-primary focus:outline-none focus:border-primary"
                  placeholder="-63.2"
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full md:w-auto self-start bg-primary text-on-primary hover:bg-[#17324D] py-2.5 px-6 rounded font-label-caps text-label-caps uppercase tracking-wider flex items-center justify-center gap-2 shadow-sm transition-colors mt-2 disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[18px]">satellite_alt</span>
              {loading ? "PREDICTING..." : "PREDICT SEA ICE"}
            </button>
          </form>

          {result && (
            <div className="flex flex-col space-y-4 pt-4 border-t border-surface-variant">
              <div className="bg-surface-container-low p-6 rounded-lg shadow-sm flex flex-col items-center justify-center text-center space-y-2">
                <span className="font-label-caps text-label-caps uppercase text-secondary tracking-widest">SEA-ICE CONCENTRATION</span>
                <span className="font-headline-lg text-primary text-5xl font-bold">{result.concentration}%</span>
                <span className="bg-amber-100 text-amber-800 font-telemetry-xs px-3 py-1 rounded uppercase tracking-wider font-bold mt-2">
                  DEMONSTRATION ESTIMATE
                </span>
                <p className="font-body-sm text-secondary mt-2">
                  Model refinement and validation are ongoing.
                </p>
              </div>

              <div className="w-full h-[400px] mt-4 rounded-xl overflow-hidden border border-surface-variant relative">
                <MapComponent center={[result.lat, result.lon]} zoom={6}>
                  <CircleMarker 
                    center={[result.lat, result.lon]} 
                    pathOptions={{ color: 'white', fillColor: '#0284C7', fillOpacity: 0.8, weight: 2 }} 
                    radius={12} 
                  />
                </MapComponent>
              </div>
            </div>
          )}

          {status && (
            <div className="bg-error-container/20 border border-error/30 p-4 rounded-lg flex items-start gap-3 mt-4">
              <span className="material-symbols-outlined text-error mt-0.5">warning</span>
              <p className="font-body-md text-error-800">{status}</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
