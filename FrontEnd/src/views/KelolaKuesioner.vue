<script setup>
import { computed, onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import ToggleSwitch from 'primevue/toggleswitch'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'

const toast = useToast()
const confirm = useConfirm()
const kategori = ref([])
const loading = ref(true)
const dialog = ref(false)
const editing = ref({})
const isNew = ref(false)

const totalAktif = computed(() =>
  kategori.value.reduce((n, k) => n + k.pertanyaan.filter((p) => p.aktif).length, 0),
)
const totalSemua = computed(() =>
  kategori.value.reduce((n, k) => n + k.pertanyaan.length, 0),
)

async function load() {
  loading.value = true
  const { data } = await api.get('/master/kuesioner/manage')
  kategori.value = data
  loading.value = false
}

function openNew(kat) {
  isNew.value = true
  editing.value = { kategori_id: kat.id, kategori_nama: `${kat.kode}. ${kat.nama}`, nomor: '', pertanyaan: '', urutan: (kat.pertanyaan.at(-1)?.urutan || 0) + 1, aktif: true }
  dialog.value = true
}
function openEdit(kat, row) {
  isNew.value = false
  editing.value = { ...row, kategori_nama: `${kat.kode}. ${kat.nama}`, aktif: !!row.aktif }
  dialog.value = true
}

async function save() {
  const body = {
    kategori_id: editing.value.kategori_id,
    nomor: editing.value.nomor,
    pertanyaan: editing.value.pertanyaan,
    urutan: editing.value.urutan,
    aktif: editing.value.aktif,
  }
  try {
    if (isNew.value) await api.post('/master/kuesioner/pertanyaan', body)
    else await api.put(`/master/kuesioner/pertanyaan/${editing.value.id}`, body)
    dialog.value = false
    await load()
    toast.add({ severity: 'success', summary: 'Pertanyaan tersimpan', life: 1500 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal menyimpan', detail: e?.response?.data?.detail, life: 3500 })
  }
}

async function togglePublish(row) {
  const target = !row.aktif
  try {
    await api.put(`/master/kuesioner/pertanyaan/${row.id}`, { aktif: target })
    row.aktif = target ? 1 : 0
    toast.add({ severity: 'success', summary: target ? 'Dipublish' : 'Di-unpublish', life: 1200 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e?.response?.data?.detail, life: 3000 })
  }
}

function confirmDelete(row) {
  confirm.require({
    message: `Hapus pertanyaan "${row.nomor || row.pertanyaan.slice(0, 40)}"? Tindakan ini tidak bisa dibatalkan.`,
    header: 'Hapus Pertanyaan',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/master/kuesioner/pertanyaan/${row.id}`)
        await load()
        toast.add({ severity: 'success', summary: 'Pertanyaan dihapus', life: 1500 })
      } catch (e) {
        toast.add({ severity: 'warn', summary: 'Tidak bisa dihapus', detail: e?.response?.data?.detail, life: 4000 })
      }
    },
  })
}

onMounted(load)
</script>

<template>
  <p class="muted" style="margin-top: 0">
    Kelola daftar pertanyaan kuesioner CEE. Hanya pertanyaan yang <strong>dipublish</strong>
    (aktif) yang muncul di Survei Publik dan Form 1.a.
  </p>

  <div class="stat-grid" style="margin-bottom: 18px">
    <div class="stat"><div class="v">{{ totalSemua }}</div><div class="l">Total Pertanyaan</div></div>
    <div class="stat"><div class="v" style="color: #16a34a">{{ totalAktif }}</div><div class="l">Dipublish (Aktif)</div></div>
    <div class="stat"><div class="v" style="color: #94a3b8">{{ totalSemua - totalAktif }}</div><div class="l">Draft (Belum Dipublish)</div></div>
    <div class="stat"><div class="v">{{ kategori.length }}</div><div class="l">Sub-unsur</div></div>
  </div>

  <div v-for="kat in kategori" :key="kat.id" class="page-card" style="margin-bottom: 16px; padding: 0">
    <div class="kat-head">
      <div><span class="kat-kode">{{ kat.kode }}</span> {{ kat.nama }}
        <span class="muted" style="font-weight: 400">({{ kat.pertanyaan.filter((p) => p.aktif).length }}/{{ kat.pertanyaan.length }} dipublish)</span>
      </div>
      <Button label="Tambah" icon="pi pi-plus" size="small" outlined @click="openNew(kat)" />
    </div>
    <DataTable :value="kat.pertanyaan" :loading="loading" size="small" stripedRows>
      <Column field="nomor" header="No" :style="{ width: '70px' }" />
      <Column field="pertanyaan" header="Pertanyaan" :style="{ minWidth: '340px' }" />
      <Column field="urutan" header="Urutan" :style="{ width: '80px' }" bodyClass="c" />
      <Column header="Publish" :style="{ width: '110px' }">
        <template #body="{ data }">
          <div style="display: flex; align-items: center; gap: 8px">
            <ToggleSwitch :modelValue="!!data.aktif" @update:modelValue="togglePublish(data)" />
            <Tag v-if="data.aktif" value="Live" severity="success" />
            <Tag v-else value="Draft" severity="secondary" />
          </div>
        </template>
      </Column>
      <Column header="" :style="{ width: '96px' }">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" text rounded size="small" @click="openEdit(kat, data)" />
          <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="confirmDelete(data)" />
        </template>
      </Column>
      <template #empty><div class="muted" style="padding: 12px">Belum ada pertanyaan pada sub-unsur ini.</div></template>
    </DataTable>
  </div>

  <Dialog v-model:visible="dialog" :header="isNew ? 'Tambah Pertanyaan' : 'Edit Pertanyaan'" modal style="width: 620px">
    <div style="display: flex; flex-direction: column; gap: 12px">
      <div><label class="lbl muted">Sub-unsur</label>
        <div class="ro-field">{{ editing.kategori_nama }}</div></div>
      <div style="display: flex; gap: 12px">
        <div style="width: 120px"><label class="lbl muted">Nomor</label>
          <InputText v-model="editing.nomor" style="width: 100%" placeholder="mis. 1" /></div>
        <div style="width: 120px"><label class="lbl muted">Urutan</label>
          <InputNumber v-model="editing.urutan" :min="0" showButtons style="width: 100%" /></div>
      </div>
      <div><label class="lbl muted">Teks Pertanyaan</label>
        <Textarea v-model="editing.pertanyaan" autoResize rows="3" style="width: 100%" /></div>
      <div style="display: flex; align-items: center; gap: 10px">
        <ToggleSwitch v-model="editing.aktif" inputId="aktif-sw" />
        <label for="aktif-sw">Publish (tampilkan di survei &amp; Form 1.a)</label>
      </div>
    </div>
    <template #footer>
      <Button label="Batal" text @click="dialog = false" />
      <Button label="Simpan" icon="pi pi-check" @click="save" />
    </template>
  </Dialog>
</template>

<style scoped>
.kat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  font-weight: 600;
  background: #eff6ff;
  border-bottom: 1px solid var(--border);
  border-radius: 12px 12px 0 0;
}
.kat-kode {
  display: inline-block;
  min-width: 22px;
  text-align: center;
  font-weight: 700;
  color: #1d4ed8;
}
.lbl { font-size: 0.8rem; display: block; margin-bottom: 3px; }
.ro-field {
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-2);
  font-size: 0.9rem;
}
:deep(td.c) { text-align: center; }
</style>
