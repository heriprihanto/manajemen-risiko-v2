<script setup>
import { onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'

const props = defineProps({
  endpoint: { type: String, required: true },
  // columns: [{ field, label, type:'text'|'textarea'|'select', options|optionsEndpoint, width, hideInTable }]
  columns: { type: Array, required: true },
  title: { type: String, default: '' },
  numbered: { type: Boolean, default: true },
})

const ctx = useContextStore()
const toast = useToast()
const confirm = useConfirm()
const rows = ref([])
const loading = ref(true)
const dialog = ref(false)
const editing = ref({})
const isNew = ref(false)
const dynOptions = ref({}) // field -> [{label, value}] untuk kolom select dinamis

// Opsi kolom select: statis (c.options) atau dinamis dari endpoint.
// Bila kolom `dependsOn`, opsi difilter mengikuti nilai kolom induk (cascading).
function colOptions(c) {
  const opts = c.options || dynOptions.value[c.field] || []
  if (!c.dependsOn) return opts
  const parent = editing.value[c.dependsOn]
  if (!parent) return []
  const key = c.dependsMatch || c.dependsOn
  return opts.filter((o) => o[key] === parent)
}

// Saat kolom induk berubah, kosongkan kolom yang bergantung padanya.
function onSelectChange(c) {
  props.columns.forEach((x) => {
    if (x.dependsOn === c.field) editing.value[x.field] = null
  })
}

async function loadDynOptions() {
  const cols = props.columns.filter((c) => c.optionsEndpoint)
  await Promise.all(
    cols.map(async (c) => {
      try {
        const { data } = await api.get(c.optionsEndpoint, {
          params: { opd_id: ctx.opdId, tahun: ctx.tahun },
        })
        dynOptions.value[c.field] = data
      } catch {
        dynOptions.value[c.field] = []
      }
    }),
  )
}

async function load() {
  loading.value = true
  const [{ data }] = await Promise.all([
    api.get(props.endpoint, { params: { opd_id: ctx.opdId, tahun: ctx.tahun } }),
    loadDynOptions(),
  ])
  rows.value = data
  loading.value = false
}

function openNew() {
  editing.value = {}
  props.columns.forEach((c) => (editing.value[c.field] = null))
  isNew.value = true
  dialog.value = true
}
function openEdit(row) {
  editing.value = { ...row }
  isNew.value = false
  dialog.value = true
}

async function save() {
  const payload = { ...editing.value, opd_id: ctx.opdId, tahun: ctx.tahun }
  if (isNew.value) await api.post(props.endpoint, payload)
  else await api.put(`${props.endpoint}/${editing.value.id}`, payload)
  dialog.value = false
  await load()
  toast.add({ severity: 'success', summary: 'Tersimpan', life: 1800 })
}

function remove(row) {
  confirm.require({
    message: 'Hapus baris ini?',
    header: 'Konfirmasi',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      await api.delete(`${props.endpoint}/${row.id}`)
      await load()
    },
  })
}

defineExpose({ load })
onMounted(load)
</script>

<template>
  <div>
    <div class="toolbar">
      <span class="muted">{{ ctx.opd?.nama_pd }} — {{ ctx.tahun }}</span>
      <div class="spacer" />
      <Button label="Tambah" icon="pi pi-plus" size="small" @click="openNew" />
    </div>

    <div class="page-card" style="padding: 0">
      <DataTable :value="rows" :loading="loading" size="small" stripedRows scrollable>
        <Column v-if="numbered" header="No" :style="{ width: '48px' }">
          <template #body="{ index }">{{ index + 1 }}</template>
        </Column>
        <Column
          v-for="c in columns.filter((x) => !x.hideInTable)"
          :key="c.field"
          :field="c.field"
          :header="c.label"
          :style="c.width ? { minWidth: c.width } : {}"
        >
          <template #body="{ data }">
            <span v-if="c.type === 'select'">
              {{ (colOptions(c).find((o) => o.value === data[c.field]) || {}).label || data[c.field] }}
            </span>
            <span v-else>{{ data[c.field] }}</span>
          </template>
        </Column>
        <Column header="" :style="{ width: '90px' }">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" text rounded size="small" @click="openEdit(data)" />
            <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="remove(data)" />
          </template>
        </Column>
        <template #empty><div class="muted" style="padding: 14px">Belum ada data.</div></template>
      </DataTable>
    </div>

    <Dialog v-model:visible="dialog" :header="title || 'Data'" modal style="width: 640px">
      <div style="display: flex; flex-direction: column; gap: 12px; padding-top: 6px">
        <div v-for="c in columns" :key="c.field">
          <label class="muted" style="font-size: 0.82rem">{{ c.label }}</label>
          <Textarea
            v-if="c.type === 'textarea'"
            v-model="editing[c.field]"
            autoResize
            rows="2"
            style="width: 100%"
          />
          <Select
            v-else-if="c.type === 'select'"
            v-model="editing[c.field]"
            :options="colOptions(c)"
            optionLabel="label"
            optionValue="value"
            :editable="c.editable"
            filter
            showClear
            :placeholder="c.placeholder || 'Pilih…'"
            :disabled="c.dependsOn && !editing[c.dependsOn]"
            style="width: 100%"
            @change="onSelectChange(c)"
          />
          <InputText v-else v-model="editing[c.field]" style="width: 100%" />
        </div>
      </div>
      <template #footer>
        <Button label="Batal" text @click="dialog = false" />
        <Button label="Simpan" icon="pi pi-check" @click="save" />
      </template>
    </Dialog>
  </div>
</template>
