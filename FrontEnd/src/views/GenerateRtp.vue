<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const toast = useToast()

const loading = ref(false)
const generating = ref(false)
const opdInfo = ref(null)

const includeMainDoc = ref(true)

const sections = [
  { key: 'f1a', form: 'Form 1.a', label: 'Rekap Kuesioner CEE (Persepsi)', desc: 'Hasil survei persepsi responden terhadap 8 sub-unsur CEE' },
  { key: 'f1b', form: 'Form 1.b', label: 'Reviu Dokumen CEE', desc: 'Analisis kondisi kerentanan berdasarkan reviu dokumen' },
  { key: 'f1c', form: 'Form 1.c', label: 'Simpulan CEE', desc: 'Simpulan gabungan survei persepsi dan reviu dokumen' },
  { key: 'f6', form: 'Form 6', label: 'RTP atas CEE', desc: 'Rencana tindak pengendalian atas kelemahan lingkungan pengendalian' },
  { key: 'f2a', form: 'Form 2.a', label: 'Konteks Strategis Pemda', desc: 'Visi, misi, sasaran, dan prioritas pembangunan Kota Tegal' },
  { key: 'f2b', form: 'Form 2.b', label: 'Konteks Strategis OPD', desc: 'Tujuan, sasaran, IKU, dan program strategis perangkat daerah' },
  { key: 'f2c', form: 'Form 2.c', label: 'Konteks Operasional OPD', desc: 'Pemetaan subkegiatan dan indikator operasional Renja' },
  { key: 'f3a', form: 'Form 3.a', label: 'Identifikasi Risiko Strategis Pemda', desc: 'Daftar risiko strategis Pemerintah Kota Tegal' },
  { key: 'f3b', form: 'Form 3.b', label: 'Identifikasi Risiko Strategis OPD', desc: 'Identifikasi risiko strategis perangkat daerah' },
  { key: 'f3c', form: 'Form 3.c', label: 'Identifikasi Risiko Operasional OPD', desc: 'Identifikasi risiko kegiatan dan subkegiatan operasional' },
  { key: 'f4', form: 'Form 4', label: 'Analisis Risiko', desc: 'Penilaian kemungkinan, dampak, skala, dan level risiko 5x5' },
  { key: 'f5', form: 'Form 5', label: 'Daftar Risiko Prioritas', desc: 'Risiko-risiko prioritas yang wajib ditangani dalam RTP' },
  { key: 'f7', form: 'Form 7', label: 'RTP atas Risiko', desc: 'Rencana tindak mitigasi dan pengendalian risiko prioritas' },
  { key: 'f8', form: 'Form 8', label: 'Informasi & Komunikasi', desc: 'Rencana sarana dan media pengkomunikasian pengendalian' },
  { key: 'f9', form: 'Form 9', label: 'Rencana Pemantauan PI', desc: 'Metode dan penanggung jawab pemantauan pengendalian intern' },
  { key: 'f10', form: 'Form 10', label: 'Monitoring Event & RTP', desc: 'Pencatatan kejadian risiko nyata dan pelaksanaan mitigasi' },
]

const selectedForms = ref(sections.map((s) => s.key))

const allSelected = computed({
  get: () => selectedForms.value.length === sections.length,
  set: (val) => {
    selectedForms.value = val ? sections.map((s) => s.key) : []
  },
})

const opdName = computed(() => opdInfo.value?.nama_pd || ctx.opd?.nama_pd || '-')

async function fetchOpdInfo() {
  if (!ctx.opdId) return
  loading.value = true
  try {
    const res = await api.get('/master/opd-print-context', {
      params: { opd_id: ctx.opdId },
    })
    opdInfo.value = res.data || {}
  } catch (err) {
    opdInfo.value = {}
  } finally {
    loading.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun], fetchOpdInfo)
onMounted(fetchOpdInfo)

async function generateDocx() {
  if (!ctx.opdId) {
    toast.add({ severity: 'warn', summary: 'Pilih OPD', detail: 'Silakan pilih OPD terlebih dahulu', life: 3000 })
    return
  }
  if (!includeMainDoc.value && !selectedForms.value.length) {
    toast.add({
      severity: 'warn',
      summary: 'Tidak Ada Konten',
      detail: 'Pilih minimal satu bagian atau sertakan Dokumen Utama',
      life: 3000,
    })
    return
  }

  generating.value = true
  try {
    const response = await api.get('/laporan/rtp-docx', {
      params: {
        opd_id: ctx.opdId,
        tahun: ctx.tahun,
        forms: selectedForms.value.join(','),
        include_main: includeMainDoc.value,
      },
      responseType: 'blob',
    })

    const cleanOpd = opdName.value.replace(/[^a-zA-Z0-9_-]/g, '_')
    const fileName = `Dokumen_RTP_${cleanOpd}_${ctx.tahun}.docx`

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    toast.add({
      severity: 'success',
      summary: 'Berhasil Generate RTP',
      detail: `File Word ${fileName} berhasil diunduh.`,
      life: 4000,
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Generate',
      detail: 'Terjadi kesalahan saat menyusun dokumen RTP. Periksa koneksi backend.',
      life: 5000,
    })
  } finally {
    generating.value = false
  }
}
</script>

