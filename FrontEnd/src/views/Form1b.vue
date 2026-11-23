<script setup>
import { onMounted, ref, watch } from 'vue'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const toast = useToast()
const rows = ref([])
const loading = ref(false)
const draft = ref({}) // item_id -> teks uraian baru

const nilaiOptions = [
  { label: 'Memadai', value: 1 },
  { label: 'Kurang Memadai', value: 0 },
]

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/cee/form1b', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    rows.value = data
  } catch (e) {
    console.error('Gagal memuat Form 1.b:', e)
  } finally {
    loading.value = false
  }
}

async function saveNilai(row) {
  await api.post('/cee/form1b', {
    opd_id: ctx.opdId,
    tahun: ctx.tahun,
    item_id: row.item_id,
    nilai: row.nilai,
    sumber_data: row.sumber_data ?? null,
  })
  toast.add({ severity: 'success', summary: 'Tersimpan', life: 1200 })
}

async function addKelemahan(row) {
  const uraian = (draft.value[row.item_id] || '').trim()
  if (!uraian) return
  await api.post('/cee/form1b/kelemahan', {
    opd_id: ctx.opdId,
    tahun: ctx.tahun,
    item_id: row.item_id,
    uraian,
    urutan: row.kelemahan.length + 1,
  })
  draft.value[row.item_id] = ''
  await load()
}

async function updateKelemahan(k) {
  const uraian = (k.uraian || '').trim()
  if (!uraian) return deleteKelemahan(k) // dikosongkan = hapus
  await api.put(`/cee/form1b/kelemahan/${k.id}`, { uraian })
  toast.add({ severity: 'success', summary: 'Tersimpan', life: 1000 })
}

async function deleteKelemahan(k) {
  await api.delete(`/cee/form1b/kelemahan/${k.id}`)
  await load()
}

watch([() => ctx.opdId, () => ctx.tahun], load)
onMounted(load)
</script>

<template>
  <div class="form1b-page">
    <!-- Header Section (Style Realisasi RTP) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-file-edit"></i>
        </div>
        <div>
          <h1 class="page-title">Reviu Dokumen CEE</h1>
          <p class="page-desc">
            Penilaian kecukupan bukti dukung dokumen dan pencatatan uraian kelemahan Lingkungan Pengendalian (Form 1.b)
          </p>
        </div>
      </div>
      <div class="header-actions">
        <div class="ctx-chip" title="Konteks Penilaian Aktif">
          <i class="pi pi-building"></i>
          <span>{{ ctx.opd?.nama_pd || 'Semua OPD' }}</span>
          <span class="chip-dot">•</span>
          <span>Tahun {{ ctx.tahun }}</span>
        </div>
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

    <AppLoader v-if="loading && !rows.length" label="Memuat data reviu dokumen…" />

    <div v-else class="page-card" style="padding: 0">
    <table class="grid-table">
      <thead>
        <tr>
          <th style="width: 50px">No</th>
          <th style="text-align: left">Sub-unsur / Aspek</th>
          <th style="width: 200px">Hasil Reviu Dokumen</th>
          <th style="text-align: left; min-width: 200px">Sumber Data</th>
          <th style="text-align: left; min-width: 320px">Uraian Kelemahan</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.item_id">
          <td style="text-align: center">{{ r.nomor }}</td>
          <td>{{ r.aspek }}</td>
          <td style="text-align: center">
            <Select
              v-model="r.nilai"
              :options="nilaiOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="—"
              showClear
              style="width: 180px"
              @change="saveNilai(r)"
            />
          </td>
          <td>
            <InputText
              v-model="r.sumber_data"
              style="width: 100%"
              placeholder="Dokumen/data yang direviu"
              @blur="saveNilai(r)"
            />
          </td>
          <td>
            <div class="kelemahan-list">
              <div v-for="(k, i) in r.kelemahan" :key="k.id" class="kelemahan-row">
                <span class="idx">{{ i + 1 }}.</span>
                <InputText
                  v-model="k.uraian"
                  style="flex: 1"
                  @blur="updateKelemahan(k)"
                  @keyup.enter="updateKelemahan(k)"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  rounded
                  v-tooltip.left="'Hapus uraian'"
                  @click="deleteKelemahan(k)"
                />
              </div>
              <div class="kelemahan-row">
                <span class="idx muted">+</span>
                <InputText
                  v-model="draft[r.item_id]"
                  style="flex: 1"
                  placeholder="Tambah uraian kelemahan…"
                  @keyup.enter="addKelemahan(r)"
                />
                <Button
                  icon="pi pi-plus"
                  severity="secondary"
                  text
                  rounded
                  v-tooltip.left="'Tambah'"
                  @click="addKelemahan(r)"
                />
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    </div>
  </div>
</template>

<style scoped>
.form1b-page {
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
  gap: 0.75rem;
  align-items: center;
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

.grid-table { border-collapse: collapse; width: 100%; font-size: 0.86rem; }
.grid-table th, .grid-table td { border: 1px solid #e2e8f0; padding: 8px 10px; vertical-align: top; }
.grid-table thead th { background: #f8fafc; font-weight: 600; color: #1e293b; border: 1px solid #e2e8f0; }
.grid-table tbody tr:nth-child(even) { background: #f8fafc; }
.grid-table tbody tr:hover { background: #f1f5f9; }
.kelemahan-list { display: flex; flex-direction: column; gap: 6px; }
.kelemahan-row { display: flex; align-items: center; gap: 6px; }
.kelemahan-row .idx { width: 18px; text-align: right; color: #475569; font-size: 0.8rem; }
.kelemahan-row .muted { color: #94a3b8; }
</style>
