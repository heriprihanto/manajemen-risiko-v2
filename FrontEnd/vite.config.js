import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Produksi dilayani di sub-path https://monevrkpd.tegalkota.go.id/manajemen-risiko/
// Base hanya diterapkan saat build agar dev server (proxy /api) tetap di root.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/manajemen-risiko/' : '/',
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8077', changeOrigin: true },
    },
  },
}))
