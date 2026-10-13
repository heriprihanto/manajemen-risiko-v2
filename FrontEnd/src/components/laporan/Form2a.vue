<script setup>
defineProps({ data: { type: Object, default: null }, tahun: [Number, String] })

// Field multi-pilihan Form 2.a disimpan sebagai teks dipisah newline.
const toList = (v) => (v ? String(v).split('\n').filter(Boolean) : [])

const rows = [
  ['Periode yang Dinilai', 'periode_dinilai', false],
  ['Visi', 'visi', false],
  ['Misi Strategis RPJMD', 'misi_strategis', true],
  ['Penetapan Konteks Tujuan Risiko Strategis Pemda', 'penetapan_konteks_tujuan', true],
  ['Penetapan Konteks Sasaran Risiko Strategis Pemda', 'penetapan_konteks_sasaran', true],
  ['Penetapan Konteks IKU Risiko Strategis Pemda', 'penetapan_konteks_iku', true],
  ['Prioritas Pembangunan Daerah', 'prioritas_pembangunan', true],
  ['Program Prioritas', 'prioritas_program', true],
]
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 2.a</div>
    <div class="report-title">Penetapan Konteks Risiko Strategis Pemda</div>
    <div class="report-subtitle">Tahun {{ tahun }}</div>
    <table class="rpt">
      <tbody v-if="data">
        <tr v-for="r in rows" :key="r[1]">
          <th style="width: 280px; text-align: left">{{ r[0] }}</th>
          <td>
            <ol v-if="r[2] && toList(data[r[1]]).length" style="margin: 0; padding-left: 1.1rem">
              <li v-for="(v, i) in toList(data[r[1]])" :key="i">{{ v }}</li>
            </ol>
            <template v-else>{{ data[r[1]] }}</template>
          </td>
        </tr>
      </tbody>
      <tbody v-else><tr><td class="c">Belum ada data</td></tr></tbody>
    </table>
  </section>
</template>
