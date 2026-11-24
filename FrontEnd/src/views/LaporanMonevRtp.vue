<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'
import MonevRtp from '@/components/laporan/MonevRtp.vue'

const ctx = useContextStore()
const loading = ref(false)
const rawItems = ref([])
const summary = ref({ total: 0, selesai: 0, proses: 0, belum: 0, total_kejadian: 0 })
const searchQuery = ref('')
const exporting = ref(false)

const periodeOptions = [
  { label: 'Tahunan ', value: 'tahunan', sub: '(Januari - Desember)' },
  { label: 'Triwulan I ', value: 'tw1', sub: '(Januari - Maret)' },
  { label: 'Triwulan II ', value: 'tw2', sub: '(April - Juni)' },
  { label: 'Triwulan III ', value: 'tw3', sub: '(Juli - September)' },
  { label: 'Triwulan IV ', value: 'tw4', sub: '(Oktober - Desember)' },
]
const selectedPeriode = ref('tahunan')

// Untuk mode tahunan: pilihan filter apakah hanya yang dilaksanakan/kejadian atau seluruh rencana
const filterTahunanMode = ref('executed') // 'executed' | 'all'
const tahunanFilterOptions = [
  { label: 'Hanya Terealisasi & Kejadian', value: 'executed' },
  { label: 'Semua Rencana RTP (Lengkap)', value: 'all' },
]

const currentPeriodeLabel = computed(() => {
  const opt = periodeOptions.find((p) => p.value === selectedPeriode.value)
  return opt ? opt.label : 'Tahunan'
})

const isTriwulan = computed(() => selectedPeriode.value !== 'tahunan')
const opdName = computed(() => ctx.opd?.nama_pd || '-')

async function loadData() {
  if (!ctx.opdId || !ctx.tahun) return
  loading.value = true
  try {
    const params = {
      opd_id: ctx.opdId,
      tahun: ctx.tahun,
      periode: selectedPeriode.value,
      include_all: selectedPeriode.value === 'tahunan' && filterTahunanMode.value === 'all',
    }
    const { data } = await api.get('/risiko/realisasi', { params })
    rawItems.value = Array.isArray(data) ? data : (data?.items || [])
    summary.value = data?.summary || { total: 0, selesai: 0, proses: 0, belum: 0, total_kejadian: 0 }
  } catch (e) {
    console.error('Gagal memuat data Monev RTP:', e)
    rawItems.value = []
  } finally {
    loading.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun, selectedPeriode, filterTahunanMode], loadData)
onMounted(loadData)

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return rawItems.value
  return rawItems.value.filter((r) => {
    const kode = (r.kode_risiko || '').toLowerCase()
    const risiko = (r.uraian_risiko || '').toLowerCase()
    const rtp = (r.rtp?.rencana_tindak || '').toLowerCase()
    const jenis = (r.jenis_risiko || '').toLowerCase()
    return kode.includes(q) || risiko.includes(q) || rtp.includes(q) || jenis.includes(q)
  })
})

function printReport() {
  window.print()
}

