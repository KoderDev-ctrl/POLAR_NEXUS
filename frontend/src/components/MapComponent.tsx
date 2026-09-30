import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Polygon, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet's default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface AntarcticMapProps {
  children?: React.ReactNode;
  center?: [number, number];
  zoom?: number;
}

export function AntarcticMap({ children, center = [-64.8, -63.5], zoom = 5 }: AntarcticMapProps) {
  return (
    <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, zIndex: 0 }}>
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%', background: '#cce5ff' }} zoomControl={false}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {children}
      </MapContainer>
    </div>
  );
}

export function MapComponent(props: AntarcticMapProps) {
  return <AntarcticMap {...props} />;
}
