<script setup>
import { computed, reactive, ref, watch } from 'vue'
import Button from 'primevue/button'
import api from '@/api'
import { useContextStore } from '@/stores/context'
import { getMatrixScore, getToleranceBorderStyles } from '@/utils/matriks'
const ctx = useContextStore()
const data = ref(null), error = ref(''), success = ref(''), saving = ref(false), loading = ref(false)
const form = reactive({ ambang: '', pertimbangan_sumber_daya: '', dasar_penetapan: '' })
let serial = 0
const current = computed(() => data.value?.aktif.find(s => !s.pemilik_key))
const accepted = computed(() => form.ambang ? Array.from({ length: Number(form.ambang) }, (_, i) => i + 1) : null)
const history = computed(() => data.value?.riwayat.filter(s => !s.pemilik_key) || [])
function resetForm() {
  const s = current.value
  Object.assign(form, { ambang: s?.ambang || '', pertimbangan_sumber_daya: s?.pertimbangan_sumber_daya || '', dasar_penetapan: s?.dasar_penetapan || '' })
}
async function load() {
  const id = ++serial
  data.value = null; error.value = ''; success.value = ''; loading.value = true
  if (!ctx.ready) { loading.value = false; return }
  try {
    const r = await api.get('/selera-risiko', { params: { opd_id: ctx.opdId, tahun: ctx.tahun } })
    if (id !== serial) return
    data.value = r.data; resetForm()
  } catch (e) { if (id === serial) error.value = 'Gagal memuat Selera Risiko. Silakan coba lagi.' }
  finally { if (id === serial) loading.value = false }
}
async function save() {
  const id = serial
  const scope = `${ctx.opdId}/${ctx.tahun}`
  saving.value = true; error.value = ''; success.value = ''
  try {
    const r = await api.post('/selera-risiko', { opd_id: ctx.opdId, tahun: ctx.tahun,
      ...form, ambang: Number(form.ambang), dasar_penetapan: form.dasar_penetapan.trim() || null })
    if (id !== serial) return
    await load()
    if (scope !== `${ctx.opdId}/${ctx.tahun}`) return
    success.value = `Ketetapan tersimpan. ${r.data.analisis_diperbarui} analisis mengikuti ambang ini.`
  } catch (e) { if (id === serial) error.value = typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Ketetapan belum tersimpan. Periksa isian dan coba lagi.' }
  finally { saving.value = false }
}
watch([() => ctx.opdId, () => ctx.tahun], load, { immediate: true })
</script>

<template>
  <div class="selera-risiko-page">
    <!-- Header Section (Style Realisasi RTP) -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon-box">
          <i class="pi pi-sliders-h"></i>
        </div>
        <div>
          <h1 class="page-title">Selera Risiko</h1>
          <p class="page-desc">
            Penetapan ambang batas toleransi besaran level risiko yang berada dalam area penerimaan risiko
          </p>
        </div>
      </div>
      <div class="header-actions">
        <div class="ctx-chip" title="Konteks Penilaian Aktif">
          <i class="pi pi-building"></i>
          <span>{{ ctx.opd?.nama_pd || 'Semua OPD' }}</span>
          <span class="chip-dot">•</span>
          <span>Tahun {{ ctx.tahun }}</span>
        </div>
        <Button
          label="Segarkan"
          icon="pi pi-refresh"
          severity="secondary"
          variant="outlined"
          :loading="loading"
          @click="load"
        />
      </div>
    </div>

    <div class="page-card">
      <p class="muted" style="margin-top: 0">
        Selera risiko adalah ambang batas besaran level risiko yang berada dalam area penerimaan risiko dan tidak perlu dilakukan kegiatan pengendalian.
        Ketetapan berlaku untuk OPD dan tahun yang dipilih. Pengelola mencatat keputusan Pemilik Risiko beserta dasar pertimbangannya.
      </p>
    <p v-if="loading">Memuat ketetapan…</p>
    <p v-if="error" role="alert" class="error">{{ error }} <button v-if="!data" @click="load">Coba lagi</button></p>
    <p v-if="success" role="status" class="success">{{ success }}</p>
    <template v-if="data">
      <p class="notice">Ambang berlaku: <strong>{{ current ? current.ambang : 'Belum ditetapkan' }}</strong></p>
      <form @submit.prevent="save">
        <fieldset :disabled="saving || !data.boleh_tulis">
          <div class="layout">
            <div>
              <label for="ambang">Ambang selera risiko (1–{{ data.skala_maksimum }})</label>
              <select id="ambang" v-model="form.ambang" required>
                <option disabled value="">Pilih ambang</option>
                <option v-for="n in data.skala_maksimum" :key="n" :value="n">{{ n }}</option>
              </select>
              <label for="sumber-daya">Pertimbangan sumber daya</label>
              <textarea id="sumber-daya" v-model="form.pertimbangan_sumber_daya" required minlength="3" maxlength="10000" rows="4" placeholder="Pertimbangkan SDM, anggaran, sarana, kemampuan pengendalian, dan kapasitas unit kerja." />
              <label for="dasar">Referensi dokumen penetapan (opsional)</label>
              <input id="dasar" v-model="form.dasar_penetapan" minlength="3" maxlength="10000" />
            </div>
            <div>
              <h3>Pratinjau area penerimaan</h3>
              <p v-if="form.ambang">Skor <strong>1–{{ form.ambang }}</strong> diterima. <span v-if="form.ambang < data.skala_maksimum">Skor <strong>{{ Number(form.ambang) + 1 }}–{{ data.skala_maksimum }}</strong> memerlukan pengendalian.</span><span v-else>Seluruh skor berada dalam area penerimaan.</span></p>
              <p v-else>Pilih ambang untuk melihat area penerimaan.</p>
              <table class="preview"><caption>Kemungkinan (baris) × Dampak (kolom)</caption><thead><tr><th>K / D</th><th v-for="d in 5" :key="d">{{ d }}</th></tr></thead><tbody>
                <tr v-for="k in [5,4,3,2,1]" :key="k"><th>{{ k }}</th><td v-for="d in 5" :key="d" :class="{ accepted: accepted?.includes(getMatrixScore(k,d)), outside: accepted && !accepted.includes(getMatrixScore(k,d)) }" :style="getToleranceBorderStyles(k,d,accepted)">{{ getMatrixScore(k,d) }}</td></tr>
              </tbody></table>
              <p class="muted">Hijau: diterima · Jingga: perlu pengendalian. Skor tepat pada ambang termasuk diterima.</p>
            </div>
          </div>
          <p>Perubahan memperbarui prioritas analisis saat ini. Riwayat penilaian, RTP, dan laporan tersimpan tetap dipertahankan.</p>
          <button type="submit" class="primary">{{ saving ? 'Menyimpan…' : 'Simpan ketetapan' }}</button>
        </fieldset>
      </form>
      <p v-if="!data.boleh_tulis" class="muted">Penugasan Anda hanya mengizinkan melihat ketetapan.</p>
      <h3>Riwayat ketetapan entitas</h3>
      <div class="scroll"><table class="history"><thead><tr><th>Dicatat</th><th>Ambang</th><th>Penetap</th><th>Pertimbangan sumber daya</th><th>Dokumen</th><th>Pencatat</th></tr></thead><tbody>
        <tr v-for="s in history" :key="s.id"><td>{{ s.created_at.replace('T',' ').slice(0,19) }}</td><td>{{ s.ambang }}</td><td>{{ s.penetap || '—' }}</td><td>{{ s.pertimbangan_sumber_daya }}</td><td>{{ s.dasar_penetapan || '—' }}</td><td>{{ s.dicatat_oleh }}</td></tr>
        <tr v-if="!history.length"><td colspan="6">Belum ada ketetapan untuk cakupan ini.</td></tr>
      </tbody></table></div>
    </template>
    </div>
  </div>
</template>
<style scoped>
.selera-risiko-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Page Header (Style Realisasi RTP) */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}

