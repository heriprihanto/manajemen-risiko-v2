<script setup>
import { computed, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import DatePicker from 'primevue/datepicker'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { formatDate, parseDateOnly, toDateOnlyString } from '@/utils/date'
import AppLoader from '@/components/AppLoader.vue'

const toast = useToast()
const ctx = useContextStore()

const loading = ref(false)
const saving = ref(false)
const items = ref([])
const error = ref('')

const searchQuery = ref('')
const filterStatus = ref('all') // all, selesai, belum

// Dialog Input/Edit Realisasi Infokom
const dialogVisible = ref(false)
const selectedItem = ref(null)
const formError = ref('')

const form = ref({
  realisasi_mulai: null,
  realisasi_selesai: null,
  keterangan: '',
  bukti_list: [], // Array of { nama: '', link: '' }
})

function parseEvidenceList(buktiLink, buktiNama) {
  if (!buktiLink) return []
  try {
    const parsed = JSON.parse(buktiLink)
    if (Array.isArray(parsed)) {
      return parsed.map((item) => ({
        nama: item.nama || '',
        link: item.link || '',
      }))
    }
  } catch {
    // bukan JSON, format string URL tunggal legacy
  }
  return [
    {
      nama: buktiNama || 'Bukti Dukung',
      link: buktiLink,
    },
  ]
}

function addEvidenceRow() {
  form.value.bukti_list.push({ nama: '', link: '' })
}

function removeEvidenceRow(idx) {
  form.value.bukti_list.splice(idx, 1)
  if (!form.value.bukti_list.length) {
    form.value.bukti_list.push({ nama: '', link: '' })
  }
}

const statusOptions = [
  { value: 'all', label: 'Semua Status Realisasi' },
  { value: 'selesai', label: 'Sudah Terealisasi' },
  { value: 'belum', label: 'Belum Terealisasi' },
]

async function loadData() {
  if (!ctx.opdId || !ctx.tahun) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/monitoring/infokom', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    items.value = Array.isArray(data) ? data : []
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal memuat data Realisasi Infokom'
    error.value = err
    toast.add({ severity: 'error', summary: 'Gagal Memuat', detail: err, life: 4000 })
  } finally {
    loading.value = false
  }
}

// Watch OPD dan tahun
watch([() => ctx.opdId, () => ctx.tahun], loadData, { immediate: true })

// Ringkasan KPI
const summary = computed(() => {
  const total = items.value.length
  let selesai = 0
  for (const it of items.value) {
    if (it.realisasi_waktu || it.realisasi_mulai) {
      selesai++
    }
  }
  const belum = total - selesai
  const persen = total > 0 ? Math.round((selesai / total) * 100) : 0
  return { total, selesai, belum, persen }
})

// Filter data tabel
const filteredItems = computed(() => {
  return items.value.filter((it) => {
    const isDone = Boolean(it.realisasi_waktu || it.realisasi_mulai)
    if (filterStatus.value === 'selesai' && !isDone) return false
    if (filterStatus.value === 'belum' && isDone) return false

    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchKode = it.kode_risiko?.toLowerCase().includes(q)
      const matchUraian = it.uraian_risiko?.toLowerCase().includes(q)
      const matchKegiatan = it.kegiatan_pengendalian?.toLowerCase().includes(q)
      const matchMedia = it.media_bentuk?.toLowerCase().includes(q)
      const matchPenyedia = it.penyedia_informasi?.toLowerCase().includes(q)
      const matchPenerima = it.penerima_informasi?.toLowerCase().includes(q)
      const matchKeterangan = it.keterangan?.toLowerCase().includes(q)
      const matchBukti = it.bukti_dukung?.toLowerCase().includes(q) || it.bukti_nama?.toLowerCase().includes(q)
      if (
        !matchKode &&
        !matchUraian &&
        !matchKegiatan &&
        !matchMedia &&
        !matchPenyedia &&
        !matchPenerima &&
        !matchKeterangan &&
        !matchBukti
      ) {
        return false
      }
    }
    return true
  })
})

