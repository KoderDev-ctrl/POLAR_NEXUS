import React from 'react';
import { MapComponent } from '../components/MapComponent';
import { CircleMarker, Polyline, Polygon, Marker, Popup } from 'react-leaflet';
import { demoDashboardMapData } from '../demo/prototypeData';
import L from 'leaflet';

// Create a simple custom icon for the vessel
const vesselIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color:#1E40AF; width:16px; height:16px; border-radius:50%; border:2px solid white;"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8]
});

export default function Dashboard() {
  const { vessel, icebergs, route } = demoDashboardMapData;

  return (
    <main className="w-full min-h-[calc(100vh-64px)] flex flex-col p-4 md:p-8 bg-surface space-y-4">
      <div className="max-w-[1600px] w-full mx-auto flex flex-col space-y-4 flex-grow">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary text-[32px]">dashboard</span>
            <h1 className="text-3xl font-headline-lg text-primary tracking-tight">System Overview</h1>
          </div>
          <div className="flex items-center gap-4 bg-surface-container-low p-2 rounded-lg border border-surface-variant">
            <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-600"></span><span className="font-telemetry-xs text-xs">Icebergs</span></div>
            <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-orange-500"></span><span className="font-telemetry-xs text-xs">Predictions</span></div>
            <div className="flex items-center gap-1.5"><span className="w-4 h-1 bg-[#0284C7]"></span><span className="font-telemetry-xs text-xs">Vessel Route</span></div>
            <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-[#1E40AF]"></span><span className="font-telemetry-xs text-xs">Vessel</span></div>
          </div>
        </div>
        
        <div className="w-full flex-grow min-h-[600px] rounded-xl overflow-hidden border border-surface-variant relative z-0 shadow-sm">
          <MapComponent center={[-63.5, -61.0]} zoom={6}>
            {/* Route */}
            <Polyline positions={route as any} color="#0284C7" weight={3} />
            
            {/* Vessel */}
            <Marker position={[vessel.lat, vessel.lon]} icon={vesselIcon}>
              <Popup>
                <div className="font-telemetry-sm">
                  <strong>Vessel Nexus-1</strong><br/>
                  Heading: {vessel.heading}°<br/>
                  Status: Underway
                </div>
              </Popup>
            </Marker>

            {/* Icebergs & Predictions */}
            {icebergs.map(ice => (
              <React.Fragment key={ice.id}>
                {/* Hazard Area */}
                <Polygon positions={ice.polygon as any} color="orange" weight={1} fillColor="orange" fillOpacity={0.2} />
                
                {/* Trajectory Line */}
                <Polyline positions={ice.trajectory as any} color="orange" weight={2} dashArray="4 4" />
                
                {/* Predicted Position */}
                <CircleMarker center={[ice.predicted.lat, ice.predicted.lon]} color="white" fillColor="orange" fillOpacity={1} weight={1} radius={5}>
                  <Popup><span className="font-telemetry-sm">Predicted: {ice.id}</span></Popup>
                </CircleMarker>
                
                {/* Current Position */}
                <CircleMarker center={[ice.current.lat, ice.current.lon]} color="white" fillColor="red" fillOpacity={1} weight={1} radius={6}>
                  <Popup><span className="font-telemetry-sm">Observed: {ice.id}</span></Popup>
                </CircleMarker>
              </React.Fragment>
            ))}
          </MapComponent>
        </div>
      </div>
    </main>
  );
}
