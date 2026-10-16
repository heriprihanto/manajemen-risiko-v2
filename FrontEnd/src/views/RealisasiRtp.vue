<script setup>
import { computed, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { formatDate } from '@/utils/date'

const toast = useToast()
const ctx = useContextStore()

const loading = ref(false)
const saving = ref(false)
const items = ref([])
const summary = ref({
  total: 0,
  selesai: 0,
  proses: 0,
  belum: 0,
  persen_selesai: 0,
})

const searchQuery = ref('')
const filterStatus = ref('all') // all, selesai, proses, belum
const filterJenis = ref('all')

// Dialog Input/Edit Realisasi RTP
const dialogVisible = ref(false)
const selectedItem = ref(null)

const form = ref({
  risiko_id: null,
  rtp_cee_id: null,
  status_realisasi: 'belum',
  tanggal_realisasi: '',
  uraian_hasil: '',
  hambatan: '',
  bukti_link: '',
  bukti_berkas_id: null,
  bukti_nama: '',
  hapus_bukti: false,
})

// File upload state
const fileInput = ref(null)
const selectedFile = ref(null)
const fileBase64 = ref(null)
const fileName = ref('')
const fileSize = ref(0)

// AI Assistant state
const aiDrafting = ref(false)

const jenisLabels = {
  strategis_pemda: 'Strategis Pemda',
  strategis_opd: 'Strategis OPD',
  operasional_opd: 'Operasional OPD',
  cee: 'RTP atas CEE',
}

const statusOptions = [
  { value: 'all', label: 'Semua Status Realisasi' },
  { value: 'selesai', label: 'Selesai Terealisasi' },
  { value: 'proses', label: 'Sedang Berjalan (Proses)' },
  { value: 'belum', label: 'Belum Direalisasikan' },
]

async function loadData() {
  if (!ctx.opdId || !ctx.tahun) return
  loading.value = true
  try {
    const { data } = await api.get('/risiko/realisasi', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    items.value = data.items || []
    summary.value = data.summary || { total: 0, selesai: 0, proses: 0, belum: 0, persen_selesai: 0 }
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal memuat data realisasi RTP'
    toast.add({ severity: 'error', summary: 'Gagal Memuat', detail: err, life: 4000 })
  } finally {
    loading.value = false
  }
}

const filteredItems = computed(() => {
  return items.value.filter((it) => {
    // Filter status
    const st = it.realisasi?.status_realisasi || 'belum'
    if (filterStatus.value !== 'all' && st !== filterStatus.value) return false

    // Filter jenis risiko
    if (filterJenis.value !== 'all' && it.jenis_risiko !== filterJenis.value) return false

    // Search query
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchKode = it.kode_risiko?.toLowerCase().includes(q)
      const matchUraian = it.uraian_risiko?.toLowerCase().includes(q)
      const matchRtp = it.rtp?.rencana_tindak?.toLowerCase().includes(q)
      const matchPemilik = it.pemilik_risiko?.toLowerCase().includes(q)
      const matchHasil = it.realisasi?.uraian_hasil?.toLowerCase().includes(q)
      if (!matchKode && !matchUraian && !matchRtp && !matchPemilik && !matchHasil) return false
    }

    return true
  })
})

function openRealisasiDialog(row) {
  selectedItem.value = row
  const rel = row.realisasi || {}

  form.value = {
    risiko_id: row.source_type === 'cee' ? null : (row.risiko_id || row.id),
    rtp_cee_id: row.rtp_cee_id || null,
    status_realisasi: rel.status_realisasi || 'belum',
    tanggal_realisasi: rel.tanggal_realisasi || '',
    uraian_hasil: rel.uraian_hasil || '',
    hambatan: rel.hambatan || '',
    bukti_link: rel.bukti_link || '',
    bukti_berkas_id: rel.bukti_berkas_id || null,
    bukti_nama: rel.bukti_nama || '',
    hapus_bukti: false,
  }

  // Reset file upload
  selectedFile.value = null
  fileBase64.value = null
  fileName.value = ''
  fileSize.value = 0
  if (fileInput.value) fileInput.value.value = ''

  dialogVisible.value = true
}

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    toast.add({
      severity: 'warn',
      summary: 'Ukuran Berkas Terlalu Besar',
      detail: 'Maksimal ukuran berkas adalah 5 MB.',
      life: 4000,
    })
    event.target.value = ''
    return
  }

  selectedFile.value = file
  fileName.value = file.name
  fileSize.value = Math.round(file.size / 1024)

  const reader = new FileReader()
  reader.onload = (e) => {
    const raw = e.target.result
    // Extract base64 part
    const b64 = raw.split(',')[1] || raw
    fileBase64.value = b64
  }
  reader.readAsDataURL(file)
}

