<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

const filteredItems = computed(() => {
  const q = props.searchQuery.trim().toLowerCase()
  if (!q) return props.data.items || []
  return (props.data.items || []).filter(
    (it) =>
      it.nama_opd.toLowerCase().includes(q) ||
      (it.kode_opd && it.kode_opd.toLowerCase().includes(q)),
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
        <div class="v">{{ summary.opd_mengisi || 0 }}</div>
        <div class="l">OPD Telah Menetapkan Konteks</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.total_strategis_opd || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Konteks Strategis OPD</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.total_operasional_opd || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Konteks Operasional OPD</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.grand_total || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Grand Total Konteks Risiko</div>
      </div>
    </div>

    <!-- Table Subbar Info -->
    <div class="table-subbar no-print">
      <div class="subbar-info">
        <span class="desc-text">
          Menampilkan <b>{{ filteredItems.length }}</b> dari <b>{{ (data.items || []).length }}</b> OPD
        </span>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi Konteks -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">REKAPITULASI PENETAPAN KONTEKS RISIKO PER PERANGKAT DAERAH</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <table class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 260px">Nama OPD</th>
            <th style="width: 220px">Jumlah Konteks Risiko Strategis OPD</th>
            <th style="width: 220px">Jumlah Konteks Risiko Operasional OPD</th>
            <th style="width: 130px">Total Konteks</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(it, idx) in filteredItems"
            :key="it.opd_id"
            :class="{ 'row-empty': it.total_konteks === 0 }"
          >
            <td class="c">{{ it.no || idx + 1 }}</td>
            <td class="opd-name-cell">
              <span class="nama-teks">{{ it.nama_opd }}</span>
              <span v-if="it.kode_opd" class="kode-sub">{{ it.kode_opd }}</span>
            </td>
            <td class="c font-bold font-mono">
              <span v-if="it.jumlah_strategis_opd > 0" class="badge-count badge-blue">
                {{ it.jumlah_strategis_opd }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>
            <td class="c font-bold font-mono">
              <span v-if="it.jumlah_operasional_opd > 0" class="badge-count badge-emerald">
                {{ it.jumlah_operasional_opd }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>
            <td class="c font-bold font-mono">
              <span v-if="it.total_konteks > 0" class="badge-count badge-total">
                {{ it.total_konteks }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>
          </tr>

          <tr v-if="!filteredItems.length">
            <td colspan="5" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan pencarian.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="2" class="font-bold c">TOTAL KESELURUHAN</td>
            <td class="c font-bold font-mono">{{ summary.total_strategis_opd || 0 }}</td>
            <td class="c font-bold font-mono">{{ summary.total_operasional_opd || 0 }}</td>
            <td class="c font-bold font-mono text-primary">{{ summary.grand_total || 0 }}</td>
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
  padding: 8px 12px;
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
.badge-count {
  display: inline-block;
  min-width: 28px;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.84rem;
}
.badge-blue {
  background: #e0e7ff;
  color: #3730a3;
}
.badge-emerald {
  background: #d1fae5;
  color: #065f46;
}
.badge-total {
  background: #ede9fe;
  color: #5b21b6;
}
.text-primary {
  color: var(--primary, #4f46e5);
}
.font-mono {
  font-family: monospace;
}
.font-bold {
  font-weight: 700;
}
</style>
