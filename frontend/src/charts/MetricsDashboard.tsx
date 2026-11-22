import Plot from 'react-plotly.js'
import type { Comparison, HospitalState } from '../api/client'
import { MODE_IDENTITY, MODE_ORDER } from '../constants/modes'

export function MetricsDashboard({ state, comparison, onCompare, busy }: { state: HospitalState | null; comparison: Comparison | null; onCompare: () => void; busy: boolean }) {
  const history = state?.history ?? []
  const hasHistory = history.length > 0
  const steps = history.map((row) => row.step)
  const departments = state?.departments.map((item) => item.name) ?? []
  const common: Partial<Plotly.Layout> = {
    autosize: true,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, sans-serif', color: '#51607A', size: 11 },
    margin: { l: 66, r: 24, t: 22, b: 54 },
    xaxis: { title: { text: 'Simulated hour', font: { size: 12 } }, tickfont: { size: 11 }, gridcolor: '#E3EAF4', zeroline: false, range: hasHistory ? [Math.max(0, steps[0] ?? 0), Math.max(1, steps.at(-1) ?? 1)] as [number, number] : [0, 24] as [number, number] },
    yaxis: { title: { font: { size: 12 } }, tickfont: { size: 11 }, gridcolor: '#E3EAF4', zeroline: false, rangemode: 'tozero' as const },
  }

  if (!hasHistory) return <section className="analytics-section"><div className="illustrated-empty chart-empty"><div className="empty-graph">▥</div><h3>No simulation samples yet</h3><p>Run the hospital to populate forecast, utilization, queue, workload and solver charts.</p></div></section>

  return <section className="analytics-section">
    <div className="chart-grid">
      <article className="chart-panel wide"><div className="chart-label"><strong>Admissions: forecast vs actual</strong><span>PATIENTS / HOUR</span></div><Plot data={departments.flatMap((department, index) => [{ x: steps, y: history.map((row) => row.arrivals[department]), type: 'scatter' as const, mode: 'lines' as const, name: `${department} actual`, line: { color: ['#3B82F6', '#FF5C6C', '#FFB020', '#7C5CFF'][index], width: 2 } }, { x: steps, y: history.map((row) => row.forecast[department]), type: 'scatter' as const, mode: 'lines' as const, name: `${department} forecast`, line: { color: ['#3B82F6', '#FF5C6C', '#FFB020', '#7C5CFF'][index], width: 1, dash: 'dot' as const } }])} layout={{ ...common, yaxis: { ...common.yaxis, title: { text: 'Arrivals (patients/hour)' }, range: [0, 12] }, legend: { orientation: 'h', y: -0.28 } }} useResizeHandler style={{ width: '100%', height: '230px' }} config={{ displayModeBar: false, responsive: true }} /></article>
      <article className="chart-panel"><div className="chart-label"><strong>Bed utilization</strong><span>PERCENT</span></div><Plot data={[{ x: steps, y: history.map((row) => row.utilization * 100), type: 'scatter', mode: 'lines', line: { color: '#2FBF71', width: 2 }, fill: 'tozeroy', fillcolor: 'rgba(47,191,113,.12)' }]} layout={{ ...common, yaxis: { ...common.yaxis, title: { text: 'Utilization (%)' }, range: [0, 100] } }} useResizeHandler style={{ width: '100%', height: '210px' }} config={{ displayModeBar: false, responsive: true }} /></article>
      <article className="chart-panel"><div className="chart-label"><strong>Queue and workload</strong><span>PATIENTS / σ</span></div><Plot data={[{ x: steps, y: history.map((row) => row.unmet_demand), type: 'scatter', mode: 'lines', name: 'Waiting queue', line: { color: '#FF5C6C', width: 2 } }, { x: steps, y: history.map((row) => row.nurse_balance), type: 'scatter', mode: 'lines', name: 'Workload σ', yaxis: 'y2', line: { color: '#3B82F6', width: 2 } }]} layout={{ ...common, yaxis: { ...common.yaxis, title: { text: 'Waiting patients' } }, yaxis2: { title: { text: 'Workload σ' }, overlaying: 'y', side: 'right', gridcolor: 'transparent', rangemode: 'tozero' }, legend: { orientation: 'h', y: -0.28 } }} useResizeHandler style={{ width: '100%', height: '210px' }} config={{ displayModeBar: false, responsive: true }} /></article>
      <article className="chart-panel"><div className="chart-label"><strong>Solver runtime</strong><span>LOG SCALE · ms</span></div><Plot data={[{ x: steps, y: history.map((row) => Math.max(row.optimizer_ms, 0.01)), type: 'scatter', mode: 'lines', line: { color: MODE_IDENTITY[state?.mode ?? 'hybrid'].color, width: 2 } }]} layout={{ ...common, yaxis: { ...common.yaxis, title: { text: 'Runtime (ms)' }, type: 'log', rangemode: 'tozero' } }} useResizeHandler style={{ width: '100%', height: '210px' }} config={{ displayModeBar: false, responsive: true }} /></article>
      <article className="chart-panel comparison-panel"><div className="chart-label"><strong>Matched scenario comparison</strong><span>{comparison ? `${comparison.horizon} H · SEED ${comparison.seed}` : 'AWAITING RUN'}</span></div>{comparison ? <Plot data={[{ x: MODE_ORDER.map((mode) => MODE_IDENTITY[mode].shortName), y: MODE_ORDER.map((mode) => comparison.results[mode].unmet_demand), type: 'bar' as const, text: MODE_ORDER.map((mode) => `${comparison.results[mode].unmet_demand} patient-hours`), textposition: 'outside' as const, marker: { color: MODE_ORDER.map((mode) => MODE_IDENTITY[mode].color) }, cliponaxis: false }]} layout={{ ...common, margin: { l: 66, r: 16, t: 30, b: 62 }, xaxis: { title: { text: 'Decision mode', font: { size: 12 } }, tickfont: { size: 11 }, fixedrange: true, gridcolor: 'transparent' }, yaxis: { ...common.yaxis, title: { text: 'Unmet demand (patient-hours)', font: { size: 12 } }, tickfont: { size: 11 }, rangemode: 'tozero', automargin: true }, bargap: 0.35, showlegend: false }} useResizeHandler style={{ width: '100%', height: '210px' }} config={{ displayModeBar: false, responsive: true }} /> : <button className="comparison-empty" onClick={onCompare} disabled={busy}>Run all three modes on identical seeded conditions <span>→</span></button>}</article>
    </div>
  </section>
}