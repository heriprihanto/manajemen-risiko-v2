<script setup>
import { RouterLink } from 'vue-router'
import Button from 'primevue/button'
import CrudTable from '@/components/CrudTable.vue'
const columns = [
  {
    field: 'tujuan_strategis',
    label: 'Tujuan Strategis',
    type: 'select',
    optionsEndpoint: '/master/renstra/tujuan',
    editable: true,
    width: '200px',
  },
  {
    field: 'sasaran_strategis',
    label: 'Sasaran Strategis',
    type: 'select',
    optionsEndpoint: '/master/renstra/sasaran',
    dependsOn: 'tujuan_strategis',
    dependsMatch: 'tujuan_strategis',
    editable: true,
    width: '200px',
  },
  {
    field: 'iku_renstra',
    label: 'IKU Renstra',
    type: 'select',
    optionsEndpoint: '/master/renstra/iku',
    editable: true,
    width: '160px',
  },
  {
    field: 'program',
    label: 'Program',
    type: 'select',
    optionsEndpoint: '/master/renstra/program',
    editable: true,
    width: '180px',
  },
  {
    field: 'periode_dinilai',
    label: 'Periode Dinilai',
    type: 'select',
    optionsEndpoint: '/master/renstra/tahap',
    editable: true,
    width: '120px',
  },
  { field: 'sumber_data', label: 'Sumber Data', type: 'textarea', width: '140px' },
]
</script>
<template>
  <div class="toolbar no-print" style="justify-content: flex-end">
    <RouterLink :to="{ name: 'laporan', query: { form: 'f2b', print: 1 } }" custom v-slot="{ navigate }">
      <Button label="Cetak Form 2.b" icon="pi pi-print" size="small" outlined @click="navigate" />
    </RouterLink>
  </div>
  <CrudTable endpoint="/konteks/strategis-opd" :columns="columns" title="Form 2.b — Konteks Strategis OPD" :numbered="false" />
</template>
