<script setup>
import { computed, onMounted, ref } from 'vue'
import DatePicker from 'primevue/datepicker'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import AppLoader from '@/components/AppLoader.vue'
import { useContextStore } from '@/stores/context'
import { formatDate, formatDateTime, parseDateOnly, toDateOnlyString } from '@/utils/date'

const toast = useToast()
const ctx = useContextStore()

const loading = ref(true)
const saving = ref(false)
const showEmailPreview = ref(false)
const showWaPreview = ref(true)

const form = ref({
  tahun_default: null,
  survei_mulai: null,
  survei_selesai: null,
  survei_aktif: true,
  survei_pesan_tutup: '',
  template_email_subject: '',
  template_email: '',
  template_wa: '',
  ai_provider: 'gemini',
  ai_model: 'gemini-3.8-flash',
  ai_api_key: '',
})

const showApiKey = ref(false)
const testingAi = ref(false)
const aiTestResult = ref(null)

const providerOptions = [
  { label: 'Hermes Agent (Lokal Komputer — Tanpa API Key)', value: 'hermes', defaultModel: 'gpt-6-astra', docUrl: '', placeholder: 'Tidak memerlukan API Key (Otomatis terhubung ke Hermes lokal)' },
  { label: 'Google Gemini (Rekomendasi Cloud 2026)', value: 'gemini', defaultModel: 'gemini-3.8-flash', docUrl: 'https://aistudio.google.com/app/apikey', placeholder: 'AIzaSy...' },
  { label: 'OpenAI (o4-mini / o3 / GPT-5)', value: 'openai', defaultModel: 'o4-mini', docUrl: 'https://platform.openai.com/api-keys', placeholder: 'sk-proj-...' },
  { label: 'Anthropic Claude (Claude Sonnet 5.5 / Haiku 5.5)', value: 'anthropic', defaultModel: 'claude-sonnet-5-5', docUrl: 'https://console.anthropic.com/settings/keys', placeholder: 'sk-ant-...' },
]

const modelPresets = {
  hermes: [
    { label: 'gpt-6-astra (Model Bawaan Hermes Agent)', value: 'gpt-6-astra' },
  ],
  gemini: [
    { label: 'gemini-3.8-flash (Model Utama 2026 - Sangat Cepat & Cerdas)', value: 'gemini-3.8-flash' },
    { label: 'gemini-3.5-flash-lite (Ultra Cepat & Ringan)', value: 'gemini-3.5-flash-lite' },
    { label: 'gemini-3.1-pro (Penalaran Mendalam & Analisis)', value: 'gemini-3.1-pro' },
    { label: 'gemini-2.5-flash (Generasi 2.5)', value: 'gemini-2.5-flash' },
  ],
  openai: [
    { label: 'o4-mini (Model Reasoning Cepat 2026)', value: 'o4-mini' },
    { label: 'o3-mini (Model Penalaran Canggih)', value: 'o3-mini' },
    { label: 'gpt-5 (Flagship AI 2026)', value: 'gpt-5' },
    { label: 'o3 (Deep Reasoning)', value: 'o3' },
    { label: 'gpt-4o (Generasi Sebelumnya)', value: 'gpt-4o' },
  ],
  anthropic: [
    { label: 'claude-sonnet-5-5 (Model Utama 2026 - Sangat Teliti)', value: 'claude-sonnet-5-5' },
    { label: 'claude-haiku-5-5 (Ultra Cepat)', value: 'claude-haiku-5-5' },
    { label: 'claude-opus-5-5 (Penalaran Paling Kuat)', value: 'claude-opus-5-5' },
    { label: 'claude-3-7-sonnet-20250219 (Claude 3.7 Hybrid Reasoning)', value: 'claude-3-7-sonnet-20250219' },
  ],
}

function onProviderChange(val) {
  const p = providerOptions.find((x) => x.value === val)
  if (p && !form.value.ai_model) {
    form.value.ai_model = p.defaultModel
  } else if (p && modelPresets[val] && !modelPresets[val].some((m) => m.value === form.value.ai_model)) {
    form.value.ai_model = p.defaultModel
  }
}

