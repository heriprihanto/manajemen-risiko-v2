<script setup>
import { computed, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { formatDate, parseDateOnly, toDateOnlyString } from '@/utils/date'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const toast = useToast()
const confirm = useConfirm()

const items = ref([]) // Data risiko beserta events per risiko
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const selectedItem = ref(null)

const editing = ref({
  id: null,
  risiko_id: null,
  tempat_kejadian: '',
  uraian_kejadian: '',
  sebab_kejadian: '',
  dampak_kejadian: '',
  bukti_list: [{ nama: '', link: '' }],
})
const tanggal = ref(null)

const searchQuery = ref('')
const filterJenis = ref('all')

const jenisLabels = {
  strategis_pemda: 'Strategis Pemda',
  strategis_opd: 'Strategis OPD',
  operasional_opd: 'Operasional OPD',
}

const jenisOptions = [
  { value: 'all', label: 'Semua Jenis Risiko' },
  { value: 'strategis_pemda', label: 'Strategis Pemda (Form 3.a)' },
  { value: 'strategis_opd', label: 'Strategis OPD (Form 3.b)' },
  { value: 'operasional_opd', label: 'Operasional OPD (Form 3.c)' },
]

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
    // bukan JSON, format URL tunggal legacy
  }
  return [
    {
      nama: buktiNama || 'Bukti Dukung',
      link: buktiLink,
    },
  ]
}

function addEvidenceRow() {
  if (!editing.value.bukti_list) {
    editing.value.bukti_list = []
  }
  editing.value.bukti_list.push({ nama: '', link: '' })
}

function removeEvidenceRow(idx) {
  editing.value.bukti_list.splice(idx, 1)
  if (!editing.value.bukti_list.length) {
    addEvidenceRow()
  }
}

function openExternalUrl(url) {
  if (!url) return
  const target = /^https?:\/\//i.test(url) ? url : `https://${url}`
  window.open(target, '_blank', 'noopener,noreferrer')
}

function parseDateTime(val) {
  if (!val) return null
  if (val instanceof Date) return val
  const s = String(val).trim()
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?/)
  if (m) {
    const year = parseInt(m[1], 10)
    const month = parseInt(m[2], 10) - 1
    const day = parseInt(m[3], 10)
    const hour = m[4] ? parseInt(m[4], 10) : 0
    const minute = m[5] ? parseInt(m[5], 10) : 0
    const second = m[6] ? parseInt(m[6], 10) : 0
    return new Date(year, month, day, hour, minute, second)
  }
  const d = new Date(s)
  return isNaN(d.getTime()) ? null : d
}

function formatDateTimeString(val) {
  if (!val) return ''
  if (val instanceof Date) {
    const pad = (n) => String(n).padStart(2, '0')
    const yyyy = val.getFullYear()
    const mm = pad(val.getMonth() + 1)
    const dd = pad(val.getDate())
    const hh = pad(val.getHours())
    const mi = pad(val.getMinutes())
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
  }
  return String(val)
}

function formatEventDateTime(val) {
  if (!val) return '—'
  const d = parseDateTime(val)
  if (!d) return String(val)
  const s = String(val).trim()
  const pad = (n) => String(n).padStart(2, '0')
  const tgl = d.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  const hasTime = /[ T]\d{2}:\d{2}/.test(s) || (d.getHours() !== 0 || d.getMinutes() !== 0)
  if (hasTime) {
    return `${tgl}, ${pad(d.getHours())}.${pad(d.getMinutes())} WIB`
  }
  return tgl
}

