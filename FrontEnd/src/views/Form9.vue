<script setup>
import { ref, watch } from 'vue'
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
const loading = ref(false)
const dialog = ref(false)
const saving = ref(false)
const editing = ref({})
const current = ref(null)
const error = ref('')
const loadError = ref('')
const legacyRencanaWaktu = ref('')
let serial = 0

const jenisLabelMap = {
  strategis_pemda: 'Strategis Pemda',
  strategis_opd: 'Strategis OPD',
  operasional_opd: 'Operasional OPD',
}

const message = (e) =>
  typeof e.response?.data?.detail === 'string'
    ? e.response.data.detail
    : 'Periksa kelengkapan isian atau coba lagi.'

async function load() {
  const id = ++serial
  rows.value = []
  loadError.value = ''
  loading.value = true
  if (!ctx.ready) {
    loading.value = false
    return
  }
  try {
    const { data } = await api.get('/monitoring/pi', {
      params: { opd_id: ctx.opdId, tahun: ctx.tahun },
    })
    if (id === serial) rows.value = data
  } catch (e) {
    if (id === serial) loadError.value = `Gagal memuat Rencana Pemantauan PI. ${message(e)}`
  } finally {
    if (id === serial) loading.value = false
  }
}

function openEdit(row) {
  current.value = row
  let mulai = row.rencana_mulai || ''
  let selesai = row.rencana_selesai || ''
  let legacy = ''

  if (!mulai && !selesai && row.rencana_waktu) {
    const rangeMatch = row.rencana_waktu.match(/^(\d{4}-\d{2}-\d{2})\s+s\.d\.\s+(\d{4}-\d{2}-\d{2})$/)
    const singleMatch = row.rencana_waktu.match(/^(\d{4}-\d{2}-\d{2})$/)
    if (rangeMatch) {
      mulai = rangeMatch[1]
      selesai = rangeMatch[2]
    } else if (singleMatch) {
      mulai = singleMatch[1]
      selesai = singleMatch[1]
    } else {
      legacy = row.rencana_waktu
    }
  }

  legacyRencanaWaktu.value = legacy
  editing.value = {
    metode_pemantauan: row.metode_pemantauan || '',
    penanggung_jawab: row.penanggung_jawab || '',
    rencana_mulai: mulai,
    rencana_selesai: selesai,
    keterangan: row.keterangan || '',
  }
  error.value = ''
  dialog.value = true
}

async function save() {
  if (saving.value || !current.value) return
  if (
    editing.value.rencana_mulai &&
    editing.value.rencana_selesai &&
    editing.value.rencana_selesai < editing.value.rencana_mulai
  ) {
    error.value = 'Sampai tanggal tidak boleh sebelum Dari tanggal'
    return
  }
  if (Boolean(editing.value.rencana_mulai) !== Boolean(editing.value.rencana_selesai)) {
    error.value = 'Isi Dari tanggal dan Sampai tanggal secara lengkap'
    return
  }

  const payload = {
    metode_pemantauan: editing.value.metode_pemantauan?.trim() || null,
    penanggung_jawab: editing.value.penanggung_jawab?.trim() || null,
    rencana_mulai: editing.value.rencana_mulai || null,
    rencana_selesai: editing.value.rencana_selesai || null,
    keterangan: editing.value.keterangan?.trim() || null,
  }

  error.value = ''
  saving.value = true
  const id = serial
  try {
    await api.put(`/monitoring/pi/${current.value.id}`, payload)
    if (id !== serial) return
    dialog.value = false
    await load()
    toast.add({
      severity: 'success',
      summary: 'Data Rencana Pemantauan PI tersimpan',
      life: 1600,
    })
  } catch (e) {
    if (id === serial) error.value = `Gagal menyimpan. ${message(e)}`
  } finally {
    saving.value = false
  }
}

watch([() => ctx.opdId, () => ctx.tahun], () => {
  dialog.value = false
  load()
}, { immediate: true })
</script>

