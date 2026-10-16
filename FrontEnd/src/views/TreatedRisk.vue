<script setup>
import { computed, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { formatDate } from '@/utils/date'

const toast = useToast()
const ctx = useContextStore()

const loading = ref(false)
const saving = ref(false)
const items = ref([])
const ambangSelera = ref(10)
const searchQuery = ref('')
const filterStatus = ref('all') // all, assessed, unassessed, met_appetite, over_appetite
const filterJenis = ref('all')

// Dialog Penilaian Treated Risk
const dialogVisible = ref(false)
const selectedRisk = ref(null)
const form = ref({
  risiko_id: null,
  dampak_treated: null,
  kemungkinan_treated: null,
  justifikasi: '',
})

// Dialog Referensi Kriteria Dampak & Kemungkinan
const criteriaDialogVisible = ref(false)

// AI Assistance state
const aiEvaluating = ref(false)
const aiSuggestion = ref(null)

const kemungkinanOptions = [
  { value: 1, label: '1 - Hampir Tidak Terjadi (Probabilitas < 20%)' },
  { value: 2, label: '2 - Jarang Terjadi (Probabilitas 20% - 40%)' },
  { value: 3, label: '3 - Kadang Terjadi (Probabilitas 40% - 60%)' },
  { value: 4, label: '4 - Sering Terjadi (Probabilitas 60% - 80%)' },
  { value: 5, label: '5 - Hampir Pasti Terjadi (Probabilitas > 80%)' },
]

const dampakOptions = [
  { value: 1, label: '1 - Tidak Signifikan (Dampak minimal, pelayanan normal)' },
  { value: 2, label: '2 - Minor (Dampak kecil, target tercapai dengan sedikit hambatan)' },
  { value: 3, label: '3 - Moderat (Dampak sedang, keterlambatan signifikan/pelayanan terganggu)' },
  { value: 4, label: '4 - Signifikan (Dampak besar, sasaran strategis terancam gagal)' },
  { value: 5, label: '5 - Sangat Signifikan (Dampak fatal/kerugian masif/reputasi rusak parah)' },
]

const levelColors = {
  'Sangat Rendah (1)': { color: '#059669', bg: '#ecfdf5', border: '#a7f3d0' },
  'Sangat Rendah': { color: '#059669', bg: '#ecfdf5', border: '#a7f3d0' },
  'Rendah (2)': { color: '#16a34a', bg: '#dcfce7', border: '#bbf7d0' },
  'Rendah': { color: '#16a34a', bg: '#dcfce7', border: '#bbf7d0' },
  'Sedang (3)': { color: '#d97706', bg: '#fef3c7', border: '#fde68a' },
  'Sedang': { color: '#d97706', bg: '#fef3c7', border: '#fde68a' },
  'Tinggi (4)': { color: '#ea580c', bg: '#ffedd5', border: '#fed7aa' },
  'Tinggi': { color: '#ea580c', bg: '#ffedd5', border: '#fed7aa' },
  'Sangat Tinggi (5)': { color: '#dc2626', bg: '#fee2e2', border: '#fecaca' },
  'Sangat Tinggi': { color: '#dc2626', bg: '#fee2e2', border: '#fecaca' },
}

const jenisLabels = {
  strategis_pemda: 'Strategis Pemda',
  strategis_opd: 'Strategis OPD',
  operasional_opd: 'Operasional OPD',
}

const responLabels = {
  kurangi_kemungkinan: { label: 'Kurangi Kemungkinan', icon: 'pi-arrow-down-left', color: '#2563eb', bg: '#eff6ff', hint: 'Fokus menurunkan skala kemungkinan' },
  kurangi_dampak: { label: 'Kurangi Dampak', icon: 'pi-shield', color: '#7c3aed', bg: '#f5f3ff', hint: 'Fokus menurunkan skala dampak' },
  bagi: { label: 'Bagi Risiko (Transfer)', icon: 'pi-share-alt', color: '#0d9488', bg: '#f0fdfa', hint: 'Pengalihan risiko ke pihak ketiga/asuransi' },
  hindari: { label: 'Hindari Risiko', icon: 'pi-ban', color: '#dc2626', bg: '#fef2f2', hint: 'Menghentikan aktivitas berisiko' },
  terima: { label: 'Terima Risiko', icon: 'pi-check', color: '#475569', bg: '#f8fafc', hint: 'Risiko dalam batas toleransi tanpa tindakan tambahan' },
}

// Matriks 5x5 lookup
const MATRIKS_MAP = {
  '5-1': 11, '5-2': 15, '5-3': 18, '5-4': 23, '5-5': 25,
  '4-1': 6,  '4-2': 12, '4-3': 16, '4-4': 19, '4-5': 24,
  '3-1': 4,  '3-2': 8,  '3-3': 14, '3-4': 17, '3-5': 22,
  '2-1': 2,  '2-2': 7,  '2-3': 10, '2-4': 13, '2-5': 21,
  '1-1': 1,  '1-2': 3,  '1-3': 5,  '1-4': 9,  '1-5': 20,
}

function calculateSkala(kemungkinan, dampak) {
  if (!kemungkinan || !dampak) return null
  return MATRIKS_MAP[`${kemungkinan}-${dampak}`] || null
}

function getLevelFromSkala(skala) {
  if (!skala) return null
  if (skala >= 20) return 'Sangat Tinggi (5)'
  if (skala >= 16) return 'Tinggi (4)'
  if (skala >= 11) return 'Sedang (3)'
  if (skala >= 6) return 'Rendah (2)'
  return 'Sangat Rendah (1)'
}

async function loadData() {
  if (!ctx.ready) return
  loading.value = true
  try {
    const { data } = await api.get('/risiko/treated', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    items.value = data.items || []
    ambangSelera.value = data.ambang_selera || 10
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal memuat data',
      detail: e.response?.data?.detail || 'Coba lagi nanti.',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

// KPI Stats
const totalCount = computed(() => items.value.length)
const withRtpCount = computed(() => items.value.filter((i) => i.rtp?.rencana_tindak).length)
const assessedCount = computed(() => items.value.filter((i) => i.treated?.skala_treated).length)
const metAppetiteCount = computed(() =>
  items.value.filter((i) => i.treated?.skala_treated && i.treated.skala_treated <= ambangSelera.value).length
)

// Filtered items
const filteredItems = computed(() => {
  return items.value.filter((row) => {
    // Filter Jenis
    if (filterJenis.value !== 'all' && row.jenis_risiko !== filterJenis.value) {
      return false
    }

    // Filter Status
    if (filterStatus.value === 'assessed' && !row.treated?.skala_treated) return false
    if (filterStatus.value === 'unassessed' && row.treated?.skala_treated) return false
    if (filterStatus.value === 'met_appetite' && (!row.treated?.skala_treated || row.treated.skala_treated > ambangSelera.value)) return false
    if (filterStatus.value === 'over_appetite' && (!row.treated?.skala_treated || row.treated.skala_treated <= ambangSelera.value)) return false

    // Search query
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      const matchKode = (row.kode_risiko || '').toLowerCase().includes(q)
      const matchUraian = (row.uraian_risiko || '').toLowerCase().includes(q)
      const matchOwner = (row.pemilik_risiko || '').toLowerCase().includes(q)
      const matchRtp = (row.rtp?.rencana_tindak || '').toLowerCase().includes(q)
      if (!matchKode && !matchUraian && !matchOwner && !matchRtp) return false
    }

    return true
  })
})

function openAssessDialog(row) {
  selectedRisk.value = row
  const t = row.treated || {}
  const an = row.analisis || {}

  // Set default nilai treated: jika belum ada, default ke nilai inheren atau turun 1 jika ada RTP
  let defD = t.dampak_treated || an.skala_dampak || null
  let defK = t.kemungkinan_treated || an.skala_kemungkinan || null

  form.value = {
    risiko_id: row.id,
    dampak_treated: defD,
    kemungkinan_treated: defK,
    justifikasi: t.justifikasi || '',
  }
  aiSuggestion.value = null
  dialogVisible.value = true
}

const previewTreatedSkala = computed(() => {
  return calculateSkala(form.value.kemungkinan_treated, form.value.dampak_treated)
})

const previewTreatedLevel = computed(() => {
  return getLevelFromSkala(previewTreatedSkala.value)
})

const previewDeltaSkor = computed(() => {
  const inh = selectedRisk.value?.analisis?.skala_risiko
  const tr = previewTreatedSkala.value
  if (inh != null && tr != null) {
    return roundTo(tr - inh, 1)
  }
  return null
})

function roundTo(val, dec = 1) {
  return Math.round(val * Math.pow(10, dec)) / Math.pow(10, dec)
}

// Evaluasi karakteristik RTP untuk panduan pengguna
const rtpCharacteristics = computed(() => {
  const r = selectedRisk.value?.rtp
  if (!r) return null
  const code = r.respon_risiko
  return responLabels[code] || { label: code || 'Belum Ditentukan', icon: 'pi-info-circle', hint: '' }
})

// Peringatan jika respon kurangi kemungkinan tapi kemungkinan tidak turun
const warningKarakteristik = computed(() => {
  if (!selectedRisk.value) return null
  const inhK = selectedRisk.value.analisis?.skala_kemungkinan
  const inhD = selectedRisk.value.analisis?.skala_dampak
  const trK = form.value.kemungkinan_treated
  const trD = form.value.dampak_treated
  const resp = selectedRisk.value.rtp?.respon_risiko

  if (!inhK || !trK) return null

  if (resp === 'kurangi_kemungkinan' && trK >= inhK) {
    return 'Karakteristik RTP adalah "Kurangi Kemungkinan", tetapi nilai kemungkinan treated belum diturunkan dari nilai inheren.'
  }
  if (resp === 'kurangi_dampak' && trD >= inhD) {
    return 'Karakteristik RTP adalah "Kurangi Dampak", tetapi nilai dampak treated belum diturunkan dari nilai inheren.'
  }
  return null
})

async function saveTreated() {
  if (!form.value.dampak_treated || !form.value.kemungkinan_treated) {
    toast.add({ severity: 'warn', summary: 'Data Belum Lengkap', detail: 'Tingkat Dampak dan Kemungkinan harus dipilih.', life: 3000 })
    return
  }
  saving.value = true
  try {
    await api.post('/risiko/treated', form.value)
    toast.add({ severity: 'success', summary: 'Treated Risk Tersimpan', detail: 'Koreksi level risiko berhasil diperbarui.', life: 2500 })
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: e.response?.data?.detail || 'Terjadi kesalahan.',
      life: 4000,
    })
  } finally {
    saving.value = false
  }
}

// Bantuan AI untuk Treated Risk
async function getAiTreatedSuggestion() {
  if (!selectedRisk.value) return
  aiEvaluating.value = true
  aiSuggestion.value = null
  try {
    const r = selectedRisk.value
    const currentOpd = ctx.opds?.find((o) => o.id === ctx.opdId)
    const { data } = await api.post('/ai/suggest-treated-risk', {
      risk_data: {
        uraian_risiko: r.uraian_risiko,
        level_inheren: r.analisis?.level || 'Sedang',
        kemungkinan_inheren: r.analisis?.skala_kemungkinan || 3,
        dampak_inheren: r.analisis?.skala_dampak || 3,
        pengendalian_ada: r.rtp?.pengendalian_ada || 'Belum ada',
        respon_risiko: r.rtp?.respon_risiko || 'kurangi_kemungkinan',
        rencana_tindak: r.rtp?.rencana_tindak || '',
      },
      context: {
        opd: currentOpd?.nama || '',
        tahun: ctx.tahun || 2026,
      },
    })
    aiSuggestion.value = data.suggestion
    toast.add({ severity: 'info', summary: 'Rekomendasi AI Siap', detail: 'Saran level treated risk berhasil dihasilkan.', life: 3000 })
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal memanggil AI'
    toast.add({ severity: 'error', summary: 'AI Error', detail: err, life: 4000 })
  } finally {
    aiEvaluating.value = false
  }
}

function applyAiSuggestion() {
  if (!aiSuggestion.value) return
  if (aiSuggestion.value.kemungkinan_treated) {
    form.value.kemungkinan_treated = Number(aiSuggestion.value.kemungkinan_treated)
  }
  if (aiSuggestion.value.dampak_treated) {
    form.value.dampak_treated = Number(aiSuggestion.value.dampak_treated)
  }
  if (aiSuggestion.value.justifikasi) {
    form.value.justifikasi = aiSuggestion.value.justifikasi
  }
  aiSuggestion.value = null
  toast.add({ severity: 'success', summary: 'Saran AI Diterapkan', detail: 'Nilai dan justifikasi telah diisikan ke form.', life: 2500 })
}

watch([() => ctx.opdId, () => ctx.tahun], loadData, { immediate: true })
</script>

<template>
  <div class="treated-risk-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-sliders-v"></i>
        </div>
        <div>
          <h1 class="page-title">Treated Risk (Tingkat Risiko Pasca-Pengendalian)</h1>
          <p class="page-desc">
            Tingkat risiko setelah adanya kegiatan pengendalian terpasang (existing control) dan Rencana Tindak Pengendalian (RTP)
          </p>
        </div>
      </div>
      <div class="header-actions">
        <Button
          label="Tabel Kriteria"
          icon="pi pi-book"
          severity="secondary"
          variant="outlined"
          @click="criteriaDialogVisible = true"
        />
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          :loading="loading"
          @click="loadData"
        />
      </div>
    </div>


    <!-- Stat Cards Header (Style Laporan Rekapitulasi) -->
    <div class="stat-grid no-print" style="margin-bottom: 18px;">
      <div class="stat">
        <div class="v">{{ totalCount }}</div>
        <div class="l">Total Risiko Teridentifikasi</div>
      </div>

      <div class="stat">
        <div class="v">
          {{ withRtpCount }} <small>({{ totalCount ? Math.round((withRtpCount / totalCount) * 100) : 0 }}%)</small>
        </div>
        <div class="l">Telah Memiliki RTP</div>
      </div>

      <div class="stat">
        <div class="v">
          {{ assessedCount }} <small>/ {{ totalCount }}</small>
        </div>
        <div class="l">Sudah Dinilai Treated Pasca-RTP</div>
      </div>

      <div class="stat">
        <div class="v">{{ metAppetiteCount }}</div>
        <div class="l">Memenuhi Selera Risiko (≤ {{ ambangSelera }})</div>
      </div>
    </div>

    <!-- Main Content Table Card -->
    <div class="content-card">
      <!-- Toolbar Filter & Search -->
      <div class="toolbar-wrap">
        <div class="toolbar-left">
          <div class="search-box">
            <i class="pi pi-search search-icon" />
            <InputText
              v-model="searchQuery"
              placeholder="Cari kode, uraian risiko, pemilik, atau RTP..."
              class="search-input"
            />
            <button
              v-if="searchQuery"
              class="clear-btn"
              @click="searchQuery = ''"
            >
              <i class="pi pi-times" />
            </button>
          </div>

          <Select
            v-model="filterStatus"
            :options="[
              { label: 'Semua Status Treated', value: 'all' },
              { label: 'Sudah Dinilai Treated', value: 'assessed' },
              { label: 'Belum Dinilai Treated', value: 'unassessed' },
              { label: 'Memenuhi Selera Risiko', value: 'met_appetite' },
              { label: 'Di Luar Selera Risiko', value: 'over_appetite' },
            ]"
            optionLabel="label"
            optionValue="value"
            class="filter-select"
          />

          <Select
            v-model="filterJenis"
            :options="[
              { label: 'Semua Jenis Risiko', value: 'all' },
              { label: 'Strategis Pemda', value: 'strategis_pemda' },
              { label: 'Strategis OPD', value: 'strategis_opd' },
              { label: 'Operasional OPD', value: 'operasional_opd' },
            ]"
            optionLabel="label"
            optionValue="value"
            class="filter-select"
          />
        </div>

        <div class="summary-count">
          Menampilkan <strong>{{ filteredItems.length }}</strong> dari <strong>{{ items.length }}</strong> risiko
        </div>
      </div>

      <!-- Table View -->
      <DataTable
        :value="filteredItems"
        :loading="loading"
        stripedRows
        responsiveLayout="scroll"
        class="custom-table"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-shield text-4xl text-slate-300 mb-2" />
            <p class="empty-title">Tidak ada data risiko yang ditemukan</p>
            <p class="empty-desc">Pastikan risiko telah diidentifikasi dan dianalisis di Form 3 dan Form 4.</p>
          </div>
        </template>

        <!-- No -->
        <Column header="No" :style="{ width: '50px', textAlign: 'center' }">
          <template #body="{ index }">
            <span class="index-num">{{ index + 1 }}</span>
          </template>
        </Column>

        <!-- Kode & Jenis -->
        <Column header="Kode & Jenis" :style="{ minWidth: '130px' }">
          <template #body="{ data }">
            <div class="kode-box">
              <span class="badge-kode">{{ data.kode_risiko }}</span>
              <span v-if="data.jenis_risiko" class="badge-jenis" :class="`jenis-${data.jenis_risiko}`">
                {{ jenisLabels[data.jenis_risiko] || data.jenis_risiko }}
              </span>
            </div>
          </template>
        </Column>

        <!-- Risiko & Pemilik -->
        <Column header="Uraian Peristiwa Risiko" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="risiko-cell">
              <span class="risiko-title">{{ data.uraian_risiko }}</span>
              <div class="risiko-meta">
                <span class="meta-item">
                  <i class="pi pi-user text-xs mr-1" />
                  {{ data.pemilik_risiko || '—' }}
                </span>
                <span v-if="data.kategori_risiko" class="meta-kategori">
                  {{ data.kategori_risiko }}
                </span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Tingkat Risiko Inheren (Form 4) -->
        <Column header="Risiko Inheren (Awal)" :style="{ minWidth: '150px' }">
          <template #body="{ data }">
            <div v-if="data.analisis?.skala_risiko" class="level-box">
              <span
                class="level-pill"
                :style="{
                  color: levelColors[data.analisis.level]?.color || '#475569',
                  backgroundColor: levelColors[data.analisis.level]?.bg || '#f1f5f9',
                  borderColor: levelColors[data.analisis.level]?.border || '#cbd5e1',
                }"
              >
                {{ data.analisis.level }}
              </span>
              <span class="formula-text">
                K: {{ data.analisis.skala_kemungkinan }} &times; D: {{ data.analisis.skala_dampak }} = <strong>{{ data.analisis.skala_risiko }}</strong>
              </span>
            </div>
            <span v-else class="text-xs text-slate-400 italic">Belum dinilai di Form 4</span>
          </template>
        </Column>

        <!-- Pengendalian Terpasang & Respon RTP -->
        <Column header="Pengendalian Terpasang & RTP" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="rtp-summary-box">
              <div v-if="data.rtp?.respon_risiko" class="respon-chip-row">
                <span
                  class="respon-badge"
                  :style="{
                    color: responLabels[data.rtp.respon_risiko]?.color || '#334155',
                    backgroundColor: responLabels[data.rtp.respon_risiko]?.bg || '#f1f5f9',
                  }"
                  :title="responLabels[data.rtp.respon_risiko]?.hint"
                >
                  <i :class="['pi', responLabels[data.rtp.respon_risiko]?.icon || 'pi-shield']" />
                  {{ responLabels[data.rtp.respon_risiko]?.label || data.rtp.respon_risiko }}
                </span>
              </div>

              <div v-if="data.rtp?.rencana_tindak" class="rtp-text">
                <strong>RTP:</strong> {{ data.rtp.rencana_tindak }}
              </div>
              <div v-else class="text-xs text-amber-600 italic">
                <i class="pi pi-exclamation-circle mr-1" /> RTP belum dirumuskan
              </div>

              <div v-if="data.rtp?.pengendalian_ada" class="control-existing">
                <small><strong>Existing Control:</strong> {{ data.rtp.pengendalian_ada }}</small>
              </div>

              <!-- Status Realisasi & Bukti Dukung -->
              <div class="mt-2 pt-1 border-t border-slate-100 flex items-center justify-between flex-wrap gap-1">
                <span v-if="data.realisasi?.status_realisasi === 'selesai'" class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  <i class="pi pi-check-circle text-emerald-600 text-[10px]" /> Realisasi Selesai
                  <span v-if="data.realisasi?.tanggal_realisasi" class="text-slate-500 font-normal">({{ formatDate(data.realisasi.tanggal_realisasi) }})</span>
                </span>
                <span v-else-if="data.realisasi?.status_realisasi === 'proses'" class="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  <i class="pi pi-spin pi-spinner text-amber-600 text-[10px]" /> Sedang Berjalan
                </span>
                <span v-else class="inline-flex items-center gap-1 text-[11px] text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded">
                  <i class="pi pi-clock text-[10px]" /> Belum Realisasi
                </span>

                <a
                  v-if="data.realisasi?.bukti_berkas_id"
                  :href="`/api/risiko/rtp/${data.id}/berkas/${data.realisasi.bukti_berkas_id}`"
                  target="_blank"
                  class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900 bg-emerald-100 hover:bg-emerald-200 px-2 py-0.5 rounded transition-colors no-underline"
                  title="Unduh Berkas Bukti Realisasi"
                >
                  <i class="pi pi-paperclip text-[10px]" /> Eviden
                </a>
              </div>
            </div>
          </template>

        </Column>

        <!-- Treated Risk (Pasca RTP) -->
        <Column header="Treated Risk (Pasca RTP)" :style="{ minWidth: '170px' }">
          <template #body="{ data }">
            <div v-if="data.treated?.skala_treated" class="treated-cell">
              <span
                class="level-pill"
                :style="{
                  color: levelColors[data.treated.level_treated]?.color || '#475569',
                  backgroundColor: levelColors[data.treated.level_treated]?.bg || '#f1f5f9',
                  borderColor: levelColors[data.treated.level_treated]?.border || '#cbd5e1',
                }"
              >
                {{ data.treated.level_treated }}
              </span>
              <span class="formula-text">
                K: {{ data.treated.kemungkinan_treated }} &times; D: {{ data.treated.dampak_treated }} = <strong>{{ data.treated.skala_treated }}</strong>
              </span>

              <!-- Delta Skor & Pergeseran -->
              <div v-if="data.treated.delta_skor != null" class="delta-badge" :class="data.treated.delta_skor <= 0 ? 'delta-down' : 'delta-up'">
                <i :class="['pi', data.treated.delta_skor <= 0 ? 'pi-arrow-down' : 'pi-arrow-up']" />
                <span>Skor {{ data.treated.delta_skor > 0 ? '+' : '' }}{{ data.treated.delta_skor }}</span>
              </div>
            </div>
            <div v-else class="empty-prompt">
              <span class="text-xs text-slate-400 italic">Belum dinilai</span>
            </div>
          </template>
        </Column>

        <!-- Status Selera Risiko -->
        <Column header="Selera Risiko" :style="{ width: '130px', textAlign: 'center' }">
          <template #body="{ data }">
            <div v-if="data.treated?.skala_treated">
              <span
                v-if="data.treated.memenuhi_selera"
                class="appetite-badge appetite-ok"
                :title="`Skor Treated (${data.treated.skala_treated}) <= Ambang Selera (${ambangSelera})`"
              >
                <i class="pi pi-check" /> Memenuhi
              </span>
              <span
                v-else
                class="appetite-badge appetite-no"
                :title="`Skor Treated (${data.treated.skala_treated}) > Ambang Selera (${ambangSelera})`"
              >
                <i class="pi pi-exclamation-triangle" /> Melebihi
              </span>
            </div>
            <span v-else class="text-slate-300">—</span>
          </template>
        </Column>

        <!-- Aksi -->
        <Column header="Aksi" :style="{ width: '130px', textAlign: 'center' }">
          <template #body="{ data }">
            <Button
              :label="data.treated?.skala_treated ? 'Ubah' : 'Nilai Treated'"
              :icon="data.treated?.skala_treated ? 'pi pi-pencil' : 'pi pi-sliders-v'"
              size="small"
              :severity="data.treated?.skala_treated ? 'secondary' : 'primary'"
              class="btn-assess"
              @click="openAssessDialog(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- ==================== Dialog Penilaian Treated Risk ==================== -->
    <Dialog
      v-model:visible="dialogVisible"
      header="Penetapan Level Treated Risk (Pasca-RTP)"
      modal
      :style="{ width: '740px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div v-if="selectedRisk" class="dialog-treated-body">
        <!-- Konteks Risiko & Inheren -->
        <div class="context-card">
          <div class="context-top">
            <span class="badge-kode">{{ selectedRisk.kode_risiko }}</span>
            <span v-if="selectedRisk.jenis_risiko" class="badge-jenis" :class="`jenis-${selectedRisk.jenis_risiko}`">
              {{ jenisLabels[selectedRisk.jenis_risiko] }}
            </span>
            <span class="context-owner">Pemilik: <strong>{{ selectedRisk.pemilik_risiko || '—' }}</strong></span>
          </div>
          <div class="context-title">{{ selectedRisk.uraian_risiko }}</div>

          <div class="inherent-summary-strip">
            <div class="strip-item">
              <span class="strip-lbl">Level Inheren Awal:</span>
              <span
                class="level-pill text-xs"
                :style="{
                  color: levelColors[selectedRisk.analisis?.level]?.color || '#475569',
                  backgroundColor: levelColors[selectedRisk.analisis?.level]?.bg || '#f1f5f9',
                }"
              >
                {{ selectedRisk.analisis?.level || 'Belum dinilai' }}
              </span>
              <span class="strip-val">
                (K: {{ selectedRisk.analisis?.skala_kemungkinan || '-' }} &times; D: {{ selectedRisk.analisis?.skala_dampak || '-' }} = Skor {{ selectedRisk.analisis?.skala_risiko || '-' }})
              </span>
            </div>
            <div class="strip-item">
              <span class="strip-lbl">Ambang Selera Risiko:</span>
              <strong>Skor &le; {{ ambangSelera }}</strong>
            </div>
          </div>
        </div>

        <!-- Rincian RTP & Karakteristik Respon -->
        <div class="rtp-highlight-card">
          <div class="rtp-highlight-header">
            <div class="rtp-char-badge" :style="{ color: rtpCharacteristics?.color, backgroundColor: rtpCharacteristics?.bg }">
              <i :class="['pi', rtpCharacteristics?.icon]" />
              <strong>Karakteristik Respon: {{ rtpCharacteristics?.label }}</strong>
            </div>
            <Button
              label="Bantuan Evaluasi AI"
              icon="pi pi-sparkles"
              size="small"
              severity="help"
              variant="outlined"
              :loading="aiEvaluating"
              @click="getAiTreatedSuggestion"
            />
          </div>

          <div class="rtp-detail-content">
            <p><strong>Rencana Tindak Pengendalian (RTP):</strong> {{ selectedRisk.rtp?.rencana_tindak || 'RTP belum diisi di Form 7.' }}</p>
            <p v-if="selectedRisk.rtp?.pengendalian_ada" class="text-xs text-slate-600 mt-1">
              <strong>Pengendalian Terpasang (Existing Control):</strong> {{ selectedRisk.rtp.pengendalian_ada }}
            </p>
            <div class="mt-2 p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div>
                <strong>Status Realisasi: </strong>
                <span v-if="selectedRisk.realisasi?.status_realisasi === 'selesai'" class="text-emerald-700 font-bold">
                  <i class="pi pi-check-circle" /> Selesai Terealisasi
                  <span v-if="selectedRisk.realisasi?.tanggal_realisasi" class="font-normal text-slate-500">({{ formatDate(selectedRisk.realisasi.tanggal_realisasi) }})</span>
                </span>
                <span v-else-if="selectedRisk.realisasi?.status_realisasi === 'proses'" class="text-amber-700 font-bold">
                  <i class="pi pi-spin pi-spinner" /> Sedang Berjalan
                </span>
                <span v-else class="text-slate-500 italic">
                  <i class="pi pi-clock" /> Belum Terealisasi
                </span>
              </div>
              <a
                v-if="selectedRisk.realisasi?.bukti_berkas_id"
                :href="`/api/risiko/rtp/${selectedRisk.id}/berkas/${selectedRisk.realisasi.bukti_berkas_id}`"
                target="_blank"
                class="text-emerald-700 hover:text-emerald-900 font-bold underline inline-flex items-center gap-1"
              >
                <i class="pi pi-paperclip" /> Unduh Berkas Eviden
              </a>
            </div>
          </div>


          <div class="rtp-char-guide">
            <i class="pi pi-info-circle text-indigo-600 mr-1" />
            <small>
              <strong>Panduan Penetapan:</strong> {{ rtpCharacteristics?.hint || 'Sesuaikan penurunan dampak/kemungkinan dengan karakteristik tindakan pengendalian.' }}
            </small>
          </div>
        </div>

        <!-- Rekomendasi AI Box (Jika dihasilkan) -->
        <div v-if="aiSuggestion" class="ai-suggestion-box">
          <div class="ai-sug-header">
            <span class="ai-sug-title">
              <i class="pi pi-sparkles text-purple-600 mr-1" />
              <strong>Rekomendasi Penilaian AI:</strong>
            </span>
            <Button
              label="Terapkan Rekomendasi Ini"
              icon="pi pi-check"
              size="small"
              severity="primary"
              @click="applyAiSuggestion"
            />
          </div>
          <div class="ai-sug-body">
            <div class="ai-sug-scores">
              <span>Kemungkinan: <strong>{{ aiSuggestion.kemungkinan_treated }}</strong></span>
              <span>&bull;</span>
              <span>Dampak: <strong>{{ aiSuggestion.dampak_treated }}</strong></span>
              <span>&bull;</span>
              <span>Skor Terkoreksi: <strong>{{ calculateSkala(aiSuggestion.kemungkinan_treated, aiSuggestion.dampak_treated) }}</strong></span>
            </div>
            <p class="ai-sug-justifikasi">{{ aiSuggestion.justifikasi }}</p>
          </div>
        </div>

        <!-- Form Isian Tingkat Kemungkinan & Dampak Pasca-RTP -->
        <div class="treated-form-grid">
          <!-- Kemungkinan Treated -->
          <div class="form-group">
            <label class="form-lbl">
              Tingkat Kemungkinan Pasca-RTP <span class="text-red-500">*</span>
            </label>
            <Select
              v-model="form.kemungkinan_treated"
              :options="kemungkinanOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Pilih tingkat kemungkinan setelah RTP"
              fluid
            />
            <small class="muted">
              Kemungkinan inheren awal: <strong>{{ selectedRisk.analisis?.skala_kemungkinan || '-' }}</strong>
            </small>
          </div>

          <!-- Dampak Treated -->
          <div class="form-group">
            <label class="form-lbl">
              Tingkat Dampak Pasca-RTP <span class="text-red-500">*</span>
            </label>
            <Select
              v-model="form.dampak_treated"
              :options="dampakOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Pilih tingkat dampak setelah RTP"
              fluid
            />
            <small class="muted">
              Dampak inheren awal: <strong>{{ selectedRisk.analisis?.skala_dampak || '-' }}</strong>
            </small>
          </div>
        </div>

        <!-- Warning jika karakteristik respon tidak konsisten dengan penurunan nilai -->
        <Message v-if="warningKarakteristik" severity="warn" :closable="false" class="mt-2 mb-2">
          <i class="pi pi-exclamation-triangle mr-1" /> {{ warningKarakteristik }}
        </Message>

        <!-- Live Score Calculation Preview -->
        <div v-if="previewTreatedSkala" class="preview-treated-strip">
          <div class="preview-left">
            <span class="preview-title">Hasil Koreksi Treated Risk:</span>
            <span
              class="level-pill"
              :style="{
                color: levelColors[previewTreatedLevel]?.color,
                backgroundColor: levelColors[previewTreatedLevel]?.bg,
                borderColor: levelColors[previewTreatedLevel]?.border,
              }"
            >
              {{ previewTreatedLevel }}
            </span>
            <span class="preview-calc">
              Skor: <strong>{{ previewTreatedSkala }}</strong>
              (K: {{ form.kemungkinan_treated }} &times; D: {{ form.dampak_treated }})
            </span>
          </div>

          <div class="preview-right">
            <div v-if="previewDeltaSkor != null" class="delta-badge" :class="previewDeltaSkor <= 0 ? 'delta-down' : 'delta-up'">
              <i :class="['pi', previewDeltaSkor <= 0 ? 'pi-arrow-down' : 'pi-arrow-up']" />
              <span>Pergeseran Skor: {{ previewDeltaSkor > 0 ? '+' : '' }}{{ previewDeltaSkor }}</span>
            </div>
            <span
              :class="['appetite-badge', previewTreatedSkala <= ambangSelera ? 'appetite-ok' : 'appetite-no']"
            >
              {{ previewTreatedSkala <= ambangSelera ? 'Memenuhi Selera' : 'Melebihi Selera' }}
            </span>
          </div>
        </div>

        <!-- Justifikasi & Dasar Pertimbangan -->
        <div class="form-group mt-3">
          <label class="form-lbl">
            Dasar Pertimbangan & Justifikasi Koreksi Nilai Risiko Pasca-RTP <span class="text-red-500">*</span>
          </label>
          <Textarea
            v-model="form.justifikasi"
            rows="3"
            autoResize
            placeholder="Jelaskan alasan teknis mengapa rencana tindak pengendalian (RTP) ini diperkirakan efektif menurunkan kemungkinan dan/atau dampak..."
            fluid
          />
          <small class="muted">
            Wajib diisi sebagai bukti dasar pertimbangan audit dan akuntabilitas evaluasi efektivitas pengendalian.
          </small>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Lihat Kriteria Matriks"
            icon="pi pi-book"
            severity="secondary"
            variant="text"
            @click="criteriaDialogVisible = true"
          />
          <div class="spacer" />
          <Button
            label="Batal"
            severity="secondary"
            variant="outlined"
            :disabled="saving"
            @click="dialogVisible = false"
          />
          <Button
            label="Simpan Treated Risk"
            icon="pi pi-check"
            severity="primary"
            :loading="saving"
            @click="saveTreated"
          />
        </div>
      </template>
    </Dialog>

    <!-- ==================== Dialog Referensi Kriteria Perwal 1/2026 ==================== -->
    <Dialog
      v-model:visible="criteriaDialogVisible"
      header="Tabel Kriteria Dampak & Kemungkinan (Kebijakan Perwal No. 1/2026)"
      modal
      :style="{ width: '840px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div class="criteria-dialog-content">
        <p class="muted text-sm mb-3">
          Gunakan kriteria standar di bawah ini sebagai acuan objektif dalam menetapkan pergeseran tingkat kemungkinan dan dampak setelah adanya kegiatan pengendalian (RTP).
        </p>

        <!-- Kriteria Kemungkinan -->
        <div class="criteria-sec">
          <h4 class="sec-title text-indigo-700">
            <i class="pi pi-chart-line mr-1" /> Tabel Kriteria Kemungkinan (Likelihood)
          </h4>
          <table class="criteria-table">
            <thead>
              <tr>
                <th style="width: 80px; text-align: center;">Skala</th>
                <th style="width: 180px;">Kategori</th>
                <th>Parameter Persentase & Frekuensi Kejadian</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-center font-bold">1</td>
                <td><span class="font-semibold text-emerald-700">Hampir Tidak Terjadi</span></td>
                <td>Probabilitas &lt; 20% dalam 1 periode penilaian; kejadian sangat luar biasa atau hampir tidak pernah terjadi.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">2</td>
                <td><span class="font-semibold text-green-700">Jarang Terjadi</span></td>
                <td>Probabilitas 20% s.d. 40%; dapat terjadi 1 kali dalam 2-3 tahun; kondisi pengendalian terpasang cukup memadai.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">3</td>
                <td><span class="font-semibold text-amber-700">Kadang Terjadi</span></td>
                <td>Probabilitas 40% s.d. 60%; dapat terjadi 1 kali dalam 1 tahun anggaran berjalan; terdapat celah pengendalian.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">4</td>
                <td><span class="font-semibold text-orange-700">Sering Terjadi</span></td>
                <td>Probabilitas 60% s.d. 80%; kemungkinan terjadi beberapa kali dalam setahun; pengendalian belum berjalan efektif.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">5</td>
                <td><span class="font-semibold text-red-700">Hampir Pasti Terjadi</span></td>
                <td>Probabilitas &gt; 80%; hampir dipastikan terjadi secara berulang dalam periode berjalan tanpa tindakan pencegahan.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Kriteria Dampak -->
        <div class="criteria-sec mt-4">
          <h4 class="sec-title text-indigo-700">
            <i class="pi pi-exclamation-triangle mr-1" /> Tabel Kriteria Dampak (Consequence)
          </h4>
          <table class="criteria-table">
            <thead>
              <tr>
                <th style="width: 80px; text-align: center;">Skala</th>
                <th style="width: 180px;">Kategori</th>
                <th>Deskripsi Dampak Terhadap Target, Finansial & Layanan Publik</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-center font-bold">1</td>
                <td><span class="font-semibold text-emerald-700">Tidak Signifikan</span></td>
                <td>Kerugian finansial sangat minimal (&le; toleransi biaya operasional); tidak mengganggu pencapaian target kinerja; pelayanan publik tetap berjalan normal.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">2</td>
                <td><span class="font-semibold text-green-700">Minor</span></td>
                <td>Kerugian finansial kecil; keterlambatan jadwal target minor tanpa merusak sasaran akhir; gangguan layanan dapat diatasi dalam hitungan jam.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">3</td>
                <td><span class="font-semibold text-amber-700">Moderat</span></td>
                <td>Kerugian finansial sedang; target sasaran kinerja OPD terganggu secara nyata; pelayanan publik mengalami hambatan signifikan beberapa hari.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">4</td>
                <td><span class="font-semibold text-orange-700">Signifikan</span></td>
                <td>Kerugian finansial besar; target prioritas daerah berpotensi gagal tercapai; tuntutan hukum atau pemberitaan negatif meluas di media.</td>
              </tr>
              <tr>
                <td class="text-center font-bold">5</td>
                <td><span class="font-semibold text-red-700">Sangat Signifikan</span></td>
                <td>Kerugian finansial masif; kegagalan fatal pada program prioritas pemerintah daerah; krisis kepercayaan publik berat dan sanksi hukum berat.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Tutup Referensi"
            severity="secondary"
            @click="criteriaDialogVisible = false"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.treated-risk-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 2rem;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
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
  background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
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
  gap: 0.75rem;
  align-items: center;
}


