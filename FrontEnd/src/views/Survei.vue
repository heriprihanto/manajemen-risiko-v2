<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { validAnswers } from '@/utils/surveyDraft'
import AppLoader from '@/components/AppLoader.vue'
import { formatDate, formatDateTime } from '@/utils/date'

const toast = useToast()
const sessionKey = `${import.meta.env.BASE_URL}cee-survei-token`

function storedToken() {
  try { return sessionStorage.getItem(sessionKey) || '' } catch { return '' }
}
function storeToken(token) {
  try {
    if (token) sessionStorage.setItem(sessionKey, token)
    else sessionStorage.removeItem(sessionKey)
  } catch {
    // Survei tetap bisa digunakan jika penyimpanan browser dibatasi.
  }
}

const user = ref(null)
const authReady = ref(false)
const tokenInput = ref('')
const verifiedToken = ref('')
const checking = ref(false)
const loadError = ref('')
const info = ref(null)
const opdList = ref([])
const kuesioner = ref([])

const opdId = ref(null)
const nama = ref('')
const jabatan = ref('')
const draftStorageKey = ref('')
const draftStorageError = ref(false)
let restoringDraft = false
const answers = ref({}) // pertanyaan_id -> nilai
const narasi = ref('') // narasi lain terkait kondisi lingkungan pengendalian
const submitting = ref(false)
const status = ref(null) // hasil /survei/status

const skala = [
  { nilai: 1, label: 'Tidak Setuju' },
  { nilai: 2, label: 'Kurang Setuju' },
  { nilai: 3, label: 'Setuju' },
  { nilai: 4, label: 'Sangat Setuju' },
]

const alreadySubmitted = computed(() => !!status.value?.submitted)
// Jadwal survei ditetapkan Admin (halaman Pengaturan); backend tetap menolak
// submit di luar rentang, ini hanya agar formulir tidak tampil percuma.
const jadwal = computed(() => info.value?.jadwal || null)
const surveiTutup = computed(() => !!jadwal.value && !jadwal.value.dibuka)
const fmtTgl = (s) => (s ? formatDate(s) : null)
const totalQuestions = computed(() =>
  kuesioner.value.reduce((n, k) => n + k.pertanyaan.length, 0),
)
const answeredCount = computed(() => Object.keys(answers.value).length)
const allAnswered = computed(
  () => totalQuestions.value > 0 && answeredCount.value === totalQuestions.value,
)
const opdOptions = computed(() =>
  opdList.value.map((o) => ({ label: o.nama_pd, value: o.id_sub_pd })),
)

function authHeader(t) {
  return { headers: { Authorization: `Bearer ${t}` } }
}

async function loadPublic() {
  const [a, b, c] = await Promise.all([
    api.get('/survei/info'),
    api.get('/survei/opd'),
    api.get('/survei/kuesioner'),
  ])
  info.value = a.data
  opdList.value = b.data
  kuesioner.value = c.data
}

function clearDraft() {
  if (!draftStorageKey.value) return
  try { localStorage.removeItem(draftStorageKey.value) } catch { draftStorageError.value = true }
}

function persistDraft() {
  if (restoringDraft || !draftStorageKey.value || !status.value || status.value.submitted) return
  try {
    localStorage.setItem(draftStorageKey.value, JSON.stringify({
      answers: answers.value,
      narasi: narasi.value,
    }))
    draftStorageError.value = false
  } catch { draftStorageError.value = true }
}

watch(answers, persistDraft, { deep: true, flush: 'sync' })
watch(narasi, persistDraft, { flush: 'sync' })

