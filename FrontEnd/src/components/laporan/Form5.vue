<script setup>
import { jenisLabel } from './constants'
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 5</div>
    <div class="report-title">Kertas Kerja Daftar Risiko Prioritas</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 28px">No</th><th>Risiko Prioritas</th><th style="width: 90px">Kode</th><th style="width: 50px">Skala</th><th>Pemilik</th><th>Penyebab</th><th>Dampak</th></tr></thead>
      <tbody>
        <template v-for="g in data" :key="g.jenis">
          <tr v-if="g.items.length"><td class="c"></td><td colspan="6"><b>{{ jenisLabel[g.jenis] }}</b></td></tr>
          <tr v-for="(it, i) in g.items" :key="it.id">
            <td class="c">{{ i + 1 }}</td><td>{{ it.uraian_risiko }}</td><td>{{ it.kode_risiko }}</td>
            <td class="c"><b>{{ it.analisis.skala_risiko }}</b></td><td>{{ it.pemilik_risiko }}</td>
            <td>{{ it.sebab_uraian }}</td><td>{{ it.dampak_uraian }}</td>
          </tr>
        </template>
      </tbody>
    </table>
  </section>
</template>
