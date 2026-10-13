<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

// Filter status: 'all', 'lengkap', 'sebagian', 'belum'
const statusFilter = ref('all')

const filteredItems = computed(() => {
  const q = props.searchQuery.trim().toLowerCase()
  return (props.data.items || []).filter((it) => {
    const matchSearch =
      !q ||
      it.nama_opd.toLowerCase().includes(q) ||
      (it.kode_opd && it.kode_opd.toLowerCase().includes(q))
    if (!matchSearch) return false

    if (statusFilter.value === 'lengkap') return it.status_kepatuhan === 'Lengkap'
    if (statusFilter.value === 'sebagian') return it.status_kepatuhan === 'Sebagian'
    if (statusFilter.value === 'belum') return it.status_kepatuhan === 'Belum Mengisi'
    return true
  })
})

const summary = computed(() => props.data.summary || {})

function statusBadgeClass(status) {
  if (status === 'Lengkap') return 'badge-lengkap'
  if (status === 'Sebagian') return 'badge-sebagian'
  return 'badge-belum'
}
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
        <div class="v text-emerald font-bold">
          {{ summary.lengkap || 0 }}
        </div>
        <div class="l">Lengkap (100% — 6 Tahap)</div>
      </div>
      <div class="stat">
        <div class="v text-amber font-bold">
          {{ summary.sebagian || 0 }}
        </div>
        <div class="l">Sebagian (Dalam Proses)</div>
      </div>
      <div class="stat">
        <div class="v text-rose font-bold">
          {{ summary.belum_mengisi || 0 }}
        </div>
        <div class="l">Belum Mengisi (0%)</div>
      </div>
      <div class="stat">
        <div class="v text-primary font-bold">
          {{ summary.rata_progres || 0 }}%
        </div>
        <div class="l">Rata-rata Progres Daerah</div>
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
            :class="{ active: statusFilter === 'lengkap' }"
            @click="statusFilter = 'lengkap'"
          >
            Lengkap ({{ summary.lengkap || 0 }})
          </button>
          <button
            type="button"
            :class="{ active: statusFilter === 'sebagian' }"
            @click="statusFilter = 'sebagian'"
          >
            Sebagian ({{ summary.sebagian || 0 }})
          </button>
          <button
            type="button"
            :class="{ active: statusFilter === 'belum' }"
            @click="statusFilter = 'belum'"
          >
            Belum ({{ summary.belum_mengisi || 0 }})
          </button>
        </div>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi Kepatuhan -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">PROGRES PENGISIAN MANAJEMEN RISIKO PER OPD</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <table class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 250px">Nama OPD</th>
            <th style="width: 105px">CEE (Form 1)</th>
            <th style="width: 110px">Konteks (Form 2)</th>
            <th style="width: 115px">Identifikasi (Form 3)</th>
            <th style="width: 105px">Analisis (Form 4)</th>
            <th style="width: 100px">RTP (Form 7)</th>
            <th style="width: 125px">Pemantauan (Form 8-10)</th>
            <th style="width: 130px">Progres (%)</th>
            <th style="width: 130px">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(it, idx) in filteredItems"
            :key="it.opd_id"
            :class="{ 'row-empty': it.persen_progres === 0 }"
          >
            <td class="c">{{ it.no || idx + 1 }}</td>
            <td class="opd-name-cell">
              <span class="nama-teks">{{ it.nama_opd }}</span>
              <span v-if="it.kode_opd" class="kode-sub">{{ it.kode_opd }}</span>
            </td>

            <!-- CEE (Form 1) -->
            <td class="c">
              <span v-if="it.cee_count > 0" class="step-badge step-done">
                <i class="pi pi-check text-xs"></i> Ada ({{ it.cee_count }})
              </span>
              <span v-else class="step-badge step-empty">Belum</span>
            </td>

            <!-- Konteks (Form 2) -->
            <td class="c">
              <span v-if="it.konteks_count > 0" class="step-badge step-done">
                <i class="pi pi-check text-xs"></i> Ada ({{ it.konteks_count }})
              </span>
              <span v-else class="step-badge step-empty">Belum</span>
            </td>

            <!-- Identifikasi (Form 3) -->
            <td class="c">
              <span v-if="it.identifikasi_count > 0" class="step-badge step-done">
                <i class="pi pi-check text-xs"></i> Ada ({{ it.identifikasi_count }})
              </span>
              <span v-else class="step-badge step-empty">Belum</span>
            </td>

            <!-- Analisis (Form 4) -->
            <td class="c">
              <span v-if="it.analisis_count > 0" class="step-badge step-done">
                <i class="pi pi-check text-xs"></i> Ada ({{ it.analisis_count }})
              </span>
              <span v-else class="step-badge step-empty">Belum</span>
            </td>

            <!-- RTP (Form 7) -->
            <td class="c">
              <span v-if="it.rtp_count > 0" class="step-badge step-done">
                <i class="pi pi-check text-xs"></i> Ada ({{ it.rtp_count }})
              </span>
              <span v-else class="step-badge step-empty">Belum</span>
            </td>

            <!-- Pemantauan (Form 8-10) -->
            <td class="c">
              <span v-if="it.pemantauan_count > 0" class="step-badge step-done">
                <i class="pi pi-check text-xs"></i> Ada ({{ it.pemantauan_count }})
              </span>
              <span v-else class="step-badge step-empty">Belum</span>
            </td>

            <!-- Progres Mini Bar -->
            <td class="c">
              <div class="progress-wrap">
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :style="{
                      width: `${it.persen_progres}%`,
                      backgroundColor:
                        it.persen_progres >= 100
                          ? '#10b981'
                          : it.persen_progres > 0
                          ? '#f59e0b'
                          : '#e2e8f0',
                    }"
                  ></div>
                </div>
                <span class="progress-val font-mono">{{ it.persen_progres }}%</span>
              </div>
            </td>

            <!-- Status Kepatuhan -->
            <td class="c">
              <span :class="['badge-status', statusBadgeClass(it.status_kepatuhan)]">
                {{ it.status_kepatuhan }}
              </span>
            </td>
          </tr>

          <tr v-if="!filteredItems.length">
            <td colspan="10" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan filter.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="8" class="font-bold c">
              RATA-RATA PROGRES KEPATUHAN DAERAH: {{ summary.rata_progres || 0 }}%
              <span class="text-muted font-normal ml-2">
                (Lengkap: {{ summary.lengkap || 0 }} OPD, Sebagian: {{ summary.sebagian || 0 }} OPD, Belum: {{ summary.belum_mengisi || 0 }} OPD)
              </span>
            </td>
            <td class="c font-bold font-mono text-primary">{{ summary.rata_progres || 0 }}%</td>
            <td class="c font-bold">
              <span :class="['badge-status', summary.rata_progres >= 100 ? 'badge-lengkap' : 'badge-sebagian']">
                {{ summary.rata_progres >= 100 ? 'Lengkap' : 'Sebagian' }}
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
}
.rekap-table th,
.rekap-table td {
  border: 1px solid #cbd5e1;
  padding: 8px 10px;
  vertical-align: middle;
}
.rekap-table thead th {
  background: #e2e8f0;
  color: #1e293b;
  font-weight: 600;
  text-align: center;
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
.step-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 6px;
  font-size: 0.76rem;
  font-weight: 600;
}
.step-done {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}
.step-empty {
  background: #f1f5f9;
  color: #94a3b8;
  border: 1px solid #e2e8f0;
}

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
.badge-lengkap {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}
.badge-sebagian {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fcd34d;
}
.badge-belum {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
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
