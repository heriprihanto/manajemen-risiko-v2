<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { useAuthStore } from '@/stores/auth'
import AppLoader from '@/components/AppLoader.vue'
import { formatDateTime } from '@/utils/date'

const ctx = useContextStore()
const auth = useAuthStore()
const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const items = ref([])
const statusFilter = ref('all')
const searchQuery = ref('')

// Dialog Validasi
const dialogVisible = ref(false)
const selectedItem = ref(null)
const validationStatus = ref('disetujui')
const validationNotes = ref('')
const selectedRisikoId = ref(null)
const copyToForm10 = ref(true)
const savingValidation = ref(false)
const risikoList = ref([])
const loadingRisiko = ref(false)

const statusOptions = [
  { label: 'Semua Status', value: 'all' },
  { label: 'Menunggu Validasi', value: 'pending' },
  { label: 'Disetujui', value: 'disetujui' },
  { label: 'Ditolak', value: 'ditolak' },
]

async function loadData() {
  loading.value = true
  try {
    const params = {
      tahun: ctx.tahun,
      status: statusFilter.value,
    }
    if (!auth.isAdmin && ctx.opdId) {
      params.opd_id = ctx.opdId
    } else if (ctx.opdId) {
      params.opd_id = ctx.opdId
    }
    const res = await api.get('/approval-kejadian', { params })
    items.value = res.data || []
  } catch (err) {
    items.value = []
    toast.add({
      severity: 'error',
      summary: 'Gagal Memuat Data',
      detail: err.response?.data?.detail || 'Tidak dapat memuat daftar approval kejadian',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

async function loadRisikoForOpd(opdId, tahun) {
  loadingRisiko.value = true
  try {
    const res = await api.get('/risiko', { params: { opd_id: opdId, tahun } })
    risikoList.value = res.data || []
  } catch (err) {
    risikoList.value = []
  } finally {
    loadingRisiko.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun, statusFilter], loadData)
onMounted(loadData)

// Ringkasan metrik
const stats = computed(() => {
  const total = items.value.length
  const pending = items.value.filter((x) => x.status === 'pending').length
  const approved = items.value.filter((x) => x.status === 'disetujui').length
  const rejected = items.value.filter((x) => x.status === 'ditolak').length
  return { total, pending, approved, rejected }
})

// Filter pencarian teks
const filteredItems = computed(() => {
  if (!searchQuery.value.trim()) return items.value
  const q = searchQuery.value.toLowerCase()
  return items.value.filter((x) =>
    (x.nama_lengkap || '').toLowerCase().includes(q) ||
    (x.nama_opd || '').toLowerCase().includes(q) ||
    (x.tempat || '').toLowerCase().includes(q) ||
    (x.uraian_kejadian || '').toLowerCase().includes(q) ||
    (x.pemicu || '').toLowerCase().includes(q)
  )
})

function openValidationDialog(row) {
  selectedItem.value = row
  validationStatus.value = row.status === 'pending' ? 'disetujui' : row.status
  validationNotes.value = row.catatan_validasi || ''
  selectedRisikoId.value = row.risiko_id || null
  copyToForm10.value = true
  dialogVisible.value = true
  loadRisikoForOpd(row.opd_id, row.tahun)
}

async function saveValidation() {
  if (!selectedItem.value) return
  savingValidation.value = true
  try {
    const payload = {
      status: validationStatus.value,
      catatan_validasi: validationNotes.value.trim() || null,
      risiko_id: selectedRisikoId.value || null,
      salin_ke_form10: validationStatus.value === 'disetujui' && copyToForm10.value,
    }

    await api.put(`/approval-kejadian/${selectedItem.value.id}/status`, payload)

    toast.add({
      severity: 'success',
      summary: 'Validasi Disimpan',
      detail: `Laporan kejadian berhasil divalidasi (${validationStatus.value}).`,
      life: 3000,
    })

    dialogVisible.value = false
    await loadData()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: err.response?.data?.detail || 'Terjadi kesalahan saat memvalidasi laporan',
      life: 4000,
    })
  } finally {
    savingValidation.value = false
  }
}

function confirmDelete(row) {
  confirm.require({
    message: `Hapus laporan kejadian dari ${row.nama_lengkap}? Tindakan ini tidak dapat dibatalkan.`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete(`/approval-kejadian/${row.id}`)
        toast.add({
          severity: 'success',
          summary: 'Dihapus',
          detail: 'Laporan kejadian telah dihapus',
          life: 3000,
        })
        await loadData()
      } catch (err) {
        toast.add({
          severity: 'error',
          summary: 'Gagal Hapus',
          detail: err.response?.data?.detail || 'Tidak dapat menghapus data',
          life: 3000,
        })
      }
    },
  })
}

