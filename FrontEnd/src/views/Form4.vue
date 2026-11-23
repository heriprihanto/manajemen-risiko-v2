<script setup>
import { computed, watch, ref } from 'vue'
import Select from 'primevue/select'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const toast = useToast()
const groups = ref([])
const loading = ref(false)
const error = ref('')
let serial = 0

const kemungkinanOptions = [
  { value: 1, label: '1 Hampir tidak terjadi' },
  { value: 2, label: '2 Jarang terjadi' },
  { value: 3, label: '3 Kadang terjadi' },
  { value: 4, label: '4 Sering terjadi' },
  { value: 5, label: '5 Hampir pasti terjadi' },
]

const dampakOptions = [
  { value: 1, label: '1 Tidak signifikan' },
  { value: 2, label: '2 Minor' },
  { value: 3, label: '3 Moderat' },
  { value: 4, label: '4 Signifikan' },
  { value: 5, label: '5 Sangat Signifikan' },
]

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

const summary = computed(() => {
  let total = 0
  let dinilai = 0
  let prioritas = 0
  for (const g of groups.value) {
    for (const it of g.items || []) {
      total++
      if (it.analisis?.skala_dampak && it.analisis?.skala_kemungkinan) dinilai++
      if (it.analisis?.is_prioritas) prioritas++
    }
  }
  const belum = total - dinilai
  return { total, dinilai, prioritas, belum }
})

async function load() {
  if (!ctx.ready) return
  const id = ++serial
  error.value = ''
  groups.value = []
  loading.value = true
  try {
    const { data } = await api.get('/risiko/form4', { params: { opd_id: ctx.opdId, tahun: ctx.tahun } })
    if (id !== serial) return
    groups.value = data
  } catch (e) {
    if (id === serial) error.value = e.response?.data?.detail || 'Gagal memuat analisis'
  } finally {
    if (id === serial) loading.value = false
  }
}

async function saveAnalisis(item) {
  const a = item.analisis
  if (!a.skala_dampak || !a.skala_kemungkinan) return
  const payload = {
    risiko_id: item.id,
    skala_dampak: a.skala_dampak,
    skala_kemungkinan: a.skala_kemungkinan,
  }
  try {
    const { data } = await api.post('/risiko/analisis', payload)
    Object.assign(item.analisis, data)
    toast.add({ severity: 'success', summary: 'Analisis tersimpan', life: 1200 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Analisis belum tersimpan', detail: typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Periksa skala dan hak akses penilaian.', life: 7000 })
    await load()
  }
}
watch([() => ctx.opdId, () => ctx.tahun], load, { immediate: true })
</script>

