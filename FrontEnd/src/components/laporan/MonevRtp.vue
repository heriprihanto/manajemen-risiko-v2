<script setup>
import { computed } from 'vue'
import { formatDate } from '@/utils/date'

const props = defineProps({
  data: { type: Array, default: () => [] },
  opdName: { type: String, default: '-' },
  tahun: [Number, String],
  periode: { type: String, default: 'tahunan' },
  periodeLabel: { type: String, default: 'Tahunan' },
})

const periodeSubtitle = computed(() => {
  if (props.periode && props.periode !== 'tahunan') {
    return `PERIODE ${props.periodeLabel.toUpperCase()} TAHUN ${props.tahun}`
  }
  return `TAHUN ${props.tahun}`
})

const ORDER = ['strategis_pemda', 'strategis_opd', 'operasional_opd']
const JENIS_LABEL = {
  strategis_pemda: 'Risiko Strategis Pemda',
  strategis_opd: 'Risiko Strategis OPD',
  operasional_opd: 'Risiko Operasional OPD',
  cee: 'RTP atas CEE (Lingkungan Pengendalian)',
}

const groups = computed(() => {
  const map = {}
  const list = Array.isArray(props.data) ? props.data : (props.data?.items || [])
  for (const r of list) {
    const key = r.source_type === 'cee' ? 'cee' : (ORDER.includes(r.jenis_risiko) ? r.jenis_risiko : '_lain')
    ;(map[key] ||= []).push(r)
  }
  const out = []
  for (const j of ORDER) {
    if (map[j]?.length) out.push({ jenis: j, label: JENIS_LABEL[j] || j, items: map[j] })
  }
  if (map.cee?.length) {
    out.push({ jenis: 'cee', label: JENIS_LABEL.cee, items: map.cee })
  }
  if (map._lain?.length) {
    out.push({ jenis: '_lain', label: 'Lainnya', items: map._lain })
  }
  return out
})

function formatRealisasiDate(rel) {
  if (!rel) return ''
  const mulai = rel.tanggal_mulai
  const selesai = rel.tanggal_selesai
  if (mulai && selesai && mulai !== selesai) {
    return `${formatDate(mulai)} s.d. ${formatDate(selesai)}`
  }
  if (mulai) return formatDate(mulai)
  if (selesai) return formatDate(selesai)
  if (rel.tanggal_realisasi) return formatDate(rel.tanggal_realisasi)
  return ''
}

function parseEvidenceList(buktiLink, buktiNama) {
  if (!buktiLink && !buktiNama) return []
  if (buktiLink) {
    try {
      const parsed = JSON.parse(buktiLink)
      if (Array.isArray(parsed) && parsed.length) {
        return parsed.map((item) => ({
          nama: item.nama || '',
          link: item.link || '',
        }))
      }
    } catch {
      // bukan JSON
    }
    return [
      {
        nama: buktiNama || 'Bukti Dokumen',
        link: buktiLink,
      },
    ]
  }
  return [
    {
      nama: buktiNama,
      link: '',
    },
  ]
}
</script>

