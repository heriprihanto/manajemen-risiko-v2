<script setup>
import { computed } from 'vue'
import { jenisLabel } from './constants'
import { formatDate } from '@/utils/date'

const props = defineProps({
  data: { type: Array, default: () => [] },
  opdName: String,
  tahun: [Number, String],
})

// Urutan tetap jenis risiko (Form 3.a → 3.b → 3.c). Hanya risiko yang punya
// kejadian (event) yang dicetak; grup tanpa event tidak ditampilkan.
const ORDER = ['strategis_pemda', 'strategis_opd', 'operasional_opd']
const groups = computed(() => {
  const map = {}
  for (const r of props.data || []) {
    if (!r.events || !r.events.length) continue
    const key = ORDER.includes(r.jenis_risiko) ? r.jenis_risiko : '_lain'
    ;(map[key] ||= []).push(r)
  }
  const out = []
  for (const j of ORDER) if (map[j]) out.push({ jenis: j, label: jenisLabel[j], items: map[j] })
  if (map._lain) out.push({ jenis: '_lain', label: 'Lainnya', items: map._lain })
  return out
})

function formatEventTime(ev) {
  const val = ev.waktu_kejadian || ev.tanggal_terjadi
  if (!val) return '—'
  const s = String(val).trim()
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?/)
  if (m) {
    const d = new Date(parseInt(m[1], 10), parseInt(m[2], 10) - 1, parseInt(m[3], 10))
    const tgl = d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
    if (m[4] && m[5]) {
      return `${tgl} ${m[4]}:${m[5]}`
    }
    return tgl
  }
  return formatDate(val)
}

function formatTanggalRealisasi(r, ev) {
  const rel = r.realisasi_data
  if (rel) {
    const mulai = rel.tanggal_mulai
    const selesai = rel.tanggal_selesai
    if (mulai && selesai && mulai !== selesai) {
      return `${formatDate(mulai)} s.d. ${formatDate(selesai)}`
    }
    if (mulai) return formatDate(mulai)
    if (selesai) return formatDate(selesai)
    if (rel.tanggal_realisasi) return formatDate(rel.tanggal_realisasi)
  }
  if (r.tanggal_realisasi_rtp && r.tanggal_realisasi_rtp !== '—') {
    return formatDate(r.tanggal_realisasi_rtp)
  }
  if (r.realisasi_rtp && r.realisasi_rtp !== '—') {
    return formatDate(r.realisasi_rtp)
  }
  if (ev?.realisasi_pelaksanaan_rtp && ev.realisasi_pelaksanaan_rtp !== '—') {
    return formatDate(ev.realisasi_pelaksanaan_rtp)
  }
  return '—'
}
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 10</div>
    <div class="report-title">Pencatatan Kejadian Risiko (Risk Event) & Pelaksanaan RTP</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead>
        <tr>
          <th style="width: 75px">Kode</th>
          <th style="width: 140px">Risiko</th>
          <th style="width: 85px">Waktu</th>
          <th style="width: 90px">Tempat</th>
          <th>Uraian Kejadian</th>
          <th style="width: 110px">Pemicu / Sebab</th>
          <th style="width: 110px">Dampak</th>
          <th style="width: 140px">RTP</th>
          <th style="width: 120px">Realisasi RTP</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="g in groups" :key="g.jenis">
          <tr><td colspan="9"><b>{{ g.label }}</b></td></tr>
          <template v-for="r in g.items" :key="r.risiko_id">
            <tr v-for="ev in r.events" :key="ev.id">
              <td>{{ r.kode_risiko }}</td>
              <td>{{ r.uraian_risiko }}</td>
              <td class="c">{{ formatEventTime(ev) }}</td>
              <td>{{ ev.tempat_kejadian || '—' }}</td>
              <td>{{ ev.uraian_kejadian || '—' }}</td>
              <td>{{ ev.sebab_kejadian || '—' }}</td>
              <td>{{ ev.dampak_kejadian || '—' }}</td>
              <td>
                <div v-if="ev.rtp">{{ ev.rtp }}</div>
                <div v-else-if="r.rtp_data?.rencana_tindak">
                  <div>{{ r.rtp_data.rencana_tindak }}</div>
                  <div v-if="r.rtp_data.target_waktu" style="font-size: 0.8em; color: #555; margin-top: 2px;">
                    Target: {{ formatDate(r.rtp_data.target_waktu) }}
                  </div>
                  <div v-if="r.rtp_data.penanggung_jawab" style="font-size: 0.8em; color: #555;">
                    PIC: {{ r.rtp_data.penanggung_jawab }}
                  </div>
                </div>
                <div v-else-if="r.rtp">{{ r.rtp }}</div>
                <span v-else>—</span>
              </td>
              <td class="c">
                {{ formatTanggalRealisasi(r, ev) }}
              </td>
            </tr>
          </template>
        </template>
        <tr v-if="!groups.length"><td colspan="9" class="c">Belum ada kejadian dicatat</td></tr>
      </tbody>
    </table>
    <div class="report-sign">
      <div class="box">
        Kota Tegal, {{ tahun }}<br />Kepala {{ opdName }}<br /><br /><br /><br />
        (...........................................)
      </div>
    </div>
  </section>
</template>
