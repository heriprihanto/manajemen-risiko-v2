<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [], rows: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

const filteredItems = computed(() => {
  const q = props.searchQuery.trim().toLowerCase()
  if (!q) return props.data.items || []
  return (props.data.items || []).filter(
    (it) =>
      it.nama_opd.toLowerCase().includes(q) ||
      (it.kode_opd && it.kode_opd.toLowerCase().includes(q)) ||
      (it.kategori_list || []).some((k) =>
        k.kategori_risiko.toLowerCase().includes(q),
      ),
  )
})

const summary = computed(() => props.data.summary || {})
const topKategori = computed(() => {
  const list = summary.value.by_kategori || []
  return list.length ? list[0].kategori_risiko : '-'
})
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
        <div class="l">OPD Teridentifikasi Risiko</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.total_strategis_opd || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Risiko Strategis OPD</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.total_operasional_opd || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Risiko Operasional OPD</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.grand_total || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Grand Total Risiko</div>
      </div>
    </div>

    <!-- Table Subbar Info -->
    <div class="table-subbar no-print">
      <div class="subbar-info">
        <span class="desc-text">
          Menampilkan <b>{{ filteredItems.length }}</b> dari <b>{{ (data.items || []).length }}</b> OPD
          <span v-if="topKategori !== '-'" class="ml-2 muted">
            | Kategori Terbanyak: <b>{{ topKategori }}</b>
          </span>
        </span>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi Identifikasi -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">REKAPITULASI IDENTIFIKASI RISIKO (KATEGORI RISIKO) PER PERANGKAT DAERAH</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <table class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 250px">Nama OPD</th>
            <th style="text-align: left; min-width: 200px">Kategori Risiko</th>
            <th style="width: 130px">Strategis OPD</th>
            <th style="width: 130px">Operasional OPD</th>
            <th style="width: 110px">Total</th>
          </tr>
        </thead>
        <tbody>
          <!-- Gunakan template per OPD untuk rowspan rapi -->
          <template v-for="(it, idx) in filteredItems" :key="it.opd_id">
            <tr
              v-for="(cat, cIdx) in it.kategori_list"
              :key="cat.kategori_risiko + cIdx"
              :class="{
                'row-empty': it.total_risiko === 0,
                'row-border-bottom': cIdx === it.kategori_list.length - 1,
              }"
            >
              <!-- Sel No & Nama OPD di-rowspan sebanyak kategori pada OPD tersebut -->
              <td
                v-if="cIdx === 0"
                :rowspan="it.kategori_list.length"
                class="c"
              >
                {{ it.no || idx + 1 }}
              </td>
              <td
                v-if="cIdx === 0"
                :rowspan="it.kategori_list.length"
                class="opd-name-cell"
              >
                <span class="nama-teks">{{ it.nama_opd }}</span>
                <span v-if="it.kode_opd" class="kode-sub">{{ it.kode_opd }}</span>
                <div v-if="it.total_risiko > 0" class="subtotal-pill no-print">
                  Total OPD: <b>{{ it.total_risiko }}</b>
                </div>
              </td>

              <!-- Kategori Risiko -->
              <td class="cat-cell">
                <span v-if="cat.kategori_risiko !== '-'" class="cat-name">
                  {{ cat.kategori_risiko }}
                </span>
                <span v-else class="text-faint">-</span>
              </td>

              <!-- Strategis OPD -->
              <td class="c font-mono">
                <span v-if="cat.strategis_opd > 0" class="badge-count badge-blue">
                  {{ cat.strategis_opd }}
                </span>
                <span v-else class="text-faint">0</span>
              </td>

              <!-- Operasional OPD -->
              <td class="c font-mono">
                <span v-if="cat.operasional_opd > 0" class="badge-count badge-emerald">
                  {{ cat.operasional_opd }}
                </span>
                <span v-else class="text-faint">0</span>
              </td>

              <!-- Total Kategori -->
              <td class="c font-bold font-mono">
                <span v-if="cat.total > 0">{{ cat.total }}</span>
                <span v-else class="text-faint">0</span>
              </td>
            </tr>
          </template>

          <tr v-if="!filteredItems.length">
            <td colspan="6" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan pencarian.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="3" class="font-bold c">TOTAL KESELURUHAN</td>
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
  padding: 7px 10px;
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
  gap: 3px;
  background: #fdfdfe;
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
.subtotal-pill {
  font-size: 0.7rem;
  color: #4338ca;
  background: #eef2ff;
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  margin-top: 3px;
  width: fit-content;
}
.cat-cell {
  vertical-align: middle;
}
.cat-name {
  font-weight: 500;
  color: #334155;
}
.row-empty {
  opacity: 0.7;
  background: #fafafa;
}
.row-border-bottom td {
  border-bottom: 2px solid #cbd5e1;
}
.tr-total td {
  background: #f1f5f9;
  font-weight: 700;
  color: #0f172a;
  border-top: 2px solid #64748b;
}
.badge-count {
  display: inline-block;
  min-width: 24px;
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.82rem;
}
.badge-blue {
  background: #e0e7ff;
  color: #3730a3;
}
.badge-emerald {
  background: #d1fae5;
  color: #065f46;
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
