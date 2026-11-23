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
  tanggal_mulai: null,
  tanggal_selesai: null,
  tanggal_realisasi: '',
  uraian_hasil: '',
  hambatan: '',
  bukti_list: [], // Array of { nama: '', link: '' }
})

function formatRealisasiDate(rel) {
  if (!rel) return ''
  const mulai = rel.tanggal_mulai
  const selesai = rel.tanggal_selesai
  if (mulai && selesai && mulai !== selesai) {
    return `${formatDate(mulai)} s.d. ${formatDate(selesai)}`
  }
  if (mulai) return formatDate(mulai)
  if (selesai) return formatDate(selesai)
  if (rel.tanggal_realisasi) return formatDate(rel.tanggal_realisasi)
  return ''
}

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
    addEvidenceRow()
  }
}

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

  let list = parseEvidenceList(rel.bukti_link, rel.bukti_nama)
  if (!list.length) {
    list = [{ nama: '', link: '' }]
  }

  let mulai = rel.tanggal_mulai ? parseDateOnly(rel.tanggal_mulai) : null
  let selesai = rel.tanggal_selesai ? parseDateOnly(rel.tanggal_selesai) : null

  if (!mulai && !selesai && rel.tanggal_realisasi) {
    const tr = String(rel.tanggal_realisasi).trim()
    const match = tr.match(/^(\d{4}-\d{2}-\d{2})\s+s\.d\.\s+(\d{4}-\d{2}-\d{2})$/)
    if (match) {
      mulai = parseDateOnly(match[1])
      selesai = parseDateOnly(match[2])
    } else {
      const single = tr.match(/^(\d{4}-\d{2}-\d{2})/)
      if (single) {
        mulai = parseDateOnly(single[1])
      }
    }
  }

  form.value = {
    risiko_id: row.source_type === 'cee' ? null : (row.risiko_id || row.id),
    rtp_cee_id: row.rtp_cee_id || null,
    status_realisasi: rel.status_realisasi || 'belum',
    tanggal_mulai: mulai,
    tanggal_selesai: selesai,
    tanggal_realisasi: rel.tanggal_realisasi || '',
    uraian_hasil: rel.uraian_hasil || '',
    hambatan: rel.hambatan || '',
    bukti_list: list,
  }

  dialogVisible.value = true
}

