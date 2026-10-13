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
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 10</div>
    <div class="report-title">Pencatatan Kejadian Risiko (Risk Event) & Pelaksanaan RTP</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 90px">Kode</th><th>Risiko</th><th style="width: 80px">Tanggal</th><th>Sebab</th><th>Dampak</th><th>RTP</th><th>Realisasi RTP</th></tr></thead>
      <tbody>
        <template v-for="g in groups" :key="g.jenis">
          <tr><td colspan="7"><b>{{ g.label }}</b></td></tr>
          <template v-for="r in g.items" :key="r.risiko_id">
            <tr v-for="ev in r.events" :key="ev.id">
              <td>{{ r.kode_risiko }}</td><td>{{ r.uraian_risiko }}</td><td class="c">{{ formatDate(ev.tanggal_terjadi) }}</td>
              <td>{{ ev.sebab_kejadian }}</td><td>{{ ev.dampak_kejadian }}</td><td>{{ ev.rtp }}</td><td>{{ ev.realisasi_pelaksanaan_rtp }}</td>
            </tr>
          </template>
        </template>
        <tr v-if="!groups.length"><td colspan="7" class="c">Belum ada kejadian dicatat</td></tr>
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
