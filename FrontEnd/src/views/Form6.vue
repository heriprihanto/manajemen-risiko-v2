<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { formatDate, parseDateOnly, toDateOnlyString } from '@/utils/date'

const ctx = useContextStore()
const toast = useToast()
const confirm = useConfirm()

// State data & filter
const rows = ref([])
const loading = ref(false)
const saving = ref(false)
const search = ref('')
const selectedAspek = ref(null)

// Pilihan cascading dari Form 1.c
const aspekOptions = ref([])
const permasalahanOptions = ref([])

// State dialog entri
const dialogVisible = ref(false)
const isEdit = ref(false)
const legacyTarget = ref('')
const form = ref({
  id: null,
  no_urut: '',
  aspek_cee: null,
  kondisi_kerentanan: '',
  rencana_tindak: '',
  pemilik_penanggung_jawab: '',
  target_mulai: null,
  target_selesai: null,
})

// Opsi kondisi permasalahan yang difilter sesuai aspek terpilih
const filteredPermasalahan = computed(() => {
  if (!form.value.aspek_cee) return []
  return permasalahanOptions.value.filter(
    (p) => !p.aspek_cee || p.aspek_cee === form.value.aspek_cee,
  )
})

// Filter data tabel
const filteredRows = computed(() => {
  let list = rows.value || []
  if (selectedAspek.value) {
    list = list.filter((r) => r.aspek_cee === selectedAspek.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    list = list.filter(
      (r) =>
        (r.aspek_cee && r.aspek_cee.toLowerCase().includes(q)) ||
        (r.kondisi_kerentanan && r.kondisi_kerentanan.toLowerCase().includes(q)) ||
        (r.rencana_tindak && r.rencana_tindak.toLowerCase().includes(q)) ||
        (r.pemilik_penanggung_jawab && r.pemilik_penanggung_jawab.toLowerCase().includes(q)) ||
        (r.target_waktu && r.target_waktu.toLowerCase().includes(q)) ||
        (r.no_urut && String(r.no_urut).toLowerCase().includes(q)),
    )
  }
  return list
})


// Muat data master aspek & permasalahan dari Form 1.c
async function loadMasterOptions() {
  if (!ctx.opdId || !ctx.tahun) return
  try {
    const [resAspek, resMasalah] = await Promise.all([
      api.get('/cee/form1c/aspek', { params: { opd_id: ctx.opdId, tahun: ctx.tahun } }),
      api.get('/cee/form1c/permasalahan', { params: { opd_id: ctx.opdId, tahun: ctx.tahun } }),
    ])
    aspekOptions.value = resAspek.data || []
    permasalahanOptions.value = resMasalah.data || []
  } catch {
    aspekOptions.value = []
    permasalahanOptions.value = []
  }
}

// Muat data Form 6 (RTP atas CEE)
async function loadData() {
  if (!ctx.opdId || !ctx.tahun) return
  loading.value = true
  try {
    const { data } = await api.get('/cee/rtp-cee', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    rows.value = data || []
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Memuat Data',
      detail: err?.response?.data?.detail || 'Tidak dapat mengambil data RTP atas CEE',
      life: 3000,
    })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  legacyTarget.value = ''
  // No urut berikutnya otomatis
  const nextNo = rows.value.length + 1
  form.value = {
    id: null,
    no_urut: String(nextNo),
    aspek_cee: null,
    kondisi_kerentanan: '',
    rencana_tindak: '',
    pemilik_penanggung_jawab: '',
    target_mulai: null,
    target_selesai: null,
  }
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  let mulai = row.target_mulai ? parseDateOnly(row.target_mulai) : null
  let selesai = row.target_selesai ? parseDateOnly(row.target_selesai) : null
  let legacy = ''

  if (!mulai && !selesai && row.target_waktu) {
    const tw = String(row.target_waktu).trim()
    if (tw.includes(' s.d. ')) {
      const [s, e] = tw.split(' s.d. ')
      mulai = parseDateOnly(s)
      selesai = parseDateOnly(e)
    } else if (/^\d{4}-\d{2}-\d{2}$/.test(tw)) {
      mulai = parseDateOnly(tw)
      selesai = parseDateOnly(tw)
    } else {
      legacy = tw
    }
  }

  form.value = {
    id: row.id,
    no_urut: row.no_urut || '',
    aspek_cee: row.aspek_cee || null,
    kondisi_kerentanan: row.kondisi_kerentanan || '',
    rencana_tindak: row.rencana_tindak || '',
    pemilik_penanggung_jawab: row.pemilik_penanggung_jawab || '',
    target_mulai: mulai,
    target_selesai: selesai,
  }
  legacyTarget.value = legacy
  dialogVisible.value = true
}

function onAspekChange() {
  // Kosongkan permasalahan jika aspek berubah dan permasalahan lama tidak sesuai
  if (
    form.value.kondisi_kerentanan &&
    !filteredPermasalahan.value.some((p) => p.value === form.value.kondisi_kerentanan)
  ) {
    form.value.kondisi_kerentanan = ''
  }
}

async function save() {
  if (!form.value.aspek_cee) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Pilih aspek / sub-unsur CEE terlebih dahulu',
      life: 2500,
    })
    return
  }
  if (!form.value.rencana_tindak?.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Rencana Tindak Pengendalian wajib diisi',
      life: 2500,
    })
    return
  }
  if (
    form.value.target_mulai &&
    form.value.target_selesai &&
    form.value.target_mulai > form.value.target_selesai
  ) {
    toast.add({
      severity: 'error',
      summary: 'Rentang Tanggal Salah',
      detail: 'Tanggal mulai tidak boleh melewati tanggal selesai',
      life: 3000,
    })
    return
  }

  const sMulai = toDateOnlyString(form.value.target_mulai)
  const sSelesai = toDateOnlyString(form.value.target_selesai)

  let tw = null
  if (sMulai && sSelesai) {
    tw = `${sMulai} s.d. ${sSelesai}`
  } else if (sMulai) {
    tw = sMulai
  } else if (sSelesai) {
    tw = sSelesai
  } else if (legacyTarget.value) {
    tw = legacyTarget.value
  }

  const payload = {
    opd_id: ctx.opdId,
    tahun: ctx.tahun,
    no_urut: form.value.no_urut || null,
    aspek_cee: form.value.aspek_cee,
    kondisi_kerentanan: form.value.kondisi_kerentanan || null,
    rencana_tindak: form.value.rencana_tindak.trim(),
    pemilik_penanggung_jawab: form.value.pemilik_penanggung_jawab?.trim() || null,
    target_mulai: sMulai,
    target_selesai: sSelesai,
    target_waktu: tw,
  }

  saving.value = true
  try {
    if (isEdit.value && form.value.id) {
      await api.put(`/cee/rtp-cee/${form.value.id}`, payload)
      toast.add({
        severity: 'success',
        summary: 'Tersimpan',
        detail: 'RTP atas CEE berhasil diperbarui',
        life: 2000,
      })
    } else {
      await api.post('/cee/rtp-cee', payload)
      toast.add({
        severity: 'success',
        summary: 'Tersimpan',
        detail: 'RTP atas CEE berhasil ditambahkan',
        life: 2000,
      })
    }
    dialogVisible.value = false
    await loadData()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: err?.response?.data?.detail || 'Terjadi kesalahan sistem',
      life: 3000,
    })
  } finally {
    saving.value = false
  }
}

