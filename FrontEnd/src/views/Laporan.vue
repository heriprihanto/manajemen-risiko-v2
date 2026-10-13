<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import MultiSelect from 'primevue/multiselect'
import Button from 'primevue/button'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'
import Form1a from '@/components/laporan/Form1a.vue'
import Form1b from '@/components/laporan/Form1b.vue'
import Form1c from '@/components/laporan/Form1c.vue'
import Form6 from '@/components/laporan/Form6.vue'
import Form2a from '@/components/laporan/Form2a.vue'
import Form2b from '@/components/laporan/Form2b.vue'
import Form2c from '@/components/laporan/Form2c.vue'
import Form3 from '@/components/laporan/Form3.vue'
import Form4 from '@/components/laporan/Form4.vue'
import Form5 from '@/components/laporan/Form5.vue'
import Form7 from '@/components/laporan/Form7.vue'
import Form8 from '@/components/laporan/Form8.vue'
import Form9 from '@/components/laporan/Form9.vue'
import Form10 from '@/components/laporan/Form10.vue'

const ctx = useContextStore()
const route = useRoute()
const loading = ref(true)
const d = ref({})

const sections = [
  { key: 'f1a', form: 'Form 1.a', label: 'Rekap Kuesioner CEE (Persepsi)' },
  { key: 'f1b', form: 'Form 1.b', label: 'Reviu Dokumen CEE' },
  { key: 'f1c', form: 'Form 1.c', label: 'Simpulan CEE' },
  { key: 'f6', form: 'Form 6', label: 'RTP atas CEE' },
  { key: 'f2a', form: 'Form 2.a', label: 'Konteks Strategis Pemda' },
  { key: 'f2b', form: 'Form 2.b', label: 'Konteks Strategis OPD' },
  { key: 'f2c', form: 'Form 2.c', label: 'Konteks Operasional OPD' },
  { key: 'f3a', form: 'Form 3.a', label: 'Identifikasi Risiko Strategis Pemda' },
  { key: 'f3b', form: 'Form 3.b', label: 'Identifikasi Risiko Strategis OPD' },
  { key: 'f3c', form: 'Form 3.c', label: 'Identifikasi Risiko Operasional OPD' },
  { key: 'f4', form: 'Form 4', label: 'Analisis Risiko' },
  { key: 'f5', form: 'Form 5', label: 'Daftar Risiko Prioritas' },
  { key: 'f7', form: 'Form 7', label: 'RTP atas Risiko' },
  { key: 'f8', form: 'Form 8', label: 'Informasi & Komunikasi' },
  { key: 'f9', form: 'Form 9', label: 'Rencana Pemantauan PI' },
  { key: 'f10', form: 'Form 10', label: 'Monitoring Risk Event & RTP' },
]
// Bila dibuka dari tombol "Cetak" sebuah modul (?form=<key>), batasi laporan
// ke satu bagian saja; jika tidak, tampilkan semua bagian.
const initialForm = String(route.query.form || '')
const selected = ref(
  sections.some((s) => s.key === initialForm) ? [initialForm] : sections.map((s) => s.key),
)
const isSel = (k) => selected.value.includes(k)
const opdName = computed(() => ctx.opd?.nama_pd || '-')

async function load() {
  loading.value = true
  const p = { opd_id: ctx.opdId, tahun: ctx.tahun }
  const g = (url, params = p) => api.get(url, { params }).then((r) => r.data).catch(() => null)
  const [f1a, f1b, f1c, f6, f2a, f2b, f2c, f4, matriks, f5, f7, f8, f9, f10,
         opdctx, rtTujuan, rtSasaran, rtIku, rtProgram] = await Promise.all([
    g('/cee/form1a'), g('/cee/form1b'), g('/cee/form1c'), g('/cee/rtp-cee'),
    g('/konteks/pemda', { tahun: ctx.tahun }), g('/konteks/strategis-opd'), g('/konteks/operasional-opd'),
    g('/risiko/form4'), g('/risiko/matriks'), g('/risiko/form5'), g('/risiko/rtp'),
    g('/monitoring/infokom'), g('/monitoring/pi'), g('/monitoring/risk-event'),
    g(`/master/opd/${ctx.opdId}/print-context`),
    // Blok hijau Form 2.b = seluruh data renstra OPD (bukan hanya yang dientri).
    g('/master/renstra/tujuan'), g('/master/renstra/sasaran'),
    g('/master/renstra/iku'), g('/master/renstra/program'),
  ])
  // Hierarki renja Form 2.c (program/kegiatan/subkegiatan + indikator) untuk cetak.
  const renjaC = await g('/master/renja/subkegiatan')
  d.value = { f1a, f1b, f1c, f6, f2a, f2b, f2c, f4, matriks, f5, f7, f8, f9, f10,
    opdctx, rtTujuan, rtSasaran, rtIku, rtProgram, renjaC }
  loading.value = false
}