function triggerFileInput() {
  if (fileInput.value) fileInput.value.click()
}

function removeFile() {
  selectedFile.value = null
  fileBase64.value = null
  fileName.value = ''
  fileSize.value = 0
  if (fileInput.value) fileInput.value.value = ''
  form.value.hapus_bukti = true
  form.value.bukti_nama = ''
  form.value.bukti_berkas_id = null
}

async function saveRealisasi() {
  if (!form.value.risiko_id && !form.value.rtp_cee_id) return

  if (form.value.status_realisasi === 'selesai' && !form.value.tanggal_realisasi) {
    toast.add({
      severity: 'warn',
      summary: 'Tanggal Wajib Diisi',
      detail: 'Untuk status Selesai Terealisasi, mohon isi tanggal realisasi pelaksanaan.',
      life: 4000,
    })
    return
  }

  saving.value = true
  try {
    const payload = {
      risiko_id: form.value.risiko_id || undefined,
      rtp_cee_id: form.value.rtp_cee_id || undefined,
      status_realisasi: form.value.status_realisasi,
      tanggal_realisasi: form.value.tanggal_realisasi || null,
      uraian_hasil: form.value.uraian_hasil,
      hambatan: form.value.hambatan,
      bukti_link: form.value.bukti_link,
      hapus_bukti: form.value.hapus_bukti,
    }

    if (fileBase64.value && fileName.value) {
      payload.bukti_upload = {
        nama: fileName.value,
        base64: fileBase64.value,
      }
    } else if (form.value.bukti_berkas_id) {
      payload.bukti_berkas_id = form.value.bukti_berkas_id
    }

    await api.post('/risiko/realisasi', payload)

    toast.add({
      severity: 'success',
      summary: 'Berhasil Disimpan',
      detail: 'Data realisasi RTP dan bukti dukung berhasil diperbarui.',
      life: 3000,
    })

    dialogVisible.value = false
    await loadData()
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal menyimpan realisasi RTP'
    toast.add({ severity: 'error', summary: 'Gagal Menyimpan', detail: err, life: 4000 })
  } finally {
    saving.value = false
  }
}

// AI Assistant untuk membuat draf narasi hasil realisasi
async function draftHasilViaAi() {
  if (!selectedItem.value) return
  aiDrafting.value = true
  try {
    const r = selectedItem.value
    const currentOpd = ctx.opds?.find((o) => o.id === ctx.opdId)
    const isCee = r.source_type === 'cee'

    const prompt = isCee
      ? `Anda adalah asisten manajemen risiko pemerintah daerah.
Bantu buatkan draf ringkas dan formal uraian hasil realisasi tindak pengendalian (RTP) atas kelemahan Lingkungan Pengendalian Intern (CEE) berikut:
- Organisasi: ${currentOpd?.nama || 'OPD'}
- Sub-unsur CEE: ${r.sasaran || '-'}
- Kondisi Permasalahan: ${r.uraian_risiko || '-'}
- Rencana Tindak Pengendalian: ${r.rtp?.rencana_tindak || '-'}
- Target Waktu: ${r.rtp?.target_waktu || '-'}

Tuliskan 1 atau 2 kalimat formal dalam bahasa Indonesia yang menyatakan bahwa rencana tindak perbaikan lingkungan pengendalian telah selesai dilaksanakan, output administratif atau SOP/kebijakan yang diterbitkan, serta dampak positifnya bagi penguatan sistem pengendalian intern OPD.`
      : `Anda adalah asisten manajemen risiko pemerintah daerah.
Bantu buatkan draf ringkas dan formal uraian hasil realisasi tindak pengendalian (RTP) berikut:
- Organisasi: ${currentOpd?.nama || 'OPD'}
- Risiko: ${r.uraian_risiko || ''}
- Rencana Tindak Pengendalian (RTP): ${r.rtp?.rencana_tindak || 'Pelaksanaan mitigasi dan perbaikan pengendalian'}
- Target Selesai: ${r.rtp?.target_selesai || r.rtp?.target_waktu || 'Tahun 2026'}

Tuliskan 1 atau 2 kalimat formal dalam bahasa Indonesia yang menyatakan bahwa kegiatan telah selesai dilaksanakan, output yang dihasilkan (misal: SOP/SK telah diterbitkan, pelatihan telah selesai, pemeliharaan telah dilakukan), serta dampak pengendalian yang diharapkan tercapai.`

    const { data } = await api.post('/ai/copilot', {
      prompt,
      context: {
        halaman: 'Realisasi RTP',
        opd: currentOpd?.nama,
        tahun: ctx.tahun,
      },
    })

    if (data.reply) {
      form.value.uraian_hasil = data.reply.trim()
      toast.add({
        severity: 'info',
        summary: 'Draf Narasi Dihasilkan',
        detail: 'AI telah mengisi saran uraian hasil realisasi.',
        life: 3000,
      })
    }
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal memanggil AI'
    toast.add({ severity: 'error', summary: 'AI Error', detail: err, life: 3000 })
  } finally {
    aiDrafting.value = false
  }
}

