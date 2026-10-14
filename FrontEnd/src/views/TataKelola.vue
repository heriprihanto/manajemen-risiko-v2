<script setup>
import { computed, ref, watch } from 'vue'
import Button from 'primevue/button'
import GovernanceForm from '@/components/GovernanceForm.vue'
import { useGovernance, field, message } from '@/composables/useGovernance'
import { useContextStore } from '@/stores/context'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const ctx = useContextStore(), auth = useAuthStore()
const tab = ref('ringkasan'), data = ref({}), roles = ref([]), loading = ref(false), error = ref('')
const tabs = [{id:'ringkasan',label:'Pemantauan'}, {id:'konsolidasi',label:'Lintas OPD'}, {id:'kebijakan',label:'Kebijakan Penilaian'}, {id:'penugasan',label:'Struktur & Penugasan'}, {id:'laporan',label:'Laporan Berkala'}, {id:'usulan-kamus',label:'Usulan Kamus'}, {id:'audit',label:'Riwayat Aktivitas'}]
const canWrite = ref(false)
const has = (...r) => r.some(x => roles.value.includes(x))
let requestId = 0
async function load() {
  if (!ctx.ready) return
  const id = ++requestId
  loading.value = true; error.value = ''; data.value = {}
  try {
    const results = await Promise.allSettled([
      api.get(`/tata-kelola/${tab.value}`, {params:{opd_id:ctx.opdId,tahun:ctx.tahun}}),
      api.get('/tata-kelola/akses', {params:{opd_id:ctx.opdId}}),
    ])
    if (id !== requestId) return
    const failed = results.find(r => r.status === 'rejected')
    if (failed) throw failed.reason
    data.value = results[0].value.data; roles.value = results[1].value.data.peran; canWrite.value = results[1].value.data.boleh_tulis
  } catch(e) { if (id === requestId) error.value = message(e) }
  finally { if (id === requestId) loading.value = false }
}
const form = useGovernance(load)
const { visible, title, fields, initial, busy, error: formError } = form
watch([() => ctx.opdId, () => ctx.tahun, tab], () => { visible.value = false; load() }, { immediate:true })
const scope = () => ({opd_id:ctx.opdId,tahun:ctx.tahun})
function policy() {
  const s = scope()
  form.open('Ajukan kebijakan penilaian', [
    field('nama','Nama / versi kebijakan'), field('dasar','Dokumen penetapan / berita acara FGD','textarea'),
    field('berlaku','Tanggal mulai berlaku','date'),
    field('dampak','Kriteria dampak skala 1–5','lines',{help:'Isi tepat lima baris; satu deskripsi operasional per skala.'}),
    field('kemungkinan','Kriteria kemungkinan skala 1–5','lines',{help:'Isi tepat lima baris; satu deskripsi operasional per skala.'}),
    field('area_dampak','Urutan prioritas area dampak','lines',{help:'Satu area per baris, prioritas tertinggi di atas.'}),
    field('kategori_prioritas','Urutan prioritas kategori risiko','lines',{help:'Satu kategori per baris, prioritas tertinggi di atas.'}),
  ], d => api.post('/tata-kelola/kebijakan',{...s,...d}))
}
function assignment() {
  const opd = ctx.opdId
  form.open('Tambah penugasan', [field('username','Username SSO'),field('nama','Nama pejabat / petugas'),
    field('peran','Peran','select',{options:['operator','upr','atasan','upr_atasan','upr_pemda','kepatuhan','inspektorat','komite','koordinator']}),
    field('mulai','Mulai penugasan','date'),field('selesai','Akhir penugasan','date'),field('dasar','Nomor SK / dasar penugasan','textarea'),
  ],d=>api.post('/tata-kelola/penugasan',{opd_id:opd,...d}))
}
function deactivate(row) {
  form.open('Nonaktifkan penugasan', [], () => api.post(`/tata-kelola/penugasan/${row.id}/nonaktif`))
}
function report() {
  const s = scope()
  const options = []
  if (canWrite.value || has('koordinator','upr_pemda')) options.push({value:'penilaian',label:'Pelaksanaan Penilaian Risiko'}, {value:'upr',label:'Pengelolaan Risiko oleh UPR'})
  if (has('kepatuhan')) options.push({value:'kepatuhan',label:'Pemantauan oleh Unit Kepatuhan'})
  if (has('komite')) options.push({value:'pembinaan',label:'Pembinaan oleh Komite'})
  const scopeFields = has('koordinator','upr_pemda') ? [
    field('cakupan','Cakupan laporan','select',{options:[{value:'opd',label:'OPD terpilih'},{value:'pemda',label:'Kompilasi risiko strategis Pemda'}],default:canWrite.value?'opd':'pemda'}),
    field('opd_ids','OPD sumber kompilasi Pemda','multi',{optional:true,options:ctx.opdList.map(o=>({value:o.id_sub_pd,label:o.nama_pd})),help:'Diisi untuk kompilasi Pemda. Hanya risiko strategis Pemda yang dikompilasi.'}),
  ] : []
  form.open('Ajukan laporan berkala', [...scopeFields,field('jenis','Jenis laporan','select',{options}),
    field('periode','Periode','select',{options:['TW1','TW2','TW3','TW4','TAHUNAN']}),
    field('ringkasan','Ringkasan pelaksanaan, hambatan, dan rekomendasi','textarea'),
  ],d=>api.post('/tata-kelola/laporan',{...s,...d}))
}
function proposal() {
  const s = scope()
  form.open('Usulkan entri kamus risiko', [field('nama','Nama risiko'),field('kategori','Kategori risiko','select',{
    options:['Risiko Kebijakan','Risiko Kepatuhan','Risiko Legal','Risiko Fraud/Kecurangan','Risiko Reputasi','Risiko Operasional','Risiko Kemitraan','Risiko SPBE']}),
    field('deskripsi','Deskripsi dan alasan usulan','textarea')],d=>api.post('/tata-kelola/usulan-kamus',{...s,...d}))
}
const other = r => r.status === 'diajukan' && r.pembuat !== auth.user?.username
const reportDecision = r => other(r) && (r.cakupan === 'pemda' ? has('upr_pemda') : r.jenis === 'kepatuhan' ? has('kepatuhan') : r.jenis === 'pembinaan' ? has('komite') : has('upr','upr_pemda'))
</script>

