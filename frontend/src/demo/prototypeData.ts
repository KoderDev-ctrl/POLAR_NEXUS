// PROTOTYPE DEMO DATA
// Used only to visualize functionality that the backend currently does not support,
// such as multiple route alternatives and multi-iceberg dashboard visualization.

export const demoRouteAlternatives = (baseRoute: any, start: number[], end: number[]) => {
  // If we already have a real route, we'll generate 3 alternatives based on it
  if (!baseRoute || !baseRoute.geometry || baseRoute.geometry.length < 2) {
    return demoRouteAlternativesFallback(start, end);
  }
  
  const genAlt = (offsetMultiplier: number, feasible: boolean, reason: string = "") => {
    // Generate a geometric offset to create a distinct path
    const offsetGeom = baseRoute.geometry.map((pt: number[], i: number) => {
      if (i === 0 || i === baseRoute.geometry.length - 1) return pt; // Keep start/end same
      // Simple lat offset for demo
      return [pt[0] + (0.1 * offsetMultiplier * (i % 2 === 0 ? 1 : 0.8)), pt[1] + (0.1 * offsetMultiplier)];
    });
    
    return {
      route_id: `ALT-${Math.abs(offsetMultiplier)}`,
      engine_category: 'Demo-A*',
      distance_nm: baseRoute.distance_nm * (1 + Math.abs(offsetMultiplier) * 0.05),
      estimated_time_hours: baseRoute.estimated_time_hours * (1 + Math.abs(offsetMultiplier) * 0.05),
      estimated_fuel_mt: baseRoute.estimated_fuel_mt * (1 + Math.abs(offsetMultiplier) * 0.05),
      environmental_risk: feasible ? baseRoute.environmental_risk * (1 - offsetMultiplier * 0.1) : 100.0,
      cpa_nm: 2.5 + offsetMultiplier,
      geometry: offsetGeom,
      feasible,
      violation_reason: reason
    };
  };

  return [
    { ...baseRoute, route_id: "ROUTE 01", feasible: true, violation_reason: "" },
    { ...genAlt(1, true), route_id: "ROUTE 02" },
    { ...genAlt(-1.5, true), route_id: "ROUTE 03" },
    { ...genAlt(2, false, "Hazard Exclusion Zone Intersect"), route_id: "ROUTE 04" }
  ];
};

export const demoRouteAlternativesFallback = (start: number[], end: number[]) => {
  // Purely artificial routes if backend fails
  const dist = Math.hypot(end[0]-start[0], end[1]-start[1]) * 60; // rough NM approx

  const genAlt = (id: string, offsetMultiplier: number, feasible: boolean, reason: string = "") => {
    const midPoint = [
      (start[0] + end[0]) / 2 + (0.2 * offsetMultiplier),
      (start[1] + end[1]) / 2 + (0.5 * offsetMultiplier)
    ];
    const qPoint1 = [
      (start[0] + midPoint[0]) / 2 + (0.1 * offsetMultiplier),
      (start[1] + midPoint[1]) / 2 + (0.3 * offsetMultiplier)
    ];
    const qPoint2 = [
      (midPoint[0] + end[0]) / 2 - (0.1 * offsetMultiplier),
      (midPoint[1] + end[1]) / 2 + (0.1 * offsetMultiplier)
    ];

    const geom = [start, qPoint1, midPoint, qPoint2, end];
    
    return {
      route_id: id,
      engine_category: 'Demo-Fallback',
      distance_nm: dist * (1 + Math.abs(offsetMultiplier) * 0.1),
      estimated_time_hours: (dist * (1 + Math.abs(offsetMultiplier) * 0.1)) / 12, // assuming 12kn
      estimated_fuel_mt: 10 + (Math.abs(offsetMultiplier) * 2),
      environmental_risk: feasible ? 15 - offsetMultiplier : 100.0,
      cpa_nm: 2.5 + offsetMultiplier,
      geometry: geom,
      feasible,
      violation_reason: reason
    };
  };

  return [
    genAlt("ROUTE 01", 0, true),
    genAlt("ROUTE 02", 1.5, true),
    genAlt("ROUTE 03", -1.5, false, "Sea Ice Concentration > 80%"),
    genAlt("ROUTE 04", 2.5, true)
  ];
};