async function testAiConnection() {
  testingAi.value = true
  aiTestResult.value = null
  try {
    const { data } = await api.post('/ai/test-connection', {
      provider: form.value.ai_provider,
      model: form.value.ai_model,
      api_key: form.value.ai_api_key,
    })
    aiTestResult.value = { success: true, message: data.message + (data.reply ? ` Respon: "${data.reply}"` : '') }
    toast.add({ severity: 'success', summary: 'Koneksi Berhasil', detail: 'Provider AI siap digunakan.', life: 3000 })
  } catch (e) {
    const err = e.response?.data?.detail || e.message || 'Gagal koneksi'
    aiTestResult.value = { success: false, message: err }
    toast.add({ severity: 'error', summary: 'Koneksi Gagal', detail: err, life: 4000 })
  } finally {
    testingAi.value = false
  }
}

const defaults = ref({
  template_email_subject: '',
  template_email: '',
  template_wa: '',
})

const status = ref(null) // status jadwal dari server
const updated = ref({ at: null, by: null })

const availablePlaceholders = [
  { tag: '{nama}', desc: 'Nama lengkap responden' },
  { tag: '{nip}', desc: 'NIP responden' },
  { tag: '{jabatan}', desc: 'Jabatan responden' },
  { tag: '{opd}', desc: 'Nama Perangkat Daerah (OPD)' },
  { tag: '{tahun}', desc: 'Tahun penilaian risiko' },
  { tag: '{link}', desc: 'Tautan survei publik' },
  { tag: '{token}', desc: 'Token akses kuesioner' },
]

// Kolom tanggal dikirim/diterima sebagai 'YYYY-MM-DD'; DatePicker memakai Date.
const toDate = parseDateOnly
const toIso = toDateOnlyString
const fmt = (s) => (s ? formatDate(s) : '—')

const rentangSalah = computed(() => {
  const { survei_mulai: a, survei_selesai: b } = form.value
  return !!(a && b && a > b)
})

async function load() {
  loading.value = true
  const { data } = await api.get('/pengaturan')
  defaults.value = {
    template_email_subject: data.default_template_email_subject || '',
    template_email: data.default_template_email || '',
    template_wa: data.default_template_wa || '',
  }
  form.value = {
    tahun_default: data.tahun_default,
    survei_mulai: toDate(data.survei_mulai),
    survei_selesai: toDate(data.survei_selesai),
    survei_aktif: !!data.survei_aktif,
    survei_pesan_tutup: data.survei_pesan_tutup || '',
    template_email_subject: data.template_email_subject || '',
    template_email: data.template_email || '',
    template_wa: data.template_wa || '',
    ai_provider: data.ai_provider || 'gemini',
    ai_model: data.ai_model || 'gemini-3.8-flash',
    ai_api_key: data.ai_api_key ? '••••••••••••••••' : '',
  }
  status.value = data.survei_status
  updated.value = { at: data.updated_at, by: data.updated_by }
  loading.value = false
}

function resetEmailTemplate() {
  form.value.template_email_subject = defaults.value.template_email_subject
  form.value.template_email = defaults.value.template_email
  toast.add({ severity: 'info', summary: 'Template Email direset', detail: 'Isian diisi dengan format bawaan sistem.', life: 2500 })
}

function resetWaTemplate() {
  form.value.template_wa = defaults.value.template_wa
  toast.add({ severity: 'info', summary: 'Template WhatsApp direset', detail: 'Isian diisi dengan format bawaan sistem.', life: 2500 })
}

function addTag(field, tag) {
  form.value[field] = (form.value[field] || '') + tag
}

const previewWaText = computed(() => {
  const tpl = form.value.template_wa || defaults.value.template_wa || ''
  return tpl
    .replace(/{nama}/g, 'Budi Santoso, S.Kom')
    .replace(/{nama_responden}/g, 'Budi Santoso, S.Kom')
    .replace(/{nip}/g, '198501012010011002')
    .replace(/{jabatan}/g, 'Sekretaris Dinas')
    .replace(/{opd}/g, 'Dinas Kesehatan')
    .replace(/{tahun}/g, String(form.value.tahun_default || 2027))
    .replace(/{link}/g, 'http://localhost:5173/survei')
    .replace(/{url}/g, 'http://localhost:5173/survei')
    .replace(/{token}/g, 'd3LIsAc9AwIXuCsbfzVhBkF7')
})