async function loadData() {
  if (!ctx.opdId || !ctx.tahun) return
  loading.value = true
  try {
    const { data } = await api.get('/monitoring/risk-event', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    items.value = Array.isArray(data) ? data : []
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal memuat data monitoring kejadian risiko'
    toast.add({ severity: 'error', summary: 'Gagal Memuat', detail: err, life: 4000 })
  } finally {
    loading.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun], loadData, { immediate: true })

// Daftar seluruh catatan kejadian risiko (dimulai dari kosong jika belum ada entri)
const eventRows = computed(() => {
  const result = []
  for (const r of items.value) {
    for (const ev of (r.events || [])) {
      result.push({
        ...ev,
        kode_risiko: r.kode_risiko,
        uraian_risiko: r.uraian_risiko,
        jenis_risiko: r.jenis_risiko,
        pemilik_risiko: r.pemilik_risiko,
      })
    }
  }
  return result.sort((a, b) => {
    const tglA = a.waktu_kejadian || a.tanggal_terjadi || ''
    const tglB = b.waktu_kejadian || b.tanggal_terjadi || ''
    return tglB.localeCompare(tglA) || (b.id - a.id)
  })
})

// Opsi daftar risiko untuk Dropdown Select
const risikoOptions = computed(() => {
  return items.value.map((r) => ({
    id: r.risiko_id,
    label: `${r.kode_risiko ? '[' + r.kode_risiko + '] ' : ''}${r.uraian_risiko}`,
    kode: r.kode_risiko,
    uraian: r.uraian_risiko,
    jenis: r.jenis_risiko,
  }))
})

// Filter data kejadian risiko
const filteredEvents = computed(() => {
  return eventRows.value.filter((ev) => {
    if (filterJenis.value !== 'all' && ev.jenis_risiko !== filterJenis.value) {
      return false
    }

    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchKode = ev.kode_risiko?.toLowerCase().includes(q)
      const matchUraian = ev.uraian_risiko?.toLowerCase().includes(q)
      const matchPemilik = ev.pemilik_risiko?.toLowerCase().includes(q)
      const matchTempat = ev.tempat_kejadian?.toLowerCase().includes(q)
      const matchKejadian = ev.uraian_kejadian?.toLowerCase().includes(q)
      const matchSebab = ev.sebab_kejadian?.toLowerCase().includes(q)
      const matchDampak = ev.dampak_kejadian?.toLowerCase().includes(q)
      const matchBukti = ev.bukti_nama?.toLowerCase().includes(q) || ev.bukti_link?.toLowerCase().includes(q)
      if (!matchKode && !matchUraian && !matchPemilik && !matchTempat && !matchKejadian && !matchSebab && !matchDampak && !matchBukti) {
        return false
      }
    }

    return true
  })
})

// Ringkasan KPI Stat Cards (Style Realisasi RTP / Laporan Rekapitulasi)
const summary = computed(() => {
  const totalRisiko = items.value.length
  const totalKejadian = eventRows.value.length
  const uniqueRiskIds = new Set(eventRows.value.map((e) => e.risiko_id))
  const risikoDenganKejadian = uniqueRiskIds.size
  const risikoNirKejadian = Math.max(0, totalRisiko - risikoDenganKejadian)
  return { totalRisiko, risikoDenganKejadian, totalKejadian, risikoNirKejadian }
})

function onRisikoSelectChange(newRisikoId) {
  const found = items.value.find((r) => r.risiko_id === newRisikoId)
  selectedItem.value = found || null
}

function openNew() {
  selectedItem.value = null
  editing.value = {
    id: null,
    risiko_id: null,
    tempat_kejadian: '',
    uraian_kejadian: '',
    sebab_kejadian: '',
    dampak_kejadian: '',
    bukti_list: [{ nama: '', link: '' }],
  }
  tanggal.value = new Date()
  dialogVisible.value = true
}

function openEdit(ev) {
  const parentRisk = items.value.find((r) => r.risiko_id === ev.risiko_id) || null
  selectedItem.value = parentRisk
  let list = parseEvidenceList(ev.bukti_link, ev.bukti_nama)
  if (!list.length) {
    list = [{ nama: '', link: '' }]
  }
  editing.value = {
    id: ev.id,
    risiko_id: ev.risiko_id,
    tempat_kejadian: ev.tempat_kejadian || '',
    uraian_kejadian: ev.uraian_kejadian || '',
    sebab_kejadian: ev.sebab_kejadian || '',
    dampak_kejadian: ev.dampak_kejadian || '',
    bukti_list: list,
  }
  tanggal.value = parseDateTime(ev.waktu_kejadian || ev.tanggal_terjadi)
  dialogVisible.value = true
}