/* Content Card & Toolbar */
.content-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.toolbar-wrap {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
  font-size: 0.85rem;
}

.search-input {
  padding-left: 32px !important;
  font-size: 0.84rem !important;
  width: 100%;
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 2px 4px;
}

.filter-select {
  font-size: 0.84rem;
  min-width: 180px;
}

.summary-count {
  font-size: 0.82rem;
  color: #64748b;
}

/* Table cells */
.index-num {
  font-weight: 600;
  font-size: 0.84rem;
  color: #64748b;
}

.kode-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.badge-kode {
  font-family: monospace;
  font-weight: 700;
  font-size: 0.78rem;
  color: #1e293b;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  width: fit-content;
}

.badge-jenis {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  width: fit-content;
}

.jenis-strategis_pemda { background: #fee2e2; color: #991b1b; }
.jenis-strategis_opd { background: #e0e7ff; color: #3730a3; }
.jenis-operasional_opd { background: #ecfdf5; color: #065f46; }

.risiko-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.risiko-title {
  font-weight: 600;
  font-size: 0.86rem;
  color: #0f172a;
  line-height: 1.45;
}

.risiko-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 0.74rem;
  color: #64748b;
}

.meta-kategori {
  font-size: 0.68rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 1px 6px;
  border-radius: 4px;
  color: #475569;
}

.level-box, .treated-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.level-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid transparent;
  width: fit-content;
}

.formula-text {
  font-size: 0.74rem;
  color: #64748b;
}

.delta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  width: fit-content;
}

