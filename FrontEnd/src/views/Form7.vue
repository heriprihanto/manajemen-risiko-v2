<script setup>
import { computed, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Menu from 'primevue/menu'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { statusPengendalian, responRisiko, statusLabel, responLabel } from '@/utils/rtp'

const router = useRouter()
const ctx = useContextStore()
const toast = useToast()

const rows = ref([])
const loading = ref(false)
const loadError = ref('')
let serial = 0

// Search & Filter
const searchQuery = ref('')
const filterStatus = ref('all') // all, needs_action, completed, missing_rtp, missing_infokom, missing_pi
const filterJenis = ref('all')

// Action Dropdown Menu
const actionMenu = ref(null)
const actionMenuItems = ref([])
const selectedRow = ref(null)

// Dialog 1: Respon Risiko (RTP)
const dialogRtp = ref(false)
const savingRtp = ref(false)
const editingRtp = ref({})
const file = ref(null)
const evidenceType = ref('link')
const errorRtp = ref('')
const legacyTarget = ref('')

// Dialog 2: Form 8 - Informasi & Komunikasi
const dialogInfokom = ref(false)
const savingInfokom = ref(false)
const editingInfokom = ref({})
const errorInfokom = ref('')
const legacyInfokomWaktu = ref('')

// Dialog 3: Form 9 - Rencana Pemantauan PI
const dialogPi = ref(false)
const savingPi = ref(false)
const editingPi = ref({})
const errorPi = ref('')
const legacyPiWaktu = ref('')

const levelColors = {
  'Sangat Rendah (1)': { color: '#059669', bg: '#ecfdf5', border: '#a7f3d0' },
  'Sangat Rendah': { color: '#059669', bg: '#ecfdf5', border: '#a7f3d0' },
  'Rendah (2)': { color: '#16a34a', bg: '#dcfce7', border: '#bbf7d0' },
  'Rendah': { color: '#16a34a', bg: '#dcfce7', border: '#bbf7d0' },
  'Sedang (3)': { color: '#d97706', bg: '#fef3c7', border: '#fde68a' },
  'Sedang': { color: '#d97706', bg: '#fef3c7', border: '#fde68a' },
  'Tinggi (4)': { color: '#ea580c', bg: '#ffedd5', border: '#fed7aa' },
  'Tinggi': { color: '#ea580c', bg: '#ffedd5', border: '#fed7aa' },
  'Sangat Tinggi (5)': { color: '#dc2626', bg: '#fee2e2', border: '#fecaca' },
  'Sangat Tinggi': { color: '#dc2626', bg: '#fee2e2', border: '#fecaca' },
}

const jenisLabels = {
  strategis_pemda: 'Strategis Pemda',
  strategis_opd: 'Strategis OPD',
  operasional_opd: 'Operasional OPD',
}

const message = (e) =>
  typeof e.response?.data?.detail === 'string'
    ? e.response.data.detail
    : 'Periksa kelengkapan isian atau coba lagi.'

function parseRange(dateStr) {
  if (!dateStr) return { mulai: '', selesai: '', legacy: '' }
  const rangeMatch = String(dateStr).match(/^(\d{4}-\d{2}-\d{2})\s+s\.d\.\s+(\d{4}-\d{2}-\d{2})$/)
  if (rangeMatch) return { mulai: rangeMatch[1], selesai: rangeMatch[2], legacy: '' }
  const singleMatch = String(dateStr).match(/^(\d{4}-\d{2}-\d{2})$/)
  if (singleMatch) return { mulai: singleMatch[1], selesai: singleMatch[1], legacy: '' }
  return { mulai: '', selesai: '', legacy: dateStr }
}

async function load() {
  const id = ++serial
  rows.value = []
  loadError.value = ''
  loading.value = true
  if (!ctx.ready) {
    loading.value = false
    return
  }
  try {
    const { data } = await api.get('/risiko/rtp', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    if (id === serial) rows.value = data
  } catch (e) {
    if (id === serial) loadError.value = `Gagal memuat data RTP. ${message(e)}`
  } finally {
    if (id === serial) loading.value = false
  }
}

// ---------------- KPI Computations ----------------
const kpi = computed(() => {
  const total = rows.value.length
  let rtpCount = 0
  let infokomCount = 0
  let piCount = 0
  let completeCount = 0

  for (const r of rows.value) {
    const hasRtp = Boolean(r.rtp?.rencana_tindak?.trim())
    const hasInfokom = Boolean(r.infokom?.media_bentuk?.trim())
    const hasPi = Boolean(r.monitoring_pi?.metode_pemantauan?.trim())

    if (hasRtp) rtpCount++
    if (hasInfokom) infokomCount++
    if (hasPi) piCount++
    if (hasRtp && hasInfokom && hasPi) completeCount++
  }

  const completionRate = total > 0 ? Math.round((completeCount / total) * 100) : 0

  return {
    total,
    rtpCount,
    infokomCount,
    piCount,
    completeCount,
    completionRate,
  }
})

// ---------------- Filtered Rows ----------------
const filteredRows = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return rows.value.filter((r) => {
    // Filter Jenis
    if (filterJenis.value !== 'all' && r.jenis_risiko !== filterJenis.value) {
      return false
    }

    // Filter Status
    const hasRtp = Boolean(r.rtp?.rencana_tindak?.trim())
    const hasInfokom = Boolean(r.infokom?.media_bentuk?.trim())
    const hasPi = Boolean(r.monitoring_pi?.metode_pemantauan?.trim())
    const isComplete = hasRtp && hasInfokom && hasPi

    if (filterStatus.value === 'completed' && !isComplete) return false
    if (filterStatus.value === 'needs_action' && isComplete) return false
    if (filterStatus.value === 'missing_rtp' && hasRtp) return false
    if (filterStatus.value === 'missing_infokom' && hasInfokom) return false
    if (filterStatus.value === 'missing_pi' && hasPi) return false

    // Search query
    if (q) {
      const matchKode = (r.kode_risiko || '').toLowerCase().includes(q)
      const matchUraian = (r.uraian_risiko || '').toLowerCase().includes(q)
      const matchPemilik = (r.pemilik_risiko || '').toLowerCase().includes(q)
      const matchTindak = (r.rtp?.rencana_tindak || '').toLowerCase().includes(q)
      const matchMedia = (r.infokom?.media_bentuk || '').toLowerCase().includes(q)
      const matchMetode = (r.monitoring_pi?.metode_pemantauan || '').toLowerCase().includes(q)
      return matchKode || matchUraian || matchPemilik || matchTindak || matchMedia || matchMetode
    }

    return true
  })
})

