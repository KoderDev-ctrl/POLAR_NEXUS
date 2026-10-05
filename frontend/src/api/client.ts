export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchStatus() {
  const res = await fetch(`${API_BASE_URL}/api/v1/status`);
  if (!res.ok) throw new Error('Failed to fetch status');
  return res.json();
}

export async function fetchModels() {
  const res = await fetch(`${API_BASE_URL}/api/v1/models`);
  if (!res.ok) throw new Error('Failed to fetch models');
  return res.json();
}

export async function fetchHazard(icebergId: string, mode = 'operational') {
  const res = await fetch(`${API_BASE_URL}/api/v1/hazard/${icebergId}?mode=${mode}`);
  if (!res.ok) throw new Error('Failed to fetch hazard');
  return res.json();
}

export async function fetchIcebergs() {
  const res = await fetch(`${API_BASE_URL}/api/v1/icebergs`);
  if (!res.ok) throw new Error('Failed to fetch icebergs');
  return res.json();
}

export async function fetchIcebergTrajectory(icebergId: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/icebergs/${icebergId}/trajectory`);
  if (!res.ok) throw new Error('Failed to fetch iceberg trajectory');
  return res.json();
}

export interface VoyagePlanRequest {
  origin: number[];
  destination: number[];
  departure_time_utc: string;
  vessel: Record<string, any>;
  mode?: string;
  iceberg_id?: string;
}

export async function planVoyage(req: VoyagePlanRequest) {
  const res = await fetch(`${API_BASE_URL}/api/v1/voyage/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error('Failed to plan voyage');
  return res.json();
}

export interface ReplanRequest {
  current_pos: number[];
  active_route: Record<string, any>;
  vessel: Record<string, any>;
  iceberg_id: string;
  locked_category: string;
  refreshed_risk: number;
}

export async function replanVoyage(req: ReplanRequest) {
  const res = await fetch(`${API_BASE_URL}/api/v1/voyage/replan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error('Failed to replan voyage');
  return res.json();
}