function applyStatus(data) {
  status.value = data
  user.value = { name: data.nama_responden }
  restoringDraft = true
  const questionIds = kuesioner.value.flatMap(k => k.pertanyaan.map(p => p.id))
  let restoredAnswers = {}
  let restoredNarasi = ''
  if (data.submitted) {
    clearDraft()
  } else if (draftStorageKey.value) {
    try {
      const raw = localStorage.getItem(draftStorageKey.value)
      if (raw) {
        try {
          const parsed = JSON.parse(raw)
          if (parsed && typeof parsed === 'object') {
            if ('answers' in parsed) {
              restoredAnswers = validAnswers(parsed.answers, questionIds)
              restoredNarasi = typeof parsed.narasi === 'string' ? parsed.narasi : ''
            } else {
              restoredAnswers = validAnswers(parsed, questionIds)
            }
          }
        } catch { clearDraft() }
      }
    } catch { draftStorageError.value = true }
  }
  answers.value = data.submitted ? { ...data.jawaban } : {
    ...validAnswers(data.jawaban, questionIds), ...restoredAnswers,
  }
  narasi.value = data.submitted ? (data.narasi || '') : (restoredNarasi || data.narasi || '')
  restoringDraft = false
  nama.value = data.nama_responden || ''
  jabatan.value = data.jabatan || ''
  opdId.value = data.opd_id
  info.value.tahun = data.tahun
}

async function checkStatus() {
  if (!verifiedToken.value || !info.value) return
  const { data } = await api.get('/survei/status', authHeader(verifiedToken.value))
  applyStatus(data)
}

async function openSurvey(token) {
  const { data } = await api.get('/survei/status', authHeader(token))
  draftStorageKey.value = ''
  draftStorageError.value = false
  try {
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(token))
    const fingerprint = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('')
    draftStorageKey.value = `${import.meta.env.BASE_URL}cee-draft:${fingerprint}`
  } catch {
    draftStorageError.value = true
  }
  verifiedToken.value = token
  applyStatus(data)
  storeToken(token)
  tokenInput.value = ''
}

async function doLogin() {
  if (!tokenInput.value.trim()) return
  checking.value = true
  try {
    await openSurvey(tokenInput.value.trim())
  } catch (e) {
    if (e.response?.status === 401) doLogout()
    toast.add({ severity: 'error', summary: 'Token tidak dapat digunakan', detail: e.response?.data?.detail || e.message, life: 5000 })
  } finally {
    checking.value = false
  }
}
function doLogout() {
  draftStorageKey.value = ''
  draftStorageError.value = false
  storeToken('')
  user.value = null
  verifiedToken.value = ''
  tokenInput.value = ''
  opdId.value = null
  answers.value = {}
  narasi.value = ''
  nama.value = ''
  jabatan.value = ''
  status.value = null
}

async function submit() {
  if (!opdId.value) {
    toast.add({ severity: 'warn', summary: 'Pilih OPD terlebih dahulu', life: 3000 })
    return
  }
  if (!nama.value.trim()) {
    toast.add({ severity: 'warn', summary: 'Nama responden wajib diisi', life: 3000 })
    return
  }
  if (!allAnswered.value) {
    toast.add({
      severity: 'warn',
      summary: 'Lengkapi semua pertanyaan',
      detail: `${answeredCount.value}/${totalQuestions.value} terjawab`,
      life: 3000,
    })
    return
  }
  submitting.value = true
  try {
    const t = verifiedToken.value
    await api.post(
      '/survei/submit',
      {
        opd_id: opdId.value,
        tahun: info.value.tahun,
        nama_responden: nama.value.trim(),
        jabatan: jabatan.value,
        jawaban: answers.value,
        narasi: narasi.value.trim(),
      },
      authHeader(t),
    )
    status.value = { ...status.value, submitted: true }
    clearDraft()
    await checkStatus() // kunci & tampilkan ringkasan
    toast.add({ severity: 'success', summary: 'Kuesioner terkirim', detail: 'Terima kasih atas partisipasi Anda.', life: 5000 })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e) {
    const msg = e.response?.data?.detail || e.message
    if (e.response?.status === 401) doLogout()
    if (e.response?.status === 409) await checkStatus()
    toast.add({ severity: 'error', summary: 'Gagal mengirim', detail: msg, life: 6000 })
  } finally {
    submitting.value = false
  }
}

