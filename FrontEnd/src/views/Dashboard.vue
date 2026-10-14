<script setup>
import { computed, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'
import {
  getMatrixScore,
  getMatrixLevel,
  getToleranceBorderStyles,
} from '@/utils/matriks'

const router = useRouter()
const ctx = useContextStore()
const data = ref(null)
const loading = ref(true)
const policy = ref(null)
const governance = ref(null)
const loadError = ref('')
let loadSerial = 0

// Filter jenis risiko untuk heatmap
const filterJenis = ref('all')

// Drilldown modal pada sel heatmap
const dialogVisible = ref(false)
const selectedCell = ref(null)

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

const levelBg = {
  'Sangat Rendah (1)': '#dcfce7',
  'Sangat Rendah': '#dcfce7',
  'Rendah (2)': '#ecfdf5',
  'Rendah': '#ecfdf5',
  'Sedang (3)': '#fef9c3',
  'Sedang': '#fef9c3',
  'Tinggi (4)': '#ffedd5',
  'Tinggi': '#ffedd5',
  'Sangat Tinggi (5)': '#fee2e2',
  'Sangat Tinggi': '#fee2e2',
}

const jenisLabel = {
  strategis_pemda: 'Strategis Pemda',
  strategis_opd: 'Strategis OPD',
  operasional_opd: 'Operasional OPD',
}

async function load() {
  if (!ctx.ready) return
  const serial = ++loadSerial
  loading.value = true
  loadError.value = ''
  try {
    const params = { opd_id: ctx.opdId, tahun: ctx.tahun }
    const results = await Promise.allSettled([
      api.get('/dashboard/summary', {params}),
      api.get('/selera-risiko', {params}),
      api.get('/tata-kelola/ringkasan', {params}),
    ])
    if (serial !== loadSerial) return
    const failed = results.find(r => r.status === 'rejected')
    if (failed) throw failed.reason
    data.value = results[0].value.data
    policy.value = results[1].value.data
    governance.value = results[2].value.data
  } catch (err) {
    if (serial === loadSerial) loadError.value = 'Gagal memuat dashboard. Silakan segarkan kembali.'
  } finally {
    if (serial === loadSerial) loading.value = false
  }
}

// 5x5 Matrix Skala 5 sampai 1
const kemungkinanScale = [
  { val: 5, label: '5 Hampir pasti terjadi', short: 'Hampir Pasti' },
  { val: 4, label: '4 Sering terjadi', short: 'Sering' },
  { val: 3, label: '3 Kadang terjadi', short: 'Kadang' },
  { val: 2, label: '2 Jarang terjadi', short: 'Jarang' },
  { val: 1, label: '1 Hampir tidak terjadi', short: 'Hampir Tidak' },
]

const dampakScale = [
  { val: 1, label: '1 Tidak signifikan', short: 'Tdk Signifikan' },
  { val: 2, label: '2 Minor', short: 'Minor' },
  { val: 3, label: '3 Moderat', short: 'Moderat' },
  { val: 4, label: '4 Signifikan', short: 'Signifikan' },
  { val: 5, label: '5 Sangat Signifikan', short: 'Sgt Signifikan' },
]

function getCellLevel(k, d) {
  return getMatrixLevel(k, d)
}

function getCellClass(k, d) {
  const score = getMatrixScore(k, d)
  if (score >= 20) return 'lvl-sangat-tinggi'
  if (score >= 16) return 'lvl-tinggi'
  if (score >= 11) return 'lvl-sedang'
  if (score >= 6) return 'lvl-rendah'
  return 'lvl-sangat-rendah'
}

function getCellRisks(k, d) {
  if (!data.value?.heatmap?.cells) return []
  const cellKey = `${k}-${d}`
  const list = data.value.heatmap.cells[cellKey] || []
  if (filterJenis.value === 'all') return list
  return list.filter((r) => r.jenis_risiko === filterJenis.value)
}

function openCellDialog(k, d) {
  const risks = getCellRisks(k, d)
  selectedCell.value = {
    k,
    d,
    score: getMatrixScore(k, d),
    level: getCellLevel(k, d),
    kLabel: kemungkinanScale.find((item) => item.val === k)?.label,
    dLabel: dampakScale.find((item) => item.val === d)?.label,
    risks,
  }
  dialogVisible.value = true
}

function navigateTo(path) {
  if (path) router.push(({ '/rtp': '/form7', '/analisis': '/form4' })[path] || path)
}

const sortedKategori = computed(() => {
  if (!data.value?.risiko_per_kategori) return []
  return Object.entries(data.value.risiko_per_kategori)
    .map(([nama, jumlah]) => ({ nama, jumlah }))
    .sort((a, b) => b.jumlah - a.jumlah)
})

const maxKategoriCount = computed(() => {
  if (!sortedKategori.value.length) return 1
  return Math.max(...sortedKategori.value.map((k) => k.jumlah), 1)
})

watch([() => ctx.opdId, () => ctx.tahun], load, { immediate: true })
</script>

<template>
  <p v-if="loadError" role="alert">{{ loadError }}</p>
  <div v-if="data" class="dashboard-container">
    <div v-if="governance" class="page-card">
      <h3>Keputusan & efektivitas pengendalian</h3>
      <p><strong>{{ governance.terlambat }}</strong> tindakan terlambat · <strong>{{ governance.menunggu }}</strong> respons menunggu keputusan · <strong>{{ governance.residual_melampaui }}</strong> risiko residual melampaui batas · <strong>{{ governance.perlu_penilaian_ulang }}</strong> risiko perlu ditinjau setelah kejadian.</p>
      <router-link :to="{name:'tata-kelola'}">Buka pemantauan dan tindak lanjut →</router-link>
      <p class="muted">Selera Risiko: {{ policy?.visual?.beragam ? 'Ambang berbeda antar Pemilik Risiko; buka Matriks Risiko untuk memilih pemilik.' : policy?.visual?.ditetapkan ? `Skor 1–${policy.visual.ambang} diterima.` : 'Belum ditetapkan.' }} <router-link :to="{ name: 'selera-risiko' }">Kelola Selera Risiko</router-link></p>
    </div>
    <!-- Header Eksekutif -->
    <div class="exec-header page-card">
      <div class="exec-header-content">
        <div class="badge-tag">Dashboard</div>
        <h1 class="exec-title">Manajemen Risiko</h1>
        <div class="exec-meta">
          <span><i class="pi pi-building"></i> <strong>{{ ctx.opd?.nama_pd || 'Perangkat Daerah' }}</strong></span>
          <span class="dot-sep">•</span>
          <span><i class="pi pi-calendar"></i> Tahun Penilaian: <strong>{{ ctx.tahun }}</strong></span>
          <span class="dot-sep">•</span>
          <span><i class="pi pi-clock"></i> Status: <Tag severity="success" value="Aktif" /></span>
        </div>
      </div>
      <div class="exec-actions">
        <Button
          icon="pi pi-refresh"
          label="Segarkan"
          outlined
          size="small"
          :loading="loading"
          @click="load"
        />
        <Button
          icon="pi pi-arrow-right"
          label="RTP Form 7"
          size="small"
          @click="navigateTo('/rtp')"
        />
      </div>
    </div>

    <!-- 6 KPI Stat Cards Utama -->
    <div class="kpi-grid">
      <!-- KPI 1: Total Risiko Teridentifikasi -->
      <div class="kpi-card accent-indigo">
        <div class="kpi-top">
          <span class="kpi-label">Total Risiko Teridentifikasi</span>
          <div class="kpi-icon"><i class="pi pi-shield"></i></div>
        </div>
        <div class="kpi-value">{{ data.jumlah_risiko }}</div>
        <div class="kpi-subtext">
          <span>Strategis Pemda: <b>{{ data.risiko_per_jenis.strategis_pemda || 0 }}</b></span>
          <span class="sep">|</span>
          <span>OPD: <b>{{ (data.risiko_per_jenis.strategis_opd || 0) + (data.risiko_per_jenis.operasional_opd || 0) }}</b></span>
        </div>
      </div>

      <!-- KPI 2: Analisis Selesai -->
       <!--
      <div class="kpi-card accent-blue">
        <div class="kpi-top">
          <span class="kpi-label">Progres Analisis (Form 4)</span>
          <div class="kpi-icon"><i class="pi pi-chart-line"></i></div>
        </div>
        <div class="kpi-value-row">
          <div class="kpi-value">{{ data.jumlah_dianalisis }}<span class="kpi-denom">/{{ data.jumlah_risiko }}</span></div>
          <Tag :severity="data.persentase_analisis === 100 ? 'success' : 'warn'" :value="`${data.persentase_analisis}% Selesai`" />
        </div>
        <div class="kpi-progress-bar">
          <div class="bar-fill blue" :style="{ width: `${data.persentase_analisis}%` }"></div>
        </div>
      </div>
      -->

      <!-- KPI 3: Risiko Prioritas -->
      <div class="kpi-card accent-rose">
        <div class="kpi-top">
          <span class="kpi-label">Risiko Prioritas</span>
          <div class="kpi-icon"><i class="pi pi-exclamation-triangle"></i></div>
        </div>
        <div class="kpi-value danger-text">{{ data.jumlah_prioritas }}</div>
        <div class="kpi-subtext">
          <span>Level Tinggi / Sangat Tinggi</span>
        </div>
      </div>

      <!-- KPI 4: Capaian RTP Prioritas -->
      <div class="kpi-card accent-emerald">
        <div class="kpi-top">
          <span class="kpi-label">Tindak Pengendalian (RTP)</span>
          <div class="kpi-icon"><i class="pi pi-check-circle"></i></div>
        </div>
        <div class="kpi-value-row">
          <div class="kpi-value success-text">{{ data.prioritas_dengan_rtp }}<span class="kpi-denom">/{{ data.jumlah_prioritas }}</span></div>
          <Tag :severity="data.prioritas_tanpa_rtp > 0 ? 'danger' : 'success'" :value="`${data.persentase_rtp}% Ber-RTP`" />
        </div>
        <div class="kpi-subtext">
          <span v-if="data.prioritas_tanpa_rtp > 0" class="text-danger font-semibold">
            <i class="pi pi-exclamation-circle"></i> {{ data.prioritas_tanpa_rtp }} prioritas belum ada RTP
          </span>
          <span v-else class="text-success font-semibold">
            <i class="pi pi-check"></i> Seluruh prioritas ber-RTP
          </span>
        </div>
      </div>

      <!-- KPI 5: Profil Kendali (C vs UC) -->
      <div class="kpi-card accent-amber">
        <div class="kpi-top">
          <span class="kpi-label">Profil Kendali (C / UC)</span>
          <div class="kpi-icon"><i class="pi pi-sliders-h"></i></div>
        </div>
        <div class="kpi-cuc-row">
          <div class="cuc-item">
            <span class="cuc-num">{{ data.risiko_per_cuc.C || 0 }}</span>
            <span class="cuc-tag tag-c">Controllable (C)</span>
          </div>
          <div class="cuc-divider"></div>
          <div class="cuc-item">
            <span class="cuc-num">{{ data.risiko_per_cuc.UC || 0 }}</span>
            <span class="cuc-tag tag-uc">Uncontrollable (UC)</span>
          </div>
        </div>
      </div>

      <!-- KPI 6: Lingkungan Pengendalian (CEE) -->
      <div class="kpi-card accent-purple">
        <div class="kpi-top">
          <span class="kpi-label">Responden Kuesioner CEE</span>
          <div class="kpi-icon"><i class="pi pi-users"></i></div>
        </div>
        <div class="kpi-value">{{ data.jumlah_responden }}</div>
        <div class="kpi-subtext">
          <router-link to="/cee/survei-hasil" class="link-action">
            Lihat Analisis Survei <i class="pi pi-angle-right"></i>
          </router-link>
        </div>
      </div>
    </div>

   
    <!-- 5x5 Heatmap Matrix & Risk Breakdown Section -->
    <div class="grid-2 heatmap-section">
      <!-- Kolom Kiri: Peta Risiko (Heatmap Matrix 5x5) -->
      <div class="page-card heatmap-card">
        <div class="section-header flex-between">
          <div>
            <h2 class="section-title"><i class="pi pi-th-large text-indigo-500"></i> Matriks Analisis Risiko (Heatmap 5×5)</h2>
            <p class="section-desc">Sebaran risiko berdasarkan Skala Kemungkinan (Y) vs Dampak (X). Klik kotak sel untuk melihat daftar risiko.</p>
          </div>
          <div class="heatmap-filters">
            <button
              class="filter-chip"
              :class="{ active: filterJenis === 'all' }"
              @click="filterJenis = 'all'"
            >
              Semua ({{ data.jumlah_dianalisis }})
            </button>
            <button
              class="filter-chip"
              :class="{ active: filterJenis === 'strategis_pemda' }"
              @click="filterJenis = 'strategis_pemda'"
            >
              Form 3.a
            </button>
            <button
              class="filter-chip"
              :class="{ active: filterJenis === 'strategis_opd' }"
              @click="filterJenis = 'strategis_opd'"
            >
              Form 3.b
            </button>
            <button
              class="filter-chip"
              :class="{ active: filterJenis === 'operasional_opd' }"
              @click="filterJenis = 'operasional_opd'"
            >
              Form 3.c
            </button>
          </div>
        </div>

        <!-- Matriks 5x5 Grid -->
        <div class="matrix-wrapper">
          <div class="matrix-y-axis">
            <div class="axis-label-vertical">KEMUNGKINAN</div>
          </div>

          <div class="matrix-table-container">
            <table class="matrix-table">
              <tbody>
                <tr v-for="k in kemungkinanScale" :key="k.val">
                  <td class="y-scale-header">
                    <div class="k-label-num">{{ k.val }}</div>
                    <div class="k-label-text">{{ k.short }}</div>
                  </td>
                  <td
                    v-for="d in dampakScale"
                    :key="d.val"
                    class="matrix-cell"
                    :class="[
                      getCellClass(k.val, d.val),
                      { 'has-risks': getCellRisks(k.val, d.val).length > 0 }
                    ]"
                    :style="getToleranceBorderStyles(k.val, d.val, policy?.visual?.diterima)"
                    @click="openCellDialog(k.val, d.val)"
                    v-tooltip.top="`Kemungkinan: ${k.val}, Dampak: ${d.val} (Skor: ${getMatrixScore(k.val, d.val)}) - ${getCellRisks(k.val, d.val).length} risiko`"
                  >
                    <div class="cell-inner">
                      <div class="cell-score-tag">
                        <span>{{ getMatrixScore(k.val, d.val) }}</span>
                      </div>
                      <div class="cell-count-wrapper">
                        <span class="cell-count">{{ getCellRisks(k.val, d.val).length }}</span>
                        <span class="cell-risk-label">Risiko</span>
                      </div>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td></td>
                  <td v-for="d in dampakScale" :key="d.val" class="x-scale-header">
                    <div class="d-label-num">{{ d.val }}</div>
                    <div class="d-label-text">{{ d.short }}</div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="axis-label-horizontal">DAMPAK</div>
          </div>
        </div>

        <!-- Heatmap Legend -->
        <div class="heatmap-legend">
          <div class="legend-item">
            <span class="legend-dot" style="background: #ef4444"></span>
            <span class="legend-title">Sangat Tinggi (5)</span>
            <span class="legend-range">(Skor 20 – 25)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #f97316"></span>
            <span class="legend-title">Tinggi (4)</span>
            <span class="legend-range">(Skor 16 – 19)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #eab308"></span>
            <span class="legend-title">Sedang (3)</span>
            <span class="legend-range">(Skor 11 – 15)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #22c55e"></span>
            <span class="legend-title">Rendah (2)</span>
            <span class="legend-range">(Skor 6 – 10)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #15803d"></span>
            <span class="legend-title">Sangat Rendah (1)</span>
            <span class="legend-range">(Skor 1 – 5)</span>
          </div>
          <div v-if="policy?.visual?.diterima" class="legend-item" style="border-left: 2px solid #cbd5e1; padding-left: 8px;">
            <span style="display: inline-block; width: 18px; height: 3.5px; background: #7c3aed; border-radius: 2px;"></span>
            <span class="legend-title">Batas Selera Risiko</span>
          </div>
        </div>
      </div>

      <!-- Kolom Kanan: Distribusi Level & Kategori Risiko -->
      <div class="page-card distribution-card">
        <!-- Distribusi Level Risiko -->
        <div class="dist-block">
          <h3 class="dist-title"><i class="pi pi-chart-pie text-indigo-500"></i> Sebaran Level Risiko</h3>
          <div class="level-bars">
            <div v-for="(count, lvl) in data.risiko_per_level" :key="lvl" class="level-bar-row">
              <div class="level-meta">
                <div class="level-name-wrap">
                  <span class="level-badge-indicator" :style="{ background: levelColor[lvl] }"></span>
                  <span class="level-name">{{ lvl }}</span>
                </div>
                <div class="level-count">
                  <strong>{{ count }}</strong>
                  <span class="level-pct">({{ data.jumlah_dianalisis ? Math.round((count / data.jumlah_dianalisis) * 100) : 0 }}%)</span>
                </div>
              </div>
              <div class="bar-track">
                <div
                  class="bar-prog"
                  :style="{
                    width: (data.jumlah_dianalisis ? (count / data.jumlah_dianalisis) * 100 : 0) + '%',
                    background: levelColor[lvl],
                  }"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="divider-hr"></div>

        <!-- Distribusi Kategori Risiko dari Kamus -->
        <div class="dist-block">
          <h3 class="dist-title"><i class="pi pi-tags text-violet-500"></i> Sebaran Kategori Risiko</h3>
          <div v-if="sortedKategori.length" class="kategori-bars">
            <div v-for="item in sortedKategori.slice(0, 6)" :key="item.nama" class="kategori-row">
              <div class="kategori-meta">
                <span class="kategori-name">{{ item.nama }}</span>
                <span class="kategori-count">{{ item.jumlah }} risiko</span>
              </div>
              <div class="kategori-track">
                <div
                  class="kategori-prog"
                  :style="{ width: `${(item.jumlah / maxKategoriCount) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
          <div v-else class="empty-text">Belum ada kategori risiko tersimpan.</div>
        </div>
      </div>
    </div>

    <!-- Tahapan Manajemen Risiko (Roadmap Pipeline) -->
    <div class="section-container page-card">
      <div class="section-header">
        <h2 class="section-title"><i class="pi pi-sitemap text-blue-500"></i> Pipeline Tahapan Manajemen Risiko 2026</h2>
        <p class="section-desc">Progres tahapan penilaian risiko terintegrasi sesuai standar pedoman SPIP Terintegrasi BPKP.</p>
      </div>

      <div class="pipeline-grid">
        <div
          v-for="stg in data.tahapan_progress"
          :key="stg.no"
          class="pipeline-step-card"
          :class="`status-${stg.status}`"
        >
          <div class="step-num-badge">{{ stg.no }}</div>
          <div class="step-content">
            <div class="step-header">
              <span class="step-form">{{ stg.form }}</span>
              <span class="step-status-chip" :class="`chip-${stg.status}`">
                <i v-if="stg.status === 'selesai'" class="pi pi-check"></i>
                <i v-else-if="stg.status === 'proses'" class="pi pi-spin pi-spinner"></i>
                <i v-else class="pi pi-clock"></i>
                {{ stg.status === 'selesai' ? 'Selesai' : stg.status === 'proses' ? 'Proses' : 'Belum' }}
              </span>
            </div>
            <h4 class="step-title">{{ stg.nama }}</h4>
            <div class="step-desc">{{ stg.keterangan }}</div>
            <div class="step-footer">
              <router-link :to="stg.link" class="step-link">
                Buka Formulir <i class="pi pi-arrow-right"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

     <!-- Rekomendasi Strategis Eksekutif (Smart Engine) -->
    <div class="section-container page-card">
      
      <div class="section-header">
        <div>
          <h2 class="section-title"><i class="pi pi-lightbulb text-amber-500"></i> Rekomendasi Strategis Eksekutif</h2>
          <p class="section-desc">Poin atensi manajerial berbasis profil risiko dan kepatuhan penyusunan rencana tindak.</p>
        </div>
      </div>

      <div class="recommendations-grid">
        <div
          v-for="(rec, idx) in data.rekomendasi"
          :key="idx"
          class="recommendation-card"
          :class="`rec-${rec.severity}`"
        >
          <div class="rec-icon">
            <i v-if="rec.severity === 'kritis'" class="pi pi-exclamation-circle"></i>
            <i v-else-if="rec.severity === 'perhatian'" class="pi pi-exclamation-triangle"></i>
            <i v-else-if="rec.severity === 'sukses'" class="pi pi-check-circle"></i>
            <i v-else class="pi pi-info-circle"></i>
          </div>
          <div class="rec-body">
            <div class="rec-head">
              <span class="rec-badge" :class="`badge-${rec.severity}`">
                {{ rec.severity.toUpperCase() }}
              </span>
              <h3 class="rec-title">{{ rec.judul }}</h3>
            </div>
            <p class="rec-message">{{ rec.pesan }}</p>
            <div class="rec-footer">
              <Button
                :label="rec.action_label"
                icon="pi pi-arrow-up-right"
                size="small"
                outlined
                class="rec-btn"
                @click="navigateTo(rec.action_link)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Register Risiko Prioritas Tertinggi (Top 10) -->
    <div class="section-container page-card">
      <div class="section-header flex-between">
        <div>
          <h2 class="section-title"><i class="pi pi-list-check text-rose-500"></i> Daftar Risiko Prioritas Utama</h2>
          <p class="section-desc">Daftar 10 risiko dengan skor dampak & kemungkinan tertinggi yang memerlukan atensi langsung pimpinan.</p>
        </div>
        <Button
          label="Kelola Seluruh RTP (Form 7)"
          icon="pi pi-external-link"
          size="small"
          outlined
          @click="navigateTo('/rtp')"
        />
      </div>

      <DataTable
        :value="data.top_prioritas"
        stripedRows
        responsiveLayout="scroll"
        class="p-datatable-sm risk-table"
      >
        <template #empty>
          <div class="text-center p-4 muted">
            Tidak ada risiko prioritas tinggi yang memerlukan tindakan segera.
          </div>
        </template>

        <Column field="kode_risiko" header="Kode" style="width: 140px">
          <template #body="{ data: r }">
            <span class="font-mono text-xs font-semibold">{{ r.kode_risiko }}</span>
            <div class="text-xs muted">{{ r.jenis_label }}</div>
          </template>
        </Column>

        <Column field="uraian_risiko" header="Uraian Risiko">
          <template #body="{ data: r }">
            <div class="font-medium text-sm">{{ r.uraian_risiko }}</div>
            <div class="sub-meta-row">
              <span class="meta-tag">{{ r.kategori_risiko }}</span>
              <span v-if="r.cuc" class="meta-tag" :class="r.cuc === 'C' ? 'tag-c' : 'tag-uc'">
                {{ r.cuc === 'C' ? 'Controllable' : 'Uncontrollable' }}
              </span>
              <span v-if="r.bidang_urusan" class="meta-text">{{ r.bidang_urusan }}</span>
            </div>
          </template>
        </Column>

        <Column header="D & K" style="width: 90px; text-align: center">
          <template #body="{ data: r }">
            <span class="score-calc">D:{{ r.skala_dampak }} | K:{{ r.skala_kemungkinan }}</span>
          </template>
        </Column>

        <Column header="Skor & Level" style="width: 130px">
          <template #body="{ data: r }">
            <div
              class="level-pill"
              :style="{ background: levelBg[r.level] || '#eee', color: levelColor[r.level] || '#333' }"
            >
              <span class="pill-score">{{ r.skala_risiko }}</span>
              <span class="pill-lvl">{{ r.level }}</span>
            </div>
          </template>
        </Column>

        <Column header="Status RTP" style="width: 140px">
          <template #body="{ data: r }">
            <Tag
              v-if="r.has_rtp"
              severity="success"
              value="Sudah Ada RTP"
              icon="pi pi-check"
            />
            <Tag
              v-else
              severity="danger"
              value="Belum Ada RTP"
              icon="pi pi-exclamation-triangle"
            />
          </template>
        </Column>

        <Column header="Rencana Mitigasi & PIC" style="width: 260px">
          <template #body="{ data: r }">
            <div v-if="r.has_rtp">
              <div class="text-xs font-medium rtp-text">{{ r.rencana_tindak }}</div>
              <div class="text-xs muted mt-1">
                <i class="pi pi-user text-xs"></i> {{ r.pemilik_penanggung_jawab || r.pemilik_risiko || '-' }}
              </div>
            </div>
            <div v-else class="text-xs text-danger">
              <em>Belum dirumuskan di Form 7</em>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal Drilldown Risiko per Sel Heatmap -->
    <Dialog
      v-model:visible="dialogVisible"
      modal
      :header="`Daftar Risiko — Sel [K:${selectedCell?.k}, D:${selectedCell?.d}] (Skor: ${selectedCell?.score} • ${selectedCell?.level})`"
      :style="{ width: '850px', maxWidth: '95vw' }"
    >
      <div v-if="selectedCell" class="cell-dialog-body">
        <div class="cell-dialog-meta">
          <div class="dialog-meta-item">
            <span class="lbl">Kemungkinan:</span>
            <strong>{{ selectedCell.kLabel }}</strong>
          </div>
          <div class="dialog-meta-item">
            <span class="lbl">Dampak:</span>
            <strong>{{ selectedCell.dLabel }}</strong>
          </div>
          <div class="dialog-meta-item">
            <span class="lbl">Level Risiko:</span>
            <Tag
              :style="{ background: levelBg[selectedCell.level], color: levelColor[selectedCell.level] }"
              :value="selectedCell.level"
            />
          </div>
          <div class="dialog-meta-item">
            <span class="lbl">Jumlah Risiko:</span>
            <strong>{{ selectedCell.risks.length }} item</strong>
          </div>
        </div>

        <DataTable
          :value="selectedCell.risks"
          stripedRows
          responsiveLayout="scroll"
          class="p-datatable-sm"
          paginator
          :rows="5"
        >
          <template #empty>
            <div class="p-3 text-center muted">Tidak ada risiko pada koordinat sel ini.</div>
          </template>
          <Column field="kode_risiko" header="Kode" style="width: 130px">
            <template #body="{ data: r }">
              <span class="font-mono text-xs font-semibold">{{ r.kode_risiko }}</span>
              <div class="text-xs muted">{{ r.jenis_label }}</div>
            </template>
          </Column>
          <Column field="uraian_risiko" header="Uraian Risiko">
            <template #body="{ data: r }">
              <div class="font-medium text-sm">{{ r.uraian_risiko }}</div>
              <div class="text-xs muted mt-1">
                Kategori: <b>{{ r.kategori_risiko }}</b> | Pemilik: <b>{{ r.pemilik_risiko || '-' }}</b>
              </div>
            </template>
          </Column>
          <Column header="RTP" style="width: 120px">
            <template #body="{ data: r }">
              <Tag
                :severity="r.has_rtp ? 'success' : 'danger'"
                :value="r.has_rtp ? 'Ada RTP' : 'Belum Ada'"
              />
            </template>
          </Column>
        </DataTable>
      </div>

      <template #footer>
        <Button label="Tutup" icon="pi pi-times" text @click="dialogVisible = false" />
        <Button
          label="Buka Form Analisis (Form 4)"
          icon="pi pi-external-link"
          @click="navigateTo('/analisis')"
        />
      </template>
    </Dialog>
  </div>

  <AppLoader v-else-if="loading" label="Memuat ringkasan eksekutif profil risiko…" />