const previewEmailSubject = computed(() => {
  const tpl = form.value.template_email_subject || defaults.value.template_email_subject || ''
  return tpl
    .replace(/{nama}/g, 'Budi Santoso, S.Kom')
    .replace(/{opd}/g, 'Dinas Kesehatan')
    .replace(/{tahun}/g, String(form.value.tahun_default || 2027))
})

const previewEmailBody = computed(() => {
  const tpl = form.value.template_email || defaults.value.template_email || ''
  return tpl
    .replace(/{nama}/g, 'Budi Santoso, S.Kom')
    .replace(/{nama_responden}/g, 'Budi Santoso, S.Kom')
    .replace(/{nip}/g, '198501012010011002')
    .replace(/{jabatan}/g, 'Sekretaris Dinas')
    .replace(/{opd}/g, 'Dinas Kesehatan')
    .replace(/{tahun}/g, String(form.value.tahun_default || 2027))
    .replace(/{link}/g, 'http://localhost:5173/survei')
    .replace(/{url}/g, 'http://localhost:5173/survei')
    .replace(/{token}/g, 'd3LIsAc9AwIXuCsbfzVhBkF7')
})

async function save() {
  if (rentangSalah.value) return
  saving.value = true
  try {
    const { data } = await api.put('/pengaturan', {
      tahun_default: form.value.tahun_default,
      survei_mulai: toIso(form.value.survei_mulai),
      survei_selesai: toIso(form.value.survei_selesai),
      survei_aktif: form.value.survei_aktif,
      survei_pesan_tutup: form.value.survei_pesan_tutup,
      template_email_subject: form.value.template_email_subject,
      template_email: form.value.template_email,
      template_wa: form.value.template_wa,
      ai_provider: form.value.ai_provider,
      ai_model: form.value.ai_model,
      ai_api_key: form.value.ai_api_key,
    })
    status.value = data.survei_status
    updated.value = { at: data.updated_at, by: data.updated_by }
    // Sesi ini ikut pindah tahun bila admin belum memilih tahun sendiri.
    if (data.tahun_default) ctx.applyTahunDefault(data.tahun_default)
    toast.add({ severity: 'success', summary: 'Pengaturan tersimpan', life: 2000 })
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal menyimpan',
      detail: e.response?.data?.detail || 'Coba lagi',
      life: 4000,
    })
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppLoader v-if="loading" label="Memuat pengaturan…" />

  <template v-else>
    <!-- 1. Tahun Penilaian -->
    <div class="page-card" style="margin-bottom: 16px">
      <h3 class="sec-title">Tahun Penilaian</h3>
      <p class="muted sec-desc">
        Tahun yang dipakai sebagai awalan saat pengguna membuka aplikasi dan sebagai tahun
        survei CEE. Pengguna tetap dapat memilih tahun lain lewat pemilih tahun di kanan atas.
      </p>
      <label class="lbl">Tahun Default</label>
      <InputNumber
        v-model="form.tahun_default"
        :useGrouping="false"
        :min="2000"
        :max="2100"
        showButtons
        placeholder="cth: 2026"
        style="width: 180px"
      />
    </div>

    <!-- 2. Jadwal Survei CEE -->
    <div class="page-card" style="margin-bottom: 16px">
      <h3 class="sec-title">Jadwal Survei CEE</h3>
      <p class="muted sec-desc">
        Rentang tanggal saat responden boleh mengisi survei publik. Tanggal bersifat
        <strong>inklusif</strong> — dikosongkan berarti tanpa batas pada sisi tersebut.
      </p>

      <Message
        v-if="status"
        :severity="status.dibuka ? 'success' : 'warn'"
        :closable="false"
        class="status-msg"
      >
        <template v-if="status.dibuka">
          Survei <strong>sedang dibuka</strong> hari ini.
        </template>
        <template v-else>
          Survei <strong>tertutup</strong> — {{ status.alasan }}
        </template>
      </Message>

      <div class="grid-2" style="gap: 14px; margin-top: 14px">
        <div>
          <label class="lbl">Tanggal Mulai</label>
          <DatePicker
            v-model="form.survei_mulai"
            dateFormat="dd-mm-yy"
            showIcon
            showButtonBar
            placeholder="Tanpa batas awal"
            fluid
          />
        </div>
        <div>
          <label class="lbl">Tanggal Selesai</label>
          <DatePicker
            v-model="form.survei_selesai"
            dateFormat="dd-mm-yy"
            showIcon
            showButtonBar
            placeholder="Tanpa batas akhir"
            :minDate="form.survei_mulai || undefined"
            fluid
          />
        </div>
      </div>

      <Message v-if="rentangSalah" severity="error" :closable="false" style="margin-top: 12px">
        Tanggal mulai tidak boleh melewati tanggal selesai.
      </Message>

      <div class="switch-row">
        <ToggleSwitch v-model="form.survei_aktif" inputId="survei-aktif" />
        <label for="survei-aktif">
          <strong>Survei aktif</strong>
          <small class="muted">
            Matikan untuk menutup survei sewaktu-waktu tanpa mengubah tanggal.
          </small>
        </label>
      </div>

      <div style="margin-top: 14px">
        <label class="lbl">Pesan saat survei tertutup</label>
        <InputText
          v-model="form.survei_pesan_tutup"
          placeholder="cth: Survei akan dibuka kembali pada Januari 2027"
          style="width: 100%"
        />
        <small class="muted">
          Ditampilkan di halaman survei publik. Dikosongkan = memakai pesan bawaan.
        </small>
      </div>

      <p class="muted preview">
        Rentang aktif: <strong>{{ fmt(status?.mulai) }}</strong> s/d
        <strong>{{ fmt(status?.selesai) }}</strong>
      </p>
    </div>

    <!-- 3. Template Undangan via WhatsApp -->
    <div class="page-card" style="margin-bottom: 16px">
      <div class="sec-header">
        <div>
          <h3 class="sec-title">
            <i class="pi pi-whatsapp" style="color: #25d366; margin-right: 6px" />
            Template Undangan via WhatsApp
          </h3>
          <p class="muted sec-desc">
            Pesan undangan yang dikirimkan ke nomor WhatsApp calon responden melalui gateway WhatsApp.
            Dikosongkan berarti menggunakan format bawaan sistem.
          </p>
        </div>
        <div class="header-actions">
          <Button
            label="Gunakan Template Bawaan"
            icon="pi pi-refresh"
            size="small"
            outlined
            severity="secondary"
            @click="resetWaTemplate"
          />
        </div>
      </div>

      <!-- Panduan Placeholder -->
      <div class="placeholder-box">
        <span class="placeholder-title">Variabel Dinamis (Klik untuk menyisipkan ke pesan WhatsApp):</span>
        <div class="placeholder-chips">
          <button
            v-for="p in availablePlaceholders"
            :key="'wa-' + p.tag"
            type="button"
            class="chip-btn"
            :title="p.desc"
            @click="addTag('template_wa', p.tag)"
          >
            <code>{{ p.tag }}</code>
            <span>{{ p.desc }}</span>
          </button>
        </div>
      </div>

      <div style="margin-top: 14px">
        <label class="lbl">Format Pesan WhatsApp</label>
        <Textarea
          v-model="form.template_wa"
          rows="9"
          autoResize
          class="template-textarea"
          :placeholder="defaults.template_wa"
        />
        <div class="tip-bar">
          <small class="muted">
            <i class="pi pi-info-circle" style="font-size: 0.75rem" /> Format teks WhatsApp: <strong>*tebal*</strong>, <em>_miring_</em>, ~coret~. Tautan <code>{link}</code> dan token <code>{token}</code> wajib disertakan agar responden dapat mengakses kuesioner.
          </small>
        </div>
      </div>

      <!-- Live Preview WhatsApp -->
      <div class="preview-section" style="margin-top: 14px">
        <div class="preview-toggle" @click="showWaPreview = !showWaPreview">
          <span>
            <i class="pi pi-eye mr-1" />
            <strong>Pratinjau Pesan WhatsApp (Simulasi Penerima)</strong>
          </span>
          <i :class="['pi', showWaPreview ? 'pi-chevron-up' : 'pi-chevron-down']" style="font-size: 0.8rem" />
        </div>

        <div v-if="showWaPreview" class="wa-mock-container">
          <div class="wa-chat-bubble">
            <div class="wa-bubble-content">
              {{ previewWaText }}
            </div>
            <div class="wa-bubble-time">
              10.45 <i class="pi pi-check" style="font-size: 0.65rem; color: #53bdeb" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Template Undangan via Email -->
    <div class="page-card" style="margin-bottom: 16px">
      <div class="sec-header">
        <div>
          <h3 class="sec-title">
            <i class="pi pi-envelope" style="color: #4f46e5; margin-right: 6px" />
            Template Undangan via Email
          </h3>
          <p class="muted sec-desc">
            Subjek dan isi surat undangan elektronik yang dikirimkan ke alamat email resmi responden via SMTP.
            Dikosongkan berarti menggunakan format bawaan sistem.
          </p>
        </div>
        <div class="header-actions">
          <Button
            label="Gunakan Template Bawaan"
            icon="pi pi-refresh"
            size="small"
            outlined
            severity="secondary"
            @click="resetEmailTemplate"
          />
        </div>
      </div>

      <!-- Panduan Placeholder -->
      <div class="placeholder-box">
        <span class="placeholder-title">Variabel Dinamis (Klik untuk menyisipkan ke email):</span>
        <div class="placeholder-chips">
          <button
            v-for="p in availablePlaceholders"
            :key="'email-' + p.tag"
            type="button"
            class="chip-btn"
            :title="p.desc"
            @click="addTag('template_email', p.tag)"
          >
            <code>{{ p.tag }}</code>
            <span>{{ p.desc }}</span>
          </button>
        </div>
      </div>

      <div style="margin-top: 14px">
        <label class="lbl">Subjek Email</label>
        <InputText
          v-model="form.template_email_subject"
          :placeholder="defaults.template_email_subject"
          style="width: 100%"
        />
      </div>

      <div style="margin-top: 14px">
        <label class="lbl">Isi Surat / Pesan Email</label>
        <Textarea
          v-model="form.template_email"
          rows="9"
          autoResize
          class="template-textarea"
          :placeholder="defaults.template_email"
        />
        <div class="tip-bar">
          <small class="muted">
            <i class="pi pi-info-circle" style="font-size: 0.75rem" /> Email HTML resmi otomatis menyertakan tombol tautan kuesioner dan kartu kode token responden yang rapi.
          </small>
        </div>
      </div>

      <!-- Live Preview Email -->
      <div class="preview-section" style="margin-top: 14px">
        <div class="preview-toggle" @click="showEmailPreview = !showEmailPreview">
          <span>
            <i class="pi pi-eye mr-1" />
            <strong>Pratinjau Tampilan Email (Simulasi Penerima)</strong>
          </span>
          <i :class="['pi', showEmailPreview ? 'pi-chevron-up' : 'pi-chevron-down']" style="font-size: 0.8rem" />
        </div>

        <div v-if="showEmailPreview" class="email-mock-container">
          <div class="email-mock-header">
            <strong>Subjek:</strong> {{ previewEmailSubject }}
          </div>
          <div class="email-mock-body">
            <div class="email-paragraphs">
              <p v-for="(par, idx) in previewEmailBody.split('\n\n')" :key="'p-' + idx">
                {{ par }}
              </p>
            </div>
            <div class="email-mock-btn-wrap">
              <span class="email-mock-btn">Buka Link Kuesioner</span>
            </div>
            <div class="email-mock-token-card">
              <small>TOKEN AKSES RESPONDEN:</small>
              <div class="token-val">d3LIsAc9AwIXuCsbfzVhBkF7</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. Integrasi AI Assistant -->
    <div class="page-card" style="margin-bottom: 16px">
      <div class="sec-header">
        <div>
          <h3 class="sec-title">
            <i class="pi pi-sparkles text-indigo-600 mr-2" />
            Integrasi AI Assistant (Kecerdasan Buatan)
          </h3>
          <p class="muted sec-desc">
            Konfigurasi penyedia Large Language Model (LLM) untuk asisten perumusan risiko otomatis (Kamus Risiko),
            rekomendasi Rencana Tindak Pengendalian (Form 7/8/9), dan Copilot interaktif.
          </p>
        </div>
        <div v-if="form.ai_provider === 'hermes' || form.ai_api_key" class="ai-active-badge">
          <i class="pi pi-check-circle" /> AI Aktif {{ form.ai_provider === 'hermes' ? '(Hermes Lokal)' : '' }}
        </div>
      </div>

      <div class="grid-2" style="gap: 16px; margin-top: 10px">
        <!-- Pilihan Provider -->
        <div>
          <label class="lbl">Provider AI</label>
          <Select
            v-model="form.ai_provider"
            :options="providerOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Pilih Penyedia AI"
            fluid
            @change="onProviderChange($event.value)"
          />
          <small v-if="form.ai_provider === 'hermes'" style="display: block; margin-top: 4px; color: #059669; font-weight: 600;">
            <i class="pi pi-check-circle mr-1" />
            Terhubung langsung dengan binary <code>~/.local/bin/hermes</code> di komputer lokal (gratis / tanpa API key).
          </small>
          <small v-else class="muted" style="display: block; margin-top: 4px">
            Dapatkan API key resmi di:
            <a
              :href="providerOptions.find((p) => p.value === form.ai_provider)?.docUrl || '#'"
              target="_blank"
              rel="noopener noreferrer"
              style="color: var(--p-primary-color); text-decoration: underline"
            >
              {{ form.ai_provider === 'gemini' ? 'Google AI Studio' : form.ai_provider === 'openai' ? 'OpenAI Platform' : 'Anthropic Console' }}
              <i class="pi pi-external-link" style="font-size: 0.7rem" />
            </a>
          </small>
        </div>

        <!-- Pilihan Model -->
        <div>
          <label class="lbl">Model AI</label>
          <Select
            v-if="modelPresets[form.ai_provider]"
            v-model="form.ai_model"
            :options="modelPresets[form.ai_provider]"
            optionLabel="label"
            optionValue="value"
            editable
            placeholder="Pilih atau ketik model"
            fluid
          />
          <InputText
            v-else
            v-model="form.ai_model"
            placeholder="cth: gemini-2.0-flash atau gpt-4o-mini"
            fluid
          />
          <small class="muted" style="display: block; margin-top: 4px">
            Dapat memilih preset rekomendasi atau mengetik nama model spesifik.
          </small>
        </div>
      </div>

      <!-- Input API Key -->
      <div style="margin-top: 16px">
        <label class="lbl">API Key</label>
        <div style="display: flex; gap: 8px">
          <InputText
            v-model="form.ai_api_key"
            :type="showApiKey ? 'text' : 'password'"
            :placeholder="providerOptions.find((p) => p.value === form.ai_provider)?.placeholder || 'Masukkan API Key...'"
            :disabled="form.ai_provider === 'hermes'"
            style="flex: 1"
          />
          <Button
            type="button"
            :icon="showApiKey ? 'pi pi-eye-slash' : 'pi pi-eye'"
            severity="secondary"
            outlined
            v-tooltip="showApiKey ? 'Sembunyikan' : 'Tampilkan'"
            :disabled="form.ai_provider === 'hermes'"
            @click="showApiKey = !showApiKey"
          />
          <Button
            type="button"
            label="Uji Koneksi"
            icon="pi pi-bolt"
            severity="help"
            :loading="testingAi"
            :disabled="form.ai_provider !== 'hermes' && !form.ai_api_key"
            @click="testAiConnection"
          />
        </div>
        <small v-if="form.ai_provider === 'hermes'" class="muted" style="display: block; margin-top: 4px">
          <i class="pi pi-info-circle" style="font-size: 0.72rem" />
          Hermes Agent menggunakan sesi otentikasi internal yang sudah aktif di sistem Anda.
        </small>
        <small v-else class="muted" style="display: block; margin-top: 4px">
          <i class="pi pi-lock" style="font-size: 0.72rem" />
          Kunci API disimpan terenkripsi di server dan hanya dipanggil backend saat fitur AI diakses.
        </small>
      </div>

      <!-- Test Connection Feedback Message -->
      <Message
        v-if="aiTestResult"
        :severity="aiTestResult.success ? 'success' : 'error'"
        :closable="true"
        style="margin-top: 12px"
        @close="aiTestResult = null"
      >
        <div style="display: flex; align-items: center; gap: 8px">
          <i :class="['pi', aiTestResult.success ? 'pi-check-circle' : 'pi-exclamation-triangle']" />
          <span>{{ aiTestResult.message }}</span>
        </div>
      </Message>
    </div>

    <!-- Tombol Simpan -->
    <div class="save-bar">
      <span v-if="updated.at" class="muted">
        Terakhir diubah {{ formatDateTime(updated.at) }}
        <template v-if="updated.by">oleh {{ updated.by }}</template>
      </span>
      <div class="spacer" />
      <Button
        label="Simpan Pengaturan"
        icon="pi pi-check"
        :loading="saving"
        :disabled="rentangSalah"
        @click="save"
      />
    </div>
  </template>
