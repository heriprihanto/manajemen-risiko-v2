<script setup>
import { computed, onMounted, ref } from 'vue'
import { onAuthStateChanged } from 'firebase/auth'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { auth, signInWithGoogle, signOut } from '@/firebase'
import api from '@/api'
import AppLoader from '@/components/AppLoader.vue'
import { formatDateTime } from '@/utils/date'

const toast = useToast()

const fbUser = ref(null)
const fbToken = ref('')
const authChecking = ref(true)
const loginLoading = ref(false)
const submitting = ref(false)
const opdList = ref([])
const myReports = ref([])
const loadingReports = ref(false)

const form = ref({
  tahun: new Date().getFullYear(),
  opd_id: null,
  no_hp: '',
  nama_lengkap: '',
  waktu_kejadian: null,
  tempat: '',
  uraian_kejadian: '',
  pemicu: '',
})

function formatWaktuKejadian(val) {
  if (!val) return ''
  if (val instanceof Date) {
    const pad = (n) => String(n).padStart(2, '0')
    const yyyy = val.getFullYear()
    const mm = pad(val.getMonth() + 1)
    const dd = pad(val.getDate())
    const hh = pad(val.getHours())
    const min = pad(val.getMinutes())
    return `${yyyy}-${mm}-${dd} ${hh}:${min}`
  }
  return String(val)
}

const tahunOptions = [
  { label: '2025', value: 2025 },
  { label: '2026', value: 2026 },
  { label: '2027', value: 2027 },
]

async function loadOpdList() {
  try {
    const res = await api.get('/lapor-kejadian/opd-list')
    opdList.value = res.data || []
  } catch (err) {
    opdList.value = []
  }
}

async function loadMyReports() {
  if (!fbToken.value) return
  loadingReports.value = true
  try {
    const res = await api.get('/lapor-kejadian/my', {
      headers: { Authorization: `Bearer ${fbToken.value}` },
    })
    myReports.value = res.data || []
  } catch (err) {
    myReports.value = []
  } finally {
    loadingReports.value = false
  }
}

onMounted(() => {
  loadOpdList()

  // Pantau state login Firebase
  onAuthStateChanged(auth, async (user) => {
    fbUser.value = user
    if (user) {
      try {
        fbToken.value = await user.getIdToken()
        if (!form.value.nama_lengkap) {
          form.value.nama_lengkap = user.displayName || ''
        }
        await loadMyReports()
      } catch (e) {
        fbToken.value = ''
      }
    } else {
      fbToken.value = ''
      myReports.value = []
    }
    authChecking.value = false
  })
})

async function handleLogin() {
  loginLoading.value = true
  try {
    const res = await signInWithGoogle()
    fbUser.value = res.user
    fbToken.value = await res.user.getIdToken()
    form.value.nama_lengkap = res.user.displayName || ''
    toast.add({
      severity: 'success',
      summary: 'Login Berhasil',
      detail: `Selamat datang, ${res.user.displayName || res.user.email}`,
      life: 3000,
    })
    await loadMyReports()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Login',
      detail: err.message || 'Tidak dapat menyelesaikan login Firebase',
      life: 4000,
    })
  } finally {
    loginLoading.value = false
  }
}

async function handleLogout() {
  try {
    await signOut()
    fbUser.value = null
    fbToken.value = ''
    myReports.value = []
    toast.add({
      severity: 'info',
      summary: 'Logout Berhasil',
      detail: 'Sesi telah ditutup',
      life: 3000,
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Gagal logout',
      life: 3000,
    })
  }
}

