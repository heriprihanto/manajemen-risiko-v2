<script setup>
import { computed, onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import SelectButton from 'primevue/selectbutton'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { useAuthStore } from '@/stores/auth'
import AppLoader from '@/components/AppLoader.vue'
import { formatDateTime } from '@/utils/date'

const ctx = useContextStore()
const auth = useAuthStore()
const toast = useToast()
const confirm = useConfirm()
const isAdmin = computed(() => auth.isAdmin)
const loading = ref(true)
const data = ref(null)
const expanded = ref([])
const sumber = ref('all')

const sumberOptions = [
  { label: 'Semua', value: 'all' },
  { label: 'Survei Publik', value: 'survei' },
  { label: 'Input Admin', value: 'admin' },
]

const skalaLabel = {
  1: 'Tidak Setuju',
  2: 'Kurang Setuju',
  3: 'Setuju',
  4: 'Sangat Setuju',
}

const responden = computed(() => {
  const list = data.value?.responden || []
  return sumber.value === 'all' ? list : list.filter((r) => r.sumber === sumber.value)
})
const totalResp = computed(() => responden.value.length)
const rataKeseluruhan = computed(() => {
  const vals = responden.value.map((r) => r.rata_rata).filter((v) => v != null)
  if (!vals.length) return '–'
  return (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2)
})
const totalPertanyaan = computed(() => data.value?.total_pertanyaan || 0)

function fmtDate(iso) {
  return formatDateTime(iso, { dateStyle: 'medium', timeStyle: 'short' })
}
function nilaiColor(v) {
  if (v == null) return 'secondary'
  if (v >= 3) return 'success'
  return 'danger'
}

function remove(r) {
  confirm.require({
    message: `Hapus hasil survei responden "${r.kode_responden}${r.nama_responden ? ' — ' + r.nama_responden : ''}"? Tindakan ini tidak dapat dibatalkan.`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await api.delete(`/cee/survei-hasil/${r.id}`)
      await load()
      toast.add({ severity: 'success', summary: 'Hasil survei dihapus', life: 1800 })
    },
  })
}

async function load() {
  loading.value = true
  expanded.value = []
  const { data: d } = await api.get('/cee/survei-hasil', {
    params: { opd_id: ctx.opdId, tahun: ctx.tahun },
  })
  data.value = d
  loading.value = false
}

onMounted(load)
</script>

<template>
  <div class="toolbar no-print">
    <span class="muted">{{ ctx.opd?.nama_pd }} — {{ ctx.tahun }}</span>
    <div class="spacer" />
    <SelectButton v-model="sumber" :options="sumberOptions" optionLabel="label" optionValue="value" />
  </div>

  <AppLoader v-if="loading" label="Memuat rincian hasil survei…" />

  <template v-else>
    <div class="stat-grid" style="margin-bottom: 16px">
      <div class="stat"><div class="v">{{ totalResp }}</div><div class="l">Responden</div></div>
      <div class="stat"><div class="v">{{ totalPertanyaan }}</div><div class="l">Pertanyaan per Responden</div></div>
      <div class="stat"><div class="v">{{ rataKeseluruhan }}</div><div class="l">Rata-rata Skor (1–4)</div></div>
    </div>

    <div class="page-card" style="padding: 0">
      <DataTable
        v-model:expandedRows="expanded"
        :value="responden"
        dataKey="id"
        size="small"
        stripedRows
        scrollable
      >
        <Column expander :style="{ width: '42px' }" />
        <Column field="kode_responden" header="Kode" :style="{ width: '70px' }" />
        <Column header="Nama Responden" :style="{ minWidth: '180px' }">
          <template #body="{ data: r }">
            <div style="display: flex; align-items: center; gap: 6px">
              <span>{{ r.nama_responden || '–' }}</span>
              <i
                v-if="r.narasi"
                class="pi pi-comment"
                style="color: #2563eb; font-size: 0.85rem"
                v-tooltip.top="'Ada narasi kondisi lingkungan pengendalian'"
              />
            </div>
          </template>
        </Column>
        <Column header="Jabatan" :style="{ minWidth: '150px' }">
          <template #body="{ data: r }">{{ r.jabatan || '–' }}</template>
        </Column>
        <Column header="Email" :style="{ minWidth: '190px' }">
          <template #body="{ data: r }"><span class="muted">{{ r.email || '–' }}</span></template>
        </Column>
        <Column header="Sumber" :style="{ width: '120px' }">
          <template #body="{ data: r }">
            <Tag
              :value="r.sumber === 'survei' ? 'Survei Publik' : 'Input Admin'"
              :severity="r.sumber === 'survei' ? 'info' : 'secondary'"
            />
          </template>
        </Column>
        <Column header="Terisi" :style="{ width: '90px' }">
          <template #body="{ data: r }">{{ r.jumlah_jawaban }} / {{ totalPertanyaan }}</template>
        </Column>
        <Column header="Rata-rata" :style="{ width: '90px' }">
          <template #body="{ data: r }"><strong>{{ r.rata_rata ?? '–' }}</strong></template>
        </Column>
        <Column header="Waktu Pengisian" :style="{ minWidth: '160px' }">
          <template #body="{ data: r }"><span class="muted">{{ fmtDate(r.submitted_at) }}</span></template>
        </Column>
        <Column v-if="isAdmin" header="" :style="{ width: '56px' }" class="no-print">
          <template #body="{ data: r }">
            <Button
              icon="pi pi-trash"
              text
              rounded
              size="small"
              severity="danger"
              @click="remove(r)"
            />
          </template>
        </Column>

        <template #expansion="{ data: r }">
          <div class="detail">
            <div v-if="r.narasi" class="narasi-box">
              <div class="narasi-head">
                <i class="pi pi-comment" />
                <span>Narasi Lain Terkait Kondisi Lingkungan Pengendalian:</span>
              </div>
              <div class="narasi-body">{{ r.narasi }}</div>
            </div>

            <div v-for="kat in data.kategori" :key="kat.id" class="detail-kat">
              <div class="detail-head">{{ kat.kode }}. {{ kat.nama }}</div>
              <table class="detail-table">
                <tbody>
                  <tr v-for="(p, i) in kat.pertanyaan" :key="p.id">
                    <td class="c muted" style="width: 32px">{{ i + 1 }}</td>
                    <td>{{ p.pertanyaan }}</td>
                    <td class="c" style="width: 150px">
                      <Tag
                        v-if="r.jawaban[p.id] != null"
                        :value="`${r.jawaban[p.id]} — ${skalaLabel[r.jawaban[p.id]]}`"
                        :severity="nilaiColor(r.jawaban[p.id])"
                      />
                      <span v-else class="muted">Belum dijawab</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>

        <template #empty><div class="muted" style="padding: 14px">Belum ada responden survei.</div></template>
      </DataTable>
    </div>
  </template>
</template>

<style scoped>
.detail { padding: 8px 14px 14px; background: #f8fafc; }
.detail-kat { margin-bottom: 12px; }
.detail-head { font-weight: 600; color: #0f172a; margin: 8px 0 4px; }
.detail-table { border-collapse: collapse; width: 100%; font-size: 0.82rem; background: #fff; }
.detail-table td { border: 1px solid #e2e8f0; padding: 4px 8px; vertical-align: top; }
.detail-table td.c { text-align: center; }
.narasi-box {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-left: 4px solid #16a34a;
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 12px;
}
.narasi-head {
  font-weight: 600;
  color: #15803d;
  font-size: 0.84rem;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.narasi-body {
  font-size: 0.85rem;
  color: #1e293b;
  white-space: pre-wrap;
  line-height: 1.5;
}
</style>