async function saveRealisasi() {
  if (!form.value.risiko_id && !form.value.rtp_cee_id) return

  if (form.value.status_realisasi === 'selesai' && !form.value.tanggal_mulai) {
    toast.add({
      severity: 'warn',
      summary: 'Tanggal Pelaksanaan Wajib Diisi',
      detail: 'Untuk status Selesai Terealisasi, mohon tentukan tanggal mulai pelaksanaan.',
      life: 4000,
    })
    return
  }

  if (
    form.value.tanggal_mulai &&
    form.value.tanggal_selesai &&
    form.value.tanggal_mulai > form.value.tanggal_selesai
  ) {
    toast.add({
      severity: 'error',
      summary: 'Rentang Tanggal Salah',
      detail: 'Tanggal mulai tidak boleh melewati tanggal selesai.',
      life: 3000,
    })
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

  if (!validEvidences.length) {
    toast.add({
      severity: 'warn',
      summary: 'Bukti Dukung Wajib Diisi',
      detail: 'Mohon masukkan minimal 1 tautan/link bukti dukung (Google Drive, OneDrive, Dropbox, dsb).',
      life: 4000,
    })
    return
  }

  // Lengkapi nama default jika kosong
  validEvidences.forEach((b, i) => {
    if (!b.nama) b.nama = `Bukti Dukung ${i + 1}`
  })

  const sMulai = toDateOnlyString(form.value.tanggal_mulai)
  const sSelesai = toDateOnlyString(form.value.tanggal_selesai)
  let sTanggalReal = null
  if (sMulai && sSelesai && sMulai !== sSelesai) {
    sTanggalReal = `${sMulai} s.d. ${sSelesai}`
  } else if (sMulai) {
    sTanggalReal = sMulai
  } else if (sSelesai) {
    sTanggalReal = sSelesai
  }

  saving.value = true
  try {
    const payload = {
      risiko_id: form.value.risiko_id || undefined,
      rtp_cee_id: form.value.rtp_cee_id || undefined,
      status_realisasi: form.value.status_realisasi,
      tanggal_mulai: sMulai,
      tanggal_selesai: sSelesai,
      tanggal_realisasi: sTanggalReal,
      uraian_hasil: form.value.uraian_hasil,
      hambatan: form.value.hambatan,
      bukti_link: validEvidences,
      bukti_nama: validEvidences[0]?.nama || null,
    }

    await api.post('/risiko/realisasi', payload)

    toast.add({
      severity: 'success',
      summary: 'Berhasil Disimpan',
      detail: 'Data realisasi RTP dan tautan bukti dukung berhasil diperbarui.',
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
        <router-link to="/laporan-monev-rtp" class="btn-link-monev">
          <Button
            label="Laporan Monev RTP"
            icon="pi pi-file-check"
            severity="info"
            variant="outlined"
          />
        </router-link>
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

              <div v-if="formatRealisasiDate(data.realisasi)" class="tgl-realisasi-tag">
                <i class="pi pi-calendar-check text-xs text-emerald-600 mr-1" />
                {{ formatRealisasiDate(data.realisasi) }}
              </div>
            </div>
          </template>
        </Column>

        <!-- Bukti Dukung (Eviden) -->
        <Column header="Bukti Dukung (Eviden)" :style="{ minWidth: '220px' }">
          <template #body="{ data }">
            <div class="evidence-cell">
              <!-- Link URL eksternal (Bisa satu atau lebih) -->
              <template v-if="parseEvidenceList(data.realisasi?.bukti_link, data.realisasi?.bukti_nama).length">
                <div
                  v-for="(ev, evIdx) in parseEvidenceList(data.realisasi?.bukti_link, data.realisasi?.bukti_nama)"
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

              <!-- Berkas Upload Legacy (jika data lama pernah diunggah berkas) -->
              <div v-else-if="data.realisasi?.bukti_nama && data.realisasi?.bukti_berkas_id" class="evidence-item">
                <a
                  :href="getEvidenceDownloadUrl(data, data.realisasi.bukti_berkas_id)"
                  target="_blank"
                  class="evidence-download-link"
                  title="Klik untuk mengunduh berkas bukti dukung"
                >
                  <i class="pi pi-paperclip text-slate-500" />
                  <span class="evidence-name">{{ data.realisasi.bukti_nama }}</span>
                  <i class="pi pi-download text-xs text-slate-400 ml-1" />
                </a>
              </div>

              <!-- Fallback jika belum ada bukti -->
              <div
                v-else
                class="no-evidence-tag"
              >
                <i class="pi pi-link mr-1 text-slate-300" />
                <span>Belum ada tautan</span>
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

          <!-- Tanggal Realisasi (Dari Tanggal s.d. Sampai Tanggal) -->
          <div class="form-group">
            <label class="form-label" :class="{ required: form.status_realisasi === 'selesai' }">
              Tanggal Pelaksanaan Realisasi
            </label>
            <div class="date-range-grid">
              <div class="date-col">
                <label for="tanggal_mulai" class="date-sublabel">
                  Dari Tanggal <span v-if="form.status_realisasi === 'selesai'" class="text-rose-500">*</span>
                </label>
                <DatePicker
                  id="tanggal_mulai"
                  v-model="form.tanggal_mulai"
                  dateFormat="dd-mm-yy"
                  showIcon
                  showButtonBar
                  placeholder="Pilih tanggal mulai"
                  :maxDate="form.tanggal_selesai || undefined"
                  class="w-full"
                />
              </div>
              <div class="date-col">
                <label for="tanggal_selesai" class="date-sublabel">
                  Sampai Tanggal
                </label>
                <DatePicker
                  id="tanggal_selesai"
                  v-model="form.tanggal_selesai"
                  dateFormat="dd-mm-yy"
                  showIcon
                  showButtonBar
                  placeholder="Pilih tanggal selesai"
                  :minDate="form.tanggal_mulai || undefined"
                  class="w-full"
                />
              </div>
            </div>
            <small class="form-hint">
              Pilih rentang tanggal pelaksanaan realisasi tindak pengendalian (dari tanggal mulai s.d. tanggal selesai). Jika pelaksanaan dilakukan satu hari, cukup tentukan Tanggal Mulai atau samakan kedua tanggal.
            </small>
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

          <!-- Berkas Bukti Dukung (Paling Bawah Form, Bisa Lebih dari Satu) -->
          <div class="form-group">
            <div class="form-label-row">
              <label class="form-label mb-0 required">
                Berkas Bukti Dukung (Eviden Fisik / Digital)
              </label>
              <span class="label-badge-optional">Google Drive / OneDrive / Dropbox / Cloud Storage</span>
            </div>
            <small class="form-hint" style="margin-top: 0; margin-bottom: 0.65rem;">
              Masukkan nama berkas dan tautan link bukti dukung. Anda dapat menambahkan lebih dari satu berkas.
            </small>

            <div class="evidence-list-wrap">
              <div
                v-for="(b, idx) in form.bukti_list"
                :key="idx"
                class="evidence-row-card"
              >
                <div class="evidence-row-header">
                  <span class="evidence-row-num">#{{ idx + 1 }}</span>
                  <span class="evidence-row-title">Berkas Bukti Dukung {{ idx + 1 }}</span>
                  <Button
                    v-if="form.bukti_list.length > 1"
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
                      :placeholder="`Contoh: SK Pengendalian / SOP Pemeliharaan / Foto Kegiatan ${idx + 1}`"
                      class="form-input-text-sub"
                    />
                  </div>

                  <div class="field-item">
                    <label class="field-sublabel">Tautan / Link Dokumen Bukti Dukung <span class="text-rose-500">*</span></label>
                    <div class="input-with-icon">
                      <i class="pi pi-link input-icon" />
                      <InputText
                        v-model="b.link"
                        placeholder="https://drive.google.com/... atau link cloud storage"
                        class="form-input-text"
                        required
                      />
                      <Button
                        v-if="b.link"
                        icon="pi pi-external-link"
                        severity="secondary"
                        text
                        size="small"
                        class="btn-test-link"
                        v-tooltip.top="'Uji / Buka Tautan'"
                        @click="window.open(b.link.startsWith('http') ? b.link : 'https://' + b.link, '_blank')"
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

/* File Upload Components & Evidence Styles */
.form-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.45rem;
}

.label-badge-format {
  font-size: 0.72rem;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.label-badge-optional {
  font-size: 0.72rem;
  font-weight: 500;
  color: #0284c7;
  background: #f0f9ff;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.upload-dropzone {
  border: 2px dashed #cbd5e1;
  border-radius: 0.75rem;
  padding: 1.5rem 1rem;
  text-align: center;
  cursor: pointer;
  background: #f8fafc;
  transition: all 0.2s ease-in-out;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
}

.upload-dropzone:hover,
.upload-dropzone.is-dragging {
  border-color: #059669;
  background: #f0fdf4;
}

.upload-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  color: #059669;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s;
}

.upload-dropzone:hover .upload-icon-circle {
  transform: translateY(-2px);
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.upload-title {
  font-size: 0.875rem;
  color: #1e293b;
  font-weight: 600;
}

.upload-subtitle {
  font-size: 0.75rem;
  color: #64748b;
}

.upload-btn-trigger {
  margin-top: 0.25rem;
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.85rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #334155;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.upload-dropzone:hover .upload-btn-trigger {
  border-color: #a7f3d0;
  color: #065f46;
}

/* Evidence File Card */
.evidence-file-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
  border: 1px solid #e2e8f0;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.evidence-file-card.stored-card {
  background: #ffffff;
  border-color: #e2e8f0;
}

.evidence-file-card.new-card {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.file-card-content {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex: 1;
  min-width: 0;
}

.file-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
  flex: 1;
}

.file-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.file-title {
  font-size: 0.875rem;
  font-weight: 650;
  color: #0f172a;
  word-break: break-all;
}

.badge-status-file {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.badge-stored {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.badge-new {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.file-meta-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  font-size: 0.75rem;
  color: #64748b;
}

.file-view-link {
  color: #0284c7;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}

.file-view-link:hover {
  text-decoration: underline;
  color: #0369a1;
}

.file-card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-file-action {
  font-size: 0.78rem !important;
  padding: 0.35rem 0.75rem !important;
}

.btn-file-delete {
  font-size: 0.78rem !important;
  width: 32px !important;
  height: 32px !important;
  padding: 0 !important;
}

/* Evidence List & Multi Evidence Styles */
.evidence-list-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
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

.add-evidence-action {
  display: flex;
  justify-content: flex-start;
  margin-top: 0.25rem;
}

.btn-add-evidence {
  font-size: 0.8rem !important;
}

@media (max-width: 640px) {
  .evidence-fields-grid {
    grid-template-columns: 1fr;
  }
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

.form-textarea {
  width: 100%;
  font-size: 0.875rem;
  border-radius: 0.5rem;
}

.btn-ai-draft {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
}

.date-range-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.date-col {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.date-sublabel {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

@media (max-width: 640px) {
  .date-range-grid {
    grid-template-columns: 1fr;
  }
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
