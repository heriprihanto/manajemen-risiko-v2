<script setup>
import { computed, onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import ToggleSwitch from 'primevue/toggleswitch'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()

const toast = useToast()
const confirm = useConfirm()

// State data & filter
const items = ref([])
const totalRecords = ref(0)
const loading = ref(false)
const saving = ref(false)

// Pagination state
const page = ref(1)
const perPage = ref(25)

// Filter & search
const search = ref('')
const selectedKategori = ref(null)
const selectedStatus = ref(null)
const kategoriList = ref([])


// Dialog state
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  no: null,
  kode_risiko: '',
  nama_klp: 'Kota Tegal',
  kategori_risiko: '',
  nama_risiko: '',
  deskripsi: '',
  aktif: true,
})
const customKategori = ref('')
const isCustomKategori = ref(false)

// AI Risk Generator state
const aiDialogVisible = ref(false)
const aiSasaran = ref('')
const aiGenerating = ref(false)
const aiSuggestions = ref([])

const quickSasaranTemplates = [
  'Peningkatan kualitas pelayanan perizinan dan kemudahan berusaha',
  'Peningkatan derajat kesehatan masyarakat dan mutu layanan Puskesmas',
  'Pengelolaan belanja modal infrastruktur jalan, drainase, dan jembatan',
  'Pengelolaan sistem informasi administrasi kepegawaian (SIMPEG/SIASN)',
  'Optimalisasi penerimaan pendapatan asli daerah (PAD) dari pajak & retribusi',
]

async function generateAiRisks() {
  if (!aiSasaran.value.trim()) return
  aiGenerating.value = true
  aiSuggestions.value = []
  try {
    const { data } = await api.post('/ai/generate-risk', {
      sasaran: aiSasaran.value.trim(),
    })
    aiSuggestions.value = data.suggestions || []
    if (!aiSuggestions.value.length) {
      toast.add({ severity: 'warn', summary: 'AI Generator', detail: 'Tidak ada saran risiko yang terstruktur.', life: 3000 })
    }
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal generate risiko'
    toast.add({ severity: 'error', summary: 'AI Error', detail: err, life: 4000 })
  } finally {
    aiGenerating.value = false
  }
}

async function useAiSuggestion(sug) {
  form.value.nama_risiko = sug.uraian_risiko || ''
  const descParts = []
  if (sug.penyebab) descParts.push(`Penyebab: ${sug.penyebab}`)
  if (sug.dampak) descParts.push(`Dampak: ${sug.dampak}`)
  form.value.deskripsi = descParts.join('\n')

  if (sug.kategori) {
    const matched = kategoriList.value.find(
      (k) =>
        k.toLowerCase().includes(sug.kategori.toLowerCase()) ||
        sug.kategori.toLowerCase().includes(k.toLowerCase())
    )
    if (matched) {
      form.value.kategori_risiko = matched
      await onFormKategoriChange(matched)
    }
  }

  aiDialogVisible.value = false
  toast.add({
    severity: 'success',
    summary: 'Rumusan Diterapkan',
    detail: 'Uraian risiko, penyebab, dan dampak berhasil diterapkan ke form.',
    life: 3000,
  })
}

// Kategori styling tag
const kategoriColors = {
  'Risiko Operasional': { bg: '#e0e7ff', text: '#3730a3', border: '#c7d2fe' },
  'Risiko Fraud': { bg: '#fee2e2', text: '#991b1b', border: '#fecaca' },
  'Risiko Stakeholder': { bg: '#e0f2fe', text: '#075985', border: '#bae6fd' },
  'Risiko Kebijakan': { bg: '#f3e8ff', text: '#6b21a8', border: '#e9d5ff' },
  'Risiko Kepatuhan': { bg: '#fef3c7', text: '#92400e', border: '#fde68a' },
  'Risiko Bencana': { bg: '#ecfdf5', text: '#065f46', border: '#a7f3d0' },
}

function getKategoriStyle(kat) {
  return (
    kategoriColors[kat] || {
      bg: '#f1f5f9',
      text: '#334155',
      border: '#cbd5e1',
    }
  )
}

