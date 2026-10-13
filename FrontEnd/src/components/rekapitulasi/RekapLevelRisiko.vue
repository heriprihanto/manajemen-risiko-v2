<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [], rows: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

// Toggle mode tampilan: 'matriks' (kolom level risiko) atau 'rincian' (baris per level)
const modeTampilan = ref('matriks')

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
const prioritasCount = computed(
  () => (summary.value.sangat_tinggi || 0) + (summary.value.tinggi || 0),
)
</script>

<template>
  <div class="rekap-subview">
    <!-- Stat Cards Header -->
    <div class="stat-grid no-print">
      <div class="stat">
        <div class="v">{{ (summary.grand_total || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Risiko Teridentifikasi</div>
      </div>
      <div class="stat">
        <div class="v text-rose">
          {{ (summary.sangat_tinggi || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">Sangat Tinggi (5) — Merah</div>
      </div>
      <div class="stat">
        <div class="v text-orange">
          {{ (summary.tinggi || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">Tinggi (4) — Oranye</div>
      </div>
      <div class="stat">
        <div class="v text-amber">
          {{ (summary.sedang || 0).toLocaleString('id-ID') }}
        </div>
        <div class="l">Sedang (3) — Kuning</div>
      </div>
      <div class="stat">
        <div class="v text-emerald">
          {{ ((summary.rendah || 0) + (summary.sangat_rendah || 0)).toLocaleString('id-ID') }}
        </div>
        <div class="l">Rendah & Sangat Rendah</div>
      </div>
      <div class="stat">
        <div class="v text-danger font-bold">
          {{ prioritasCount.toLocaleString('id-ID') }}
        </div>
        <div class="l">Risiko Prioritas Penanganan</div>
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
        <span class="switch-label">Mode Tabel:</span>
        <div class="view-switch">
          <button
            type="button"
            :class="{ active: modeTampilan === 'matriks' }"
            @click="modeTampilan = 'matriks'"
            title="Tampilan Matriks: Kolom Level Risiko (Sangat Tinggi s.d Sangat Rendah)"
          >
            Matriks Level (Kolom)
          </button>
          <button
            type="button"
            :class="{ active: modeTampilan === 'rincian' }"
            @click="modeTampilan = 'rincian'"
            title="Tampilan Rincian: Baris per Level Risiko"
          >
            Rincian per Level (Baris)
          </button>
        </div>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi Level Risiko -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">REKAPITULASI IDENTIFIKASI & ANALISIS RISIKO (LEVEL RISIKO) PER OPD</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <!-- MODE 1: MATRIKS KOLOM 5 LEVEL RISIKO -->
      <table v-if="modeTampilan === 'matriks'" class="rpt rekap-table">
        <thead>
          <tr>
            <th rowspan="2" style="width: 44px">No</th>
            <th rowspan="2" style="text-align: left; min-width: 260px">Nama OPD</th>
            <th colspan="6" class="c group-header">Level Risiko</th>
            <th rowspan="2" style="width: 100px">Total Risiko</th>
          </tr>
          <tr>
            <th style="width: 110px" class="th-level th-st">Sangat Tinggi (5)</th>
            <th style="width: 95px" class="th-level th-t">Tinggi (4)</th>
            <th style="width: 95px" class="th-level th-sd">Sedang (3)</th>
            <th style="width: 95px" class="th-level th-r">Rendah (2)</th>
            <th style="width: 115px" class="th-level th-sr">Sangat Rendah (1)</th>
            <th style="width: 115px" class="th-level th-ba">Belum Dianalisis</th>
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

            <!-- Sangat Tinggi (5) -->
            <td class="c font-mono">
              <span v-if="it.sangat_tinggi > 0" class="badge-level badge-st">
                {{ it.sangat_tinggi }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Tinggi (4) -->
            <td class="c font-mono">
              <span v-if="it.tinggi > 0" class="badge-level badge-t">
                {{ it.tinggi }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Sedang (3) -->
            <td class="c font-mono">
              <span v-if="it.sedang > 0" class="badge-level badge-sd">
                {{ it.sedang }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Rendah (2) -->
            <td class="c font-mono">
              <span v-if="it.rendah > 0" class="badge-level badge-r">
                {{ it.rendah }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Sangat Rendah (1) -->
            <td class="c font-mono">
              <span v-if="it.sangat_rendah > 0" class="badge-level badge-sr">
                {{ it.sangat_rendah }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Belum Dianalisis -->
            <td class="c font-mono">
              <span v-if="it.belum_analisis > 0" class="badge-level badge-ba">
                {{ it.belum_analisis }}
              </span>
              <span v-else class="text-faint">0</span>
            </td>

            <!-- Total Risiko -->
            <td class="c font-bold font-mono">
              <span v-if="it.total_risiko > 0">{{ it.total_risiko }}</span>
              <span v-else class="text-faint">0</span>
            </td>
          </tr>

          <tr v-if="!filteredItems.length">
            <td colspan="9" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan pencarian.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="2" class="font-bold c">TOTAL KESELURUHAN</td>
            <td class="c font-bold font-mono text-st">{{ summary.sangat_tinggi || 0 }}</td>
            <td class="c font-bold font-mono text-t">{{ summary.tinggi || 0 }}</td>
            <td class="c font-bold font-mono text-sd">{{ summary.sedang || 0 }}</td>
            <td class="c font-bold font-mono text-r">{{ summary.rendah || 0 }}</td>
            <td class="c font-bold font-mono text-sr">{{ summary.sangat_rendah || 0 }}</td>
            <td class="c font-bold font-mono text-ba">{{ summary.belum_analisis || 0 }}</td>
            <td class="c font-bold font-mono text-primary">{{ summary.grand_total || 0 }}</td>
          </tr>
        </tfoot>
      </table>

      <!-- MODE 2: RINCIAN BARIS PER LEVEL RISIKO -->
      <table v-else class="rpt rekap-table">
        <thead>
          <tr>
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 260px">Nama OPD</th>
            <th style="text-align: left; min-width: 220px">Level Risiko</th>
            <th style="width: 130px">Jumlah Risiko</th>
            <th style="width: 110px">Persentase</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(it, idx) in filteredItems" :key="it.opd_id">
            <tr
              v-for="(lvl, lIdx) in [
                { k: 'st', label: 'Sangat Tinggi (5)', count: it.sangat_tinggi },
                { k: 't', label: 'Tinggi (4)', count: it.tinggi },
                { k: 'sd', label: 'Sedang (3)', count: it.sedang },
                { k: 'r', label: 'Rendah (2)', count: it.rendah },
                { k: 'sr', label: 'Sangat Rendah (1)', count: it.sangat_rendah },
                { k: 'ba', label: 'Belum Dianalisis', count: it.belum_analisis },
              ].filter(x => it.total_risiko === 0 ? x.k === 'ba' : x.count > 0)"
              :key="lvl.k + lIdx"
            >
              <td v-if="lIdx === 0" class="c">
                {{ it.no || idx + 1 }}
              </td>
              <td v-if="lIdx === 0" class="opd-name-cell">
                <span class="nama-teks">{{ it.nama_opd }}</span>
                <span v-if="it.kode_opd" class="kode-sub">{{ it.kode_opd }}</span>
                <div v-if="it.total_risiko > 0" class="subtotal-pill no-print">
                  Total: <b>{{ it.total_risiko }}</b> risiko
                </div>
              </td>
              <td>
                <span :class="['badge-level', `badge-${lvl.k}`]">
                  {{ lvl.label }}
                </span>
              </td>
              <td class="c font-mono font-bold">{{ lvl.count }}</td>
              <td class="c font-mono">
                {{ it.total_risiko ? Math.round((lvl.count / it.total_risiko) * 100) : 0 }}%
              </td>
            </tr>
          </template>

          <tr v-if="!filteredItems.length">
            <td colspan="5" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan pencarian.
            </td>
          </tr>
        </tbody>
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="3" class="font-bold c">TOTAL RISIKO KESELURUHAN</td>
            <td class="c font-bold font-mono text-primary">{{ summary.grand_total || 0 }}</td>
            <td class="c font-bold font-mono">100%</td>
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
.text-orange { color: #f97316; }
.text-amber { color: #eab308; }
.text-emerald { color: #10b981; }
.text-danger { color: #b91c1c; }

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
  padding: 7px 10px;
  vertical-align: middle;
}
.rekap-table thead th {
  background: #e2e8f0;
  color: #1e293b;
  font-weight: 600;
  text-align: center;
}
.rekap-table thead th.group-header {
  background: #f1f5f9;
  color: #0f172a;
}
.th-level {
  font-size: 0.76rem;
  font-weight: 600;
}
.th-st { background: #fee2e2 !important; color: #991b1b !important; }
.th-t { background: #ffedd5 !important; color: #9a3412 !important; }
.th-sd { background: #fef9c3 !important; color: #854d0e !important; }
.th-r { background: #dcfce7 !important; color: #166534 !important; }
.th-sr { background: #d1fae5 !important; color: #065f46 !important; }
.th-ba { background: #f1f5f9 !important; color: #475569 !important; }

.badge-level {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.8rem;
}
.badge-st { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.badge-t { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.badge-sd { background: #fef9c3; color: #a16207; border: 1px solid #fde047; }
.badge-r { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.badge-sr { background: #d1fae5; color: #047857; border: 1px solid #6ee7b7; }
.badge-ba { background: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; }

.text-st { color: #b91c1c; }
.text-t { color: #c2410c; }
.text-sd { color: #a16207; }
.text-r { color: #15803d; }
.text-sr { color: #047857; }
.text-ba { color: #64748b; }

.opd-name-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
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
  margin-top: 2px;
  width: fit-content;
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
