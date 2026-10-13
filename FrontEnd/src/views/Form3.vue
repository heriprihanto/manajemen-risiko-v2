<script setup>
import { computed, onMounted, ref, watch } from 'vue'
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

// Jenis risiko dikunci oleh menu (Form 3.a/3.b/3.c) lewat prop.
const props = defineProps({
  jenis: { type: String, required: true }, // strategis_pemda | strategis_opd | operasional_opd
})

const ctx = useContextStore()
const toast = useToast()
const confirm = useConfirm()

const jenisLabel = {
  strategis_pemda: 'Risiko Strategis Pemda (Form 3.a)',
  strategis_opd: 'Risiko Strategis OPD (Form 3.b)',
  operasional_opd: 'Risiko Operasional OPD (Form 3.c)',
}
const rows = ref([])
const loading = ref(true)
const dialog = ref(false)
const editing = ref({})
const isNew = ref(false)
// Form 2.b — daftar konteks strategis OPD sebagai sumber pilihan Form 3.b.
const konteksOptions = ref([])

// Form 2.a — daftar Penetapan Konteks IKU sebagai sumber pilihan Form 3.a.
const ikuOptions = ref([])

const isOperasional = computed(() => props.jenis === 'operasional_opd')
const isStrategisOpd = computed(() => props.jenis === 'strategis_opd')
const isStrategisPemda = computed(() => props.jenis === 'strategis_pemda')

// Field multi-pilihan Form 2.a disimpan sebagai teks dipisah newline.
const toList = (v) => (v ? String(v).split('\n').filter(Boolean) : [])

// Nilai lama yang tidak (lagi) ada di Form 2.a tetap ditampilkan sebagai opsi
// supaya tidak hilang saat baris risiko disimpan ulang.
const ikuSelectOptions = computed(() => {
  const cur = (editing.value.indikator_kinerja || '').trim()
  if (!cur || ikuOptions.value.some((o) => o.value === cur)) return ikuOptions.value
  return [...ikuOptions.value, { value: cur, label: cur }]
})
const selectedIku = computed(() =>
  ikuOptions.value.find((o) => o.value === editing.value.indikator_kinerja),
)

// IKU Pemda menempel pada tujuan (lvl 1) atau sasaran (lvl 2) RPJMD, jadi
// Tujuan/Sasaran Strategis diturunkan dari IKU yang dipilih (masih bisa
// disunting bila perlu).
function applyIku(e) {
  const iku = ikuOptions.value.find((o) => o.value === e?.value)
  if (iku?.induk) editing.value.tujuan_sasaran = iku.induk
}

// Label ringkas satu baris Form 2.b: pakai penetapan konteks bila diisi,
// jika tidak gabungkan tujuan/sasaran/program.
function konteksLabel(k) {
  if (!k) return ''
  const penetapan = (k.tujuan_sasaran_iku_program || '').trim()
  if (penetapan) return penetapan
  return [k.tujuan_strategis, k.sasaran_strategis, k.program].filter(Boolean).join(' / ')
}
// Kunci gabungan sumber+id supaya pilihan Form 2.b & 2.c tidak bentrok id-nya.
const konteksKey = computed({
  get: () =>
    editing.value.konteks_id != null
      ? `${editing.value.konteks_sumber || 'b'}:${editing.value.konteks_id}`
      : null,
  set: () => {}, // ditulis lewat applyKonteks
})
const selectedKonteks = computed(() =>
  konteksOptions.value.find((k) => k._key === konteksKey.value),
)
// Saat konteks dipilih, turunkan kolom Tujuan/Sasaran & IKU dari sumbernya.
function applyKonteks(e) {
  const key = e?.value ?? null
  const k = konteksOptions.value.find((o) => o._key === key)
  if (!k) {
    editing.value.konteks_id = null
    editing.value.konteks_sumber = null
    editing.value.tujuan_sasaran = null
    editing.value.indikator_kinerja = null
    return
  }
  editing.value.konteks_id = k._id
  editing.value.konteks_sumber = k._source
  if (isOperasional.value) {
    // Form 3.c: konteks = subkegiatan (kegiatan + indikator keluaran) Form 2.c.
    editing.value.kegiatan = k.keluaran_hasil_kegiatan
    editing.value.indikator_keluaran = k.keluaran_sub_kegiatan
  } else if (k._source === 'c') {
    // Indikator program Form 2.c: konteks = program + indikatornya.
    editing.value.tujuan_sasaran = k.program
    editing.value.indikator_kinerja = k.indikator_program
  } else {
    editing.value.tujuan_sasaran = konteksLabel(k)
    editing.value.indikator_kinerja = k.iku_renstra
  }
}