function parseDatesFromRow(row) {
  let mulai = row.realisasi_mulai ? parseDateOnly(row.realisasi_mulai) : null
  let selesai = row.realisasi_selesai ? parseDateOnly(row.realisasi_selesai) : null

  if (!mulai && !selesai && row.realisasi_waktu) {
    const rangeMatch = row.realisasi_waktu.match(/^(\d{4}-\d{2}-\d{2})\s+s\.d\.\s+(\d{4}-\d{2}-\d{2})$/)
    const singleMatch = row.realisasi_waktu.match(/^(\d{4}-\d{2}-\d{2})$/)
    if (rangeMatch) {
      mulai = parseDateOnly(rangeMatch[1])
      selesai = parseDateOnly(rangeMatch[2])
    } else if (singleMatch) {
      mulai = parseDateOnly(singleMatch[1])
      selesai = parseDateOnly(singleMatch[1])
    }
  }
  return { mulai, selesai }
}

function openEditDialog(row) {
  selectedItem.value = row
  formError.value = ''
  const { mulai, selesai } = parseDatesFromRow(row)

  let list = parseEvidenceList(row.bukti_dukung, row.bukti_nama)
  if (!list.length) {
    list = [{ nama: '', link: '' }]
  }

  form.value = {
    realisasi_mulai: mulai,
    realisasi_selesai: selesai,
    keterangan: row.keterangan || '',
    bukti_list: list,
  }
  dialogVisible.value = true
}

function setQuickToday() {
  const now = new Date()
  form.value.realisasi_mulai = now
  form.value.realisasi_selesai = now
}

function copyPlanDates() {
  if (!selectedItem.value) return
  let mulai = selectedItem.value.rencana_mulai ? parseDateOnly(selectedItem.value.rencana_mulai) : null
  let selesai = selectedItem.value.rencana_selesai ? parseDateOnly(selectedItem.value.rencana_selesai) : null

  if (!mulai && !selesai && selectedItem.value.rencana_waktu) {
    const rangeMatch = selectedItem.value.rencana_waktu.match(/^(\d{4}-\d{2}-\d{2})\s+s\.d\.\s+(\d{4}-\d{2}-\d{2})$/)
    const singleMatch = selectedItem.value.rencana_waktu.match(/^(\d{4}-\d{2}-\d{2})$/)
    if (rangeMatch) {
      mulai = parseDateOnly(rangeMatch[1])
      selesai = parseDateOnly(rangeMatch[2])
    } else if (singleMatch) {
      mulai = parseDateOnly(singleMatch[1])
      selesai = parseDateOnly(singleMatch[1])
    }
  }

  if (mulai) form.value.realisasi_mulai = mulai
  if (selesai) form.value.realisasi_selesai = selesai
}

function openTestLink(url) {
  if (!url) return
  let finalUrl = url.trim()
  if (!/^https?:\/\//i.test(finalUrl)) {
    finalUrl = 'https://' + finalUrl
  }
  window.open(finalUrl, '_blank', 'noopener,noreferrer')
}

async function saveRealisasi() {
  if (!selectedItem.value) return
  formError.value = ''

  if (
    form.value.realisasi_mulai &&
    form.value.realisasi_selesai &&
    form.value.realisasi_selesai < form.value.realisasi_mulai
  ) {
    formError.value = 'Sampai Tanggal tidak boleh mendahului Dari Tanggal'
    return
  }

  // Filter bukti yang memiliki link
  const validEvidences = form.value.bukti_list
    .map((b) => {
      let lk = (b.link || '').trim()
      if (lk && !/^https?:\/\//i.test(lk)) {
        lk = 'https://' + lk
      }
      return {
        nama: (b.nama || '').trim(),
        link: lk,
      }
    })
    .filter((b) => Boolean(b.link))

  // Lengkapi nama default jika belum terisi
  validEvidences.forEach((b, i) => {
    if (!b.nama) b.nama = `Bukti Dukung ${i + 1}`
  })

  saving.value = true
  try {
    const payload = {
      realisasi_mulai: toDateOnlyString(form.value.realisasi_mulai),
      realisasi_selesai: toDateOnlyString(form.value.realisasi_selesai),
      keterangan: form.value.keterangan?.trim() || null,
      bukti_dukung: validEvidences.length ? validEvidences : null,
      bukti_nama: validEvidences[0]?.nama || null,
    }

    await api.put(`/monitoring/infokom/${selectedItem.value.id}`, payload)
    toast.add({
      severity: 'success',
      summary: 'Tersimpan',
      detail: 'Realisasi Infokom berhasil diperbarui (Form 8).',
      life: 3000,
    })
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal menyimpan realisasi Infokom'
    formError.value = err
    toast.add({ severity: 'error', summary: 'Gagal Menyimpan', detail: err, life: 4000 })
  } finally {
    saving.value = false
  }
}

