<script setup>
import { computed } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] }, // entri Form 2.b (blok kuning + kop)
  opdctx: { type: Object, default: () => ({}) }, // kop & tanda tangan (ta_opd)
  tujuan: { type: Array, default: () => [] }, // data renstra (blok hijau)
  sasaran: { type: Array, default: () => [] },
  iku: { type: Array, default: () => [] },
  program: { type: Array, default: () => [] },
  opdName: String,
  tahun: [Number, String],
})

const uniq = (arr) => [...new Set(arr.filter(Boolean))]
// Blok HIJAU = seluruh data renstra OPD.
const rtTujuan = computed(() => props.tujuan.map((o) => o.value))
const rtSasaran = computed(() => props.sasaran.map((o) => o.value))
const rtIku = computed(() => props.iku.map((o) => o.value))
const rtProgram = computed(() => props.program.map((o) => o.value))
// Kop = data yang dientri di Form 2.b.
const sumber = computed(() => uniq(props.rows.map((r) => r.sumber_data)).join('; '))
const periode = computed(() => uniq(props.rows.map((r) => r.periode_dinilai)).join('; '))
// Blok KUNING = HANYA T/S/IKU/Program yang dipilih/dientri di Form 2.b
// (subset yang akan dinilai risikonya), bukan seluruh data renstra.
const enTujuan = computed(() => uniq(props.rows.map((r) => r.tujuan_strategis)))
const enSasaran = computed(() => uniq(props.rows.map((r) => r.sasaran_strategis)))
const enIku = computed(() => uniq(props.rows.map((r) => r.iku_renstra)))
const enProgram = computed(() => uniq(props.rows.map((r) => r.program)))
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Lampiran 5<br />Form 2.b</div>
    <div class="report-title">Penetapan Konteks Risiko Strategis OPD</div>
    <table class="rpt f2b">
      <colgroup><col style="width: 210px" /><col /></colgroup>
      <tbody>
        <!-- Kop identitas -->
        <tr><td>Nama Pemda</td><td class="hijau">Pemerintah Kota Tegal</td></tr>
        <tr><td>Tahun Penilaian</td><td class="hijau">{{ tahun }}</td></tr>
        <tr><td>Periode yang Dinilai</td><td class="hijau">{{ periode || '-' }}</td></tr>
        <tr><td>Bidang Urusan</td><td class="hijau">{{ opdctx.bidang_urusan || '-' }}</td></tr>
        <tr><td>OPD yang Dinilai</td><td class="hijau">{{ opdName }}</td></tr>
        <!-- Isi konteks: blok hijau = data renstra -->
        <tr><td>Sumber Data</td><td class="hijau">{{ sumber || '-' }}</td></tr>
        <tr>
          <td>Tujuan Strategis</td>
          <td class="hijau">
            <div v-for="(t, i) in rtTujuan" :key="i" class="pre-line">{{ t }}</div>
            <span v-if="!rtTujuan.length">-</span>
          </td>
        </tr>
        <tr>
          <td>Sasaran Strategis</td>
          <td class="hijau">
            <div v-for="(s, i) in rtSasaran" :key="i" class="pre-line">{{ s }}</div>
            <span v-if="!rtSasaran.length">-</span>
          </td>
        </tr>
        <tr>
          <td>IKU Renstra OPD</td>
          <td class="hijau">
            <ol v-if="rtIku.length" class="kelemahan-ol"><li v-for="(k, i) in rtIku" :key="i">{{ k }}</li></ol>
            <span v-else>-</span>
          </td>
        </tr>
        <tr>
          <td>Program</td>
          <td class="hijau">
            <ol v-if="rtProgram.length" class="kelemahan-ol"><li v-for="(p, i) in rtProgram" :key="i">{{ p }}</li></ol>
            <span v-else>-</span>
          </td>
        </tr>
        <!-- Blok kuning = data yang dientri di Form 2.b -->
        <tr>
          <td>Tujuan, Sasaran, IKU dan Program yang akan dilakukan penilaian risiko</td>
          <td class="kuning pre-line">
            <b>Tujuan Strategis :</b>
              <div v-for="(t, i) in enTujuan" :key="i" class="pre-line">{{ t }}</div>
              <span v-if="!enTujuan.length">-</span>
            <b>Sasaran Strategis :</b>
              <div v-for="(s, i) in enSasaran" :key="i" class="pre-line">- {{ s }}</div>
              <span v-if="!enSasaran.length">-</span>
            <b>IKU Renstra OPD :</b>
              <ol v-if="enIku.length" class="kelemahan-ol"><li v-for="(k, i) in enIku" :key="i">{{ k }}</li></ol>
              <span v-else>-</span>
            <b>Program :</b>
              <ol v-if="enProgram.length" class="kelemahan-ol"><li v-for="(p, i) in enProgram" :key="i">{{ p }}</li></ol>
              <span v-else>-</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="report-sign">
      <div class="box">
        Kota Tegal, Desember {{ Number(tahun) - 1 }}<br />
        {{ opdctx.jabatan_kepala || ('Kepala ' + opdName) }}<br /><br /><br /><br />
        <span style="text-decoration: underline; font-weight: 600">{{ opdctx.nama_kepala || '(………………………………)' }}</span><br />
        <span v-if="opdctx.nip_kepala">NIP. {{ opdctx.nip_kepala }}</span>
      </div>
    </div>
  </section>
</template>