<template>
  <section class="governance">
    <div class="intro"><h2>Tata Kelola Risiko</h2><p>Kelola keputusan, pelaksanaan pengendalian, dan laporan {{ ctx.tahun }} untuk {{ ctx.opd?.nama_pd }}.</p>
      <small>Peran aktif: {{ roles.join(', ') || (canWrite ? 'Pengelola OPD (pengajuan)' : 'Baca saja') }}. Persetujuan memerlukan penugasan dan pengguna yang berbeda.</small>
    </div>
    <nav class="tabs no-print" aria-label="Modul tata kelola"><button v-for="t in tabs" :key="t.id" :class="{active:tab===t.id}" @click="tab=t.id">{{ t.label }}</button></nav>
    <p v-if="error" role="alert" class="error">{{ error }} <Button label="Coba lagi" text @click="load" /></p>
    <p v-if="loading" role="status">Memuat data…</p>
    <template v-else-if="!error">
      <section v-if="tab==='ringkasan'">
        <div class="metrics"><div><strong>{{ data.terlambat || 0 }}</strong>Tindakan terlambat</div><div><strong>{{ data.menunggu || 0 }}</strong>Respons menunggu keputusan</div><div><strong>{{ data.residual_melampaui || 0 }}</strong>Risiko residual melampaui batas</div><div><strong>{{ data.perlu_penilaian_ulang || 0 }}</strong>Risiko perlu dinilai ulang setelah kejadian</div></div>
        <p>Skor residual dicatat melalui penilaian ulang berbukti. Jumlah risiko yang sedikit belum menunjukkan pengelolaan yang lebih baik.</p>
        <div class="table-wrap"><table><thead><tr><th>Risiko / sasaran</th><th>Pemilik</th><th>Awal</th><th>Residual</th><th>Perhatian</th></tr></thead><tbody>
          <tr v-for="r in data.items" :key="r.id"><td><router-link :to="{name:'detail-risiko',params:{id:r.id}}">{{ r.kode }} — {{ r.uraian }}</router-link><small>{{ r.sasaran }}</small></td><td>{{ r.pemilik }}</td><td>{{ r.skor_awal ?? 'Belum dinilai' }}</td><td>{{ r.residual ?? 'Belum dinilai ulang' }}</td><td><span v-if="r.melampaui">Melampaui batas. </span><span v-if="r.terlambat">{{ r.terlambat }} tindakan terlambat. </span><span v-if="r.perlu_penilaian_ulang">Tinjau setelah kejadian. </span><span v-if="r.menunggu">{{ r.menunggu }} pengajuan.</span></td></tr>
          <tr v-if="!data.items?.length"><td colspan="5">Belum ada risiko. Tambahkan melalui menu Identifikasi Risiko.</td></tr>
        </tbody></table></div>
      </section>
      <section v-if="tab==='konsolidasi'">
        <h3>Pemantauan lintas OPD yang dapat Anda akses</h3><p>Bandingkan kelengkapan penilaian, keterlambatan, dan kebutuhan tindak lanjut. Jumlah risiko bukan peringkat kinerja OPD.</p>
        <div class="table-wrap"><table><thead><tr><th>OPD</th><th>Risiko</th><th>Belum dinilai</th><th>Tindakan terlambat</th><th>Residual melampaui</th><th>Respons menunggu</th><th>Perlu penilaian ulang</th></tr></thead><tbody><tr v-for="r in data" :key="r.opd_id"><td>{{ r.nama }}</td><td>{{ r.risiko }}</td><td>{{ r.belum_dinilai }}</td><td>{{ r.terlambat }}</td><td>{{ r.residual_melampaui }}</td><td>{{ r.menunggu }}</td><td>{{ r.perlu_penilaian_ulang }}</td></tr></tbody></table></div>
      </section>
      <section v-if="tab==='kebijakan'">
        <div class="toolbar"><h3>Kebijakan penilaian</h3><Button v-if="canWrite" label="Ajukan versi baru" icon="pi pi-plus" @click="policy" /></div>
        <p class="notice">Aktif: {{ data.aktif?.nama }}. Perubahan berlaku untuk penilaian berikutnya; penilaian lama menyimpan kebijakan asalnya.</p>
        <p>Kriteria penilaian memerlukan pengesahan UPR Pemda. Selera Risiko ditetapkan oleh Pemilik Risiko melalui menu Selera Risiko. Matriks tetap mengikuti Tabel 9 Perwal 1/2026.</p>
        <article v-for="r in data.items" :key="r.id" class="page-card"><h3>{{ r.nama }} <span class="status">{{ r.status }} · #{{ r.id }}</span></h3><p>{{ r.dasar }}</p><p>Berlaku {{ r.berlaku }} · Pengusul {{ r.pembuat }} · Penyetuju {{ r.penyetuju || '—' }}</p><p>Arsip selera saat pengajuan: {{ r.selera.join(', ') }}<br>Arsip toleransi: {{ r.toleransi.join(', ') }}</p>
          <details><summary>Kriteria penilaian</summary><p v-for="(values,key) in r.kriteria" :key="key"><strong>{{ key }}</strong><br><span v-for="(v,i) in values" :key="i">{{ i+1 }}. {{ v }}<br></span></p></details>
          <p v-if="r.catatan">Keputusan: {{ r.catatan }}</p><Button v-if="other(r)&&has('upr_pemda')" label="Tinjau dan putuskan" @click="form.decision('kebijakan',r)" />
        </article><p v-if="!data.items?.length">Belum ada kebijakan yang diajukan.</p>
      </section>
      <section v-if="tab==='penugasan'">
        <div class="toolbar"><h3>Struktur pengelola pada OPD terpilih</h3><Button v-if="auth.isAdmin" label="Tambah penugasan" @click="assignment" /></div>
        <p>Penugasan harus sesuai SK dan cakupan OPD akun SSO. Admin teknis tidak otomatis menjadi pejabat penyetuju.</p>
        <p>UPR atasannya menyetujui pembagian/penghindaran dan eskalasi risiko; atasan langsung menyetujui penerimaan risiko.</p>
        <div class="table-wrap"><table><thead><tr><th>Pejabat</th><th>Peran</th><th>Masa tugas</th><th>Dasar</th><th>Status</th></tr></thead><tbody><tr v-for="r in data" :key="r.id"><td>{{ r.nama }}<small>{{ r.username }}</small></td><td>{{ r.peran }}</td><td>{{ r.mulai }} – {{ r.selesai }}</td><td>{{ r.dasar }}</td><td>{{ r.aktif?'Aktif':'Nonaktif' }} <Button v-if="auth.isAdmin&&r.aktif" label="Nonaktifkan" text @click="deactivate(r)" /></td></tr></tbody></table></div>
      </section>
      <section v-if="tab==='laporan'">
        <div class="toolbar"><h3>Laporan triwulanan & tahunan</h3><Button v-if="canWrite||has('kepatuhan','komite','koordinator')" label="Susun laporan" @click="report" /></div>
        <p>Data dibekukan saat pengajuan. Untuk revisi, ajukan laporan baru. Pengesahan di aplikasi dicatat sebagai keputusan internal.</p>
        <article v-for="r in data" :key="r.id" class="page-card"><h3>{{ r.periode }} {{ r.tahun }} · {{ r.jenis }} · #{{ r.id }}</h3><p>{{ r.ringkasan }}</p><p>{{ r.status }} · Pengusul {{ r.pembuat }} · Penyetuju {{ r.penyetuju || '—' }}</p><router-link :to="{name:'laporan-berkala',params:{id:r.id}}">Buka / cetak laporan</router-link><Button v-if="reportDecision(r)" label="Tinjau dan putuskan" text @click="form.decision('laporan',r)" /></article>
        <p v-if="!data.length">Belum ada laporan.</p>
      </section>
      <section v-if="tab==='usulan-kamus'">
        <div class="toolbar"><h3>Usulan kamus risiko</h3><Button v-if="canWrite" label="Usulkan risiko" @click="proposal" /></div>
        <article v-for="r in data" :key="r.id" class="page-card"><h3>{{ r.nama }}</h3><p>{{ r.kategori }} · {{ r.status }}</p><p>{{ r.deskripsi }}</p><p>{{ r.catatan }}</p><Button v-if="other(r)&&has('upr','inspektorat')" label="Reviu usulan" @click="form.decision('usulan-kamus',r)" /></article><p v-if="!data.length">Belum ada usulan.</p>
      </section>
      <section v-if="tab==='audit'"><h3>Riwayat aktivitas terbaru</h3><p>Menampilkan maksimal 200 aktivitas pada OPD dan tahun terpilih.</p><div class="table-wrap"><table><thead><tr><th>Waktu</th><th>Pelaku</th><th>Aktivitas</th><th>Referensi</th></tr></thead><tbody><tr v-for="r in data" :key="r.id"><td>{{ r.created_at }}</td><td>{{ r.pelaku }}</td><td>{{ r.aksi }}</td><td>{{ r.entitas }} #{{ r.entitas_id }}</td></tr></tbody></table></div></section>
    </template>
    <GovernanceForm v-model:visible="visible" :title="title" :fields="fields" :initial="initial" :busy="busy" :error="formError" @submit="form.submit" />
  </section>
</template>
<style scoped>
.intro{margin-bottom:18px}.intro h2{margin-top:0}.tabs{display:flex;flex-wrap:wrap;gap:6px;border-bottom:1px solid #cbd5e1;margin-bottom:22px;padding-bottom:10px}.tabs button{padding:10px 14px;border:1px solid #cbd5e1;border-radius:6px;background:white;color:#334155;cursor:pointer}.tabs .active{background:#075985;color:white;border-color:#075985}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}.metrics div{background:#f0f9ff;border:1px solid #bae6fd;padding:18px;border-radius:8px}.metrics strong{display:block;font-size:2rem;color:#075985}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;border:1px solid #e2e8f0;text-align:left}th{background:#f1f5f9}small{display:block;color:#475569;margin-top:5px}.page-card{margin-bottom:14px}.status{font-size:.85rem;color:#475569}.notice{background:#fff7ed;padding:14px;border-left:4px solid #ea580c}.error{color:#b91c1c}
</style>
