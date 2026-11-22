import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { ControlRoom } from './pages/ControlRoom'
import { Arena } from './pages/Arena'
import { Dashboard } from './pages/Dashboard'
import { FailureLab } from './pages/FailureLab'
import { Methodology } from './pages/Methodology'
import { Settings } from './pages/Settings'
import { useSimulationStore } from './store/simulation'
import { MODE_ORDER } from './constants/modes'
import './style.css'

const nav = [
  { path: '/control', label: 'Control Room', icon: '⌂', key: 'G' },
  { path: '/arena', label: 'Arena', icon: '⚔', key: 'A' },
  { path: '/dashboard', label: 'Dashboard', icon: '▥', key: 'D' },
  { path: '/failures', label: 'Failure Lab', icon: '⚠', key: 'F' },
  { path: '/methodology', label: 'Methodology', icon: '⌁' },
  { path: '/settings', label: 'Settings', icon: '⚙' },
]

function AppShell() {
  const state = useSimulationStore((store) => store.state)
  const online = useSimulationStore((store) => store.online)
  const refresh = useSimulationStore((store) => store.refresh)
  const speed = useSimulationStore((store) => store.speed)
  const step = useSimulationStore((store) => store.step)
  const start = useSimulationStore((store) => store.start)
  const pause = useSimulationStore((store) => store.pause)
  const setMode = useSimulationStore((store) => store.setMode)
  const toggleDark = useSimulationStore((store) => store.toggleDark)
  const navigate = useNavigate()

  useEffect(() => { void refresh(); const refreshTimer = window.setInterval(() => void refresh(), 1000); return () => window.clearInterval(refreshTimer) }, [refresh])
  useEffect(() => {
    if (!state?.running) return
    const stepTimer = window.setInterval(() => void step(), 1000 / speed)
    return () => window.clearInterval(stepTimer)
  }, [state?.running, speed, step])
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement) return
      if (event.code === 'Space') { event.preventDefault(); state?.running ? void pause() : void start() }
      if (event.key.toLowerCase() === 's') void step()
      if (event.key === '1') void setMode(MODE_ORDER[2])
      if (event.key === '2') void setMode(MODE_ORDER[1])
      if (event.key === '3') void setMode(MODE_ORDER[0])
      const destinations: Record<string, string> = { g: '/control', a: '/arena', d: '/dashboard', f: '/failures' }
      const destination = destinations[event.key.toLowerCase()]
      if (destination) { event.preventDefault(); navigate(destination) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [state?.running, start, pause, step, setMode, navigate])

  const clock = state ? `DAY ${Math.floor(state.step / 24) + 1} · ${String(state.step % 24).padStart(2, '0')}:00` : 'CONNECTING'
  return <main className="app-frame">
    <nav className="nav-dock" aria-label="Primary pages">
      <div className="nav-brand" aria-label="Hospital Operations Intelligence">HI</div>
      {nav.map((item) => <NavLink key={item.path} to={item.path} className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'} title={`${item.label}${item.key ? ` (${item.key})` : ''}`}><span>{item.icon}</span><small>{item.label}</small></NavLink>)}
      <button className="nav-item nav-theme" onClick={toggleDark} title="Toggle dark mode"><span>◐</span><small>Theme</small></button>
    </nav>
    <section className="hud-shell">
      <header className="hud-topbar">
        <div><p className="hud-kicker">OPERATIONS INTELLIGENCE</p><h1>Hospital Control Room</h1></div>
        <div className="live-ticker"><span className={online ? 'status-live' : 'status-offline'}>{online ? '● LIVE' : '● OFFLINE'}</span><strong>{clock}</strong><b>{state?.mode ? state.mode.toUpperCase() : ''} {state?.running ? 'RUNNING' : 'PAUSED'}</b></div>
      </header>
      <Routes>
        <Route path="/control" element={<ControlRoom />} />
        <Route path="/arena" element={<Arena />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/failures" element={<FailureLab />} />
        <Route path="/methodology" element={<Methodology />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/control" replace />} />
      </Routes>
    </section>
  </main>
}

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><BrowserRouter><AppShell /></BrowserRouter></React.StrictMode>)