function fmtDate(iso) {
  return formatDateTime(iso, { dateStyle: 'long', timeStyle: 'short' })
}

onMounted(async () => {
  try {
    await loadPublic()
    const token = storedToken()
    if (token) {
      try {
        await openSurvey(token)
      } catch (e) {
        if (e.response?.status === 401) {
          doLogout()
          toast.add({ severity: 'warn', summary: 'Token tidak lagi valid. Masukkan token terbaru dari undangan.', life: 5000 })
        } else {
          // Gangguan jaringan tidak menghapus token sesi yang masih dapat digunakan.
          throw e
        }
      }
    }
    authReady.value = true
  } catch (e) {
    loadError.value = 'Kuesioner gagal dimuat. Silakan muat ulang halaman.'
  }
})
</script>

<template>
  <div class="survei-page">
    <header class="survei-top">
      <div class="brand">
        <i class="pi pi-shield" />
        <div>
          <div class="t">Survei Penilaian Lingkungan Pengendalian Internal</div>
          <div class="s">CONTROL ENVIRONMENT EVALUATION (CEE) - {{ info?.instansi || 'Pemerintah Kota Tegal' }} — Tahun {{ info?.tahun || '' }}</div>
        </div>
      </div>
      <div v-if="user" class="userbox">
        <img v-if="user.photo" :src="user.photo" referrerpolicy="no-referrer" />
        <span>{{ user.name || user.email }}</span>
        <Button icon="pi pi-sign-out" text rounded size="small" @click="doLogout" v-tooltip.bottom="'Keluar'" />
      </div>
    </header>

    <main class="survei-body">
      <!-- Di luar jadwal: form tidak ditampilkan sama sekali. Responden yang
           sudah mengisi tetap bisa melihat ringkasannya di bawah. -->
      <div v-if="surveiTutup && user && !alreadySubmitted" class="login-card">
        <i class="pi pi-calendar-times" style="font-size: 2.4rem; color: #f59e0b" />
        <h2>Survei Belum Dibuka</h2>
        <p class="muted">
          {{ jadwal.alasan }}
          <br v-if="jadwal.mulai || jadwal.selesai" />
          <template v-if="jadwal.mulai || jadwal.selesai">
            Jadwal pengisian:
            <strong>{{ fmtTgl(jadwal.mulai) || 'tanpa batas awal' }}</strong>
            s/d
            <strong>{{ fmtTgl(jadwal.selesai) || 'tanpa batas akhir' }}</strong>.
          </template>
        </p>
      </div>

      <!-- Masukkan token undangan -->
      <div v-else-if="authReady && !user" class="login-card">
        <i class="pi pi-user-edit" style="font-size: 2.4rem; color: #3b82f6" />
        <h2>Masukkan Token ID</h2>
        <p class="muted">
          Masukkan token ID yang dikirim admin melalui email undangan.
          <br /><strong>Jawaban hanya dapat dikirim satu kali untuk setiap undangan.</strong>
        </p>
        <form @submit.prevent="doLogin" style="display: grid; gap: 12px; width: 100%">
          <InputText v-model="tokenInput" aria-label="Token ID" placeholder="Token ID dari email" autocomplete="off" required />
          <Button type="submit" label="Buka Survei" icon="pi pi-key" :loading="checking" />
        </form>
      </div>

      <!-- Sudah mengisi: terkunci -->
      <div v-else-if="user && info && alreadySubmitted" class="form-wrap">
        <div class="done-card">
          <i class="pi pi-check-circle" style="font-size: 2.6rem; color: #16a34a" />
          <h2>Terima kasih, survei Anda sudah tercatat</h2>
          <p class="muted">
            Setiap responden hanya dapat mengisi survei <strong>satu kali dalam satu tahun</strong>.
            Berikut ringkasan jawaban Anda untuk Tahun {{ info.tahun }}.
          </p>
          <div class="summary">
            <div><span class="muted">Nama Responden</span><b>{{ status.nama_responden || '-' }}</b></div>
            <div><span class="muted">OPD</span><b>{{ status.opd_nama }}</b></div>
            <div><span class="muted">Jabatan</span><b>{{ status.jabatan || '-' }}</b></div>
            <div><span class="muted">Kode Responden</span><b>{{ status.kode_responden }}</b></div>
            <div><span class="muted">Waktu Pengisian</span><b>{{ fmtDate(status.submitted_at) }}</b></div>
          </div>
        </div>

        <!-- Jawaban read-only -->
        <div v-for="kat in kuesioner" :key="kat.id" class="card">
          <div class="kat-head">{{ kat.kode }}. {{ kat.nama }}</div>
          <div v-for="(p, i) in kat.pertanyaan" :key="p.id" class="q">
            <div class="q-text"><span class="q-no">{{ i + 1 }}.</span> {{ p.pertanyaan }}</div>
            <div class="q-opts">
              <span v-for="s in skala" :key="s.nilai" class="opt ro" :class="{ on: answers[p.id] === s.nilai }">
                <b>{{ s.nilai }}</b><span>{{ s.label }}</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Narasi read-only -->
        <div class="card">
          <div class="kat-head">Narasi Lain Terkait Kondisi Lingkungan Pengendalian</div>
          <div v-if="status.narasi" class="narasi-submitted">
            {{ status.narasi }}
          </div>
          <div v-else class="muted" style="font-style: italic; font-size: 0.88rem; padding: 6px 0">
            Tidak ada narasi tambahan yang disampaikan.
          </div>
        </div>
      </div>

      <!-- Token valid, belum mengisi: form -->
      <div v-else-if="user && info" class="form-wrap">
        <section class="card survey-guide" aria-labelledby="pengantar-survei">
          <h2 id="pengantar-survei">Pengantar</h2>
          <p>
            Bapak/Ibu yang terhormat, terima kasih sudah bersedia mengisi kuesioner ini.
            Kuesioner ini bertujuan untuk keperluan internal dan dimaksudkan untuk melihat
            kondisi lingkungan pengendalian di unit instansi Bapak/Ibu. Mengingat pentingnya
            data dari kuesioner ini, diharapkan Bapak/Ibu mengisinya dengan <b>benar dan jujur
            sesuai dengan kondisi saat ini</b>.
          </p>
          <p>
            Identitas dan jawaban Bapak/Ibu digunakan untuk keperluan evaluasi internal
            dan dapat diakses oleh pengelola survei yang berwenang.
          </p>
          <h2 id="petunjuk-survei">Petunjuk Pengisian</h2>
          <ol aria-labelledby="petunjuk-survei">
            <li>
              Bacalah setiap pernyataan dengan saksama, lalu pilih satu jawaban yang paling
              sesuai dengan kondisi di unit instansi Bapak/Ibu:
              <ul class="guide-scale">
                <li><strong>1</strong> — Tidak Setuju/Belum ada/ belum dibangun</li>
                <li><strong>2</strong> — Kurang Setuju/Telah dibangun/diterapkan, akan tetapi belum konsisten</li>
                <li><strong>3</strong> — Setuju/Sudah dibangun atau diterapkan dengan baik, tetapi masih bisa ditingkatkan</li>
                <li><strong>4</strong> — Sangat Setuju/Sudah dibangun atau diterapkan dengan baik dan dapat ditularkan ke organisasi lain</li>
              </ul>
            </li>
            <li>Jawablah seluruh pernyataan dengan benar dan jujur sesuai kondisi saat ini.</li>
            <li>Apabila terdapat pernyataan yang dirasa kurang jelas, silakan ditanyakan kepada fasilitator.</li>
            <li>
              Periksa kembali jawaban sebelum menekan <strong>Kirim Jawaban</strong>.
              Jawaban hanya dapat dikirim satu kali dan tidak dapat diubah oleh responden setelah dikirim.
            </li>
          </ol>
        </section>
        <div class="card identity">
          <div style="flex: 1 1 100%">
            <label class="lbl">Nama Responden</label>
            <InputText readonly v-model="nama" placeholder="Nama lengkap Anda" style="width: 100%" />
          </div>
          <div style="flex: 1">
            <label class="lbl">Organisasi Perangkat Daerah (OPD)</label>
            <Select
              disabled
              v-model="opdId"
              :options="opdOptions"
              optionLabel="label"
              optionValue="value"
              filter
              placeholder="Pilih OPD Anda"
              style="width: 100%"
            />
          </div>
          <div style="flex: 1">
            <label class="lbl">Jabatan</label>
            <InputText readonly v-model="jabatan" placeholder="cth: Kepala Subbagian" style="width: 100%" />
          </div>
        </div>

        <template v-if="opdId">
          <p role="status" class="muted">
            {{ draftStorageError
              ? 'Draf tidak dapat disimpan di browser ini. Jangan tutup atau muat ulang halaman sebelum mengirim jawaban.'
              : '' }}
          </p>
          <div class="progress">
            <div class="bar"><div :style="{ width: (answeredCount / totalQuestions) * 100 + '%' }" /></div>
            <span class="muted">{{ answeredCount }} / {{ totalQuestions }} terjawab</span>
          </div>

          <div v-for="kat in kuesioner" :key="kat.id" class="card">
            <div class="kat-head">{{ kat.kode }}. {{ kat.nama }}</div>
            <div v-for="(p, i) in kat.pertanyaan" :key="p.id" class="q">
              <div class="q-text"><span class="q-no">{{ i + 1 }}.</span> {{ p.pertanyaan }}</div>
              <div class="q-opts">
                <label v-for="s in skala" :key="s.nilai" class="opt" :class="{ on: answers[p.id] === s.nilai }">
                  <input type="radio" :name="'q' + p.id" :value="s.nilai" v-model="answers[p.id]" />
                  <b>{{ s.nilai }}</b><span>{{ s.label }}</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Narasi lain terkait kondisi lingkungan pengendalian -->
          <div class="card">
            <div class="kat-head">Narasi Lain Terkait Kondisi Lingkungan Pengendalian</div>
            <label for="narasi-kondisi" class="lbl" style="margin-top: 6px; margin-bottom: 8px; font-size: 0.85rem">
              Sampaikan penjelasan, catatan, atau masukan lain mengenai kondisi lingkungan pengendalian pada unit kerja / instansi Anda (opsional):
            </label>
            <Textarea
              id="narasi-kondisi"
              v-model="narasi"
              rows="4"
              autoResize
              placeholder="Tuliskan narasi atau catatan kondisi lingkungan pengendalian di sini..."
              style="width: 100%"
            />
          </div>

          <div class="submit-bar">
            <span class="muted" v-if="!allAnswered">Lengkapi semua pertanyaan untuk mengirim.</span>
            <span class="muted" v-else style="color: #16a34a"><i class="pi pi-check" /> Semua pertanyaan terjawab</span>
            <Button label="Kirim Jawaban" icon="pi pi-send" :loading="submitting" :disabled="!allAnswered" @click="submit" />
          </div>
          <p class="muted" style="text-align: center; font-size: 0.8rem; margin-top: 4px">
            Pastikan OPD &amp; jawaban sudah benar — jawaban hanya dapat dikirim satu kali per periode.
          </p>
        </template>
        <div v-else class="muted" style="text-align: center; padding: 30px">
          Pilih OPD Anda untuk menampilkan pertanyaan.
        </div>
      </div>

      <p v-else-if="loadError" role="alert">{{ loadError }}</p>
      <AppLoader v-else label="Memuat kuesioner…" />
    </main>
  </div>
