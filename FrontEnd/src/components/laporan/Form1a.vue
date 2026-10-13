<script setup>
defineProps({ data: { type: Object, required: true }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 1.a</div>
    <div class="report-title">Rekapitulasi Hasil Kuesioner Penilaian Lingkungan Pengendalian (CEE)</div>
    <div class="report-subtitle">{{ opdName }} — Tahun Penilaian {{ tahun }}</div>
    <table class="rpt">
      <thead>
        <tr>
          <th rowspan="2" style="width: 28px">No</th>
          <th rowspan="2">Pertanyaan / Sub-unsur</th>
          <th :colspan="data.responden.length || 1">Jawaban Responden</th>
          <th rowspan="2" style="width: 48px">Modus</th>
          <th rowspan="2" style="width: 120px">Simpulan</th>
        </tr>
        <tr>
          <th v-for="r in data.responden" :key="r.id" style="width: 30px">{{ r.kode_responden }}</th>
          <th v-if="!data.responden.length">—</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="kat in data.kategori" :key="kat.id">
          <tr>
            <td class="c"><b>{{ kat.kode }}</b></td>
            <td :colspan="(data.responden.length || 1) + 2"><b>{{ kat.nama }}</b></td>
            <td class="c">{{ kat.simpulan }}</td>
          </tr>
          <tr v-for="(pq, i) in kat.pertanyaan" :key="pq.id">
            <td class="c">{{ i + 1 }}</td>
            <td>{{ pq.pertanyaan }}</td>
            <td v-for="r in data.responden" :key="r.id" class="c">{{ pq.jawaban[r.id] ?? '' }}</td>
            <td v-if="!data.responden.length" class="c"></td>
            <td class="c">{{ pq.modus ?? '' }}</td>
            <td class="c">{{ pq.simpulan ?? '' }}</td>
          </tr>
        </template>
      </tbody>
    </table>
  </section>
</template>
