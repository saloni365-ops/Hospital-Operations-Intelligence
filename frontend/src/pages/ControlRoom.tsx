import { useEffect, useState } from 'react'
import { HospitalView } from '../game/HospitalView'
import { EventLog } from '../components/EventLog'
import { MetricsDashboard } from '../charts/MetricsDashboard'
import { useSimulationStore } from '../store/simulation'
import { api, type Comparison } from '../api/client'
import { MODE_IDENTITY, MODE_ORDER, type Mode } from '../constants/modes'

export function ControlRoom() {
  const state = useSimulationStore((store) => store.state)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [busy, setBusy] = useState(false)
  const compare = async () => { setBusy(true); try { setComparison(await api.comparison(state?.seed ?? 42)) } finally { setBusy(false) } }
  const utilization = Math.round((state?.metrics?.utilization ?? 0) * 100)
  const waiting = state?.metrics?.unmet_demand ?? 0
  const eventCount = state?.events?.length ?? 0
  const mode = useSimulationStore((store) => store.mode)
  const setMode = useSimulationStore((store) => store.setMode)
  const speed = useSimulationStore((store) => store.speed)
  const setSpeed = useSimulationStore((store) => store.setSpeed)
  const setSettings = useSimulationStore((store) => store.setSettings)
  const reset = useSimulationStore((store) => store.reset)
  const start = useSimulationStore((store) => store.start)
  const pause = useSimulationStore((store) => store.pause)
  const step = useSimulationStore((store) => store.step)
  const busyStore = useSimulationStore((store) => store.busy)
  const [liveSeed, setLiveSeed] = useState(state?.seed ?? 42)
  const [liveHorizon, setLiveHorizon] = useState(state?.horizon ?? 168)
  useEffect(() => {
    if (state) {
      setLiveSeed(state.seed)
      setLiveHorizon(state.horizon)
    }
  }, [state?.seed, state?.horizon])
  return <div className="control-room">
    <div className="control-stats" aria-label="Hospital live statistics">
      <Kpi label="Beds occupied" value={`${utilization}%`} grade={utilization > 90 ? 'C' : 'A'} trend={utilization > 75 ? '↑' : '→'} spark={[28,32,29,35,34,utilization]} />
      <Kpi label="Patients waiting" value={String(waiting)} grade={waiting > 8 ? 'D' : waiting > 3 ? 'C' : 'A'} trend={waiting ? '↑' : '→'} spark={[0,1,waiting]} />
      <Kpi label="Nurses on duty" value={String(state?.departments?.reduce((sum, ward) => sum + ward.nurses, 0) ?? 25)} grade="A" trend="→" spark={[25,25,24,25,25]} />
      <Kpi label="Unmet demand" value={String(waiting)} grade={waiting > 8 ? 'D' : 'B'} trend={waiting ? '↑' : '→'} spark={[waiting,waiting]} />
      <Kpi label="Active events" value={String(eventCount)} grade={eventCount ? 'C' : 'A'} trend={eventCount ? '↑' : '→'} spark={[0,eventCount]} />
    </div>
    <div className="control-mode-dock" aria-label="Select decision mode">
      {MODE_ORDER.map((value: Mode) => <button key={value} className={mode === value ? 'active' : ''} style={{ '--mode': MODE_IDENTITY[value].color } as React.CSSProperties} onClick={() => void setMode(value)} aria-pressed={mode === value}>
        <span className="mode-icon">{MODE_IDENTITY[value].icon}</span><span className="mode-copy"><b>Mode {MODE_IDENTITY[value].number} · {MODE_IDENTITY[value].name}</b><small>{MODE_IDENTITY[value].description}</small></span>{value === 'hybrid' && <em>FLAGSHIP</em>}
      </button>)}
    </div>
    <div className="control-live-settings" aria-label="Live simulation controls">
      <button className="icon-button" onClick={() => void reset(liveSeed)} title="Reset simulation" aria-label="Reset simulation">↺</button>
      {state?.running ? <button className="primary-button" onClick={() => void pause()} disabled={busyStore}>Ⅱ Pause</button> : <button className="primary-button" onClick={() => void start(liveSeed)} disabled={busyStore}>▶ Run</button>}
      <button className="icon-button" onClick={() => void step()} title="Advance one hour" aria-label="Advance one hour">›</button>
      <label><span>Speed</span><select value={speed} onChange={(event) => setSpeed(Number(event.target.value))}><option value={0.5}>0.5x</option><option value={1}>1x</option><option value={2}>2x</option><option value={4}>4x</option></select></label>
      <label><span>Seed</span><input type="number" min="0" value={liveSeed} onChange={(event) => setLiveSeed(Number(event.target.value))} /></label>
      <label><span>Hours</span><input type="number" min="1" max="720" value={liveHorizon} onChange={(event) => setLiveHorizon(Number(event.target.value))} /></label>
      <button className="hud-button cyan" onClick={() => void setSettings(liveSeed, liveHorizon)}>Apply</button>
      <span className="top-setting-divider" />
      <button className="top-disruption" onClick={() => void api.event('surge')}><b>⚡</b> Surge</button>
      <button className="top-disruption" onClick={() => void api.event('nurse_unavailable', 'General Medicine')}><b>✚</b> Nurses</button>
      <button className="top-disruption" onClick={() => void api.event('bed_closure', 'Cardiology')}><b>▣</b> Beds</button>
      <button className="top-disruption" onClick={() => void api.event('ed_overload')}><b>▲</b> ED overload</button>
    </div>
    <div className="control-grid">
      <aside className="left-hud">
        <section className="hud-card"><div className="hud-card-title"><span>01</span><h2>Objectives</h2></div><Objective title="Keep unmet demand below 3" progress={waiting < 3 ? 100 : 55} stars="★★☆" /><Objective title="Survive 30% surge" progress={eventCount ? 65 : 20} stars="★☆☆" /></section>
        <section className="hud-card"><div className="hud-card-title"><span>02</span><h2>Shift schedule</h2></div><div className="shift-row active"><b>Day</b><span>07:00—20:00</span></div><div className="shift-row"><b>Night</b><span>20:00—07:00</span></div><div className="shift-row"><b>Visiting</b><span>14:00—17:00</span></div></section>
      </aside>
      <section className="world-column"><HospitalView state={state} /></section>
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