<template>
  <div class="page-header" style="margin-bottom: 1rem">
    <h2 style="margin: 0 0 4px 0">Form 9 — Rencana Pemantauan PI</h2>
    <p class="muted" style="margin: 0">
      Rencana dan realisasi pemantauan atas kegiatan pengendalian intern yang dibangun dari Respon Risiko (RTP).
    </p>
  </div>

  <p v-if="loadError" role="alert" class="error">
    {{ loadError }} <Button label="Coba lagi" text @click="load" />
  </p>

  <div class="page-card" style="padding: 0">
    <DataTable :value="rows" :loading="loading" size="small" stripedRows scrollable responsiveLayout="scroll">
      <Column header="No" :style="{ width: '50px', textAlign: 'center' }">
        <template #body="{ data, index }">{{ data.no_urut || index + 1 }}</template>
      </Column>
      <Column field="jenis_risiko" header="Jenis Risiko" :style="{ minWidth: '140px' }">
        <template #body="{ data }">
          <span v-if="data.jenis_risiko" :class="['badge-jenis', `badge-${data.jenis_risiko}`]">
            {{ jenisLabelMap[data.jenis_risiko] || data.jenis_risiko }}
          </span>
          <span v-else class="muted-dash">—</span>
        </template>
      </Column>
      <Column header="Kegiatan Pengendalian dari RTP" :style="{ minWidth: '280px' }">
        <template #body="{ data }">
          <div v-if="data.kode_risiko" class="badge-kode">{{ data.kode_risiko }}</div>
          <div class="kegiatan-text">{{ data.kegiatan_pengendalian }}</div>
          <div v-if="data.uraian_risiko" class="risiko-text muted text-xs">{{ data.uraian_risiko }}</div>
        </template>
      </Column>
      <Column field="metode_pemantauan" header="Bentuk / Metode Pemantauan" :style="{ minWidth: '200px' }">
        <template #body="{ data }">
          <span :class="{ 'muted-dash': !data.metode_pemantauan }">{{ data.metode_pemantauan || '—' }}</span>
        </template>
      </Column>
      <Column field="penanggung_jawab" header="Penanggung Jawab" :style="{ minWidth: '160px' }">
        <template #body="{ data }">
          <span :class="{ 'muted-dash': !data.penanggung_jawab }">{{ data.penanggung_jawab || '—' }}</span>
        </template>
      </Column>
      <Column field="rencana_waktu" header="Rencana Waktu" :style="{ minWidth: '170px' }">
        <template #body="{ data }">
          <span :class="{ 'muted-dash': !data.rencana_waktu }">{{ data.rencana_waktu || '—' }}</span>
        </template>
      </Column>
      <Column field="keterangan" header="Keterangan" :style="{ minWidth: '150px' }">
        <template #body="{ data }">
          <span :class="{ 'muted-dash': !data.keterangan }">{{ data.keterangan || '—' }}</span>
        </template>
      </Column>
      <Column header="Aksi" :style="{ width: '80px', textAlign: 'center' }">
        <template #body="{ data }">
          <Button
            icon="pi pi-pencil"
            aria-label="Edit Rencana Pemantauan PI"
            text
            rounded
            size="small"
            title="Edit / Isi Form"
            @click="openEdit(data)"
          />
        </template>
      </Column>
      <template #empty>
        <div class="muted" style="padding: 18px; text-align: center">
          Belum ada Kegiatan Pengendalian dari Respon Risiko (RTP). Pastikan Rencana Tindak Pengendalian telah diisi pada Form 7.
        </div>
      </template>
    </DataTable>
  </div>

  <Dialog
    v-model:visible="dialog"
    header="Rencana Pemantauan Pengendalian Intern (PI)"
    modal
    :closable="!saving"
    :closeOnEscape="!saving"
    :style="{ width: '640px', maxWidth: '95vw' }"
  >
    <div v-if="current" class="rtp-context-box">
      <div class="context-top">
        <span v-if="current.kode_risiko" class="context-kode">{{ current.kode_risiko }}</span>
        <span v-if="current.jenis_risiko" :class="['badge-jenis', `badge-${current.jenis_risiko}`]">
          {{ jenisLabelMap[current.jenis_risiko] || current.jenis_risiko }}
        </span>
      </div>
      <div class="context-kegiatan">
        <strong>Kegiatan Pengendalian (RTP):</strong>
        <p>{{ current.kegiatan_pengendalian }}</p>
      </div>
      <div v-if="current.uraian_risiko" class="context-risiko muted text-xs">
        Risiko: {{ current.uraian_risiko }}
      </div>
    </div>

    <form id="monitoring-pi-form" @submit.prevent="save">
      <fieldset :disabled="saving" class="fields">
        <div>
          <label for="f9-metode">Bentuk / Metode Pemantauan</label>
          <Textarea
            id="f9-metode"
            v-model="editing.metode_pemantauan"
            autoResize
            rows="2"
            maxlength="1000"
            placeholder="Contoh: Supervisi berkala, reviu laporan bulanan, inspeksi lapangan, pengujian sistem, dll."
            fluid
          />
        </div>

        <div>
          <label for="f9-pj">Penanggung Jawab</label>
          <InputText
            id="f9-pj"
            v-model="editing.penanggung_jawab"
            maxlength="255"
            placeholder="Contoh: Kepala Bidang / Tim Pemantau / Pengendali Teknis"
            fluid
          />
        </div>

        <div>
          <label>Rencana Waktu</label>
          <div class="date-range">
            <div>
              <label for="f9-rencana-mulai" class="sublabel">Dari tanggal</label>
              <input
                id="f9-rencana-mulai"
                v-model="editing.rencana_mulai"
                type="date"
                :max="editing.rencana_selesai || undefined"
              />
            </div>
            <div>
              <label for="f9-rencana-selesai" class="sublabel">Sampai tanggal</label>
              <input
                id="f9-rencana-selesai"
                v-model="editing.rencana_selesai"
                type="date"
                :min="editing.rencana_mulai || undefined"
              />
            </div>
          </div>
          <small v-if="legacyRencanaWaktu" class="muted">
            Rencana waktu sebelumnya: {{ legacyRencanaWaktu }}. Pilih rentang tanggal untuk memperbaruinya.
          </small>
        </div>

        <div>
          <label for="f9-keterangan">Keterangan</label>
          <Textarea
            id="f9-keterangan"
            v-model="editing.keterangan"
            autoResize
            rows="2"
            maxlength="2000"
            placeholder="Keterangan tambahan (opsional)"
            fluid
          />
        </div>
      </fieldset>

      <p v-if="error" role="alert" class="error">{{ error }}</p>
    </form>

    <template #footer>
      <Button label="Batal" text :disabled="saving" @click="dialog = false" />
      <Button
        label="Simpan"
        icon="pi pi-check"
        type="submit"
        form="monitoring-pi-form"
        :loading="saving"
        :disabled="saving"
      />
    </template>
  </Dialog>
