<script setup>
import { onMounted, ref } from 'vue'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const toast = useToast()
const model = ref({})
const options = ref({})
const loading = ref(true)
const saving = ref(false)

// Seluruh isian dipilih dari data RPJMD/referensi; field `multi` boleh lebih
// dari satu pilihan dan disimpan sebagai teks yang dipisah newline.
const fields = [
  { key: 'periode_dinilai', label: 'Periode yang Dinilai', endpoint: '/master/rpjmd/periode' },
  { key: 'visi', label: 'Visi', endpoint: '/master/rpjmd/visi' },
  { key: 'misi_strategis', label: 'Misi Strategis RPJMD', endpoint: '/master/rpjmd/misi', multi: true },
  {
    key: 'penetapan_konteks_tujuan',
    label: 'Penetapan Konteks Tujuan Risiko Strategis Pemda',
    endpoint: '/master/rpjmd/tujuan',
    multi: true,
  },
  {
    key: 'penetapan_konteks_sasaran',
    label: 'Penetapan Konteks Sasaran Risiko Strategis Pemda',
    endpoint: '/master/rpjmd/sasaran',
    multi: true,
  },
  {
    key: 'penetapan_konteks_iku',
    label: 'Penetapan Konteks IKU Risiko Strategis Pemda',
    endpoint: '/master/rpjmd/iku',
    multi: true,
  },
  {
    key: 'prioritas_pembangunan',
    label: 'Prioritas Pembangunan Daerah',
    endpoint: '/master/ref/prioritas',
    multi: true,
  },
  { key: 'prioritas_program', label: 'Program Prioritas', endpoint: '/master/rpjmd/program', multi: true },
]

const toList = (v) => (v ? String(v).split('\n').filter(Boolean) : [])

// Nilai tersimpan yang tidak ada di daftar opsi (mis. entri bebas sebelum
// revisi, atau data RPJMD yang berubah) tetap ditampilkan agar tidak hilang
// diam-diam saat form disimpan ulang.
function withStored(opts, stored) {
  const known = new Set(opts.map((o) => o.value))
  const extra = stored.filter((v) => !known.has(v)).map((v) => ({ value: v, label: v }))
  return [...opts, ...extra]
}

async function load() {
  loading.value = true
  const { data } = await api.get('/konteks/pemda', { params: { tahun: ctx.tahun } })
  const saved = data || {}
  const lists = await Promise.all(
    fields.map((f) =>
      api
        .get(f.endpoint, { params: { tahun: ctx.tahun } })
        .then((r) => r.data || [])
        .catch(() => []),
    ),
  )
  const next = {}
  const opts = {}
  fields.forEach((f, i) => {
    const stored = f.multi ? toList(saved[f.key]) : [saved[f.key]].filter(Boolean)
    next[f.key] = f.multi ? stored : saved[f.key] || null
    opts[f.key] = withStored(lists[i], stored)
  })
  model.value = next
  options.value = opts
  loading.value = false
}

async function save() {
  saving.value = true
  try {
    const payload = { tahun: ctx.tahun }
    for (const f of fields) {
      const v = model.value[f.key]
      payload[f.key] = f.multi ? (v || []).join('\n') || null : v || null
    }
    await api.post('/konteks/pemda', payload)
    toast.add({ severity: 'success', summary: 'Konteks Pemda tersimpan', life: 2000 })
    await load()
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page-card">
    <p class="muted" style="margin-top: 0">
      Penetapan konteks risiko strategis Pemerintah Daerah — berlaku untuk seluruh OPD pada
      Tahun {{ ctx.tahun }}. Pilihan diambil dari data RPJMD.
    </p>

    <AppLoader v-if="loading" label="Memuat pilihan RPJMD…" />

    <template v-else>
      <!-- minmax(0,1fr): kolom tidak boleh ikut melebar mengikuti isi pilihan -->
      <div style="display: grid; grid-template-columns: minmax(0, 1fr); gap: 14px">
        <div v-for="f in fields" :key="f.key">
          <label class="muted" style="font-size: 0.82rem">{{ f.label }}</label>
          <!-- `induk` (tujuan/sasaran RPJMD induk) hanya ada pada opsi sasaran
               & IKU; ditampilkan sebagai baris kedua di daftar pilihan. -->
          <MultiSelect
            v-if="f.multi"
            v-model="model[f.key]"
            :options="options[f.key]"
            optionLabel="label"
            optionValue="value"
            display="chip"
            filter
            :placeholder="`Pilih ${f.label.toLowerCase()}`"
            :maxSelectedLabels="99"
            style="width: 100%"
          >
            <template #option="{ option }">
              <div>
                <div>{{ option.label }}</div>
                <small v-if="option.induk" class="muted">
                  {{ option.induk_jenis }}: {{ option.induk }}
                </small>
              </div>
            </template>
          </MultiSelect>
          <Select
            v-else
            v-model="model[f.key]"
            :options="options[f.key]"
            optionLabel="label"
            optionValue="value"
            filter
            showClear
            :placeholder="`Pilih ${f.label.toLowerCase()}`"
            style="width: 100%"
          />
        </div>
      </div>

      <div style="margin-top: 16px">
        <Button label="Simpan" icon="pi pi-check" :loading="saving" @click="save" />
      </div>
    </template>
  </div>
</template>