async function resetRealisasi() {
  if (!selectedItem.value) return
  saving.value = true
  try {
    const payload = {
      realisasi_mulai: null,
      realisasi_selesai: null,
      realisasi_waktu: null,
      keterangan: null,
      bukti_dukung: null,
      bukti_nama: null,
    }
    await api.put(`/monitoring/infokom/${selectedItem.value.id}`, payload)
    toast.add({
      severity: 'info',
      summary: 'Direset',
      detail: 'Data realisasi telah dikosongkan.',
      life: 3000,
    })
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal mereset realisasi Infokom'
    toast.add({ severity: 'error', summary: 'Gagal', detail: err, life: 4000 })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="realisasi-infokom-page">
    <!-- Header Section (Style Realisasi RTP) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-comments"></i>
        </div>
        <div>
          <h1 class="page-title">Realisasi Informasi & Komunikasi (Infokom)</h1>
          <p class="page-desc">
            Pencatatan realisasi atas pengkomunikasian kegiatan pengendalian yang dibangun (melengkapi Form 8)
          </p>
        </div>
      </div>
      <div class="header-actions">
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

    <!-- Alert Error Jika Ada -->
    <div v-if="error" class="alert-box alert-error" role="alert">
      <i class="pi pi-exclamation-circle" />
      <span>{{ error }}</span>
      <Button label="Coba Lagi" text size="small" @click="loadData" />
    </div>

    <!-- Stat Cards Header (Style Realisasi RTP / Laporan Rekapitulasi) -->
    <div class="stat-grid no-print" style="margin-bottom: 4px;">
      <div class="stat">
        <div class="v">{{ summary.total }}</div>
        <div class="l">Total Kegiatan Infokom</div>
      </div>

      <div class="stat">
        <div class="v">
          {{ summary.selesai }} <small>({{ summary.persen }}%)</small>
        </div>
        <div class="l">Sudah Terealisasi</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.belum }}</div>
        <div class="l">Belum Terealisasi</div>
      </div>
    </div>

    <!-- Main Card & Table Toolbar -->
    <div class="main-card">
      <!-- Toolbar Filter & Search -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <div class="search-wrap">
            <i class="pi pi-search search-icon" />
            <InputText
              v-model="searchQuery"
              placeholder="Cari kegiatan, media, penyedia, keterangan, bukti..."
              class="search-input"
            />
            <button
              v-if="searchQuery"
              class="search-clear-btn"
              type="button"
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
        </div>

        <div class="summary-count">
          Menampilkan <strong>{{ filteredItems.length }}</strong> dari <strong>{{ items.length }}</strong> kegiatan Infokom
        </div>
      </div>

      <!-- Table View -->
      <DataTable
        :value="filteredItems"
        :loading="loading"
        stripedRows
        responsiveLayout="scroll"
        class="custom-datatable"
        emptyMessage="Tidak ada data kegiatan Infokom yang ditemukan."
      >
        <Column header="No" :style="{ width: '50px', textAlign: 'center' }">
          <template #body="{ index }">
            <span class="row-number">{{ index + 1 }}</span>
          </template>
        </Column>

        <Column header="Risiko & RTP" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="cell-risk">
              <span v-if="data.kode_risiko" class="kode-badge">{{ data.kode_risiko }}</span>
              <div class="risk-desc">{{ data.uraian_risiko || '—' }}</div>
              <div class="rtp-box">
                <i class="pi pi-shield rtp-icon" />
                <span class="rtp-text"><strong>RTP:</strong> {{ data.kegiatan_pengendalian || '—' }}</span>
              </div>
            </div>
          </template>
        </Column>

        <Column header="Sarana & Pihak Terkait" :style="{ minWidth: '200px' }">
          <template #body="{ data }">
            <div class="media-info">
              <div class="media-title">
                <i class="pi pi-megaphone media-icon" />
                <strong>{{ data.media_bentuk || '—' }}</strong>
              </div>
              <div v-if="data.penyedia_informasi || data.penerima_informasi" class="parties-flow">
                <span class="provider" :title="'Penyedia: ' + data.penyedia_informasi">
                  <i class="pi pi-arrow-circle-up text-primary mr-1" />{{ data.penyedia_informasi || '—' }}
                </span>
                <i class="pi pi-arrow-right flow-arrow" />
                <span class="receiver" :title="'Penerima: ' + data.penerima_informasi">
                  <i class="pi pi-arrow-circle-down text-info mr-1" />{{ data.penerima_informasi || '—' }}
                </span>
              </div>
            </div>
          </template>
        </Column>

        <Column header="Waktu Rencana" :style="{ minWidth: '130px' }">
          <template #body="{ data }">
            <span class="text-sm text-slate-700">
              <i class="pi pi-calendar text-slate-400 mr-1" />
              {{ formatDate(data.rencana_waktu) }}
            </span>
          </template>
        </Column>

        <Column header="Waktu Realisasi" :style="{ minWidth: '150px' }">
          <template #body="{ data }">
            <div v-if="data.realisasi_waktu || data.realisasi_mulai" class="status-realisasi-badge done">
              <i class="pi pi-check-circle" />
              <span>{{ formatDate(data.realisasi_waktu) }}</span>
            </div>
            <div v-else class="status-realisasi-badge pending">
              <i class="pi pi-clock" />
              <span>Belum Terealisasi</span>
            </div>
          </template>
        </Column>

        <Column header="Keterangan" :style="{ minWidth: '180px' }">
          <template #body="{ data }">
            <span v-if="data.keterangan" class="keterangan-text">
              {{ data.keterangan }}
            </span>
            <span v-else class="text-muted text-xs italic">Belum diisi</span>
          </template>
        </Column>

        <Column header="Bukti Dukung" :style="{ minWidth: '220px' }">
          <template #body="{ data }">
            <div class="evidence-cell">
              <template v-if="parseEvidenceList(data.bukti_dukung, data.bukti_nama).length">
                <div
                  v-for="(ev, evIdx) in parseEvidenceList(data.bukti_dukung, data.bukti_nama)"
                  :key="evIdx"
                  class="evidence-item mb-1"
                >
                  <a
                    :href="ev.link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="evidence-external-link"
                    :title="ev.link"
                  >
                    <i class="pi pi-link text-xs mr-1 text-emerald-600" />
                    <span>{{ ev.nama || 'Tautan Eviden ' + (evIdx + 1) }}</span>
                    <i class="pi pi-external-link text-[10px] text-slate-400 ml-1" />
                  </a>
                </div>
              </template>
              <span v-else class="text-muted text-xs italic">Tidak ada</span>
            </div>
          </template>
        </Column>

        <Column header="Aksi" :style="{ width: '130px', textAlign: 'center' }">
          <template #body="{ data }">
            <Button
              v-if="data.realisasi_waktu || data.realisasi_mulai"
              label="Ubah"
              icon="pi pi-pencil"
              size="small"
              class="btn-action btn-edit"
              @click="openEditDialog(data)"
            />
            <Button
              v-else
              label="Entri"
              icon="pi pi-plus"
              size="small"
              class="btn-action btn-entry"
              @click="openEditDialog(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog Modal Entri / Edit Realisasi Infokom -->
    <Dialog
      v-model:visible="dialogVisible"
      header="Entri Realisasi Infokom (Form 8)"
      modal
      :style="{ width: '680px', maxWidth: '95vw' }"
      class="dialog-realisasi-infokom"
    >
      <div v-if="selectedItem" class="dialog-body">
        <!-- Context Card -->
        <div class="dialog-context-box">
          <div class="context-header">
            <span v-if="selectedItem.kode_risiko" class="kode-pill">{{ selectedItem.kode_risiko }}</span>
            <span class="context-media">
              <i class="pi pi-megaphone" /> {{ selectedItem.media_bentuk || 'Sarana Komunikasi' }}
            </span>
          </div>
          <div class="context-desc">
            <strong>Risiko:</strong> {{ selectedItem.uraian_risiko || '—' }}
          </div>
          <div class="context-rtp">
            <strong>Kegiatan Pengendalian (RTP):</strong> {{ selectedItem.kegiatan_pengendalian || '—' }}
          </div>
          <div class="context-meta-row">
            <div class="context-meta-item">
              <span class="meta-label">Penyedia:</span>
              <span class="meta-val">{{ selectedItem.penyedia_informasi || '—' }}</span>
            </div>
            <div class="context-meta-item">
              <span class="meta-label">Penerima:</span>
              <span class="meta-val">{{ selectedItem.penerima_informasi || '—' }}</span>
            </div>
            <div class="context-meta-item">
              <span class="meta-label">Target Rencana:</span>
              <span class="meta-val">{{ formatDate(selectedItem.rencana_waktu) }}</span>
            </div>
          </div>
        </div>

        <!-- Alert Error Form -->
        <div v-if="formError" class="alert-box alert-error" role="alert">
          <i class="pi pi-exclamation-triangle" />
          <span>{{ formError }}</span>
        </div>

        <!-- Form Input -->
        <form id="form-realisasi-infokom" @submit.prevent="saveRealisasi">
          <!-- Rentang Tanggal Realisasi -->
          <div class="form-group">
            <div class="form-label-row">
              <label class="form-label required">
                <i class="pi pi-calendar mr-1 text-primary" />
                Tanggal Realisasi (Dari Tanggal s.d. Sampai Tanggal):
              </label>
              <div class="date-shortcuts">
                <button type="button" class="btn-shortcut" @click="setQuickToday">Hari Ini</button>
                <button
                  v-if="selectedItem.rencana_mulai || selectedItem.rencana_waktu"
                  type="button"
                  class="btn-shortcut"
                  @click="copyPlanDates"
                >
                  Sama dg Rencana
                </button>
              </div>
            </div>

            <div class="date-range-grid">
              <div class="date-col">
                <label for="realisasi_mulai" class="sub-label">Dari Tanggal</label>
                <DatePicker
                  id="realisasi_mulai"
                  v-model="form.realisasi_mulai"
                  dateFormat="dd-mm-yy"
                  showIcon
                  showButtonBar
                  placeholder="Pilih tanggal mulai"
                  :maxDate="form.realisasi_selesai || undefined"
                  class="w-full"
                />
              </div>
              <div class="date-col">
                <label for="realisasi_selesai" class="sub-label">Sampai Tanggal</label>
                <DatePicker
                  id="realisasi_selesai"
                  v-model="form.realisasi_selesai"
                  dateFormat="dd-mm-yy"
                  showIcon
                  showButtonBar
                  placeholder="Pilih tanggal selesai"
                  :minDate="form.realisasi_mulai || undefined"
                  class="w-full"
                />
              </div>
            </div>
            <small class="form-hint">
              Pilih tanggal pelaksanaan pengkomunikasian pengendalian. Jika pelaksanaan berlangsung satu hari, samakan tanggal mulai dan selesai.
            </small>
          </div>

          <!-- Keterangan -->
          <div class="form-group">
            <label for="infokom_keterangan" class="form-label">
              <i class="pi pi-file-edit mr-1 text-primary" />
              Keterangan / Catatan Realisasi:
            </label>
            <Textarea
              id="infokom_keterangan"
              v-model="form.keterangan"
              rows="3"
              placeholder="Contoh: Telah dilaksanakan sosialisasi secara daring melalui Zoom dihadiri 30 peserta pada seksi teknis terkait..."
              class="w-full"
            />
            <small class="form-hint">
              Uraikan ringkasan pelaksanaan, kesepakatan, atau catatan relevan lainnya.
            </small>
          </div>

          <!-- Berkas Bukti Dukung (Bisa Lebih Dari Satu) -->
          <div class="form-group mb-0">
            <div class="flex items-center justify-between mb-1">
              <label class="form-label mb-0">
                <i class="pi pi-link mr-1 text-primary" />
                Berkas Bukti Dukung (Eviden Fisik / Digital):
              </label>
              <Button
                label="Tambah Tautan Bukti Lainnya"
                icon="pi pi-plus"
                size="small"
                severity="success"
                outlined
                class="btn-add-evidence"
                type="button"
                @click="addEvidenceRow"
              />
            </div>
            <p class="form-hint mb-3">
              Cantumkan satu atau beberapa tautan berkas bukti dukung (Google Drive, OneDrive, Dropbox, dsb) beserta nama dokumennya.
            </p>

            <div class="evidence-list-wrap">
              <div
                v-for="(ev, idx) in form.bukti_list"
                :key="idx"
                class="evidence-row-card"
              >
                <div class="evidence-row-header">
                  <span class="evidence-row-num">#{{ idx + 1 }}</span>
                  <span class="evidence-row-title">Bukti Dukung {{ idx + 1 }}</span>
                  <Button
                    v-if="form.bukti_list.length > 1"
                    icon="pi pi-trash"
                    severity="danger"
                    text
                    rounded
                    size="small"
                    class="btn-remove-evidence"
                    title="Hapus baris bukti dukung ini"
                    type="button"
                    @click="removeEvidenceRow(idx)"
                  />
                </div>

                <div class="evidence-fields-grid">
                  <div class="form-subgroup">
                    <label class="field-sublabel">
                      Nama Berkas Bukti Dukung
                    </label>
                    <InputText
                      v-model="ev.nama"
                      :placeholder="`Contoh: Undangan, Notulensi, Dokumentasi Foto ${idx + 1}`"
                      class="form-input-text-sub"
                    />
                  </div>

                  <div class="form-subgroup">
                    <label class="field-sublabel">
                      Tautan / Link Eviden (URL)
                    </label>
                    <div class="input-with-icon">
                      <i class="pi pi-link input-icon" />
                      <InputText
                        v-model="ev.link"
                        placeholder="https://drive.google.com/..."
                        class="form-input-text form-input-text-sub"
                      />
                      <Button
                        v-if="ev.link"
                        icon="pi pi-external-link"
                        size="small"
                        severity="secondary"
                        text
                        type="button"
                        class="btn-test-link"
                        title="Uji coba buka link di tab baru"
                        @click="openTestLink(ev.link)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            v-if="selectedItem?.realisasi_waktu || selectedItem?.realisasi_mulai"
            label="Hapus / Reset Realisasi"
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            :disabled="saving"
            @click="resetRealisasi"
          />
          <div class="footer-right">
            <Button
              label="Batal"
              icon="pi pi-times"
              severity="secondary"
              text
              :disabled="saving"
              @click="dialogVisible = false"
            />
            <Button
              label="Simpan Realisasi"
              icon="pi pi-check"
              class="btn-save"
              :loading="saving"
              form="form-realisasi-infokom"
              type="submit"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.realisasi-infokom-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Page Header (Style Realisasi RTP) */
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
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
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

