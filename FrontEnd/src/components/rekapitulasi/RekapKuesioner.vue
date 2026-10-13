<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [], summary: {} }) },
  searchQuery: { type: String, default: '' },
  tahun: [Number, String],
})

// Toggle mode tampilan: 'lengkap' (termasuk distribusi nilai 1..4) atau 'ringkas'
const modeTampilan = ref('lengkap')

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

function simpulanBadgeClass(simp) {
  if (simp === 'Memadai') return 'badge-memadai'
  if (simp === 'Kurang Memadai') return 'badge-kurang'
  return 'badge-neutral'
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
        <div class="v">{{ summary.opd_mengisi || 0 }}</div>
        <div class="l">OPD Telah Mengisi CEE</div>
      </div>
      <div class="stat">
        <div class="v">{{ (summary.total_responden || 0).toLocaleString('id-ID') }}</div>
        <div class="l">Total Responden</div>
      </div>
      <div class="stat">
        <div class="v">
          <span class="badge-modus">{{ summary.modus ?? '-' }}</span>
        </div>
        <div class="l">Modus Gabungan Daerah</div>
      </div>
      <div class="stat">
        <div class="v">
          <span :class="['badge-status', simpulanBadgeClass(summary.simpulan)]">
            {{ summary.simpulan || '-' }}
          </span>
        </div>
        <div class="l">Simpulan Gabungan Daerah</div>
      </div>
    </div>

    <!-- Toolbar Opsi Tampilan & Info -->
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
            :class="{ active: modeTampilan === 'ringkas' }"
            @click="modeTampilan = 'ringkas'"
            title="Tampilan Standar: No | Nama OPD | Jumlah Responden | Modus | Simpulan"
          >
            Ringkas (5 Kolom)
          </button>
          <button
            type="button"
            :class="{ active: modeTampilan === 'lengkap' }"
            @click="modeTampilan = 'lengkap'"
            title="Tampilan Lengkap: Termasuk distribusi nilai jawaban 1, 2, 3, 4 dan persentase"
          >
            Lengkap (+ Distribusi Nilai & %)
          </button>
        </div>
      </div>
    </div>

    <!-- Lembar Laporan / Tabel Rekapitulasi -->
    <div class="report-sheet-inner">
      <div class="print-kop">
        <div class="report-title">REKAPITULASI HASIL KUESIONER CEE PER PERANGKAT DAERAH</div>
        <div class="report-subtitle">Tahun Penilaian: {{ tahun }}</div>
      </div>

      <table class="rpt rekap-table">
        <thead>
          <tr v-if="modeTampilan === 'lengkap'">
            <th rowspan="2" style="width: 44px">No</th>
            <th rowspan="2" style="text-align: left; min-width: 260px">Nama OPD</th>
            <th rowspan="2" style="width: 100px">Jumlah Responden</th>
            <th colspan="4" class="c group-header">Distribusi Jawaban Responden (Nilai & %)</th>
            <th rowspan="2" style="width: 80px">Modus</th>
            <th rowspan="2" style="width: 120px">Simpulan</th>
          </tr>
          <tr v-if="modeTampilan === 'lengkap'">
            <th style="width: 90px">Nilai 1</th>
            <th style="width: 90px">Nilai 2</th>
            <th style="width: 90px">Nilai 3</th>
            <th style="width: 90px">Nilai 4</th>
          </tr>

          <!-- Mode Ringkas persis sesuai prompt: No | Nama OPD | Jumlah Responden | Modus | Simpulan -->
          <tr v-if="modeTampilan === 'ringkas'">
            <th style="width: 44px">No</th>
            <th style="text-align: left; min-width: 280px">Nama OPD</th>
            <th style="width: 130px">Jumlah Responden</th>
            <th style="width: 90px">Modus</th>
            <th style="width: 130px">Simpulan</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(it, idx) in filteredItems" :key="it.opd_id" :class="{ 'row-empty': it.jumlah_responden === 0 }">
            <td class="c">{{ it.no || idx + 1 }}</td>
            <td class="opd-name-cell">
              <span class="nama-teks">{{ it.nama_opd }}</span>
              <span v-if="it.kode_opd" class="kode-sub">{{ it.kode_opd }}</span>
            </td>
            <td class="c font-bold">{{ it.jumlah_responden }}</td>

            <!-- Kolom Distribusi (Jika Mode Lengkap) -->
            <template v-if="modeTampilan === 'lengkap'">
              <td class="c font-mono">
                <span v-if="it.total_jawaban">
                  {{ it.nilai_1 }} <small class="text-muted">({{ it.persen_1 }}%)</small>
                </span>
                <span v-else class="text-faint">-</span>
              </td>
              <td class="c font-mono">
                <span v-if="it.total_jawaban">
                  {{ it.nilai_2 }} <small class="text-muted">({{ it.persen_2 }}%)</small>
                </span>
                <span v-else class="text-faint">-</span>
              </td>
              <td class="c font-mono font-medium">
                <span v-if="it.total_jawaban">
                  {{ it.nilai_3 }} <small class="text-muted">({{ it.persen_3 }}%)</small>
                </span>
                <span v-else class="text-faint">-</span>
              </td>
              <td class="c font-mono font-medium">
                <span v-if="it.total_jawaban">
                  {{ it.nilai_4 }} <small class="text-muted">({{ it.persen_4 }}%)</small>
                </span>
                <span v-else class="text-faint">-</span>
              </td>
            </template>

            <td class="c font-bold">
              <span v-if="it.modus !== null" class="badge-modus-sm">{{ it.modus }}</span>
              <span v-else class="text-faint">-</span>
            </td>
            <td class="c">
              <span :class="['badge-status', simpulanBadgeClass(it.simpulan)]">
                {{ it.simpulan }}
              </span>
            </td>
          </tr>

          <tr v-if="!filteredItems.length">
            <td :colspan="modeTampilan === 'lengkap' ? 9 : 5" class="c py-4 text-muted">
              Tidak ada data OPD yang sesuai dengan pencarian.
            </td>
          </tr>
        </tbody>

        <!-- Baris Total Footer -->
        <tfoot v-if="filteredItems.length">
          <tr class="tr-total">
            <td colspan="2" class="font-bold c">TOTAL KESELURUHAN</td>
            <td class="c font-bold">{{ summary.total_responden || 0 }}</td>

            <template v-if="modeTampilan === 'lengkap'">
              <td class="c font-bold font-mono">
                {{ summary.nilai_1 || 0 }} <small class="text-muted">({{ summary.persen_1 || 0 }}%)</small>
              </td>
              <td class="c font-bold font-mono">
                {{ summary.nilai_2 || 0 }} <small class="text-muted">({{ summary.persen_2 || 0 }}%)</small>
              </td>
              <td class="c font-bold font-mono">
                {{ summary.nilai_3 || 0 }} <small class="text-muted">({{ summary.persen_3 || 0 }}%)</small>
              </td>
              <td class="c font-bold font-mono">
                {{ summary.nilai_4 || 0 }} <small class="text-muted">({{ summary.persen_4 || 0 }}%)</small>
              </td>
            </template>

            <td class="c font-bold">
              <span class="badge-modus-sm">{{ summary.modus ?? '-' }}</span>
            </td>
            <td class="c font-bold">
              <span :class="['badge-status', simpulanBadgeClass(summary.simpulan)]">
                {{ summary.simpulan || '-' }}
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
.rekap-table thead th.group-header {
  background: #dbeafe;
  color: #1e40af;
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
.badge-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 600;
}
.badge-memadai {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}
.badge-kurang {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}
.badge-neutral {
  color: #64748b;
}
.badge-modus {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: var(--primary-soft, #eef2ff);
  color: var(--primary, #4f46e5);
  font-weight: 800;
  font-size: 1.4rem;
}
.badge-modus-sm {
  display: inline-block;
  min-width: 24px;
  padding: 2px 6px;
  border-radius: 6px;
  background: #e0e7ff;
  color: #3730a3;
  font-weight: 700;
}
.font-mono {
  font-family: monospace;
}
.font-bold {
  font-weight: 700;
}
.font-medium {
  font-weight: 500;
}
</style>