const statusOptions = [
  { label: 'Semua Status', value: null },
  { label: 'Aktif Saja', value: 1 },
  { label: 'Non-Aktif Saja', value: 0 },
]

const kategoriOptions = computed(() => [
  { label: 'Semua Kategori', value: null },
  ...kategoriList.value.map((k) => ({ label: k, value: k })),
])


// Muat daftar kategori unik
async function loadKategori() {
  try {
    const { data } = await api.get('/kamus-risiko/kategori')
    kategoriList.value = data
  } catch (err) {
    console.error('Gagal memuat kategori:', err)
  }
}

// Muat daftar kamus risiko
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: perPage.value,
    }
    if (search.value && search.value.trim()) {
      params.q = search.value.trim()
    }
    if (selectedKategori.value) {
      params.kategori = selectedKategori.value
    }
    if (selectedStatus.value !== null) {
      params.aktif = selectedStatus.value
    }

    const { data } = await api.get('/kamus-risiko', { params })
    items.value = data.items
    totalRecords.value = data.total
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Memuat Data',
      detail: err?.response?.data?.detail || 'Terjadi kesalahan koneksi ke server',
      life: 3000,
    })
  } finally {
    loading.value = false
  }
}

function onPageChange(event) {
  page.value = Math.floor(event.first / event.rows) + 1
  perPage.value = event.rows
  loadData()
}

let searchTimer = null
function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadData()
  }, 350)
}

function onFilterChange() {
  page.value = 1
  loadData()
}

function resetFilter() {
  search.value = ''
  selectedKategori.value = null
  selectedStatus.value = null
  page.value = 1
  loadData()
}

async function fetchNextCode(kat) {
  try {
    const { data } = await api.get('/kamus-risiko/next-code', {
      params: { kategori: kat },
    })
    return data
  } catch (e) {
    console.error('Gagal mengambil next-code:', e)
    return null
  }
}

async function onFormKategoriChange(newKat) {
  if (!isEdit.value && newKat) {
    const res = await fetchNextCode(newKat)
    if (res?.next_kode_risiko) {
      form.value.kode_risiko = res.next_kode_risiko
    }
  }
}

// Buka dialog tambah
async function openCreateDialog() {
  isEdit.value = false
  isCustomKategori.value = false
  customKategori.value = ''

  const defaultKat = kategoriList.value[0] || 'Risiko Operasional'
  let nextNo = totalRecords.value + 1
  let nextCode = 'RO-001'
  const res = await fetchNextCode(defaultKat)
  if (res) {
    nextNo = res.next_no
    nextCode = res.next_kode_risiko
  }

  form.value = {
    id: null,
    no: nextNo,
    kode_risiko: nextCode,
    nama_klp: 'Kota Tegal',
    kategori_risiko: defaultKat,
    nama_risiko: '',
    deskripsi: '',
    aktif: true,
  }
  dialogVisible.value = true
}

// Buka dialog edit
function openEditDialog(row) {
  isEdit.value = true
  isCustomKategori.value = false
  customKategori.value = ''

  form.value = {
    id: row.id,
    no: row.no,
    kode_risiko: row.kode_risiko || '',
    nama_klp: row.nama_klp || 'Kota Tegal',
    kategori_risiko: row.kategori_risiko || '',
    nama_risiko: row.nama_risiko || '',
    deskripsi: row.deskripsi || '',
    aktif: row.aktif === 1,
  }
  dialogVisible.value = true
}

