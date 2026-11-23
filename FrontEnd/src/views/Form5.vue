<script setup>
import { computed, ref, watch } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const groups = ref([])
const loading = ref(false)
const error = ref('')

const searchQuery = ref('')
const filterJenis = ref('all')
const filterLevel = ref('all')

const levelColor = {
  'Sangat Rendah (1)': '#15803d',
  'Sangat Rendah': '#15803d',
  'Rendah (2)': '#22c55e',
  'Rendah': '#22c55e',
  'Sedang (3)': '#eab308',
  'Sedang': '#eab308',
  'Tinggi (4)': '#f97316',
  'Tinggi': '#f97316',
  'Sangat Tinggi (5)': '#ef4444',
  'Sangat Tinggi': '#ef4444',
}

const jenisOptions = [
  { value: 'all', label: 'Semua Kategori Risiko' },
  { value: 'strategis_pemda', label: 'Risiko Strategis Pemda' },
  { value: 'strategis_opd', label: 'Risiko Strategis OPD' },
  { value: 'operasional_opd', label: 'Risiko Operasional OPD' },
]

const levelOptions = [
  { value: 'all', label: 'Semua Level Risiko' },
  { value: 'Sangat Tinggi', label: 'Sangat Tinggi (5)' },
  { value: 'Tinggi', label: 'Tinggi (4)' },
  { value: 'Sedang', label: 'Sedang (3)' },
  { value: 'Rendah', label: 'Rendah (2)' },
  { value: 'Sangat Rendah', label: 'Sangat Rendah (1)' },
]

const summary = computed(() => {
  let total = 0
  const byJenis = {}
  for (const g of groups.value) {
    const count = (g.items || []).length
    total += count
    byJenis[g.jenis] = count
  }
  return {
    total,
    strategisPemda: byJenis['strategis_pemda'] || 0,
    strategisOpd: byJenis['strategis_opd'] || 0,
    operasionalOpd: byJenis['operasional_opd'] || 0,
  }
})

async function load() {
  if (!ctx.opdId || !ctx.tahun) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/risiko/form5', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    groups.value = data || []
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Gagal memuat data risiko prioritas'
  } finally {
    loading.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun], load, { immediate: true })

const filteredGroups = computed(() => {
  return groups.value
    .filter(g => filterJenis.value === 'all' || g.jenis === filterJenis.value)
    .map(g => {
      const q = searchQuery.value.trim().toLowerCase()
      const items = (g.items || []).filter(it => {
        // Filter level
        if (filterLevel.value !== 'all') {
          const lvl = it.analisis?.level || ''
          if (!lvl.toLowerCase().includes(filterLevel.value.toLowerCase())) {
            return false
          }
        }
        // Search query
        if (q) {
          const matchUraian = (it.uraian_risiko || '').toLowerCase().includes(q)
          const matchKode = (it.kode_risiko || '').toLowerCase().includes(q)
          const matchPemilik = (it.pemilik_risiko || '').toLowerCase().includes(q)
          const matchSebab = (it.sebab_uraian || '').toLowerCase().includes(q)
          const matchDampak = (it.dampak_uraian || '').toLowerCase().includes(q)
          if (!matchUraian && !matchKode && !matchPemilik && !matchSebab && !matchDampak) {
            return false
          }
        }
        return true
      })
      return { ...g, filteredItems: items }
    })
})

const hasFilteredResults = computed(() => {
  return filteredGroups.value.some(g => g.filteredItems.length > 0)
})
</script>

