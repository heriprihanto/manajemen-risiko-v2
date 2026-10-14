<script setup>
import { watch, ref } from 'vue'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import {
  getMatrixScore,
  getMatrixLevel,
  getToleranceBorderStyles,
} from '@/utils/matriks'

const ctx = useContextStore()
const data = ref(null)
const error = ref('')
const owner = ref(null)
let serial = 0

const dampakHeaders = [
  { val: 1, label: 'Tidak Signifikan' },
  { val: 2, label: 'Minor' },
  { val: 3, label: 'Moderat' },
  { val: 4, label: 'Signifikan' },
  { val: 5, label: 'Sangat Signifikan' },
]

const kemungkinanHeaders = [
  { val: 5, label: 'Hampir pasti terjadi' },
  { val: 4, label: 'Sering terjadi' },
  { val: 3, label: 'Kadang terjadi' },
  { val: 2, label: 'Jarang terjadi' },
  { val: 1, label: 'Hampir tidak terjadi' },
]

// Warna sel heatmap sesuai standar referensi
function cellBgColor(k, d) {
  const s = getMatrixScore(k, d)
  if (s >= 20) return '#ef4444' // Merah: Sangat Tinggi (5)
  if (s >= 16) return '#f97316' // Oranye: Tinggi (4)
  if (s >= 11) return '#facc15' // Kuning: Sedang (3)
  if (s >= 6) return '#84cc16'  // Hijau Muda: Rendah (2)
  return '#10b981'              // Hijau Tua / Emerald: Sangat Rendah (1)
}

function cellTextColor(k, d) {
  const s = getMatrixScore(k, d)
  if (s >= 20) return '#ffffff'
  if (s >= 16) return '#ffffff'
  if (s >= 11) return '#1e293b'
  if (s >= 6) return '#1e293b'
  return '#ffffff'
}

function cellItems(k, d) {
  return data.value?.cells?.[`${k}-${d}`] || []
}

async function load() {
  if (!ctx.ready) return
  const id = ++serial
  error.value = ''; data.value = null
  try {
  const { data: d } = await api.get('/risiko/matriks', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun, ...(owner.value !== null ? { pemilik: owner.value } : {}) },
  })
  if (id === serial) data.value = d
  } catch (e) { if (id === serial) error.value = 'Gagal memuat matriks risiko.' }
}
watch([() => ctx.opdId, () => ctx.tahun], () => { owner.value = null; load() }, { immediate: true })
watch(owner, load)
</script>

