<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

// Filter status: 'all', 'selesai', 'proses', 'belum'
const statusFilter = ref('all')

const filteredItems = computed(() => {
  const q = props.searchQuery.trim().toLowerCase()
  return (props.data.items || []).filter((it) => {
    const matchSearch =
      !q ||
      it.nama_opd.toLowerCase().includes(q) ||
      (it.kode_opd && it.kode_opd.toLowerCase().includes(q))
    if (!matchSearch) return false

    if (statusFilter.value === 'selesai') return it.status_tindak_lanjut === 'Selesai 100%'
    if (statusFilter.value === 'proses') return it.status_tindak_lanjut === 'Dalam Proses'
    if (statusFilter.value === 'belum') return it.status_tindak_lanjut === 'Belum Terealisasi'
    return true
  })
})

const summary = computed(() => props.data.summary || {})

function statusBadgeClass(status) {
  if (status === 'Selesai 100%') return 'badge-selesai'
  if (status === 'Dalam Proses') return 'badge-proses'
  if (status === 'Belum Terealisasi') return 'badge-belum'
  return 'badge-neutral'
}
</script>

<template>
  <div class="rekap-subview">
    <!-- Stat Cards Header -->
    <div class="stat-grid no-print">
      <div class="stat">
        <div class="v">{{ (summary.total_risiko || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Risiko Teridentifikasi</div>
      </div>
      <div class="stat">
        <div class="v text-rose font-bold">
          {{ (summary.total_prioritas || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">Risiko Prioritas (Hasil Penilaian)</div>
      </div>
      <div class="stat">
        <div class="v text-primary font-bold">
          {{ (summary.total_target_rtp || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">Target RTP Direncanakan</div>
      </div>
      <div class="stat">
        <div class="v text-emerald font-bold">
          {{ (summary.total_realisasi_selesai || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">RTP Selesai Direalisasikan</div>
      </div>
      <div class="stat">
        <div class="v text-amber font-bold">
          {{ (summary.total_dalam_proses || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">RTP Dalam Proses / Belum</div>
      </div>
      <div class="stat">
        <div class="v text-primary font-bold">
          {{ summary.tingkat_realisasi_daerah || 0 }}%
        </div>
        <div class="l">Tingkat Realisasi Daerah</div>
      </div>
    </div>

    <!-- Table Subbar Controls -->
    <div class="table-subbar no-print">
      <div class="subbar-info">
        <span class="desc-text">
          Menampilkan <b>{{ filteredItems.length }}</b> dari <b>{{ (data.items || []).length }}</b> OPD
        </span>
      </div>
      <div class="subbar-controls">
        <span class="switch-label">Filter Status:</span>
        <div class="view-switch">
          <button
            type="button"
            :class="{ active: statusFilter === 'all' }"
            @click="statusFilter = 'all'"
          >
            Semua ({{ (data.items || []).length }})
          </button>
          <button
            type="button"
            :class="{ active: statusFilter === 'selesai' }"
            @click="statusFilter = 'selesai'"
          >
            Selesai 100% ({{ summary.opd_selesai || 0 }})
          </button>
          <button
            type="button"
            :class="{ active: statusFilter === 'proses' }"
            @click="statusFilter = 'proses'"
          >
            Dalam Proses ({{ summary.opd_proses || 0 }})
          </button>
          <button
            type="button"
            :class="{ active: statusFilter === 'belum' }"
            @click="statusFilter = 'belum'"
          >
            Belum ({{ summary.opd_belum || 0 }})
          </button>
        </div>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi Realisasi RTP -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">REKAPITULASI REALISASI RENCANA TINDAK PENGENDALIAN (RTP) PER OPD</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <table class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 250px">Nama OPD</th>
            <th style="width: 100px">Total Risiko</th>
            <th style="width: 110px">Risiko Prioritas</th>
            <th style="width: 105px">Target RTP</th>
            <th style="width: 120px">Realisasi Selesai</th>
            <th style="width: 125px">Dalam Proses / Belum</th>
            <th style="width: 135px">Tingkat Realisasi (%)</th>
            <th style="width: 140px">Status Tindak Lanjut</th>
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

            <!-- Risiko Prioritas -->
            <td class="c font-mono">
              <span v-if="it.risiko_prioritas > 0" class="badge-count badge-rose">
                {{ it.risiko_prioritas }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Target RTP -->
            <td class="c font-mono">
              <span v-if="it.target_rtp > 0" class="badge-count badge-blue">
                {{ it.target_rtp }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Realisasi Selesai -->
            <td class="c font-mono">
              <span v-if="it.realisasi_selesai > 0" class="badge-count badge-emerald">
                {{ it.realisasi_selesai }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Dalam Proses / Belum -->
            <td class="c font-mono">
              <span v-if="it.dalam_proses > 0" class="badge-count badge-amber">
                {{ it.dalam_proses }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Tingkat Realisasi (%) Mini Progress -->
            <td class="c">
              <div v-if="it.target_rtp > 0" class="progress-wrap">
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :style="{
                      width: `${it.tingkat_realisasi}%`,
                      backgroundColor:
                        it.tingkat_realisasi >= 100
                          ? '#10b981'
                          : it.tingkat_realisasi > 0
                          ? '#3b82f6'
                          : '#e2e8f0',
                    }"
                  ></div>
                </div>
                <span class="progress-val font-mono">{{ it.tingkat_realisasi }}%</span>
              </div>
              <span v-else class="text-faint">-</span>
            </td>

            <!-- Status Tindak Lanjut -->
            <td class="c">
              <span :class="['badge-status', statusBadgeClass(it.status_tindak_lanjut)]">
                {{ it.status_tindak_lanjut }}
              </span>
            </td>
          </tr>

          <tr v-if="!filteredItems.length">
            <td colspan="9" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan filter.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="2" class="font-bold c">TOTAL KESELURUHAN</td>
            <td class="c font-bold font-mono">{{ summary.total_risiko || 0 }}</td>
            <td class="c font-bold font-mono text-rose">{{ summary.total_prioritas || 0 }}</td>
            <td class="c font-bold font-mono text-primary">{{ summary.total_target_rtp || 0 }}</td>
            <td class="c font-bold font-mono text-emerald">{{ summary.total_realisasi_selesai || 0 }}</td>
            <td class="c font-bold font-mono text-amber">{{ summary.total_dalam_proses || 0 }}</td>
            <td class="c font-bold font-mono text-primary">{{ summary.tingkat_realisasi_daerah || 0 }}%</td>
            <td class="c font-bold">
              <span class="badge-status badge-proses">
                {{ summary.tingkat_realisasi_daerah || 0 }}% Terealisasi
              </span>
            </td>
          </tr>
        </tfoot>
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
.text-primary { color: var(--primary, #4f46e5); }

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
.badge-blue { background: #e0e7ff; color: #3730a3; }
.badge-emerald { background: #d1fae5; color: #047857; }
.badge-amber { background: #fef3c7; color: #b45309; }

.progress-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.progress-track {
  flex: 1;
  height: 7px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}
.progress-val {
  font-size: 0.78rem;
  font-weight: 700;
  min-width: 44px;
  text-align: right;
}

.badge-status {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
}
.badge-selesai {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}
.badge-proses {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fcd34d;
}
.badge-belum {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}
.badge-neutral {
  background: #f1f5f9;
  color: #64748b;
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
</style>