async function load() {
  loading.value = true
  const params = { opd_id: ctx.opdId, tahun: ctx.tahun }
  if (isStrategisOpd.value) {
    const [kb, kc] = await Promise.all([
      api.get('/konteks/strategis-opd', { params }).then((r) => r.data).catch(() => []),
      api.get('/konteks/operasional-opd', { params }).then((r) => r.data).catch(() => []),
    ])
    const opt2b = (kb || []).map((k) => ({
      ...k,
      _id: k.id,
      _source: 'b',
      _key: `b:${k.id}`,
      _label: konteksLabel(k),
    }))
    // Hanya baris indikator program Form 2.c (field indikator_program terisi).
    const opt2c = (kc || [])
      .filter((k) => (k.indikator_program || '').trim())
      .map((k) => ({
        ...k,
        _id: k.id,
        _source: 'c',
        _key: `c:${k.id}`,
        _label: `[Form 2.c] ${[k.program, k.indikator_program].filter(Boolean).join(' — ')}`,
      }))
    konteksOptions.value = [...opt2b, ...opt2c]
  } else if (isOperasional.value) {
    // Form 3.c: subkegiatan yang dicentang di Form 2.c (punya ref_subkegiatan).
    const kc = await api
      .get('/konteks/operasional-opd', { params })
      .then((r) => r.data)
      .catch(() => [])
    konteksOptions.value = (kc || [])
      .filter((k) => (k.ref_subkegiatan || '').toString().trim())
      .map((k) => ({
        ...k,
        _id: k.id,
        _source: 'c',
        _key: `c:${k.id}`,
        _label:
          [k.keluaran_hasil_kegiatan, k.keluaran_sub_kegiatan].filter(Boolean).join(' — ') ||
          k.program ||
          '(subkegiatan)',
      }))
  } else if (isStrategisPemda.value) {
    // Form 3.a: Indikator Kinerja dipilih dari Penetapan Konteks IKU Form 2.a
    // (konteks Pemda berlaku untuk seluruh OPD, jadi hanya difilter per tahun).
    // Daftar master dipakai untuk melengkapi tujuan/sasaran RPJMD induk IKU.
    const [pemda, masterIku] = await Promise.all([
      api.get('/konteks/pemda', { params: { tahun: ctx.tahun } })
        .then((r) => r.data).catch(() => null),
      api.get('/master/rpjmd/iku', { params: { tahun: ctx.tahun } })
        .then((r) => r.data).catch(() => []),
    ])
    const byValue = new Map((masterIku || []).map((m) => [m.value, m]))
    ikuOptions.value = toList(pemda?.penetapan_konteks_iku).map(
      (v) => byValue.get(v) || { value: v, label: v },
    )
  }
  const { data } = await api.get('/risiko', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun, jenis: props.jenis },
  })
  rows.value = data
  loading.value = false
}

// Master Bidang Urusan (ref_bidang_urusan)
const bidangUrusanList = ref([])
const bidangUrusanOptions = computed(() =>
  bidangUrusanList.value.map((b) => ({
    id: b.id,
    label: `${b.kode_risk} — ${b.bidang_urusan_alias || b.nama_bidang_urusan}`,
    kode_risk: b.kode_risk,
    kode_bidang_urusan: b.kode_bidang_urusan,
    nama_bidang_urusan: b.nama_bidang_urusan,
    bidang_urusan_alias: b.bidang_urusan_alias,
  }))
)

async function loadBidangUrusan() {
  try {
    const { data } = await api.get('/master/bidang-urusan')
    bidangUrusanList.value = data || []
  } catch (err) {
    console.error('Gagal memuat master bidang urusan:', err)
  }
}