// ---------------- Dropdown Menu Aksi ----------------
function toggleActionMenu(event, row) {
  selectedRow.value = row
  actionMenuItems.value = [
    {
      label: 'Respon Risiko (RTP)',
      icon: 'pi pi-shield',
      command: () => openEditRtp(row),
    },
    {
      label: 'Informasi & Komunikasi (Form 8)',
      icon: 'pi pi-megaphone',
      command: () => openEditInfokom(row),
    },
    {
      label: 'Rencana Pemantauan PI (Form 9)',
      icon: 'pi pi-eye',
      command: () => openEditPi(row),
    },
    { separator: true },
    {
      label: 'Lihat Detail Risiko',
      icon: 'pi pi-arrow-up-right',
      command: () => router.push({ name: 'detail-risiko', params: { id: row.id } }),
    },
  ]
  actionMenu.value.toggle(event)
}

// ---------------- 1. Respon Risiko (RTP) ----------------
function openEditRtp(row) {
  selectedRow.value = row
  const r = row.rtp || {}
  const validDate = /^\d{4}-\d{2}-\d{2}$/.test(r.target_waktu || '')
  legacyTarget.value = r.target_waktu && !validDate && !r.target_mulai ? r.target_waktu : ''
  editingRtp.value = {
    status_pengendalian: r.status_pengendalian || (r.pengendalian_ada?.trim() ? 'sudah_ada' : ''),
    respon_risiko: r.respon_risiko || '',
    pengendalian_ada: r.pengendalian_ada || '',
    bukti_judul: r.bukti_judul || '',
    bukti_link: r.bukti_link || '',
    bukti_berkas_id: r.bukti_berkas_id || null,
    bukti_nama: r.bukti_nama || '',
    celah_pengendalian: r.celah_pengendalian || '',
    rencana_tindak: r.rencana_tindak || '',
    target_mulai: r.target_mulai || (validDate ? r.target_waktu : ''),
    target_selesai: r.target_selesai || (validDate ? r.target_waktu : ''),
    keterangan: r.keterangan || null,
  }
  evidenceType.value = r.bukti_berkas_id ? 'berkas' : 'link'
  file.value = null
  errorRtp.value = ''
  dialogRtp.value = true
}

function chooseFile(event) {
  const selected = event.target.files?.[0]
  errorRtp.value = ''
  file.value = null
  if (selected && (!selected.size || selected.size > 5 * 1024 * 1024)) {
    errorRtp.value = 'Berkas harus berisi data dan maksimal 5 MB.'
    event.target.value = ''
    return
  }
  file.value = selected || null
}

function encodeFile(val) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve({ nama: val.name, base64: reader.result.split(',')[1] })
    reader.onerror = () => reject(new Error('Berkas tidak dapat dibaca'))
    reader.readAsDataURL(val)
  })
}

async function downloadBukti(row) {
  try {
    const r = row.rtp
    const { data } = await api.get(`/risiko/rtp/${row.id}/berkas/${r.bukti_berkas_id}`, {
      responseType: 'blob',
    })
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = r.bukti_nama || 'bukti'
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Berkas gagal diunduh', life: 5000 })
  }
}

async function saveRtp() {
  if (savingRtp.value || !selectedRow.value) return
  const id = serial
  const payload = {
    ...editingRtp.value,
    risiko_id: selectedRow.value.id,
    target_mulai: editingRtp.value.target_mulai || null,
    target_selesai: editingRtp.value.target_selesai || null,
  }
  delete payload.bukti_nama
  errorRtp.value = ''
  savingRtp.value = true
  try {
    if (payload.status_pengendalian === 'tidak_ada') {
      Object.assign(payload, {
        pengendalian_ada: null,
        bukti_judul: null,
        bukti_link: null,
        bukti_berkas_id: null,
      })
    } else if (evidenceType.value === 'link') {
      payload.bukti_berkas_id = null
    } else {
      payload.bukti_link = null
      if (file.value) {
        payload.bukti_upload = await encodeFile(file.value)
        payload.bukti_berkas_id = null
      }
      if (!payload.bukti_upload && !payload.bukti_berkas_id) {
        errorRtp.value = 'Pilih berkas bukti terlebih dahulu.'
        return
      }
    }
    if (id !== serial) return
    await api.post('/risiko/rtp', payload)
    if (id !== serial) return
    dialogRtp.value = false
    await load()
    toast.add({ severity: 'success', summary: 'Respon Risiko (RTP) tersimpan', life: 1600 })
  } catch (e) {
    if (id === serial) errorRtp.value = `RTP belum tersimpan. ${message(e)}`
  } finally {
    savingRtp.value = false
  }
}

// ---------------- 2. Form 8 - Informasi & Komunikasi ----------------
function openEditInfokom(row) {
  selectedRow.value = row
  const inf = row.infokom || {}
  const { mulai, selesai, legacy } = parseRange(inf.rencana_waktu)
  const defaultMulai = inf.rencana_mulai || mulai || row.rtp?.target_mulai || ''
  const defaultSelesai = inf.rencana_selesai || selesai || row.rtp?.target_selesai || ''

  legacyInfokomWaktu.value = legacy
  editingInfokom.value = {
    media_bentuk: inf.media_bentuk || '',
    penyedia_informasi: inf.penyedia_informasi || '',
    penerima_informasi: inf.penerima_informasi || '',
    rencana_mulai: defaultMulai,
    rencana_selesai: defaultSelesai,
    keterangan: inf.keterangan || '',
  }
  errorInfokom.value = ''
  dialogInfokom.value = true
}

async function saveInfokom() {
  if (savingInfokom.value || !selectedRow.value) return
  if (
    editingInfokom.value.rencana_mulai &&
    editingInfokom.value.rencana_selesai &&
    editingInfokom.value.rencana_selesai < editingInfokom.value.rencana_mulai
  ) {
    errorInfokom.value = 'Sampai tanggal tidak boleh sebelum Dari tanggal'
    return
  }
  if (Boolean(editingInfokom.value.rencana_mulai) !== Boolean(editingInfokom.value.rencana_selesai)) {
    errorInfokom.value = 'Isi Dari tanggal dan Sampai tanggal secara lengkap'
    return
  }

  const payload = {
    media_bentuk: editingInfokom.value.media_bentuk?.trim() || null,
    penyedia_informasi: editingInfokom.value.penyedia_informasi?.trim() || null,
    penerima_informasi: editingInfokom.value.penerima_informasi?.trim() || null,
    rencana_mulai: editingInfokom.value.rencana_mulai || null,
    rencana_selesai: editingInfokom.value.rencana_selesai || null,
    keterangan: editingInfokom.value.keterangan?.trim() || null,
  }

  errorInfokom.value = ''
  savingInfokom.value = true
  const id = serial
  try {
    if (selectedRow.value.infokom?.id) {
      await api.put(`/monitoring/infokom/${selectedRow.value.infokom.id}`, payload)
    } else {
      await api.post('/monitoring/infokom', {
        ...payload,
        opd_id: ctx.opdId,
        tahun: ctx.tahun,
        risiko_id: selectedRow.value.id,
        kegiatan_pengendalian:
          selectedRow.value.rtp?.rencana_tindak || selectedRow.value.uraian_risiko || '',
      })
    }
    if (id !== serial) return
    dialogInfokom.value = false
    await load()
    toast.add({
      severity: 'success',
      summary: 'Data Informasi & Komunikasi tersimpan',
      life: 1600,
    })
  } catch (e) {
    if (id === serial) errorInfokom.value = `Gagal menyimpan Informasi & Komunikasi. ${message(e)}`
  } finally {
    savingInfokom.value = false
  }
}

