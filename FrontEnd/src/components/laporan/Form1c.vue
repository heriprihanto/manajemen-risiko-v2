<script setup>
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 1.c</div>
    <div class="report-title">Simpulan Survei Persepsi atas Lingkungan Pengendalian Intern</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 36px">No</th><th>Sub-unsur</th><th style="width: 110px">Hasil Persepsi</th><th style="width: 110px">Hasil Dokumen</th><th style="width: 110px">Simpulan</th><th>Penjelasan</th></tr></thead>
      <tbody>
        <tr v-for="r in data" :key="r.kategori_id">
          <td class="c">{{ r.no }}</td><td>{{ r.sub_unsur }}</td>
          <td class="c">{{ r.hasil_persepsi }}</td><td class="c">{{ r.hasil_dokumen }}</td>
          <td class="c">{{ r.simpulan }}</td>
          <td>
            <span v-if="r.penjelasan" class="pre-line">{{ r.penjelasan }}</span>
            <ol v-else-if="r.kelemahan && r.kelemahan.length" class="kelemahan-ol">
              <li v-for="k in r.kelemahan" :key="k.id">{{ k.uraian }}</li>
            </ol>
            <span v-else class="pre-line">{{ r.uraian_dokumen }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
