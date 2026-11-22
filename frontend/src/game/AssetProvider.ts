import Phaser from 'phaser'

export class AssetProvider {
  static generate(scene: Phaser.Scene) {
    const g = scene.make.graphics({ x: 0, y: 0 })

    g.clear().fillStyle(0xEEF3F8).fillRect(0, 0, 64, 32)
    g.lineStyle(1, 0xD7E1EC).moveTo(32, 0).lineTo(64, 16).moveTo(32, 32).lineTo(64, 16).moveTo(32, 0).lineTo(0, 16).moveTo(32, 32).lineTo(0, 16).strokePath()
    g.generateTexture('iso-floor', 64, 32)

    const colors = [0x3B82F6, 0xFF5C6C, 0xFFB020, 0x7C5CFF]
    colors.forEach((color, index) => {
      g.clear().fillStyle(color, 0.16).fillRect(0, 0, 64, 32)
      g.fillStyle(color).fillTriangle(32, 0, 64, 16, 32, 32)
      g.generateTexture(`iso-ward-${index}`, 64, 32)
    })

    g.clear().fillStyle(0xFFFFFF).fillRoundedRect(0, 0, 48, 26, 5)
    g.fillStyle(0xFF5C6C).fillRect(5, 7, 38, 5)
    g.generateTexture('iso-bed-occupied', 48, 26)

    g.clear().fillStyle(0xFFFFFF).fillRoundedRect(0, 0, 48, 26, 5)
    g.fillStyle(0x2FBF71).fillRect(5, 7, 38, 5)
    g.generateTexture('iso-bed-available', 48, 26)

    g.clear().fillStyle(0x9AA5B8).fillRoundedRect(0, 0, 48, 26, 5)
    g.lineStyle(2, 0xFFFFFF).moveTo(8, 5).lineTo(40, 21).strokePath()
    g.generateTexture('iso-bed-unavailable', 48, 26)

    g.clear().fillStyle(0x3B82F6).fillCircle(8, 8, 8)
    g.fillStyle(0xEAF2FF).fillCircle(8, 7, 3)
    g.generateTexture('patient', 16, 16)

    g.clear().fillStyle(0x12B5A6).fillCircle(8, 8, 8)
    g.fillStyle(0xFFFFFF).fillRect(6, 5, 4, 8)
    g.generateTexture('nurse', 16, 16)

    g.clear().fillStyle(0xF8FAFF).fillRoundedRect(0, 5, 72, 32, 8)
    g.fillStyle(0x3B82F6).fillRect(8, 12, 56, 14)
    g.fillStyle(0xFF5C6C).fillRect(0, 16, 72, 5)
    g.generateTexture('ambulance', 72, 42)

    g.clear().fillStyle(0xFFFFFF).fillRoundedRect(0, 0, 52, 30, 6)
    g.fillStyle(0x51607A).fillCircle(13, 12, 5)
    g.fillStyle(0x22D3EE).fillCircle(39, 12, 5)
    g.generateTexture('reception', 52, 30)

    g.destroy()
  }
}