// ---------------- 3. Form 9 - Rencana Pemantauan PI ----------------
function openEditPi(row) {
  selectedRow.value = row
  const pi = row.monitoring_pi || {}
  const { mulai, selesai, legacy } = parseRange(pi.rencana_waktu)
  const defaultMulai = pi.rencana_mulai || mulai || row.rtp?.target_mulai || ''
  const defaultSelesai = pi.rencana_selesai || selesai || row.rtp?.target_selesai || ''

  legacyPiWaktu.value = legacy
  editingPi.value = {
    metode_pemantauan: pi.metode_pemantauan || '',
    penanggung_jawab: pi.penanggung_jawab || row.pemilik_risiko || '',
    rencana_mulai: defaultMulai,
    rencana_selesai: defaultSelesai,
    keterangan: pi.keterangan || '',
  }
  errorPi.value = ''
  dialogPi.value = true
}

async function savePi() {
  if (savingPi.value || !selectedRow.value) return
  if (
    editingPi.value.rencana_mulai &&
    editingPi.value.rencana_selesai &&
    editingPi.value.rencana_selesai < editingPi.value.rencana_mulai
  ) {
    errorPi.value = 'Sampai tanggal tidak boleh sebelum Dari tanggal'
    return
  }
  if (Boolean(editingPi.value.rencana_mulai) !== Boolean(editingPi.value.rencana_selesai)) {
    errorPi.value = 'Isi Dari tanggal dan Sampai tanggal secara lengkap'
    return
  }

  const payload = {
    metode_pemantauan: editingPi.value.metode_pemantauan?.trim() || null,
    penanggung_jawab: editingPi.value.penanggung_jawab?.trim() || null,
    rencana_mulai: editingPi.value.rencana_mulai || null,
    rencana_selesai: editingPi.value.rencana_selesai || null,
    keterangan: editingPi.value.keterangan?.trim() || null,
  }

  errorPi.value = ''
  savingPi.value = true
  const id = serial
  try {
    if (selectedRow.value.monitoring_pi?.id) {
      await api.put(`/monitoring/pi/${selectedRow.value.monitoring_pi.id}`, payload)
    } else {
      await api.post('/monitoring/pi', {
        ...payload,
        opd_id: ctx.opdId,
        tahun: ctx.tahun,
        risiko_id: selectedRow.value.id,
        jenis_risiko: selectedRow.value.jenis_risiko,
        kegiatan_pengendalian:
          selectedRow.value.rtp?.rencana_tindak || selectedRow.value.uraian_risiko || '',
      })
    }
    if (id !== serial) return
    dialogPi.value = false
    await load()
    toast.add({
      severity: 'success',
      summary: 'Data Rencana Pemantauan PI tersimpan',
      life: 1600,
    })
  } catch (e) {
    if (id === serial) errorPi.value = `Gagal menyimpan Rencana Pemantauan PI. ${message(e)}`
  } finally {
    savingPi.value = false
  }
}

watch(
  [() => ctx.opdId, () => ctx.tahun],
  () => {
    dialogRtp.value = false
    dialogInfokom.value = false
    dialogPi.value = false
    load()
  },
  { immediate: true }
)
</script>

