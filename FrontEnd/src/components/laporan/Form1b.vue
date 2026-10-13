<script setup>
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 1.b</div>
    <div class="report-title">Simpulan CEE Berdasarkan Reviu Dokumen</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 40px">No</th><th>Sub-unsur / Aspek</th><th style="width: 130px">Hasil Reviu</th><th style="width: 180px">Sumber Data</th><th>Uraian Kelemahan</th></tr></thead>
      <tbody>
        <tr v-for="r in data" :key="r.item_id">
          <td class="c">{{ r.nomor }}</td><td>{{ r.aspek }}</td>
          <td class="c">{{ r.simpulan ?? '' }}</td>
          <td>{{ r.sumber_data }}</td>
          <td>
            <ol v-if="r.kelemahan && r.kelemahan.length" class="kelemahan-ol">
              <li v-for="k in r.kelemahan" :key="k.id">{{ k.uraian }}</li>
            </ol>
            <span v-else class="pre-line">{{ r.keterangan }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
