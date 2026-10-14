<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import AppLoader from '@/components/AppLoader.vue'
import { useContextStore } from '@/stores/context'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const ctx = useContextStore()
const auth = useAuthStore()
const base = import.meta.env.BASE_URL // '/manajemen-risiko/' di produksi

// Bar progres tipis saat pindah halaman. Komponen rute dimuat lazy (dynamic
// import), jadi tanpa ini perpindahan menu terasa menggantung tanpa umpan balik.
const navigating = ref(false)
// Di layar sempit sidebar jadi drawer; ditutup otomatis tiap pindah halaman.
const sidebarOpen = ref(false)
router.beforeEach(() => {
  navigating.value = true
})
router.afterEach(() => {
  navigating.value = false
  sidebarOpen.value = false
})
router.onError(() => {
  navigating.value = false
})

function logout() {
  auth.logout()
  ctx.$reset()
  router.push({ name: 'login' })
}

const navGroups = [
  {
    label: 'Beranda',
    items: [
      ['dashboard', 'Dashboard', 'pi-home'],
      ['tata-kelola', 'Tata Kelola Risiko', 'pi-sitemap'],
      ['laporan', 'Cetak Laporan', 'pi-print'],
      ['generate-rtp', 'Generate Dokumen RTP', 'pi-file-word'],
    ],
  },
  {
    label: 'Laporan Rekapitulasi',
    items: [
      ['rekap-kuesioner', 'Rekapitulasi Kuesioner', 'pi-chart-pie'],
      ['rekap-konteks', 'Rekapitulasi Konteks', 'pi-sitemap'],
      ['rekap-identifikasi', 'Rekapitulasi Kategori Risiko', 'pi-tags'],
      ['rekap-level', 'Rekapitulasi Level Risiko', 'pi-chart-bar'],
      ['rekap-kepatuhan', 'Progres OPD', 'pi-check-circle'],
      ['rekap-rtp', 'Realisasi RTP', 'pi-shield'],
      ['rekap-event', 'Keterjadian Risiko', 'pi-exclamation-triangle'],
    ],
  },
  {
    label: 'Lingkungan Pengendalian (CEE)',
    items: [
      ['form1a', 'Kuesioner', 'pi-list-check'],
      ['survei-hasil', 'Rincian Hasil Survei', 'pi-users'],
      ['form1b', 'Reviu Dokumen', 'pi-file-edit'],
      ['form1c', 'Simpulan CEE', 'pi-check-square'],
      ['form6', 'RTP atas CEE', 'pi-wrench'],
    ],
  },
  {
    label: 'Pengelolaan Risiko',
    items: [
      ['selera-risiko', 'Selera Risiko', 'pi-sliders-h'],
      ['kamus-risiko', 'Kamus Risiko', 'pi-book'],
      ['konteks', 'Penetapan Konteks', 'pi-sitemap'],
      ['identifikasi-risiko', 'Identifikasi Risiko', 'pi-flag'],
      ['form4', 'Analisis Risiko', 'pi-chart-bar'],
      ['matriks', 'Matriks Risiko', 'pi-th-large'],
      ['form5', 'Risiko Prioritas', 'pi-star'],
      ['form7', 'Respon Risiko (RTP)', 'pi-shield'],
    ],
  },
  {
    label: 'Komunikasi & Pemantauan',
    items: [
      ['form10', 'Monitoring Event', 'pi-history'],
      ['approval-kejadian', 'Approval Kejadian', 'pi-check-circle'],
    ],
  },
  {
    label: 'Administrasi',
    admin: true,
    items: [
      ['kelola-kuesioner', 'Kelola Kuesioner CEE', 'pi-list-check'],
      ['pengaturan', 'Pengaturan Aplikasi', 'pi-cog'],
    ],
  },
]

// Grup ber-flag admin hanya tampil bagi Admin.
const visibleGroups = computed(() => navGroups.filter((g) => !g.admin || auth.isAdmin))

// Sidebar accordion: hanya satu grup terbuka; grup berisi menu aktif dibuka.
function activeGroupLabel() {
  const g = navGroups.find((grp) =>
    grp.items.some(
      (it) => it[0] === route.name || (route.name === 'rekapitulasi' && grp.label === 'Laporan Rekapitulasi'),
    ),
  )
  return g ? g.label : navGroups[0].label
}
const openGroup = ref(activeGroupLabel())
function toggleGroup(label) {
  openGroup.value = openGroup.value === label ? null : label
}
watch(
  () => route.name,
  () => {
    const l = activeGroupLabel()
    if (l) openGroup.value = l
  },
)

