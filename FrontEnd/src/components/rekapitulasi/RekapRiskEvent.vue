<script setup>
import { computed, ref } from 'vue'
import { formatDate } from '@/utils/date'


const props = defineProps({
  data: { type: Object, default: () => ({ items: [], log_rows: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

// Toggle mode tampilan: 'rekap' (per OPD) atau 'log' (rincian kejadian)
const modeTampilan = ref('rekap')
// Filter status: 'all', 'ada', 'nihil'
const statusFilter = ref('all')

const filteredItems = computed(() => {
  const q = props.searchQuery.trim().toLowerCase()
  return (props.data.items || []).filter((it) => {
    const matchSearch =
      !q ||
      it.nama_opd.toLowerCase().includes(q) ||
      (it.kode_opd && it.kode_opd.toLowerCase().includes(q))
    if (!matchSearch) return false

    if (statusFilter.value === 'ada') return it.status === 'Ada Kejadian'
    if (statusFilter.value === 'nihil') return it.status === 'Nihil Kejadian'
    return true
  })
})

const filteredLogs = computed(() => {
  const q = props.searchQuery.trim().toLowerCase()
  if (!q) return props.data.log_rows || []
  return (props.data.log_rows || []).filter(
    (lr) =>
      lr.nama_opd.toLowerCase().includes(q) ||
      lr.kode_risiko.toLowerCase().includes(q) ||
      lr.uraian_risiko.toLowerCase().includes(q) ||
      lr.sebab_kejadian.toLowerCase().includes(q),
  )
})

const summary = computed(() => props.data.summary || {})
</script>

<template>
  <div class="rekap-subview">
    <!-- Stat Cards Header -->
    <div class="stat-grid no-print">
      <div class="stat">
        <div class="v">{{ summary.total_opd || 0 }}</div>
        <div class="l">Total OPD Terdaftar</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.total_risiko || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Risiko Teridentifikasi</div>
      </div>
      <div class="stat">
        <div class="v text-rose font-bold">
          {{ (summary.total_events || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">Total Kejadian Risiko (Events)</div>
      </div>
      <div class="stat">
        <div class="v text-amber font-bold">
          {{ summary.opd_ada_kejadian || 0 }}
        </div>
        <div class="l">OPD Melaporkan Kejadian</div>
      </div>
      <div class="stat">
        <div class="v text-emerald font-bold">
          {{ summary.opd_nihil_kejadian || 0 }}
        </div>
        <div class="l">OPD Nihil Kejadian</div>
      </div>
    </div>

    <!-- Table Subbar Controls -->
    <div class="table-subbar no-print">
      <div class="subbar-info">
        <span v-if="modeTampilan === 'rekap'" class="desc-text">
          Menampilkan <b>{{ filteredItems.length }}</b> dari <b>{{ (data.items || []).length }}</b> OPD
        </span>
        <span v-else class="desc-text">
          Menampilkan <b>{{ filteredLogs.length }}</b> dari <b>{{ (data.log_rows || []).length }}</b> Kejadian Tercatat
        </span>
      </div>
      <div class="subbar-controls">
        <span class="switch-label">Mode Tabel:</span>
        <div class="view-switch mr-2">
          <button
            type="button"
            :class="{ active: modeTampilan === 'rekap' }"
            @click="modeTampilan = 'rekap'"
          >
            Rekap per OPD
          </button>
          <button
            type="button"
            :class="{ active: modeTampilan === 'log' }"
            @click="modeTampilan = 'log'"
          >
            Rincian Log Kejadian ({{ (data.log_rows || []).length }})
          </button>
        </div>

        <template v-if="modeTampilan === 'rekap'">
          <span class="switch-label">Filter:</span>
          <div class="view-switch">
            <button
              type="button"
              :class="{ active: statusFilter === 'all' }"
              @click="statusFilter = 'all'"
            >
              Semua
            </button>
            <button
              type="button"
              :class="{ active: statusFilter === 'ada' }"
              @click="statusFilter = 'ada'"
            >
              Ada Kejadian ({{ summary.opd_ada_kejadian || 0 }})
            </button>
            <button
              type="button"
              :class="{ active: statusFilter === 'nihil' }"
              @click="statusFilter = 'nihil'"
            >
              Nihil ({{ summary.opd_nihil_kejadian || 0 }})
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi Keterjadian Risiko -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">REKAPITULASI KETERJADIAN RISIKO (RISK EVENT LOG) PER PERANGKAT DAERAH</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <!-- TAMPILAN 1: REKAP PER OPD -->
      <table v-if="modeTampilan === 'rekap'" class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 260px">Nama OPD</th>
            <th style="width: 140px">Total Risiko</th>
            <th style="width: 200px">Risiko Mengalami Kejadian</th>
            <th style="width: 180px">Total Kejadian (Events)</th>
            <th style="width: 150px">Status Keterjadian</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(it, idx) in filteredItems"
            :key="it.opd_id"
            :class="{ 'row-empty': it.total_risiko === 0 }"
          >
            <td class="c">{{ it.no || idx + 1 }}</td>
            <td class="opd-name-cell">
              <span class="nama-teks">{{ it.nama_opd }}</span>
              <span v-if="it.kode_opd" class="kode-sub">{{ it.kode_opd }}</span>
            </td>

            <!-- Total Risiko -->
            <td class="c font-mono">
              <span v-if="it.total_risiko > 0">{{ it.total_risiko }}</span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Risiko Terkena Kejadian -->
            <td class="c font-mono">
              <span v-if="it.risiko_terkena > 0" class="badge-count badge-rose">
                {{ it.risiko_terkena }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Total Events -->
            <td class="c font-mono font-bold">
              <span v-if="it.total_events > 0" class="badge-count badge-amber">
                {{ it.total_events }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Status Keterjadian -->
            <td class="c">
              <span
                :class="[
                  'badge-status',
                  it.total_events > 0 ? 'badge-ada' : 'badge-nihil',
                ]"
              >
                {{ it.status }}
              </span>
            </td>
          </tr>

          <tr v-if="!filteredItems.length">
            <td colspan="6" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan filter.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="2" class="font-bold c">TOTAL KESELURUHAN</td>
            <td class="c font-bold font-mono">{{ summary.total_risiko || 0 }}</td>
            <td class="c font-bold font-mono text-rose">{{ summary.total_risiko_terjadi || 0 }}</td>
            <td class="c font-bold font-mono text-amber">{{ summary.total_events || 0 }}</td>
            <td class="c font-bold">
              <span class="badge-status badge-neutral">
                {{ summary.opd_ada_kejadian || 0 }} OPD Ada Kejadian
              </span>
            </td>
          </tr>
        </tfoot>
      </table>

      <!-- TAMPILAN 2: RINCIAN LOG KEJADIAN (RISK EVENT DETAIL) -->
      <table v-else class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 200px">Nama OPD</th>
            <th style="width: 140px">Kode Risiko</th>
            <th style="text-align: left; min-width: 220px">Uraian Risiko</th>
            <th style="width: 100px">Tanggal</th>
            <th style="text-align: left; min-width: 180px">Sebab Kejadian</th>
            <th style="text-align: left; min-width: 180px">Dampak Kejadian</th>
            <th style="text-align: left; min-width: 180px">Realisasi RTP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lr in filteredLogs" :key="lr.no">
            <td class="c">{{ lr.no }}</td>
            <td>
              <div class="font-semibold">{{ lr.nama_opd }}</div>
              <div class="text-xs text-muted font-mono">{{ lr.kode_opd }}</div>
            </td>
            <td class="c font-mono font-medium">{{ lr.kode_risiko }}</td>
            <td>{{ lr.uraian_risiko }}</td>
            <td class="c font-mono">{{ formatDate(lr.tanggal_terjadi) }}</td>
            <td>{{ lr.sebab_kejadian }}</td>
            <td>{{ lr.dampak_kejadian }}</td>
            <td>{{ lr.realisasi_rtp }}</td>
          </tr>

          <tr v-if="!filteredLogs.length">
            <td colspan="8" class="c py-5 text-muted">
              <i class="pi pi-info-circle mr-1"></i>
              Belum ada pencatatan kejadian risiko (risk event) pada Form 10 untuk tahun penilaian ini.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.rekap-subview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.text-rose { color: #ef4444; }
.text-amber { color: #f59e0b; }
.text-emerald { color: #10b981; }

.table-subbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--surface-2, #f8fafc);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: var(--radius-sm, 8px);
}
.subbar-info {
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
}
.subbar-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
.switch-label {
  font-size: 0.8rem;
  color: var(--text-muted, #64748b);
  font-weight: 500;
}
.view-switch {
  display: flex;
  background: #e2e8f0;
  border-radius: 6px;
  padding: 2px;
}
.view-switch button {
  border: none;
  background: transparent;
  padding: 4px 10px;
  font-size: 0.78rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  color: var(--text, #334155);
  transition: all 0.15s ease;
}
.view-switch button.active {
  background: #fff;
  color: var(--primary, #4f46e5);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.report-sheet-inner {
  background: #fff;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: var(--radius, 12px);
  padding: 20px;
  box-shadow: var(--shadow-xs, 0 1px 2px rgba(0,0,0,0.05));
  overflow-x: auto;
}
.print-kop {
  margin-bottom: 16px;
  text-align: center;
}
.rekap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
  border: 1px solid #e2e8f0;
}
.rekap-table th,
.rekap-table td {
  border: 1px solid #e2e8f0;
  padding: 8px 10px;
  vertical-align: middle;
}
.rekap-table thead th {
  background: #f8fafc;
  color: #1e293b;
  font-weight: 600;
  text-align: center;
  border: 1px solid #e2e8f0;
}
.rekap-table tbody tr:nth-child(even) {
  background-color: #f8fafc;
}
.rekap-table tbody tr:nth-child(odd) {
  background-color: #ffffff;
}
.rekap-table tbody tr:hover {
  background-color: #f1f5f9;
}
.opd-name-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nama-teks {
  font-weight: 600;
  color: #1e293b;
}
.kode-sub {
  font-size: 0.72rem;
  color: #64748b;
  font-family: monospace;
}

.badge-count {
  display: inline-block;
  min-width: 24px;
  padding: 2px 7px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.82rem;
}
.badge-rose { background: #fee2e2; color: #b91c1c; }
.badge-amber { background: #fef3c7; color: #b45309; }

.badge-status {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
}
.badge-ada {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}
.badge-nihil {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}
.badge-neutral {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.row-empty {
  opacity: 0.7;
  background: #fafafa;
}
.tr-total td {
  background: #f1f5f9;
  font-weight: 700;
  color: #0f172a;
  border-top: 2px solid #64748b;
}
.font-mono {
  font-family: monospace;
}
.font-bold {
  font-weight: 700;
}
.mr-2 {
  margin-right: 0.5rem;
}
</style>
