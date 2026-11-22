import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type RunFailure } from '../api/client'
import { MODE_ORDER, MODE_IDENTITY, type Mode } from '../constants/modes'
import { useSimulationStore } from '../store/simulation'

export function FailureLab() {
  const [failures, setFailures] = useState<RunFailure[]>([])
  const [loading, setLoading] = useState(true)
  const [scenario, setScenario] = useState('admission_surge')
  const state = useSimulationStore((store) => store.state)
  const mode = useSimulationStore((store) => store.mode)
  const setMode = useSimulationStore((store) => store.setMode)
  const speed = useSimulationStore((store) => store.speed)
  const setSpeed = useSimulationStore((store) => store.setSpeed)
  const setSettings = useSimulationStore((store) => store.setSettings)
  const reset = useSimulationStore((store) => store.reset)
  const start = useSimulationStore((store) => store.start)
  const pause = useSimulationStore((store) => store.pause)
  const step = useSimulationStore((store) => store.step)
  const busy = useSimulationStore((store) => store.busy)
  const setReplay = useSimulationStore((store) => store.setReplay)
  const navigate = useNavigate()
  const [liveSeed, setLiveSeed] = useState(state?.seed ?? 42)
  const [liveHorizon, setLiveHorizon] = useState(state?.horizon ?? 72)

  useEffect(() => {
    if (state) {
      setLiveSeed(state.seed)
      setLiveHorizon(state.horizon)
    }
  }, [state?.seed, state?.horizon])

  useEffect(() => {
    let active = true
    setLoading(true)
    const seeds = `${liveSeed},${liveSeed + 11},${liveSeed + 23}`
    api.failures(scenario, seeds, liveHorizon).then((data) => { if (active) setFailures(data.failures) }).catch(() => { if (active) setFailures([]) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [scenario, liveSeed, liveHorizon])

  const replay = (failure: RunFailure) => { setReplay(true, Math.max(0, failure.t_start - 6)); navigate('/control') }
  const replayMostFrequent = failures.length ? failures.slice().sort((a, b) => (b.t_end - b.t_start) - (a.t_end - a.t_start))[0] : null

  return <section className="page-stage">
    <header className="page-heading"><div><p>Measured evidence</p><h2>Failure Lab</h2></div><label className="scenario-actions"><span>Scenario</span><select value={scenario} onChange={(event) => setScenario(event.target.value)}><option value="admission_surge">Admission surge</option><option value="nurse_shortage">Nurse shortage</option><option value="bed_closure">Bed closure</option><option value="ed_overload">ED overload</option></select></label></header>
    <div className="control-mode-dock" aria-label="Select decision mode">
      {MODE_ORDER.map((value: Mode) => <button key={value} className={mode === value ? 'active' : ''} style={{ '--mode': MODE_IDENTITY[value].color } as React.CSSProperties} onClick={() => void setMode(value)} aria-pressed={mode === value}><span className="mode-icon">{MODE_IDENTITY[value].icon}</span><span className="mode-copy"><b>Mode {MODE_IDENTITY[value].number} · {MODE_IDENTITY[value].name}</b><small>{MODE_IDENTITY[value].description}</small></span>{value === 'hybrid' && <em>FLAGSHIP</em>}</button>)}
    </div>
    <div className="control-live-settings" aria-label="Live simulation controls">
      <button className="icon-button" onClick={() => void reset(liveSeed)} title="Reset simulation" aria-label="Reset simulation">↺</button>
      {state?.running ? <button className="primary-button" onClick={() => void pause()} disabled={busy}>Ⅱ Pause</button> : <button className="primary-button" onClick={() => void start(liveSeed)} disabled={busy}>▶ Run</button>}
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
    {loading ? <div className="illustrated-empty"><div className="empty-graph">◷</div><h3>Detecting measured failures</h3><p>Replaying matched seeds through the identical threshold configuration…</p></div> : failures.length === 0 ? <div className="illustrated-empty"><div className="empty-graph">✓</div><h3>No threshold failures detected</h3><p>This scenario stayed within every identical configured threshold.</p></div> : <>
      <div className="failure-summary">{MODE_ORDER.map((mode) => { const rows = failures.filter((failure) => failure.mode === mode); const hours = rows.reduce((sum, failure) => sum + Math.max(1, failure.t_end - failure.t_start), 0); return <article key={mode} style={{ borderTopColor: MODE_IDENTITY[mode].color }}><span>{MODE_IDENTITY[mode].icon}</span><div><b>{MODE_IDENTITY[mode].name}</b><strong>{rows.length} failures</strong><small>{hours} failure-hours · first at hour {rows[0]?.t_start ?? '—'}</small></div></article> })}</div>
      <div className="failure-timeline">{MODE_ORDER.map((mode) => <article key={mode} className="failure-lane"><h3><span style={{ color: MODE_IDENTITY[mode].color }}>{MODE_IDENTITY[mode].icon}</span>{MODE_IDENTITY[mode].name}</h3>{failures.filter((failure) => failure.mode === mode).slice(0, 8).map((failure, index) => <button key={`${failure.type}-${index}`} className="failure-block" onClick={() => replay(failure)} title={`${failure.root_cause}\n${JSON.stringify(failure.evidence)}`}><b>{failure.type}</b><small>Hour {failure.t_start}–{failure.t_end} · {failure.department}</small><p>{failure.root_cause}</p></button>)}</article>)}</div>
      {replayMostFrequent && <p className="verdict">Verdict: measured across the selected scenario and seeds. <b>{MODE_IDENTITY[replayMostFrequent.mode].name}</b> has the longest observed failure block in this result set. Replay evidence with its root cause rather than a scripted outcome. <button onClick={() => replay(replayMostFrequent)}>Replay strongest case</button></p>}
    </>}
  </section>
}
