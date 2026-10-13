<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'
import RekapKuesioner from '@/components/rekapitulasi/RekapKuesioner.vue'
import RekapKonteks from '@/components/rekapitulasi/RekapKonteks.vue'
import RekapIdentifikasi from '@/components/rekapitulasi/RekapIdentifikasi.vue'
import RekapLevelRisiko from '@/components/rekapitulasi/RekapLevelRisiko.vue'
import RekapKepatuhan from '@/components/rekapitulasi/RekapKepatuhan.vue'
import RekapRealisasiRtp from '@/components/rekapitulasi/RekapRealisasiRtp.vue'
import RekapRiskEvent from '@/components/rekapitulasi/RekapRiskEvent.vue'

const route = useRoute()
const router = useRouter()
const ctx = useContextStore()

// Daftar tab yang valid
const TABS = [
  { key: 'kuesioner', routeName: 'rekap-kuesioner', label: '1. Rekap Kuesioner', icon: 'pi-chart-pie' },
  { key: 'konteks', routeName: 'rekap-konteks', label: '2. Rekap Konteks', icon: 'pi-sitemap' },
  { key: 'identifikasi', routeName: 'rekap-identifikasi', label: '3. Kategori Risiko', icon: 'pi-tags' },
  { key: 'level', routeName: 'rekap-level', label: '4. Level Risiko', icon: 'pi-chart-bar' },
  { key: 'kepatuhan', routeName: 'rekap-kepatuhan', label: '5. Progres OPD', icon: 'pi-check-circle' },
  { key: 'rtp', routeName: 'rekap-rtp', label: '6. Realisasi RTP', icon: 'pi-shield' },
  { key: 'risk_event', routeName: 'rekap-event', label: '7. Keterjadian Risiko', icon: 'pi-exclamation-triangle' },
]

// Tentukan tab aktif dari route meta, query, atau default 'kuesioner'
function resolveActiveTab() {
  if (route.meta?.tab) return route.meta.tab
  if (route.query?.tab && TABS.some((t) => t.key === route.query.tab)) return route.query.tab
  const found = TABS.find((t) => t.routeName === route.name)
  return found ? found.key : 'kuesioner'
}

const currentTab = ref(resolveActiveTab())
const tahunLocal = ref(ctx.tahun || new Date().getFullYear())
const searchQuery = ref('')
const loading = ref(false)
const exporting = ref(false)

// Cache data per tab
const dataStore = ref({
  kuesioner: { items: [], summary: {} },
  konteks: { items: [], summary: {} },
  identifikasi: { items: [], rows: [], summary: {} },
  level: { items: [], rows: [], summary: {} },
  kepatuhan: { items: [], summary: {} },
  rtp: { items: [], summary: {} },
  risk_event: { items: [], log_rows: [], summary: {} },
})

const tahunOptions = computed(() => {
  const y = new Date().getFullYear()
  return [y + 1, y, y - 1, y - 2].map((t) => ({ label: `Tahun ${t}`, value: t }))
})

// Muat data untuk tab yang sedang aktif
async function loadTabData(tabKey = currentTab.value) {
  loading.value = true
  const th = tahunLocal.value
  try {
    let endpoint = ''
    if (tabKey === 'kuesioner') endpoint = '/rekapitulasi/kuesioner'
    else if (tabKey === 'konteks') endpoint = '/rekapitulasi/konteks'
    else if (tabKey === 'identifikasi') endpoint = '/rekapitulasi/identifikasi'
    else if (tabKey === 'level') endpoint = '/rekapitulasi/level-risiko'
    else if (tabKey === 'kepatuhan') endpoint = '/rekapitulasi/kepatuhan'
    else if (tabKey === 'rtp') endpoint = '/rekapitulasi/realisasi-rtp'
    else if (tabKey === 'risk_event') endpoint = '/rekapitulasi/risk-event'

    if (endpoint) {
      const res = await api.get(endpoint, { params: { tahun: th } })
      dataStore.value[tabKey] = res.data || {}
    }
  } catch (err) {
    console.error(`Gagal memuat data rekapitulasi (${tabKey}):`, err)
  } finally {
    loading.value = false
  }
}

