<script setup>
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 8</div>
    <div class="report-title">Rencana & Realisasi Pengkomunikasian Pengendalian</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 28px">No</th><th>Kegiatan Pengendalian</th><th>Media/Bentuk</th><th>Penyedia</th><th>Penerima</th><th style="width: 90px">Rencana</th><th style="width: 90px">Realisasi</th></tr></thead>
      <tbody>
        <tr v-for="(r, i) in data" :key="r.id">
          <td class="c">{{ r.no_urut || i + 1 }}</td><td>{{ r.kegiatan_pengendalian }}</td><td>{{ r.media_bentuk }}</td>
          <td>{{ r.penyedia_informasi }}</td><td>{{ r.penerima_informasi }}</td><td>{{ r.rencana_waktu }}</td><td>{{ r.realisasi_waktu }}</td>
        </tr>
        <tr v-if="!data || !data.length"><td colspan="7" class="c">Belum ada data</td></tr>
      </tbody>
    </table>
  </section>
</template>
