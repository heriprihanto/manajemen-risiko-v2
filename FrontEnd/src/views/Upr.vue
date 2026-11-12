<script setup>
import { computed, onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const ctx = useContextStore()
const toast = useToast()
const confirm = useConfirm()

// State data & filter
const items = ref([])
const totalRecords = ref(0)
const loading = ref(false)
const saving = ref(false)
const syncing = ref(false)

// Pagination
const page = ref(1)
const perPage = ref(25)

// Filter & search
const search = ref('')
const selectedOpdFilter = ref(null)
const selectedTingkatOrg = ref(null)
const selectedJabatanUpr = ref(null)
const selectedEselon = ref(null)
const selectedStatus = ref(null)

const tingkatOrgList = [
  'UPR tingkat pemerintah daerah',
  'UPR tingkat unit Eselon II',
  'UPR tingkat unit Eselon III dan IV',
]

const jabatanUprList = [
  'Ketua',
  'Koordinator Teknis',
  'Anggota',
]

const eselonList = [
  'Eselon II.a',
  'Eselon II.b',
  'Eselon III.a',
  'Eselon III.b',
  'Eselon IV.a',
  'Eselon IV.b',
  'Non-Eselon / JF',
]

const statusList = [
  { label: 'Semua Status', value: null },
  { label: 'Aktif', value: 'Aktif' },
  { label: 'Tidak Aktif', value: 'Tidak Aktif' },
]

// Dialog modal state
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  opd_id: null,
  nip: '',
  nama: '',
  jabatan: '',
  tingkat_organisasi: 'UPR tingkat unit Eselon II',
  jabatan_upr: 'Ketua',
  eselon: 'Eselon II.b',
  status: 'Aktif',
  keterangan: '',
})

// Options OPD
const opdFilterOptions = computed(() => [
  { label: 'Semua Perangkat Daerah', value: null },
  ...ctx.opdList.map((o) => ({
    label: o.nama_pd || o.nama_pd_singkat,
    value: o.id_sub_pd,
  })),
])

const opdFormOptions = computed(() => [
  { label: 'Pemerintah Daerah / Setda / Umum', value: null },
  ...ctx.opdList.map((o) => ({
    label: o.nama_pd || o.nama_pd_singkat,
    value: o.id_sub_pd,
  })),
])

