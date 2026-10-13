import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { title: 'Login', public: true, guestOnly: true } },
  { path: '/survei', name: 'survei', component: () => import('@/views/Survei.vue'), meta: { title: 'Survei CEE', public: true } },
  { path: '/lapor-kejadian', name: 'lapor-kejadian', component: () => import('@/views/LaporKejadian.vue'), meta: { title: 'Lapor Kejadian Risiko', public: true } },
  { path: '/dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: 'Dashboard' } },
  { path: '/laporan', name: 'laporan', component: () => import('@/views/Laporan.vue'), meta: { title: 'Cetak Laporan / Print Preview' } },
  { path: '/generate-rtp', name: 'generate-rtp', component: () => import('@/views/GenerateRtp.vue'), meta: { title: 'Generate Dokumen RTP' } },
  { path: '/rekapitulasi', name: 'rekapitulasi', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Laporan Rekapitulasi' } },
  { path: '/rekap-kuesioner', name: 'rekap-kuesioner', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Kuesioner', tab: 'kuesioner' } },
  { path: '/rekap-konteks', name: 'rekap-konteks', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Konteks Risiko', tab: 'konteks' } },
  { path: '/rekap-identifikasi', name: 'rekap-identifikasi', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Kategori Risiko', tab: 'identifikasi' } },
  { path: '/rekap-level', name: 'rekap-level', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Level Risiko', tab: 'level' } },
  { path: '/rekap-kepatuhan', name: 'rekap-kepatuhan', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Kepatuhan OPD', tab: 'kepatuhan' } },
  { path: '/rekap-rtp', name: 'rekap-rtp', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Realisasi RTP', tab: 'rtp' } },
  { path: '/rekap-event', name: 'rekap-event', component: () => import('@/views/LaporanRekapitulasi.vue'), meta: { title: 'Rekapitulasi Keterjadian Risiko', tab: 'risk_event' } },

  { path: '/form1a', name: 'form1a', component: () => import('@/views/Form1a.vue'), meta: { title: 'Form 1.a — Kuesioner CEE (Persepsi)' } },
  { path: '/form1b', name: 'form1b', component: () => import('@/views/Form1b.vue'), meta: { title: 'Form 1.b — Reviu Dokumen CEE' } },
  { path: '/form1c', name: 'form1c', component: () => import('@/views/Form1c.vue'), meta: { title: 'Form 1.c — Simpulan CEE' } },
  { path: '/survei-hasil', name: 'survei-hasil', component: () => import('@/views/SurveiHasil.vue'), meta: { title: 'Rincian Hasil Survei CEE' } },
  { path: '/form6', name: 'form6', component: () => import('@/views/Form6.vue'), meta: { title: 'Form 6 — RTP atas CEE' } },

  { path: '/konteks', name: 'konteks', component: () => import('@/views/PenetapanKonteks.vue'), meta: { title: 'Penetapan Konteks Risiko' } },
  { path: '/form2a', redirect: () => ({ name: 'konteks', query: { tab: '2a' } }) },
  { path: '/form2b', redirect: () => ({ name: 'konteks', query: { tab: '2b' } }) },
  { path: '/form2c', redirect: () => ({ name: 'konteks', query: { tab: '2c' } }) },

  { path: '/kamus-risiko', name: 'kamus-risiko', component: () => import('@/views/KamusRisiko.vue'), meta: { title: 'Kamus Risiko' } },
  { path: '/identifikasi-risiko', name: 'identifikasi-risiko', component: () => import('@/views/IdentifikasiRisiko.vue'), meta: { title: 'Identifikasi Risiko' } },
  { path: '/form3a', redirect: () => ({ name: 'identifikasi-risiko', query: { tab: '3a' } }) },
  { path: '/form3b', redirect: () => ({ name: 'identifikasi-risiko', query: { tab: '3b' } }) },
  { path: '/form3c', redirect: () => ({ name: 'identifikasi-risiko', query: { tab: '3c' } }) },
  { path: '/form4', name: 'form4', component: () => import('@/views/Form4.vue'), meta: { title: 'Form 4 — Analisis Risiko' } },
  { path: '/matriks', name: 'matriks', component: () => import('@/views/Matriks.vue'), meta: { title: 'Matriks Risiko' } },
  { path: '/form5', name: 'form5', component: () => import('@/views/Form5.vue'), meta: { title: 'Form 5 — Daftar Risiko Prioritas' } },
  { path: '/form7', name: 'form7', component: () => import('@/views/Form7.vue'), meta: { title: 'Form 7 — RTP atas Risiko' } },

  { path: '/form8', name: 'form8', component: () => import('@/views/Form8.vue'), meta: { title: 'Form 8 — Informasi & Komunikasi' } },
  { path: '/form9', name: 'form9', component: () => import('@/views/Form9.vue'), meta: { title: 'Form 9 — Rencana Pemantauan PI' } },
  { path: '/form10', name: 'form10', component: () => import('@/views/Form10.vue'), meta: { title: 'Form 10 — Monitoring Risk Event & RTP' } },
  { path: '/approval-kejadian', name: 'approval-kejadian', component: () => import('@/views/ApprovalKejadian.vue'), meta: { title: 'Approval Kejadian Risiko' } },

  { path: '/kelola-kuesioner', name: 'kelola-kuesioner', component: () => import('@/views/KelolaKuesioner.vue'), meta: { title: 'Kelola Kuesioner CEE', admin: true } },
  { path: '/pengaturan', name: 'pengaturan', component: () => import('@/views/Pengaturan.vue'), meta: { title: 'Pengaturan Aplikasi', admin: true } },
]

const router = createRouter({
  // BASE_URL = '/manajemen-risiko/' saat produksi, '/' saat dev (lihat vite.config).
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Guard autentikasi: rute non-publik butuh token; rute guest (login) dialihkan
// bila sudah login. Impor store di dalam guard agar Pinia sudah terpasang.
router.beforeEach(async (to) => {
  const { useAuthStore } = await import('@/stores/auth')
  const auth = useAuthStore()
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && !auth.isAdmin) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
