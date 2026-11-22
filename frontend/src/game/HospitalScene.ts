import Phaser from 'phaser'
import type { HospitalState } from '../api/client'
import { AssetProvider } from './AssetProvider'

const WARD_COLORS = ['#3B82F6', '#FF5C6C', '#FFB020', '#7C5CFF']

export class HospitalScene extends Phaser.Scene {
  private current: HospitalState | null = null
  private objects: Phaser.GameObjects.Container[] = []
  private overlay: 'occupancy' | 'nurses' | 'queue' = 'occupancy'

  constructor() { super('hospital') }

  create() {
    AssetProvider.generate(this)
    this.drawMap()

    this.input.on('wheel', (_pointer: unknown, _objects: unknown, _dx: number, dy: number) => {
      const camera = this.cameras.main
      camera.zoom = Phaser.Math.Clamp(camera.zoom * (dy > 0 ? 0.92 : 1.08), 0.7, 1.8)
    })
    const camera = this.cameras.main
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => { if (pointer.rightButtonDown()) camera.setScroll(camera.scrollX - pointer.velocity.x * 0.02, camera.scrollY - pointer.velocity.y * 0.02) })
    this.input.mouse?.disableContextMenu()
  }

  setState(state: HospitalState | null) { this.current = state; if (this.scene.isActive()) this.drawMap() }
  setOverlay(value: 'occupancy' | 'nurses' | 'queue') { this.overlay = value; this.drawMap() }
  zoom(delta: number) { this.cameras.main.zoom = Phaser.Math.Clamp(this.cameras.main.zoom + delta, 0.7, 1.8) }
  resetCamera() { this.cameras.main.setZoom(1); this.cameras.main.centerOn(420, 300) }

  private iso(x: number, y: number) { return { x: 420 + (x - y) * 34, y: 70 + (x + y) * 17 } }

  private drawMap() {
    if (this.objects.length) {
      this.objects.forEach((object) => object.destroy(true));
      this.objects = []
    }

    const lawn = this.add.graphics(); lawn.fillStyle(0xD8F0E4).fillRect(0, 0, 840, 500); this.objects.push(this.add.container(0, 0, [lawn]))

    for (let y = -1; y <= 8; y++) {
      for (let x = -1; x <= 11; x++) {
        const p = this.iso(x, y)
        const tile = this.add.image(p.x, p.y, 'iso-floor').setOrigin(0.5, 0.5)
        tile.setDepth(p.y)
        this.objects.push(this.add.container(0, 0, [tile]))
      }
    }

    const wards = this.current?.departments ?? [
      { name: 'General Medicine', occupied: 0, capacity: 18, nurses: 8, queue: 0, forecast: 0, arrivals: 0, beds: [] },
      { name: 'Cardiology', occupied: 0, capacity: 12, nurses: 6, queue: 0, forecast: 0, arrivals: 0, beds: [] },
      { name: 'Orthopedics', occupied: 0, capacity: 14, nurses: 6, queue: 0, forecast: 0, arrivals: 0, beds: [] },
      { name: 'Neurology', occupied: 0, capacity: 10, nurses: 5, queue: 0, forecast: 0, arrivals: 0, beds: [] },
    ]

    const wardPositions = [[2, 2], [7, 2], [2, 6], [7, 6]]
    wards.forEach((ward, index) => {
      const [x, y] = wardPositions[index]
      const p = this.iso(x, y)
      const g = this.add.graphics()
      g.fillStyle(Phaser.Display.Color.HexStringToColor(WARD_COLORS[index]).color, 0.14)
      g.fillPoints([new Phaser.Math.Vector2(p.x, p.y - 42), new Phaser.Math.Vector2(p.x + 85, p.y), new Phaser.Math.Vector2(p.x, p.y + 42), new Phaser.Math.Vector2(p.x - 85, p.y)], true)
      g.lineStyle(2, Phaser.Display.Color.HexStringToColor(WARD_COLORS[index]).color, 0.9)
      g.strokePoints([new Phaser.Math.Vector2(p.x, p.y - 42), new Phaser.Math.Vector2(p.x + 85, p.y), new Phaser.Math.Vector2(p.x, p.y + 42), new Phaser.Math.Vector2(p.x - 85, p.y)], true)
      g.setDepth(p.y - 5)
      this.objects.push(this.add.container(0, 0, [g]))

      const ratio = ward.capacity ? ward.occupied / ward.capacity : 0
      const label = this.add.text(p.x, p.y - 76, `${ward.name}\n${ward.occupied}/${ward.capacity} BEDS  ·  ${ward.nurses} RN`, { fontFamily: 'Inter, sans-serif', fontSize: '12px', color: '#14213D', backgroundColor: '#FFFFFF', align: 'center', padding: { x: 9, y: 6 }, resolution: 2 })
        .setOrigin(0.5).setDepth(p.y + 100)
      this.objects.push(this.add.container(0, 0, [label]))

      const beds = ward.beds.length ? ward.beds : Array.from({ length: Math.min(ward.capacity, 6) }, () => 'available')
      beds.slice(0, 6).forEach((status, bedIndex) => {
        const bx = x + (bedIndex % 3) * 0.75
        const by = y + Math.floor(bedIndex / 3) * 0.75
        const bp = this.iso(bx, by)
        const key = status === 'occupied' ? 'iso-bed-occupied' : status === 'unavailable' ? 'iso-bed-unavailable' : 'iso-bed-available'
        const bed = this.add.image(bp.x, bp.y - 8, key).setScale(0.8).setDepth(bp.y)
        this.objects.push(this.add.container(0, 0, [bed]))
      })

      if (ratio > 0.9) {
        const siren = this.add.circle(p.x + 72, p.y - 72, 6, 0xFF5C6C).setDepth(p.y + 120)
        this.tweens.add({ targets: siren, alpha: 0.25, scale: 1.5, yoyo: true, repeat: -1, duration: 550 })
        this.objects.push(this.add.container(0, 0, [siren]))
      }

      const nurseCount = this.overlay === 'nurses' ? Math.max(1, ward.nurses) : 2
      for (let n = 0; n < nurseCount; n++) {
        const np = this.iso(x + 0.2 + n * 0.4, y + 1)
        const nurse = this.add.image(np.x, np.y, 'nurse').setDepth(np.y + 40)
        this.tweens.add({ targets: nurse, x: np.x + (n % 2 ? 16 : -16), yoyo: true, repeat: -1, duration: 1800 + n * 250 })
        this.objects.push(this.add.container(0, 0, [nurse]))
      }
    })

    const reception = this.iso(5, 8)
    const desk = this.add.image(reception.x, reception.y, 'reception').setScale(1.2).setDepth(reception.y)
    const ambulance = this.add.image(reception.x - 95, reception.y - 15, 'ambulance').setScale(0.85).setDepth(reception.y - 10)
    const queueText = this.add.text(reception.x + 38, reception.y - 42, `QUEUE ${this.current?.metrics?.unmet_demand ?? 0}`, { fontFamily: 'JetBrains Mono, monospace', fontSize: '11px', color: '#FFFFFF', backgroundColor: '#0F1B33', padding: { x: 8, y: 5 }, resolution: 2 }).setDepth(reception.y + 100)
    const receptionLabel = this.add.text(reception.x - 5, reception.y + 38, 'RECEPTION · AMBULANCE BAY', { fontFamily: 'Inter, sans-serif', fontSize: '10px', color: '#14213D', backgroundColor: '#FFFFFF', padding: { x: 7, y: 4 }, resolution: 2 }).setOrigin(0.5).setDepth(reception.y + 100)
    this.objects.push(this.add.container(0, 0, [desk, ambulance, queueText, receptionLabel]))

    const active = this.current?.events?.filter((event: any) => event.kind === 'surge').length ?? 0
    if (active) {
      const flash = this.add.rectangle(420, 250, 840, 500, 0xFF5C6C, 0.08).setDepth(1000)
      this.tweens.add({ targets: flash, alpha: 0, yoyo: true, repeat: 2, duration: 350 })
      this.objects.push(this.add.container(0, 0, [flash]))
    }

    this.cameras.main.setBounds(0, 0, 840, 500)
  }
}