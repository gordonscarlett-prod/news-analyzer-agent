import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.PORT) || 5174,
    allowedHosts: true,
    proxy: {
      '/api': 'http://localhost:8010',
    },
  },
})
