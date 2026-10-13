<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })

// Form 6 dikelompokkan per Aspek/Sub-unsur CEE.
const grouped = computed(() => {
  const groups = {}
  for (const r of props.data || []) {
    const key = r.aspek_cee || '(Tanpa Sub-unsur)'
    ;(groups[key] ||= []).push(r)
  }
  return Object.entries(groups).map(([aspek, items]) => ({ aspek, items }))
})
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 6</div>
    <div class="report-title">Penilaian Kegiatan Pengendalian (RTP atas CEE)</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 36px">No</th><th>Kondisi Kurang Memadai</th><th>Rencana Tindak Pengendalian</th><th>Penanggung Jawab</th><th style="width: 90px">Target</th><th style="width: 90px">Realisasi</th></tr></thead>
      <tbody>
        <template v-for="g in grouped" :key="g.aspek">
          <tr><td class="c"></td><td colspan="5"><b>{{ g.aspek }}</b></td></tr>
          <tr v-for="(r, i) in g.items" :key="r.id">
            <td class="c">{{ r.no_urut || i + 1 }}</td><td>{{ r.kondisi_kerentanan }}</td><td>{{ r.rencana_tindak }}</td>
            <td>{{ r.pemilik_penanggung_jawab }}</td><td>{{ r.target_waktu }}</td><td>{{ r.realisasi_waktu }}</td>
          </tr>
        </template>
        <tr v-if="!data || !data.length"><td colspan="6" class="c">Belum ada data</td></tr>
      </tbody>
    </table>
  </section>
</template>