<template>
  <section class="report-section">
    <div class="report-formno">Monev RTP</div>
    <div class="report-title">MONITORING DAN EVALUASI RENCANA TINDAK PENGENDALIAN RISIKO</div>
    <div class="report-subtitle">{{ opdName.toUpperCase() }} {{ periodeSubtitle }}</div>

    <table class="rpt">
      <thead>
        <tr>
          <th style="width: 40px">No</th>
          <th style="width: 220px">Risiko yang Terindentifikasi</th>
          <th style="width: 220px">Rencana Tindak Pengendalian (RTP)</th>
          <th style="width: 120px">Rencana Pelaksanaan RTP</th>
          <th style="width: 120px">Realisasi Pelaksanaan RTP</th>
          <th style="width: 200px">Bukti Dokumen</th>
          <th style="width: 180px">Keterjadian</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="g in groups" :key="g.jenis">
          <tr>
            <td colspan="7" class="group-header">
              <b>{{ g.label }}</b>
            </td>
          </tr>
          <tr v-for="(r, idx) in g.items" :key="r.id || idx">
            <!-- 1. No -->
            <td class="c">{{ idx + 1 }}</td>

            <!-- 2. Risiko yang Terindentifikasi -->
            <td>
              <div v-if="r.kode_risiko" class="kode-tag">[{{ r.kode_risiko }}]</div>
              <div class="uraian-risiko-text">{{ r.uraian_risiko || r.kondisi_kerentanan || '—' }}</div>
            </td>

            <!-- 3. Rencana Tindak Pengendalian (RTP) -->
            <td>
              {{ r.rtp?.rencana_tindak || r.rencana_tindak || '—' }}
            </td>

            <!-- 4. Rencana Pelaksanaan RTP -->
            <td class="c">
              {{ r.rtp?.target_waktu || r.target_waktu || '—' }}
            </td>

            <!-- 5. Realisasi Pelaksanaan RTP -->
            <td class="c">
              <span v-if="r.realisasi?.dilaksanakan_pada_periode === false" class="text-slate-400 italic">
                —
              </span>
              <span v-else>
                {{ formatRealisasiDate(r.realisasi) || r.rtp?.realisasi_waktu || r.realisasi_waktu || '—' }}
              </span>
            </td>

            <!-- 6. Bukti Dokumen -->
            <td>
              <template v-if="r.realisasi?.dilaksanakan_pada_periode !== false && parseEvidenceList(r.realisasi?.bukti_link, r.realisasi?.bukti_nama).length">
                <div
                  v-for="(ev, bIdx) in parseEvidenceList(r.realisasi?.bukti_link, r.realisasi?.bukti_nama)"
                  :key="bIdx"
                  class="doc-item mb-1"
                >
                  <a
                    v-if="ev.link"
                    :href="ev.link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="doc-link"
                    :title="ev.link"
                  >
                    <i class="pi pi-link text-xs mr-1" />
                    <span>{{ ev.nama || 'Tautan Bukti ' + (bIdx + 1) }}</span>
                  </a>
                  <span v-else class="doc-text">
                    {{ ev.nama }}
                  </span>
                </div>
              </template>
              <span v-else class="text-slate-400 italic">Tidak ada dokumen</span>
            </td>

            <!-- 7. Keterjadian -->
            <td>
              <div v-if="r.events && r.events.length" class="keterjadian-terjadi">
                <div class="status-terjadi">Risiko terjadi</div>
                <div
                  v-for="(e, eIdx) in r.events"
                  :key="eIdx"
                  class="sub-kejadian-item"
                >
                  {{ e.uraian_kejadian || e.dampak_kejadian || e.sebab_kejadian }}
                </div>
              </div>
              <div v-else class="keterjadian-nihil">
                Risiko tidak terjadi
              </div>
            </td>
          </tr>
        </template>

        <tr v-if="!groups.length">
          <td colspan="7" class="c py-6 text-slate-500">
            <template v-if="periode && periode !== 'tahunan'">
              Tidak ada Realisasi RTP yang dilaksanakan maupun Kejadian risiko pada {{ periodeLabel }} Tahun {{ tahun }}.
            </template>
            <template v-else>
              Belum ada data Realisasi RTP yang dilaksanakan maupun Kejadian risiko pada Tahun {{ tahun }}.
            </template>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="report-sign">
      <div class="box">
        Kota Tegal, {{ tahun }}<br />
        Kepala {{ opdName }}<br /><br /><br /><br />
        (...........................................)
      </div>
    </div>
  </section>
</template>

<style scoped>
.kode-tag {
  font-size: 0.75rem;
  font-weight: 700;
  color: #0369a1;
  margin-bottom: 2px;
}

.uraian-risiko-text {
  font-size: 0.85rem;
  line-height: 1.35;
}

.group-header {
  background: #f1f5f9;
  padding: 0.45rem 0.65rem;
}

.doc-item {
  font-size: 0.8rem;
  line-height: 1.35;
}

.doc-link {
  color: #0284c7;
  text-decoration: none;
}

.doc-link:hover {
  text-decoration: underline;
}

.status-terjadi {
  font-weight: 700;
  color: #b91c1c;
  font-size: 0.85rem;
  margin-bottom: 2px;
}

.sub-kejadian-item {
  font-size: 0.78rem;
  color: #334155;
  line-height: 1.3;
  margin-top: 2px;
  padding-left: 0.5rem;
  border-left: 2px solid #fca5a5;
}

.keterjadian-nihil {
  font-size: 0.85rem;
  color: #334155;
}
</style>

