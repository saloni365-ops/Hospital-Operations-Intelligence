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
      const job = await api.comparisonJob(state?.seed ?? 42, state?.horizon ?? 48, scenario)
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
  return <section className="page-stage"><header className="page-heading"><div><p>Matched analytics</p><h2>Operations Dashboard</h2></div><div className="scenario-actions"><select value={scenario} onChange={(event) => setScenario(event.target.value)} aria-label="Scenario"><option value="admission_surge">Admission surge</option><option value="nurse_shortage">Nurse shortage</option><option value="bed_closure">Bed closure</option><option value="ed_overload">ED overload</option></select><button className="hud-button cyan" onClick={run} disabled={running}>{running ? `Running · ${progress}%` : 'Run matched comparison'}</button></div></header>{running && <div className="job-stepper" aria-label="Comparison progress"><div className="job-track"><i style={{ width: `${progress}%` }} /></div><span>{progress < 34 ? 'Preparing scenario' : progress < 67 ? 'Running modes' : 'Aggregating evidence'}</span></div>}{comparison && <><div className="mode-kpis">{MODE_ORDER.map((mode) => { const result = comparison.results[mode]; const top = [...MODE_ORDER].sort((a, b) => comparison.results[a].unmet_demand - comparison.results[b].unmet_demand)[0] === mode; return <article key={mode} style={{ borderTopColor: MODE_IDENTITY[mode].color }}><div><span>{MODE_IDENTITY[mode].icon}</span><b>{MODE_IDENTITY[mode].name}</b>{top && <em>★ Best queue</em>}</div><strong>{result.unmet_demand}</strong><small>patient-hours unmet</small></article> })}</div><DashboardVerdict comparison={comparison} /></>}<MetricsDashboard state={state} comparison={comparison} onCompare={run} busy={running} /></section>
}

function DashboardVerdict({ comparison }: { comparison: Comparison }) {
  const ranked = MODE_ORDER.map((mode) => ({ mode, ...comparison.results[mode] })).sort((a, b) => {
    if (a.unmet_demand !== b.unmet_demand) return a.unmet_demand - b.unmet_demand
    if (a.final_queue !== b.final_queue) return a.final_queue - b.final_queue
    return a.nurse_balance - b.nurse_balance
  })
  const winner = ranked[0]
  const runnerUp = ranked[1]
  const saved = runnerUp.unmet_demand - winner.unmet_demand
  const reason = winner.mode === 'hybrid' ? 'it combines forecasts, live queues, and nurse rebalancing' : winner.mode === 'quantum' ? 'its allocation search spreads demand across departments' : 'it responds quickly using a forecast-first rule'
  return <div className="explainable-result"><span>One-line result</span><strong>{MODE_IDENTITY[winner.mode].name} wins: {winner.unmet_demand} unmet patient-hours versus {runnerUp.unmet_demand} for {MODE_IDENTITY[runnerUp.mode].name}, saving {saved} patient-hours because {reason}.</strong></div>
}