async function exportExcel() {
  exporting.value = true
  try {
    const { data } = await api.get('/laporan/excel', {
      params: {
        opd_id: ctx.opdId,
        tahun: ctx.tahun,
        forms: 'monev_rtp',
        periode: selectedPeriode.value,
      },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    const pTag = selectedPeriode.value.toUpperCase()
    a.download = `Laporan_Monev_RTP_${pTag}_${opdName.value.replace(/[^a-zA-Z0-9_-]/g, '_')}_${ctx.tahun}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Gagal mengunduh Excel:', e)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="laporan-monev-page">
    <!-- Header Standar -->
    <div class="page-header no-print">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-file-check"></i>
        </div>
        <div>
          <h1 class="page-title">Laporan Monitoring &amp; Evaluasi RTP</h1>
          <p class="page-desc">
            <template v-if="isTriwulan">
              Laporan triwulanan pelaksanaan RTP dan keterjadian risiko &middot; {{ opdName }} &middot; Periode {{ currentPeriodeLabel }} Tahun {{ ctx.tahun }}
            </template>
            <template v-else>
              Laporan monitoring dan evaluasi tahunan pelaksanaan RTP dan keterjadian risiko &middot; {{ opdName }} &middot; Tahun {{ ctx.tahun }}
            </template>
          </p>
        </div>
      </div>

      <div class="header-actions">
        <div class="ctx-chip" title="Konteks Penilaian Aktif">
          <i class="pi pi-building"></i>
          <span>{{ opdName }}</span>
          <span class="chip-dot">•</span>
          <span>Tahun {{ ctx.tahun }}</span>
        </div>
      </div>
    </div>

    <!-- Filter & Action Toolbar (tidak tercetak saat print) -->
    <div class="toolbar-card no-print">
      <div class="toolbar-left">
        <!-- Periode Selector -->
        <div class="filter-item">
          <label class="filter-label"><i class="pi pi-calendar mr-1"></i>Periode Laporan:</label>
          <Select
            v-model="selectedPeriode"
            :options="periodeOptions"
            optionLabel="label"
            optionValue="value"
            class="p-inputtext-sm periode-select"
          >
            <template #option="{ option }">
              <div class="flex flex-col">
                <span class="font-semibold">{{ option.label }}</span>
                <span class="text-xs text-slate-500">{{ option.sub }}</span>
              </div>
            </template>
          </Select>
        </div>

        <!-- Filter Tambahan Khusus Tahunan -->
        <div v-if="!isTriwulan" class="filter-item">
          <label class="filter-label"><i class="pi pi-filter mr-1"></i>Cakupan Data:</label>
          <Select
            v-model="filterTahunanMode"
            :options="tahunanFilterOptions"
            optionLabel="label"
            optionValue="value"
            class="p-inputtext-sm filter-mode-select"
          />
        </div>

        <!-- Search Bar -->
        <div class="search-box">
          <i class="pi pi-search search-icon" />
          <InputText
            v-model="searchQuery"
            placeholder="Cari risiko / RTP..."
            class="p-inputtext-sm search-input"
          />
        </div>
      </div>

      <div class="toolbar-right">
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          :loading="loading"
          @click="loadData"
        />
        <Button
          label="Unduh Excel"
          icon="pi pi-file-excel"
          severity="success"
          :loading="exporting"
          @click="exportExcel"
        />
        <Button
          label="Cetak / Simpan PDF"
          icon="pi pi-print"
          severity="primary"
          @click="printReport"
        />
      </div>
    </div>

    <!-- Info Banner Status Periode (tidak tercetak saat print) -->
    <div class="period-info-card no-print">
      <div class="period-info-left">
        <span class="period-tag" :class="isTriwulan ? 'period-tw' : 'period-annual'">
          <i class="pi" :class="isTriwulan ? 'pi-clock' : 'pi-calendar'"></i>
          {{ currentPeriodeLabel }}
        </span>
        <div class="period-rule-text">
          <template v-if="isTriwulan">
            <strong>Mode Triwulan:</strong> Hanya menampilkan <strong>Realisasi RTP</strong> yang dilaksanakan dan <strong>Kejadian</strong> pada triwulan ini.
          </template>
          <template v-else-if="filterTahunanMode === 'executed'">
            <strong>Mode Tahunan:</strong> Menampilkan semua <strong>Realisasi RTP</strong> yang dilaksanakan dan <strong>Kejadian</strong> pada tahun {{ ctx.tahun }}.
          </template>
          <template v-else>
            <strong>Mode Tahunan (Lengkap):</strong> Menampilkan seluruh Rencana Tindak Pengendalian (RTP) terdaftar beserta status keterjadiannya pada tahun {{ ctx.tahun }}.
          </template>
        </div>
      </div>

      <div class="period-stats">
        <div class="stat-pill" title="Total Risiko / RTP pada laporan ini">
          <span class="stat-num">{{ summary.total || 0 }}</span>
          <span class="stat-lbl">Risiko</span>
        </div>
        <div class="stat-pill pill-success" title="RTP Selesai Dilaksanakan">
          <span class="stat-num">{{ summary.selesai || 0 }}</span>
          <span class="stat-lbl">Terealisasi</span>
        </div>
        <div class="stat-pill pill-warning" title="RTP Dalam Proses">
          <span class="stat-num">{{ summary.proses || 0 }}</span>
          <span class="stat-lbl">Proses</span>
        </div>
        <div class="stat-pill pill-danger" title="Total Kejadian Risiko Terjadi">
          <span class="stat-num">{{ summary.total_kejadian || 0 }}</span>
          <span class="stat-lbl">Kejadian</span>
        </div>
      </div>
    </div>

    <!-- State Loading -->
    <AppLoader v-if="loading" />

    <!-- Paper Container for Report -->
    <div v-else class="report-paper">
      <MonevRtp
        :data="filteredItems"
        :opd-name="opdName"
        :tahun="ctx.tahun"
        :periode="selectedPeriode"
        :periode-label="currentPeriodeLabel"
      />
    </div>
  </div>
</template>

<style scoped>
.laporan-monev-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}

.page-desc {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.ctx-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.chip-dot {
  color: #94a3b8;
}

/* Toolbar Card */
.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  background: #ffffff;
  padding: 0.875rem 1.25rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.toolbar-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.periode-select {
  min-width: 210px;
}

.filter-mode-select {
  min-width: 210px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 0.85rem;
}

.search-input {
  padding-left: 2.2rem;
  width: 190px;
  border-radius: 6px;
}

/* Period Info Card */
.period-info-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  background: #f8fafc;
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  border-left: 4px solid #059669;
  border-top: 1px solid #e2e8f0;
  border-right: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
}

.period-info-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.period-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.825rem;
  font-weight: 700;
}

.period-tw {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.period-annual {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.period-rule-text {
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.4;
}

.period-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3px 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  min-width: 55px;
}

.stat-num {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.1;
}

.stat-lbl {
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 500;
}

.pill-success .stat-num {
  color: #059669;
}

.pill-warning .stat-num {
  color: #d97706;
}

.pill-danger .stat-num {
  color: #dc2626;
}

.report-paper {
  background: #ffffff;
  padding: 2rem;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

@media print {
  .no-print {
    display: none !important;
  }
  .laporan-monev-page {
    gap: 0;
  }
  .report-paper {
    padding: 0;
    border: none;
    box-shadow: none;
    background: transparent;
  }
}
</style>