/* Alert */
.alert-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.88rem;
}

.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

/* Main Card & Table Toolbar (Style Realisasi RTP) */
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

/* DataTable Custom */
.row-number {
  font-weight: 600;
  color: #64748b;
  font-size: 0.85rem;
}

.cell-risk {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.kode-badge {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.72rem;
  font-weight: 700;
  background: #e0e7ff;
  color: #4338ca;
  padding: 2px 7px;
  border-radius: 4px;
}

.risk-desc {
  font-size: 0.88rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
}

.rtp-box {
  display: flex;
  align-items: flex-start;
  gap: 5px;
  background: #f8fafc;
  padding: 6px 8px;
  border-radius: 6px;
  border-left: 3px solid #0284c7;
  font-size: 0.8rem;
  color: #334155;
  line-height: 1.35;
}

.rtp-icon {
  color: #0284c7;
  margin-top: 2px;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.media-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.media-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.86rem;
  color: #0f172a;
}

.media-icon {
  color: #0284c7;
  font-size: 0.9rem;
}

.parties-flow {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 0.78rem;
  color: #475569;
}

.provider, .receiver {
  display: inline-flex;
  align-items: center;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}

.flow-arrow {
  color: #94a3b8;
  font-size: 0.75rem;
}

.status-realisasi-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 9px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.3;
}