// Simpan data (create / update)
async function saveItem() {
  const finalKategori = isCustomKategori.value
    ? customKategori.value.trim()
    : form.value.kategori_risiko

  if (!form.value.nama_risiko.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Nama / Uraian Risiko wajib diisi',
      life: 2500,
    })
    return
  }

  if (!finalKategori) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Kategori Risiko wajib dipilih atau diisi',
      life: 2500,
    })
    return
  }

  saving.value = true
  try {
    const payload = {
      no: form.value.no,
      kode_risiko: form.value.kode_risiko,
      nama_klp: form.value.nama_klp,
      kategori_risiko: finalKategori,
      nama_risiko: form.value.nama_risiko.trim(),
      deskripsi: form.value.deskripsi ? form.value.deskripsi.trim() : null,
      aktif: form.value.aktif ? 1 : 0,
    }

    if (isEdit.value) {
      await api.put(`/kamus-risiko/${form.value.id}`, payload)
      toast.add({
        severity: 'success',
        summary: 'Berhasil',
        detail: 'Data kamus risiko berhasil diperbarui',
        life: 2000,
      })
    } else {
      await api.post('/kamus-risiko', payload)
      toast.add({
        severity: 'success',
        summary: 'Berhasil',
        detail: 'Data kamus risiko baru berhasil ditambahkan',
        life: 2000,
      })
    }

    dialogVisible.value = false
    await Promise.all([loadData(), loadKategori()])
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: err?.response?.data?.detail || 'Terjadi kesalahan saat menyimpan data',
      life: 3500,
    })
  } finally {
    saving.value = false
  }
}

// Toggle status aktif langsung dari tabel
async function toggleStatus(row) {
  const newStatus = row.aktif === 1 ? 0 : 1
  try {
    await api.put(`/kamus-risiko/${row.id}`, { aktif: newStatus })
    row.aktif = newStatus
    toast.add({
      severity: 'success',
      summary: newStatus === 1 ? 'Risiko Diaktifkan' : 'Risiko Dinonaktifkan',
      detail: row.kode_risiko ? `Status ${row.kode_risiko} berhasil diperbarui` : 'Status berhasil diperbarui',
      life: 1500,
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Mengubah Status',
      detail: err?.response?.data?.detail || 'Terjadi kesalahan',
      life: 2500,
    })
  }
}

// Konfirmasi hapus
function confirmDelete(row) {
  confirm.require({
    message: `Hapus risiko "${row.nama_risiko}" (${row.kode_risiko || `#${row.id}`})? Tindakan ini tidak dapat dibatalkan.`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/kamus-risiko/${row.id}`)
        toast.add({
          severity: 'success',
          summary: 'Terhapus',
          detail: 'Data kamus risiko berhasil dihapus',
          life: 2000,
        })
        await Promise.all([loadData(), loadKategori()])
      } catch (err) {
        toast.add({
          severity: 'error',
          summary: 'Gagal Menghapus',
          detail: err?.response?.data?.detail || 'Data tidak dapat dihapus',
          life: 3000,
        })
      }
    },
  })
}

onMounted(() => {
  loadKategori()
  loadData()
})
</script>