// Generate format Kode Risiko:
// Form 3.a (Strategis Pemda) : RSP.26.01.02.05.001
// Form 3.b (Strategis OPD)   : RSO.26.02.02.05.001
// Form 3.c (Operasional OPD) : ROO.26.03.02.05.001
function generateKodeRisiko(buKodeRisk) {
  if (!buKodeRisk) return ''
  const jenisPrefix = isOperasional.value ? 'ROO' : isStrategisOpd.value ? 'RSO' : 'RSP'
  const jenisCode = isOperasional.value ? '03' : isStrategisOpd.value ? '02' : '01'
  const tahun2 = String(ctx.tahun || 2026).slice(-2)
  const buCode = String(buKodeRisk).padStart(2, '0')
  const opdCode = String(ctx.opd?.kode_risk || (isStrategisPemda.value ? '01' : '00')).padStart(2, '0')
  const prefix = `${jenisPrefix}.${tahun2}.${jenisCode}.${buCode}.${opdCode}.`

  let maxSeq = 0
  for (const r of rows.value) {
    if (r.kode_risiko && r.kode_risiko.startsWith(prefix)) {
      const seqStr = r.kode_risiko.slice(prefix.length)
      const seq = parseInt(seqStr, 10)
      if (!isNaN(seq) && seq > maxSeq) {
        maxSeq = seq
      }
    }
  }
  const nextSeq = String(maxSeq + 1).padStart(3, '0')
  return `${prefix}${nextSeq}`
}

function onBidangUrusanChange(e) {
  const selectedId = e?.value ?? editing.value.id_bidang_urusan
  const bu = bidangUrusanList.value.find((b) => b.id === selectedId)
  if (bu) {
    editing.value.kode_risiko = generateKodeRisiko(bu.kode_risk)
  }
}

function openNew() {
  editing.value = { jenis_risiko: props.jenis, sebab_sumber: 'Internal', cuc: 'C', keterangan_risiko: '' }
  let defaultBu = null
  if (ctx.opd?.kode) {
    defaultBu = bidangUrusanList.value.find((b) =>
      ctx.opd.kode.startsWith(b.kode_bidang_urusan + '.')
    )
  }
  if (!defaultBu && bidangUrusanList.value.length) {
    defaultBu = bidangUrusanList.value[0]
  }
  if (defaultBu) {
    editing.value.id_bidang_urusan = defaultBu.id
    editing.value.kode_risiko = generateKodeRisiko(defaultBu.kode_risk)
  }
  isNew.value = true
  dialog.value = true
}
function openEdit(r) {
  editing.value = { ...r }
  isNew.value = false
  dialog.value = true
}
async function save() {
  const uraian = (editing.value.uraian_risiko || '').trim()
  if (!uraian) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Uraian Risiko wajib dipilih dari Kamus Risiko',
      life: 3000,
    })
    return
  }

  const isInKamus = kamusList.value.some(
    (k) => k.nama_risiko.trim().toLowerCase() === uraian.toLowerCase()
  )
  if (!isInKamus) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Uraian Risiko harus dipilih dari daftar Kamus Risiko yang tersedia (tidak bisa mengetik sendiri)',
      life: 3500,
    })
    return
  }

  const payload = { ...editing.value, opd_id: ctx.opdId, tahun: ctx.tahun }
  if (isNew.value) await api.post('/risiko', payload)
  else await api.put(`/risiko/${editing.value.id}`, payload)
  dialog.value = false
  await load()
  toast.add({ severity: 'success', summary: 'Risiko tersimpan', life: 1800 })
}
const kamusList = ref([])
const selectedKamusItem = computed(() =>
  kamusList.value.find(
    (k) => k.nama_risiko.trim().toLowerCase() === (editing.value?.uraian_risiko || '').trim().toLowerCase()
  )
)

const kamusOptions = computed(() => {
  const list = kamusList.value.map((k) => ({
    label: `${k.kode_risiko ? k.kode_risiko + ' — ' : ''}${k.nama_risiko}`,
    value: k.nama_risiko,
    kode: k.kode_risiko,
    kategori: k.kategori_risiko,
    nama: k.nama_risiko,
    deskripsi: k.deskripsi,
  }))
  if (
    editing.value?.uraian_risiko &&
    !list.some((item) => item.value === editing.value.uraian_risiko)
  ) {
    list.unshift({
      label: `[Belum dari Kamus] ${editing.value.uraian_risiko}`,
      value: editing.value.uraian_risiko,
      kode: 'MANUAL',
      kategori: editing.value.kategori_risiko || 'Lainnya',
      nama: editing.value.uraian_risiko,
      deskripsi: editing.value.keterangan_risiko || '',
      isLegacy: true,
    })
  }
  return list
})

