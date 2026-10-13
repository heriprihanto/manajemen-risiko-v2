<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import AppLoader from '@/components/AppLoader.vue'

const ctx = useContextStore()
const toast = useToast()
const subs = ref([]) // subkegiatan renja OPD (+indikator lvl-7)
const progInd = ref([]) // indikator program (lvl-5)
const kegInd = ref([]) // indikator kegiatan (lvl-6)
const checkedSub = ref(new Set()) // Set idsubkegiatan
const checkedInd = ref(new Set()) // Set id indikator (program & kegiatan → ref_indikator)
const loading = ref(true)
const saving = ref(false)

async function load() {
  loading.value = true
  const params = { opd_id: ctx.opdId, tahun: ctx.tahun }
  const [renja, konteks] = await Promise.all([
    api.get('/master/renja/subkegiatan', { params }).then((r) => r.data).catch(() => ({})),
    api.get('/konteks/operasional-opd', { params }).then((r) => r.data).catch(() => []),
  ])
  subs.value = renja?.subkegiatan || []
  progInd.value = renja?.indikator_program || []
  kegInd.value = renja?.indikator_kegiatan || []
  const rows = konteks || []
  checkedSub.value = new Set(rows.map((r) => r.ref_subkegiatan).filter(Boolean))
  checkedInd.value = new Set(rows.map((r) => r.ref_indikator).filter(Boolean))
  loading.value = false
}

// Kelompokkan Program → (indikator program) + Kegiatan → (indikator kegiatan) + subkegiatan.
const groups = computed(() => {
  const prog = new Map()
  const ensureProg = (idprogram, nama) => {
    if (!prog.has(idprogram)) {
      prog.set(idprogram, { idprogram, program: nama, indikator: [], kegMap: new Map() })
    }
    return prog.get(idprogram)
  }
  const ensureKeg = (g, idkegiatan, nama) => {
    if (!g.kegMap.has(idkegiatan)) {
      g.kegMap.set(idkegiatan, { idkegiatan, nama, indikator: [], subkegiatan: [] })
    }
    return g.kegMap.get(idkegiatan)
  }
  for (const s of subs.value) {
    ensureKeg(ensureProg(s.idprogram, s.nm_program), s.idkegiatan, s.nm_kegiatan).subkegiatan.push(s)
  }
  for (const pi of progInd.value) ensureProg(pi.idprogram, pi.nm_program).indikator.push(pi)
  for (const ki of kegInd.value) {
    ensureKeg(ensureProg(ki.idprogram, ki.nm_program), ki.idkegiatan, ki.nm_kegiatan).indikator.push(ki)
  }
  return [...prog.values()].map((g) => ({ ...g, kegiatan: [...g.kegMap.values()] }))
})

const selectedCount = computed(() => checkedSub.value.size + checkedInd.value.size)
const isSub = (id) => checkedSub.value.has(id)
const isInd = (id) => checkedInd.value.has(id)
function toggleSet(refSet, id) {
  const set = new Set(refSet.value)
  set.has(id) ? set.delete(id) : set.add(id)
  refSet.value = set
}
const toggleSub = (id) => toggleSet(checkedSub, id)
const toggleInd = (id) => toggleSet(checkedInd, id)

