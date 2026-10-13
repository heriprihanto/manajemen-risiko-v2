<script setup>
import CrudTable from '@/components/CrudTable.vue'
const jenisOptions = [
  { label: 'Risiko Strategis Pemda', value: 'strategis_pemda' },
  { label: 'Risiko Strategis OPD', value: 'strategis_opd' },
  { label: 'Risiko Operasional OPD', value: 'operasional_opd' },
]
const columns = [
  { field: 'no_urut', label: 'No', width: '60px' },
  { field: 'jenis_risiko', label: 'Jenis Risiko', type: 'select', options: jenisOptions, width: '160px' },
  { field: 'kegiatan_pengendalian', label: 'Kegiatan Pengendalian', type: 'textarea', width: '240px' },
  { field: 'metode_pemantauan', label: 'Bentuk/Metode Pemantauan', type: 'textarea', width: '180px' },
  { field: 'penanggung_jawab', label: 'Penanggung Jawab', width: '150px' },
  { field: 'rencana_waktu', label: 'Rencana Waktu', width: '120px' },
  { field: 'realisasi_waktu', label: 'Realisasi Waktu', width: '120px' },
  { field: 'keterangan', label: 'Keterangan', type: 'textarea', width: '140px' },
]
</script>
<template>
  <CrudTable endpoint="/monitoring/pi" :columns="columns" title="Form 9 — Rencana Pemantauan PI" />
</template>