.status-realisasi-badge.done {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.status-realisasi-badge.pending {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.keterangan-text {
  font-size: 0.82rem;
  color: #334155;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.bukti-link-wrap {
  display: inline-flex;
}

.btn-bukti-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 4px 8px;
  border-radius: 5px;
  text-decoration: none;
  transition: all 0.15s ease;
}

.btn-bukti-link:hover {
  background: #dbeafe;
  color: #1d4ed8;
}

.btn-action {
  font-weight: 600;
  width: 100%;
}

.btn-entry {
  background: #0284c7 !important;
  border-color: #0284c7 !important;
  color: #ffffff !important;
}

.btn-entry:hover {
  background: #0369a1 !important;
}

.btn-edit {
  background: #f8fafc !important;
  border-color: #cbd5e1 !important;
  color: #334155 !important;
}

.btn-edit:hover {
  background: #f1f5f9 !important;
  color: #0f172a !important;
}

/* Dialog Styles */
.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-context-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.86rem;
}

.context-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.kode-pill {
  font-size: 0.75rem;
  font-weight: 700;
  background: #e0e7ff;
  color: #3730a3;
  padding: 2px 7px;
  border-radius: 4px;
}

.context-media {
  font-weight: 700;
  color: #0284c7;
}

.context-desc, .context-rtp {
  color: #334155;
  line-height: 1.4;
}

