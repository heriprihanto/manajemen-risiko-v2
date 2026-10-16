<script setup>
import { statusLabel, responLabel } from '@/utils/rtp'
import { formatDate } from '@/utils/date'
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 10 Perwal / Form 7 aplikasi</div>
    <div class="report-title">Penilaian Kegiatan Pengendalian (RTP atas Hasil Identifikasi Risiko)</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 28px">No</th><th>Risiko Prioritas</th><th style="width: 90px">Kode</th><th>Pemilik</th><th>Status / Pengendalian / Bukti</th><th>Celah</th><th>Respon Risiko / Rencana Tindak</th><th style="width: 90px">Target</th></tr></thead>
      <tbody>
        <tr v-for="(it, i) in data" :key="it.id">
          <td class="c">{{ i + 1 }}</td><td>{{ it.uraian_risiko }}</td><td>{{ it.kode_risiko }}</td>
          <td>{{ it.pemilik_risiko }}</td>
          <td><div v-if="it.rtp?.status_pengendalian">{{ statusLabel(it.rtp.status_pengendalian) }}</div>{{ it.rtp?.pengendalian_ada }}<div v-if="it.rtp?.bukti_judul">Bukti: {{ it.rtp.bukti_judul }}<br>{{ it.rtp.bukti_link || it.rtp.bukti_nama }}</div></td><td>{{ it.rtp?.celah_pengendalian }}</td>
          <td><div v-if="it.rtp?.respon_risiko">{{ responLabel(it.rtp.respon_risiko) }}</div>{{ it.rtp?.rencana_tindak }}</td><td>{{ formatDate(it.rtp?.target_waktu) }}</td>
        </tr>

        <tr v-if="!data || !data.length"><td colspan="8" class="c">Belum ada risiko prioritas</td></tr>
      </tbody>
    </table>
  </section>
</template>