<template>
  <div class="form5-page">
    <!-- Header Section (Style Realisasi RTP) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-star"></i>
        </div>
        <div>
          <h1 class="page-title">Daftar Risiko Prioritas</h1>
          <p class="page-desc">
            Daftar risiko prioritas hasil evaluasi dan ambang Selera Risiko yang wajib ditangani dalam Rencana Tindak Pengendalian (RTP).
          </p>
        </div>
      </div>
      <div class="header-actions">
        <router-link to="/matriks" style="text-decoration: none">
          <Button label="Matriks Risiko" icon="pi pi-th-large" severity="info" variant="outlined" />
        </router-link>
        <router-link to="/form7" style="text-decoration: none">
          <Button label="Respon Risiko (RTP)" icon="pi pi-shield" severity="help" variant="outlined" />
        </router-link>
        <Button label="Segarkan" icon="pi pi-refresh" severity="secondary" variant="outlined" :loading="loading" @click="load" />
      </div>
    </div>

    <!-- Stat Cards Header (Style Realisasi RTP / Form 4) -->
    <div class="stat-grid no-print" style="margin-bottom: 18px;">
      <div class="stat">
        <div class="v">{{ summary.total }}</div>
        <div class="l">Total Risiko Prioritas</div>
      </div>
      <div class="stat">
        <div class="v">{{ summary.strategisPemda }}</div>
        <div class="l">Strategis Pemda</div>
      </div>
      <div class="stat">
        <div class="v">{{ summary.strategisOpd }}</div>
        <div class="l">Strategis OPD</div>
      </div>
      <div class="stat">
        <div class="v">{{ summary.operasionalOpd }}</div>
        <div class="l">Operasional OPD</div>
      </div>
    </div>

    <!-- Alert Box Error -->
    <div v-if="error" class="alert-box alert-error" role="alert">
      <i class="pi pi-exclamation-circle"></i>
      <span>{{ error }}</span>
      <Button label="Coba Lagi" text size="small" @click="load" />
    </div>

    <!-- Toolbar Filter & Search -->
    <div class="filter-card no-print">
      <div class="search-wrap">
        <i class="pi pi-search search-icon"></i>
        <InputText
          v-model="searchQuery"
          placeholder="Cari uraian risiko, kode, pemilik, penyebab, atau dampak..."
          class="search-input"
        />
        <button
          v-if="searchQuery"
          class="search-clear-btn"
          type="button"
          @click="searchQuery = ''"
        >
          <i class="pi pi-times"></i>
        </button>
      </div>
      <div class="filter-actions">
        <Select
          v-model="filterJenis"
          :options="jenisOptions"
          optionLabel="label"
          optionValue="value"
          class="filter-select"
        />
        <Select
          v-model="filterLevel"
          :options="levelOptions"
          optionLabel="label"
          optionValue="value"
          class="filter-select"
        />
      </div>
    </div>

    <AppLoader v-if="loading && !groups.length" />

    <!-- Table Section -->
    <div v-if="!loading || groups.length">
      <div
        v-for="g in filteredGroups"
        :key="g.jenis"
        class="group-section"
      >
        <div class="group-header">
          <div class="group-header-title">
            <span class="group-indicator"></span>
            <span>{{ g.label }}</span>
          </div>
          <span class="group-badge">
            {{ g.filteredItems.length }}
            <span v-if="g.filteredItems.length !== g.items.length">dari {{ g.items.length }}</span>
            prioritas
          </span>
        </div>

        <div class="table-wrap">
          <table class="grid-table">
            <thead>
              <tr>
                <th style="width: 44px; text-align: center">No</th>
                <th style="text-align: left; min-width: 240px">Risiko Prioritas</th>
                <th style="width: 110px; text-align: center">Kode</th>
                <th style="width: 70px; text-align: center">Skala</th>
                <th style="width: 140px; text-align: center">Level</th>
                <th style="text-align: left; min-width: 180px">Pemilik Risiko</th>
                <th style="text-align: left; min-width: 200px">Penyebab</th>
                <th style="text-align: left; min-width: 200px">Dampak</th>
                <th style="width: 80px; text-align: center" class="no-print">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(it, i) in g.filteredItems" :key="it.id">
                <td style="text-align: center; color: var(--text-muted)">{{ i + 1 }}</td>
                <td>
                  <router-link :to="{ name: 'detail-risiko', params: { id: it.id } }" class="risk-link">
                    {{ it.uraian_risiko }}
                  </router-link>
                </td>
                <td style="text-align: center; font-weight: 500; font-family: monospace">
                  {{ it.kode_risiko }}
                </td>
                <td style="text-align: center; font-weight: 700; font-size: 0.95rem">
                  {{ it.analisis.skala_risiko }}
                </td>
                <td style="text-align: center">
                  <span
                    class="pill level-pill"
                    :style="{
                      backgroundColor: levelColor[it.analisis.level] + '18',
                      color: levelColor[it.analisis.level],
                      borderColor: levelColor[it.analisis.level] + '40',
                    }"
                  >
                    <span class="pill-dot" :style="{ backgroundColor: levelColor[it.analisis.level] }"></span>
                    {{ it.analisis.level }}
                  </span>
                </td>
                <td style="font-weight: 500; color: #334155">{{ it.pemilik_risiko || '-' }}</td>
                <td style="color: #475569">{{ it.sebab_uraian || '-' }}</td>
                <td style="color: #475569">{{ it.dampak_uraian || '-' }}</td>
                <td style="text-align: center" class="no-print">
                  <router-link :to="{ name: 'detail-risiko', params: { id: it.id } }">
                    <Button icon="pi pi-arrow-right" severity="secondary" text rounded size="small" v-tooltip.top="'Lihat Detail'" />
                  </router-link>
                </td>
              </tr>
              <tr v-if="!g.filteredItems.length">
                <td colspan="9" class="empty-cell">
                  <i class="pi pi-info-circle empty-icon"></i>
                  <span>Tidak ada risiko prioritas pada kategori ini<span v-if="searchQuery || filterLevel !== 'all'"> yang cocok dengan kriteria filter</span>.</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="!hasFilteredResults && groups.length > 0" class="empty-state-card no-print">
        <i class="pi pi-filter-slash empty-state-icon"></i>
        <h3>Tidak Ada Data yang Cocok</h3>
        <p>Tidak ditemukan risiko prioritas yang memenuhi kriteria pencarian atau penyaringan.</p>
        <Button label="Reset Filter" icon="pi pi-refresh" severity="secondary" size="small" @click="searchQuery = ''; filterJenis = 'all'; filterLevel = 'all'" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.form5-page {
  max-width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
  background: #ffffff;
  padding: 1.5rem 1.75rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
}