async function save() {
  if (!editing.value.risiko_id) {
    toast.add({
      severity: 'warn',
      summary: 'Uraian Risiko Wajib Dipilih',
      detail: 'Silakan pilih uraian risiko yang terkait dengan kejadian ini.',
      life: 3000,
    })
    return
  }

  if (!tanggal.value) {
    toast.add({
      severity: 'warn',
      summary: 'Waktu Kejadian Wajib Diisi',
      detail: 'Silakan tentukan tanggal / waktu terjadinya peristiwa risiko.',
      life: 3000,
    })
    return
  }

  if (!editing.value.tempat_kejadian?.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Tempat Kejadian Wajib Diisi',
      detail: 'Mohon cantumkan tempat atau lokasi terjadinya peristiwa risiko.',
      life: 3000,
    })
    return
  }

  if (!editing.value.uraian_kejadian?.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Uraian Kejadian Wajib Diisi',
      detail: 'Mohon jelaskan secara rinci uraian peristiwa yang terjadi.',
      life: 3000,
    })
    return
  }

  if (!editing.value.sebab_kejadian?.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Pemicu / Sebab Wajib Diisi',
      detail: 'Mohon isi pemicu atau faktor penyebab terjadinya kejadian.',
      life: 3000,
    })
    return
  }

  if (!editing.value.dampak_kejadian?.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Dampak Kejadian Wajib Diisi',
      detail: 'Mohon isi dampak kerugian yang ditimbulkan dari kejadian ini.',
      life: 3000,
    })
    return
  }

  // Filter bukti yang memiliki link
  const validEvidences = (editing.value.bukti_list || [])
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

  validEvidences.forEach((b, i) => {
    if (!b.nama) b.nama = `Bukti Dukung Kejadian ${i + 1}`
  })

  const dateOnlyStr = toDateOnlyString(tanggal.value)
  const dateTimeStr = formatDateTimeString(tanggal.value)
  const payload = {
    risiko_id: editing.value.risiko_id,
    tanggal_terjadi: dateOnlyStr,
    waktu_kejadian: dateTimeStr,
    tempat_kejadian: editing.value.tempat_kejadian.trim(),
    uraian_kejadian: editing.value.uraian_kejadian.trim(),
    sebab_kejadian: editing.value.sebab_kejadian.trim(),
    dampak_kejadian: editing.value.dampak_kejadian.trim(),
    bukti_link: validEvidences.length ? validEvidences : null,
    bukti_nama: validEvidences[0]?.nama || null,
  }

  saving.value = true
  try {
    if (editing.value.id) {
      await api.put(`/monitoring/risk-event/${editing.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil Diperbarui', detail: 'Catatan kejadian risiko berhasil disimpan.', life: 3000 })
    } else {
      await api.post('/monitoring/risk-event', payload)
      toast.add({ severity: 'success', summary: 'Berhasil Ditambahkan', detail: 'Catatan kejadian risiko baru berhasil disimpan.', life: 3000 })
    }
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal menyimpan kejadian risiko'
    toast.add({ severity: 'error', summary: 'Gagal Menyimpan', detail: err, life: 4000 })
  } finally {
    saving.value = false
  }
}

function remove(ev) {
  confirm.require({
    message: 'Apakah Anda yakin ingin menghapus catatan kejadian risiko ini?',
    header: 'Konfirmasi Penghapusan',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Ya, Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/monitoring/risk-event/${ev.id}`)
        toast.add({ severity: 'success', summary: 'Terhapus', detail: 'Catatan kejadian berhasil dihapus.', life: 2500 })
        await loadData()
      } catch (e) {
        const err = e.response?.data?.detail || e.message || 'Gagal menghapus catatan'
        toast.add({ severity: 'error', summary: 'Gagal Menghapus', detail: err, life: 4000 })
      }
    },
  })
}
</script>

