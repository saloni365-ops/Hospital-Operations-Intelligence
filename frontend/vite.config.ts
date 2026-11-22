import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: false,
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          plotly: ['react-plotly.js', 'plotly.js-dist-min'],
          phaser: ['phaser'],
          router: ['react-router-dom'],
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    clearMocks: true,
  },
})
