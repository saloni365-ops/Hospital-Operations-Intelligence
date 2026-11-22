import { useEffect, useState } from 'react'
import { api, type Comparison } from '../api/client'
import { useSimulationStore } from '../store/simulation'
import { MODE_ORDER, MODE_IDENTITY } from '../constants/modes'

export function Arena() {
  const state = useSimulationStore((store) => store.state)
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setBusy(true)
    setError('')
    try { setComparison(await api.comparison(state?.seed ?? 42, state?.horizon ?? 48)) }
    catch { setError('Comparison could not run. Keep the backend on port 8001.') }
    finally { setBusy(false) }
  }

  useEffect(() => { void run() }, [])

  const values = comparison?.results
  return <section className="page-stage">
    <header className="page-heading"><div><p>Matched run · seed {comparison?.seed ?? state?.seed ?? 42}</p><h2>Decision Arena</h2></div><button className="hud-button cyan" onClick={run} disabled={busy}>{busy ? `Running ${comparison?.horizon ?? 48}-hour race…` : 'Run matched race'}</button></header>
    {error && <div className="connection-error">{error}</div>}
    {!comparison && !error && <div className="arena-loading">Running all three modes on identical admissions and disruptions…</div>}
    {comparison && <><div className="arena-grid">{MODE_ORDER.map((mode) => {
      const result = values?.[mode]
      const hybrid = mode === 'hybrid'
      const measuredLowest = comparison && result && (() => {
        const lowestQueue = Math.min(...MODE_ORDER.map((candidate) => comparison.results[candidate].unmet_demand ?? 0))
        const queueTies = MODE_ORDER.filter((candidate) => comparison.results[candidate].unmet_demand === lowestQueue)
        const winner = [...queueTies].sort((a, b) => (comparison.results[a].optimizer_ms ?? 0) - (comparison.results[b].optimizer_ms ?? 0))[0]
        return mode === winner
      })()
      const utilization = Math.round((result?.bed_utilization ?? 0) * 100)
      const queue = result?.final_queue ?? 0
      const unmet = result?.unmet_demand ?? 0
      return <article className="arena-card" key={mode} style={{ '--mode': MODE_IDENTITY[mode].color } as React.CSSProperties}>
        <div className="arena-title"><span>{MODE_IDENTITY[mode].icon}</span><strong>{MODE_IDENTITY[mode].name}</strong>{hybrid && <b>FLAGSHIP</b>}</div>
        <div className="arena-world arena-world-real">
          <div className="arena-hospital"><i /><i /><i /><i /><i /><i /></div>
          <div className="arena-fill"><b>{utilization}%</b><span>Bed utilization</span></div>
          {measuredLowest && <div className="arena-crown">★ LOWEST MEASURED QUEUE</div>}
        </div>
        <div className="arena-score"><span>Unmet <b>{unmet}</b></span><span>Queue <b>{queue}</b></span><span>{mode === 'predictive' ? 'Rule engine' : 'Solver'} <b title="Measured execution time for this policy">{(result?.optimizer_ms ?? 0) < 1 ? (result?.optimizer_ms ?? 0).toFixed(3) : (result?.optimizer_ms ?? 0).toFixed(1)} ms</b></span></div>
      </article>
    })}</div><ExplainableResult comparison={comparison} /></>}
  </section>
}

function ExplainableResult({ comparison }: { comparison: Comparison }) {
  const ranked = MODE_ORDER.map((mode) => ({ mode, ...comparison.results[mode] })).sort((a, b) => {
    if (a.unmet_demand !== b.unmet_demand) return a.unmet_demand - b.unmet_demand
    if (a.final_queue !== b.final_queue) return a.final_queue - b.final_queue
    if (a.nurse_balance !== b.nurse_balance) return a.nurse_balance - b.nurse_balance
    return a.optimizer_ms - b.optimizer_ms
  })
  const winner = ranked[0]
  const runnerUp = ranked[1]
  const queueSaved = runnerUp.unmet_demand - winner.unmet_demand
  const reason = winner.mode === 'hybrid'
    ? 'it combines forecast demand, queue pressure, and nurse rebalancing'
    : winner.mode === 'quantum'
      ? 'its allocation search balances nurse demand across departments'
      : 'its forecast-first allocation rule responds quickly with low overhead'
  const line = queueSaved > 0
    ? `${MODE_IDENTITY[winner.mode].name} wins: it leaves ${winner.unmet_demand} patient-hours unmet versus ${runnerUp.unmet_demand} for ${MODE_IDENTITY[runnerUp.mode].name}, saving ${queueSaved} patient-hours because ${reason}.`
    : `${MODE_IDENTITY[winner.mode].name} wins the close result: queue outcomes tie, so workload balance and solver speed decide the ranking.`
  return <div className="explainable-result"><span>One-line result</span><strong>{line}</strong></div>
}