function onTabChange(newTab) {
  if (currentTab.value === newTab) return
  currentTab.value = newTab
  const target = TABS.find((t) => t.key === newTab)
  if (target) {
    router.push({ name: target.routeName })
  }
}

// Sinkronkan pergantian rute ke tab aktif
watch(
  () => [route.name, route.meta?.tab, route.query?.tab],
  () => {
    const t = resolveActiveTab()
    if (t !== currentTab.value) {
      currentTab.value = t
      loadTabData(t)
    }
  },
)

// Sinkronkan perubahan tahun global dari topbar ctx
watch(
  () => ctx.tahun,
  (newTh) => {
    if (newTh && newTh !== tahunLocal.value) {
      tahunLocal.value = newTh
      loadTabData()
    }
  },
)

// Pergantian tahun lokal
function onTahunChange(newTh) {
  tahunLocal.value = newTh
  ctx.setTahun(newTh)
  loadTabData()
}

// Ekspor Excel
async function exportExcel() {
  exporting.value = true
  try {
    const tab = currentTab.value
    const jenisParam = tab === 'kuesioner' ? 'kuesioner'
      : tab === 'konteks' ? 'konteks'
      : tab === 'identifikasi' ? 'identifikasi'
      : tab === 'level' ? 'level'
      : tab === 'kepatuhan' ? 'kepatuhan'
      : tab === 'rtp' ? 'rtp'
      : tab === 'risk_event' ? 'risk_event' : 'all'

    const { data } = await api.get('/rekapitulasi/excel', {
      params: { tahun: tahunLocal.value, jenis: jenisParam },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `Laporan_Rekapitulasi_${tab}_${tahunLocal.value}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Gagal mengekspor file Excel:', err)
  } finally {
    exporting.value = false
  }
}

function cetakLaporan() {
  window.print()
}

onMounted(() => {
  loadTabData(currentTab.value)
})
</script>

<template>
  <div class="rekap-page">
    <!-- Header Banner Halaman -->
    <div class="page-header no-print">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-table"></i>
        </div>
        <div>
          <h1 class="page-title">Laporan Rekapitulasi</h1>
          <p class="page-desc">
            Rekapitulasi Hasil Kuesioner CEE, Penetapan Konteks, Kategori Risiko, dan Level Risiko seluruh Perangkat Daerah
          </p>
        </div>
      </div>
      <div class="header-actions">
        <Select
          :modelValue="tahunLocal"
          @update:modelValue="onTahunChange"
          :options="tahunOptions"
          optionLabel="label"
          optionValue="value"
          class="tahun-dropdown"
        />
        <Button
          label="Export Excel"
          icon="pi pi-file-excel"
          severity="success"
          outlined
          :loading="exporting"
          @click="exportExcel"
          v-tooltip.bottom="'Unduh rekapitulasi aktif sebagai file Excel (.xlsx)'"
        />
        <Button
          label="Cetak / PDF"
          icon="pi pi-print"
          severity="primary"
          @click="cetakLaporan"
          v-tooltip.bottom="'Cetak atau simpan sebagai PDF format landscape'"
        />
      </div>
    </div>

    <!-- Navigasi Tabs & Filter Bar -->
    <div class="tabs-card no-print">
      <div class="tabs-toolbar-wrap">
        <Tabs :value="currentTab" @update:value="onTabChange" class="rekap-tabs">
          <TabList class="custom-tab-list">
            <Tab v-for="t in TABS" :key="t.key" :value="t.key" class="custom-tab">
              <i class="pi tab-icon" :class="t.icon"></i>
              <span>{{ t.label }}</span>
            </Tab>
          </TabList>
        </Tabs>

        <div class="search-box">
          <i class="pi pi-search search-icon"></i>
          <InputText
            v-model="searchQuery"
            placeholder="Cari Nama OPD..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- Loader -->
    <AppLoader v-if="loading" label="Memuat data rekapitulasi daerah..." />

    <!-- Konten Tab Aktif -->
    <div v-else class="tab-content-area">
      <!-- 1. Rekapitulasi Kuesioner -->
      <RekapKuesioner
        v-if="currentTab === 'kuesioner'"
        :data="dataStore.kuesioner"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />

      <!-- 2. Rekapitulasi Konteks Risiko -->
      <RekapKonteks
        v-if="currentTab === 'konteks'"
        :data="dataStore.konteks"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />

      <!-- 3. Rekapitulasi Identifikasi Risiko (Kategori) -->
      <RekapIdentifikasi
        v-if="currentTab === 'identifikasi'"
        :data="dataStore.identifikasi"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />

      <!-- 4. Rekapitulasi Identifikasi Risiko (Level Risiko) -->
      <RekapLevelRisiko
        v-if="currentTab === 'level'"
        :data="dataStore.level"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />

      <!-- 5. Rekapitulasi Kepatuhan & Progres Pengisian OPD -->
      <RekapKepatuhan
        v-if="currentTab === 'kepatuhan'"
        :data="dataStore.kepatuhan"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />

      <!-- 6. Rekapitulasi Realisasi RTP (Tingkat Tindak Lanjut) -->
      <RekapRealisasiRtp
        v-if="currentTab === 'rtp'"
        :data="dataStore.rtp"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />

      <!-- 7. Rekapitulasi Keterjadian Risiko (Risk Event Log) -->
      <RekapRiskEvent
        v-if="currentTab === 'risk_event'"
        :data="dataStore.risk_event"
        :search-query="searchQuery"
        :tahun="tahunLocal"
      />
    </div>
  </div>
</template>

<style scoped>
.rekap-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 18px 24px;
  border-radius: var(--radius, 14px);
  border: 1px solid var(--border, #e6eaf4);
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.05));
  flex-wrap: wrap;
  gap: 14px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--grad-brand, linear-gradient(135deg, #6366f1, #8b5cf6));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.4rem;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}
.page-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text, #17203a);
}
.page-desc {
  margin: 4px 0 0;
  font-size: 0.84rem;
  color: var(--text-muted, #64748b);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.tahun-dropdown {
  min-width: 140px;
}

.tabs-card {
  background: #fff;
  border-radius: var(--radius, 14px);
  border: 1px solid var(--border, #e6eaf4);
  padding: 8px 14px;
  box-shadow: var(--shadow-xs, 0 1px 2px rgba(0,0,0,0.05));
}
.tabs-toolbar-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.rekap-tabs {
  flex: 1 1 auto;
}
.custom-tab-list {
  border-bottom: none !important;
  gap: 6px;
}
.custom-tab {
  font-size: 0.86rem;
  font-weight: 600;
  padding: 8px 14px !important;
  border-radius: 8px !important;
  border: none !important;
  color: var(--text-muted, #64748b) !important;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}
.custom-tab:hover {
  background: #f1f5f9;
  color: var(--text, #1e293b) !important;
}
.custom-tab[data-p-active="true"] {
  background: var(--primary-soft, #eef2ff) !important;
  color: var(--primary, #4f46e5) !important;
}
.tab-icon {
  font-size: 0.95rem;
}
.search-box {
  position: relative;
  min-width: 240px;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted, #94a3b8);
  font-size: 0.85rem;
}
.search-input {
  padding-left: 32px !important;
  font-size: 0.84rem !important;
  width: 100%;
}

.tab-content-area {
  margin-top: 4px;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .header-actions {
    flex-wrap: wrap;
  }
  .tabs-toolbar-wrap {
    flex-direction: column;
    align-items: stretch;
  }
  .search-box {
    width: 100%;
  }
}
</style>