async function loadKamus() {
  try {
    const { data } = await api.get('/kamus-risiko', {
      params: { all_data: true, aktif: 1 },
    })
    kamusList.value = data.items || []
  } catch (err) {
    console.error('Gagal memuat kamus risiko:', err)
  }
}

function onKamusSelect(e) {
  const val = e?.value ?? editing.value.uraian_risiko
  const item = kamusList.value.find(
    (k) => k.nama_risiko === val || `${k.kode_risiko} — ${k.nama_risiko}` === val,
  )
  if (item) {
    editing.value.uraian_risiko = item.nama_risiko
    editing.value.kategori_risiko = item.kategori_risiko
    if (!editing.value.kode_risiko) {
      editing.value.kode_risiko = item.kode_risiko
    }
    if (item.deskripsi && !editing.value.keterangan_risiko) {
      editing.value.keterangan_risiko = item.deskripsi
    }
  }
}

watch(
  () => editing.value.uraian_risiko,
  (val) => {
    if (!val) return
    const item = kamusList.value.find(
      (k) => k.nama_risiko === val || `${k.kode_risiko} — ${k.nama_risiko}` === val,
    )
    if (item && item.kategori_risiko) {
      editing.value.kategori_risiko = item.kategori_risiko
    }
  },
)

function remove(r) {
  confirm.require({
    message: `Hapus risiko "${r.uraian_risiko || ''}"?`,
    header: 'Konfirmasi',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      await api.delete(`/risiko/${r.id}`)
      await load()
    },
  })
}
onMounted(() => {
  load()
  loadBidangUrusan()
  loadKamus()
})
watch(() => [ctx.opdId, ctx.tahun, props.jenis], load)
</script>