.context-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 4px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  font-size: 0.8rem;
}

.context-meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.meta-label {
  color: #64748b;
  font-weight: 600;
}

.meta-val {
  color: #0f172a;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.form-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  font-size: 0.88rem;
  color: #1e293b;
}

.form-label.required::after {
  content: " *";
  color: #dc2626;
}

.date-shortcuts {
  display: flex;
  gap: 6px;
}

.btn-shortcut {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #475569;
  border-radius: 4px;
  font-size: 0.74rem;
  font-weight: 600;
  padding: 2px 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-shortcut:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.date-range-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.date-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sub-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
}

.link-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.link-input {
  font-size: 0.88rem;
}

/* Evidence Cell in Table */
.evidence-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.evidence-item {
  display: flex;
  align-items: center;
}

.evidence-external-link {
  font-size: 0.78rem;
  color: #2563eb;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  line-height: 1.3;
}

.evidence-external-link:hover {
  text-decoration: underline;
  color: #1d4ed8;
}

/* Multi-evidence Form Cards */
.btn-add-evidence {
  font-size: 0.78rem !important;
}

.evidence-list-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.evidence-row-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 0.85rem;
  transition: border-color 0.15s ease;
}

.evidence-row-card:hover {
  border-color: #cbd5e1;
}

.evidence-row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px dashed #e2e8f0;
}

