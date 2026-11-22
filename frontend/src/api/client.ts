export type Mode = 'predictive' | 'quantum' | 'hybrid'
export type EventKind = 'surge' | 'nurse_unavailable' | 'bed_closure' | 'ed_overload'
export interface DepartmentState { name: string; beds: string[]; capacity: number; occupied: number; queue: number; nurses: number; forecast: number; arrivals: number }
export interface MetricRecord { step: number; hour: number; arrivals: Record<string, number>; forecast: Record<string, number>; occupancy: Record<string, number>; capacity: Record<string, number>; nurses: Record<string, number>; queue: Record<string, number>; utilization: number; unmet_demand: number; nurse_balance: number; optimizer_ms: number }
export interface HospitalState { seed: number; step: number; horizon: number; running: boolean; mode: Mode; departments: DepartmentState[]; metrics: MetricRecord; history: MetricRecord[]; events: unknown[]; event_log: string[]; optimizer_ms: number }
export interface Comparison { seed: number; horizon: number; scenario: string; results: Record<Mode, { bed_utilization: number; unmet_demand: number; nurse_balance: number; optimizer_ms: number; final_queue: number }> }
export interface ComparisonJob { id: string; status: 'running' | 'complete'; progress: number; seed: number; horizon: number; scenario: string; results: Comparison['results'] | null }
export interface RunFailure { mode: Mode; seed: number; scenario: string; t_start: number; t_end: number; department: string; type: string; severity: string; root_cause: string; evidence: Record<string, number> }
const base = import.meta.env.VITE_API_BASE_URL ?? `${window.location.protocol}//${window.location.hostname}:8001`
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } })
  if (!response.ok) throw new Error(`API ${response.status}`)
  return response.json() as Promise<T>
}
const post = (path: string, body?: unknown) => request<HospitalState>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) })
export const api = {
  state: () => request<HospitalState>('/simulation/state'),
  start: (seed: number) => post('/simulation/start', { seed, horizon: 168 }),
  pause: () => post('/simulation/pause'),
  reset: (seed: number) => post('/simulation/reset', { seed, horizon: 168 }),
  settings: (seed: number, horizon: number) => post('/simulation/settings', { seed, horizon }),
  step: () => post('/simulation/step'),
  mode: (mode: Mode) => post('/simulation/mode', { mode }),
  event: (kind: EventKind, department?: string) => post('/simulation/events', { kind, department, duration: 8, magnitude: 0.3 }),
  comparison: (seed: number, horizon = 48) => request<Comparison>(`/comparison?seed=${seed}&horizon=${horizon}`),
  comparisonJob: async (seed: number, horizon = 48, scenario = 'admission_surge') => {
    const started = await request<ComparisonJob>(`/comparison/run?seed=${seed}&horizon=${horizon}&scenario=${encodeURIComponent(scenario)}`, { method: 'POST' })
    return started
  },
  comparisonJobState: (jobId: string) => request<ComparisonJob>(`/comparison/${jobId}`),
  failures: (scenario = 'admission_surge', seeds = '11,23,42', horizon = 72) => request<{ failures: RunFailure[]; thresholds: Record<string, unknown>; runs: Record<string, string> }>(`/failures?scenario=${scenario}&seeds=${encodeURIComponent(seeds)}&horizon=${horizon}`),
}