</template>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Executive Header */
.exec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-left: 5px solid var(--primary);
  padding: 22px 26px;
  flex-wrap: wrap;
  gap: 16px;
}
.badge-tag {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--primary);
  background: var(--primary-soft);
  padding: 3px 10px;
  border-radius: 999px;
  margin-bottom: 6px;
}
.exec-title {
  margin: 0 0 6px;
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #0f172a;
}
.exec-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}
.dot-sep {
  color: #cbd5e1;
}
.exec-actions {
  display: flex;
  gap: 10px;
}

/* KPI Stat Cards Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 16px;
}
.kpi-card {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.kpi-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}
.accent-indigo::before { background: #6366f1; }
.accent-blue::before { background: #3b82f6; }
.accent-rose::before { background: #ef4444; }
.accent-emerald::before { background: #10b981; }
.accent-amber::before { background: #f59e0b; }
.accent-purple::before { background: #8b5cf6; }

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.kpi-label {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}
.kpi-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #475569;
  font-size: 0.95rem;
}
.accent-indigo .kpi-icon { background: #e0e7ff; color: #4338ca; }
.accent-blue .kpi-icon { background: #dbeafe; color: #1d4ed8; }
.accent-rose .kpi-icon { background: #fee2e2; color: #b91c1c; }
.accent-emerald .kpi-icon { background: #d1fae5; color: #047857; }
.accent-amber .kpi-icon { background: #fef3c7; color: #b45309; }
.accent-purple .kpi-icon { background: #ede9fe; color: #6d28d9; }

.kpi-value {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin-bottom: 6px;
}
.kpi-value-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 6px;
}
.kpi-denom {
  font-size: 1.1rem;
  color: #94a3b8;
  font-weight: 600;
}
.danger-text { color: #ef4444; }
.success-text { color: #10b981; }

.kpi-subtext {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sep { color: #cbd5e1; }
.kpi-progress-bar {
  background: #e2e8f0;
  border-radius: 999px;
  height: 6px;
  overflow: hidden;
  margin-top: 8px;
}
.bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}
.bar-fill.blue { background: #3b82f6; }

.kpi-cuc-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-top: 4px;
}
.cuc-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.cuc-num {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
}
.cuc-tag {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  margin-top: 2px;
}
.tag-c { background: #dbeafe; color: #1e40af; }
.tag-uc { background: #fee2e2; color: #991b1b; }
.cuc-divider {
  width: 1px;
  height: 28px;
  background: #e2e8f0;
}
.link-action {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.link-action:hover { text-decoration: underline; }

/* Rekomendasi Eksekutif */
.section-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.section-header {
  margin-bottom: 4px;
}
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}
.section-title {
  margin: 0 0 4px;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-desc {
  margin: 0;
  font-size: 0.83rem;
  color: var(--text-muted);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
}
.recommendation-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  background: #ffffff;
  box-shadow: var(--shadow-xs);
  transition: transform 0.15s ease;
}
.recommendation-card:hover {
  transform: translateY(-2px);
}
.rec-kritis {
  background: #fef2f2;
  border-color: #fecaca;
}
.rec-perhatian {
  background: #fffbeb;
  border-color: #fde68a;
}
.rec-informasi {
  background: #f8fafc;
  border-color: #e2e8f0;
}
.rec-sukses {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.rec-icon {
  font-size: 1.35rem;
  flex-shrink: 0;
  margin-top: 2px;
}
.rec-kritis .rec-icon { color: #dc2626; }
.rec-perhatian .rec-icon { color: #d97706; }
.rec-informasi .rec-icon { color: #4f46e5; }
.rec-sukses .rec-icon { color: #16a34a; }

.rec-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.rec-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}
.rec-badge {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.05em;
}
.badge-kritis { background: #fee2e2; color: #991b1b; }
.badge-perhatian { background: #fef3c7; color: #92400e; }
.badge-informasi { background: #e0e7ff; color: #3730a3; }
.badge-sukses { background: #dcfce7; color: #166534; }

.rec-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
}
.rec-message {
  margin: 0 0 10px;
  font-size: 0.82rem;
  line-height: 1.45;
  color: #334155;
}
.rec-footer {
  margin-top: auto;
}
.rec-btn {
  padding: 4px 10px !important;
  font-size: 0.78rem !important;
}

/* Heatmap Section */
.heatmap-section {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 20px;
}
.heatmap-filters {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.filter-chip {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
}
.filter-chip:hover {
  background: #e2e8f0;
}
.filter-chip.active {
  background: var(--primary);
  color: #ffffff;
  border-color: var(--primary);
}

.matrix-wrapper {
  display: flex;
  gap: 10px;
  margin: 16px 0 12px;
  align-items: center;
}
.matrix-y-axis {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
}
.axis-label-vertical {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--text-muted);
}
.matrix-table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.matrix-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 6px;
}
.y-scale-header {
  width: 70px;
  text-align: right;
  padding-right: 8px;
  vertical-align: middle;
}
.k-label-num {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
}
.k-label-text {
  font-size: 0.68rem;
  color: var(--text-muted);
  white-space: nowrap;
}
.x-scale-header {
  text-align: center;
  padding-top: 6px;
}
.d-label-num {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
}
.d-label-text {
  font-size: 0.68rem;
  color: var(--text-muted);
}
.axis-label-horizontal {
  text-align: center;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  margin-top: 6px;
}

/* Matrix Cells */
.matrix-cell {
  height: 64px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  border: 1px solid rgba(0, 0, 0, 0.06);
}
.matrix-cell:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  z-index: 2;
}

/* BPKP Colors */
.lvl-sangat-tinggi {
  background: #fee2e2;
  border-color: #fca5a5;
}
.lvl-sangat-tinggi.has-risks {
  background: #ef4444;
  color: #ffffff;
}
.lvl-sangat-tinggi.has-risks .cell-score-tag {
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
}
.lvl-sangat-tinggi.has-risks .cell-count {
  color: #ffffff;
}
.lvl-sangat-tinggi.has-risks .cell-risk-label {
  color: rgba(255, 255, 255, 0.85);
}

.lvl-tinggi {
  background: #ffedd5;
  border-color: #fdba74;
}
.lvl-tinggi.has-risks {
  background: #f97316;
  color: #ffffff;
}
.lvl-tinggi.has-risks .cell-score-tag {
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
}
.lvl-tinggi.has-risks .cell-count {
  color: #ffffff;
}
.lvl-tinggi.has-risks .cell-risk-label {
  color: rgba(255, 255, 255, 0.85);
}

.lvl-sedang {
  background: #fef9c3;
  border-color: #fde047;
}
.lvl-sedang.has-risks {
  background: #eab308;
  color: #ffffff;
}
.lvl-sedang.has-risks .cell-score-tag {
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
}
.lvl-sedang.has-risks .cell-count {
  color: #ffffff;
}
.lvl-sedang.has-risks .cell-risk-label {
  color: rgba(255, 255, 255, 0.85);
}

.lvl-rendah {
  background: #dcfce7;
  border-color: #86efac;
}
.lvl-rendah.has-risks {
  background: #22c55e;
  color: #ffffff;
}
.lvl-rendah.has-risks .cell-score-tag {
  background: rgba(0, 0, 0, 0.2);
  color: #fff;
}
.lvl-rendah.has-risks .cell-count {
  color: #ffffff;
}
.lvl-rendah.has-risks .cell-risk-label {
  color: rgba(255, 255, 255, 0.85);
}

.lvl-sangat-rendah {
  background: #dcfce7;
  border-color: #86efac;
}
.lvl-sangat-rendah.has-risks {
  background: #15803d;
  color: #ffffff;
}
.lvl-sangat-rendah.has-risks .cell-score-tag {
  background: rgba(0, 0, 0, 0.25);
  color: #fff;
}
.lvl-sangat-rendah.has-risks .cell-count {
  color: #ffffff;
}
.lvl-sangat-rendah.has-risks .cell-risk-label {
  color: rgba(255, 255, 255, 0.85);
}

.cell-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 6px 8px;
}
.cell-score-tag {
  align-self: flex-start;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.06);
  color: #475569;
}
.cell-count-wrapper {
  text-align: center;
}
.cell-count {
  font-size: 1.45rem;
  font-weight: 800;
  line-height: 1;
  display: block;
}
.cell-risk-label {
  font-size: 0.65rem;
  font-weight: 600;
  opacity: 0.8;
}

.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}
.legend-title {
  font-weight: 600;
  color: #1e293b;
}
.legend-range {
  color: var(--text-muted);
}

/* Kolom Kanan: Distribusi Level & Kategori */
.distribution-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.dist-title {
  margin: 0 0 12px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 6px;
}
.level-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.level-bar-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.level-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
}
.level-name-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}
.level-badge-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.level-name {
  font-weight: 600;
  color: #334155;
}
.level-pct {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-left: 4px;
}
.bar-track {
  background: #f1f5f9;
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
}
.bar-prog {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.divider-hr {
  height: 1px;
  background: var(--border);
}

.kategori-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kategori-row {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.kategori-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}
.kategori-name {
  font-weight: 500;
  color: #334155;
}
.kategori-count {
  font-weight: 600;
  color: var(--text-muted);
  font-size: 0.75rem;
}
.kategori-track {
  background: #f1f5f9;
  border-radius: 999px;
  height: 6px;
  overflow: hidden;
}
.kategori-prog {
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  height: 100%;
  border-radius: 999px;
}
.empty-text {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Pipeline Tahapan 6 Langkah */
.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}
.pipeline-step-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-sm);
  padding: 14px;
  position: relative;
  display: flex;
  gap: 10px;
  transition: all 0.15s ease;
}
.pipeline-step-card:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  box-shadow: var(--shadow-sm);
}
.status-selesai {
  border-left: 4px solid #10b981;
}
.status-proses {
  border-left: 4px solid #3b82f6;
}
.status-belum {
  border-left: 4px solid #94a3b8;
}