</template>

<style scoped>
.page-header h2 {
  font-weight: 700;
  color: var(--text-color, #1e293b);
}
.badge-kode {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  font-family: monospace;
  background: var(--surface-2, #e2e8f0);
  color: var(--primary-color, #0284c7);
  padding: 1px 6px;
  border-radius: 4px;
  margin-bottom: 4px;
}
.badge-jenis {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
}
.badge-strategis_pemda {
  background: #dbeafe;
  color: #1e40af;
}
.badge-strategis_opd {
  background: #ede9fe;
  color: #6b21a8;
}
.badge-operasional_opd {
  background: #fef3c7;
  color: #92400e;
}
.kegiatan-text {
  font-weight: 500;
  line-height: 1.4;
}
.risiko-text {
  margin-top: 2px;
}
.muted-dash {
  color: #94a3b8;
}
.rtp-context-box {
  padding: 12px 14px;
  background: var(--surface-ground, #f8fafc);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  margin-bottom: 16px;
}
.context-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.context-kode {
  font-size: 0.75rem;
  font-weight: 700;
  font-family: monospace;
  color: var(--primary-color, #0284c7);
}
.context-kegiatan strong {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 2px;
}
.context-kegiatan p {
  margin: 0;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}
.context-risiko {
  margin-top: 6px;
  font-size: 0.78rem;
}
.fields {
  border: 0;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}
label {
  font-size: 0.85rem;
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
  color: var(--text-color, #334155);
}
label.sublabel {
  font-weight: 500;
  font-size: 0.78rem;
  color: #64748b;
}
.date-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.date-range > div {
  min-width: 0;
}
input[type='date'] {
  width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font: inherit;
  background: var(--surface-0, #fff);
  color: inherit;
}
input[type='date']:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}
@media (max-width: 480px) {
  .date-range {
    grid-template-columns: 1fr;
  }
}
.error {
  color: #b91c1c;
  font-size: 0.85rem;
  margin-top: 8px;
}
small {
  display: block;
  margin-top: 4px;
  font-size: 0.78rem;
}
</style>