<template>
  <div class="toolbar">
    <span class="muted">{{ jenisLabel[jenis] }} — {{ ctx.opd?.nama_pd }} — {{ ctx.tahun }}</span>
    <div class="spacer" />
    <Button label="Tambah Identifikasi Risiko" icon="pi pi-plus" size="small" @click="openNew" />
  </div>

  <div class="page-card" style="padding: 0">
    <DataTable :value="rows" :loading="loading" size="small" stripedRows scrollable>
      <Column header="No" :style="{ width: '46px' }">
        <template #body="{ index }">{{ index + 1 }}</template>
      </Column>
      <Column field="kode_risiko" header="Kode" :style="{ minWidth: '150px' }">
        <template #body="{ data }">
          <span class="code-badge-sm">{{ data.kode_risiko || '—' }}</span>
        </template>
      </Column>
      <Column header="Bidang Urusan" :style="{ minWidth: '180px' }">
        <template #body="{ data }">
          <span v-if="data.bidang_urusan">
            <span class="code-badge-sm" style="margin-right: 4px;">{{ data.bidang_urusan.kode_risk }}</span>
            {{ data.bidang_urusan.bidang_urusan_alias || data.bidang_urusan.nama_bidang_urusan }}
          </span>
          <span v-else class="muted">—</span>
        </template>
      </Column>
      <Column :header="isOperasional ? 'Kegiatan' : 'Tujuan/Sasaran'" :style="{ minWidth: '180px' }">
        <template #body="{ data }">{{ data.kegiatan || data.tujuan_sasaran }}</template>
      </Column>
      <Column field="uraian_risiko" header="Risiko" :style="{ minWidth: '240px' }">
        <template #body="{ data }">
          <div style="font-weight: 500;">{{ data.uraian_risiko }}</div>
          <div v-if="data.keterangan_risiko" class="muted" style="font-size: 0.78rem; margin-top: 4px; line-height: 1.35; white-space: pre-line;">
            {{ data.keterangan_risiko }}
          </div>
        </template>
      </Column>
      <Column field="kategori_risiko" header="Kategori" :style="{ minWidth: '140px' }">
        <template #body="{ data }">
          <span v-if="data.kategori_risiko" class="category-tag-sm">
            {{ data.kategori_risiko }}
          </span>
          <span v-else class="muted">—</span>
        </template>
      </Column>
      <Column field="pemilik_risiko" header="Pemilik" :style="{ minWidth: '130px' }" />
      <Column field="sebab_uraian" header="Sebab" :style="{ minWidth: '180px' }" />
      <Column field="cuc" header="Status (C/UC)" :style="{ width: '70px' }" />
      <Column field="dampak_uraian" header="Dampak" :style="{ minWidth: '180px' }" />
      <Column header="" :style="{ width: '90px' }">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" text rounded size="small" @click="openEdit(data)" />
          <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="remove(data)" />
        </template>
      </Column>
      <template #empty><div class="muted" style="padding: 14px">Belum ada risiko untuk jenis ini.</div></template>
    </DataTable>
  </div>

  <Dialog v-model:visible="dialog" :header="jenisLabel[jenis]" modal style="width: 720px">
    <div class="grid-2" style="gap: 12px; padding-top: 6px">
      <template v-if="isOperasional">
        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Bidang Urusan</label>
          <Select
            v-model="editing.id_bidang_urusan"
            :options="bidangUrusanOptions"
            optionLabel="label"
            optionValue="id"
            filter
            filterPlaceholder="Cari bidang urusan..."
            placeholder="Pilih Bidang Urusan"
            style="width: 100%"
            @change="onBidangUrusanChange"
          >
            <template #option="{ option }">
              <div style="display: flex; flex-direction: column; gap: 2px;">
                <div style="font-weight: 500;">
                  <span class="code-badge-sm" style="margin-right: 6px;">{{ option.kode_risk }}</span>
                  {{ option.bidang_urusan_alias || option.nama_bidang_urusan }}
                </div>
                <small v-if="option.bidang_urusan_alias" class="muted" style="font-size: 0.75rem;">
                  {{ option.kode_bidang_urusan }} — {{ option.nama_bidang_urusan }}
                </small>
              </div>
            </template>
          </Select>
        </div>
        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Indikator Subkegiatan (dari Form 2.c)</label>
          <Select
            :modelValue="konteksKey"
            :options="konteksOptions"
            optionLabel="_label"
            optionValue="_key"
            filter
            placeholder="Pilih subkegiatan yang dinilai"
            style="width: 100%"
            @change="applyKonteks"
          />
          <small v-if="!konteksOptions.length" class="muted">
            Belum ada subkegiatan dipilih pada Form 2.c — Konteks Operasional OPD untuk OPD & tahun ini.
          </small>
        </div>
        <div v-if="selectedKonteks" style="grid-column: 1 / -1" class="konteks-ref">
          <div><span class="muted">Program:</span> {{ selectedKonteks.program || '—' }}</div>
          <div><span class="muted">Kegiatan:</span> {{ selectedKonteks.keluaran_hasil_kegiatan || '—' }}</div>
          <div><span class="muted">Indikator Subkegiatan:</span> {{ selectedKonteks.keluaran_sub_kegiatan || '—' }}</div>
        </div>
        <div>
          <label class="muted lbl">Tahap Kegiatan</label>
          <Select
            v-model="editing.tahap_kegiatan"
            :options="['Pelaksanaan', 'Pertanggungjawaban']"
            placeholder="Pilih tahap"
            style="width: 100%"
          />
        </div>
      </template>
      <template v-else-if="isStrategisOpd">
        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Bidang Urusan</label>
          <Select
            v-model="editing.id_bidang_urusan"
            :options="bidangUrusanOptions"
            optionLabel="label"
            optionValue="id"
            filter
            filterPlaceholder="Cari bidang urusan..."
            placeholder="Pilih Bidang Urusan"
            style="width: 100%"
            @change="onBidangUrusanChange"
          >
            <template #option="{ option }">
              <div style="display: flex; flex-direction: column; gap: 2px;">
                <div style="font-weight: 500;">
                  <span class="code-badge-sm" style="margin-right: 6px;">{{ option.kode_risk }}</span>
                  {{ option.bidang_urusan_alias || option.nama_bidang_urusan }}
                </div>
                <small v-if="option.bidang_urusan_alias" class="muted" style="font-size: 0.75rem;">
                  {{ option.kode_bidang_urusan }} — {{ option.nama_bidang_urusan }}
                </small>
              </div>
            </template>
          </Select>
        </div>

        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Tujuan/Sasaran/IKU/Program (dari Form 2.b)</label>
          <Select
            :modelValue="konteksKey"
            :options="konteksOptions"
            optionLabel="_label"
            optionValue="_key"
            filter
            placeholder="Pilih konteks (Form 2.b / indikator program Form 2.c)"
            style="width: 100%"
            @change="applyKonteks"
          />
          <small v-if="!konteksOptions.length" class="muted">
            Belum ada data pada Form 2.b / Form 2.c untuk OPD & tahun ini.
          </small>
        </div>
        <div v-if="selectedKonteks" style="grid-column: 1 / -1" class="konteks-ref">
          <div>
            <span class="muted">Sumber:</span>
            {{ selectedKonteks._source === 'c' ? 'Form 2.c — Indikator Program' : 'Form 2.b — Konteks Strategis OPD' }}
          </div>
          <template v-if="selectedKonteks._source === 'c'">
            <div><span class="muted">Program:</span> {{ selectedKonteks.program || '—' }}</div>
            <div><span class="muted">Indikator Program:</span> {{ selectedKonteks.indikator_program || '—' }}</div>
          </template>
          <template v-else>
            <div><span class="muted">Tujuan:</span> {{ selectedKonteks.tujuan_strategis || '—' }}</div>
            <div><span class="muted">Sasaran:</span> {{ selectedKonteks.sasaran_strategis || '—' }}</div>
            <div><span class="muted">IKU Renstra:</span> {{ selectedKonteks.iku_renstra || '—' }}</div>
            <div><span class="muted">Program:</span> {{ selectedKonteks.program || '—' }}</div>
          </template>
        </div>
      </template>
      <template v-else>
        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Bidang Urusan</label>
          <Select
            v-model="editing.id_bidang_urusan"
            :options="bidangUrusanOptions"
            optionLabel="label"
            optionValue="id"
            filter
            filterPlaceholder="Cari bidang urusan..."
            placeholder="Pilih Bidang Urusan"
            style="width: 100%"
            @change="onBidangUrusanChange"
          >
            <template #option="{ option }">
              <div style="display: flex; flex-direction: column; gap: 2px;">
                <div style="font-weight: 500;">
                  <span class="code-badge-sm" style="margin-right: 6px;">{{ option.kode_risk }}</span>
                  {{ option.bidang_urusan_alias || option.nama_bidang_urusan }}
                </div>
                <small v-if="option.bidang_urusan_alias" class="muted" style="font-size: 0.75rem;">
                  {{ option.kode_bidang_urusan }} — {{ option.nama_bidang_urusan }}
                </small>
              </div>
            </template>
          </Select>
        </div>
        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Indikator Kinerja (dari Form 2.a)</label>
          <Select
            v-model="editing.indikator_kinerja"
            :options="ikuSelectOptions"
            optionLabel="label"
            optionValue="value"
            filter
            showClear
            placeholder="Pilih IKU yang dinilai"
            style="width: 100%"
            @change="applyIku"
          >
            <template #option="{ option }">
              <div>
                <div>{{ option.label }}</div>
                <small v-if="option.induk" class="muted">
                  {{ option.induk_jenis }}: {{ option.induk }}
                </small>
              </div>
            </template>
          </Select>
          <small v-if="!ikuOptions.length" class="muted">
            Belum ada Penetapan Konteks IKU pada Form 2.a — Konteks Strategis Pemda untuk tahun ini.
          </small>
        </div>
        <div v-if="selectedIku?.induk" style="grid-column: 1 / -1" class="konteks-ref">
          <div>
            <span class="muted">{{ selectedIku.induk_jenis }} RPJMD:</span> {{ selectedIku.induk }}
          </div>
        </div>
        <div style="grid-column: 1 / -1">
          <label class="muted lbl">Tujuan/Sasaran Strategis</label>
          <Textarea v-model="editing.tujuan_sasaran" autoResize rows="2" style="width: 100%" />
        </div>
      </template>
      <div style="grid-column: 1 / -1">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <label class="muted lbl" style="margin-bottom: 0;">
            Uraian Risiko <span style="color: #ef4444;">*</span>
          </label>
          <small style="font-size: 0.75rem; color: #4f46e5; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
            <i class="pi pi-book" style="font-size: 0.75rem;"></i>
            Pilih dari Kamus Risiko
          </small>
        </div>
        <Select
          v-model="editing.uraian_risiko"
          :options="kamusOptions"
          optionLabel="label"
          optionValue="value"
          filter
          filterPlaceholder="Ketik untuk mencari uraian atau kode di Kamus Risiko..."
          placeholder="Pilih Uraian Risiko dari Kamus..."
          style="width: 100%"
          @change="onKamusSelect"
        >
          <template #value="{ value, placeholder }">
            <div v-if="value" style="display: flex; align-items: center; gap: 8px; max-width: 100%; overflow: hidden;">
              <span v-if="selectedKamusItem?.kode_risiko" class="code-badge-sm">{{ selectedKamusItem.kode_risiko }}</span>
              <span style="font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ value }}</span>
            </div>
            <span v-else class="p-placeholder">{{ placeholder }}</span>
          </template>
          <template #option="{ option }">
            <div class="kamus-option-item">
              <div class="kamus-option-header">
                <span class="code-badge-sm">{{ option.kode }}</span>
                <span class="category-tag-sm">{{ option.kategori }}</span>
              </div>
              <div class="kamus-option-name">{{ option.nama }}</div>
            </div>
          </template>
        </Select>
        <small class="muted" style="font-size: 0.72rem; display: block; margin-top: 3px;">
          Uraian risiko harus dipilih dari Kamus Risiko dan tidak dapat diketik manual.
        </small>
      </div>
      <div style="grid-column: 1 / -1">
        <label class="muted lbl">Keterangan Uraian Risiko</label>
        <InputText
          v-model="editing.keterangan_risiko"
          placeholder="Keterangan atau rincian tambahan uraian risiko (opsional)..."
          style="width: 100%"
        />
      </div>
      <div>
        <label class="muted lbl">Kategori Risiko</label>
        <InputText
          :modelValue="editing.kategori_risiko"
          readonly
          placeholder="Kategori Risiko"
          style="width: 100%; background: var(--p-surface-100, #f4f4f5); cursor: not-allowed;"
        />
        <small class="muted" style="font-size: 0.72rem; display: block; margin-top: 2px;">
          Kategori Risiko
        </small>
      </div>
      <div>
        <label class="muted lbl">Kode Risiko</label>
        <InputText
          v-model="editing.kode_risiko"
          :placeholder="isOperasional ? 'Contoh: ROO.26.03.02.05.001' : (isStrategisOpd ? 'Contoh: RSO.26.02.02.05.001' : 'Contoh: RSP.26.01.02.05.001')"
          style="width: 100%"
        />
        <small class="muted" style="font-size: 0.72rem; display: block; margin-top: 2px;">
          Format otomatis: {{ isOperasional ? 'ROO' : (isStrategisOpd ? 'RSO' : 'RSP') }}.[th].[jenis].[urusan].[opd].[urut]
        </small>
      </div>
      <div>
        <label class="muted lbl">Pemilik Risiko</label>
        <InputText v-model="editing.pemilik_risiko" style="width: 100%" />
      </div>
      <div>
        <label class="muted lbl">Sebab (Uraian)</label>
        <Textarea v-model="editing.sebab_uraian" autoResize rows="2" style="width: 100%" />
      </div>
      <div>
        <label class="muted lbl">Sumber Sebab</label>
        <Select v-model="editing.sebab_sumber" :options="['Internal', 'Eksternal', 'Internal/Eksternal']" style="width: 100%" />
      </div>
      <div>
        <label class="muted lbl">C (Controllable) / UC (Uncontrollable)</label>
        <Select v-model="editing.cuc" :options="['C', 'UC']" style="width: 100%" />
      </div>
      <div>
        <label class="muted lbl">Dampak — Pihak Terkena</label>
        <InputText v-model="editing.dampak_pihak_terkena" style="width: 100%" />
      </div>
      <div style="grid-column: 1 / -1">
        <label class="muted lbl">Dampak (Uraian)</label>
        <Textarea v-model="editing.dampak_uraian" autoResize rows="2" style="width: 100%" />
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
.konteks-ref {
  font-size: 0.82rem;
  line-height: 1.5;
  background: var(--p-surface-100, #f4f4f5);
  border-radius: 6px;
  padding: 8px 10px;
}
.kamus-option-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 4px 0;
}
.kamus-option-header {
  display: flex;
  align-items: center;
  gap: 6px;
}
.code-badge-sm {
  font-family: monospace;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 1px 6px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  color: #1e293b;
}
.category-tag-sm {
  font-size: 0.7rem;
  padding: 1px 6px;
  border-radius: 9999px;
  background: #e0e7ff;
  color: #3730a3;
  font-weight: 600;
}
.kamus-option-name {
  font-size: 0.85rem;
  color: #0f172a;
  line-height: 1.35;
}
</style>