function cetak() {
  window.print()
}

// Ekspor Excel: satu sheet per form yang sedang dipilih. Diunduh lewat api
// (bukan link biasa) agar header Authorization ikut terkirim.
const exporting = ref(false)
async function exportExcel() {
  exporting.value = true
  try {
    const { data } = await api.get('/laporan/excel', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun, forms: selected.value.join(',') },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `Laporan Manajemen Risiko ${opdName.value} ${ctx.tahun}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    exporting.value = false
  }
}

// Ekspor Word (.docx): dokumen RTP lengkap via docxtpl & lampiran form terpilih.
const exportingWord = ref(false)
async function exportWord() {
  exportingWord.value = true
  try {
    const { data } = await api.get('/laporan/rtp-docx', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun, forms: selected.value.join(','), include_main: true },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `Dokumen_RTP_${opdName.value.replace(/[^a-zA-Z0-9_-]/g, '_')}_${ctx.tahun}.docx`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    exportingWord.value = false
  }
}
onMounted(async () => {
  await load()
  // Auto-cetak saat dibuka via tombol Cetak modul (?print=1).
  if (route.query.print) {
    await nextTick()
    setTimeout(() => window.print(), 300)
  }
})
</script>

<template>
  <div class="no-print toolbar">
    <MultiSelect
      v-model="selected"
      :options="sections"
      optionLabel="label"
      optionValue="key"
      display="chip"
      placeholder="Pilih form"
      style="max-width: 640px"
    >
      <template #option="{ option }">{{ option.form }} — {{ option.label }}</template>
    </MultiSelect>
    <div class="spacer" />
    <Button
      label="Export Excel"
      icon="pi pi-file-excel"
      severity="secondary"
      outlined
      :loading="exporting"
      :disabled="loading || !selected.length"
      v-tooltip.bottom="'Unduh form terpilih sebagai file Excel'"
      @click="exportExcel"
    />
    <Button
      label="Dokumen RTP (Word)"
      icon="pi pi-file-word"
      severity="info"
      outlined
      :loading="exportingWord"
      :disabled="loading || !selected.length"
      v-tooltip.bottom="'Generate Dokumen RTP lengkap (Word .docx)'"
      @click="exportWord"
    />
    <Button label="Cetak / Print Preview" icon="pi pi-print" @click="cetak" :disabled="loading" />
  </div>

  <AppLoader v-if="loading" label="Memuat data laporan…" />

  <div v-else class="report-sheet">
    <Form1a v-if="isSel('f1a') && d.f1a" :data="d.f1a" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form1b v-if="isSel('f1b') && d.f1b" :data="d.f1b" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form1c v-if="isSel('f1c') && d.f1c" :data="d.f1c" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form6 v-if="isSel('f6')" :data="d.f6" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form2a v-if="isSel('f2a')" :data="d.f2a" :tahun="ctx.tahun" />
    <Form2b
      v-if="isSel('f2b')"
      :rows="d.f2b || []"
      :opdctx="d.opdctx || {}"
      :tujuan="d.rtTujuan || []"
      :sasaran="d.rtSasaran || []"
      :iku="d.rtIku || []"
      :program="d.rtProgram || []"
      :opd-name="opdName"
      :tahun="ctx.tahun"
    />
    <Form2c
      v-if="isSel('f2c')"
      :renja="d.renjaC || {}"
      :rows="d.f2c || []"
      :tujuan="d.rtTujuan || []"
      :opdctx="d.opdctx || {}"
      :opd-name="opdName"
      :tahun="ctx.tahun"
    />
    <!-- Form 3.a/3.b/3.c dicetak terpisah (tiap section = halaman sendiri). -->
    <Form3 v-if="isSel('f3a') && d.f4" :data="d.f4" jenis="strategis_pemda" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form3 v-if="isSel('f3b') && d.f4" :data="d.f4" jenis="strategis_opd" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form3 v-if="isSel('f3c') && d.f4" :data="d.f4" jenis="operasional_opd" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form4 v-if="isSel('f4') && d.f4" :data="d.f4" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form5 v-if="isSel('f5') && d.f5" :data="d.f5" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form7 v-if="isSel('f7') && d.f7" :data="d.f7" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form8 v-if="isSel('f8')" :data="d.f8" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form9 v-if="isSel('f9')" :data="d.f9" :opd-name="opdName" :tahun="ctx.tahun" />
    <Form10 v-if="isSel('f10') && d.f10" :data="d.f10" :opd-name="opdName" :tahun="ctx.tahun" />
  </div>
</template>
