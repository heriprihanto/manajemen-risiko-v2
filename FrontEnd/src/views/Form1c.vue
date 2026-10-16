<script setup>
import { onMounted, ref } from 'vue'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const ctx = useContextStore()
const toast = useToast()
const rows = ref([])

const simpulanOptions = [
  { label: 'Memadai', value: 'Memadai' },
  { label: 'Kurang Memadai', value: 'Kurang Memadai' },
]

function pill(v) {
  return v === 'Memadai' ? 'pill-ok' : v ? 'pill-bad' : ''
}
async function load() {
  const { data } = await api.get('/cee/form1c', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  rows.value = data
}
async function saveSimpulan(row) {
  await api.post('/cee/form1c/simpulan', {
    opd_id: ctx.opdId,
    tahun: ctx.tahun,
    kategori_id: row.kategori_id,
    simpulan: row.simpulan ?? null, // kosong = kembali ke otomatis
  })
  toast.add({ severity: 'success', summary: 'Simpulan tersimpan', life: 1200 })
  await load() // segarkan agar nilai otomatis / status manual sinkron
}

function onFocusPenjelasan(row) {
  row._origPenjelasan = row.penjelasan ?? ''
}

async function onBlurPenjelasan(row) {
  const current = row.penjelasan ?? ''
  if (current === (row._origPenjelasan ?? '')) return
  await savePenjelasan(row)
}

async function savePenjelasan(row) {
  try {
    await api.post('/cee/form1c/simpulan', {
      opd_id: ctx.opdId,
      tahun: ctx.tahun,
      kategori_id: row.kategori_id,
      penjelasan: row.penjelasan ?? '',
    })
    toast.add({ severity: 'success', summary: 'Penjelasan tersimpan', life: 1200 })
    row.penjelasan_manual = true
    row._origPenjelasan = row.penjelasan
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Gagal menyimpan penjelasan', life: 2500 })
  }
}

async function resetPenjelasan(row) {
  try {
    await api.post('/cee/form1c/simpulan', {
      opd_id: ctx.opdId,
      tahun: ctx.tahun,
      kategori_id: row.kategori_id,
      reset_penjelasan: true,
    })
    toast.add({ severity: 'info', summary: 'Penjelasan dikembalikan ke otomatis', life: 1200 })
    await load()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Gagal reset penjelasan', life: 2500 })
  }
}

onMounted(load)
</script>

<template>
  <p class="muted" style="margin-top: 0">
    Simpulan gabungan: hasil survei persepsi (Form 1.a) + hasil reviu dokumen (Form 1.b). Simpulan akhir
    <strong>Kurang Memadai</strong> bila salah satunya Kurang Memadai.
  </p>
  <div class="page-card" style="padding: 0">
    <table class="grid-table">
      <thead>
        <tr>
          <th style="width: 46px">No</th>
          <th style="text-align: left">Sub-unsur</th>
          <th style="width: 150px">Hasil Persepsi</th>
          <th style="width: 150px">Hasil Dokumen</th>
          <th style="width: 150px">Simpulan</th>
          <th style="text-align: left; min-width: 280px">Penjelasan</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.kategori_id">
          <td style="text-align: center">{{ r.no }}</td>
          <td>{{ r.sub_unsur }}</td>
          <td style="text-align: center">
            <span v-if="r.hasil_persepsi" class="pill" :class="pill(r.hasil_persepsi)">{{ r.hasil_persepsi }}</span>
          </td>
          <td style="text-align: center">
            <span v-if="r.hasil_dokumen" class="pill" :class="pill(r.hasil_dokumen)">{{ r.hasil_dokumen }}</span>
            <span v-else class="muted">—</span>
          </td>
          <td style="text-align: center">
            <Select
              v-model="r.simpulan"
              :options="simpulanOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="—"
              showClear
              style="width: 150px"
              @change="saveSimpulan(r)"
            />
            <div v-if="r.simpulan_manual" class="manual-tag">disunting manual</div>
            <div v-else-if="r.simpulan_auto" class="muted auto-tag">otomatis</div>
          </td>
          <td>
            <Textarea
              v-model="r.penjelasan"
              autoResize
              rows="2"
              class="penjelasan-input"
              placeholder="Penjelasan ..."
              @focus="onFocusPenjelasan(r)"
              @blur="onBlurPenjelasan(r)"
            />
            
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.grid-table { border-collapse: collapse; width: 100%; font-size: 0.86rem; }
.grid-table th, .grid-table td { border: 1px solid #e2e8f0; padding: 8px 10px; }
.grid-table thead th { background: #f8fafc; font-weight: 600; color: #1e293b; border: 1px solid #e2e8f0; }
.grid-table tbody tr:nth-child(even) { background: #f8fafc; }
.grid-table tbody tr:hover { background: #f1f5f9; }
.kelemahan-ol { margin: 0; padding-left: 1.1em; }
.kelemahan-ol li { margin: 0 0 2px; }
.pre-line { white-space: pre-line; }
.manual-tag { font-size: 0.68rem; color: #b45309; margin-top: 3px; }
.auto-tag { font-size: 0.68rem; margin-top: 3px; }
.penjelasan-input {
  width: 100%;
  font-size: 0.85rem;
  line-height: 1.4;
  box-sizing: border-box;
}
.btn-reset {
  background: none;
  border: none;
  padding: 0;
  margin-left: 4px;
  color: #2563eb;
  cursor: pointer;
  font-size: 0.68rem;
  text-decoration: underline;
}
.btn-reset:hover {
  color: #1d4ed8;
}
</style>