.step-num-badge {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  font-weight: 800;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.status-selesai .step-num-badge { background: #d1fae5; color: #065f46; }
.status-proses .step-num-badge { background: #dbeafe; color: #1e40af; }

.step-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.step-form {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}
.step-status-chip {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.chip-selesai { background: #dcfce7; color: #15803d; }
.chip-proses { background: #dbeafe; color: #1d4ed8; }
.chip-belum { background: #f1f5f9; color: #64748b; }

.step-title {
  margin: 2px 0 4px;
  font-size: 0.86rem;
  font-weight: 700;
  color: #1e293b;
}
.step-desc {
  font-size: 0.74rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.step-footer {
  margin-top: auto;
}
.step-link {
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--primary);
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.step-link:hover { text-decoration: underline; }

/* Top Priority Register Table */
.risk-table {
  margin-top: 6px;
}
.sub-meta-row {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 4px;
  flex-wrap: wrap;
}
.meta-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #475569;
}
.meta-text {
  font-size: 0.72rem;
  color: var(--text-muted);
}
.score-calc {
  font-weight: 700;
  font-size: 0.85rem;
  color: #334155;
}
.level-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
}
.pill-score {
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 5px;
  border-radius: 999px;
  font-size: 0.72rem;
}
.rtp-text {
  color: #1e293b;
  line-height: 1.35;
}

/* Modal Drill-Down */
.cell-dialog-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
  background: #f8fafc;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  margin-bottom: 16px;
  border: 1px solid #e2e8f0;
}
.dialog-meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.8rem;
}
.dialog-meta-item .lbl {
  color: var(--text-muted);
  font-size: 0.72rem;
}

/* Responsiveness */
@media (max-width: 1024px) {
  .heatmap-section {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 768px) {
  .exec-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .exec-actions {
    width: 100%;
    justify-content: flex-start;
  }
  .matrix-cell {
    height: 52px;
  }
  .cell-count {
    font-size: 1.15rem;
  }
}
</style>