.delta-down {
  background: #dcfce7;
  color: #15803d;
}

.delta-up {
  background: #fee2e2;
  color: #b91c1c;
}

.appetite-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.appetite-ok {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.appetite-no {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.rtp-summary-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.respon-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.rtp-text {
  font-size: 0.8rem;
  line-height: 1.4;
  color: #1e293b;
}

.control-existing {
  font-size: 0.74rem;
  color: #64748b;
  background: #f8fafc;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #f1f5f9;
}

.btn-assess {
  font-size: 0.78rem !important;
}

/* Dialog Styles */
.dialog-treated-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.context-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
}

.context-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.context-owner {
  margin-left: auto;
  font-size: 0.78rem;
  color: #475569;
}

.context-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.45;
}

.inherent-summary-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 10px;
  margin-top: 10px;
  font-size: 0.8rem;
  flex-wrap: wrap;
  gap: 8px;
}

.strip-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.strip-lbl {
  color: #64748b;
  font-weight: 600;
}

.rtp-highlight-card {
  background: #fbfbfe;
  border: 1px solid #e0e7ff;
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rtp-highlight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rtp-char-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  padding: 4px 10px;
  border-radius: 6px;
}

.rtp-detail-content {
  font-size: 0.84rem;
  line-height: 1.48;
  color: #1e293b;
}