.evidence-row-num {
  font-size: 0.72rem;
  font-weight: 700;
  color: #059669;
  background: #ecfdf5;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.evidence-row-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
  margin-left: 0.4rem;
  flex: 1;
}

.btn-remove-evidence {
  width: 26px !important;
  height: 26px !important;
  padding: 0 !important;
}

.evidence-fields-grid {
  display: grid;
  grid-template-columns: 1fr 1.35fr;
  gap: 0.75rem;
}

.field-sublabel {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.3rem;
}

.form-input-text-sub {
  width: 100%;
  font-size: 0.85rem;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 0.85rem;
  color: #94a3b8;
  font-size: 0.875rem;
  pointer-events: none;
}

.form-input-text {
  width: 100%;
  padding-left: 2.25rem !important;
  padding-right: 2.5rem !important;
  font-size: 0.875rem;
}

.btn-test-link {
  position: absolute;
  right: 0.25rem;
  top: 50%;
  transform: translateY(-50%);
}

@media (max-width: 640px) {
  .evidence-fields-grid {
    grid-template-columns: 1fr;
  }
}

.form-hint {
  font-size: 0.78rem;
  color: #64748b;
  line-height: 1.4;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.btn-save {
  background: #0284c7 !important;
  border-color: #0284c7 !important;
  font-weight: 600;
}

.btn-save:hover {
  background: #0369a1 !important;
}

@media (max-width: 768px) {
  .date-range-grid {
    grid-template-columns: 1fr;
  }
}
</style>