</template>

<style scoped>
.sec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.ai-active-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #15803d;
  background: #dcfce7;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #bbf7d0;
}
.sec-title {
  margin: 0 0 4px;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}
.sec-desc { margin: 0 0 14px; font-size: 0.84rem; line-height: 1.5; }
.lbl { display: block; font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px; }
.status-msg { margin: 0; }
.switch-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
}
.switch-row label { font-size: 0.86rem; cursor: pointer; }
.switch-row small { display: block; font-size: 0.78rem; margin-top: 2px; }
.preview { margin: 14px 0 0; font-size: 0.84rem; }
.save-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
  position: sticky;
  bottom: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

/* Placeholder Chips */
.placeholder-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px 12px;
}
.placeholder-title {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 6px;
}
.placeholder-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 2px 7px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
  color: #334155;
}
.chip-btn:hover {
  background: #eef2ff;
  border-color: #6366f1;
  color: #4f46e5;
  transform: translateY(-1px);
}
.chip-btn code {
  font-weight: bold;
  color: #4f46e5;
}
.chip-btn span {
  color: #64748b;
  font-size: 0.72rem;
}

.template-textarea {
  width: 100%;
  font-family: inherit;
  font-size: 0.86rem;
  line-height: 1.5;
}
.tip-bar {
  margin-top: 4px;
}

