import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use backend container name when running in Docker
const backendUrl = process.env.DOCKER_ENV ? 'http://backend:8000' : 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/videos': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
