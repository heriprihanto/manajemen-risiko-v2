<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'
import MonevRtp from '@/components/laporan/MonevRtp.vue'

const ctx = useContextStore()
const loading = ref(false)
const rawItems = ref([])
const searchQuery = ref('')
const exporting = ref(false)

const opdName = computed(() => ctx.opd?.nama_pd || '-')

async function loadData() {
  loading.value = true
  try {
    const { data } = await api.get('/risiko/realisasi', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    rawItems.value = Array.isArray(data) ? data : (data?.items || [])
  } catch (e) {
    console.error('Gagal memuat data Monev RTP:', e)
    rawItems.value = []
  } finally {
    loading.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun], loadData)
onMounted(loadData)

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return rawItems.value
  return rawItems.value.filter((r) => {
    const kode = (r.kode_risiko || '').toLowerCase()
    const risiko = (r.uraian_risiko || '').toLowerCase()
    const rtp = (r.rtp?.rencana_tindak || '').toLowerCase()
    const jenis = (r.jenis_risiko || '').toLowerCase()
    return kode.includes(q) || risiko.includes(q) || rtp.includes(q) || jenis.includes(q)
  })
})

function printReport() {
  window.print()
}

async function exportExcel() {
  exporting.value = true
  try {
    const { data } = await api.get('/laporan/excel', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun, forms: 'monev_rtp' },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = `Laporan_Monev_RTP_${opdName.value.replace(/[^a-zA-Z0-9_-]/g, '_')}_${ctx.tahun}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Gagal mengunduh Excel:', e)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="laporan-monev-page">
    <!-- Header Toolbar (tidak tercetak saat print) -->
    <div class="page-header no-print">
      <div class="header-left">
        <router-link to="/realisasi-rtp" class="back-link">
          <Button icon="pi pi-arrow-left" text rounded severity="secondary" v-tooltip="'Kembali ke Realisasi RTP'" />
        </router-link>
        <div class="header-icon-box">
          <i class="pi pi-file-check"></i>
        </div>
        <div>
          <h1 class="page-title">Laporan Monitoring &amp; Evaluasi RTP</h1>
          <p class="page-desc">
            Format Resmi Monev Rencana Tindak Pengendalian Risiko &middot; {{ opdName }} &middot; Tahun {{ ctx.tahun }}
          </p>
        </div>
      </div>

      <div class="header-actions">
        <div class="search-box">
          <i class="pi pi-search search-icon" />
          <InputText
            v-model="searchQuery"
            placeholder="Cari risiko / RTP..."
            class="p-inputtext-sm search-input"
          />
        </div>
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          :loading="loading"
          @click="loadData"
        />
        <Button
          label="Unduh Excel"
          icon="pi pi-file-excel"
          severity="success"
          :loading="exporting"
          @click="exportExcel"
        />
        <Button
          label="Cetak / Simpan PDF"
          icon="pi pi-print"
          severity="primary"
          @click="printReport"
        />
      </div>
    </div>

    <!-- State Loading -->
    <AppLoader v-if="loading" />

    <!-- Paper Container for Report -->
    <div v-else class="report-paper">
      <MonevRtp :data="filteredItems" :opd-name="opdName" :tahun="ctx.tahun" />
    </div>
  </div>
</template>

<style scoped>
.laporan-monev-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}

.page-desc {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 0.85rem;
}

.search-input {
  padding-left: 2.2rem;
  width: 200px;
  border-radius: 6px;
}

.report-paper {
  background: #ffffff;
  padding: 2rem;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

@media print {
  .no-print {
    display: none !important;
  }
  .laporan-monev-page {
    gap: 0;
  }
  .report-paper {
    padding: 0;
    border: none;
    box-shadow: none;
    background: transparent;
  }
}
</style>