async function handleSubmit() {
  // Validasi form
  if (!form.value.tahun) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Tahun anggaran wajib diisi', life: 3000 })
    return
  }
  if (!form.value.opd_id) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Pilih Organisasi Perangkat Daerah', life: 3000 })
    return
  }
  if (!form.value.nama_lengkap.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama lengkap pelapor wajib diisi', life: 3000 })
    return
  }
  if (!form.value.no_hp.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nomor HP pelapor wajib diisi', life: 3000 })
    return
  }
  if (!form.value.waktu_kejadian) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Waktu kejadian wajib dipilih', life: 3000 })
    return
  }
  if (!form.value.tempat.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Tempat kejadian wajib diisi', life: 3000 })
    return
  }
  if (!form.value.uraian_kejadian.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Uraian kejadian wajib diisi', life: 3000 })
    return
  }
  if (!form.value.pemicu.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Pemicu kejadian wajib diisi', life: 3000 })
    return
  }

  submitting.value = true
  try {
    // Refresh token jika perlu
    if (fbUser.value) {
      fbToken.value = await fbUser.value.getIdToken(true)
    }

    const payload = {
      tahun: Number(form.value.tahun),
      opd_id: Number(form.value.opd_id),
      no_hp: form.value.no_hp.trim(),
      nama_lengkap: form.value.nama_lengkap.trim(),
      waktu_kejadian: formatWaktuKejadian(form.value.waktu_kejadian),
      tempat: form.value.tempat.trim(),
      uraian_kejadian: form.value.uraian_kejadian.trim(),
      pemicu: form.value.pemicu.trim(),
    }

    const res = await api.post('/lapor-kejadian', payload, {
      headers: { Authorization: `Bearer ${fbToken.value}` },
    })

    toast.add({
      severity: 'success',
      summary: 'Laporan Terkirim',
      detail: 'Laporan kejadian berhasil disimpan dan akan divalidasi oleh pengelola risiko.',
      life: 5000,
    })

    // Reset form bagian kejadian
    form.value.uraian_kejadian = ''
    form.value.pemicu = ''
    form.value.tempat = ''
    form.value.waktu_kejadian = null

    await loadMyReports()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: err.response?.data?.detail || 'Terjadi kesalahan saat menyimpan laporan kejadian',
      life: 4000,
    })
  } finally {
    submitting.value = false
  }
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
</script>

