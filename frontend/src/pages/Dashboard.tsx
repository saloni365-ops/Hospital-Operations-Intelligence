import { useEffect, useState } from 'react'
import { api, type Comparison } from '../api/client'
import { MODE_ORDER, MODE_IDENTITY } from '../constants/modes'
import { MetricsDashboard } from '../charts/MetricsDashboard'
import { useSimulationStore } from '../store/simulation'
export function Dashboard() {
  const state = useSimulationStore((store) => store.state)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [scenario, setScenario] = useState('admission_surge')
  const run = async () => {
    setRunning(true); setProgress(0)
    try {
      const job = await api.comparisonJob(state?.seed ?? 42, 48, scenario)
      let current = job
      while (current.status !== 'complete') {
        await new Promise((resolve) => window.setTimeout(resolve, 350))
        current = await api.comparisonJobState(job.id)
        setProgress(current.progress)
      }
      setProgress(100)
      if (current.results) setComparison({ seed: current.seed, horizon: current.horizon, scenario: current.scenario, results: current.results })
    } finally { setRunning(false) }
  }
  useEffect(() => { void run() }, [])
  return <section className="page-stage"><header className="page-heading"><div><p>Matched analytics</p><h2>Operations Dashboard</h2></div><div className="scenario-actions"><select value={scenario} onChange={(event) => setScenario(event.target.value)} aria-label="Scenario"><option value="admission_surge">Admission surge</option><option value="nurse_shortage">Nurse shortage</option><option value="bed_closure">Bed closure</option><option value="ed_overload">ED overload</option></select><button className="hud-button cyan" onClick={run} disabled={running}>{running ? `Running · ${progress}%` : 'Run matched comparison'}</button></div></header>{running && <div className="job-stepper" aria-label="Comparison progress"><div className="job-track"><i style={{ width: `${progress}%` }} /></div><span>{progress < 34 ? 'Preparing scenario' : progress < 67 ? 'Running modes' : 'Aggregating evidence'}</span></div>}{comparison && <div className="mode-kpis">{MODE_ORDER.map((mode) => { const result = comparison.results[mode]; const top = [...MODE_ORDER].sort((a, b) => comparison.results[a].unmet_demand - comparison.results[b].unmet_demand)[0] === mode; return <article key={mode} style={{ borderTopColor: MODE_IDENTITY[mode].color }}><div><span>{MODE_IDENTITY[mode].icon}</span><b>{MODE_IDENTITY[mode].name}</b>{top && <em>★ Best queue</em>}</div><strong>{result.unmet_demand}</strong><small>patient-hours unmet</small></article> })}</div>}<MetricsDashboard state={state} comparison={comparison} onCompare={run} busy={running} /></section>
}