const opdOptions = computed(() =>
  ctx.opdList.map((o) => ({ label: o.nama_pd || o.nama_pd_singkat, value: o.id_sub_pd })),
)
const tahunOptions = computed(() => {
  const y = new Date().getFullYear()
  return [y + 1, y, y - 1, y - 2].map((t) => ({ label: String(t), value: t }))
})
const pageTitle = computed(() => route.meta.title || 'Manajemen Risiko')
const isPublic = computed(() => !!route.meta.public)

// Pemetaan modul -> bagian (section) pada halaman Laporan/Cetak.
// Modul di sini dicetak lewat laporan berformat resmi; sisanya (matriks,
// dashboard) dicetak apa adanya dari layar via window.print().
const laporanKey = {
  form1a: 'f1a', form1b: 'f1b', form1c: 'f1c', form6: 'f6',
  form2a: 'f2a', form2b: 'f2b', form2c: 'f2c',
  form3a: 'f3a', form3b: 'f3b', form3c: 'f3c', form4: 'f4', form5: 'f5', form7: 'f7',
  form8: 'f8', form9: 'f9', form10: 'f10',
}
// Tampilkan tombol Cetak di setiap modul kecuali halaman laporan itu sendiri.
const showCetak = computed(() => route.name !== 'laporan')
function cetak() {
  let key = laporanKey[route.name]
  if (route.name === 'konteks') {
    const tab = route.query.tab || '2a'
    key = `f${tab}`
  } else if (route.name === 'identifikasi-risiko') {
    const tab = route.query.tab || '3a'
    key = `f${tab}`
  }
  if (key) router.push({ name: 'laporan', query: { form: key, print: 1 } })
  else window.print()
}
// OPD hanya bisa dipilih bebas oleh Admin / pengguna dengan >1 OPD.
const opdLocked = computed(() => !auth.isAdmin && ctx.opdList.length <= 1)

// Daftar OPD dimuat saat masuk area terproteksi — tidak cukup lewat onMounted:
// App hanya mount sekali, sehingga bila aplikasi dibuka di /login daftar OPD
// tidak pernah dimuat dan halaman setelah login menunggu selamanya (harus
// reload manual). Watcher ini juga menangani pergantian pengguna.
const opdError = ref('')
let opdLoading = false

async function ensureOpd() {
  if (isPublic.value || !auth.isAuthenticated || ctx.loaded || opdLoading) return
  opdLoading = true
  opdError.value = ''
  try {
    // Tahun default (Pengaturan) tidak boleh menggagalkan pemuatan OPD.
    await Promise.all([
      ctx.loadOpd(auth.allowedOpds),
      ctx.loadPengaturan().catch(() => null),
    ])
  } catch (e) {
    // 401 sudah ditangani interceptor api.js (redirect ke login).
    if (e.response?.status !== 401) opdError.value = 'Gagal memuat daftar OPD.'
  } finally {
    opdLoading = false
  }
}

watch(
  [isPublic, () => auth.user?.username],
  ([, username], prev) => {
    // Pengguna berganti tanpa reload -> konteks OPD lama tidak berlaku lagi.
    if (prev?.[1] && prev[1] !== username) ctx.$reset()
    ensureOpd()
  },
  { immediate: true },
)
</script>

