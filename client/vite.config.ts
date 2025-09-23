import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Any request that starts with "/api" will be forwarded
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      }
    }
  }
})