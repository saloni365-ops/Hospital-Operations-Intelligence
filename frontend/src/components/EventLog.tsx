import type { DepartmentState } from '../api/client'
export function EventLog({ events, departments }: { events: string[]; departments: DepartmentState[] }) {
  const alerts = departments.filter(department => department.capacity && department.occupied / department.capacity > 0.85)
  const feed = events.length ? events : ['Hospital is open — dynamic hybrid monitoring is ready']
  return <section className="event-panel"><div className="section-heading compact"><div><p className="eyebrow">SYSTEM FEED</p><h2>Decision feed</h2></div><span className="feed-count">{feed.length.toString().padStart(2, '0')}</span></div>
    {alerts.map(alert => <div className="alert-row" key={alert.name}><span className="alert-icon">!</span><div><strong>{alert.name} near capacity</strong><small>{alert.occupied} occupied of {alert.capacity} beds</small></div></div>)}
    <div className="feed-list">{[...feed].reverse().map((event, index) => <div className="feed-entry" key={`${event}-${index}`}><span className="feed-pin" /><p>{event}</p></div>)}</div>
    <div className="mode-note"><span className="note-mark">i</span><p><strong>Mode brain</strong><br />Forecast pressure: live admissions · QUBO: local neal · solver runtime: measured</p></div>
  </section>
}