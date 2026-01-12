import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 13000,
    host: '0.0.0.0',
    proxy: {
      '/api': 'http://localhost:13001',
      '/health': 'http://localhost:13001',
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
