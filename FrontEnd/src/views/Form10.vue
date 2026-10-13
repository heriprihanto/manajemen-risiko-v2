<script setup>
import { onMounted, ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import DatePicker from 'primevue/datepicker'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { formatDate, parseDateOnly, toDateOnlyString } from '@/utils/date'

const ctx = useContextStore()
const toast = useToast()
const confirm = useConfirm()
const list = ref([])
const dialog = ref(false)
const editing = ref({})
const current = ref(null)
const tanggal = ref(null)

async function load() {
  const { data } = await api.get('/monitoring/risk-event', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  list.value = data
}
function openNew(risiko) {
  current.value = risiko
  editing.value = { risiko_id: risiko.risiko_id }
  tanggal.value = null
  dialog.value = true
}
function openEdit(risiko, ev) {
  current.value = risiko
  editing.value = { ...ev }
  tanggal.value = ev.tanggal_terjadi ? parseDateOnly(ev.tanggal_terjadi) : null
  dialog.value = true
}
async function save() {
  const payload = {
    ...editing.value,
    risiko_id: current.value.risiko_id,
    tanggal_terjadi: toDateOnlyString(tanggal.value),
  }
  if (editing.value.id) await api.put(`/monitoring/risk-event/${editing.value.id}`, payload)
  else await api.post('/monitoring/risk-event', payload)
  dialog.value = false
  await load()
  toast.add({ severity: 'success', summary: 'Kejadian risiko tersimpan', life: 1600 })
}
function remove(ev) {
  confirm.require({
    message: 'Hapus catatan kejadian ini?',
    header: 'Konfirmasi',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      await api.delete(`/monitoring/risk-event/${ev.id}`)
      await load()
    },
  })
}
onMounted(load)
</script>

<template>
  <p class="muted" style="margin-top: 0">Pencatatan kejadian risiko (risk event) dan pelaksanaan RTP per risiko teridentifikasi.</p>
  <div v-for="r in list" :key="r.risiko_id" class="page-card" style="margin-bottom: 12px">
    <div style="display: flex; align-items: center; gap: 10px">
      <span class="pill" style="background: #e0e7ff; color: #3730a3">{{ r.kode_risiko || '—' }}</span>
      <strong style="flex: 1">{{ r.uraian_risiko }}</strong>
      <Button label="Catat Kejadian" icon="pi pi-plus" size="small" text @click="openNew(r)" />
    </div>
    <table v-if="r.events.length" class="grid-table" style="margin-top: 10px">
      <thead>
        <tr>
          <th>Tanggal</th><th>Sebab</th><th>Dampak</th><th>RTP</th><th>Realisasi RTP</th><th style="width: 70px"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ev in r.events" :key="ev.id">
          <td>{{ formatDate(ev.tanggal_terjadi) }}</td>
          <td>{{ ev.sebab_kejadian }}</td>
          <td>{{ ev.dampak_kejadian }}</td>
          <td>{{ ev.rtp }}</td>
          <td>{{ ev.realisasi_pelaksanaan_rtp }}</td>
          <td style="text-align: center">
            <Button icon="pi pi-pencil" text rounded size="small" @click="openEdit(r, ev)" />
            <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="remove(ev)" />
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="muted" style="margin-top: 8px; font-size: 0.82rem">Belum ada kejadian dicatat.</div>
  </div>
  <div v-if="!list.length" class="muted">Belum ada risiko teridentifikasi untuk OPD/tahun ini.</div>

  <Dialog v-model:visible="dialog" header="Kejadian Risiko & RTP" modal style="width: 620px">
    <div v-if="current" class="muted" style="margin-bottom: 8px"><strong>{{ current.kode_risiko }}</strong> — {{ current.uraian_risiko }}</div>
    <div style="display: flex; flex-direction: column; gap: 12px">
      <div><label class="muted lbl">Tanggal Terjadi</label>
        <DatePicker v-model="tanggal" dateFormat="yy-mm-dd" showIcon style="width: 100%" /></div>
      <div><label class="muted lbl">Sebab Kejadian</label>
        <Textarea v-model="editing.sebab_kejadian" autoResize rows="2" style="width: 100%" /></div>
      <div><label class="muted lbl">Dampak Kejadian</label>
        <Textarea v-model="editing.dampak_kejadian" autoResize rows="2" style="width: 100%" /></div>
      <div><label class="muted lbl">RTP</label>
        <Textarea v-model="editing.rtp" autoResize rows="2" style="width: 100%" /></div>
      <div style="display: flex; gap: 12px">
        <div style="flex: 1"><label class="muted lbl">Rencana Pelaksanaan RTP</label>
          <InputText v-model="editing.rencana_pelaksanaan_rtp" style="width: 100%" /></div>
        <div style="flex: 1"><label class="muted lbl">Realisasi Pelaksanaan RTP</label>
          <InputText v-model="editing.realisasi_pelaksanaan_rtp" style="width: 100%" /></div>
      </div>
      <div><label class="muted lbl">Keterangan</label>
        <InputText v-model="editing.keterangan_rtp" style="width: 100%" /></div>
    </div>
    <template #footer>
      <Button label="Batal" text @click="dialog = false" />
      <Button label="Simpan" icon="pi pi-check" @click="save" />
    </template>
  </Dialog>
</template>

<style scoped>
.grid-table { border-collapse: collapse; width: 100%; font-size: 0.82rem; }
.grid-table th, .grid-table td { border: 1px solid #e2e8f0; padding: 6px 8px; text-align: left; }
.grid-table thead th { background: #f8fafc; font-weight: 600; }
.lbl { font-size: 0.8rem; display: block; margin-bottom: 2px; }
</style>
