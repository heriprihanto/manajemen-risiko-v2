<script setup>
import { onMounted, ref } from 'vue'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const ctx = useContextStore()
const toast = useToast()
const groups = ref([])

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

async function load() {
  const { data } = await api.get('/risiko/form4', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  groups.value = data
}
async function saveAnalisis(item, { recalcPrioritas = false } = {}) {
  const a = item.analisis
  const payload = {
    risiko_id: item.id,
    skala_dampak: a.skala_dampak,
    skala_kemungkinan: a.skala_kemungkinan,
  }
  // Saat dampak/kemungkinan diubah, biarkan backend menghitung ulang is_prioritas default.
  if (!recalcPrioritas) payload.is_prioritas = a.is_prioritas
  const { data } = await api.post('/risiko/analisis', payload)
  Object.assign(item.analisis, data)
  toast.add({ severity: 'success', summary: 'Analisis tersimpan', life: 1200 })
}
onMounted(load)
</script>

<template>
  <p class="muted" style="margin-top: 0">
    Skala Risiko ditentukan berdasarkan Matriks Analisis Risiko 5×5 (Kemungkinan vs Dampak). Risiko dengan Skala &gt; 11 otomatis menjadi
    <strong>prioritas</strong> (dapat disesuaikan manual).
  </p>
  <div v-for="g in groups" :key="g.jenis" class="page-card" style="margin-bottom: 16px; padding: 0">
    <div style="padding: 10px 14px; font-weight: 600; background: #eff6ff; border-bottom: 1px solid #e2e8f0">
      {{ g.label }} ({{ g.items.length }})
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
          <td>{{ it.uraian_risiko }}</td>
          <td style="text-align: center">{{ it.kode_risiko }}</td>
          <td style="text-align: center">
            <Select v-model="it.analisis.skala_dampak" :options="dampakOptions" optionLabel="label" optionValue="value"
              placeholder="—" style="width: 100%; min-width: 160px" @change="saveAnalisis(it, { recalcPrioritas: true })" />
          </td>
          <td style="text-align: center">
            <Select v-model="it.analisis.skala_kemungkinan" :options="kemungkinanOptions" optionLabel="label" optionValue="value"
              placeholder="—" style="width: 100%; min-width: 190px" @change="saveAnalisis(it, { recalcPrioritas: true })" />
          </td>
          <td style="text-align: center; font-weight: 700">{{ it.analisis.skala_risiko ?? '–' }}</td>
          <td style="text-align: center">
            <span v-if="it.analisis.level" class="pill" :style="{ background: (levelColor[it.analisis.level] || '#64748b') + '22', color: levelColor[it.analisis.level] || '#64748b' }">
              {{ it.analisis.level }}
            </span>
          </td>
          <td style="text-align: center">
            <Checkbox v-model="it.analisis.is_prioritas" binary @change="saveAnalisis(it)" />
          </td>
        </tr>
        <tr v-if="!g.items.length"><td colspan="8" class="muted" style="padding: 12px">Belum ada risiko.</td></tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.grid-table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
.grid-table th, .grid-table td { border: 1px solid #e2e8f0; padding: 6px 10px; }
.grid-table thead th { background: #f8fafc; font-weight: 600; }
</style>