<template>
  <div class="kamus-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-book"></i>
        </div>
        <div>
          <h1 class="page-title">Kamus Risiko</h1>
          <p class="page-desc">
            Katalog dan standar identifikasi risiko Pemerintah Daerah sebagai acuan penilaian risiko OPD
          </p>
        </div>
      </div>
      <div class="header-actions">
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          @click="loadData(); loadKategori()"
          :loading="loading"
        />
        <Button
          v-if="auth.isAdmin"
          label="Tambah Risiko"
          icon="pi pi-plus"
          severity="primary"
          @click="openCreateDialog"
        />
        <router-link v-if="!auth.isAdmin" :to="{name:'tata-kelola'}">Usulkan risiko melalui Tata Kelola → Usulan Kamus</router-link>
      </div>
    </div>

    <!-- Filter & Content Card -->
    <div class="content-card">
      <div class="toolbar-box">
        <div class="filter-group">
          <!-- Search Input -->
          <div class="search-wrap">
            <i class="pi pi-search search-icon"></i>
            <InputText
              v-model="search"
              placeholder="Cari nama risiko, kode, deskripsi..."
              class="search-input"
              @input="onSearchInput"
            />
            <button
              v-if="search"
              class="clear-btn"
              @click="search = ''; onFilterChange()"
              title="Bersihkan pencarian"
            >
              <i class="pi pi-times"></i>
            </button>
          </div>

          <!-- Kategori Filter -->
          <Select
            v-model="selectedKategori"
            :options="kategoriOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Semua Kategori"
            class="filter-select"
            @change="onFilterChange"
          />

          <!-- Status Filter -->
          <Select
            v-model="selectedStatus"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Semua Status"
            class="filter-select-sm"
            @change="onFilterChange"
          />

          <Button
            v-if="search || selectedKategori || selectedStatus !== null"
            icon="pi pi-filter-slash"
            label="Reset"
            severity="secondary"
            variant="text"
            size="small"
            @click="resetFilter"
          />
        </div>

        <div class="summary-count">
          Menampilkan <strong>{{ items.length }}</strong> dari <strong>{{ totalRecords }}</strong> data
        </div>
      </div>

      <!-- Data Table -->
      <DataTable
        :value="items"
        :loading="loading"
        lazy
        :paginator="true"
        :rows="perPage"
        :totalRecords="totalRecords"
        :first="(page - 1) * perPage"
        :rowsPerPageOptions="[10, 25, 50, 100]"
        @page="onPageChange"
        responsiveLayout="scroll"
        stripedRows
        class="custom-table"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-search-minus empty-icon"></i>
            <p class="empty-title">Tidak ada data kamus risiko ditemukan</p>
            <p class="empty-desc">Coba sesuaikan kata kunci pencarian atau filter kategori Anda.</p>
          </div>
        </template>

        <!-- Kolom No -->
        <Column header="No." style="width: 70px; text-align: center;">
          <template #body="{ data, index }">
            <span class="row-number">
              {{ data.no || (page - 1) * perPage + index + 1 }}
            </span>
          </template>
        </Column>

        <!-- Kolom Kode Risiko -->
        <Column header="Kode" style="width: 110px;">
          <template #body="{ data }">
            <span class="code-badge">
              {{ data.kode_risiko || '-' }}
            </span>
          </template>
        </Column>

        <!-- Kolom Kategori Risiko -->
        <Column header="Kategori Risiko" style="width: 180px;">
          <template #body="{ data }">
            <span
              class="kategori-pill"
              :style="{
                backgroundColor: getKategoriStyle(data.kategori_risiko).bg,
                color: getKategoriStyle(data.kategori_risiko).text,
                borderColor: getKategoriStyle(data.kategori_risiko).border,
              }"
            >
              {{ data.kategori_risiko }}
            </span>
          </template>
        </Column>

        <!-- Kolom Nama / Uraian Risiko -->
        <Column header="Nama / Uraian Risiko">
          <template #body="{ data }">
            <div class="nama-risiko-cell">
              <span class="nama-text">{{ data.nama_risiko }}</span>
              <span v-if="data.deskripsi" class="desc-text">{{ data.deskripsi }}</span>
            </div>
          </template>
        </Column>

        <!-- Kolom Kelompok / Pemda -->
        <Column header="Kelompok" style="width: 140px;">
          <template #body="{ data }">
            <span class="klp-text">{{ data.nama_klp || 'Kota Tegal' }}</span>
          </template>
        </Column>

        <!-- Kolom Status Aktif -->
        <Column header="Status" style="width: 120px; text-align: center;">
          <template #body="{ data }">
            <div class="status-toggle-wrapper">
              <ToggleSwitch
                :modelValue="data.aktif === 1"
                @update:modelValue="toggleStatus(data)"
              />
              <span :class="['status-label', data.aktif === 1 ? 'aktif' : 'nonaktif']">
                {{ data.aktif === 1 ? 'Aktif' : 'Non-Aktif' }}
              </span>
            </div>
          </template>
        </Column>

        <!-- Kolom Aksi -->
        <Column v-if="auth.isAdmin" header="Aksi" style="width: 110px; text-align: center;">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button
                icon="pi pi-pencil"
                severity="primary"
                variant="text"
                rounded
                size="small"
                v-tooltip.top="'Ubah Risiko'"
                @click="openEditDialog(data)"
              />
              <Button
                icon="pi pi-trash"
                severity="danger"
                variant="text"
                rounded
                size="small"
                v-tooltip.top="'Hapus Risiko'"
                @click="confirmDelete(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog Tambah / Ubah Kamus Risiko -->
    <Dialog
      v-model:visible="dialogVisible"
      :header="isEdit ? 'Ubah Data Kamus Risiko' : 'Tambah Kamus Risiko Baru'"
      :modal="true"
      :style="{ width: '640px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div class="dialog-form">
        <!-- AI Assist Banner -->
        <div class="ai-assist-banner">
          <div class="ai-banner-left">
            <div class="ai-banner-icon">
              <i class="pi pi-sparkles" />
            </div>
            <div>
              <div class="ai-banner-title">Bantuan AI Rumus Risiko</div>
              <div class="ai-banner-desc">Punya sasaran atau kegiatan? Biarkan AI merumuskan risiko, penyebab & dampaknya.</div>
            </div>
          </div>
          <Button
            type="button"
            label="Rumuskan dengan AI"
            icon="pi pi-sparkles"
            size="small"
            severity="help"
            @click="aiDialogVisible = true"
          />
        </div>

        <!-- Kode, No & Kelompok -->
        <div class="form-grid-3">
          <div class="form-item">
            <label class="form-label">
              Kode Risiko <span class="required">*</span>
            </label>
            <InputText
              v-model="form.kode_risiko"
              placeholder="Contoh: RO-001, RF-001, RK-001"
              class="w-full"
            />
            <span class="help-text">Format: Kategori-nomor urut (contoh: RO-001, RF-001, RK-001).</span>
          </div>

          <div class="form-item">
            <label class="form-label">Nomor Urut</label>
            <InputNumber
              v-model="form.no"
              placeholder="Auto"
              class="w-full"
              :useGrouping="false"
            />
          </div>

          <div class="form-item">
            <label class="form-label">Kelompok Pemda</label>
            <InputText
              v-model="form.nama_klp"
              placeholder="Kota Tegal"
              class="w-full"
            />
          </div>
        </div>

        <!-- Kategori Risiko -->
        <div class="form-item">
          <div class="label-with-action">
            <label class="form-label">
              Kategori Risiko <span class="required">*</span>
            </label>
            <Button
              :label="isCustomKategori ? 'Pilih dari daftar' : '+ Kategori Baru'"
              variant="link"
              size="small"
              class="link-action-btn"
              @click="isCustomKategori = !isCustomKategori"
            />
          </div>

          <Select
            v-if="!isCustomKategori"
            v-model="form.kategori_risiko"
            :options="kategoriList"
            placeholder="Pilih Kategori Risiko"
            class="w-full"
            @change="onFormKategoriChange(form.kategori_risiko)"
          />

          <InputText
            v-else
            v-model="customKategori"
            placeholder="Ketikkan nama kategori risiko baru..."
            class="w-full"
            @blur="onFormKategoriChange(customKategori)"
          />
        </div>

        <!-- Nama / Uraian Risiko -->
        <div class="form-item">
          <label class="form-label">
            Nama / Uraian Peristiwa Risiko <span class="required">*</span>
          </label>
          <Textarea
            v-model="form.nama_risiko"
            rows="3"
            placeholder="Contoh: Gangguan integritas data akibat serangan ransomware pada basis data..."
            class="w-full"
            autoResize
          />
          <span class="help-text">
            Tuliskan peristiwa atau potensi kegagalan yang dapat menghambat pencapaian tujuan/sasaran.
          </span>
        </div>

        <!-- Deskripsi Tambahan -->
        <div class="form-item">
          <label class="form-label">Deskripsi / Penjelasan Tambahan (Opsional)</label>
          <Textarea
            v-model="form.deskripsi"
            rows="2"
            placeholder="Penjelasan latar belakang atau konteks risiko (opsional)..."
            class="w-full"
            autoResize
          />
        </div>

        <!-- Status Aktif -->
        <div class="form-item status-row">
          <div class="status-info">
            <label class="form-label mb-0">Status Aktif</label>
            <span class="help-text">
              Risiko aktif akan tersedia sebagai referensi pada formulir identifikasi risiko OPD.
            </span>
          </div>
          <div class="status-switch">
            <ToggleSwitch v-model="form.aktif" />
            <span :class="['status-label', form.aktif ? 'aktif' : 'nonaktif']">
              {{ form.aktif ? 'Aktif' : 'Non-Aktif' }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Batal"
            severity="secondary"
            variant="outlined"
            @click="dialogVisible = false"
            :disabled="saving"
          />
          <Button
            :label="isEdit ? 'Simpan Perubahan' : 'Tambah Risiko'"
            icon="pi pi-check"
            severity="primary"
            @click="saveItem"
            :loading="saving"
          />
        </div>
      </template>
    </Dialog>

    <!-- Dialog AI Risk Generator -->
    <Dialog
      v-model:visible="aiDialogVisible"
      header="AI Assistant — Rumuskan Pernyataan Risiko"
      :modal="true"
      :style="{ width: '680px', maxWidth: '95vw' }"
      class="custom-dialog"
    >
      <div class="ai-generator-body">
        <p class="ai-gen-intro">
          Masukkan <strong>Sasaran OPD</strong>, <strong>Program</strong>, atau <strong>Kegiatan</strong> Anda.
          AI akan menganalisis potensi kegagalan dan merumuskan pernyataan risiko sesuai standar Perwal No. 1/2026.
        </p>

        <div class="form-item">
          <label class="form-label">Sasaran / Program / Kegiatan OPD</label>
          <div style="display: flex; gap: 8px">
            <InputText
              v-model="aiSasaran"
              placeholder="cth: Peningkatan kualitas pelayanan Puskesmas..."
              class="w-full"
              @keydown.enter="generateAiRisks"
            />
            <Button
              label="Generate"
              icon="pi pi-bolt"
              severity="help"
              :loading="aiGenerating"
              :disabled="!aiSasaran.trim()"
              @click="generateAiRisks"
            />
          </div>
        </div>

        <!-- Template Cepat -->
        <div class="ai-quick-templates">
          <span class="ai-quick-lbl">Contoh Sasaran:</span>
          <div class="ai-quick-chips">
            <button
              v-for="(t, idx) in quickSasaranTemplates"
              :key="idx"
              type="button"
              class="ai-quick-chip"
              @click="aiSasaran = t; generateAiRisks()"
            >
              {{ t }}
            </button>
          </div>
        </div>

        <!-- Hasil Generate -->
        <div v-if="aiGenerating" class="ai-gen-loading">
          <i class="pi pi-spin pi-spinner text-2xl text-indigo-600 mb-2" />
          <p>AI sedang merumuskan pernyataan risiko, penyebab, dan dampak...</p>
        </div>

        <div v-else-if="aiSuggestions.length > 0" class="ai-suggestions-list">
          <div class="ai-suggestions-header">
            <strong>Rekomendasi Rumusan Risiko ({{ aiSuggestions.length }} Pilihan):</strong>
            <span class="muted text-xs">Pilih salah satu untuk diterapkan langsung ke formulir.</span>
          </div>

          <div
            v-for="(sug, idx) in aiSuggestions"
            :key="idx"
            class="ai-suggestion-card"
          >
            <div class="ai-sug-top">
              <span class="ai-sug-badge">{{ sug.kategori || 'Risiko Operasional' }}</span>
              <Button
                label="Gunakan Risiko Ini"
                icon="pi pi-check"
                size="small"
                severity="primary"
                @click="useAiSuggestion(sug)"
              />
            </div>
            <div class="ai-sug-title">
              <i class="pi pi-exclamation-triangle text-amber-500 mr-1" />
              <strong>{{ sug.uraian_risiko }}</strong>
            </div>
            <div class="ai-sug-details">
              <div v-if="sug.penyebab" class="ai-sug-row">
                <span class="ai-sug-lbl">Penyebab:</span>
                <span>{{ sug.penyebab }}</span>
              </div>
              <div v-if="sug.dampak" class="ai-sug-row">
                <span class="ai-sug-lbl">Dampak:</span>
                <span>{{ sug.dampak }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Tutup"
            severity="secondary"
            variant="outlined"
            @click="aiDialogVisible = false"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.kamus-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

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


/* Content Card & Toolbar */
.content-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.toolbar-box {
  padding: 1.15rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  color: #94a3b8;
  font-size: 0.875rem;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 2.35rem !important;
  padding-right: 2rem !important;
  border-radius: 8px;
  font-size: 0.875rem;
}

.clear-btn {
  position: absolute;
  right: 0.65rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.clear-btn:hover {
  color: #475569;
}

.filter-select {
  min-width: 190px;
  border-radius: 8px;
  font-size: 0.875rem;
}

.filter-select-sm {
  min-width: 150px;
  border-radius: 8px;
  font-size: 0.875rem;
}

.summary-count {
  font-size: 0.85rem;
  color: #64748b;
}

/* Custom Table Styles */
.custom-table {
  font-size: 0.875rem;
}

.row-number {
  font-size: 0.825rem;
  color: #64748b;
  font-weight: 500;
}

.code-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-family: monospace;
  font-weight: 600;
  font-size: 0.8rem;
  color: #1e293b;
}

.kategori-pill {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}

.nama-risiko-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nama-text {
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
}

.desc-text {
  font-size: 0.775rem;
  color: #64748b;
  line-height: 1.35;
}

.klp-text {
  font-size: 0.825rem;
  color: #475569;
}

.status-toggle-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.status-label {
  font-size: 0.7rem;
  font-weight: 600;
}

.status-label.aktif {
  color: #059669;
}

.status-label.nonaktif {
  color: #94a3b8;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

/* Empty State */
.empty-state {
  padding: 3rem 1.5rem;
  text-align: center;
  color: #64748b;
}

.empty-icon {
  font-size: 2.75rem;
  color: #cbd5e1;
  margin-bottom: 0.75rem;
}

.empty-title {
  font-size: 1rem;
  font-weight: 600;
  color: #334155;
  margin: 0 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.85rem;
  margin: 0;
}

/* Dialog & Form */
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 0.5rem 0;
}

.form-grid-3 {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1.5fr;
  gap: 0.75rem;
}

@media (max-width: 600px) {
  .form-grid-3 {
    grid-template-columns: 1fr;
  }
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.825rem;
  font-weight: 600;
  color: #334155;
}

.required {
  color: #ef4444;
}

.help-text {
  font-size: 0.75rem;
  color: #64748b;
}

.label-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.link-action-btn {
  padding: 0 !important;
  font-size: 0.75rem !important;
  text-decoration: none;
}

.status-row {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.status-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.mb-0 {
  margin-bottom: 0;
}

.w-full {
  width: 100%;
}

/* AI Assist Banner */
.ai-assist-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  border: 1px solid #ddd6fe;
  border-radius: 10px;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.ai-banner-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-banner-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.ai-banner-title {
  font-weight: 700;
  font-size: 0.85rem;
  color: #5b21b6;
}

.ai-banner-desc {
  font-size: 0.74rem;
  color: #6b21a8;
  margin-top: 1px;
}

/* AI Generator Dialog */
.ai-generator-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ai-gen-intro {
  font-size: 0.84rem;
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

.ai-quick-templates {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ai-quick-lbl {
  font-size: 0.74rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.ai-quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ai-quick-chip {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.74rem;
  cursor: pointer;
  transition: all 0.18s;
  text-align: left;
}

.ai-quick-chip:hover {
  background: #ede9fe;
  border-color: #c4b5fd;
  color: #6d28d9;
}

.ai-gen-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
  text-align: center;
  color: #64748b;
  font-size: 0.85rem;
}

.ai-suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 6px;
}

.ai-suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 0.84rem;
  color: #1e293b;
}

.ai-suggestion-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-suggestion-card:hover {
  border-color: #818cf8;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
}

.ai-sug-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-sug-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #4338ca;
  background: #e0e7ff;
  padding: 2px 8px;
  border-radius: 999px;
}

.ai-sug-title {
  font-size: 0.88rem;
  color: #0f172a;
  line-height: 1.45;
}

.ai-sug-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: #f8fafc;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #f1f5f9;
  font-size: 0.78rem;
  color: #334155;
  line-height: 1.4;
}

.ai-sug-row {
  display: flex;
  gap: 6px;
}

.ai-sug-lbl {
  font-weight: 600;
  color: #64748b;
  flex-shrink: 0;
}
</style>
