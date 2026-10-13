<script setup>
import { computed } from 'vue'
import { jenisLabel } from './constants'

const props = defineProps({
  data: { type: Array, default: () => [] },
  opdName: String,
  tahun: [Number, String],
})

// Urutan tetap jenis risiko (Form 3.a → 3.b → 3.c); baris tanpa jenis diletakkan
// di grup "Lainnya" agar tetap tercetak.
const ORDER = ['strategis_pemda', 'strategis_opd', 'operasional_opd']
const groups = computed(() => {
  const map = {}
  for (const r of props.data || []) {
    const key = ORDER.includes(r.jenis_risiko) ? r.jenis_risiko : '_lain'
    ;(map[key] ||= []).push(r)
  }
  const out = []
  for (const j of ORDER) if (map[j]) out.push({ jenis: j, label: jenisLabel[j], items: map[j] })
  if (map._lain) out.push({ jenis: '_lain', label: 'Lainnya', items: map._lain })
  return out
})
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 9</div>
    <div class="report-title">Rencana &amp; Realisasi Pemantauan atas Kegiatan Pengendalian</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 28px">No</th><th>Kegiatan Pengendalian</th><th>Metode Pemantauan</th><th>Penanggung Jawab</th><th style="width: 90px">Rencana</th><th style="width: 90px">Realisasi</th></tr></thead>
      <tbody>
        <template v-for="g in groups" :key="g.jenis">
          <tr><td class="c"></td><td colspan="5"><b>{{ g.label }}</b></td></tr>
          <tr v-for="(r, i) in g.items" :key="r.id">
            <td class="c">{{ r.no_urut || i + 1 }}</td><td>{{ r.kegiatan_pengendalian }}</td><td>{{ r.metode_pemantauan }}</td>
            <td>{{ r.penanggung_jawab }}</td><td>{{ r.rencana_waktu }}</td><td>{{ r.realisasi_waktu }}</td>
          </tr>
        </template>
        <tr v-if="!groups.length"><td colspan="6" class="c">Belum ada data</td></tr>
      </tbody>
    </table>
  </section>
</template>