<template>
  <!-- Progres perpindahan halaman, di atas segalanya -->
  <div v-if="navigating" class="route-progress no-print" />

  <!-- Halaman publik (survei) tampil tanpa shell admin -->
  <template v-if="isPublic">
    <router-view />
    <Toast position="top-right" />
  </template>

  <div v-else class="app-shell" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- Latar gelap penutup saat drawer terbuka (hanya tampil di layar sempit) -->
    <div class="sidebar-backdrop no-print" @click="sidebarOpen = false" />

    <aside class="sidebar">
      <div class="brand">
        Manajemen Risiko
        <small>Pemerintah Kota Tegal — SPIP</small>
      </div>
      <template v-for="g in visibleGroups" :key="g.label">
        <div
          class="nav-group-label"
          :class="{ open: openGroup === g.label }"
          @click="toggleGroup(g.label)"
        >
          <span>{{ g.label }}</span>
          <i class="pi pi-chevron-down chev" />
        </div>
        <div class="nav-group-items" :class="{ open: openGroup === g.label }">
          <div class="nav-group-inner">
            <router-link
              v-for="it in g.items"
              :key="it[0]"
              :to="{ name: it[0] }"
              custom
              v-slot="{ navigate, isActive }"
            >
              <div class="nav-item" :class="{ active: isActive }" @click="navigate">
                <i class="pi" :class="it[2]" />
                <span>{{ it[1] }}</span>
              </div>
            </router-link>
          </div>
        </div>
      </template>
      <a class="nav-item" :href="`${base}survei`" target="_blank" style="margin-top: auto; border-top: 1px solid #1e293b">
        <i class="pi pi-external-link" />
        <span>Buka Survei Publik</span>
      </a>
    </aside>

    <div class="main">
      <header class="topbar">
        <Button
          class="nav-toggle no-print"
          :icon="sidebarOpen ? 'pi pi-times' : 'pi pi-bars'"
          severity="secondary"
          text
          rounded
          aria-label="Menu"
          @click="sidebarOpen = !sidebarOpen"
        />
        <div class="page-title">{{ pageTitle }}</div>
        <div class="ctx">
          <i class="pi pi-building muted ctx-icon" />
          <Select
            class="opd-select"
            :modelValue="ctx.opdId"
            @update:modelValue="ctx.setOpd"
            :options="opdOptions"
            optionLabel="label"
            optionValue="value"
            filter
            placeholder="Pilih OPD"
            :disabled="opdLocked"
          />
          <Select
            class="tahun-select"
            :modelValue="ctx.tahun"
            @update:modelValue="ctx.setTahun"
            :options="tahunOptions"
            optionLabel="label"
            optionValue="value"
          />
          <div class="user-box">
            <i class="pi pi-user" />
            <span class="user-name">{{ auth.displayName }}</span>
            <small class="user-role">{{ auth.isAdmin ? 'Admin' : 'OPD' }}</small>
          </div>
          <Button
            v-if="showCetak"
            class="btn-cetak"
            label="Cetak"
            icon="pi pi-print"
            size="small"
            severity="secondary"
            outlined
            v-tooltip.bottom="'Cetak modul ini'"
            @click="cetak"
          />
          <Button
            icon="pi pi-sign-out"
            severity="secondary"
            text
            rounded
            v-tooltip.bottom="'Keluar'"
            @click="logout"
          />
        </div>
      </header>
      <main class="content">
        <router-view v-if="ctx.loaded" :key="route.name + '-' + ctx.opdId + '-' + ctx.tahun" />
        <div v-else-if="opdError" class="muted">
          {{ opdError }}
          <Button label="Coba lagi" icon="pi pi-refresh" size="small" text @click="ensureOpd" />
        </div>
        <AppLoader v-else label="Memuat data OPD…" />
      </main>
    </div>
    <Toast position="top-right" />
    <ConfirmDialog />
  </div>
</template>

<style scoped>
/* Bar progres perpindahan halaman: melintas dari kiri ke kanan di tepi atas. */
.route-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 3000;
  overflow: hidden;
  background: rgba(99, 102, 241, 0.14);
}
.route-progress::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--grad-brand);
  transform-origin: 0 50%;
  animation: route-progress-slide 1.1s ease-in-out infinite;
}
@keyframes route-progress-slide {
  0% { transform: translateX(-100%) scaleX(0.4); }
  50% { transform: translateX(0) scaleX(0.7); }
  100% { transform: translateX(100%) scaleX(0.4); }
}
@media (prefers-reduced-motion: reduce) {
  .route-progress::before { animation-duration: 2.4s; }
}

.user-box {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding-left: 0.75rem;
  margin-left: 0.25rem;
  border-left: 1px solid #e2e8f0;
}
.user-box .pi-user {
  color: #64748b;
}
.user-name {
  font-weight: 600;
  font-size: 0.85rem;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role {
  color: #1d4ed8;
  font-weight: 600;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  background: #eff4ff;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
}
</style>
