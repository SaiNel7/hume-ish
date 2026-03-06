import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy /chat/* to the FastAPI backend in dev so the browser never
    // needs to know the backend URL — no CORS issues and no API URL
    // hardcoded in the JS bundle.
    proxy: {
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
