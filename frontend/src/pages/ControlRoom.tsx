import { useState } from 'react'
import { HospitalView } from '../game/HospitalView'
import { ControlPanel } from '../components/ControlPanel'
import { EventLog } from '../components/EventLog'
import { MetricsDashboard } from '../charts/MetricsDashboard'
import { useSimulationStore } from '../store/simulation'
import { api, type Comparison } from '../api/client'

export function ControlRoom() {
  const state = useSimulationStore((store) => store.state)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [busy, setBusy] = useState(false)
  const compare = async () => { setBusy(true); try { setComparison(await api.comparison(state?.seed ?? 42)) } finally { setBusy(false) } }
  const utilization = Math.round((state?.metrics?.utilization ?? 0) * 100)
  const waiting = state?.metrics?.unmet_demand ?? 0
  const eventCount = state?.events?.length ?? 0
  return <div className="control-room">
    <div className="control-stats" aria-label="Hospital live statistics">
      <Kpi label="Beds occupied" value={`${utilization}%`} grade={utilization > 90 ? 'C' : 'A'} trend={utilization > 75 ? '↑' : '→'} spark={[28,32,29,35,34,utilization]} />
      <Kpi label="Patients waiting" value={String(waiting)} grade={waiting > 8 ? 'D' : waiting > 3 ? 'C' : 'A'} trend={waiting ? '↑' : '→'} spark={[0,1,waiting]} />
      <Kpi label="Nurses on duty" value={String(state?.departments?.reduce((sum, ward) => sum + ward.nurses, 0) ?? 25)} grade="A" trend="→" spark={[25,25,24,25,25]} />
      <Kpi label="Unmet demand" value={String(waiting)} grade={waiting > 8 ? 'D' : 'B'} trend={waiting ? '↑' : '→'} spark={[waiting,waiting]} />
      <Kpi label="Active events" value={String(eventCount)} grade={eventCount ? 'C' : 'A'} trend={eventCount ? '↑' : '→'} spark={[0,eventCount]} />
    </div>
    <div className="control-grid">
      <aside className="left-hud">
        <section className="hud-card"><div className="hud-card-title"><span>01</span><h2>Objectives</h2></div><Objective title="Keep unmet demand below 3" progress={waiting < 3 ? 100 : 55} stars="★★☆" /><Objective title="Survive 30% surge" progress={eventCount ? 65 : 20} stars="★☆☆" /></section>
        <section className="hud-card"><div className="hud-card-title"><span>02</span><h2>Shift schedule</h2></div><div className="shift-row active"><b>Day</b><span>07:00—20:00</span></div><div className="shift-row"><b>Night</b><span>20:00—07:00</span></div><div className="shift-row"><b>Visiting</b><span>14:00—17:00</span></div></section>
      </aside>
      <section className="world-column"><HospitalView state={state} /><div className="bottom-controls"><ControlPanel state={state} /></div></section>
      <aside className="decision-column"><EventLog events={state?.event_log ?? []} departments={state?.departments ?? []} /></aside>
    </div>
    <MetricsDashboard state={state} comparison={comparison} onCompare={compare} busy={busy} />
  </div>
}

function Kpi({ label, value, grade, trend, spark }: { label: string; value: string; grade: string; trend: string; spark: number[] }) {
  const points = spark.map((n, i) => `${i * 8},${22 - Math.min(n, 20)}`).join(' ')
  return <article className="hex-kpi"><div className="hex-grade">{grade}</div><div><small>{label}</small><strong>{value}</strong><span>{trend} spark</span></div><svg viewBox="0 0 48 24" aria-hidden="true"><polyline points={points} /></svg></article>
}
function Objective({ title, progress, stars }: { title: string; progress: number; stars: string }) { return <div className="objective"><div><strong>{title}</strong><span>{stars}</span></div><div className="progress"><i style={{ width: `${progress}%` }} /></div></div> }