</template>

<style scoped>
.survey-guide { color: #334155; line-height: 1.75; }
.survey-guide h2 { margin: 0 0 12px; font-size: 1.05rem; color: #0f172a; }
.survey-guide h2:not(:first-child) { margin-top: 24px; }
.survey-guide p { margin: 0 0 12px; }
.survey-guide ol { margin: 0; padding-left: 24px; }
.survey-guide li { margin-bottom: 8px; }
.guide-scale { margin: 8px 0; padding-left: 20px; }
.guide-scale li { margin-bottom: 2px; }

.survei-page { min-height: 100vh; background: #f1f5f9; }
.survei-top {
  background: #0f172a; color: #fff; padding: 14px 22px;
  display: flex; align-items: center; gap: 14px; position: sticky; top: 0; z-index: 10;
}
.survei-top .brand { display: flex; align-items: center; gap: 12px; flex: 1; }
.survei-top .brand i { font-size: 1.6rem; color: #60a5fa; }
.survei-top .brand .t { font-weight: 700; }
.survei-top .brand .s { font-size: 0.78rem; color: #94a3b8; }
.userbox { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; }
.userbox img { width: 30px; height: 30px; border-radius: 50%; }

.survei-body { max-width: 880px; margin: 0 auto; padding: 24px 16px 60px; }
.login-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 40px;
  text-align: center; max-width: 480px; margin: 60px auto; display: flex;
  flex-direction: column; align-items: center; gap: 12px;
}
.login-card h2 { margin: 4px 0; }
.muted { color: #64748b; }

.done-card {
  background: #fff; border: 1px solid #bbf7d0; border-radius: 14px; padding: 28px;
  text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; margin-bottom: 16px;
}
.done-card h2 { margin: 4px 0; }
.summary {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;
  width: 100%; margin-top: 12px; text-align: left;
}
.summary > div { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; }
.summary span { display: block; font-size: 0.74rem; }
.summary b { font-size: 0.9rem; }

.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 16px; }
.identity { display: flex; gap: 16px; flex-wrap: wrap; }
.lbl { font-size: 0.8rem; color: #64748b; display: block; margin-bottom: 4px; }

.progress { display: flex; align-items: center; gap: 12px; margin: 4px 0 14px; }
.progress .bar { flex: 1; height: 8px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
.progress .bar div { height: 100%; background: #3b82f6; transition: width 0.2s; }

.kat-head { font-weight: 700; color: #0f172a; padding-bottom: 8px; margin-bottom: 8px; border-bottom: 2px solid #eff6ff; }
.q { padding: 12px 0; border-bottom: 1px dashed #e2e8f0; }
.q:last-child { border-bottom: none; }
.q-text { font-size: 0.9rem; margin-bottom: 8px; }
.q-no { color: #94a3b8; font-weight: 600; margin-right: 4px; }
.q-opts { display: flex; gap: 8px; flex-wrap: wrap; }
.opt {
  display: flex; align-items: center; gap: 6px; border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 6px 12px; cursor: pointer; font-size: 0.82rem; user-select: none;
}
.opt:hover { border-color: #93c5fd; background: #f8fafc; }
.opt.on { border-color: #3b82f6; background: #eff6ff; color: #1d4ed8; }
.opt.ro { cursor: default; opacity: 0.65; }
.opt.ro.on { opacity: 1; border-color: #16a34a; background: #dcfce7; color: #166534; }
.opt input { display: none; }
.opt b { font-size: 0.95rem; }

.submit-bar {
  display: flex; align-items: center; justify-content: space-between; gap: 14px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 18px;
  position: sticky; bottom: 14px; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
}
.narasi-submitted {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 0.9rem;
  color: #1e293b;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  margin-top: 8px;
}
</style>
