<script setup>
import { computed } from 'vue'

// Satu komponen dipakai untuk tiga cetakan terpisah (3.a/3.b/3.c); `data`
// adalah hasil /risiko/form4 yang sudah dikelompokkan per jenis.
const props = defineProps({
  data: { type: Array, default: () => [] },
  jenis: { type: String, required: true },
  opdName: String,
  tahun: [Number, String],
})

// Nomor form, judul, dan label kolom konteks mengikuti sheet asal pada
// "Kertas Kerja Manajemen Risiko" (Form3a/3b/3c).
const META = {
  strategis_pemda: {
    no: 'Form 3.a',
    judul: 'Identifikasi Risiko Strategis Pemerintah Daerah',
    konteks: 'Tujuan/Sasaran Strategis/Program',
    indikator: 'Indikator Kinerja',
  },
  strategis_opd: {
    no: 'Form 3.b',
    judul: 'Identifikasi Risiko Strategis OPD',
    konteks: 'Tujuan/Sasaran Strategis',
    indikator: 'Indikator Kinerja',
  },
  operasional_opd: {
    no: 'Form 3.c',
    judul: 'Identifikasi Risiko Operasional OPD',
    konteks: 'Kegiatan',
    indikator: 'Indikator Keluaran',
  },
}
const meta = computed(() => META[props.jenis] || META.strategis_pemda)
// Hanya Form 3.c yang punya kolom Tahap (di bawah grup Risiko).
const isOperasional = computed(() => props.jenis === 'operasional_opd')
const items = computed(
  () => (props.data || []).find((g) => g.jenis === props.jenis)?.items || [],
)
const cols = computed(() => (isOperasional.value ? 12 : 11))
</script>

<template>
  <section class="report-section">
    <div class="report-formno">{{ meta.no }}</div>
    <div class="report-title">Kertas Kerja {{ meta.judul }}</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead>
        <tr>
          <th rowspan="2" style="width: 28px">No</th>
          <th rowspan="2">{{ meta.konteks }}</th>
          <th rowspan="2">{{ meta.indikator }}</th>
          <th :colspan="isOperasional ? 4 : 3">Risiko</th>
          <th colspan="2">Sebab</th>
          <th rowspan="2" style="width: 40px">Status (C/UC)</th>
          <th colspan="2">Dampak</th>
        </tr>
        <tr>
          <th v-if="isOperasional" style="width: 90px">Tahap</th>
          <th>Uraian</th>
          <th style="width: 90px">Kode Risiko</th>
          <th style="width: 110px">Pemilik</th>
          <th>Uraian</th>
          <th style="width: 80px">Sumber</th>
          <th>Uraian</th>
          <th style="width: 110px">Pihak yang Terkena</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(it, i) in items" :key="it.id">
          <td class="c">{{ it.no_urut || i + 1 }}</td>
          <td>{{ isOperasional ? it.kegiatan : it.tujuan_sasaran }}</td>
          <td>{{ isOperasional ? it.indikator_keluaran : it.indikator_kinerja }}</td>
          <td v-if="isOperasional">{{ it.tahap_kegiatan }}</td>
          <td>
            <div>{{ it.uraian_risiko }}</div>
            <div v-if="it.keterangan_risiko" class="muted" style="font-size: 0.72rem; margin-top: 2px;">
              {{ it.keterangan_risiko }}
            </div>
          </td>
          <td>{{ it.kode_risiko }}</td>
          <td>{{ it.pemilik_risiko }}</td>
          <td>{{ it.sebab_uraian }}</td>
          <td>{{ it.sebab_sumber }}</td>
          <td class="c">{{ it.cuc }}</td>
          <td>{{ it.dampak_uraian }}</td>
          <td>{{ it.dampak_pihak_terkena }}</td>
        </tr>
        <tr v-if="!items.length">
          <td :colspan="cols" class="c">Belum ada data</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