function remove(row) {
  confirm.require({
    message: `Hapus rencana tindak "${row.rencana_tindak?.slice(0, 60)}..."?`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/cee/rtp-cee/${row.id}`)
        toast.add({
          severity: 'success',
          summary: 'Terhapus',
          detail: 'Data berhasil dihapus',
          life: 2000,
        })
        await loadData()
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

watch([() => ctx.opdId, () => ctx.tahun], () => {
  loadMasterOptions()
  loadData()
})

onMounted(() => {
  loadMasterOptions()
  loadData()
})
</script>

<template>
  <div class="form6-page">
    <!-- Header Section (Style Kamus Risiko) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-wrench"></i>
        </div>
        <div>
          <h1 class="page-title">RTP atas CEE</h1>
          <p class="page-desc">
            Penilaian Kegiatan Pengendalian dan Rencana Tindak Pengendalian (RTP) atas kelemahan Lingkungan Pengendalian Intern (CEE)
          </p>
        </div>
      </div>
      <div class="header-actions">
        <div class="ctx-chip" title="Konteks Penilaian Aktif">
          <i class="pi pi-building"></i>
          <span>{{ ctx.opd?.nama_pd || 'Semua OPD' }}</span>
          <span class="chip-dot">•</span>
          <span>Tahun {{ ctx.tahun }}</span>
        </div>
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          @click="loadData"
          :loading="loading"
        />
        <Button
          label="Tambah RTP CEE"
          icon="pi pi-plus"
          severity="primary"
          @click="openCreate"
        />
      </div>
    </div>

    <!-- Content Card -->
    <div class="content-card">
      <!-- Toolbar Filter & Search -->
      <div class="toolbar-box">
        <div class="filter-group">
          <div class="search-wrap">
            <i class="pi pi-search search-icon"></i>
            <InputText
              v-model="search"
              placeholder="Cari sub-unsur, kelemahan, rencana tindak, atau penanggung jawab..."
              class="search-input"
            />
            <button
              v-if="search"
              type="button"
              class="clear-btn"
              @click="search = ''"
              title="Bersihkan pencarian"
            >
              <i class="pi pi-times"></i>
            </button>
          </div>

          <Select
            v-model="selectedAspek"
            :options="aspekOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Semua Sub-unsur CEE"
            showClear
            class="aspek-filter"
          />
        </div>

        <div class="toolbar-meta">
          <span class="muted text-sm">Menampilkan {{ filteredRows.length }} dari {{ rows.length }} data</span>
        </div>
      </div>

      <!-- Data Table (Realisasi disembunyikan sesuai permintaan) -->
      <DataTable
        :value="filteredRows"
        :loading="loading"
        size="small"
        stripedRows
        responsiveLayout="scroll"
        class="custom-table"
      >
        <Column header="No." style="width: 60px; text-align: center">
          <template #body="{ data, index }">
            <span class="row-num">{{ data.no_urut || index + 1 }}</span>
          </template>
        </Column>

        <Column field="aspek_cee" header="Aspek / Sub-unsur CEE" style="min-width: 180px; width: 18%">
          <template #body="{ data }">
            <div class="aspek-badge">
              <i class="pi pi-bookmark text-xs"></i>
              <span>{{ data.aspek_cee || '—' }}</span>
            </div>
          </template>
        </Column>

        <Column field="kondisi_kerentanan" header="Kondisi Kurang Memadai (Form 1.c)" style="min-width: 240px; width: 25%">
          <template #body="{ data }">
            <span class="cell-text font-medium">{{ data.kondisi_kerentanan || '—' }}</span>
          </template>
        </Column>

        <Column field="rencana_tindak" header="Rencana Tindak Pengendalian" style="min-width: 250px; width: 27%">
          <template #body="{ data }">
            <span class="cell-text text-primary-strong">{{ data.rencana_tindak || '—' }}</span>
          </template>
        </Column>

        <Column field="pemilik_penanggung_jawab" header="Penanggung Jawab" style="min-width: 150px; width: 14%">
          <template #body="{ data }">
            <div v-if="data.pemilik_penanggung_jawab" class="pj-tag">
              <i class="pi pi-user text-xs"></i>
              <span>{{ data.pemilik_penanggung_jawab }}</span>
            </div>
            <span v-else class="muted">—</span>
          </template>
        </Column>

        <Column field="target_waktu" header="Target Waktu" style="min-width: 150px; width: 14%">
          <template #body="{ data }">
            <div v-if="data.target_waktu" class="target-chip">
              <i class="pi pi-calendar text-xs"></i>
              <span>{{ formatDate(data.target_waktu) }}</span>
            </div>
            <span v-else class="muted">—</span>
          </template>
        </Column>

        <Column header="Aksi" style="width: 90px; text-align: center" frozen alignFrozen="right">
          <template #body="{ data }">
            <div class="actions-cell">
              <Button
                icon="pi pi-pencil"
                text
                rounded
                size="small"
                severity="secondary"
                title="Ubah RTP CEE"
                @click="openEdit(data)"
              />
              <Button
                icon="pi pi-trash"
                text
                rounded
                size="small"
                severity="danger"
                title="Hapus RTP CEE"
                @click="remove(data)"
              />
            </div>
          </template>
        </Column>

        <template #empty>
          <div class="empty-state">
            <div class="empty-icon-wrap">
              <i class="pi pi-inbox"></i>
            </div>
            <p class="empty-title">Belum Ada Rencana Tindak Pengendalian (CEE)</p>
            <p class="empty-desc">
              Klik tombol <strong>Tambah RTP CEE</strong> untuk merumuskan rencana tindak pengendalian dari simpulan CEE.
            </p>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Dialog Form Entri Form 6 — RTP atas CEE -->
    <Dialog
      v-model:visible="dialogVisible"
      :header="isEdit ? 'Ubah RTP atas CEE' : 'Tambah RTP atas CEE'"
      modal
      class="form-dialog"
      :style="{ width: '680px', maxWidth: '95vw' }"
    >
      <div class="dialog-body">
        <!-- Info Banner -->
        <div class="dialog-banner">
          <i class="pi pi-info-circle text-lg banner-icon"></i>
          <div>
            <div class="banner-title">Formulir Rencana Tindak Pengendalian Lingkungan Pengendalian</div>
            <div class="banner-desc">
              Pilih sub-unsur dan kondisi yang kurang memadai pada Form 1.c, lalu tentukan rencana tindak serta target waktu pelaksanaannya.
            </div>
          </div>
        </div>

        <div class="form-grid">
          <!-- No Urut -->
          <div class="field-row">
            <label class="field-label" for="no_urut">No. Urut</label>
            <InputText
              id="no_urut"
              v-model="form.no_urut"
              placeholder="Contoh: 1, 2, dst."
              style="width: 140px"
            />
          </div>

          <!-- Aspek CEE -->
          <div class="field-row">
            <label class="field-label" for="aspek_cee">
              Aspek / Sub-unsur CEE <span class="req">*</span>
            </label>
            <Select
              id="aspek_cee"
              v-model="form.aspek_cee"
              :options="aspekOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Pilih sub-unsur CEE (Form 1.c)..."
              filter
              showClear
              class="w-full"
              @change="onAspekChange"
            >
              <template #option="{ option }">
                <div class="select-option-item">
                  <span class="option-title">{{ option.label }}</span>
                  <span v-if="option.kurang_memadai" class="badge-kurang">Kurang Memadai</span>
                </div>
              </template>
            </Select>
          </div>

          <!-- Kondisi Kerentanan -->
          <div class="field-row">
            <label class="field-label" for="kondisi_kerentanan">
              Kondisi Kurang Memadai (Form 1.c)
            </label>
            <Select
              id="kondisi_kerentanan"
              v-model="form.kondisi_kerentanan"
              :options="filteredPermasalahan"
              optionLabel="label"
              optionValue="value"
              editable
              filter
              placeholder="Pilih dari daftar permasalahan atau ketik uraian baru..."
              class="w-full"
              :disabled="!form.aspek_cee"
            />
            <small v-if="!form.aspek_cee" class="field-hint">
              * Pilih Aspek / Sub-unsur CEE terlebih dahulu untuk menampilkan daftar kelemahan.
            </small>
          </div>

          <!-- Rencana Tindak -->
          <div class="field-row">
            <label class="field-label" for="rencana_tindak">
              Rencana Tindak Pengendalian <span class="req">*</span>
            </label>
            <Textarea
              id="rencana_tindak"
              v-model="form.rencana_tindak"
              rows="3"
              autoResize
              placeholder="Uraikan rencana tindak pengendalian secara spesifik, terukur, dan realistis..."
              class="w-full"
            />
          </div>

          <!-- Penanggung Jawab -->
          <div class="field-row">
            <label class="field-label" for="penanggung_jawab">
              Penanggung Jawab Pelaksanaan
            </label>
            <InputText
              id="penanggung_jawab"
              v-model="form.pemilik_penanggung_jawab"
              placeholder="Misal: Kepala OPD / Sekretaris / Kasubag Program / Bidang Terkait"
              class="w-full"
            />
          </div>

          <!-- Target Waktu: Datepicker dari tanggal sampai tanggal -->
          <div class="field-row">
            <label class="field-label">
              Target Waktu Pelaksanaan <span class="req">*</span>
            </label>
            <div class="date-range-container">
              <div class="date-col">
                <label class="date-label-sub" for="target_mulai">Dari Tanggal</label>
                <DatePicker
                  id="target_mulai"
                  v-model="form.target_mulai"
                  dateFormat="dd-mm-yy"
                  showIcon
                  showButtonBar
                  placeholder="Pilih tanggal mulai"
                  :maxDate="form.target_selesai || undefined"
                  class="w-full"
                />
              </div>
              <div class="date-col">
                <label class="date-label-sub" for="target_selesai">Sampai Tanggal</label>
                <DatePicker
                  id="target_selesai"
                  v-model="form.target_selesai"
                  dateFormat="dd-mm-yy"
                  showIcon
                  showButtonBar
                  placeholder="Pilih tanggal selesai"
                  :minDate="form.target_mulai || undefined"
                  class="w-full"
                />
              </div>
            </div>
            <small v-if="legacyTarget" class="legacy-date-note">
              Target waktu sebelumnya: <em>{{ legacyTarget }}</em>. Pilih rentang tanggal untuk memperbaruinya.
            </small>
          </div>

          <!-- NOTE: Field realisasi disembunyikan sama sekali dari form entri sesuai permintaan -->
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Batal"
            severity="secondary"
            variant="text"
            @click="dialogVisible = false"
            :disabled="saving"
          />
          <Button
            label="Simpan"
            icon="pi pi-check"
            severity="primary"
            @click="save"
            :loading="saving"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.form6-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  flex-shrink: 0;
}

.page-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text, #1e293b);
  letter-spacing: -0.01em;
}

.page-desc {
  margin: 3px 0 0;
  font-size: 0.84rem;
  color: var(--text-muted, #64748b);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.ctx-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.chip-dot {
  color: #94a3b8;
}


/* Content Card */
.content-card {
  background: var(--surface, #ffffff);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: var(--radius, 14px);
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
  overflow: hidden;
}

.toolbar-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border, #e2e8f0);
  flex-wrap: wrap;
  background: #fcfdfe;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 260px;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 11px;
  color: #94a3b8;
  font-size: 0.85rem;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 32px;
  padding-right: 30px;
  font-size: 0.84rem;
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.clear-btn:hover {
  color: #475569;
}

.aspek-filter {
  min-width: 220px;
}

.toolbar-meta {
  color: var(--text-muted, #64748b);
}

/* Custom Table */
.custom-table :deep(th) {
  background: #f8fafc;
  color: #1e293b;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
}

.custom-table :deep(td) {
  font-size: 0.84rem;
  padding: 10px 14px;
  vertical-align: top;
  border: 1px solid #e2e8f0;
}

.row-num {
  font-weight: 600;
  color: #64748b;
  font-size: 0.82rem;
}

.aspek-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eef2ff;
  color: #4338ca;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 0.77rem;
  font-weight: 600;
  line-height: 1.4;
}

.cell-text {
  line-height: 1.5;
  color: #334155;
  display: block;
}

.text-primary-strong {
  color: #1e1b4b;
  font-weight: 500;
}

.pj-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #f1f5f9;
  color: #334155;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 500;
}

.target-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.actions-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 36px 16px;
  color: var(--text-muted, #64748b);
}

.empty-icon-wrap {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  border-radius: 12px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #94a3b8;
}

.empty-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #334155;
  margin: 0 0 4px;
}

.empty-desc {
  font-size: 0.82rem;
  margin: 0;
  color: #64748b;
}

/* Dialog Form Entri */
.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 10px;
  padding: 12px 14px;
  color: #312e81;
}

.banner-icon {
  color: #4f46e5;
  margin-top: 2px;
  flex-shrink: 0;
}

.banner-title {
  font-weight: 700;
  font-size: 0.88rem;
}

.banner-desc {
  font-size: 0.78rem;
  color: #4338ca;
  margin-top: 2px;
  line-height: 1.4;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
}

.req {
  color: #dc2626;
}

.field-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.select-option-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 8px;
}

.badge-kurang {
  font-size: 0.68rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: #fee2e2;
  color: #b91c1c;
  font-weight: 600;
}

/* Target Waktu Pelaksanaan - Date Range */
.date-range-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.date-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-label-sub {
  font-size: 0.76rem;
  font-weight: 500;
  color: #64748b;
}

.legacy-date-note {
  font-size: 0.76rem;
  color: #d97706;
  background: #fffbeb;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #fde68a;
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.w-full {
  width: 100%;
}

@media (max-width: 640px) {
  .date-range-container {
    grid-template-columns: 1fr;
  }
}
</style>
