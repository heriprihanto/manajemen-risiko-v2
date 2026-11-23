<script setup>
import { formatDate } from '@/utils/date'
defineProps({ data: { type: Array, default: () => [] }, opdName: String, tahun: [Number, String] })

function parseEvidenceList(buktiLink, buktiNama) {
  if (!buktiLink) return []
  try {
    const parsed = JSON.parse(buktiLink)
    if (Array.isArray(parsed)) {
      return parsed.map((item) => ({
        nama: item.nama || '',
        link: item.link || '',
      }))
    }
  } catch {}
  return [
    {
      nama: buktiNama || 'Bukti Dukung',
      link: buktiLink,
    },
  ]
}
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Form 11 Perwal / Form 8 aplikasi</div>
    <div class="report-title">Rencana & Realisasi Pengkomunikasian Pengendalian</div>
    <div class="report-subtitle">{{ opdName }} — Tahun {{ tahun }}</div>
    <table class="rpt">
      <thead><tr><th style="width: 28px">No</th><th>Kegiatan Pengendalian</th><th>Media/Bentuk</th><th>Penyedia</th><th>Penerima</th><th style="width: 90px">Rencana</th><th style="width: 90px">Realisasi</th></tr></thead>
      <tbody>
        <tr v-for="(r, i) in data" :key="r.id">
          <td class="c">{{ r.no_urut || i + 1 }}</td><td>{{ r.kegiatan_pengendalian }}</td><td>{{ r.media_bentuk }}</td>
          <td>{{ r.penyedia_informasi }}</td><td>{{ r.penerima_informasi }}</td><td>{{ formatDate(r.rencana_waktu) }}</td>
          <td>
            <div>{{ formatDate(r.realisasi_waktu) }}</div>
            <div v-if="r.keterangan" style="font-size: 0.78rem; color: #475569; margin-top: 3px;">
              <em>{{ r.keterangan }}</em>
            </div>
            <div v-if="parseEvidenceList(r.bukti_dukung, r.bukti_nama).length" style="margin-top: 3px;">
              <div v-for="(ev, evIdx) in parseEvidenceList(r.bukti_dukung, r.bukti_nama)" :key="evIdx" style="margin-bottom: 2px;">
                <a :href="ev.link" target="_blank" rel="noopener noreferrer" style="font-size: 0.75rem; color: #2563eb; text-decoration: underline">
                  {{ ev.nama || 'Bukti Dukung ' + (evIdx + 1) }} &nearr;
                </a>
              </div>
            </div>
          </td>
        </tr>

        <tr v-if="!data || !data.length"><td colspan="7" class="c">Belum ada data</td></tr>
      </tbody>
    </table>
  </section>
</template>