<template>
  <p v-if="error" role="alert">{{ error }}</p>
  <div v-if="data" class="page-card">
    <div class="header-banner">
      <h2 class="title"><i class="pi pi-th-large"></i> Matriks Analisis Risiko 5 × 5</h2>
      <p class="muted" style="margin: 4px 0 0 0">
        Sebaran risiko pada matriks analisis 5×5 (Kemungkinan vs Dampak). Nilai angka pada setiap sel menunjukkan
        <strong>Besaran Risiko (Skala 1–25)</strong>. Garis ungu mengikuti ambang Selera Risiko yang ditetapkan Pemilik Risiko.
        Warna menunjukkan level risiko. Skor ≤ ambang termasuk area penerimaan.
      </p>
      <label>Pemilik Risiko <select v-model="owner"><option :value="null">Semua Pemilik Risiko</option><option v-for="n in data.pemilik" :key="n" :value="n">{{ n || 'Belum diisi / tingkat entitas' }}</option></select></label>
      <p v-if="data.selera?.beragam">Ambang berbeda antar pemilik. Pilih Pemilik Risiko untuk melihat batas penerimaannya.</p>
      <p v-else-if="data.selera?.ditetapkan">Ambang Selera Risiko: <strong>{{ data.selera.ambang }}</strong>. Skor 1–{{ data.selera.ambang }} diterima.</p>
      <p v-else>Selera Risiko belum ditetapkan. <router-link :to="{ name: 'selera-risiko' }">Buka pengaturan</router-link>.</p>
    </div>

    <div class="matrix-scroll">
      <table class="matrix">
        <thead>
          <tr>
            <th class="corner" colspan="3" rowspan="3">
              <div class="corner-title">Matriks Analisis Risiko 5 × 5</div>
            </th>
            <th :colspan="5" class="axis-dampak">Tingkat Dampak</th>
          </tr>
          <tr>
            <th v-for="d in dampakHeaders" :key="'num-' + d.val" class="hd-num">
              {{ d.val }}
            </th>
          </tr>
          <tr>
            <th v-for="d in dampakHeaders" :key="'lbl-' + d.val" class="hd-lbl">
              {{ d.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(k, idx) in kemungkinanHeaders" :key="k.val">
            <th v-if="idx === 0" class="axis-kemungkinan" rowspan="5">
              <span>Tingkat Kemungkinan</span>
            </th>
            <th class="k-num">{{ k.val }}</th>
            <th class="k-lbl">{{ k.label }}</th>
            <td
              v-for="d in [1, 2, 3, 4, 5]"
              :key="d"
              class="cell"
              :style="{
                background: cellBgColor(k.val, d),
                color: cellTextColor(k.val, d),
                ...getToleranceBorderStyles(k.val, d, data.selera?.diterima)
              }"
            >
              <div class="cell-content">
                <div class="score" :style="{ color: cellTextColor(k.val, d) }">
                  {{ getMatrixScore(k.val, d) }}
                </div>
                <div v-if="cellItems(k.val, d).length" class="items-list">
                  <div
                    v-for="(it, i) in cellItems(k.val, d)"
                    :key="i"
                    class="chip"
                    :title="it.uraian"
                  >
                    {{ it.kode || it.uraian }}
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="legend-card">
      <div class="legend-title">Keterangan Level Risiko:</div>
      <div class="legend-items">
        <span class="legend-badge"><i style="background: #ef4444" /><strong>Sangat Tinggi (5)</strong> : Skala 20 – 25</span>
        <span class="legend-badge"><i style="background: #f97316" /><strong>Tinggi (4)</strong> : Skala 16 – 19</span>
        <span class="legend-badge"><i style="background: #facc15" /><strong>Sedang (3)</strong> : Skala 11 – 15</span>
        <span class="legend-badge"><i style="background: #84cc16" /><strong>Rendah (2)</strong> : Skala 6 – 10</span>
        <span class="legend-badge"><i style="background: #10b981" /><strong>Sangat Rendah (1)</strong> : Skala 1 – 5</span>
        <span v-if="data.selera?.diterima" class="legend-badge line-badge"><span class="purple-sample-line"></span><strong>Batas Selera Risiko</strong></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-banner {
  margin-bottom: 16px;
}
.title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}
.matrix-scroll {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.matrix {
  border-collapse: collapse;
  width: 100%;
  min-width: 780px;
  background: #ffffff;
}
.matrix th, .matrix td {
  border: 1px solid #94a3b8;
  padding: 8px;
  text-align: center;
}
.corner {
  background: #e2e8f0;
  vertical-align: middle;
  width: 220px;
}
.corner-title {
  font-weight: 700;
  font-size: 1.05rem;
  color: #1e293b;
}
.axis-dampak {
  background: #e2e8f0;
  font-weight: 700;
  font-size: 1.05rem;
  color: #0f172a;
  padding: 10px;
}
.hd-num {
  background: #f1f5f9;
  font-weight: 600;
  font-size: 1rem;
  width: 15%;
}
.hd-lbl {
  background: #f8fafc;
  font-size: 0.85rem;
  font-weight: 500;
  height: 48px;
  vertical-align: middle;
  color: #334155;
}
.axis-kemungkinan {
  background: #e2e8f0;
  width: 44px;
  vertical-align: middle;
  padding: 8px 4px;
}
.axis-kemungkinan span {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  white-space: nowrap;
  font-weight: 700;
  font-size: 1rem;
  color: #0f172a;
  letter-spacing: 0.5px;
}
.k-num {
  background: #f1f5f9;
  font-weight: 600;
  font-size: 1rem;
  width: 38px;
  color: #1e293b;
}
.k-lbl {
  background: #f8fafc;
  font-size: 0.85rem;
  font-weight: 500;
  text-align: left !important;
  padding-left: 12px !important;
  width: 140px;
  color: #334155;
}
.cell {
  height: 84px;
  vertical-align: middle;
  position: relative;
  transition: all 0.15s ease;
}
.cell:hover {
  filter: brightness(1.05);
}
.cell-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.score {
  font-weight: 800;
  font-size: 1.35rem;
  line-height: 1;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.items-list {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  justify-content: center;
  max-height: 45px;
  overflow-y: auto;
}
.chip {
  background: rgba(255, 255, 255, 0.9);
  color: #0f172a;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 5px;
  white-space: nowrap;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
.legend-card {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.legend-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
  margin-bottom: 8px;
}
.legend-items {
  display: flex;
  gap: 16px;
  font-size: 0.82rem;
  flex-wrap: wrap;
  align-items: center;
}
.legend-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #334155;
}
.legend-badge i {
  display: inline-block;
  width: 15px;
  height: 15px;
  border-radius: 3px;
  border: 1px solid rgba(0,0,0,0.15);
}
.line-badge {
  padding-left: 8px;
  border-left: 2px solid #cbd5e1;
}
.purple-sample-line {
  display: inline-block;
  width: 22px;
  height: 4px;
  background: #7c3aed;
  border-radius: 2px;
}
</style>