<template>
  <div class="monitoring-event-page">
    <!-- Header Section (Persis Style Realisasi RTP) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-history"></i>
        </div>
        <div>
          <h1 class="page-title">Monitoring Kejadian Risiko (Risk Event)</h1>
          <p class="page-desc">
            Pencatatan dan pemantauan kejadian risiko aktual (Risk Event) serta evaluasi penanganannya (Form 10)
          </p>
        </div>
      </div>
      <div class="header-actions">
        <Button
          label="Catat Kejadian Risiko"
          icon="pi pi-plus"
          class="btn-create-event"
          @click="openNew"
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

    <!-- Stat Cards Header (Persis Style Realisasi RTP / Laporan Rekapitulasi) -->
    <div class="stat-grid no-print" style="margin-bottom: 18px;">
      <div class="stat">
        <div class="v">{{ summary.totalKejadian }}</div>
        <div class="l">Total Kejadian Dicatat</div>
      </div>

      <div class="stat">
        <div class="v">
          {{ summary.risikoDenganKejadian }}
          <small v-if="summary.totalRisiko">({{ Math.round(summary.risikoDenganKejadian / summary.totalRisiko * 100) }}%)</small>
        </div>
        <div class="l">Risiko Terkena Peristiwa</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.totalRisiko }}</div>
        <div class="l">Total Risiko Teridentifikasi</div>
      </div>

      <div class="stat">
        <div class="v">{{ summary.risikoNirKejadian }}</div>
        <div class="l">Risiko Tanpa Kejadian</div>
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
              placeholder="Cari kode risiko, uraian, tempat, kejadian, sebab, atau dampak..."
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
            v-model="filterJenis"
            :options="jenisOptions"
            optionLabel="label"
            optionValue="value"
            class="filter-select"
          />
        </div>

        <div class="summary-count">
          Menampilkan <strong>{{ filteredEvents.length }}</strong> dari <strong>{{ eventRows.length }}</strong> catatan kejadian risiko
        </div>
      </div>

      <!-- Data Table Kejadian Risiko (Mulai dari Kosong) -->
      <DataTable
        :value="filteredEvents"
        :loading="loading"
        stripedRows
        responsiveLayout="scroll"
        class="custom-table"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-history text-4xl text-slate-300 mb-2" />
            <p class="empty-title">Belum ada catatan kejadian risiko</p>
            <p class="empty-desc">Klik tombol "Catat Kejadian Risiko" di atas untuk menambahkan catatan peristiwa risiko baru.</p>
          </div>
        </template>

        <!-- No -->
        <Column header="No" :style="{ width: '50px', textAlign: 'center' }">
          <template #body="{ index }">
            <span class="index-num">{{ index + 1 }}</span>
          </template>
        </Column>

        <!-- Kode & Jenis Risiko -->
        <Column header="Kode & Jenis" :style="{ minWidth: '130px' }">
          <template #body="{ data }">
            <div class="kode-box">
              <span class="badge-kode">{{ data.kode_risiko || '—' }}</span>
              <span v-if="data.jenis_risiko" class="badge-jenis" :class="`jenis-${data.jenis_risiko}`">
                {{ jenisLabels[data.jenis_risiko] || data.jenis_risiko }}
              </span>
            </div>
          </template>
        </Column>

        <!-- Uraian Risiko -->
        <Column header="Uraian Risiko" :style="{ minWidth: '220px' }">
          <template #body="{ data }">
            <div class="risk-profile-cell">
              <div class="risk-desc" :title="data.uraian_risiko">{{ data.uraian_risiko }}</div>
              <div v-if="data.pemilik_risiko" class="risk-meta-row">
                <span class="meta-item">
                  <i class="pi pi-user text-xs mr-1 text-slate-400" />{{ data.pemilik_risiko }}
                </span>
              </div>
            </div>
          </template>
        </Column>

        <!-- Waktu Kejadian -->
        <Column header="Waktu Kejadian" :style="{ minWidth: '165px' }">
          <template #body="{ data }">
            <div class="cell-time">
              <i class="pi pi-clock mr-1 text-rose-600 text-xs" />
              <span>{{ formatEventDateTime(data.waktu_kejadian || data.tanggal_terjadi) }}</span>
            </div>
          </template>
        </Column>

        <!-- Tempat Kejadian -->
        <Column header="Tempat Kejadian" :style="{ minWidth: '160px' }">
          <template #body="{ data }">
            <div class="cell-place">
              <i class="pi pi-map-marker mr-1 text-slate-400 text-xs" />
              <span>{{ data.tempat_kejadian || '—' }}</span>
            </div>
          </template>
        </Column>

        <!-- Uraian Kejadian -->
        <Column header="Uraian Kejadian" :style="{ minWidth: '240px' }">
          <template #body="{ data }">
            <div class="cell-uraian">
              {{ data.uraian_kejadian || '—' }}
            </div>
          </template>
        </Column>

        <!-- Pemicu / Sebab Kejadian -->
        <Column header="Pemicu / Sebab" :style="{ minWidth: '180px' }">
          <template #body="{ data }">
            <div class="cell-cause">
              {{ data.sebab_kejadian || '—' }}
            </div>
          </template>
        </Column>

        <!-- Dampak Kejadian -->
        <Column header="Dampak Kejadian" :style="{ minWidth: '180px' }">
          <template #body="{ data }">
            <div class="cell-impact">
              {{ data.dampak_kejadian || '—' }}
            </div>
          </template>
        </Column>

        <!-- Bukti Dukung (Eviden) -->
        <Column header="Bukti Dukung" :style="{ minWidth: '190px' }">
          <template #body="{ data }">
            <div class="evidence-cell">
              <template v-if="parseEvidenceList(data.bukti_link, data.bukti_nama).length">
                <div
                  v-for="(ev, evIdx) in parseEvidenceList(data.bukti_link, data.bukti_nama)"
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
                    <i class="pi pi-link text-xs mr-1 text-rose-600" />
                    <span>{{ ev.nama || 'Tautan Bukti ' + (evIdx + 1) }}</span>
                    <i class="pi pi-external-link text-[10px] text-slate-400 ml-1" />
                  </a>
                </div>
              </template>
              <span v-else class="text-xs text-slate-400 italic">Belum ada</span>
            </div>
          </template>
        </Column>

        <!-- Aksi -->
        <Column header="Aksi" :style="{ width: '120px', textAlign: 'center' }">
          <template #body="{ data }">
            <div class="action-btn-group">
              <Button
                icon="pi pi-pencil"
                size="small"
                severity="secondary"
                variant="outlined"
                class="btn-action-edit"
                title="Ubah catatan kejadian ini"
                @click="openEdit(data)"
              />
              <Button
                icon="pi pi-trash"
                size="small"
                severity="danger"
                variant="outlined"
                class="btn-action-delete"
                title="Hapus catatan kejadian ini"
                @click="remove(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal Dialog Entri / Edit Kejadian Risiko (Persis Style Realisasi RTP) -->
    <Dialog
      v-model:visible="dialogVisible"
      modal
      :header="editing.id ? 'Ubah Catatan Kejadian Risiko' : 'Entri Kejadian Risiko (Risk Event)'"
      :style="{ width: '720px', maxWidth: '95vw' }"
      :closable="!saving"
    >
      <div class="dialog-body">
        <!-- Banner Konteks Risiko (Jika risiko sudah terpilih) -->
        <div v-if="selectedItem" class="risk-context-banner">
          <div class="banner-top-row">
            <span class="badge-kode-lg">{{ selectedItem.kode_risiko }}</span>
            <span class="badge-jenis-lg" :class="`jenis-${selectedItem.jenis_risiko}`">
              {{ jenisLabels[selectedItem.jenis_risiko] || selectedItem.jenis_risiko }}
            </span>
          </div>
          <div class="banner-risk-text">
            {{ selectedItem.uraian_risiko }}
          </div>
        </div>

        <!-- Form Fields (Hanya 6 Poin Field Sesuai Request) -->
        <div class="form-grid">
          <!-- 1. Uraian Risiko -->
          <div class="form-group">
            <label class="form-label required">
              Uraian Risiko
            </label>
            <Select
              v-model="editing.risiko_id"
              :options="risikoOptions"
              optionLabel="label"
              optionValue="id"
              placeholder="Pilih Uraian Risiko"
              class="w-full"
              filter
              @change="onRisikoSelectChange(editing.risiko_id)"
            />
            <small class="form-hint">
              Pilih risiko teridentifikasi pada register risiko OPD yang mengalami kejadian.
            </small>
          </div>

          <!-- Grid 2 Kolom: Waktu Kejadian & Tempat Kejadian -->
          <div class="form-grid-2">
            <!-- 2. Waktu Kejadian -->
            <div class="form-group">
              <label class="form-label required">
                Waktu Kejadian
              </label>
              <DatePicker
                v-model="tanggal"
                dateFormat="dd-mm-yy"
                showTime
                hourFormat="24"
                showIcon
                showButtonBar
                fluid
                placeholder="Pilih tanggal & waktu kejadian"
                class="w-full"
              />
              <small class="form-hint">
                Pilih tanggal beserta jam dan menit (WIB) saat peristiwa risiko terjadi.
              </small>
            </div>

            <!-- 3. Tempat Kejadian -->
            <div class="form-group">
              <label class="form-label required">
                Tempat Kejadian
              </label>
              <InputText
                v-model="editing.tempat_kejadian"
                placeholder="Contoh: Kantor Dinas / Ruang Server Lt. 2 / Lapangan"
                class="w-full"
              />
              <small class="form-hint">
                Lokasi fisik atau tempat peristiwa berlangsung.
              </small>
            </div>
          </div>

          <!-- 4. Uraian Kejadian -->
          <div class="form-group">
            <label class="form-label required">
              Uraian Kejadian
            </label>
            <Textarea
              v-model="editing.uraian_kejadian"
              rows="3"
              autoResize
              placeholder="Jelaskan secara rinci kronologi, rincian peristiwa, atau insiden risiko yang terjadi..."
              class="w-full"
            />
            <small class="form-hint">
              Deskripsi peristiwa aktual insiden risiko secara lengkap dan objektif.
            </small>
          </div>

          <!-- 5. Pemicu / Sebab Kejadian -->
          <div class="form-group">
            <label class="form-label required">
              Pemicu / Sebab Kejadian
            </label>
            <Textarea
              v-model="editing.sebab_kejadian"
              rows="2"
              autoResize
              placeholder="Faktor penyebab langsung atau pemicu timbulnya peristiwa risiko ini..."
              class="w-full"
            />
            <small class="form-hint">
              Penyebab langsung, kesalahan sistem, kelalaian prosedur, atau faktor eksternal pemicu.
            </small>
          </div>

          <!-- 6. Dampak Kejadian -->
          <div class="form-group">
            <label class="form-label required">
              Dampak Kejadian
            </label>
            <Textarea
              v-model="editing.dampak_kejadian"
              rows="2"
              autoResize
              placeholder="Dampak nyata kerugian (keuangan, keterlambatan, reputasi, gangguan layanan publik, dll)..."
              class="w-full"
            />
            <small class="form-hint">
              Konsekuensi dan akibat negatif yang dialami organisasi atau masyarakat.
            </small>
          </div>

          <!-- 7. Berkas Bukti Dukung (Paling Bawah Form, Bisa Lebih dari Satu) -->
          <div class="form-group">
            <div class="form-label-row">
              <label class="form-label mb-0">
                Berkas Bukti Dukung (Eviden Fisik / Digital)
              </label>
              <span class="label-badge-optional">Google Drive / OneDrive / Dropbox / Cloud Storage</span>
            </div>
            <small class="form-hint" style="margin-top: 0; margin-bottom: 0.65rem;">
              Masukkan nama berkas dan tautan link bukti dukung. Anda dapat menambahkan lebih dari satu berkas.
            </small>

            <div class="evidence-list-wrap">
              <div
                v-for="(b, idx) in editing.bukti_list"
                :key="idx"
                class="evidence-row-card"
              >
                <div class="evidence-row-header">
                  <span class="evidence-row-num">#{{ idx + 1 }}</span>
                  <span class="evidence-row-title">Berkas Bukti Dukung {{ idx + 1 }}</span>
                  <Button
                    v-if="editing.bukti_list.length > 1"
                    icon="pi pi-trash"
                    severity="danger"
                    text
                    rounded
                    size="small"
                    class="btn-remove-evidence"
                    v-tooltip.top="'Hapus berkas ini'"
                    @click="removeEvidenceRow(idx)"
                  />
                </div>

                <div class="evidence-fields-grid">
                  <div class="field-item">
                    <label class="field-sublabel">Nama Berkas Bukti Dukung</label>
                    <InputText
                      v-model="b.nama"
                      :placeholder="`Contoh: Foto Kejadian / Berita Acara / Laporan Insiden ${idx + 1}`"
                      class="form-input-text-sub"
                    />
                  </div>

                  <div class="field-item">
                    <label class="field-sublabel">Tautan / Link Dokumen Bukti Dukung</label>
                    <div class="input-with-icon">
                      <i class="pi pi-link input-icon" />
                      <InputText
                        v-model="b.link"
                        placeholder="https://drive.google.com/... atau tautan cloud storage"
                        class="form-input-text"
                      />
                      <Button
                        v-if="b.link"
                        icon="pi pi-external-link"
                        severity="secondary"
                        text
                        size="small"
                        class="btn-test-link"
                        v-tooltip.top="'Uji / Buka Tautan'"
                        @click="openExternalUrl(b.link)"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="add-evidence-action">
                <Button
                  label="Tambah Berkas Bukti Dukung Lainnya"
                  icon="pi pi-plus"
                  severity="secondary"
                  variant="outlined"
                  size="small"
                  class="btn-add-evidence"
                  @click="addEvidenceRow"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Batal"
            icon="pi pi-times"
            severity="secondary"
            variant="text"
            :disabled="saving"
            @click="dialogVisible = false"
          />
          <Button
            label="Simpan Kejadian"
            icon="pi pi-check"
            class="btn-save-event"
            :loading="saving"
            @click="save"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.monitoring-event-page {
  padding-bottom: 2rem;
}