<template>
  <div class="rtp-container">
    <!-- Header Hero Banner -->
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-shield"></i>
        </div>
        <div>
          <h1 class="page-title">Respon Risiko (RTP)</h1>
          <p class="page-desc">
            
          </p>
        </div>
      </div>
      <div class="header-actions">
        
      </div>
    </div>

    <!-- KPI / Progress Cards -->
    <div class="kpi-grid">
      <div class="kpi-card card-total">
        <div class="kpi-icon-wrap">
          <i class="pi pi-star-fill" />
        </div>
        <div class="kpi-data">
          <div class="kpi-num">{{ kpi.total }}</div>
          <div class="kpi-label">Total Risiko Prioritas</div>
        </div>
        <div class="kpi-sub muted text-xs">Penetapan Form 4/5</div>
      </div>

      <div class="kpi-card card-rtp">
        <div class="kpi-icon-wrap">
          <i class="pi pi-shield" />
        </div>
        <div class="kpi-data">
          <div class="kpi-num">{{ kpi.rtpCount }} <span class="kpi-max">/ {{ kpi.total }}</span></div>
          <div class="kpi-label">Respon Risiko (RTP)</div>
        </div>
        <div class="kpi-status-tag" :class="kpi.rtpCount === kpi.total && kpi.total > 0 ? 'tag-done' : 'tag-pending'">
          {{ kpi.total > 0 ? Math.round((kpi.rtpCount / kpi.total) * 100) : 0 }}% Terisi
        </div>
      </div>

      <div class="kpi-card card-infokom">
        <div class="kpi-icon-wrap">
          <i class="pi pi-megaphone" />
        </div>
        <div class="kpi-data">
          <div class="kpi-num">{{ kpi.infokomCount }} <span class="kpi-max">/ {{ kpi.total }}</span></div>
          <div class="kpi-label">Info & Komunikasi (F8)</div>
        </div>
        <div class="kpi-status-tag" :class="kpi.infokomCount === kpi.total && kpi.total > 0 ? 'tag-done' : 'tag-pending'">
          {{ kpi.total > 0 ? Math.round((kpi.infokomCount / kpi.total) * 100) : 0 }}% Terisi
        </div>
      </div>

      <div class="kpi-card card-pi">
        <div class="kpi-icon-wrap">
          <i class="pi pi-eye" />
        </div>
        <div class="kpi-data">
          <div class="kpi-num">{{ kpi.piCount }} <span class="kpi-max">/ {{ kpi.total }}</span></div>
          <div class="kpi-label">Pemantauan PI (F9)</div>
        </div>
        <div class="kpi-status-tag" :class="kpi.piCount === kpi.total && kpi.total > 0 ? 'tag-done' : 'tag-pending'">
          {{ kpi.total > 0 ? Math.round((kpi.piCount / kpi.total) * 100) : 0 }}% Terisi
        </div>
      </div>
    </div>

    <!-- Alert / Error message -->
    <div v-if="loadError" class="alert-box alert-error" role="alert">
      <i class="pi pi-exclamation-triangle" />
      <div class="alert-text">{{ loadError }}</div>
      <Button label="Coba lagi" size="small" text @click="load" />
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="toolbar-card">
      <div class="search-box">
        <i class="pi pi-search search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari kode, risiko, pemilik, rencana tindak, media, metode pemantauan..."
          class="search-input"
        />
        <button v-if="searchQuery" class="clear-btn" title="Hapus pencarian" @click="searchQuery = ''">
          <i class="pi pi-times" />
        </button>
      </div>

      <div class="filter-group">
        <div class="filter-item">
          <label class="filter-label">Status Form:</label>
          <select v-model="filterStatus" class="filter-select">
            <option value="all">Semua Status</option>
            <option value="needs_action">Perlu Dilengkapi</option>
            <option value="completed">Lengkap Semua (3/3)</option>
            <option value="missing_rtp">RTP Belum Diisi</option>
            <option value="missing_infokom">Form 8 Belum Diisi</option>
            <option value="missing_pi">Form 9 Belum Diisi</option>
          </select>
        </div>

        <div class="filter-item">
          <label class="filter-label">Jenis Risiko:</label>
          <select v-model="filterJenis" class="filter-select">
            <option value="all">Semua Jenis</option>
            <option value="strategis_pemda">Strategis Pemda</option>
            <option value="strategis_opd">Strategis OPD</option>
            <option value="operasional_opd">Operasional OPD</option>
          </select>
        </div>

        <div class="row-count-badge">
          Menampilkan <strong>{{ filteredRows.length }}</strong> dari {{ rows.length }}
        </div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="table-card">
      <DataTable
        :value="filteredRows"
        :loading="loading"
        size="small"
        stripedRows
        scrollable
        responsiveLayout="scroll"
        class="custom-table"
      >
        <!-- No -->
        <Column header="No" :style="{ width: '48px', textAlign: 'center' }">
          <template #body="{ index }">
            <span class="index-num">{{ index + 1 }}</span>
          </template>
        </Column>

        <!-- Kode & Jenis -->
        <Column header="Kode & Jenis" :style="{ minWidth: '130px' }">
          <template #body="{ data }">
            <div class="kode-box">
              <span class="badge-kode">{{ data.kode_risiko }}</span>
              <span v-if="data.jenis_risiko" class="badge-jenis" :class="`jenis-${data.jenis_risiko}`">
                {{ jenisLabels[data.jenis_risiko] || data.jenis_risiko }}
              </span>
            </div>
          </template>
        </Column>

        <!-- Risiko Prioritas & Level -->
        <Column header="Risiko Prioritas" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="risiko-cell">
              <router-link
                :to="{ name: 'detail-risiko', params: { id: data.id } }"
                class="risiko-link"
                title="Buka rincian risiko"
              >
                {{ data.uraian_risiko }}
                <i class="pi pi-arrow-up-right link-icon" />
              </router-link>
              <div class="risiko-meta">
                <span class="meta-item">
                  <i class="pi pi-user text-xs" />
                  {{ data.pemilik_risiko || '—' }}
                </span>
                <span
                  v-if="data.analisis?.level"
                  class="level-pill"
                  :style="{
                    color: levelColors[data.analisis.level]?.color || '#475569',
                    backgroundColor: levelColors[data.analisis.level]?.bg || '#f1f5f9',
                    borderColor: levelColors[data.analisis.level]?.border || '#cbd5e1',
                  }"
                >
                  {{ data.analisis.level }}
                </span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Pengendalian Yang Ada & Bukti -->
        <Column header="Pengendalian Ada & Bukti" :style="{ minWidth: '210px' }">
          <template #body="{ data }">
            <div class="control-cell">
              <div class="control-status">
                <span
                  v-if="data.rtp?.status_pengendalian === 'sudah_ada'"
                  class="pill-status status-ada"
                >
                  <i class="pi pi-check-circle" /> Sudah Ada
                </span>
                <span
                  v-else-if="data.rtp?.status_pengendalian === 'tidak_ada'"
                  class="pill-status status-tidak"
                >
                  <i class="pi pi-times-circle" /> Tidak Ada
                </span>
                <span v-else class="pill-status status-empty">
                  Belum ditentukan
                </span>
              </div>

              <div v-if="data.rtp?.pengendalian_ada" class="control-text">
                {{ data.rtp.pengendalian_ada }}
              </div>

              <div v-if="data.rtp?.bukti_link" class="evidence-box">
                <a :href="data.rtp.bukti_link" target="_blank" rel="noopener noreferrer" class="evidence-link">
                  <i class="pi pi-link" />
                  <span>{{ data.rtp.bukti_judul || 'Tautan Bukti' }}</span>
                </a>
              </div>
              <div v-else-if="data.rtp?.bukti_berkas_id" class="evidence-box">
                <button class="evidence-btn" @click="downloadBukti(data)">
                  <i class="pi pi-file" />
                  <span>{{ data.rtp.bukti_judul || 'Unduh Berkas' }}</span>
                </button>
              </div>
            </div>
          </template>
        </Column>

        <!-- Respon & Rencana Tindak (RTP) -->
        <Column header="Respon & Rencana Tindak (RTP)" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="rtp-cell">
              <div v-if="data.rtp?.respon_risiko" class="respon-tag">
                <i class="pi pi-shield" />
                {{ responLabel(data.rtp?.respon_risiko) }}
              </div>

              <div v-if="data.rtp?.rencana_tindak" class="tindak-text">
                {{ data.rtp.rencana_tindak }}
              </div>
              <div v-else class="empty-prompt">
                <span class="muted text-xs">RTP belum dirumuskan</span>
                <button class="quick-add-btn" @click="openEditRtp(data)">+ Isi RTP</button>
              </div>

              <div v-if="data.rtp?.target_waktu" class="target-chip">
                <i class="pi pi-calendar" />
                <span>{{ data.rtp.target_waktu }}</span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Info & Komunikasi (Form 8) -->
        <Column header="Info & Komunikasi (F8)" :style="{ minWidth: '210px' }">
          <template #body="{ data }">
            <div v-if="data.infokom?.media_bentuk" class="subform-card card-f8">
              <div class="subform-header">
                <span class="subform-type"><i class="pi pi-megaphone" /> Media / Sarana</span>
                <span class="subform-status status-ok">Lengkap</span>
              </div>
              <div class="subform-main">{{ data.infokom.media_bentuk }}</div>
              <div v-if="data.infokom.penyedia_informasi || data.infokom.penerima_informasi" class="subform-meta">
                <span>{{ data.infokom.penyedia_informasi || '—' }} → {{ data.infokom.penerima_informasi || '—' }}</span>
              </div>
              <div v-if="data.infokom.rencana_waktu" class="subform-time">
                <i class="pi pi-clock" /> {{ data.infokom.rencana_waktu }}
              </div>
            </div>
            <div v-else class="subform-empty" @click="openEditInfokom(data)">
              <div class="empty-dashed">
                <i class="pi pi-plus-circle" />
                <span>Isi Form 8 (Infokom)</span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Pemantauan PI (Form 9) -->
        <Column header="Pemantauan PI (F9)" :style="{ minWidth: '210px' }">
          <template #body="{ data }">
            <div v-if="data.monitoring_pi?.metode_pemantauan" class="subform-card card-f9">
              <div class="subform-header">
                <span class="subform-type"><i class="pi pi-eye" /> Bentuk / Metode</span>
                <span class="subform-status status-ok">Lengkap</span>
              </div>
              <div class="subform-main">{{ data.monitoring_pi.metode_pemantauan }}</div>
              <div v-if="data.monitoring_pi.penanggung_jawab" class="subform-meta">
                <span>PJ: {{ data.monitoring_pi.penanggung_jawab }}</span>
              </div>
              <div v-if="data.monitoring_pi.rencana_waktu" class="subform-time">
                <i class="pi pi-clock" /> {{ data.monitoring_pi.rencana_waktu }}
              </div>
            </div>
            <div v-else class="subform-empty" @click="openEditPi(data)">
              <div class="empty-dashed">
                <i class="pi pi-plus-circle" />
                <span>Isi Form 9 (Pemantauan PI)</span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Aksi (Dropdown Menu) -->
        <Column header="Aksi" :style="{ width: '90px', textAlign: 'center' }" frozen alignFrozen="right">
          <template #body="{ data }">
            <Button
              label="Aksi"
              icon="pi pi-chevron-down"
              iconPos="right"
              size="small"
              class="action-btn"
              aria-label="Menu Aksi"
              @click="toggleActionMenu($event, data)"
            />
          </template>
        </Column>

        <!-- Empty state -->
        <template #empty>
          <div class="empty-state-wrap">
            <div class="empty-icon-circle">
              <i class="pi pi-shield" />
            </div>
            <h3>Tidak ada data risiko prioritas</h3>
            <p class="muted">
              {{ searchQuery ? 'Tidak ada risiko yang sesuai dengan kriteria pencarian.' : 'Belum ada risiko prioritas yang ditetapkan. Selesaikan analisis di Form 4 dan Form 5.' }}
            </p>
            <Button
              v-if="searchQuery"
              label="Reset Pencarian"
              icon="pi pi-times"
              text
              size="small"
              @click="searchQuery = ''"
            />
          </div>
        </template>
      </DataTable>
    </div>

    <!-- PrimeVue Dropdown Popup Menu -->
    <Menu id="rtp-action-menu" ref="actionMenu" :model="actionMenuItems" popup />

    <!-- ==================== Dialog 1: Respon Risiko (RTP) ==================== -->
    <Dialog
      v-model:visible="dialogRtp"
      header="Respon Risiko (RTP) — Rencana Tindak Pengendalian"
      modal
      :closable="!savingRtp"
      :closeOnEscape="!savingRtp"
      :style="{ width: '700px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div v-if="selectedRow" class="dialog-context-card theme-rtp">
        <div class="context-top">
          <span class="badge-kode">{{ selectedRow.kode_risiko }}</span>
          <span v-if="selectedRow.jenis_risiko" class="badge-jenis" :class="`jenis-${selectedRow.jenis_risiko}`">
            {{ jenisLabels[selectedRow.jenis_risiko] }}
          </span>
          <span v-if="selectedRow.analisis?.level" class="pill-level-badge">
            {{ selectedRow.analisis.level }}
          </span>
          <span class="context-owner">Pemilik: <strong>{{ selectedRow.pemilik_risiko || '—' }}</strong></span>
        </div>
        <div class="context-title">{{ selectedRow.uraian_risiko }}</div>
      </div>

      <form id="rtp-form" @submit.prevent="saveRtp">
        <fieldset :disabled="savingRtp" class="dialog-fields">
          <!-- Status Pengendalian -->
          <div class="field-item">
            <label for="rtp-status" class="field-label">Status Kegiatan Pengendalian <span class="req">*</span></label>
            <select id="rtp-status" v-model="editingRtp.status_pengendalian" class="field-select" required>
              <option disabled value="">Pilih status kegiatan pengendalian</option>
              <option v-for="o in statusPengendalian" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </div>

          <!-- Bagian jika Sudah Ada -->
          <div v-if="editingRtp.status_pengendalian === 'sudah_ada'" class="nested-box">
            <div class="nested-header">
              <i class="pi pi-info-circle" />
              <span>Rincian Pengendalian yang Sudah Ada</span>
            </div>

            <div class="field-item">
              <label for="rtp-existing" class="field-label">Uraian Pengendalian yang Sudah Ada <span class="req">*</span></label>
              <Textarea
                id="rtp-existing"
                v-model="editingRtp.pengendalian_ada"
                required
                maxlength="10000"
                autoResize
                rows="2"
                fluid
                placeholder="Deskripsikan SOP, sistem, atau kontrol yang sudah berjalan..."
              />
            </div>

            <div class="grid-2col">
              <div class="field-item">
                <label for="rtp-proof-type" class="field-label">Bentuk Bukti Pengendalian</label>
                <select id="rtp-proof-type" v-model="evidenceType" class="field-select">
                  <option value="link">Tautan Web (URL)</option>
                  <option value="berkas">Unggah Berkas (PDF/Dokumen)</option>
                </select>
              </div>

              <div class="field-item">
                <label for="rtp-title" class="field-label">Judul / Keterangan Bukti <span class="req">*</span></label>
                <InputText id="rtp-title" v-model="editingRtp.bukti_judul" required maxlength="500" fluid placeholder="Contoh: SOP Pelayanan Nomor 12" />
              </div>
            </div>

            <div v-if="evidenceType === 'link'" class="field-item">
              <label for="rtp-link" class="field-label">Link Bukti Pengendalian <span class="req">*</span></label>
              <input id="rtp-link" v-model="editingRtp.bukti_link" type="url" pattern="https?://.+" required maxlength="2000" placeholder="https://..." class="field-input" />
            </div>

            <div v-else class="field-item">
              <label for="rtp-file" class="field-label">Unggah Berkas Bukti (Maks. 5 MB) <span class="req">*</span></label>
              <input id="rtp-file" type="file" :required="!editingRtp.bukti_berkas_id" class="field-file" @change="chooseFile" />
              <small v-if="editingRtp.bukti_berkas_id" class="file-note">
                <i class="pi pi-check" /> Berkas tersimpan: <strong>{{ editingRtp.bukti_nama }}</strong>. Pilih file baru untuk menggantinya.
              </small>
            </div>
          </div>

          <!-- Celah Pengendalian -->
          <div class="field-item">
            <label for="rtp-gap" class="field-label">Celah Pengendalian (Kelemahan Pengendalian)</label>
            <Textarea
              id="rtp-gap"
              v-model="editingRtp.celah_pengendalian"
              autoResize
              rows="2"
              maxlength="10000"
              fluid
              placeholder="Uraikan kelemahan, celah, atau kekurangan pengendalian yang masih ada..."
            />
          </div>

          <!-- Respon Risiko -->
          <div class="field-item">
            <label for="rtp-response" class="field-label">Respon Risiko <span class="req">*</span></label>
            <select id="rtp-response" v-model="editingRtp.respon_risiko" class="field-select" required>
              <option disabled value="">Pilih strategi respon risiko</option>
              <option v-for="o in responRisiko" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </div>

          <!-- Rencana Tindak Pengendalian (RTP) -->
          <div class="field-item">
            <label for="rtp-plan" class="field-label">Rencana Tindak Pengendalian (RTP) <span class="req">*</span></label>
            <Textarea
              id="rtp-plan"
              v-model="editingRtp.rencana_tindak"
              required
              autoResize
              rows="3"
              maxlength="10000"
              fluid
              placeholder="Uraikan langkah nyata, kegiatan perbaikan, atau inovasi pengendalian yang akan dilaksanakan..."
            />
          </div>

          <!-- Target Waktu -->
          <div class="field-item">
            <label class="field-label">Target Waktu Pelaksanaan</label>
            <div class="date-range-grid">
              <div class="date-col">
                <label for="rtp-target-start" class="date-sublabel">Dari Tanggal</label>
                <input
                  id="rtp-target-start"
                  v-model="editingRtp.target_mulai"
                  type="date"
                  :max="editingRtp.target_selesai || undefined"
                  :required="!!legacyTarget || !!editingRtp.target_selesai"
                  class="field-input"
                />
              </div>
              <div class="date-col">
                <label for="rtp-target-end" class="date-sublabel">Sampai Tanggal</label>
                <input
                  id="rtp-target-end"
                  v-model="editingRtp.target_selesai"
                  type="date"
                  :min="editingRtp.target_mulai || undefined"
                  :required="!!legacyTarget || !!editingRtp.target_mulai"
                  class="field-input"
                />
              </div>
            </div>
            <small v-if="legacyTarget" class="legacy-date-note">
              Target waktu sebelumnya: <em>{{ legacyTarget }}</em>. Pilih rentang tanggal untuk memperbaruinya.
            </small>
          </div>
        </fieldset>

        <p v-if="errorRtp" role="alert" class="dialog-error">
          <i class="pi pi-exclamation-circle" /> {{ errorRtp }}
        </p>
      </form>

      <template #footer>
        <div class="dialog-footer">
          <Button label="Batal" text :disabled="savingRtp" @click="dialogRtp = false" />
          <Button
            label="Simpan Respon Risiko"
            icon="pi pi-check"
            type="submit"
            form="rtp-form"
            :loading="savingRtp"
            :disabled="savingRtp"
            class="btn-primary-action"
          />
        </div>
      </template>
    </Dialog>

    <!-- ==================== Dialog 2: Form 8 - Informasi & Komunikasi ==================== -->
    <Dialog
      v-model:visible="dialogInfokom"
      header="Form 8 — Informasi & Komunikasi"
      modal
      :closable="!savingInfokom"
      :closeOnEscape="!savingInfokom"
      :style="{ width: '680px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div v-if="selectedRow" class="dialog-context-card theme-infokom">
        <div class="context-top">
          <span class="badge-kode">{{ selectedRow.kode_risiko }}</span>
          <span class="context-owner">Risiko: <strong>{{ selectedRow.uraian_risiko }}</strong></span>
        </div>
        <div class="context-sub">
          <strong>Kegiatan Pengendalian dari RTP:</strong>
          <p>{{ selectedRow.rtp?.rencana_tindak || 'Belum ada Rencana Tindak Pengendalian pada Form RTP.' }}</p>
        </div>
      </div>

      <form id="infokom-form" @submit.prevent="saveInfokom">
        <fieldset :disabled="savingInfokom" class="dialog-fields">
          <!-- Media / Bentuk Sarana -->
          <div class="field-item">
            <label for="f8-media" class="field-label">Media / Bentuk Sarana Komunikasi <span class="req">*</span></label>
            <Textarea
              id="f8-media"
              v-model="editingInfokom.media_bentuk"
              required
              autoResize
              rows="2"
              maxlength="1000"
              placeholder="Contoh: Rapat Koordinasi Rutin, Diseminasi WhatsApp Group, Surat Edaran Kepala OPD, dsb."
              fluid
            />
          </div>

          <div class="grid-2col">
            <div class="field-item">
              <label for="f8-penyedia" class="field-label">Penyedia Informasi <span class="req">*</span></label>
              <InputText
                id="f8-penyedia"
                v-model="editingInfokom.penyedia_informasi"
                required
                maxlength="255"
                placeholder="Contoh: Pengelola Risiko / Sekretaris / Kasubbag"
                fluid
              />
            </div>

            <div class="field-item">
              <label for="f8-penerima" class="field-label">Penerima Informasi <span class="req">*</span></label>
              <InputText
                id="f8-penerima"
                v-model="editingInfokom.penerima_informasi"
                required
                maxlength="255"
                placeholder="Contoh: Seluruh Pegawai OPD / Pelaku Usaha / Pimpinan"
                fluid
              />
            </div>
          </div>

          <!-- Rencana Waktu -->
          <div class="field-item">
            <label class="field-label">Rencana Waktu Pelaksanaan</label>
            <div class="date-range-grid">
              <div class="date-col">
                <label for="f8-rencana-mulai" class="date-sublabel">Dari Tanggal</label>
                <input
                  id="f8-rencana-mulai"
                  v-model="editingInfokom.rencana_mulai"
                  type="date"
                  :max="editingInfokom.rencana_selesai || undefined"
                  class="field-input"
                />
              </div>
              <div class="date-col">
                <label for="f8-rencana-selesai" class="date-sublabel">Sampai Tanggal</label>
                <input
                  id="f8-rencana-selesai"
                  v-model="editingInfokom.rencana_selesai"
                  type="date"
                  :min="editingInfokom.rencana_mulai || undefined"
                  class="field-input"
                />
              </div>
            </div>
            <small v-if="legacyInfokomWaktu" class="legacy-date-note">
              Rencana waktu sebelumnya: <em>{{ legacyInfokomWaktu }}</em>. Pilih rentang tanggal untuk memperbaruinya.
            </small>
          </div>

          <!-- Keterangan -->
          <div class="field-item">
            <label for="f8-keterangan" class="field-label">Keterangan Tambahan</label>
            <Textarea
              id="f8-keterangan"
              v-model="editingInfokom.keterangan"
              autoResize
              rows="2"
              maxlength="2000"
              placeholder="Catatan atau keterangan teknis lainnya (opsional)..."
              fluid
            />
          </div>
        </fieldset>

        <p v-if="errorInfokom" role="alert" class="dialog-error">
          <i class="pi pi-exclamation-circle" /> {{ errorInfokom }}
        </p>
      </form>

      <template #footer>
        <div class="dialog-footer">
          <Button label="Batal" text :disabled="savingInfokom" @click="dialogInfokom = false" />
          <Button
            label="Simpan Informasi & Komunikasi"
            icon="pi pi-check"
            type="submit"
            form="infokom-form"
            :loading="savingInfokom"
            :disabled="savingInfokom"
            class="btn-primary-action btn-infokom"
          />
        </div>
      </template>
    </Dialog>

    <!-- ==================== Dialog 3: Form 9 - Rencana Pemantauan PI ==================== -->
    <Dialog
      v-model:visible="dialogPi"
      header="Form 9 — Rencana Pemantauan Pengendalian Intern (PI)"
      modal
      :closable="!savingPi"
      :closeOnEscape="!savingPi"
      :style="{ width: '680px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div v-if="selectedRow" class="dialog-context-card theme-pi">
        <div class="context-top">
          <span class="badge-kode">{{ selectedRow.kode_risiko }}</span>
          <span class="context-owner">Risiko: <strong>{{ selectedRow.uraian_risiko }}</strong></span>
        </div>
        <div class="context-sub">
          <strong>Kegiatan Pengendalian dari RTP:</strong>
          <p>{{ selectedRow.rtp?.rencana_tindak || 'Belum ada Rencana Tindak Pengendalian pada Form RTP.' }}</p>
        </div>
      </div>

      <form id="pi-form" @submit.prevent="savePi">
        <fieldset :disabled="savingPi" class="dialog-fields">
          <!-- Bentuk / Metode Pemantauan -->
          <div class="field-item">
            <label for="f9-metode" class="field-label">Bentuk / Metode Pemantauan <span class="req">*</span></label>
            <Textarea
              id="f9-metode"
              v-model="editingPi.metode_pemantauan"
              required
              autoResize
              rows="2"
              maxlength="1000"
              placeholder="Contoh: Reviu berkala bulanan, monitoring langsung di lapangan, uji petik dokumen kepatuhan, dsb."
              fluid
            />
          </div>

          <!-- Penanggung Jawab -->
          <div class="field-item">
            <label for="f9-pj" class="field-label">Penanggung Jawab Pemantauan <span class="req">*</span></label>
            <InputText
              id="f9-pj"
              v-model="editingPi.penanggung_jawab"
              required
              maxlength="255"
              placeholder="Contoh: Tim Kepatuhan Intern / Kasubbag Umum / Inspektorat"
              fluid
            />
          </div>

          <!-- Rencana Waktu -->
          <div class="field-item">
            <label class="field-label">Rencana Waktu Pemantauan</label>
            <div class="date-range-grid">
              <div class="date-col">
                <label for="f9-rencana-mulai" class="date-sublabel">Dari Tanggal</label>
                <input
                  id="f9-rencana-mulai"
                  v-model="editingPi.rencana_mulai"
                  type="date"
                  :max="editingPi.rencana_selesai || undefined"
                  class="field-input"
                />
              </div>
              <div class="date-col">
                <label for="f9-rencana-selesai" class="date-sublabel">Sampai Tanggal</label>
                <input
                  id="f9-rencana-selesai"
                  v-model="editingPi.rencana_selesai"
                  type="date"
                  :min="editingPi.rencana_mulai || undefined"
                  class="field-input"
                />
              </div>
            </div>
            <small v-if="legacyPiWaktu" class="legacy-date-note">
              Rencana waktu sebelumnya: <em>{{ legacyPiWaktu }}</em>. Pilih rentang tanggal untuk memperbaruinya.
            </small>
          </div>

          <!-- Keterangan -->
          <div class="field-item">
            <label for="f9-keterangan" class="field-label">Keterangan Tambahan</label>
            <Textarea
              id="f9-keterangan"
              v-model="editingPi.keterangan"
              autoResize
              rows="2"
              maxlength="2000"
              placeholder="Catatan tindak lanjut atau indikator pemantauan (opsional)..."
              fluid
            />
          </div>
        </fieldset>

        <p v-if="errorPi" role="alert" class="dialog-error">
          <i class="pi pi-exclamation-circle" /> {{ errorPi }}
        </p>
      </form>

      <template #footer>
        <div class="dialog-footer">
          <Button label="Batal" text :disabled="savingPi" @click="dialogPi = false" />
          <Button
            label="Simpan Pemantauan PI"
            icon="pi pi-check"
            type="submit"
            form="pi-form"
            :loading="savingPi"
            :disabled="savingPi"
            class="btn-primary-action btn-pi"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
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
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
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
  gap: 0.75rem;
  align-items: center;
}