<template>
  <div class="lapor-container">
    <AppLoader v-if="authChecking" label="Memeriksa autentikasi Firebase…" />

    <!-- 1. Belum Login: Tampilkan Halaman Pendaratan & Login Google -->
    <div v-else-if="!fbUser" class="auth-gate-card">
      <div class="hero-brand">
        <div class="brand-icon-wrap">
          <i class="pi pi-shield" />
        </div>
        <Tag value="LAYANAN PUBLIK OPD" severity="info" class="badge-tag" />
        <h1 class="hero-title">Lapor Kejadian Risiko</h1>
        <p class="hero-desc">
          Saluran pelaporan resmi bagi seluruh pegawai di lingkungan Pemerintah Kota Tegal untuk mencatat potensi insiden,
          hambatan pelaksanaan tugas, dan kejadian risiko secara cepat, akurat, dan terverifikasi.
        </p>
      </div>

      <div class="auth-box">
        <p class="auth-box-msg">
          Silakan masuk menggunakan akun Google Anda untuk memulai pelaporan kejadian risiko:
        </p>

        <Button
          label="Masuk dengan Google Akun"
          icon="pi pi-google"
          size="large"
          class="btn-google-login"
          :loading="loginLoading"
          @click="handleLogin"
        />

        <div class="auth-guarantee">
          <i class="pi pi-lock lock-icon" />
          <span>Autentikasi aman melalui Google Akun</span>
        </div>
      </div>

      <div class="features-preview">
        <div class="feat-card">
          <i class="pi pi-send feat-icon" />
          <h3>Pelaporan Cepat</h3>
          <p>Catat kronologi kejadian, waktu, tempat, dan pemicu risiko langsung dari perangkat Anda.</p>
        </div>
        <div class="feat-card">
          <i class="pi pi-check-circle feat-icon" />
          <h3>Approval Pengelola</h3>
          <p>Laporan langsung masuk ke dashboard Approval Kejadian untuk divalidasi oleh tim Manajemen Risiko OPD.</p>
        </div>
        <div class="feat-card">
          <i class="pi pi-history feat-icon" />
          <h3>Pantau Status</h3>
          <p>Lihat perkembangan validasi laporan Anda secara transparan kapan saja.</p>
        </div>
      </div>
    </div>

    <!-- 2. Sudah Login: Formulir Lapor Kejadian & Riwayat Laporan -->
    <div v-else class="lapor-main">
      <!-- User Profile Header Bar -->
      <div class="user-bar">
        <div class="user-meta">
          <div class="user-avatar">
            <img v-if="fbUser.photoURL" :src="fbUser.photoURL" alt="Profile" />
            <i v-else class="pi pi-user" />
          </div>
          <div>
            <div class="user-name">{{ fbUser.displayName || 'Pegawai OPD' }}</div>
            <div class="user-email">{{ fbUser.email }}</div>
          </div>
        </div>
        <div class="user-actions">
          <Button
            label="Logout"
            icon="pi pi-sign-out"
            severity="secondary"
            outlined
            size="small"
            class="btn-logout"
            @click="handleLogout"
          />
        </div>
      </div>

      <div class="main-form-card">
        <div class="form-header">
          <div class="form-header-left">
            <div class="form-icon">
              <i class="pi pi-file-edit" />
            </div>
            <div>
              <h2 class="form-title">Formulir Lapor Kejadian</h2>
              <p class="form-subtitle">
                Isi data rincian kejadian risiko dengan lengkap dan jelas. Semua laporan akan masuk ke menu Approval Kejadian.
              </p>
            </div>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="form-body">
          <div class="form-grid">
            <!-- Tahun -->
            <div class="field-item">
              <label for="tahun" class="field-label">Tahun Anggaran <span class="req">*</span></label>
              <Select
                id="tahun"
                v-model="form.tahun"
                :options="tahunOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Pilih Tahun"
                class="w-full"
              />
            </div>

            <!-- Organisasi Perangkat Daerah -->
            <div class="field-item">
              <label for="opd" class="field-label">Organisasi Perangkat Daerah (OPD) <span class="req">*</span></label>
              <Select
                id="opd"
                v-model="form.opd_id"
                :options="opdList"
                optionLabel="nama"
                optionValue="id"
                filter
                placeholder="Pilih OPD Tempat Kejadian"
                class="w-full"
              />
            </div>

            <!-- Nama Lengkap -->
            <div class="field-item">
              <label for="nama_lengkap" class="field-label">Nama Lengkap Pelapor <span class="req">*</span></label>
              <InputText
                id="nama_lengkap"
                v-model="form.nama_lengkap"
                placeholder="Masukkan nama lengkap Anda"
                class="w-full"
              />
            </div>

            <!-- No. HP -->
            <div class="field-item">
              <label for="no_hp" class="field-label">No. HP / WhatsApp <span class="req">*</span></label>
              <InputText
                id="no_hp"
                v-model="form.no_hp"
                placeholder="Contoh: 081234567890"
                class="w-full"
              />
            </div>

            <!-- Waktu Kejadian -->
            <div class="field-item">
              <label for="waktu_kejadian" class="field-label">Waktu Kejadian <span class="req">*</span></label>
              <DatePicker
                id="waktu_kejadian"
                v-model="form.waktu_kejadian"
                dateFormat="dd-mm-yy"
                showTime
                hourFormat="24"
                showIcon
                showButtonBar
                fluid
                placeholder="Pilih tanggal & waktu kejadian"
              />
            </div>

            <!-- Tempat -->
            <div class="field-item">
              <label for="tempat" class="field-label">Tempat Kejadian <span class="req">*</span></label>
              <InputText
                id="tempat"
                v-model="form.tempat"
                placeholder="Contoh: Ruang Pelayanan / Lab / Lokasi Proyek"
                class="w-full"
              />
            </div>

            <!-- Uraian Kejadian -->
            <div class="field-item full-width">
              <label for="uraian" class="field-label">Uraian Kejadian <span class="req">*</span></label>
              <Textarea
                id="uraian"
                v-model="form.uraian_kejadian"
                rows="4"
                placeholder="Jelaskan secara kronologis kejadian risiko yang terjadi, kendala, atau dampak kerugian yang ditimbulkan..."
                class="w-full"
              />
            </div>

            <!-- Pemicu -->
            <div class="field-item full-width">
              <label for="pemicu" class="field-label">Pemicu Kejadian <span class="req">*</span></label>
              <Textarea
                id="pemicu"
                v-model="form.pemicu"
                rows="3"
                placeholder="Jelaskan faktor pemicu atau penyebab terjadinya kejadian risiko tersebut (misal: cuaca ekstrem, sistem server down, kelalaian prosedur, dll.)..."
                class="w-full"
              />
            </div>
          </div>

          <!-- Tombol Aksi Sesuai Perintah: Button Simpan & Logout -->
          <div class="form-actions">
            <Button
              label="Simpan Laporan Kejadian"
              icon="pi pi-check"
              size="large"
              type="submit"
              class="btn-submit"
              :loading="submitting"
            />
            <Button
              label="Logout"
              icon="pi pi-sign-out"
              severity="secondary"
              outlined
              size="large"
              class="btn-logout-bottom"
              @click="handleLogout"
            />
          </div>
        </form>
      </div>

      <!-- Riwayat Laporan Pengguna -->
      <div class="my-reports-card">
        <div class="reports-header">
          <span class="reports-title">
            <i class="pi pi-history card-icon" /> Riwayat Laporan Saya
          </span>
          <Button
            icon="pi pi-refresh"
            size="small"
            text
            severity="secondary"
            v-tooltip="'Segarkan Riwayat'"
            @click="loadMyReports"
          />
        </div>

        <div v-if="loadingReports" class="loading-state">
          <i class="pi pi-spin pi-spinner" /> Memuat riwayat laporan…
        </div>

        <div v-else-if="!myReports.length" class="empty-reports">
          <i class="pi pi-inbox empty-icon" />
          <p>Belum ada laporan kejadian yang Anda kirimkan.</p>
        </div>

        <div v-else class="reports-list">
          <div v-for="item in myReports" :key="item.id" class="report-box">
            <div class="report-top">
              <div class="report-opd-badge">
                <i class="pi pi-building" /> {{ item.nama_opd }} (Tahun {{ item.tahun }})
              </div>
              <Tag :value="statusLabel(item.status)" :severity="statusSeverity(item.status)" />
            </div>

            <div class="report-meta-grid">
              <div>
                <strong>Waktu:</strong> {{ item.waktu_kejadian }}
              </div>
              <div>
                <strong>Tempat:</strong> {{ item.tempat }}
              </div>
              <div>
                <strong>Dilaporkan:</strong> {{ formatDateTime(item.created_at) }}
              </div>
            </div>

            <div class="report-content-body">
              <div class="content-row">
                <span class="content-lbl">Uraian Kejadian:</span>
                <p class="content-val">{{ item.uraian_kejadian }}</p>
              </div>
              <div class="content-row">
                <span class="content-lbl">Pemicu:</span>
                <p class="content-val">{{ item.pemicu }}</p>
              </div>
            </div>

            <div v-if="item.catatan_validasi" class="report-feedback">
              <i class="pi pi-comment feedback-icon" />
              <div>
                <strong>Catatan Validasi Pengelola:</strong>
                <p>{{ item.catatan_validasi }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lapor-container {
  min-height: 100vh;
  padding: 2rem 1.5rem;
  max-width: 1040px;
  margin: 0 auto;
}

/* Auth Gate (Belum Login) */
.auth-gate-card {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  padding: 3rem 2rem;
  text-align: center;
}

.hero-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 680px;
  margin: 0 auto 2.5rem;
}