.rtp-detail-content p {
  margin: 0;
}

.rtp-char-guide {
  background: #f5f3ff;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 0.76rem;
  color: #4338ca;
  display: flex;
  align-items: center;
}

/* AI Suggestion Box */
.ai-suggestion-box {
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
  border: 1px solid #d8b4fe;
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ai-sug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-sug-title {
  font-size: 0.82rem;
  color: #6b21a8;
}

.ai-sug-scores {
  font-size: 0.82rem;
  color: #581c87;
  display: flex;
  gap: 8px;
}

.ai-sug-justifikasi {
  margin: 4px 0 0;
  font-size: 0.78rem;
  line-height: 1.45;
  color: #4c1d95;
  background: rgba(255, 255, 255, 0.75);
  padding: 6px 8px;
  border-radius: 6px;
}

.treated-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

@media (max-width: 600px) {
  .treated-form-grid { grid-template-columns: 1fr; }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-lbl {
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
}

.preview-treated-strip {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-left, .preview-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
}

.preview-calc {
  font-size: 0.82rem;
  color: #64748b;
}

.dialog-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.spacer { flex: 1; }

/* Criteria Table */
.criteria-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.criteria-sec {
  background: #ffffff;
}

.sec-title {
  margin: 0 0 8px;
  font-size: 0.95rem;
  font-weight: 700;
}

.criteria-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.criteria-table th, .criteria-table td {
  border: 1px solid #e2e8f0;
  padding: 8px 10px;
  line-height: 1.45;
}

.criteria-table th {
  background: #f8fafc;
  font-weight: 700;
  color: #334155;
}

.criteria-table tr:nth-child(even) {
  background: #fbfcfd;
}
</style>