export const demoHazardFallback = {
  status: "SUCCESS",
  points: [
    { role: "P4", lat: -62.20, lon: -58.90, horizon_h: 0, source: "PROTOTYPE DEMONSTRATION" },
    { role: "P_kin24", lat: -62.12, lon: -58.55, horizon_h: 24, source: "PROTOTYPE DEMONSTRATION" },
    { role: "P6", lat: -62.02, lon: -58.15, horizon_h: 72, source: "PROTOTYPE DEMONSTRATION" }
  ],
  advisories: [],
  envelope: [
    [-62.30, -59.00],
    [-62.25, -58.60],
    [-61.90, -58.00],
    [-62.10, -58.05],
    [-62.40, -58.95]
  ]
};

export const demoDashboardMapData = {
  vessel: { lat: -62.5, lon: -59.5, heading: 210 },
  icebergs: [
    {
      id: "A23a",
      current: { lat: -64.2, lon: -62.5 },
      predicted: { lat: -64.0, lon: -62.0 },
      trajectory: [[-64.2, -62.5], [-64.1, -62.2], [-64.0, -62.0]],
      polygon: [[-64.2, -62.6], [-63.9, -61.9], [-64.3, -62.1]]
    }
  ],
  route: [
    [-62.2, -58.9],
    [-63.0, -60.0],
    [-63.5, -61.5],
    [-64.77, -64.05]
  ]
};

const WATER_SAFE_COORDS = [
  [-61.0, -59.0], [-60.5, -57.5], [-61.8, -57.0], [-62.5, -59.5], 
  [-63.0, -58.0], [-64.0, -54.0], [-65.0, -55.0], [-66.0, -53.0], 
  [-64.5, -62.5], [-65.2, -64.0], [-66.0, -66.0], [-67.0, -69.0], 
  [-68.0, -73.0], [-69.0, -75.0], [-61.2, -55.0], [-62.8, -60.8],
  [-63.5, -61.2], [-64.2, -56.5], [-65.8, -58.2], [-67.5, -71.0]
];

export const demoIcebergsFallback = WATER_SAFE_COORDS.map((coord, i) => {
  return {
    id: `demo_iceberg_${i+1}`,
    latitude: coord[0],
    longitude: coord[1],
    observedAt: new Date().toISOString(),
    source: 'DEMO/REPLAY',
    status: 'REPLAY'
  };
});

export const getDemoHazardFallback = (id: string, lat: number, lon: number) => {
  const seed = id.charCodeAt(id.length - 1);
  const dLat = (seed % 5 + 1) * 0.02 * (seed % 2 === 0 ? 1 : -1);
  const dLon = (seed % 7 + 1) * 0.03 * (seed % 3 === 0 ? 1 : -1);
  
  const p4 = { lat: lat, lon: lon };
  const pKin = { lat: lat + dLat, lon: lon + dLon };
  const p6 = { lat: lat + dLat * 2.2, lon: lon + dLon * 2.5 };
  
  return {
    status: "SUCCESS",
    points: [
      { role: "P4", lat: p4.lat, lon: p4.lon, horizon_h: 0, source: "DEMO/REPLAY" },
      { role: "P_kin24", lat: pKin.lat, lon: pKin.lon, horizon_h: 24, source: "DEMO/REPLAY" },
      { role: "P6", lat: p6.lat, lon: p6.lon, horizon_h: 72, source: "DEMO/REPLAY" }
    ],
    advisories: [],
    envelope: [
      [p4.lat - Math.abs(dLat), p4.lon - Math.abs(dLon)],
      [p4.lat + Math.abs(dLat), p4.lon - Math.abs(dLon)],
      [p6.lat + Math.abs(dLat)*1.5, p6.lon + Math.abs(dLon)*1.5],
      [p6.lat - Math.abs(dLat)*1.5, p6.lon + Math.abs(dLon)*1.5]
    ]
  };
};
