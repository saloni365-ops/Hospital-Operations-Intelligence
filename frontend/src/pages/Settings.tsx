import { useState } from 'react'
import { useSimulationStore } from '../store/simulation'

export function Settings() {
  const state = useSimulationStore((store) => store.state)
  const setSettings = useSimulationStore((store) => store.setSettings)
  const reset = useSimulationStore((store) => store.reset)
  const speed = useSimulationStore((store) => store.speed)
  const setSpeed = useSimulationStore((store) => store.setSpeed)
  const [seed, setSeed] = useState(state?.seed ?? 42)
  const [horizon, setHorizon] = useState(state?.horizon ?? 168)
  const dark = useSimulationStore((store) => store.dark)
  const toggleDark = useSimulationStore((store) => store.toggleDark)
  const [sound, setSound] = useState(() => localStorage.getItem('hospital:sound') === 'on')
  const [tourDone, setTourDone] = useState(() => localStorage.getItem('hospital:tour') === 'done')
  const toggleSound = () => { const value = !sound; setSound(value); localStorage.setItem('hospital:sound', value ? 'on' : 'off') }
  const resetTour = () => { localStorage.removeItem('hospital:tour'); setTourDone(false) }
  const finishTour = () => { localStorage.setItem('hospital:tour', 'done'); setTourDone(true) }

  return <section className="page-stage"><header className="page-heading"><div><p>Local preferences</p><h2>Settings</h2></div></header>
    <div className="settings-grid">
      <label><b>Live simulation seed</b><p>Changes the random admissions stream. Restart to rebuild the run from step one.</p><input className="settings-input" type="number" min="0" value={seed} onChange={(event) => setSeed(Number(event.target.value))} /></label>
      <label><b>Simulation horizon</b><p>Number of hours available to the live run.</p><input className="settings-input" type="number" min="1" max="720" value={horizon} onChange={(event) => setHorizon(Number(event.target.value))} /></label>
      <label><b>Simulation speed</b><p>Changes only playback speed; it does not alter the policy results.</p><select className="settings-input" value={speed} onChange={(event) => setSpeed(Number(event.target.value))}><option value={0.5}>0.5x</option><option value={1}>1x</option><option value={2}>2x</option><option value={4}>4x</option></select></label>
      <label><b>Apply live run settings</b><p>Applies seed and horizon while the backend is running.</p><button className="hud-button cyan" onClick={() => void setSettings(seed, horizon)}>Apply settings</button></label>
      <label><b>Restart simulation</b><p>Rebuilds beds and history using the selected seed and horizon.</p><button className="hud-button" onClick={() => void reset(seed)}>Restart now</button></label>
      <label><b>Dark-mode interface</b><p>Uses the same clinical control-room tokens.</p><button className="hud-button" onClick={toggleDark}>{dark ? 'Switch to light' : 'Switch to dark'}</button></label>
      <label><b>Sound effects</b><p>Off by default. This preference is stored locally.</p><button className="hud-button" onClick={toggleSound} aria-pressed={sound}>{sound ? 'Disable sounds' : 'Enable sounds'}</button></label>
      <label><b>Four-step guided tour</b><p>{tourDone ? 'Completed and remembered locally.' : 'Ready to run again.'}</p><button className="hud-button" onClick={tourDone ? resetTour : finishTour}>{tourDone ? 'Reset tour' : 'Finish tour'}</button></label>
      <label><b>Zero queue achievement</b><p>Earned in UI as the run remains at zero waiting patients for 24 hours.</p><span className="status-chip">Badge system active</span></label>
      <label><b>Reduced motion</b><p>The interface follows the operating system preference.</p><span className="status-chip">System managed</span></label>
    </div>
  </section>
}