async function save() {
  saving.value = true
  const subItems = subs.value
    .filter((s) => checkedSub.value.has(s.idsubkegiatan))
    .map((s) => ({
      ref_subkegiatan: s.idsubkegiatan,
      program: s.nm_program,
      keluaran_hasil_kegiatan: s.nm_kegiatan,
      keluaran_sub_kegiatan: s.indikator || s.nm_sub_kegiatan,
    }))
  const progItems = progInd.value
    .filter((p) => checkedInd.value.has(p.id))
    .map((p) => ({ ref_indikator: p.id, program: p.nm_program, indikator_program: p.label }))
  const kegItems = kegInd.value
    .filter((k) => checkedInd.value.has(k.id))
    .map((k) => ({ ref_indikator: k.id, program: k.nm_program, keluaran_hasil_kegiatan: k.label }))
  const items = [...subItems, ...progItems, ...kegItems]
  try {
    await api.post('/konteks/operasional-opd/sync', { opd_id: ctx.opdId, tahun: ctx.tahun, items })
    toast.add({ severity: 'success', summary: `Tersimpan (${items.length} indikator)`, life: 1800 })
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="toolbar no-print" style="justify-content: flex-end; gap: 8px">
    <RouterLink :to="{ name: 'laporan', query: { form: 'f2c', print: 1 } }" custom v-slot="{ navigate }">
      <Button label="Cetak Form 2.c" icon="pi pi-print" size="small" outlined @click="navigate" />
    </RouterLink>
    <Button
      :label="`Simpan Pilihan (${selectedCount})`"
      icon="pi pi-check"
      size="small"
      :loading="saving"
      :disabled="loading"
      @click="save"
    />
  </div>

  <div class="page-card">
    <p class="muted" style="margin-top: 0">
      Centang indikator (program, kegiatan &amp; subkegiatan) yang akan dilakukan penilaian risiko — Form 2.c Konteks Operasional OPD.
      <b>{{ ctx.opd?.nama_pd }}</b> — {{ ctx.tahun }}
    </p>

    <AppLoader v-if="loading" label="Memuat data renja…" />
    <div v-else-if="!subs.length && !progInd.length && !kegInd.length" class="muted">
      Belum ada data renja untuk OPD &amp; tahun ini.
    </div>

    <div v-else class="renja-list">
      <div v-for="g in groups" :key="g.idprogram" class="renja-prog">
        <div class="renja-prog-head">{{ g.program }}</div>

        <!-- Indikator program (lvl-5) -->
        <div v-if="g.indikator.length" class="renja-keg">
          <div class="renja-keg-head">Indikator Program</div>
          <label v-for="pi in g.indikator" :key="pi.id" class="renja-row">
            <Checkbox :modelValue="isInd(pi.id)" binary @update:modelValue="toggleInd(pi.id)" />
            <span class="renja-sub"><span>{{ pi.label }}</span></span>
          </label>
        </div>

        <!-- Per Kegiatan: indikator kegiatan (lvl-6) + subkegiatan (lvl-7) -->
        <div v-for="k in g.kegiatan" :key="k.idkegiatan" class="renja-keg">
          <div class="renja-keg-head">{{ k.nama }}</div>
          <label v-for="ki in k.indikator" :key="ki.id" class="renja-row indikator-keg">
            <Checkbox :modelValue="isInd(ki.id)" binary @update:modelValue="toggleInd(ki.id)" />
            <span class="renja-sub"><span><span class="tag">Indikator Kegiatan</span> {{ ki.label }}</span></span>
          </label>
          <label v-for="s in k.subkegiatan" :key="s.idsubkegiatan" class="renja-row">
            <Checkbox :modelValue="isSub(s.idsubkegiatan)" binary @update:modelValue="toggleSub(s.idsubkegiatan)" />
            <span class="renja-sub">
              <span><span class="kode">{{ s.kode_sub_kegiatan }}</span> {{ s.nm_sub_kegiatan }}</span>
              <span v-if="s.indikator" class="muted ind">Indikator: {{ s.indikator }}</span>
            </span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.renja-prog { margin-bottom: 18px; }
.renja-prog-head {
  font-weight: 700;
  font-size: 0.9rem;
  background: var(--p-surface-100, #f1f5f9);
  padding: 6px 10px;
  border-radius: 6px;
}
.renja-keg { margin: 8px 0 8px 6px; }
.renja-keg-head { font-weight: 600; font-size: 0.84rem; margin: 8px 0 4px; }
.renja-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
}
.renja-row:hover { background: var(--p-surface-50, #f8fafc); }
.renja-sub { display: flex; flex-direction: column; gap: 2px; font-size: 0.85rem; }
.renja-sub .kode { font-family: monospace; color: var(--p-text-muted-color, #64748b); margin-right: 4px; }
.renja-sub .ind { font-size: 0.78rem; }
.renja-sub .tag {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--p-primary-color, #3b82f6);
  border: 1px solid currentColor;
  border-radius: 4px;
  padding: 0 4px;
  margin-right: 4px;
}
</style>