/* Header Section (Persis Style Realisasi RTP) */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
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
  background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(225, 29, 72, 0.25);
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

.btn-create-event {
  background: #e11d48 !important;
  border-color: #e11d48 !important;
  font-weight: 600;
}

.btn-create-event:hover {
  background: #be123c !important;
  border-color: #be123c !important;
}

/* Stat Grid Header (Persis Style Realisasi RTP / Rekapitulasi) */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.stat {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 14px 18px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.stat .v {
  font-size: 1.65rem;
  font-weight: 750;
  color: #0f172a;
  line-height: 1.2;
}

.stat .v small {
  font-size: 0.825rem;
  font-weight: 600;
  color: #64748b;
}

.stat .l {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  margin-top: 4px;
}

/* Main Card & Table Toolbar (Persis Style Realisasi RTP) */
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

/* Table Cells & Badges */
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
}

.risk-meta-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #64748b;
}

.meta-item {
  display: flex;
  align-items: center;
}

.cell-time {
  font-size: 0.825rem;
  font-weight: 650;
  color: #be123c;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.cell-place {
  font-size: 0.825rem;
  color: #334155;
  display: flex;
  align-items: center;
}

.cell-uraian {
  font-size: 0.825rem;
  color: #1e293b;
  line-height: 1.4;
}