/* WhatsApp Mock Preview */
.preview-section {
  border-top: 1px dashed #e2e8f0;
  padding-top: 10px;
}
.preview-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 6px 0;
  color: #475569;
  font-size: 0.84rem;
  user-select: none;
}
.preview-toggle:hover {
  color: #1e293b;
}

.wa-mock-container {
  background: #efeae2;
  border-radius: 8px;
  padding: 16px;
  margin-top: 8px;
  display: flex;
  justify-content: flex-start;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.06);
}
.wa-chat-bubble {
  background: #ffffff;
  border-radius: 7.5px 7.5px 7.5px 0;
  padding: 10px 14px 6px;
  max-width: 90%;
  min-width: 260px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
  position: relative;
}
.wa-bubble-content {
  font-size: 0.84rem;
  line-height: 1.45;
  color: #111b21;
  white-space: pre-wrap;
  word-break: break-word;
}
.wa-bubble-time {
  text-align: right;
  font-size: 0.68rem;
  color: #667781;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 3px;
}

/* Email Mock Preview */
.email-mock-container {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 8px;
}
.email-mock-header {
  background: #e2e8f0;
  padding: 8px 14px;
  font-size: 0.84rem;
  color: #1e293b;
  border-bottom: 1px solid #cbd5e1;
}
.email-mock-body {
  background: #ffffff;
  padding: 20px;
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.55;
  max-width: 600px;
  margin: 0 auto;
}
.email-paragraphs p {
  margin: 0 0 12px;
}
.email-mock-btn-wrap {
  text-align: center;
  margin: 20px 0;
}
.email-mock-btn {
  display: inline-block;
  background: #30394a;
  color: #ffffff;
  padding: 9px 22px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.email-mock-token-card {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 10px 14px;
  text-align: center;
  margin-bottom: 12px;
}
.email-mock-token-card small {
  display: block;
  font-size: 0.72rem;
  color: #64748b;
  font-weight: bold;
  letter-spacing: 0.8px;
}
.email-mock-token-card .token-val {
  font-family: Consolas, monospace;
  font-size: 1.1rem;
  font-weight: bold;
  color: #0f172a;
  letter-spacing: 1px;
}
</style>
