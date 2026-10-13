<script setup>
import CrudTable from '@/components/CrudTable.vue'
const columns = [
  { field: 'no_urut', label: 'No', width: '60px' },
  { field: 'kegiatan_pengendalian', label: 'Kegiatan Pengendalian yang Dibutuhkan', type: 'textarea', width: '240px' },
  { field: 'media_bentuk', label: 'Media/Bentuk Sarana', type: 'textarea', width: '160px' },
  { field: 'penyedia_informasi', label: 'Penyedia Informasi', width: '140px' },
  { field: 'penerima_informasi', label: 'Penerima Informasi', width: '140px' },
  { field: 'rencana_waktu', label: 'Rencana Waktu', width: '120px' },
  { field: 'realisasi_waktu', label: 'Realisasi Waktu', width: '120px' },
  { field: 'keterangan', label: 'Keterangan', type: 'textarea', width: '140px' },
]
</script>
<template>
  <CrudTable endpoint="/monitoring/infokom" :columns="columns" title="Form 8 — Informasi & Komunikasi" />
</template>