// Muat data tabel
async function loadData() {
  loading.value = true
  try {
    const { data } = await api.get('/upr', {
      params: {
        opd_id: selectedOpdFilter.value || undefined,
        search: search.value.trim() || undefined,
        tingkat_organisasi: selectedTingkatOrg.value || undefined,
        jabatan_upr: selectedJabatanUpr.value || undefined,
        eselon: selectedEselon.value || undefined,
        status: selectedStatus.value || undefined,
        page: page.value,
        per_page: perPage.value,
      },
    })
    items.value = data.items || []
    totalRecords.value = data.total || 0
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Memuat Data',
      detail: e.response?.data?.detail || e.message || 'Terjadi kesalahan sistem',
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
  selectedOpdFilter.value = null
  selectedTingkatOrg.value = null
  selectedJabatanUpr.value = null
  selectedEselon.value = null
  selectedStatus.value = null
  page.value = 1
  loadData()
}

function openAdd() {
  isEdit.value = false
  form.value = {
    id: null,
    opd_id: ctx.opdId || null,
    nip: '',
    nama: '',
    jabatan: '',
    tingkat_organisasi: 'UPR tingkat unit Eselon II',
    jabatan_upr: 'Ketua',
    eselon: 'Eselon II.b',
    status: 'Aktif',
    keterangan: '',
  }
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  form.value = {
    id: row.id,
    opd_id: row.opd_id,
    nip: row.nip,
    nama: row.nama,
    jabatan: row.jabatan,
    tingkat_organisasi: row.tingkat_organisasi || 'UPR tingkat unit Eselon II',
    jabatan_upr: row.jabatan_upr || 'Anggota',
    eselon: row.eselon || 'Non-Eselon / JF',
    status: row.status || 'Aktif',
    keterangan: row.keterangan || '',
  }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.nip.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'NIP wajib diisi', life: 2500 })
    return
  }
  if (!form.value.nama.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama pejabat wajib diisi', life: 2500 })
    return
  }
  if (!form.value.jabatan.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Jabatan wajib diisi', life: 2500 })
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/upr/${form.value.id}`, form.value)
      toast.add({ severity: 'success', summary: 'Sukses', detail: 'Data UPR berhasil diperbarui', life: 2500 })
    } else {
      await api.post('/upr', form.value)
      toast.add({ severity: 'success', summary: 'Sukses', detail: 'Pejabat UPR baru berhasil ditambahkan', life: 2500 })
    }
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: e.response?.data?.detail || e.message || 'Terjadi kesalahan sistem',
      life: 3500,
    })
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) {
  confirm.require({
    message: `Hapus data pejabat UPR "${row.nama}" (${row.nip})? Tindakan ini tidak dapat dibatalkan.`,
    header: 'Konfirmasi Hapus Pejabat UPR',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Hapus',
    rejectLabel: 'Batal',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete(`/upr/${row.id}`)
        toast.add({ severity: 'success', summary: 'Terhapus', detail: 'Data pejabat UPR berhasil dihapus', life: 2000 })
        await loadData()
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Gagal', detail: e.response?.data?.detail || 'Gagal menghapus data', life: 3000 })
      }
    },
  })
}

async function quickToggleStatus(row) {
  const newStatus = row.status === 'Aktif' ? 'Tidak Aktif' : 'Aktif'
  try {
    await api.put(`/upr/${row.id}`, { status: newStatus })
    row.status = newStatus
    toast.add({
      severity: newStatus === 'Aktif' ? 'success' : 'info',
      summary: 'Status Diperbarui',
      detail: `${row.nama} kini ${newStatus}`,
      life: 2000,
    })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengubah status', life: 3000 })
  }
}

async function syncFromOpd() {
  confirm.require({
    message: 'Sinkronisasi akan mengimpor data Kepala OPD aktif dari master OPD ke dalam Unit Pemilik Risiko (UPR) lengkap dengan penentuan tingkat organisasi dan jabatan UPR. Lanjutkan?',
    header: 'Sinkronisasi Kepala OPD ke UPR',
    icon: 'pi pi-sync',
    acceptLabel: 'Sinkronkan',
    rejectLabel: 'Batal',
    accept: async () => {
      syncing.value = true
      try {
        const { data } = await api.post('/upr/sync-from-opd')
        toast.add({
          severity: 'success',
          summary: 'Sinkronisasi Berhasil',
          detail: data.message,
          life: 4000,
        })
        await loadData()
      } catch (e) {
        toast.add({
          severity: 'error',
          summary: 'Sinkronisasi Gagal',
          detail: e.response?.data?.detail || e.message || 'Gagal sinkronisasi data',
          life: 3500,
        })
      } finally {
        syncing.value = false
      }
    },
  })
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
  toast.add({ severity: 'info', summary: 'Disalin', detail: `NIP ${text} disalin ke clipboard`, life: 1500 })
}

function getEselonBadgeClass(eselon) {
  if (!eselon) return 'badge-slate'
  const e = eselon.toLowerCase()
  if (e.includes('ii.a')) return 'badge-blue'
  if (e.includes('ii.b')) return 'badge-indigo'
  if (e.includes('iii.a')) return 'badge-emerald'
  if (e.includes('iii.b')) return 'badge-teal'
  if (e.includes('iv')) return 'badge-amber'
  return 'badge-slate'
}

function getTingkatOrgBadgeClass(tingkat) {
  if (!tingkat) return 'badge-slate'
  const t = tingkat.toLowerCase()
  if (t.includes('pemerintah daerah') || t.includes('pemda')) return 'badge-purple'
  if (t.includes('eselon ii')) return 'badge-blue'
  if (t.includes('eselon iii')) return 'badge-teal'
  return 'badge-slate'
}

function getJabatanUprBadgeClass(jabatan) {
  if (!jabatan) return 'badge-slate'
  const j = jabatan.toLowerCase()
  if (j === 'ketua') return 'badge-gold'
  if (j.includes('koordinator')) return 'badge-indigo'
  return 'badge-slate'
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="upr-page">
    <!-- Header Section (Style Kamus Risiko) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-id-card"></i>
        </div>
        <div>
          <h1 class="page-title">Unit Pemilik Risiko (UPR)</h1>
          <p class="page-desc">
            Daftar personil dan pejabat penanggung jawab pengelolaan risiko di lingkungan Pemerintah Daerah Kota Tegal
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
        <Button
          label="Sinkron Kepala OPD"
          icon="pi pi-sync"
          severity="secondary"
          variant="outlined"
          :loading="syncing"
          @click="syncFromOpd"
        />
        <Button
          label="Tambah Pejabat UPR"
          icon="pi pi-plus"
          severity="primary"
          @click="openAdd"
        />
      </div>
    </div>

    <!-- Content Card (Toolbar & Table) -->
    <div class="content-card">
      <!-- Toolbar Box -->
      <div class="toolbar-box">
        <div class="filter-group">
          <!-- Search Input -->
          <div class="search-wrap">
            <i class="pi pi-search search-icon"></i>
            <InputText
              v-model="search"
              placeholder="Cari NIP, nama, jabatan..."
              class="search-input"
              @input="onSearchInput"
            />
            <button
              v-if="search"
              class="clear-btn"
              title="Bersihkan pencarian"
              @click="search = ''; onFilterChange()"
            >
              <i class="pi pi-times"></i>
            </button>
          </div>

          <!-- Filter OPD -->
          <Select
            v-model="selectedOpdFilter"
            :options="opdFilterOptions"
            option-label="label"
            option-value="value"
            placeholder="Semua Perangkat Daerah"
            class="filter-select"
            filter
            @change="onFilterChange"
          />

          <!-- Filter Tingkat Organisasi -->
          <Select
            v-model="selectedTingkatOrg"
            :options="['Semua Tingkat Organisasi', ...tingkatOrgList]"
            :option-value="(val) => (val === 'Semua Tingkat Organisasi' ? null : val)"
            placeholder="Semua Tingkat Organisasi"
            class="filter-select"
            @change="onFilterChange"
          />

          <!-- Filter Jabatan dalam UPR -->
          <Select
            v-model="selectedJabatanUpr"
            :options="['Semua Jabatan UPR', ...jabatanUprList]"
            :option-value="(val) => (val === 'Semua Jabatan UPR' ? null : val)"
            placeholder="Semua Jabatan UPR"
            class="filter-select-sm"
            @change="onFilterChange"
          />

          <!-- Filter Eselon -->
          <Select
            v-model="selectedEselon"
            :options="['Semua Eselon', ...eselonList]"
            :option-value="(val) => (val === 'Semua Eselon' ? null : val)"
            placeholder="Semua Eselon"
            class="filter-select-sm"
            @change="onFilterChange"
          />

          <!-- Filter Status -->
          <Select
            v-model="selectedStatus"
            :options="statusList"
            option-label="label"
            option-value="value"
            placeholder="Semua Status"
            class="filter-select-sm"
            @change="onFilterChange"
          />

          <!-- Reset Filter -->
          <Button
            v-if="search || selectedOpdFilter || selectedTingkatOrg || selectedJabatanUpr || selectedEselon || selectedStatus"
            icon="pi pi-filter-slash"
            severity="secondary"
            text
            rounded
            title="Reset filter"
            @click="resetFilter"
          />
        </div>

        <div class="summary-count">
          Total: <strong>{{ totalRecords }}</strong> personil
        </div>
      </div>

      <!-- Table Section -->
      <DataTable
        :value="items"
        :loading="loading"
        striped-rows
        responsive-layout="scroll"
        class="p-datatable-sm custom-upr-table"
        :paginator="true"
        :rows="perPage"
        :total-records="totalRecords"
        :lazy="true"
        :first="(page - 1) * perPage"
        :rows-per-page-options="[10, 25, 50, 100]"
        paginator-template="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
        current-page-report-template="Menampilkan {first} sampai {last} dari {totalRecords} entri"
        @page="onPageChange"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-inbox empty-icon"></i>
            <p class="empty-title">Belum ada data Unit Pemilik Risiko (UPR)</p>
            <p class="empty-desc">Silakan tambahkan data baru atau klik "Sinkron Kepala OPD" untuk mengimpor data awal.</p>
          </div>
        </template>

        <!-- No -->
        <Column header="No" :style="{ width: '50px', textAlign: 'center' }">
          <template #body="{ index }">
            <span class="row-number">{{ (page - 1) * perPage + index + 1 }}</span>
          </template>
        </Column>

        <!-- NIP -->
        <Column field="nip" header="NIP" :style="{ width: '180px' }">
          <template #body="{ data }">
            <div class="nip-cell">
              <span class="code-badge">{{ data.nip }}</span>
              <button
                v-if="data.nip && data.nip !== '-'"
                class="copy-btn"
                title="Salin NIP"
                @click="copyToClipboard(data.nip)"
              >
                <i class="pi pi-copy"></i>
              </button>
            </div>
          </template>
        </Column>

        <!-- Nama -->
        <Column field="nama" header="Nama" :style="{ minWidth: '220px' }">
          <template #body="{ data }">
            <div class="nama-cell">
              <span class="nama-text">{{ data.nama }}</span>
              <span v-if="data.keterangan" class="desc-text">{{ data.keterangan }}</span>
            </div>
          </template>
        </Column>

        <!-- Jabatan -->
        <Column field="jabatan" header="Jabatan Kedinasan" :style="{ minWidth: '220px' }">
          <template #body="{ data }">
            <div class="jabatan-cell">
              <span class="jabatan-text">{{ data.jabatan }}</span>
              <span class="opd-text"><i class="pi pi-building mr-1"></i>{{ data.nama_pd }}</span>
            </div>
          </template>
        </Column>

        <!-- Tingkat Organisasi -->
        <Column field="tingkat_organisasi" header="Tingkat Organisasi" :style="{ minWidth: '220px' }">
          <template #body="{ data }">
            <span :class="['org-badge', getTingkatOrgBadgeClass(data.tingkat_organisasi)]">
              {{ data.tingkat_organisasi || 'UPR tingkat unit Eselon II' }}
            </span>
          </template>
        </Column>

        <!-- Jabatan dalam UPR -->
        <Column field="jabatan_upr" header="Jabatan dalam UPR" :style="{ width: '160px', textAlign: 'center' }">
          <template #body="{ data }">
            <span :class="['upr-role-badge', getJabatanUprBadgeClass(data.jabatan_upr)]">
              <i v-if="data.jabatan_upr === 'Ketua'" class="pi pi-star-fill mr-1 text-amber-500"></i>
              <i v-else-if="data.jabatan_upr === 'Koordinator Teknis'" class="pi pi-cog mr-1"></i>
              <i v-else class="pi pi-user mr-1"></i>
              {{ data.jabatan_upr || 'Anggota' }}
            </span>
          </template>
        </Column>

        <!-- Eselon -->
        <Column field="eselon" header="Eselon" :style="{ width: '130px', textAlign: 'center' }">
          <template #body="{ data }">
            <span :class="['eselon-badge', getEselonBadgeClass(data.eselon)]">
              {{ data.eselon || 'Non-Eselon' }}
            </span>
          </template>
        </Column>

        <!-- Status -->
        <Column field="status" header="Status" :style="{ width: '120px', textAlign: 'center' }">
          <template #body="{ data }">
            <button
              class="status-toggle-btn"
              :title="`Klik untuk ubah ke ${data.status === 'Aktif' ? 'Tidak Aktif' : 'Aktif'}`"
              @click="quickToggleStatus(data)"
            >
              <span
                v-if="data.status === 'Aktif'"
                class="status-pill aktif"
              >
                <i class="pi pi-check mr-1"></i> Aktif
              </span>
              <span
                v-else
                class="status-pill nonaktif"
              >
                <i class="pi pi-times mr-1"></i> Tidak Aktif
              </span>
            </button>
          </template>
        </Column>

        <!-- Aksi -->
        <Column header="Aksi" :style="{ width: '90px', textAlign: 'center' }">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button
                icon="pi pi-pencil"
                rounded
                text
                severity="info"
                size="small"
                title="Edit pejabat"
                @click="openEdit(data)"
              />
              <Button
                icon="pi pi-trash"
                rounded
                text
                severity="danger"
                size="small"
                title="Hapus pejabat"
                @click="confirmDelete(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog Modal Tambah / Edit -->
    <Dialog
      v-model:visible="dialogVisible"
      :header="isEdit ? 'Ubah Pejabat UPR' : 'Tambah Pejabat Unit Pemilik Risiko (UPR)'"
      :modal="true"
      :style="{ width: '580px', maxWidth: '95vw' }"
    >
      <form class="dialog-form" @submit.prevent="save">
        <div class="form-field">
          <label for="form-opd" class="form-label">
            Unit Kerja / Perangkat Daerah <span class="required">*</span>
          </label>
          <Select
            id="form-opd"
            v-model="form.opd_id"
            :options="opdFormOptions"
            option-label="label"
            option-value="value"
            placeholder="Pilih Perangkat Daerah"
            class="w-full"
            filter
          />
        </div>

        <div class="form-field">
          <label for="form-nip" class="form-label">
            NIP (Nomor Induk Pegawai) <span class="required">*</span>
          </label>
          <InputText
            id="form-nip"
            v-model="form.nip"
            placeholder="Contoh: 19810503 199912 1 001"
            class="w-full"
            required
          />
        </div>

        <div class="form-field">
          <label for="form-nama" class="form-label">
            Nama Lengkap & Gelar <span class="required">*</span>
          </label>
          <InputText
            id="form-nama"
            v-model="form.nama"
            placeholder="Contoh: drg. AGUS DWI SULISTYANTONO, MM"
            class="w-full"
            required
          />
        </div>

        <div class="form-field">
          <label for="form-jabatan" class="form-label">
            Jabatan Kedinasan <span class="required">*</span>
          </label>
          <InputText
            id="form-jabatan"
            v-model="form.jabatan"
            placeholder="Contoh: Kepala Dinas / Sekretaris Daerah / Kepala Bagian..."
            class="w-full"
            required
          />
        </div>

        <!-- Tingkat Organisasi & Jabatan dalam UPR -->
        <div class="form-grid-2">
          <div class="form-field">
            <label for="form-tingkat-org" class="form-label">
              Tingkat Organisasi <span class="required">*</span>
            </label>
            <Select
              id="form-tingkat-org"
              v-model="form.tingkat_organisasi"
              :options="tingkatOrgList"
              placeholder="Pilih Tingkat Organisasi"
              class="w-full"
            />
          </div>

          <div class="form-field">
            <label for="form-jabatan-upr" class="form-label">
              Jabatan dalam UPR <span class="required">*</span>
            </label>
            <Select
              id="form-jabatan-upr"
              v-model="form.jabatan_upr"
              :options="jabatanUprList"
              placeholder="Pilih Jabatan UPR"
              class="w-full"
            />
          </div>
        </div>

        <!-- Eselon & Status -->
        <div class="form-grid-2">
          <div class="form-field">
            <label for="form-eselon" class="form-label">
              Eselon <span class="required">*</span>
            </label>
            <Select
              id="form-eselon"
              v-model="form.eselon"
              :options="eselonList"
              placeholder="Pilih Eselon"
              class="w-full"
            />
          </div>

          <div class="form-field">
            <label for="form-status" class="form-label">
              Status <span class="required">*</span>
            </label>
            <Select
              id="form-status"
              v-model="form.status"
              :options="['Aktif', 'Tidak Aktif']"
              placeholder="Pilih Status"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="form-keterangan" class="form-label">
            Keterangan (Opsional)
          </label>
          <Textarea
            id="form-keterangan"
            v-model="form.keterangan"
            rows="2"
            placeholder="Catatan tambahan / peran spesifik..."
            class="w-full"
          />
        </div>

        <div class="dialog-actions">
          <Button
            type="button"
            label="Batal"
            severity="secondary"
            variant="outlined"
            @click="dialogVisible = false"
          />
          <Button
            type="submit"
            :label="isEdit ? 'Simpan Perubahan' : 'Tambah Pejabat'"
            icon="pi pi-check"
            severity="primary"
            :loading="saving"
          />
        </div>
      </form>
    </Dialog>
  </div>
</template>

<style scoped>
.upr-page {
  padding: 1.5rem;
  max-width: 1440px;
  margin: 0 auto;
}

/* Page Header (Matching Kamus Risiko) */
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
  min-width: 250px;
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
  min-width: 210px;
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
.custom-upr-table {
  font-size: 0.875rem;
}

.row-number {
  font-size: 0.825rem;
  color: #64748b;
  font-weight: 500;
}

.nip-cell {
  display: flex;
  align-items: center;
  gap: 0.4rem;
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
  white-space: nowrap;
}

.copy-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 2px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  transition: color 0.15s;
}

.copy-btn:hover {
  color: #0284c7;
}

.nama-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
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

.jabatan-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.jabatan-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
}

.opd-text {
  font-size: 0.775rem;
  color: #64748b;
  display: inline-flex;
  align-items: center;
}

/* Tingkat Organisasi Badge */
.org-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  line-height: 1.35;
}

.badge-purple {
  background: #f5f3ff;
  color: #6d28d9;
  border-color: #ddd6fe;
}

/* Jabatan UPR Role Badge */
.upr-role-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}

.badge-gold {
  background: #fffbeb;
  color: #b45309;
  border-color: #fde68a;
  box-shadow: 0 1px 2px rgba(245, 158, 11, 0.1);
}

/* Eselon Badges */
.eselon-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}

.badge-blue {
  background: #eff6ff;
  color: #1e40af;
  border-color: #bfdbfe;
}

.badge-indigo {
  background: #eef2ff;
  color: #3730a3;
  border-color: #c7d2fe;
}

.badge-emerald {
  background: #ecfdf5;
  color: #065f46;
  border-color: #a7f3d0;
}

.badge-teal {
  background: #f0fdfa;
  color: #115e59;
  border-color: #99f6e4;
}

.badge-amber {
  background: #fffbeb;
  color: #92400e;
  border-color: #fde68a;
}

.badge-slate {
  background: #f8fafc;
  color: #475569;
  border-color: #e2e8f0;
}

/* Status Pill */
.status-toggle-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  border-radius: 9999px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  transition: opacity 0.15s;
}

.status-pill:hover {
  opacity: 0.85;
}

.status-pill.aktif {
  background: #ecfdf5;
  color: #059669;
  border-color: #a7f3d0;
}

.status-pill.nonaktif {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
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

/* Dialog Form */
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 0.5rem;
}

.form-field {
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

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}
</style>
