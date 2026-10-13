import axios from 'axios'
import router from '@/router'

// Base API mengikuti sub-path deploy: dev '/api', produksi '/manajemen-risiko/api'.
// Bisa dioverride via VITE_API_BASE bila backend berada di origin/host lain.
const apiBase = import.meta.env.VITE_API_BASE || `${import.meta.env.BASE_URL}api`
const api = axios.create({ baseURL: apiBase })

// Endpoint survei publik (router prefix /survei) memakai token undangan
// sendiri — jangan disentuh sesi JWT admin/OPD. Cocokkan awalan path saja agar
// tidak bentrok dengan endpoint admin seperti /cee/survei-hasil.
function isSurvei(url = '') {
  return /^\/?survei(\/|$)/.test(url)
}

// Sisipkan Bearer token JWT bila pengguna login, KECUALI request sudah membawa
// Authorization sendiri (mis. token undangan pada halaman survei).
api.interceptors.request.use((config) => {
  if (config.headers.Authorization || isSurvei(config.url)) return config
  const token = localStorage.getItem('mr_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 401 pada area terproteksi -> paksa login ulang. Halaman publik (survei/login)
// dibiarkan menangani auth-nya sendiri.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response?.status
    const url = err.config?.url || ''
    const onPublicPage = router.currentRoute.value.meta?.public
    if (status === 401 && !url.includes('/auth/login') && !isSurvei(url) && !onPublicPage) {
      localStorage.removeItem('mr_token')
      localStorage.removeItem('mr_user')
      if (router.currentRoute.value.name !== 'login') {
        router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
      }
    }
    return Promise.reject(err)
  },
)

export default api