function statusSeverity(st) {
  if (st === 'disetujui') return 'success'
  if (st === 'ditolak') return 'danger'
  return 'warn'
}

function statusLabel(st) {
  if (st === 'disetujui') return 'Disetujui'
  if (st === 'ditolak') return 'Ditolak'
  return 'Menunggu Validasi'
}

function openPublicForm() {
  const url = `${window.location.origin}${import.meta.env.BASE_URL}lapor-kejadian`
  window.open(url, '_blank')
}

async function copyPublicUrl() {
  const url = `${window.location.origin}${import.meta.env.BASE_URL}lapor-kejadian`
  try {
    await navigator.clipboard.writeText(url)
    toast.add({
      severity: 'info',
      summary: 'Tautan Disalin',
      detail: 'URL Halaman Lapor Kejadian berhasil disalin ke clipboard.',
      life: 3000,
    })
  } catch {
    toast.add({ severity: 'warn', summary: 'Info', detail: url, life: 5000 })
  }
}
</script>

<template>
  <div class="approval-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-check-circle" />
        </div>
        <div>
          <h1 class="page-title">Approval Kejadian Risiko</h1>
          <p class="page-desc">
            Validasi dan tindak lanjut laporan kejadian risiko yang dikirim oleh seluruh pegawai OPD melalui saluran Lapor Kejadian
          </p>
        </div>
      </div>
      <div class="header-actions">
        <Button
          label="Buka Lapor Kejadian (Publik)"
          icon="pi pi-external-link"
          severity="info"
          variant="outlined"
          @click="openPublicForm"
        />
        <Button
          label="Salin Tautan"
          icon="pi pi-copy"
          severity="secondary"
          variant="outlined"
          @click="copyPublicUrl"
        />
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


    <!-- Stat Metrics Cards (Style Laporan Rekapitulasi) -->
    <div class="stat-grid no-print" style="margin-bottom: 20px;">
      <div
        class="stat"
        :class="{ 'stat-active': statusFilter === 'all' }"
        style="cursor: pointer;"
        @click="statusFilter = 'all'"
      >
        <div class="v">{{ stats.total }}</div>
        <div class="l">Total Laporan Masuk</div>
      </div>

      <div
        class="stat"
        :class="{ 'stat-active': statusFilter === 'pending' }"
        style="cursor: pointer;"
        @click="statusFilter = 'pending'"
      >
        <div class="v" style="color: #d97706;">{{ stats.pending }}</div>
        <div class="l">Menunggu Validasi</div>
      </div>

      <div
        class="stat"
        :class="{ 'stat-active': statusFilter === 'disetujui' }"
        style="cursor: pointer;"
        @click="statusFilter = 'disetujui'"
      >
        <div class="v" style="color: #059669;">{{ stats.approved }}</div>
        <div class="l">Laporan Disetujui</div>
      </div>

      <div
        class="stat"
        :class="{ 'stat-active': statusFilter === 'ditolak' }"
        style="cursor: pointer;"
        @click="statusFilter = 'ditolak'"
      >
        <div class="v" style="color: #dc2626;">{{ stats.rejected }}</div>
        <div class="l">Laporan Ditolak</div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="card table-card">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <Select
            v-model="statusFilter"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Filter Status"
            style="width: 200px"
          />
        </div>
        <div class="toolbar-right">
          <div class="search-input-wrap">
            <i class="pi pi-search search-icon" />
            <InputText
              v-model="searchQuery"
              placeholder="Cari nama, OPD, tempat, uraian…"
              class="search-input"
            />
          </div>
        </div>
      </div>

      <DataTable
        :value="filteredItems"
        :loading="loading"
        paginator
        :rows="10"
        :rowsPerPageOptions="[10, 20, 50]"
        stripedRows
        responsiveLayout="scroll"
        class="p-datatable-sm"
      >
        <template #empty>
          <div class="empty-table-state">
            <i class="pi pi-folder-open empty-icon" />
            <p>Tidak ada laporan kejadian risiko yang sesuai filter.</p>
          </div>
        </template>

        <Column header="No" style="width: 50px; text-align: center">
          <template #body="{ index }">
            {{ index + 1 }}
          </template>
        </Column>

        <Column header="Tanggal Lapor" style="width: 140px">
          <template #body="{ data }">
            <div class="date-cell">
              <span class="date-txt">{{ formatDateTime(data.created_at) }}</span>
              <span class="badge-year">Thn {{ data.tahun }}</span>
            </div>
          </template>
        </Column>

        <Column header="Pelapor" style="width: 200px">
          <template #body="{ data }">
            <div class="pelapor-cell">
              <strong>{{ data.nama_lengkap }}</strong>
              <div class="contact-links">
                <a
                  :href="`https://wa.me/${data.no_hp.replace(/[^0-9]/g, '')}`"
                  target="_blank"
                  class="wa-link"
                  v-tooltip="'Hubungi via WhatsApp'"
                >
                  <i class="pi pi-whatsapp" /> {{ data.no_hp }}
                </a>
              </div>
              <span class="reporter-email">{{ data.reporter_email }}</span>
            </div>
          </template>
        </Column>

        <Column header="OPD" style="width: 220px">
          <template #body="{ data }">
            <span class="opd-name">{{ data.nama_opd }}</span>
          </template>
        </Column>

        <Column header="Waktu & Tempat" style="width: 200px">
          <template #body="{ data }">
            <div class="event-meta">
              <div><strong>Waktu:</strong> {{ data.waktu_kejadian }}</div>
              <div><strong>Tempat:</strong> {{ data.tempat }}</div>
            </div>
          </template>
        </Column>

        <Column header="Uraian Kejadian & Pemicu" style="min-width: 260px">
          <template #body="{ data }">
            <div class="desc-box">
              <p class="uraian-txt"><strong>Kejadian:</strong> {{ data.uraian_kejadian }}</p>
              <p class="pemicu-txt"><strong>Pemicu:</strong> {{ data.pemicu }}</p>
            </div>
          </template>
        </Column>

        <Column header="Status" style="width: 140px; text-align: center">
          <template #body="{ data }">
            <Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" />
            <div v-if="data.validated_by_name" class="validated-by">
              Oleh: {{ data.validated_by_name }}
            </div>
          </template>
        </Column>

        <Column header="Aksi" style="width: 130px; text-align: center">
          <template #body="{ data }">
            <div class="action-buttons">
              <Button
                icon="pi pi-check-square"
                severity="primary"
                rounded
                outlined
                size="small"
                v-tooltip.top="'Validasi Laporan'"
                @click="openValidationDialog(data)"
              />
              <Button
                v-if="auth.isAdmin"
                icon="pi pi-trash"
                severity="danger"
                rounded
                outlined
                size="small"
                v-tooltip.top="'Hapus Laporan'"
                @click="confirmDelete(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog Validasi Kejadian -->
    <Dialog
      v-model:visible="dialogVisible"
      modal
      header="Validasi Laporan Kejadian Risiko"
      :style="{ width: '680px' }"
    >
      <div v-if="selectedItem" class="validation-dialog-body">
        <div class="dialog-report-summary">
          <div class="sum-row">
            <span class="sum-lbl">Pelapor:</span>
            <span class="sum-val font-bold">{{ selectedItem.nama_lengkap }} ({{ selectedItem.no_hp }})</span>
          </div>
          <div class="sum-row">
            <span class="sum-lbl">OPD:</span>
            <span class="sum-val">{{ selectedItem.nama_opd }} (Tahun {{ selectedItem.tahun }})</span>
          </div>
          <div class="sum-row">
            <span class="sum-lbl">Waktu Kejadian:</span>
            <span class="sum-val">{{ selectedItem.waktu_kejadian }}</span>
          </div>
          <div class="sum-row">
            <span class="sum-lbl">Tempat:</span>
            <span class="sum-val">{{ selectedItem.tempat }}</span>
          </div>
          <div class="sum-col">
            <span class="sum-lbl">Uraian Kejadian:</span>
            <p class="sum-txt">{{ selectedItem.uraian_kejadian }}</p>
          </div>
          <div class="sum-col">
            <span class="sum-lbl">Pemicu:</span>
            <p class="sum-txt">{{ selectedItem.pemicu }}</p>
          </div>
        </div>

        <div class="validation-form-section">
          <h3 class="section-title">Keputusan Validasi</h3>

          <div class="decision-radios">
            <div
              class="radio-btn-box approved"
              :class="{ selected: validationStatus === 'disetujui' }"
              @click="validationStatus = 'disetujui'"
            >
              <i class="pi pi-check-circle radio-icon" />
              <div>
                <strong>Setujui Laporan</strong>
                <p>Kejadian terverifikasi sebagai kejadian risiko resmi OPD.</p>
              </div>
            </div>

            <div
              class="radio-btn-box rejected"
              :class="{ selected: validationStatus === 'ditolak' }"
              @click="validationStatus = 'ditolak'"
            >
              <i class="pi pi-times-circle radio-icon" />
              <div>
                <strong>Tolak Laporan</strong>
                <p>Informasi tidak sesuai, duplikat, atau bukan kejadian risiko.</p>
              </div>
            </div>
          </div>

          <div class="field-wrap">
            <label class="field-lbl">Catatan / Umpan Balik Validasi:</label>
            <Textarea
              v-model="validationNotes"
              rows="3"
              placeholder="Berikan catatan, rekomendasi, atau alasan penolakan/persetujuan..."
              class="w-full"
            />
          </div>

          <!-- Opsi Tambahan Jika Disetujui -->
          <div v-if="validationStatus === 'disetujui'" class="extra-approval-options">
            <div class="field-wrap">
              <label class="field-lbl">Tautkan ke Risiko Teridentifikasi (Opsional):</label>
              <Select
                v-model="selectedRisikoId"
                :options="risikoList"
                optionLabel="uraian_risiko"
                optionValue="id"
                filter
                showClear
                placeholder="Pilih risiko yang relevan dari register risiko..."
                class="w-full"
              >
                <template #option="{ option }">
                  <div>
                    <strong>[{{ option.kode_risiko }}]</strong> {{ option.uraian_risiko }}
                  </div>
                </template>
              </Select>
            </div>

            <div v-if="selectedRisikoId" class="checkbox-row">
              <Checkbox v-model="copyToForm10" binary inputId="copyF10" />
              <label for="copyF10" class="checkbox-lbl">
                Salin otomatis ke <strong>Form 10 (Monitoring Risk Event)</strong> pada register risiko
              </label>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Batal" severity="secondary" text @click="dialogVisible = false" />
        <Button
          label="Simpan Validasi"
          icon="pi pi-check"
          :loading="savingValidation"
          @click="saveValidation"
        />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.approval-page {
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


.card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  color: #94a3b8;
}

