<script setup>
import { onMounted, ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const ctx = useContextStore()
const toast = useToast()
const rows = ref([])
const loading = ref(true)
const dialog = ref(false)
const editing = ref({})
const current = ref(null)

async function load() {
  loading.value = true
  const { data } = await api.get('/risiko/rtp', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  rows.value = data
  loading.value = false
}
function openEdit(row) {
  current.value = row
  editing.value = { ...(row.rtp || {}) }
  dialog.value = true
}
async function save() {
  await api.post('/risiko/rtp', { ...editing.value, risiko_id: current.value.id })
  dialog.value = false
  await load()
  toast.add({ severity: 'success', summary: 'RTP tersimpan', life: 1600 })
}
onMounted(load)
</script>

<template>
  <p class="muted" style="margin-top: 0">
    Rencana Tindak Pengendalian (RTP) untuk setiap risiko prioritas hasil Form 5.
  </p>
  <div class="page-card" style="padding: 0">
    <DataTable :value="rows" :loading="loading" size="small" stripedRows scrollable>
      <Column header="No" :style="{ width: '46px' }"><template #body="{ index }">{{ index + 1 }}</template></Column>
      <Column field="kode_risiko" header="Kode" :style="{ minWidth: '110px' }" />
      <Column field="uraian_risiko" header="Risiko Prioritas" :style="{ minWidth: '220px' }" />
      <Column field="pemilik_risiko" header="Pemilik" :style="{ minWidth: '130px' }" />
      <Column header="Pengendalian yang Ada" :style="{ minWidth: '180px' }">
        <template #body="{ data }">{{ data.rtp?.pengendalian_ada }}</template>
      </Column>
      <Column header="Celah" :style="{ minWidth: '160px' }">
        <template #body="{ data }">{{ data.rtp?.celah_pengendalian }}</template>
      </Column>
      <Column header="Rencana Tindak" :style="{ minWidth: '200px' }">
        <template #body="{ data }">{{ data.rtp?.rencana_tindak }}</template>
      </Column>
      <Column header="Target" :style="{ minWidth: '120px' }">
        <template #body="{ data }">{{ data.rtp?.target_waktu }}</template>
      </Column>
      <Column header="" :style="{ width: '60px' }">
        <template #body="{ data }"><Button icon="pi pi-pencil" text rounded size="small" @click="openEdit(data)" /></template>
      </Column>
      <template #empty><div class="muted" style="padding: 14px">Belum ada risiko prioritas. Tetapkan di Form 4/5.</div></template>
    </DataTable>
  </div>

  <Dialog v-model:visible="dialog" header="RTP atas Risiko" modal style="width: 620px">
    <div v-if="current" class="muted" style="margin-bottom: 8px">
      <strong>{{ current.kode_risiko }}</strong> — {{ current.uraian_risiko }}
    </div>
    <div style="display: flex; flex-direction: column; gap: 12px">
      <div><label class="muted lbl">Uraian Pengendalian yang Sudah Ada</label>
        <Textarea v-model="editing.pengendalian_ada" autoResize rows="2" style="width: 100%" /></div>
      <div><label class="muted lbl">Celah Pengendalian</label>
        <Textarea v-model="editing.celah_pengendalian" autoResize rows="2" style="width: 100%" /></div>
      <div><label class="muted lbl">Rencana Tindak Pengendalian</label>
        <Textarea v-model="editing.rencana_tindak" autoResize rows="2" style="width: 100%" /></div>
      <div><label class="muted lbl">Pemilik / Penanggung Jawab</label>
        <div class="ro-field">{{ current?.pemilik_risiko || '—' }}</div>
        <small class="muted">Mengikuti Form 3.b — ubah pemilik di sana.</small></div>
      <div style="display: flex; gap: 12px">
        <div style="flex: 1"><label class="muted lbl">Target Waktu</label>
          <InputText v-model="editing.target_waktu" style="width: 100%" /></div>
        <div style="flex: 1"><label class="muted lbl">Realisasi Waktu</label>
          <InputText v-model="editing.realisasi_waktu" style="width: 100%" /></div>
      </div>
    </div>
    <template #footer>
      <Button label="Batal" text @click="dialog = false" />
      <Button label="Simpan" icon="pi pi-check" @click="save" />
    </template>
  </Dialog>
</template>

<style scoped>
.lbl { font-size: 0.8rem; display: block; margin-bottom: 2px; }
.ro-field {
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-2);
  font-size: 0.9rem;
  min-height: 2.25rem;
}
</style>
