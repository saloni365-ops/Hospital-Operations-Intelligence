import { useState } from 'react'
import type { EventKind } from '../api/client'
import { MODE_IDENTITY, MODE_ORDER, type Mode } from '../constants/modes'
import { useSimulationStore } from '../store/simulation'

export function ControlPanel({ state }: { state: any }) {
  const [seed, setSeed] = useState(state?.seed ?? 42)
  const running = state?.running ?? false
  const mode = useSimulationStore((store) => store.mode)
  const speed = useSimulationStore((store) => store.speed)
  const busy = useSimulationStore((store) => store.busy)
  const start = useSimulationStore((store) => store.start)
  const pause = useSimulationStore((store) => store.pause)
  const reset = useSimulationStore((store) => store.reset)
  const step = useSimulationStore((store) => store.step)
  const setMode = useSimulationStore((store) => store.setMode)
  const setSpeed = useSimulationStore((store) => store.setSpeed)

  const inject = async (kind: EventKind, department?: string) => {
    const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
    await fetch(`${base}/simulation/events`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ kind, department, duration: 8, magnitude: 0.3 }) })
  }

  return <div className="controls">
    <div className="transport"><button className="icon-button" onClick={() => void reset(seed)} title="Reset simulation" aria-label="Reset simulation">↺</button>{running ? <button className="primary-button" onClick={() => void pause()} disabled={busy}>Ⅱ Pause</button> : <button className="primary-button" onClick={() => void start(seed)} disabled={busy}>▶ Run</button>}<button className="icon-button" onClick={() => void step()} title="Advance one hour" aria-label="Advance one hour">›</button></div>
    <div className="speed-control"><span>SPEED</span><div className="speed-segments">{[0.5, 1, 2, 4].map((value) => <button key={value} className={speed === value ? 'active' : ''} onClick={() => setSpeed(value)} aria-pressed={speed === value}>{value}×</button>)}</div></div>
    <label className="seed-control"><span>SEED</span><input type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} /></label>
    <div className="mode-control"><div className="segmented">{MODE_ORDER.map((value: Mode) => <button key={value} className={mode === value ? 'selected' : ''} style={{ borderColor: mode === value ? MODE_IDENTITY[value].color : undefined }} onClick={() => void setMode(value)} title={MODE_IDENTITY[value].description}><span>{MODE_IDENTITY[value].icon}</span> {MODE_IDENTITY[value].name}{value === 'hybrid' && <b> Flagship</b>}</button>)}</div></div>
    <div className="disruption-control"><div className="event-buttons"><button onClick={() => void inject('surge')} title="Admissions surge for 8 hours">⚡ Surge</button><button onClick={() => void inject('nurse_unavailable', 'General Medicine')} title="Remove nurses from a shift">✚ Nurses</button><button onClick={() => void inject('bed_closure', 'Cardiology')} title="Close cardiology beds temporarily">▣ Beds</button><button onClick={() => void inject('ed_overload')} title="Create an emergency-department overload">▲ ED overload</button></div></div>
  </div>
}