function getEvidenceDownloadUrl(row, berkasId) {
  if (row?.source_type === 'cee' || row?.rtp_cee_id) {
    return `/api/risiko/bukti/${berkasId}`
  }
  return `/api/risiko/rtp/${row?.risiko_id || row?.id || 0}/berkas/${berkasId}`
}

watch([() => ctx.opdId, () => ctx.tahun], loadData, { immediate: true })
</script>

<template>
  <div class="realisasi-rtp-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-check-circle"></i>
        </div>
        <div>
          <h1 class="page-title">Realisasi Rencana Tindak Pengendalian (RTP)</h1>
          <p class="page-desc">
            Pencatatan tanggal realisasi pelaksanaan tindak pengendalian dan unggah berkas bukti dukung (eviden)
          </p>
        </div>
      </div>
      <div class="header-actions">
        <router-link to="/treated-risk" class="btn-link-treated">
          <Button
            label="Lanjut ke Treated Risk"
            icon="pi pi-arrow-right"
            iconPos="right"
            severity="help"
            variant="outlined"
          />
        </router-link>
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          :loading="loading"
          @click="loadData"
        />
      </div>
    </div>


    <!-- Stat Cards Header (Style Laporan Rekapitulasi) -->
    <div class="stat-grid no-print" style="margin-bottom: 18px;">
      <div class="stat">
        <div class="v">{{ summary.total }}</div>
        <div class="l">Total Rencana Tindak (RTP)</div>
      </div>

      <div class="stat">
        <div class="v">
          {{ summary.selesai }} <small>({{ summary.persen_selesai }}%)</small>
        </div>
        <div class="l">Selesai Terealisasi</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.proses }}</div>
        <div class="l">Sedang Berjalan (Proses)</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.belum }}</div>
        <div class="l">Belum Dilaksanakan</div>
      </div>
    </div>

    <!-- Main Content Card -->
    <div class="main-card">
      <!-- Toolbar Filter & Search -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <div class="search-wrap">
            <i class="pi pi-search search-icon" />
            <InputText
              v-model="searchQuery"
              placeholder="Cari kode risiko, uraian, pemilik, atau kegiatan RTP..."
              class="search-input"
            />
            <button
              v-if="searchQuery"
              class="search-clear-btn"
              title="Bersihkan pencarian"
              @click="searchQuery = ''"
            >
              <i class="pi pi-times" />
            </button>
          </div>

          <Select
            v-model="filterStatus"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            class="filter-select"
          />

          <Select
            v-model="filterJenis"
            :options="[
              { label: 'Semua Jenis RTP (Risiko & CEE)', value: 'all' },
              { label: 'RTP atas CEE (Form 6)', value: 'cee' },
              { label: 'Strategis Pemda (Form 3.a)', value: 'strategis_pemda' },
              { label: 'Strategis OPD (Form 3.b)', value: 'strategis_opd' },
              { label: 'Operasional OPD (Form 3.c)', value: 'operasional_opd' },
            ]"
            optionLabel="label"
            optionValue="value"
            class="filter-select"
          />
        </div>

        <div class="summary-count">
          Menampilkan <strong>{{ filteredItems.length }}</strong> dari <strong>{{ items.length }}</strong> rencana pengendalian
        </div>
      </div>

      <!-- Data Table -->
      <DataTable
        :value="filteredItems"
        :loading="loading"
        stripedRows
        responsiveLayout="scroll"
        class="custom-table"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-shield text-4xl text-slate-300 mb-2" />
            <p class="empty-title">Tidak ada data rencana tindak pengendalian (RTP)</p>
            <p class="empty-desc">Pastikan risiko telah ditetapkan responnya pada menu Form 7 (Respon Risiko RTP).</p>
          </div>
        </template>

        <!-- No -->
        <Column header="No" :style="{ width: '50px', textAlign: 'center' }">
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

        <!-- Profil Risiko / Sub-unsur CEE -->
        <Column header="Profil Risiko / Aspek CEE" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="risk-profile-cell">
              <div v-if="data.source_type === 'cee'" class="cee-sublabel">
                <i class="pi pi-bookmark text-xs mr-1 text-purple-600" />{{ data.sasaran }}
              </div>
              <div class="risk-desc" :title="data.uraian_risiko">{{ data.uraian_risiko }}</div>
              <div class="risk-meta-row">
                <span v-if="data.pemilik_risiko" class="meta-item">
                  <i class="pi pi-user text-xs mr-1 text-slate-400" />{{ data.pemilik_risiko }}
                </span>
                <span v-if="data.analisis?.skala_risiko" class="meta-item meta-score">
                  Inheren: <strong>{{ data.analisis.skala_risiko }}</strong> ({{ data.analisis.level || 'Sedang' }})
                </span>
                <span v-else-if="data.source_type === 'cee'" class="meta-item meta-score cee-pill">
                  RTP atas CEE
                </span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Rencana Tindak Pengendalian (RTP) -->
        <Column header="Rencana Tindak (RTP)" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="rtp-cell">
              <div v-if="data.rtp?.rencana_tindak" class="rtp-text">
                {{ data.rtp.rencana_tindak }}
              </div>
              <div v-else class="text-xs text-amber-600 italic">
                <i class="pi pi-exclamation-circle mr-1" /> Belum ada rencana tindak
              </div>
              <div v-if="data.rtp?.target_mulai || data.rtp?.target_selesai" class="target-time-badge">
                <i class="pi pi-calendar text-xs mr-1 text-indigo-500" />
                Target: {{ formatDate(data.rtp.target_mulai) }} s.d. {{ formatDate(data.rtp.target_selesai) }}
              </div>
              <div v-else-if="data.rtp?.target_waktu" class="target-time-badge">
                <i class="pi pi-calendar text-xs mr-1 text-indigo-500" />
                Target: {{ formatDate(data.rtp.target_waktu) }}
              </div>
            </div>
          </template>
        </Column>

        <!-- Status Realisasi -->
        <Column header="Status Realisasi" :style="{ minWidth: '160px' }">
          <template #body="{ data }">
            <div class="status-cell">
              <span
                v-if="data.realisasi?.status_realisasi === 'selesai'"
                class="status-pill status-selesai"
              >
                <i class="pi pi-check-circle mr-1" /> Selesai
              </span>
              <span
                v-else-if="data.realisasi?.status_realisasi === 'proses'"
                class="status-pill status-proses"
              >
                <i class="pi pi-spin pi-spinner mr-1" /> Sedang Berjalan
              </span>
              <span
                v-else
                class="status-pill status-belum"
              >
                <i class="pi pi-clock mr-1" /> Belum Realisasi
              </span>

              <div v-if="data.realisasi?.tanggal_realisasi" class="tgl-realisasi-tag">
                <i class="pi pi-calendar-check text-xs text-emerald-600 mr-1" />
                {{ formatDate(data.realisasi.tanggal_realisasi) }}
              </div>
            </div>
          </template>
        </Column>

        <!-- Bukti Dukung (Eviden) -->
        <Column header="Bukti Dukung (Eviden)" :style="{ minWidth: '180px' }">
          <template #body="{ data }">
            <div class="evidence-cell">
              <!-- Berkas Upload -->
              <div v-if="data.realisasi?.bukti_nama && data.realisasi?.bukti_berkas_id" class="evidence-item">
                <a
                  :href="getEvidenceDownloadUrl(data, data.realisasi.bukti_berkas_id)"
                  target="_blank"
                  class="evidence-download-link"
                  title="Klik untuk mengunduh bukti dukung"
                >
                  <i class="pi pi-paperclip text-emerald-600" />
                  <span class="evidence-name">{{ data.realisasi.bukti_nama }}</span>
                  <i class="pi pi-download text-xs text-slate-400 ml-1" />
                </a>
              </div>

              <!-- Link URL eksternal jika ada -->
              <div v-if="data.realisasi?.bukti_link" class="evidence-item mt-1">
                <a
                  :href="data.realisasi.bukti_link"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="evidence-external-link"
                >
                  <i class="pi pi-external-link text-xs mr-1 text-blue-500" />
                  <span>Tautan Eviden</span>
                </a>
              </div>

              <!-- Fallback jika belum ada bukti -->
              <div
                v-if="!data.realisasi?.bukti_nama && !data.realisasi?.bukti_link"
                class="no-evidence-tag"
              >
                <i class="pi pi-file-excel mr-1 text-slate-300" />
                <span>Belum unggah bukti</span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Status Treated Risk -->
        <Column header="Treated Risk" :style="{ minWidth: '130px', textAlign: 'center' }">
          <template #body="{ data }">
            <div v-if="data.treated?.skala_treated" class="treated-status-cell">
              <span class="treated-done-pill">
                <i class="pi pi-sliders-v mr-1" /> Skor {{ data.treated.skala_treated }}
              </span>
              <span class="text-[10px] text-slate-400 block mt-0.5">{{ data.treated.level_treated }}</span>
            </div>
            <div v-else class="treated-pending-tag">
              <span class="text-xs text-slate-400 italic">Belum dinilai</span>
            </div>
          </template>
        </Column>

        <!-- Aksi -->
        <Column header="Aksi" :style="{ width: '130px', textAlign: 'center' }">
          <template #body="{ data }">
            <Button
              :label="data.realisasi?.status_realisasi === 'selesai' ? 'Edit Realisasi' : 'Isi Realisasi'"
              :icon="data.realisasi?.status_realisasi === 'selesai' ? 'pi pi-pencil' : 'pi pi-plus-circle'"
              :severity="data.realisasi?.status_realisasi === 'selesai' ? 'secondary' : 'success'"
              size="small"
              class="btn-action-realisasi"
              @click="openRealisasiDialog(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal Dialog Entri / Edit Realisasi RTP -->
    <Dialog
      v-model:visible="dialogVisible"
      modal
      header="Entri Realisasi Rencana Tindak Pengendalian"
      :style="{ width: '720px', maxWidth: '95vw' }"
      :closable="!saving"
    >
      <div v-if="selectedItem" class="dialog-body">
        <!-- Banner Konteks Risiko / CEE -->
        <div class="risk-context-banner">
          <div class="banner-top-row">
            <span class="badge-kode-lg">{{ selectedItem.kode_risiko }}</span>
            <span class="badge-jenis-lg" :class="`jenis-${selectedItem.jenis_risiko}`">
              {{ jenisLabels[selectedItem.jenis_risiko] || selectedItem.jenis_risiko }}
            </span>
            <span v-if="selectedItem.analisis?.skala_risiko" class="banner-score">
              Skala Inheren: <strong>{{ selectedItem.analisis?.skala_risiko || '-' }}</strong>
            </span>
            <span v-else-if="selectedItem.source_type === 'cee'" class="banner-score">
              Sub-unsur: <strong>{{ selectedItem.sasaran }}</strong>
            </span>
          </div>
          <div class="banner-risk-text">
            <small v-if="selectedItem.source_type === 'cee'" class="text-xs text-purple-700 font-semibold block mb-1">
              Kondisi Kurang Memadai:
            </small>
            {{ selectedItem.uraian_risiko }}
          </div>
          <div class="banner-rtp-box">
            <span class="banner-rtp-label"><i class="pi pi-shield mr-1" /> Rencana Tindak (RTP):</span>
            <span class="banner-rtp-val">{{ selectedItem.rtp?.rencana_tindak || 'Belum dirumuskan' }}</span>
            <span v-if="selectedItem.rtp?.target_mulai || selectedItem.rtp?.target_selesai" class="banner-rtp-target">
              (Target: {{ formatDate(selectedItem.rtp.target_mulai) }} s.d. {{ formatDate(selectedItem.rtp.target_selesai) }})
            </span>
            <span v-else-if="selectedItem.rtp?.target_waktu" class="banner-rtp-target">
              (Target: {{ formatDate(selectedItem.rtp.target_waktu) }})
            </span>
          </div>
        </div>

        <!-- Form Realisasi -->
        <div class="form-grid">
          <!-- Status Realisasi -->
          <div class="form-group">
            <label class="form-label required">Status Pelaksanaan Realisasi</label>
            <div class="status-options-grid">
              <button
                type="button"
                class="status-opt-btn"
                :class="{ active: form.status_realisasi === 'belum' }"
                @click="form.status_realisasi = 'belum'"
              >
                <i class="pi pi-clock" />
                <div class="opt-text">
                  <span class="opt-title">Belum Terealisasi</span>
                  <span class="opt-desc">Kegiatan belum dimulai</span>
                </div>
              </button>

              <button
                type="button"
                class="status-opt-btn"
                :class="{ active: form.status_realisasi === 'proses' }"
                @click="form.status_realisasi = 'proses'"
              >
                <i class="pi pi-spin pi-spinner" />
                <div class="opt-text">
                  <span class="opt-title">Sedang Berjalan</span>
                  <span class="opt-desc">Pelaksanaan bertahap / proses</span>
                </div>
              </button>

              <button
                type="button"
                class="status-opt-btn opt-success"
                :class="{ active: form.status_realisasi === 'selesai' }"
                @click="form.status_realisasi = 'selesai'"
              >
                <i class="pi pi-check-circle" />
                <div class="opt-text">
                  <span class="opt-title">Selesai Terealisasi</span>
                  <span class="opt-desc">Pengendalian tuntas dilaksanakan</span>
                </div>
              </button>
            </div>
          </div>

          <!-- Tanggal Realisasi -->
          <div class="form-group">
            <label class="form-label" :class="{ required: form.status_realisasi === 'selesai' }">
              Tanggal Realisasi Selesai / Aktual
            </label>
            <div class="input-date-wrap">
              <input
                type="date"
                v-model="form.tanggal_realisasi"
                class="native-date-input"
                :required="form.status_realisasi === 'selesai'"
              />
            </div>
            <small class="form-hint">
              Cantumkan tanggal penetapan, penerbitan dokumen, atau selesainya kegiatan pengendalian.
            </small>
          </div>

          <!-- Upload Berkas Bukti Dukung (Eviden) -->
          <div class="form-group">
            <label class="form-label">Berkas Bukti Dukung (Eviden Fisik / Digital)</label>
            
            <!-- Hidden input file -->
            <input
              type="file"
              ref="fileInput"
              class="hidden"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg"
              @change="handleFileSelect"
            />

            <!-- Preview berkas yang sudah ada atau baru dipilih -->
            <div v-if="form.bukti_nama && !form.hapus_bukti" class="current-file-box">
              <div class="current-file-info">
                <i class="pi pi-file-pdf text-xl text-rose-500" />
                <div class="file-text">
                  <span class="file-name">{{ form.bukti_nama }}</span>
                  <span class="file-sub">Berkas tersimpan di database</span>
                </div>
              </div>
              <div class="current-file-actions">
                <Button
                  label="Ganti Berkas"
                  icon="pi pi-upload"
                  size="small"
                  severity="secondary"
                  variant="outlined"
                  @click="triggerFileInput"
                />
                <Button
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  variant="text"
                  title="Hapus berkas"
                  @click="removeFile"
                />
              </div>
            </div>

            <!-- Preview berkas yang baru dipilih (belum disimpan) -->
            <div v-else-if="selectedFile" class="current-file-box new-file">
              <div class="current-file-info">
                <i class="pi pi-file text-xl text-emerald-600" />
                <div class="file-text">
                  <span class="file-name">{{ fileName }} ({{ fileSize }} KB)</span>
                  <span class="file-sub text-emerald-700">Berkas baru siap diunggah saat disimpan</span>
                </div>
              </div>
              <Button
                icon="pi pi-times"
                size="small"
                severity="danger"
                variant="text"
                title="Batal pilih"
                @click="removeFile"
              />
            </div>

            <!-- Upload drop area jika belum ada berkas -->
            <div v-else class="upload-dropzone" @click="triggerFileInput">
              <i class="pi pi-cloud-upload upload-icon" />
              <div class="upload-text">
                <strong>Klik untuk memilih berkas bukti dukung</strong>
                <span>Format: PDF, Word, Excel, Gambar (Maks. 5 MB)</span>
              </div>
            </div>
          </div>

          <!-- Tautan Bukti Online (Alternatif Cloud Link) -->
          <div class="form-group">
            <label class="form-label">Tautan / Link Cloud Dokumen (Opsional)</label>
            <div class="input-with-icon">
              <i class="pi pi-link input-icon" />
              <InputText
                v-model="form.bukti_link"
                placeholder="https://drive.google.com/... atau tautan sistem eksternal"
                class="form-input-text"
              />
            </div>
          </div>

          <!-- Uraian Hasil Pelaksanaan -->
          <div class="form-group">
            <div class="flex items-center justify-between mb-1">
              <label class="form-label mb-0">Uraian Hasil Pelaksanaan Realisasi</label>
              <Button
                label="🪄 Draf via AI"
                size="small"
                severity="help"
                variant="text"
                :loading="aiDrafting"
                class="btn-ai-draft"
                @click="draftHasilViaAi"
              />
            </div>
            <Textarea
              v-model="form.uraian_hasil"
              rows="3"
              placeholder="Contoh: Telah diterbitkan SOP Nomor 05/2026 tentang pemeliharaan server berkala, serta dilakukan pelatihan bagi 12 personil..."
              class="form-textarea"
            />
          </div>

          <!-- Hambatan / Kendala Pelaksanaan -->
          <div class="form-group">
            <label class="form-label">Hambatan / Kendala Pelaksanaan (Jika Ada)</label>
            <Textarea
              v-model="form.hambatan"
              rows="2"
              placeholder="Catat kendala keterlambatan atau hambatan koordinasi jika kegiatan belum selesai 100%..."
              class="form-textarea"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Batal"
            severity="secondary"
            variant="text"
            :disabled="saving"
            @click="dialogVisible = false"
          />
          <Button
            label="Simpan Realisasi & Bukti"
            icon="pi pi-save"
            severity="success"
            :loading="saving"
            @click="saveRealisasi"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.realisasi-rtp-page {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
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

.btn-link-treated {
  text-decoration: none;
}


/* Main Card & Table Toolbar */
.main-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-toolbar {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  background: #f8fafc;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.search-wrap {
  position: relative;
  min-width: 280px;
  flex: 1;
  max-width: 420px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.875rem;
}

.search-input {
  width: 100%;
  padding-left: 2.35rem;
  padding-right: 2rem;
  font-size: 0.875rem;
  border-radius: 0.5rem;
}

.search-clear-btn {
  position: absolute;
  right: 0.65rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
}

.filter-select {
  font-size: 0.875rem;
  border-radius: 0.5rem;
  min-width: 200px;
}

.summary-count {
  font-size: 0.825rem;
  color: #64748b;
}

/* Table Cells */
.index-num {
  font-weight: 600;
  color: #64748b;
  font-size: 0.825rem;
}

.kode-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.badge-kode {
  font-family: monospace;
  font-weight: 700;
  font-size: 0.8rem;
  color: #065f46;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  padding: 0.15rem 0.45rem;
  border-radius: 0.375rem;
  display: inline-block;
  width: fit-content;
}

.badge-jenis {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
  width: fit-content;
  text-transform: capitalize;
}

.jenis-strategis_pemda { background: #ede9fe; color: #6d28d9; }
.jenis-strategis_opd { background: #e0f2fe; color: #0369a1; }
.jenis-operasional_opd { background: #fef3c7; color: #b45309; }
.jenis-cee { background: #fdf4ff; color: #a21caf; border: 1px solid #f0abfc; }

.cee-sublabel {
  font-size: 0.73rem;
  font-weight: 600;
  color: #7c3aed;
  margin-bottom: 2px;
}

.cee-pill {
  background: #fdf4ff !important;
  color: #a21caf !important;
  font-weight: 600;
}

.risk-profile-cell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.risk-desc {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.risk-meta-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #64748b;
}

.meta-score {
  background: #f1f5f9;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
}

.rtp-cell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.rtp-text {
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.35;
}

.target-time-badge {
  font-size: 0.75rem;
  color: #4f46e5;
  background: #eef2ff;
  padding: 0.15rem 0.5rem;
  border-radius: 0.375rem;
  width: fit-content;
  display: flex;
  align-items: center;
}

/* Status Cell */
.status-cell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  width: fit-content;
}

.status-selesai { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
.status-proses { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.status-belum { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }

.tgl-realisasi-tag {
  font-size: 0.75rem;
  color: #334155;
  display: flex;
  align-items: center;
}

/* Evidence Cell */
.evidence-cell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.evidence-download-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.775rem;
  font-weight: 600;
  color: #065f46;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  padding: 0.25rem 0.55rem;
  border-radius: 0.375rem;
  text-decoration: none;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-download-link:hover {
  background: #d1fae5;
  color: #047857;
}

.evidence-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-external-link {
  font-size: 0.75rem;
  color: #2563eb;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.evidence-external-link:hover {
  text-decoration: underline;
}

.no-evidence-tag {
  font-size: 0.75rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
}

/* Treated Status Cell */
.treated-done-pill {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6d28d9;
  background: #f5f3ff;
  border: 1px solid #ddd6fe;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
}

.btn-action-realisasi {
  font-size: 0.775rem;
  white-space: nowrap;
}

/* Dialog Styles */
.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.risk-context-banner {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.banner-top-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.badge-kode-lg {
  font-family: monospace;
  font-weight: 800;
  font-size: 0.9rem;
  color: #065f46;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  padding: 0.2rem 0.6rem;
  border-radius: 0.375rem;
}

.badge-jenis-lg {
  font-size: 0.75rem;
  font-weight: 600;
  background: #ede9fe;
  color: #6d28d9;
  padding: 0.2rem 0.55rem;
  border-radius: 0.375rem;
}

.banner-score {
  font-size: 0.8rem;
  color: #475569;
  margin-left: auto;
}

.banner-risk-text {
  font-size: 0.925rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.35;
}

.banner-rtp-box {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 0.5rem;
  padding: 0.65rem 0.85rem;
  font-size: 0.825rem;
  color: #334155;
  line-height: 1.4;
}

.banner-rtp-label {
  font-weight: 700;
  color: #4338ca;
  margin-right: 0.35rem;
}

.banner-rtp-target {
  color: #64748b;
  font-style: italic;
  margin-left: 0.35rem;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-label {
  font-size: 0.825rem;
  font-weight: 700;
  color: #334155;
}

.form-label.required::after {
  content: ' *';
  color: #dc2626;
}

.form-hint {
  font-size: 0.75rem;
  color: #64748b;
}

/* Status Options Grid */
.status-options-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.status-opt-btn {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 0.65rem;
  padding: 0.75rem 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.status-opt-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.status-opt-btn.active {
  border-color: #059669;
  background: #ecfdf5;
  box-shadow: 0 0 0 1px #059669;
}

.status-opt-btn.active i {
  color: #059669;
}

.opt-text {
  display: flex;
  flex-direction: column;
}

.opt-title {
  font-size: 0.825rem;
  font-weight: 700;
  color: #1e293b;
}

.opt-desc {
  font-size: 0.7rem;
  color: #64748b;
}

.native-date-input {
  width: 100%;
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  color: #1e293b;
  outline: none;
  font-family: inherit;
}

.native-date-input:focus {
  border-color: #059669;
  box-shadow: 0 0 0 1px #059669;
}

/* File Upload Components */
.upload-dropzone {
  border: 2px dashed #cbd5e1;
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  background: #f8fafc;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-dropzone:hover {
  border-color: #059669;
  background: #ecfdf5;
}

.upload-icon {
  font-size: 2rem;
  color: #64748b;
}

.upload-dropzone:hover .upload-icon {
  color: #059669;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.825rem;
  color: #475569;
}

.current-file-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.65rem;
  padding: 0.75rem 1rem;
}

.current-file-box.new-file {
  background: #ecfdf5;
  border-color: #a7f3d0;
}

.current-file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-text {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e293b;
}

.file-sub {
  font-size: 0.725rem;
  color: #64748b;
}

.current-file-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 0.85rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

.form-input-text {
  width: 100%;
  padding-left: 2.25rem;
  font-size: 0.875rem;
}

.form-textarea {
  width: 100%;
  font-size: 0.875rem;
  border-radius: 0.5rem;
}

.btn-ai-draft {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

@media (max-width: 768px) {
  .status-options-grid {
    grid-template-columns: 1fr;
  }
}
</style>