<template>
  <div class="generate-rtp-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-file-word" />
        </div>
        <div>
          <h1 class="page-title">Generate Dokumen RTP</h1>
          <p class="page-desc">
            Penyusunan Rencana Tindak Pengendalian (RTP) format Word (.docx) berbasis template resmi dengan seluruh lampiran
          </p>
        </div>
      </div>
      <div class="header-actions">
        <Button
          label="Generate Dokumen Word (.docx)"
          icon="pi pi-download"
          severity="primary"
          :loading="generating"
          :disabled="loading || (!includeMainDoc && !selectedForms.length)"
          @click="generateDocx"
        />
      </div>
    </div>


    <AppLoader v-if="loading" label="Memuat profil dan konteks dokumen…" />

    <div v-else class="content-grid">
      <!-- Panel Kiri: Profil & Konteks Dokumen -->
      <div class="panel-left">
        <div class="card meta-card">
          <div class="card-header">
            <span class="card-title">
              <i class="pi pi-id-card card-icon" /> Identitas & Penandatangan Dokumen
            </span>
            <Tag :value="`Tahun ${ctx.tahun}`" severity="info" class="year-tag" />
          </div>

          <div class="meta-list">
            <div class="meta-row">
              <span class="meta-label">Organisasi Perangkat Daerah</span>
              <span class="meta-value highlight">{{ opdName }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Kepala OPD</span>
              <span class="meta-value">{{ opdInfo?.nama_kepala || '-' }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">NIP</span>
              <span class="meta-value">{{ opdInfo?.nip_kepala || '-' }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Jabatan Penandatangan</span>
              <span class="meta-value">{{ opdInfo?.jabatan_kepala || `Kepala ${opdName}` }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Bidang Urusan</span>
              <span class="meta-value text-small">{{ opdInfo?.bidang_urusan || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- Panel Struktur Dokumen Utama -->
        <div class="card structure-card">
          <div class="card-header">
            <span class="card-title">
              <i class="pi pi-book card-icon" /> Dokumen Utama RTP (Word Template)
            </span>
            <Checkbox v-model="includeMainDoc" binary inputId="mainDocToggle" />
          </div>

          <p class="section-desc">
            Menggunakan template baku Pemerintah Kota Tegal (docxtpl) dengan logo Pemkot, tipografi resmi Times New Roman,
            dan pembagian bab naratif:
          </p>

          <div class="chapters-timeline">
            <div class="chap-item">
              <div class="chap-badge">Cover</div>
              <div class="chap-content">
                <strong>Cover & Identitas Dokumen</strong>
                <span>Lambang Pemkot Tegal, nama OPD, dan tahun anggaran</span>
              </div>
            </div>
            <div class="chap-item">
              <div class="chap-badge">I</div>
              <div class="chap-content">
                <strong>BAB I — Pendahuluan</strong>
                <span>Latar belakang, tupoksi organisasi, dasar hukum, maksud, tujuan & manfaat</span>
              </div>
            </div>
            <div class="chap-item">
              <div class="chap-badge">II</div>
              <div class="chap-content">
                <strong>BAB II — Lingkungan Pengendalian</strong>
                <span>Penciptaan lingkungan pengendalian (CEE) 8 sub-unsur</span>
              </div>
            </div>
            <div class="chap-item">
              <div class="chap-badge">III</div>
              <div class="chap-content">
                <strong>BAB III — Penilaian & Pengendalian Risiko</strong>
                <span>Penerapan SPIP, identifikasi risiko, hasil analisis, mitigasi</span>
              </div>
            </div>
            <div class="chap-item">
              <div class="chap-badge">IV</div>
              <div class="chap-content">
                <strong>BAB IV — Informasi, Komunikasi & Pemantauan</strong>
                <span>Sarana komunikasi, media penyampaian, dan rencana monitoring PI</span>
              </div>
            </div>
            <div class="chap-item">
              <div class="chap-badge">V</div>
              <div class="chap-content">
                <strong>BAB V — Penutup</strong>
                <span>Kesimpulan dan lembar pengesahan tanda tangan Kepala OPD</span>
              </div>
            </div>
            <div class="chap-item">
              <div class="chap-badge">KK</div>
              <div class="chap-content">
                <strong>Kertas Kerja RTP</strong>
                <span>Halaman pembuka kertas kerja & rincian identitas OPD</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel Kanan: Pilihan Lampiran Kertas Kerja (Form 1.a - Form 10) -->
      <div class="panel-right">
        <div class="card attachments-card">
          <div class="card-header">
            <div>
              <span class="card-title">
                <i class="pi pi-paperclip card-icon" /> Lampiran Kertas Kerja (Printout Form)
              </span>
              <p class="card-subtitle">
                Tiap form disusun dengan tabel lengkap, cell shading, batas kolom terstruktur, dan tanda tangan resmi.
              </p>
            </div>
            <div class="selection-control">
              <Checkbox v-model="allSelected" binary inputId="selectAllForms" />
              <label for="selectAllForms" class="label-select-all">
                {{ allSelected ? 'Hapus Semua' : 'Pilih Semua' }}
              </label>
            </div>
          </div>

          <div class="forms-grid">
            <div
              v-for="s in sections"
              :key="s.key"
              class="form-item-box"
              :class="{ active: selectedForms.includes(s.key) }"
              @click="
                selectedForms.includes(s.key)
                  ? selectedForms = selectedForms.filter((x) => x !== s.key)
                  : selectedForms.push(s.key)
              "
            >
              <div class="item-check">
                <Checkbox
                  :modelValue="selectedForms.includes(s.key)"
                  binary
                  @click.stop
                  @change="
                    selectedForms.includes(s.key)
                      ? selectedForms = selectedForms.filter((x) => x !== s.key)
                      : selectedForms.push(s.key)
                  "
                />
              </div>
              <div class="item-info">
                <div class="item-top">
                  <span class="item-code">{{ s.form }}</span>
                  <span class="item-title">{{ s.label }}</span>
                </div>
                <p class="item-desc">{{ s.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Card -->
        <div class="card summary-action-card">
          <div class="summary-details">
            <div class="stat-box">
              <span class="stat-num">{{ includeMainDoc ? '1 Dokumen' : '0' }}</span>
              <span class="stat-lbl">Dokumen Narasi Utama</span>
            </div>
            <div class="stat-divider" />
            <div class="stat-box">
              <span class="stat-num">{{ selectedForms.length }} / {{ sections.length }}</span>
              <span class="stat-lbl">Form Lampiran Terpilih</span>
            </div>
            <div class="stat-divider" />
            <div class="stat-box">
              <span class="stat-num">.DOCX</span>
              <span class="stat-lbl">Format Microsoft Word</span>
            </div>
          </div>

          <div class="action-btn-row">
            <Button
              label="Generate & Unduh Dokumen RTP (.docx)"
              icon="pi pi-download"
              class="btn-download-big"
              :loading="generating"
              :disabled="loading || (!includeMainDoc && !selectedForms.length)"
              @click="generateDocx"
            />
          </div>

          <div v-if="generating" class="generating-progress">
            <ProgressBar mode="indeterminate" style="height: 6px" />
            <span class="progress-txt">Sedang menyusun dan merender dokumen Word via docxtpl…</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.generate-rtp-page {
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
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
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


.btn-generate-main {
  background: #ffffff !important;
  color: #1e3a8a !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}
.btn-generate-main:hover {
  background: #f1f5f9 !important;
  transform: translateY(-1px);
}

.content-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 1080px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

.card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-icon {
  color: #2563eb;
}

.card-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.825rem;
  color: #64748b;
}

.meta-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.meta-row {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.meta-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
}

.meta-value {
  font-size: 0.95rem;
  color: #1e293b;
  font-weight: 500;
}

.meta-value.highlight {
  font-weight: 700;
  color: #1e3a8a;
  font-size: 1.05rem;
}

.text-small {
  font-size: 0.85rem;
  line-height: 1.4;
}

.year-tag {
  font-weight: 600;
}

.section-desc {
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.45;
}

.chapters-timeline {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chap-item {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
}

.chap-badge {
  background: #e0e7ff;
  color: #3730a3;
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  min-width: 44px;
  text-align: center;
}

.chap-content {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.chap-content strong {
  font-size: 0.875rem;
  color: #1e293b;
}

.chap-content span {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.35;
}

.selection-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.label-select-all {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
}

.forms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.85rem;
}

.form-item-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.form-item-box:hover {
  border-color: #93c5fd;
  background: #f0f7ff;
}

.form-item-box.active {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 1px #3b82f6;
}

.item-check {
  margin-top: 2px;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.item-top {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.item-code {
  font-size: 0.75rem;
  font-weight: 700;
  color: #1d4ed8;
  background: #dbeafe;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
}

.item-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
}

.item-desc {
  margin: 0;
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.3;
}

.summary-action-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.summary-details {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-num {
  font-size: 1.35rem;
  font-weight: 800;
  color: #1e3a8a;
}

.stat-lbl {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #cbd5e1;
}

.action-btn-row {
  display: flex;
  justify-content: center;
}

.btn-download-big {
  width: 100%;
  max-width: 480px;
  padding: 0.85rem 1.75rem !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  background: #2563eb !important;
  border: none !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
  transition: all 0.2s ease;
}

.btn-download-big:hover {
  background: #1d4ed8 !important;
  transform: translateY(-1px);
}

.generating-progress {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: center;
}

.progress-txt {
  font-size: 0.825rem;
  color: #2563eb;
  font-weight: 600;
}
</style>
