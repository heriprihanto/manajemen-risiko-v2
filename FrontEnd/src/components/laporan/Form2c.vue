<script setup>
import { computed } from 'vue'

const props = defineProps({
  renja: { type: Object, default: () => ({}) }, // {subkegiatan, indikator_program, indikator_kegiatan}
  rows: { type: Array, default: () => [] }, // konteks_operasional (menandai yg dicentang)
  tujuan: { type: Array, default: () => [] }, // renstra_tujuan [{value,label}]
  opdctx: { type: Object, default: () => ({}) },
  opdName: String,
  tahun: [Number, String],
})

const checkedSub = computed(() => new Set(props.rows.map((r) => r.ref_subkegiatan).filter(Boolean)))
const checkedInd = computed(() => new Set(props.rows.map((r) => r.ref_indikator).filter(Boolean)))
const tujuanList = computed(() => props.tujuan.map((t) => t.value))

// Ratakan hierarki Program → Kegiatan → Sub Kegiatan menjadi baris tabel cetak.
const flat = computed(() => {
  const subkeg = props.renja.subkegiatan || []
  const progInd = props.renja.indikator_program || []
  const kegInd = props.renja.indikator_kegiatan || []
  const prog = new Map()
  const ensureProg = (id, nm) => {
    if (!prog.has(id)) prog.set(id, { nm, progInd: [], kegMap: new Map() })
    return prog.get(id)
  }
  const ensureKeg = (g, id, nm) => {
    if (!g.kegMap.has(id)) g.kegMap.set(id, { nm, kegInd: [], subs: [] })
    return g.kegMap.get(id)
  }
  for (const s of subkeg) ensureKeg(ensureProg(s.idprogram, s.nm_program), s.idkegiatan, s.nm_kegiatan).subs.push(s)
  for (const pi of progInd) ensureProg(pi.idprogram, pi.nm_program).progInd.push(pi)
  for (const ki of kegInd) ensureKeg(ensureProg(ki.idprogram, ki.nm_program), ki.idkegiatan, ki.nm_kegiatan).kegInd.push(ki)

  const out = []
  const cs = checkedSub.value
  const ci = checkedInd.value
  for (const g of prog.values()) {
    if (g.progInd.length) {
      g.progInd.forEach((pi, i) =>
        out.push({ level: 1, nama: i === 0 ? g.nm : '', indikator: pi.tolok, target: pi.target, sel: ci.has(pi.id) }),
      )
    } else {
      out.push({ level: 1, nama: g.nm, indikator: '', target: '', sel: false })
    }
    for (const k of g.kegMap.values()) {
      if (k.kegInd.length) {
        k.kegInd.forEach((ki, i) =>
          out.push({ level: 2, nama: i === 0 ? k.nm : '', indikator: ki.tolok, target: ki.target, sel: ci.has(ki.id) }),
        )
      } else {
        out.push({ level: 2, nama: k.nm, indikator: '', target: '', sel: false })
      }
      for (const s of k.subs) {
        const inds = s.indikator_list?.length ? s.indikator_list : [{ tolok: '', target: '' }]
        inds.forEach((ind, i) =>
          out.push({
            level: 3,
            nama: i === 0 ? `${s.kode_sub_kegiatan} ${s.nm_sub_kegiatan}` : '',
            indikator: ind.tolok,
            target: ind.target,
            sel: i === 0 && cs.has(s.idsubkegiatan),
          }),
        )
      }
    }
  }
  return out.map((r, i) => ({ ...r, no: i + 1 }))
})
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Lampiran 6<br />Form 2.c</div>
    <div class="report-title">Penetapan Konteks Risiko Operasional OPD</div>

    <table class="rpt f2b">
      <colgroup><col style="width: 210px" /><col /></colgroup>
      <tbody>
        <tr><td>Nama Pemda</td><td>Pemerintah Kota Tegal</td></tr>
        <tr><td>Tahun Penilaian</td><td>{{ tahun }}</td></tr>
        <tr><td>Periode yang Dinilai</td><td>DPA/APBD {{ opdName }} Tahun {{ tahun }}</td></tr>
        <tr><td>Urusan Pemerintahan</td><td>{{ opdctx.bidang_urusan || '-' }}</td></tr>
        <tr><td>OPD yang Dinilai</td><td>{{ opdName }}</td></tr>
        <tr><td>Sumber Data</td><td>Renja {{ opdName }} Tahun {{ tahun }}</td></tr>
        <tr>
          <td>Tujuan Strategis</td>
          <td>
            <div v-for="(t, i) in tujuanList" :key="i" class="pre-line">{{ t }}</div>
            <span v-if="!tujuanList.length">-</span>
          </td>
        </tr>
      </tbody>
    </table>

    <table class="rpt" style="margin-top: 10px">
      <thead>
        <tr>
          <th style="width: 34px">No</th>
          <th>Program / Kegiatan / Sub Kegiatan</th>
          <th>Indikator Program / Kegiatan / Sub Kegiatan</th>
          <th style="width: 110px">Target</th>
          <th style="width: 70px">Dilakukan Penilaian Risiko</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in flat" :key="r.no">
          <td class="c">{{ r.no }}</td>
          <td :class="'lvl' + r.level">{{ r.nama }}</td>
          <td>{{ r.indikator }}</td>
          <td>{{ r.target }}</td>
          <td class="c">{{ r.sel ? '✓' : '' }}</td>
        </tr>
        <tr v-if="!flat.length"><td colspan="5" class="c">Belum ada data renja</td></tr>
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

<style scoped>
table.rpt td.lvl1 { font-weight: 700; }
table.rpt td.lvl2 { font-weight: 600; padding-left: 16px; }
table.rpt td.lvl3 { padding-left: 30px; }
</style>