.brand-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 2.2rem;
  margin-bottom: 1rem;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.badge-tag {
  font-weight: 700;
  margin-bottom: 0.75rem;
  letter-spacing: 0.05em;
}

.hero-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.75rem;
  letter-spacing: -0.02em;
}

.hero-desc {
  font-size: 1.05rem;
  color: #475569;
  line-height: 1.6;
  margin: 0;
}

.auth-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 2rem;
  max-width: 520px;
  margin: 0 auto 3rem;
}

.auth-box-msg {
  color: #334155;
  font-size: 0.95rem;
  margin: 0 0 1.25rem;
}

.btn-google-login {
  width: 100%;
  font-weight: 700 !important;
  background: #2563eb !important;
  border: none !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
  transition: transform 0.15s ease;
}
.btn-google-login:hover {
  transform: translateY(-2px);
}

.auth-guarantee {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  margin-top: 1rem;
  font-size: 0.8rem;
  color: #64748b;
}

.lock-icon {
  color: #10b981;
}

.features-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
  text-align: left;
}

.feat-card {
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.feat-icon {
  font-size: 1.75rem;
  color: #2563eb;
  margin-bottom: 0.75rem;
}

.feat-card h3 {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
  color: #1e293b;
}

.feat-card p {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.45;
}

/* Main Form (Sudah Login) */
.user-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  background: #ffffff;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #64748b;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 1rem;
}

.user-email {
  font-size: 0.825rem;
  color: #64748b;
}

.main-form-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.25rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.form-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.form-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.form-title {
  margin: 0 0 0.25rem;
  font-size: 1.35rem;
  font-weight: 700;
  color: #1e293b;
}

.form-subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-item.full-width {
  grid-column: 1 / -1;
}

.field-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #334155;
}

.req {
  color: #ef4444;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
}

.btn-submit {
  padding: 0.75rem 2rem !important;
  font-weight: 700 !important;
  background: #2563eb !important;
  border: none !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.my-reports-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 1.75rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.reports-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.reports-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.report-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.15s ease;
}

.report-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.report-opd-badge {
  font-weight: 700;
  color: #1e3a8a;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.report-meta-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  font-size: 0.8rem;
  color: #475569;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed #cbd5e1;
}

.content-row {
  margin-bottom: 0.4rem;
}

.content-lbl {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  display: block;
}

.content-val {
  margin: 0.15rem 0 0;
  font-size: 0.875rem;
  color: #1e293b;
  line-height: 1.45;
}

.report-feedback {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background: #ecfdf5;
  border-left: 4px solid #10b981;
  border-radius: 6px;
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.825rem;
  color: #065f46;
}

.feedback-icon {
  font-size: 1.1rem;
  margin-top: 2px;
}

.empty-reports {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}
</style>
