import { useEffect, useRef, useState } from 'react'
import Phaser from 'phaser'
import type { HospitalState } from '../api/client'
import { HospitalScene } from './HospitalScene'

export function HospitalView({ state }: { state: HospitalState | null }) {
  const host = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<HospitalScene | null>(null)
  const [overlay, setOverlay] = useState<'occupancy' | 'nurses' | 'queue'>('occupancy')

  useEffect(() => {
    if (!host.current) return
    const game = new Phaser.Game({ type: Phaser.CANVAS, width: 840, height: 500, parent: host.current, backgroundColor: '#EAF0F8', scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH }, scene: [HospitalScene], render: { antialias: true } })
    game.events.once('ready', () => { sceneRef.current = game.scene.getScene('hospital') as HospitalScene; sceneRef.current.setState(state) })
    return () => { sceneRef.current = null; game.destroy(true) }
  }, [])

  useEffect(() => { sceneRef.current?.setState(state) }, [state])
  useEffect(() => { sceneRef.current?.setOverlay(overlay) }, [overlay])

  const zoom = (delta: number) => sceneRef.current?.zoom(delta)
  return <div className="world-wrap">
    <div className="hospital-canvas" ref={host} aria-label="Interactive dimetric isometric hospital ward map" />
    <div className="overlay-toolbar" aria-label="Map overlays">
      <button className={overlay === 'occupancy' ? 'active' : ''} onClick={() => setOverlay('occupancy')} title="Occupancy heatmap">▦ <span>Occupancy</span></button>
      <button className={overlay === 'nurses' ? 'active' : ''} onClick={() => setOverlay('nurses')} title="Nurse workload overlay">♟ <span>Nurses</span></button>
      <button className={overlay === 'queue' ? 'active' : ''} onClick={() => setOverlay('queue')} title="Queue overlay">≡ <span>Queue</span></button>
    </div>
    <div className="zoom-toolbar" aria-label="Camera zoom"><button onClick={() => zoom(0.1)} title="Zoom in">+</button><button onClick={() => zoom(-0.1)} title="Zoom out">−</button><button onClick={() => sceneRef.current?.resetCamera()} title="Reset camera">⌂</button></div>
  </div>
}