.cell-cause {
  font-size: 0.825rem;
  color: #b45309;
  line-height: 1.4;
}

.cell-impact {
  font-size: 0.825rem;
  color: #be123c;
  font-weight: 600;
  line-height: 1.4;
}

.action-btn-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.btn-action-edit, .btn-action-delete {
  width: 30px !important;
  height: 30px !important;
  padding: 0 !important;
}

/* Modal Dialog (Persis Style Realisasi RTP) */
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

.banner-risk-text {
  font-size: 0.925rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.35;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.form-label {
  font-size: 0.8rem;
  font-weight: 650;
  color: #334155;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-hint {
  font-size: 0.72rem;
  color: #64748b;
  line-height: 1.35;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-save-event {
  background: #e11d48 !important;
  border-color: #e11d48 !important;
  font-weight: 600;
}

.btn-save-event:hover {
  background: #be123c !important;
  border-color: #be123c !important;
}

.empty-state {
  text-align: center;
  padding: 3.5rem 1.5rem;
  color: #64748b;
}

.empty-title {
  font-weight: 650;
  font-size: 1.05rem;
  color: #1e293b;
  margin: 0.5rem 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
}

@media (max-width: 900px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
  }
  .btn-create-event {
    flex: 1;
  }
  .stat-grid {
    grid-template-columns: 1fr;
  }
  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-wrap {
    max-width: 100%;
  }
  .form-grid-2 {
    grid-template-columns: 1fr;
  }
}

/* Bukti Dukung (Eviden) Styling */
.form-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.label-badge-optional {
  font-size: 0.68rem;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
}

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
  font-size: 0.75rem;
  color: #0284c7;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-external-link:hover {
  text-decoration: underline;
  color: #0369a1;
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
  padding: 0.85rem 1rem;
  transition: border-color 0.15s ease;
}

.evidence-row-card:hover {
  border-color: #cbd5e1;
}

.evidence-row-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px dashed #e2e8f0;
}

.evidence-row-num {
  font-size: 0.72rem;
  font-weight: 700;
  color: #e11d48;
  background: #fff1f2;
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

.add-evidence-action {
  display: flex;
  justify-content: flex-start;
  margin-top: 0.25rem;
}

.btn-add-evidence {
  font-size: 0.8rem !important;
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
</style>
