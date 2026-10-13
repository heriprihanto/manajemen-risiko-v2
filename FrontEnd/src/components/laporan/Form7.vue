<script setup>
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 7</div>
    <div class="report-title">Penilaian Kegiatan Pengendalian (RTP atas Hasil Identifikasi Risiko)</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 28px">No</th><th>Risiko Prioritas</th><th style="width: 90px">Kode</th><th>Pemilik</th><th>Pengendalian yang Ada</th><th>Celah</th><th>Rencana Tindak Pengendalian</th><th style="width: 90px">Target</th></tr></thead>
      <tbody>
        <tr v-for="(it, i) in data" :key="it.id">
          <td class="c">{{ i + 1 }}</td><td>{{ it.uraian_risiko }}</td><td>{{ it.kode_risiko }}</td>
          <td>{{ it.pemilik_risiko }}</td>
          <td>{{ it.rtp?.pengendalian_ada }}</td><td>{{ it.rtp?.celah_pengendalian }}</td>
          <td>{{ it.rtp?.rencana_tindak }}</td><td>{{ it.rtp?.target_waktu }}</td>
        </tr>
        <tr v-if="!data || !data.length"><td colspan="8" class="c">Belum ada risiko prioritas</td></tr>
      </tbody>
    </table>
  </section>
</template>
