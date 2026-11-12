import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// Produksi dilayani di sub-path https://monevrkpd.tegalkota.go.id/manajemen-risiko/
// Base hanya diterapkan saat build agar dev server (proxy /api) tetap di root.
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const appBase = env.VITE_APP_BASE || '/manajemen-risiko/'
  return {
    base: command === 'build' ? `${appBase.replace(/\/$/, '')}/` : '/',
    plugins: [vue()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },
    server: {
      port: 5173,
      proxy: {
        '/api': { target: 'http://127.0.0.1:2707', changeOrigin: true },
      },
    },
  }
})
