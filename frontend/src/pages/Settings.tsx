import { useState } from 'react'
import { useSimulationStore } from '../store/simulation'

export function Settings() {
  const dark = useSimulationStore((store) => store.dark)
  const toggleDark = useSimulationStore((store) => store.toggleDark)
  const [sound, setSound] = useState(() => localStorage.getItem('hospital:sound') === 'on')
  const [tourDone, setTourDone] = useState(() => localStorage.getItem('hospital:tour') === 'done')
  const toggleSound = () => { const value = !sound; setSound(value); localStorage.setItem('hospital:sound', value ? 'on' : 'off') }
  const resetTour = () => { localStorage.removeItem('hospital:tour'); setTourDone(false) }
  const finishTour = () => { localStorage.setItem('hospital:tour', 'done'); setTourDone(true) }

  return <section className="page-stage"><header className="page-heading"><div><p>Local preferences</p><h2>Settings</h2></div></header>
    <div className="settings-grid">
      <label><b>Dark-mode interface</b><p>Uses the same clinical control-room tokens.</p><button className="hud-button" onClick={toggleDark}>{dark ? 'Switch to light' : 'Switch to dark'}</button></label>
      <label><b>Sound effects</b><p>Off by default. This preference is stored locally.</p><button className="hud-button" onClick={toggleSound} aria-pressed={sound}>{sound ? 'Disable sounds' : 'Enable sounds'}</button></label>
      <label><b>Four-step guided tour</b><p>{tourDone ? 'Completed and remembered locally.' : 'Ready to run again.'}</p><button className="hud-button" onClick={tourDone ? resetTour : finishTour}>{tourDone ? 'Reset tour' : 'Finish tour'}</button></label>
      <label><b>Zero queue achievement</b><p>Earned in UI as the run remains at zero waiting patients for 24 hours.</p><span className="status-chip">Badge system active</span></label>
      <label><b>Reduced motion</b><p>The interface follows the operating system preference.</p><span className="status-chip">System managed</span></label>
    </div>
  </section>
}
