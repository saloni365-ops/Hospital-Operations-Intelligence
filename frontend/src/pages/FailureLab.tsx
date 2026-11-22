import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type RunFailure } from '../api/client'
import { MODE_ORDER, MODE_IDENTITY } from '../constants/modes'
import { useSimulationStore } from '../store/simulation'

export function FailureLab() {
  const [failures, setFailures] = useState<RunFailure[]>([])
  const [loading, setLoading] = useState(true)
  const [scenario, setScenario] = useState('admission_surge')
  const setReplay = useSimulationStore((store) => store.setReplay)
  const navigate = useNavigate()

  useEffect(() => {
    let active = true
    setLoading(true)
    api.failures(scenario).then((data) => { if (active) setFailures(data.failures) }).catch(() => { if (active) setFailures([]) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [scenario])

  const replay = (failure: RunFailure) => { setReplay(true, Math.max(0, failure.t_start - 6)); navigate('/control') }
  const replayMostFrequent = failures.length ? failures.slice().sort((a, b) => (b.t_end - b.t_start) - (a.t_end - a.t_start))[0] : null

  return <section className="page-stage">
    <header className="page-heading"><div><p>Measured evidence</p><h2>Failure Lab</h2></div><label className="scenario-actions"><span>Scenario</span><select value={scenario} onChange={(event) => setScenario(event.target.value)}><option value="admission_surge">Admission surge</option><option value="nurse_shortage">Nurse shortage</option><option value="bed_closure">Bed closure</option><option value="ed_overload">ED overload</option></select></label></header>
    {loading ? <div className="illustrated-empty"><div className="empty-graph">◷</div><h3>Detecting measured failures</h3><p>Replaying matched seeds through the identical threshold configuration…</p></div> : failures.length === 0 ? <div className="illustrated-empty"><div className="empty-graph">✓</div><h3>No threshold failures detected</h3><p>This scenario stayed within every identical configured threshold.</p></div> : <>
      <div className="failure-summary">{MODE_ORDER.map((mode) => { const rows = failures.filter((failure) => failure.mode === mode); const hours = rows.reduce((sum, failure) => sum + Math.max(1, failure.t_end - failure.t_start), 0); return <article key={mode} style={{ borderTopColor: MODE_IDENTITY[mode].color }}><span>{MODE_IDENTITY[mode].icon}</span><div><b>{MODE_IDENTITY[mode].name}</b><strong>{rows.length} failures</strong><small>{hours} failure-hours · first at hour {rows[0]?.t_start ?? '—'}</small></div></article> })}</div>
      <div className="failure-timeline">{MODE_ORDER.map((mode) => <article key={mode} className="failure-lane"><h3><span style={{ color: MODE_IDENTITY[mode].color }}>{MODE_IDENTITY[mode].icon}</span>{MODE_IDENTITY[mode].name}</h3>{failures.filter((failure) => failure.mode === mode).slice(0, 8).map((failure, index) => <button key={`${failure.type}-${index}`} className="failure-block" onClick={() => replay(failure)} title={`${failure.root_cause}\n${JSON.stringify(failure.evidence)}`}><b>{failure.type}</b><small>Hour {failure.t_start}–{failure.t_end} · {failure.department}</small><p>{failure.root_cause}</p></button>)}</article>)}</div>
      {replayMostFrequent && <p className="verdict">Verdict: measured across the selected scenario and seeds. <b>{MODE_IDENTITY[replayMostFrequent.mode].name}</b> has the longest observed failure block in this result set. Replay evidence with its root cause rather than a scripted outcome. <button onClick={() => replay(replayMostFrequent)}>Replay strongest case</button></p>}
    </>}
  </section>
}