<template>
  <div class="form4-page">
    <!-- Header Section (Style Realisasi RTP) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-chart-bar"></i>
        </div>
        <div>
          <h1 class="page-title">Analisis Risiko</h1>
          <p class="page-desc">
            Penilaian tingkat kemungkinan dan dampak risiko menggunakan matriks analisis 5×5. Skor di atas ambang Selera Risiko masuk ke daftar prioritas.
          </p>
        </div>
      </div>
      <div class="header-actions">
        <router-link to="/matriks" style="text-decoration: none">
          <Button
            label="Matriks Risiko"
            icon="pi pi-th-large"
            severity="info"
            variant="outlined"
          />
        </router-link>
        <router-link to="/selera-risiko" style="text-decoration: none">
          <Button
            label="Selera Risiko"
            icon="pi pi-sliders-h"
            severity="help"
            variant="outlined"
          />
        </router-link>
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          :loading="loading"
          @click="load"
        />
      </div>
    </div>

    <!-- Alert Error Jika Ada -->
    <div v-if="error" class="alert-box alert-error" role="alert">
      <i class="pi pi-exclamation-circle" />
      <span>{{ error }}</span>
      <Button label="Coba Lagi" text size="small" @click="load" />
    </div>

    <!-- Stat Cards Header (Style Realisasi RTP) -->
    <div class="stat-grid no-print" style="margin-bottom: 18px;">
      <div class="stat">
        <div class="v">{{ summary.total }}</div>
        <div class="l">Total Risiko Teridentifikasi</div>
      </div>

      <div class="stat">
        <div class="v">
          {{ summary.dinilai }} <small v-if="summary.total">({{ Math.round((summary.dinilai / summary.total) * 100) }}%)</small>
        </div>
        <div class="l">Sudah Dianalisis</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.prioritas }}</div>
        <div class="l">Risiko Prioritas (Melebihi Selera)</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.belum }}</div>
        <div class="l">Belum Dianalisis</div>
      </div>
    </div>

    <AppLoader v-if="loading && !groups.length" label="Memuat analisis risiko…" />

    <div v-for="g in groups" :key="g.jenis" class="page-card" style="margin-bottom: 16px; padding: 0">
      <div style="padding: 10px 14px; font-weight: 600; background: #eff6ff; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between">
        <div style="display: flex; align-items: center; gap: 8px">
          <i class="pi pi-folder text-primary" />
          <span>{{ g.label }}</span>
        </div>
        <span class="count-badge">{{ g.items.length }} risiko</span>
      </div>
      <table class="grid-table">
        <thead>
          <tr>
            <th style="width: 40px">No</th>
            <th style="text-align: left; min-width: 200px">Risiko</th>
            <th style="width: 110px">Kode</th>
            <th style="width: 180px">Dampak</th>
            <th style="width: 210px">Kemungkinan</th>
            <th style="width: 70px">Skala</th>
            <th style="width: 140px">Level</th>
            <th style="width: 80px">Prioritas</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(it, i) in g.items" :key="it.id">
            <td style="text-align: center">{{ i + 1 }}</td>
            <td><router-link :to="{ name: 'detail-risiko', params: { id: it.id } }" class="risk-link">{{ it.uraian_risiko }}</router-link></td>
            <td style="text-align: center"><span class="kode-chip">{{ it.kode_risiko }}</span></td>
            <td style="text-align: center">
              <Select v-model="it.analisis.skala_dampak" :options="dampakOptions" optionLabel="label" optionValue="value"
                :disabled="!it.selera_risiko" placeholder="—" style="width: 100%; min-width: 160px" @change="saveAnalisis(it)" />
            </td>
            <td style="text-align: center">
              <Select v-model="it.analisis.skala_kemungkinan" :options="kemungkinanOptions" optionLabel="label" optionValue="value"
                :disabled="!it.selera_risiko" placeholder="—" style="width: 100%; min-width: 190px" @change="saveAnalisis(it)" />
            </td>
            <td style="text-align: center; font-weight: 700; font-size: 1rem">{{ it.analisis.skala_risiko ?? '–' }}</td>
            <td style="text-align: center">
              <span v-if="it.analisis.level" class="pill" :style="{ background: (levelColor[it.analisis.level] || '#64748b') + '22', color: levelColor[it.analisis.level] || '#64748b', fontWeight: 600 }">
                {{ it.analisis.level }}
              </span>
            </td>
            <td style="text-align: center">
              <template v-if="it.selera_risiko">
                <i
                  class="pi"
                  :class="it.analisis.is_prioritas === null ? 'pi-question-circle' : it.analisis.is_prioritas ? 'pi-check-circle' : 'pi-minus-circle'"
                  :style="{ color: it.analisis.is_prioritas ? '#ef4444' : '#94a3b8', fontSize: '1.15rem' }"
                  role="img"
                  :aria-label="it.analisis.is_prioritas === null ? 'Belum dinilai' : it.analisis.is_prioritas ? 'Prioritas' : 'Bukan prioritas'"
                  :title="`${it.analisis.is_prioritas === null ? 'Belum dinilai' : it.analisis.is_prioritas ? 'Prioritas' : 'Bukan prioritas'} · Ambang ${it.selera_risiko.ambang}`"
                />
              </template>
              <router-link v-else :to="{ name: 'selera-risiko' }" aria-label="Selera Risiko belum ditetapkan" title="Selera Risiko belum ditetapkan" class="text-warning">
                <i class="pi pi-exclamation-circle" aria-hidden="true" style="font-size: 1.15rem; color: #d97706" />
              </router-link>
            </td>
          </tr>
          <tr v-if="!g.items.length"><td colspan="8" class="muted" style="padding: 12px; text-align: center">Belum ada risiko pada jenis ini.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.form4-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Page Header (Style Realisasi RTP) */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
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
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
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
  line-height: 1.4;
  max-width: 800px;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

/* Alert */
.alert-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.88rem;
  margin-bottom: 12px;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

.count-badge {
  font-size: 0.75rem;
  font-weight: 600;
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 12px;
}

.risk-link {
  color: #1e293b;
  font-weight: 500;
  text-decoration: none;
}

.risk-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.kode-chip {
  font-size: 0.75rem;
  font-weight: 600;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 6px;
  border-radius: 4px;
}

.grid-table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
.grid-table th, .grid-table td { border: 1px solid #e2e8f0; padding: 6px 10px; }
.grid-table thead th { background: #f8fafc; font-weight: 600; color: #1e293b; border: 1px solid #e2e8f0; }
.grid-table tbody tr:nth-child(even) { background: #f8fafc; }
.grid-table tbody tr:hover { background: #f1f5f9; }

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
