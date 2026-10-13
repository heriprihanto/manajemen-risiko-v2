<script setup>
import { onMounted, ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Menu from 'primevue/menu'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const kategoriJabatanOptions = ['Pejabat Struktural', 'Pejabat Fungsional Tertentu', 'Pejabat Fungsional Umum / Staf']
const ctx = useContextStore()
const auth = useAuthStore()
const activeTab = ref(auth.isAdmin ? 'responden' : 'hasil')
const sending = ref(false)
const showImport = ref(false)
const importFile = ref(null)
const importing = ref(false)
const importResult = ref(null)
const downloading = ref(false)
const saving = ref(false)
const deletingId = ref(null)
const actionMenu = ref(null)
const actionItems = ref([])
const inviteMenu = ref(null)
const inviteMenuItems = ref([
  {
    label: 'Kirim Undangan via Email',
    icon: 'pi pi-envelope',
    command: () => sendInvitations('email'),
  },
  {
    label: 'Kirim Undangan via WhatsApp',
    icon: 'pi pi-whatsapp',
    command: () => sendInvitations('whatsapp'),
  },
])
const editingId = ref(null)
const invitationResult = ref(null)
const toast = useToast()
const confirm = useConfirm()
const form = ref(null)
const loading = ref(true)
const showAdd = ref(false)
const newResp = ref({ nip: '', nama_responden: '', jabatan: '', kategori_jabatan: null, email: '', no_hp: '' })

async function load() {
  loading.value = true
  const { data } = await api.get('/cee/form1a', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  form.value = data
  loading.value = false
}

async function downloadTemplate() {
  downloading.value = true
  try {
    const { data } = await api.get('/cee/responden/template', { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = url
    link.download = 'template-calon-responden.xlsx'
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal mengunduh template', life: 4000 })
  } finally { downloading.value = false }
}
async function importExcel() {
  const file = importFile.value
  if (!file || !file.name.toLowerCase().endsWith('.xlsx') || file.size > 5 * 1024 * 1024) {
    toast.add({ severity: 'warn', summary: 'Pilih file .xlsx maksimal 5 MB', life: 4000 })
    return
  }
  importing.value = true
  importResult.value = null
  try {
    const { data } = await api.post('/cee/responden/import', file, {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
      headers: { 'Content-Type': 'application/octet-stream' },
    })
    importResult.value = data
    importFile.value = null
    await load()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Impor gagal', detail: e.response?.data?.detail || e.message, life: 6000 })
  } finally { importing.value = false }
}

function toggleActions(event, r) {
  actionItems.value = [
    {
      label: 'Kirim Undangan via Email',
      icon: 'pi pi-envelope',
      disabled: !!r.submitted_at || r.sumber === 'survei' || sending.value,
      command: () => sendSingleInvitation(r, 'email'),
    },
    {
      label: 'Kirim Undangan via WhatsApp',
      icon: 'pi pi-whatsapp',
      disabled: !!r.submitted_at || r.sumber === 'survei' || sending.value,
      command: () => sendSingleInvitation(r, 'whatsapp'),
    },
    { separator: true },
    {
      label: 'Edit',
      icon: 'pi pi-pencil',
      disabled: !!r.submitted_at || r.sumber === 'survei' || deletingId.value !== null,
      command: () => openResponden(r),
    },
    {
      label: 'Hapus',
      icon: 'pi pi-trash',
      disabled: !!r.submitted_at || r.sumber === 'survei' || deletingId.value !== null,
      command: () => delResponden(r),
    },
  ]
  actionMenu.value.toggle(event)
}

function openResponden(r = null) {
  if (r && (r.submitted_at || r.sumber === 'survei')) return
  editingId.value = r?.id || null
  newResp.value = r ? { ...r } : { nip: '', nama_responden: '', jabatan: '', kategori_jabatan: null, email: '', no_hp: '' }
  showAdd.value = true
}
async function addResponden() {
  saving.value = true
  try {
    const payload = { ...newResp.value, opd_id: ctx.opdId, tahun: ctx.tahun }
    if (editingId.value) await api.put(`/cee/responden/${editingId.value}`, payload)
    else await api.post('/cee/responden', payload)
    showAdd.value = false
    await load()
    toast.add({ severity: 'success', summary: 'Responden disimpan', life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal menyimpan', detail: e.response?.data?.detail || e.message, life: 5000 })
  } finally { saving.value = false }
}
async function sendInvitations(channel = 'email') {
  sending.value = true
  invitationResult.value = null
  const mediaLabel = channel === 'whatsapp' ? 'WhatsApp' : 'Email'
  try {
    const { data } = await api.post('/cee/responden/undang', null, {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun, channel },
    })
    invitationResult.value = { ...data, channel }
    await load()
    if (data.terkirim > 0) {
      toast.add({
        severity: 'success',
        summary: `Undangan ${mediaLabel} Terkirim`,
        detail: `${data.terkirim} undangan berhasil dikirim.`,
        life: 3000,
      })
    }
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: `Gagal mengirim undangan via ${mediaLabel}`,
      detail: e.response?.data?.detail || e.message,
      life: 6000,
    })
  } finally {
    sending.value = false
  }
}

async function sendSingleInvitation(r, channel = 'email') {
  sending.value = true
  const mediaLabel = channel === 'whatsapp' ? 'WhatsApp' : 'Email'
  try {
    await api.post(`/cee/responden/${r.id}/undang`, null, {
      params: { channel },
    })
    toast.add({
      severity: 'success',
      summary: `Undangan ${mediaLabel} Terkirim`,
      detail: `Undangan berhasil dikirim ke ${r.nama_responden || r.kode_responden}`,
      life: 3000,
    })
    await load()
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: `Gagal mengirim undangan via ${mediaLabel}`,
      detail: e.response?.data?.detail || e.message,
      life: 5000,
    })
  } finally {
    sending.value = false
  }
}

function delResponden(r) {
  if (r.submitted_at || r.sumber === 'survei') return
  confirm.require({
    message: `Hapus responden ${r.nama_responden || r.kode_responden}? Token undangan dan seluruh jawaban responden ini juga akan dihapus.`,
    header: 'Hapus Responden',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Hapus',
    rejectLabel: 'Batal',
    acceptProps: { severity: 'danger' },
    accept: async () => {
      deletingId.value = r.id
      try {
        await api.delete(`/cee/responden/${r.id}`)
        await load()
        toast.add({ severity: 'success', summary: 'Responden dihapus', life: 3000 })
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Gagal menghapus responden', detail: e.response?.data?.detail || e.message, life: 5000 })
      } finally {
        deletingId.value = null
      }
    },
  })
}

let saveTimer = null
async function onAnswer(pertanyaan, respId, ev) {
  let v = ev.target.value
  if (v === '') v = null
  else {
    v = parseInt(v)
    if (isNaN(v) || v < 1 || v > 4) {
      ev.target.value = ''
      return
    }
  }
  pertanyaan.jawaban[respId] = v
  await api.post('/cee/jawaban', {
    responden_id: respId,
    pertanyaan_id: pertanyaan.id,
    nilai: v,
  })
  clearTimeout(saveTimer)
  saveTimer = setTimeout(load, 350)
}

onMounted(load)
</script>

<template>
  <div v-if="form">
    <div class="toolbar">
      <span class="muted">{{ ctx.opd?.nama_pd }} — {{ ctx.tahun }}</span>
      <span class="muted">| {{ form.responden.length }} responden (R1..R{{ form.responden.length }})</span>
    </div>

    <Tabs v-model:value="activeTab">
      <TabList>
        <Tab v-if="auth.isAdmin" value="responden">Daftar Calon Responden</Tab>
        <Tab value="hasil">Hasil Kuesioner</Tab>
      </TabList>
      <TabPanels class="cee-tab-panels">
        <TabPanel v-if="auth.isAdmin" value="responden">
          <div class="toolbar">
            <div class="spacer" />
            <Button label="Import Excel" icon="pi pi-file-excel" size="small" @click="showImport = true; importResult = null; importFile = null" />
            <Button v-if="auth.isAdmin" label="Tambah Responden" icon="pi pi-plus" size="small" @click="openResponden()" />
            <Button
              v-if="auth.isAdmin"
              type="button"
              size="small"
              :loading="sending"
              :disabled="!form.responden.length"
              aria-haspopup="true"
              aria-controls="invite-menu"
              @click="(event) => inviteMenu.toggle(event)"
            >
              <i class="pi pi-send" />
              <span>Kirim Undangan</span>
              <i class="pi pi-chevron-down" style="font-size: 0.72rem; margin-left: 2px" />
            </Button>
          </div>
          <div v-if="invitationResult" class="page-card" role="status">
            <div style="font-weight: 600; margin-bottom: 4px">
              Hasil Pengiriman Undangan ({{ invitationResult.channel === 'whatsapp' ? 'WhatsApp' : 'Email' }}):
            </div>
            <div>
              {{ invitationResult.terkirim }} undangan terkirim; {{ invitationResult.gagal.length }} gagal;
              {{ invitationResult.dilewati }} responden sudah mengisi.
            </div>
            <p v-for="r in invitationResult.gagal" :key="r.id" style="color: #ef4444; margin: 4px 0 0">
              <strong>{{ r.nama }}</strong>: {{ r.alasan }}
            </p>
          </div>
          <div v-if="auth.isAdmin" class="page-card" style="overflow-x: auto">
            <p class="muted">Daftar Calon Responden</p>
            <table class="grid-table">
              <thead><tr><th>NIP</th><th>Nama</th><th>Jabatan</th><th>Kategori Jabatan</th><th>Email</th><th>No HP</th><th>Status</th><th>Aksi</th></tr></thead>
              <tbody>
                <tr v-for="r in form.responden" :key="r.id">
                  <td>{{ r.nip || '–' }}</td><td>{{ r.nama_responden }}</td><td>{{ r.jabatan }}</td><td>{{ r.kategori_jabatan || '–' }}</td><td>{{ r.email || '–' }}</td><td>{{ r.no_hp || '–' }}</td>
                  <td>
                    <span v-if="r.submitted_at || r.sumber === 'survei'" class="status-badge badge-done">Sudah mengisi</span>
                    <span v-else-if="r.invited_at && r.whatsapp_invited_at" class="status-badge badge-sent">Email &amp; WA terkirim</span>
                    <span v-else-if="r.invited_at" class="status-badge badge-sent">Email terkirim</span>
                    <span v-else-if="r.whatsapp_invited_at" class="status-badge badge-sent">WA terkirim</span>
                    <span v-else class="status-badge badge-pending">Belum diundang</span>
                  </td>
                  <td>
                    <Button icon="pi pi-ellipsis-v" text rounded size="small" v-tooltip.top="'Aksi'" :loading="deletingId === r.id" :disabled="deletingId !== null" aria-haspopup="menu" aria-controls="responden-action-menu" :aria-label="`Aksi responden ${r.nama_responden || r.kode_responden}`" @click="toggleActions($event, r)" />
                  </td>
                </tr>
                <tr v-if="!form.responden.length"><td colspan="8">Belum ada calon responden.</td></tr>
              </tbody>
            </table>
          </div>
        </TabPanel>
        <TabPanel value="hasil">
          <div class="page-card" style="overflow-x: auto; padding: 0">
            <table class="grid-table">
              <thead>
                <tr>
                  <th style="width: 34px">No</th>
                  <th style="min-width: 320px; text-align: left">Pertanyaan / Sub-unsur</th>
                  <th v-for="r in form.responden" :key="r.id" :title="r.nama_responden || ''" class="resp-col">
                    {{ r.kode_responden }}
                    <i v-if="auth.isAdmin && !r.submitted_at && r.sumber !== 'survei'" class="pi pi-times del" @click="delResponden(r)" />
                  </th>
                  <th style="width: 60px">Modus</th>
                  <th style="width: 140px">Simpulan</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="kat in form.kategori" :key="kat.id">
                  <tr class="kat-row">
                    <td>{{ kat.kode }}</td>
                    <td style="text-align: left; font-weight: 600">{{ kat.nama }}</td>
                    <td :colspan="form.responden.length + 1"></td>
                    <td>
                      <span v-if="kat.simpulan" class="pill" :class="kat.simpulan === 'Memadai' ? 'pill-ok' : 'pill-bad'">
                        {{ kat.simpulan }}
                      </span>
                    </td>
                  </tr>
                  <tr v-for="(p, i) in kat.pertanyaan" :key="p.id">
                    <td class="muted">{{ i + 1 }}</td>
                    <td style="text-align: left">{{ p.pertanyaan }}</td>
                    <td v-for="r in form.responden" :key="r.id" class="ans-cell">
                      <input
                        class="ans-input"
                        type="number"
                        min="1"
                        max="4"
                        :value="p.jawaban[r.id] ?? ''"
                        @change="onAnswer(p, r.id, $event)"
                      />
                    </td>
                    <td><strong>{{ p.modus ?? '–' }}</strong></td>
                    <td>
                      <span v-if="p.simpulan" class="pill" :class="p.simpulan === 'Memadai' ? 'pill-ok' : 'pill-bad'">
                        {{ p.simpulan }}
                      </span>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          <p class="muted" style="font-size: 0.8rem; margin-top: 10px">
            Skala jawaban 1–4 (1=Tidak Setuju, 2=Kurang Setuju, 3=Setuju, 4=Sangat Setuju). Simpulan
            pertanyaan <strong>Memadai</strong> bila modus 3/4, <strong>Kurang Memadai</strong> bila modus 1/2.
          </p>

        </TabPanel>
      </TabPanels>
    </Tabs>

    <Dialog v-model:visible="showImport" header="Import Calon Responden dari Excel" modal :closable="!importing" :closeOnEscape="!importing" style="width: 620px; max-width: 95vw">
      <p>Tujuan: <strong>{{ ctx.opd?.nama_pd }} — {{ ctx.tahun }}</strong></p>
      <p>Gunakan kolom <strong>NIP | Nama | Jabatan | Email | No HP | Kategori Jabatan</strong>. Kategori jabatan boleh kosong untuk data lama; kolom lainnya wajib diisi. Format NIP dan No HP sebagai teks agar seluruh digit tetap utuh.</p>
      <p class="muted">Maksimal 1.000 baris dan 5 MB (.xlsx). Baris valid akan ditambahkan; baris tidak valid atau duplikat dilewati. Token dibuat otomatis. Email undangan dikirim melalui tombol Kirim Email Undangan setelah impor.</p>
      <Button label="Unduh Template Excel" icon="pi pi-download" text :loading="downloading" @click="downloadTemplate" />
      <div style="margin: 16px 0">
        <label for="responden-excel">File Excel</label>
        <input id="responden-excel" :key="importResult ? 'done' : 'ready'" type="file" accept=".xlsx" :disabled="importing" style="display: block; margin-top: 8px; max-width: 100%" @change="importFile = $event.target.files?.[0] || null" />
      </div>
      <div v-if="importResult" role="status">
        <p><strong>{{ importResult.berhasil }} berhasil diimpor</strong>, {{ importResult.gagal.length }} gagal dari {{ importResult.total }} baris data.</p>
        <div v-if="importResult.gagal.length" style="max-height: 220px; overflow: auto">
          <p v-for="error in importResult.gagal" :key="error.baris">Baris {{ error.baris }}: {{ error.alasan }}</p>
        </div>
      </div>
      <template #footer>
        <Button label="Tutup" text :disabled="importing" @click="showImport = false" />
        <Button label="Import" icon="pi pi-upload" :loading="importing" :disabled="!importFile || !ctx.opdId" @click="importExcel" />
      </template>
    </Dialog>

    <Menu id="responden-action-menu" ref="actionMenu" :model="actionItems" popup />
    <Menu id="invite-menu" ref="inviteMenu" :model="inviteMenuItems" popup />

    <Dialog v-model:visible="showAdd" :header="editingId ? 'Edit Responden' : 'Tambah Responden'" modal style="width: 420px">
      <div style="display: flex; flex-direction: column; gap: 12px; padding-top: 6px">
        <span v-for="field in [{ key: 'nip', label: 'NIP' }, { key: 'nama_responden', label: 'Nama' }, { key: 'jabatan', label: 'Jabatan' }, { key: 'email', label: 'Email' }, { key: 'no_hp', label: 'No HP' }]" :key="field.key">
          <label :for="field.key" class="muted" style="font-size: 0.82rem">{{ field.label }}</label>
          <InputText :id="field.key" v-model="newResp[field.key]" :type="field.key === 'email' ? 'email' : 'text'" style="width: 100%" />
        </span>
        <span>
          <label for="kategori-jabatan" class="muted" style="font-size: 0.82rem">Kategori Jabatan</label>
          <Select inputId="kategori-jabatan" v-model="newResp.kategori_jabatan" :options="kategoriJabatanOptions" placeholder="Pilih kategori jabatan" showClear style="width: 100%" />
        </span>
      </div>
      <template #footer>
        <Button label="Batal" text @click="showAdd = false" />
        <Button label="Simpan" icon="pi pi-check" :loading="saving" @click="addResponden" />
      </template>
    </Dialog>
  </div>
  <AppLoader v-else-if="loading" label="Memuat kuesioner…" />
</template>

<style scoped>
.cee-tab-panels { padding: 16px 0 0; background: transparent; }
.grid-table { border-collapse: collapse; width: 100%; font-size: 0.84rem; }
.grid-table th, .grid-table td {
  border: 1px solid #e2e8f0; padding: 6px 8px; vertical-align: middle;
}
.grid-table thead th { background: #f8fafc; position: sticky; top: 0; font-weight: 600; }
.kat-row td { background: #eff6ff; }
.resp-col { white-space: nowrap; }
.resp-col .del { color: #cbd5e1; cursor: pointer; margin-left: 4px; font-size: 0.7rem; }
.resp-col .del:hover { color: #ef4444; }
.ans-cell { padding: 2px !important; }
.ans-input {
  width: 42px; text-align: center; border: 1px solid #e2e8f0; border-radius: 5px;
  padding: 4px 2px; font-size: 0.84rem;
}
.ans-input:focus { outline: 2px solid #93c5fd; border-color: #3b82f6; }
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 500;
  white-space: nowrap;
}
.badge-done { background: #dcfce7; color: #166534; }
.badge-sent { background: #e0f2fe; color: #0369a1; }
.badge-pending { background: #f1f5f9; color: #64748b; }
</style>
