<script setup>
import CrudTable from '@/components/CrudTable.vue'
const columns = [
  { field: 'no_urut', label: 'No. Urut', width: '70px' },
  {
    field: 'aspek_cee',
    label: 'Aspek/Sub-unsur CEE',
    type: 'select',
    optionsEndpoint: '/cee/form1c/aspek',
    editable: true,
    placeholder: 'Pilih sub-unsur (Form 1.c)',
    width: '200px',
  },
  {
    field: 'kondisi_kerentanan',
    label: 'Kondisi Kurang Memadai',
    type: 'select',
    optionsEndpoint: '/cee/form1c/permasalahan',
    dependsOn: 'aspek_cee', // cascading: ikuti sub-unsur terpilih
    editable: true,
    placeholder: 'Pilih uraian permasalahan (Form 1.c)',
    width: '260px',
  },
  { field: 'rencana_tindak', label: 'Rencana Tindak Pengendalian', type: 'textarea', width: '220px' },
  { field: 'pemilik_penanggung_jawab', label: 'Penanggung Jawab', type: 'textarea', width: '150px' },
  { field: 'target_waktu', label: 'Target Waktu', width: '120px' },
  { field: 'realisasi_waktu', label: 'Realisasi', width: '120px' },
]
</script>
<template>
  <CrudTable endpoint="/cee/rtp-cee" :columns="columns" title="Form 6 — RTP atas CEE" />
</template>