.search-input {
  padding-left: 2.4rem !important;
  width: 280px;
}

.date-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.8rem;
}

.date-txt {
  color: #334155;
  font-weight: 600;
}

.badge-year {
  background: #e2e8f0;
  color: #475569;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  align-self: flex-start;
}

.pelapor-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.85rem;
}

.contact-links {
  margin-top: 0.1rem;
}

.wa-link {
  color: #16a34a;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}
.wa-link:hover {
  text-decoration: underline;
}

.reporter-email {
  font-size: 0.75rem;
  color: #64748b;
}

.opd-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.85rem;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #475569;
}

.desc-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
}

.uraian-txt,
.pemicu-txt {
  margin: 0;
  line-height: 1.4;
  color: #334155;
}

.validated-by {
  font-size: 0.7rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.empty-table-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

/* Dialog Styles */
.validation-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.dialog-report-summary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.sum-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.sum-col {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  margin-top: 0.25rem;
}

.sum-lbl {
  font-weight: 600;
  color: #64748b;
  min-width: 120px;
}

.sum-val {
  color: #1e293b;
}

.sum-txt {
  margin: 0;
  color: #1e293b;
  background: #ffffff;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  line-height: 1.45;
}

.validation-form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
}

.decision-radios {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.radio-btn-box {
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.radio-btn-box.approved:hover {
  border-color: #86efac;
}
.radio-btn-box.approved.selected {
  border-color: #22c55e;
  background: #f0fdf4;
}

.radio-btn-box.rejected:hover {
  border-color: #fca5a5;
}
.radio-btn-box.rejected.selected {
  border-color: #ef4444;
  background: #fef2f2;
}

.radio-icon {
  font-size: 1.4rem;
  margin-top: 2px;
}
.approved .radio-icon {
  color: #22c55e;
}
.rejected .radio-icon {
  color: #ef4444;
}

.radio-btn-box strong {
  display: block;
  font-size: 0.9rem;
  color: #1e293b;
}

.radio-btn-box p {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.35;
}

.field-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-lbl {
  font-size: 0.85rem;
  font-weight: 600;
  color: #334155;
}

.extra-approval-options {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-lbl {
  font-size: 0.825rem;
  color: #166534;
  cursor: pointer;
}
</style>