.page-desc {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.ctx-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.chip-dot {
  color: #94a3b8;
}

h2 { margin-top: 0; } label { display:block; font-weight:600; margin: 14px 0 6px; }
input, select, textarea { width:100%; padding:10px; border:1px solid #cbd5e1; border-radius:6px; font:inherit; box-sizing:border-box; }
fieldset { border:0; padding:0; min-width:0; } .layout { display:grid; grid-template-columns:1fr 1fr; gap:32px; }
.notice { background:#eff6ff; padding:12px; border-radius:6px; } .error { color:#b91c1c; } .success { color:#166534; }
.preview { width:100%; border-collapse:collapse; text-align:center; } .preview td, .preview th { padding:12px; border:1px solid #cbd5e1; } caption { margin-bottom:12px; }
.accepted { background:#dcfce7; color:#14532d; } .outside { background:#ffedd5; color:#7c2d12; }
.primary { background:#2563eb; color:white; border:0; padding:12px 18px; border-radius:6px; cursor:pointer; } button:disabled { opacity:.6; cursor:wait; }
.scroll { overflow:auto; } .history { border-collapse:collapse; width:100%; border:1px solid #e2e8f0; } .history th,.history td { text-align:left; padding:10px; border:1px solid #e2e8f0; vertical-align:top; white-space:pre-wrap; } .history thead th { background:#f8fafc; color:#1e293b; font-weight:600; } .history tbody tr:nth-child(even) { background:#f8fafc; } .history tbody tr:hover { background:#f1f5f9; }
@media(max-width:760px) { .layout { grid-template-columns:1fr; gap:12px; } }
</style>
