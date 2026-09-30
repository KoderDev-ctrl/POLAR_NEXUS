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
    },
    {
      id: "D28",
      current: { lat: -65.5, lon: -60.0 },
      predicted: { lat: -65.1, lon: -59.5 },
      trajectory: [[-65.5, -60.0], [-65.3, -59.8], [-65.1, -59.5]],
      polygon: [[-65.6, -60.2], [-65.0, -59.4], [-65.4, -59.3]]
    }
  ],
  route: [
    [-62.2, -58.9],
    [-63.0, -60.0],
    [-63.5, -61.5],
    [-64.77, -64.05]
  ]
};
