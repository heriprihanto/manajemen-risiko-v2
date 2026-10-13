<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const ctx = useContextStore()
const groups = ref([])
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
  const { data } = await api.get('/risiko/form5', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  groups.value = data
}
onMounted(load)
</script>

<template>
  <p class="muted" style="margin-top: 0">
    Daftar risiko prioritas (skala risiko &ge; 16 atau prioritas khusus), diurutkan dari skala tertinggi. Tetapkan prioritas pada Form 4.
  </p>
  <div v-for="g in groups" :key="g.jenis" class="page-card" style="margin-bottom: 16px; padding: 0">
    <div style="padding: 10px 14px; font-weight: 600; background: #fff7ed; border-bottom: 1px solid #e2e8f0">
      {{ g.label }} — {{ g.items.length }} prioritas
    </div>
    <table class="grid-table">
      <thead>
        <tr>
          <th style="width: 40px">No</th>
          <th style="text-align: left; min-width: 240px">Risiko Prioritas</th>
          <th style="width: 110px">Kode</th>
          <th style="width: 70px">Skala</th>
          <th style="width: 120px">Level</th>
          <th style="text-align: left; min-width: 160px">Pemilik</th>
          <th style="text-align: left; min-width: 200px">Penyebab</th>
          <th style="text-align: left; min-width: 200px">Dampak</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(it, i) in g.items" :key="it.id">
          <td style="text-align: center">{{ i + 1 }}</td>
          <td>{{ it.uraian_risiko }}</td>
          <td style="text-align: center">{{ it.kode_risiko }}</td>
          <td style="text-align: center; font-weight: 700">{{ it.analisis.skala_risiko }}</td>
          <td style="text-align: center">
            <span class="pill" :style="{ background: levelColor[it.analisis.level] + '22', color: levelColor[it.analisis.level] }">
              {{ it.analisis.level }}
            </span>
          </td>
          <td>{{ it.pemilik_risiko }}</td>
          <td>{{ it.sebab_uraian }}</td>
          <td>{{ it.dampak_uraian }}</td>
        </tr>
        <tr v-if="!g.items.length"><td colspan="8" class="muted" style="padding: 12px">Tidak ada risiko prioritas.</td></tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.grid-table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
.grid-table th, .grid-table td { border: 1px solid #e2e8f0; padding: 6px 10px; }
.grid-table thead th { background: #f8fafc; font-weight: 600; }
</style>