.header-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(217, 119, 6, 0.25);
}

.page-title {
  font-size: 1.45rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.35rem 0;
  line-height: 1.25;
}

.page-desc {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
  line-height: 1.45;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.alert-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
}

.alert-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Filter Card */
.filter-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.search-wrap {
  position: relative;
  flex: 1;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 2.35rem !important;
  padding-right: 2rem !important;
  font-size: 0.875rem;
  border-radius: 8px;
}

.search-clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.search-clear-btn:hover {
  color: #475569;
}

.filter-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-select {
  min-width: 200px;
  font-size: 0.875rem;
}

/* Group Sections */
.group-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.group-header-title {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-weight: 650;
  font-size: 0.95rem;
  color: #1e293b;
}

.group-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
}

.group-badge {
  font-size: 0.78rem;
  font-weight: 600;
  color: #b45309;
  background: #fef3c7;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid #fde68a;
}

.table-wrap {
  overflow-x: auto;
  width: 100%;
}

.grid-table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.85rem;
}

.grid-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  padding: 9px 12px;
  white-space: nowrap;
}

.grid-table td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  vertical-align: middle;
}

.grid-table tbody tr:nth-child(even) {
  background-color: #f8fafc;
}

.grid-table tbody tr:hover {
  background-color: #f1f5f9;
}

.risk-link {
  color: #2563eb;
  font-weight: 550;
  transition: color 0.15s ease;
}

.risk-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

.level-pill {
  border: 1px solid;
  font-size: 0.75rem;
  padding: 3px 9px;
  font-weight: 600;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.empty-cell {
  text-align: center;
  padding: 1.5rem !important;
  color: #64748b;
  font-size: 0.875rem;
}

.empty-icon {
  margin-right: 0.5rem;
  color: #94a3b8;
}

.empty-state-card {
  text-align: center;
  padding: 3rem 1.5rem;
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: #64748b;
}

.empty-state-icon {
  font-size: 2.5rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

.empty-state-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.empty-state-card p {
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    padding: 1.25rem;
  }
  .header-actions {
    width: 100%;
  }
  .filter-card {
    flex-direction: column;
    align-items: stretch;
  }
  .search-wrap {
    max-width: 100%;
  }
  .filter-actions {
    flex-direction: column;
  }
  .filter-select {
    width: 100%;
  }
}
</style>
