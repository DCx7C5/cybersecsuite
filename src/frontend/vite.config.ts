import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  base: '/static/react/',
  build: {
    outDir: '../dashboard/static/react',
    emptyOutDir: true,
    assetsDir: 'assets',
  },
  server: {
    host: true,
    proxy: {
      '/api': process.env.BACKEND_URL ?? 'http://localhost:8000',
      '/sse': process.env.BACKEND_URL ?? 'http://localhost:8000',
      '/ts':  process.env.BACKEND_URL ?? 'http://localhost:8000',
    },
  },
})