.rtp-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* Hero Banner */
.hero-banner {
  background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 50%, #1e293b 100%);
  border-radius: var(--radius, 14px);
  padding: 24px 28px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  box-shadow: 0 10px 25px -5px rgba(30, 27, 75, 0.25);
  position: relative;
  overflow: hidden;
}

.hero-banner::after {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.35) 0%, transparent 70%);
  pointer-events: none;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #c4b5fd;
  margin-bottom: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.hero-title {
  margin: 0 0 6px 0;
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #ffffff;
}

.hero-desc {
  margin: 0;
  font-size: 0.88rem;
  color: #cbd5e1;
  max-width: 800px;
  line-height: 1.45;
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  border-color: rgba(255, 255, 255, 0.25) !important;
  font-weight: 600;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  transition: all 0.2s ease;
}

.btn-refresh:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

.kpi-card {
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.07);
}

.kpi-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.card-total .kpi-icon-wrap { background: #e0f2fe; color: #0284c7; }
.card-rtp .kpi-icon-wrap { background: #e0e7ff; color: #4338ca; }
.card-infokom .kpi-icon-wrap { background: #ccfbf1; color: #0f766e; }
.card-pi .kpi-icon-wrap { background: #f3e8ff; color: #7e22ce; }

.kpi-num {
  font-size: 1.55rem;
  font-weight: 800;
  line-height: 1.1;
  color: var(--text, #1e293b);
}

.kpi-max {
  font-size: 0.95rem;
  font-weight: 600;
  color: #94a3b8;
}

.kpi-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  margin-top: 2px;
}

.kpi-status-tag {
  align-self: flex-start;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  margin-top: auto;
}

.tag-done {
  background: #dcfce7;
  color: #15803d;
}

.tag-pending {
  background: #f1f5f9;
  color: #475569;
}

/* Toolbar & Filters */
.toolbar-card {
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 260px;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
}

.search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.5rem 2rem 0.5rem 2.2rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.86rem;
  background: var(--surface-2, #f8fafc);
  color: inherit;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  background: #ffffff;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
}

.clear-btn:hover {
  color: #475569;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
}

.filter-select {
  padding: 0.45rem 0.75rem;
  font-size: 0.82rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: var(--surface-0, #ffffff);
  color: inherit;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: #6366f1;
}

.row-count-badge {
  font-size: 0.78rem;
  color: #64748b;
  padding: 4px 10px;
  background: #f1f5f9;
  border-radius: 6px;
}

/* Table Card */
.table-card {
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.index-num {
  font-weight: 600;
  color: #64748b;
  font-size: 0.82rem;
}

.kode-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.badge-kode {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 800;
  font-family: monospace;
  background: #f1f5f9;
  color: #1e293b;
  padding: 2px 7px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.badge-jenis {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 1px 6px;
  border-radius: 4px;
  letter-spacing: 0.02em;
}

.jenis-strategis_pemda {
  background: #e0f2fe;
  color: #0369a1;
}

.jenis-strategis_opd {
  background: #fef3c7;
  color: #b45309;
}

.jenis-operasional_opd {
  background: #f1f5f9;
  color: #475569;
}

/* Risiko Cell */
.risiko-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.risiko-link {
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
  font-size: 0.88rem;
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  transition: color 0.15s ease;
}

.risiko-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.link-icon {
  font-size: 0.7rem;
  color: #94a3b8;
}

.risiko-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.76rem;
  color: #64748b;
}

.level-pill {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 999px;
  border: 1px solid transparent;
}

/* Control Cell */
.control-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pill-status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.status-ada {
  background: #dcfce7;
  color: #15803d;
}

.status-tidak {
  background: #fee2e2;
  color: #b91c1c;
}

.status-empty {
  background: #f1f5f9;
  color: #64748b;
}

.control-text {
  font-size: 0.8rem;
  color: #334155;
  line-height: 1.35;
}

.evidence-box {
  margin-top: 2px;
}

.evidence-link,
.evidence-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  color: #0284c7;
  font-weight: 600;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  padding: 2px 7px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.evidence-link:hover,
.evidence-btn:hover {
  background: #e0f2fe;
}

/* RTP Cell */
.rtp-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.respon-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  background: #e0e7ff;
  color: #3730a3;
  align-self: flex-start;
}

.tindak-text {
  font-size: 0.84rem;
  font-weight: 500;
  color: #1e293b;
  line-height: 1.35;
}

.empty-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.quick-add-btn {
  font-size: 0.74rem;
  font-weight: 700;
  color: #4f46e5;
  background: #eef2ff;
  border: 1px dashed #a5b4fc;
  padding: 2px 8px;
  border-radius: 6px;
  cursor: pointer;
}

.quick-add-btn:hover {
  background: #e0e7ff;
}

.target-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.73rem;
  color: #64748b;
  margin-top: 2px;
}

/* Subform mini cards in table */
.subform-card {
  padding: 8px 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  border: 1px solid;
}

.card-f8 {
  background: #f0fdfa;
  border-color: #ccfbf1;
}

.card-f9 {
  background: #faf5ff;
  border-color: #f3e8ff;
}

.subform-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.subform-type {
  font-size: 0.72rem;
  font-weight: 700;
  color: #475569;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.subform-status {
  font-size: 0.68rem;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 999px;
}

.subform-status.status-ok {
  background: #dcfce7;
  color: #15803d;
}

.subform-main {
  font-size: 0.8rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.3;
}

.subform-meta {
  font-size: 0.72rem;
  color: #64748b;
}

.subform-time {
  font-size: 0.7rem;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.subform-empty {
  cursor: pointer;
}

.empty-dashed {
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  color: #64748b;
  font-size: 0.76rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: #f8fafc;
  transition: all 0.15s ease;
}

.empty-dashed:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #1e293b;
}

/* Action dropdown button */
.action-btn {
  font-weight: 700 !important;
  font-size: 0.8rem !important;
  padding: 0.35rem 0.75rem !important;
  border-color: #cbd5e1 !important;
  color: #334155 !important;
  border-radius: 8px !important;
}

.action-btn:hover {
  background: #f1f5f9 !important;
  border-color: #94a3b8 !important;
}

/* Empty State */
.empty-state-wrap {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 4px;
}

.empty-state-wrap h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
}

/* Alert Box */
.alert-box {
  padding: 12px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.86rem;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fee2e2;
  color: #b91c1c;
}

.alert-text {
  flex: 1;
  font-weight: 500;
}

/* Dialog Styles */
.custom-dialog :deep(.p-dialog-header) {
  padding: 18px 24px;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 700;
  background: #f8fafc;
}

.custom-dialog :deep(.p-dialog-content) {
  padding: 20px 24px;
}

.custom-dialog :deep(.p-dialog-footer) {
  padding: 14px 24px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.dialog-context-card {
  padding: 14px 16px;
  border-radius: 10px;
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid;
}

.theme-rtp {
  background: #eef2ff;
  border-color: #c7d2fe;
}

.theme-infokom {
  background: #f0fdfa;
  border-color: #99f6e4;
}

.theme-pi {
  background: #faf5ff;
  border-color: #e9d5ff;
}

.context-top {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.pill-level-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.context-owner {
  font-size: 0.8rem;
  color: #475569;
  margin-left: auto;
}

.context-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.35;
}

.context-sub strong {
  display: block;
  font-size: 0.78rem;
  color: #475569;
  margin-bottom: 2px;
}

.context-sub p {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
}

.dialog-fields {
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
}

.req {
  color: #dc2626;
}

.field-select,
.field-input,
.field-file {
  width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.88rem;
  background: #ffffff;
  color: inherit;
}

.field-select:focus,
.field-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 600px) {
  .grid-2col {
    grid-template-columns: 1fr;
  }
}

.nested-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nested-header {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 6px;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 8px;
}

.file-note {
  font-size: 0.76rem;
  color: #15803d;
  display: block;
  margin-top: 4px;
}

.date-range-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 480px) {
  .date-range-grid {
    grid-template-columns: 1fr;
  }
}

.date-col {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.date-sublabel {
  font-size: 0.76rem;
  font-weight: 600;
  color: #64748b;
}

.legacy-date-note {
  font-size: 0.76rem;
  color: #64748b;
  display: block;
  margin-top: 4px;
}

.dialog-error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.84rem;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.btn-primary-action {
  font-weight: 700;
  border-radius: 8px;
}

.btn-infokom {
  background: #0d9488 !important;
  border-color: #0d9488 !important;
}

.btn-infokom:hover {
  background: #0f766e !important;
  border-color: #0f766e !important;
}

.btn-pi {
  background: #7c3aed !important;
  border-color: #7c3aed !important;
}

.btn-pi:hover {
  background: #6d28d9 !important;
  border-color: #6d28d9 !important;
}
</style>
