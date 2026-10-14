<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import GovernanceForm from '@/components/GovernanceForm.vue'
import { useGovernance, field, message } from '@/composables/useGovernance'
import { useAuthStore } from '@/stores/auth'
import { useContextStore } from '@/stores/context'
import api from '@/api'
const route = useRoute(), auth = useAuthStore(), ctx = useContextStore()
const data = ref(null), roles = ref([]), error = ref(''), loading = ref(false), fraudData = ref(null)
const rid = () => Number(route.params.id)
const has = (...rs) => rs.some(r=>roles.value.includes(r))
const canWrite = ref(false)
const isFraud = computed(()=> /fraud|kecurangan/i.test(data.value?.risiko?.kategori_risiko || ''))
const other = r => r.status==='diajukan' && r.pembuat!==auth.user?.username
let loadId = 0
async function load() {
  const id = ++loadId
  loading.value=true; error.value=''; data.value=null; fraudData.value=null
  try {
    const result = await api.get(`/tata-kelola/risiko/${rid()}`)
    const access = await api.get('/tata-kelola/akses',{params:{opd_id:result.data.risiko.opd_id}})
    if (id !== loadId) return
    data.value=result.data; roles.value=access.data.peran; canWrite.value=access.data.boleh_tulis
    if(isFraud.value && has('upr','inspektorat')) {
      const response = await api.get(`/tata-kelola/risiko/${rid()}/fraud`)
      if(id===loadId) fraudData.value=response.data
    }
  }catch(e){if(id===loadId)error.value=message(e)}finally{if(id===loadId)loading.value=false}
}
const form=useGovernance(load)
const {visible,title,fields,initial,busy,error:formError}=form
watch(()=>route.params.id,()=>{visible.value=false;load()},{immediate:true})
// Detail mengikuti ID, bukan selector global; tampilkan konteks record secara eksplisit.
const mismatch = computed(()=>data.value && (data.value.risiko.opd_id!==ctx.opdId || data.value.risiko.tahun!==ctx.tahun))
const options = [1,2,3,4,5]
function assessment() {
  const id=rid()
  form.open('Catat penilaian risiko',[
    field('tahap','Tahap penilaian','select',{options:[{value:'awal',label:'Penilaian awal'},{value:'target',label:'Target setelah pengendalian'},{value:'residual',label:'Penilaian ulang / residual'}]}),
    field('dampak','Dampak','select',{options}),field('kemungkinan','Kemungkinan','select',{options}),
    field('alasan','Dasar penilaian dan pertimbangan','textarea'),
    field('bukti','Referensi bukti / lokasi dokumen','textarea',{optional:true,help:'Wajib untuk penilaian residual. Jangan masukkan token akses atau tautan rahasia.'}),
  ],d=>api.post(`/tata-kelola/risiko/${id}/penilaian`,d))
}
const responseLabels={kurangi_kemungkinan:'Kurangi kemungkinan',kurangi_dampak:'Kurangi dampak',bagi:'Bagi risiko',hindari:'Hindari risiko',terima:'Terima risiko'}
function response() {
  const id=rid()
  form.open('Ajukan respons risiko',[
    field('penilaian_id','Penilaian yang menjadi dasar','select',{options:data.value.penilaian.map(p=>({value:p.id,label:`#${p.id} ${p.tahap} · skor ${p.skor} · ${p.created_at}`}))}),
    field('opsi','Opsi respons','multi',{options:Object.entries(responseLabels).map(([value,label])=>({value,label}))}),
    field('alasan','Pertimbangan, kelayakan, dan alasan respons','textarea',{help:'Pembagian/penghindaran dan risiko target/residual yang melampaui batas diteruskan ke UPR atasannya. Penerimaan risiko memerlukan persetujuan atasan langsung.'}),
  ],d=>api.post(`/tata-kelola/risiko/${id}/respons`,d))
}
function action() {
  const id=rid()
  form.open('Tambah tindakan pengendalian',[field('uraian','Tindakan pengendalian','textarea'),field('pic','Penanggung jawab'),field('target','Target penyelesaian','date')],d=>api.post(`/tata-kelola/risiko/${id}/tindakan`,d))
}
function execute(r) {
  form.open('Catat pelaksanaan tindakan',[
    field('status','Status','select',{options:[{value:'berjalan',label:'Berjalan'},{value:'selesai',label:'Selesai, menunggu verifikasi'}]}),
    field('hasil','Hasil pelaksanaan','textarea'),field('bukti','Referensi bukti / lokasi dokumen','textarea',{optional:true,help:'Wajib jika tindakan dinyatakan selesai.'}),
  ],d=>api.post(`/tata-kelola/tindakan/${r.id}/pelaksanaan`,d),r)
}
function verify(r,type='tindakan') {
  form.open(type==='tindakan'?'Verifikasi efektivitas tindakan':'Verifikasi tindak lanjut reviu',[
    field('efektif','Hasil verifikasi','select',{options:[{value:true,label:'Efektif / memadai'},{value:false,label:'Belum efektif / perlu tindak lanjut'}]}),field('catatan','Dasar dan catatan verifikasi','textarea'),
  ],d=>api.post(`/tata-kelola/${type}/${r.id}/verifikasi`,d))
}
function review() {
  const id=rid()
  form.open('Catat hasil reviu',[
    field('jenis','Pelaksana reviu','select',{options:['kepatuhan','inspektorat'].filter(r=>has(r))}),
    field('temuan','Temuan','textarea'),field('rekomendasi','Rekomendasi','textarea'),field('target','Batas tindak lanjut','date'),
  ],d=>api.post(`/tata-kelola/risiko/${id}/reviu`,d))
}
function followup(r) {
  form.open('Tindak lanjut reviu',[field('tindak_lanjut','Tindak lanjut','textarea'),field('bukti','Referensi bukti','textarea')],d=>api.post(`/tata-kelola/reviu/${r.id}/tindak-lanjut`,d))
}
function fraud() {
  const id=rid()
  form.open('Skenario risiko fraud',[
    field('skenario','Skenario kecurangan potensial','textarea'),field('proses_rawan','Proses yang rawan','textarea'),
    field('kelemahan','Kelemahan pengendalian','textarea'),field('indikator','Indikator peringatan','textarea'),
  ],d=>api.put(`/tata-kelola/risiko/${id}/fraud`,d),fraudData.value || {})
}
function ranking() {
  const id=rid()
  form.open('Tetapkan urutan prioritas',[
    field('area_dampak','Area dampak','select',{options:data.value.kebijakan.kriteria?.area_dampak || []}),
    field('urutan_pimpinan','Urutan keputusan pimpinan','number',{min:1,max:9999,default:9999,help:'Digunakan jika skor, area dampak, dan kategori sama. Angka lebih kecil didahulukan.'}),
    field('alasan','Dasar keputusan prioritas','textarea'),
  ],d=>api.put(`/tata-kelola/risiko/${id}/urutan`,d),data.value.urutan || {})
}
</script>
<template>
  <div class="detail">
    <router-link :to="{name:'tata-kelola'}">← Pemantauan risiko</router-link>
    <p v-if="error" class="error" role="alert">{{ error }} <Button label="Coba lagi" text @click="load" /></p>
    <p v-if="loading" role="status">Memuat rincian risiko…</p>
    <template v-else-if="data">
      <p v-if="mismatch" class="notice">Halaman ini menampilkan risiko OPD #{{ data.risiko.opd_id }} tahun {{ data.risiko.tahun }}, sesuai tautan yang dibuka. Pilihan OPD/tahun di atas tidak mengubah identitas risiko ini.</p>
      <header class="page-card"><small>{{ data.risiko.kode_risiko }} · {{ data.risiko.tahun }} · {{ data.risiko.kategori_risiko }}</small><h2>{{ data.risiko.uraian_risiko }}</h2><p>{{ data.risiko.keterangan_risiko }}</p>
        <dl><dt>Tujuan / kegiatan</dt><dd>{{ data.risiko.tujuan_sasaran || data.risiko.kegiatan }}</dd><dt>Indikator</dt><dd>{{ data.risiko.indikator_kinerja || data.risiko.indikator_keluaran }}</dd><dt>Pemilik</dt><dd>{{ data.risiko.pemilik_risiko }}</dd><dt>Penyebab</dt><dd>{{ data.risiko.sebab_uraian }}</dd><dt>Dampak</dt><dd>{{ data.risiko.dampak_uraian }}</dd></dl>
      </header>
      <section class="page-card"><div class="toolbar"><h3>Pemeringkatan prioritas</h3><Button v-if="has('upr','upr_pemda')" label="Tetapkan urutan" @click="ranking" /></div><p>Urutan Form Prioritas: skor tertinggi → area dampak → kategori risiko → keputusan pimpinan.</p><p v-if="data.urutan">Area: {{ data.urutan.area_dampak }} · Urutan pimpinan: {{ data.urutan.urutan_pimpinan }}<br>{{ data.urutan.alasan }}</p><p v-else>Area dampak dan urutan pimpinan belum ditetapkan.</p></section>
      <section class="page-card"><div class="toolbar"><h3>Riwayat penilaian</h3><Button v-if="canWrite" label="Catat penilaian" @click="assessment" /></div>
        <p>Penilaian awal terhubung dengan Form Analisis. Target adalah perkiraan; residual adalah hasil penilaian ulang berbukti.</p>
        <p>Ambang selera saat ini: <strong>{{ data.kebijakan.selera_risiko?.ambang ?? 'Belum ditetapkan' }}</strong>. <router-link :to="{name:'selera-risiko'}">Kelola Selera Risiko</router-link>. Riwayat di bawah mengikuti ambang saat penilaian dibuat.</p>
        <div class="table-wrap"><table><thead><tr><th>Tahap / waktu</th><th>Dampak / kemungkinan</th><th>Skor</th><th>Hasil</th><th>Dasar & kebijakan</th></tr></thead><tbody><tr v-for="p in data.penilaian" :key="p.id"><td>#{{ p.id }} {{ p.tahap }}<small>{{ p.created_at }} · {{ p.pembuat }}</small></td><td>{{ p.dampak }} / {{ p.kemungkinan }}</td><td>{{ p.skor }}</td><td>{{ p.prioritas?'Prioritas':'Dalam selera / keputusan UPR' }}<br>{{ p.di_luar_toleransi?'Melampaui toleransi':'' }}</td><td>{{ p.alasan }}<small>{{ p.kebijakan_snapshot.nama }}</small><small>Ambang saat penilaian: {{ p.kebijakan_snapshot.selera_risiko?.ambang ?? 'Arsip kebijakan lama' }}</small><small v-if="p.bukti">Bukti: {{ p.bukti }}</small></td></tr></tbody></table></div>
        <p v-if="!data.penilaian.length">Belum ada riwayat baru. Skor formulir lama: {{ data.analisis?.skala_risiko ?? 'Belum dinilai' }}.</p>
      </section>
      <section class="page-card"><div class="toolbar"><h3>Respons & persetujuan</h3><Button v-if="canWrite" label="Ajukan respons" :disabled="!data.penilaian.length" @click="response" /></div>
        <article v-for="r in data.respons" :key="r.id"><h4>{{ r.opsi.map(x=>responseLabels[x]).join(' + ') }} · {{ r.status }}</h4><p>{{ r.alasan }}</p><p>Dasar penilaian #{{ r.penilaian_id }} · Kewenangan: {{ r.peran_penyetuju }} · Pengusul: {{ r.pembuat }}</p><p v-if="r.catatan">{{ r.penyetuju }}: {{ r.catatan }}</p><Button v-if="other(r)&&has(r.peran_penyetuju)" label="Tinjau dan putuskan" @click="form.decision('respons',r)" /></article><p v-if="!data.respons.length">Belum ada pengajuan respons.</p>
      </section>
      <section class="page-card"><div class="toolbar"><h3>Tindakan pengendalian</h3><Button v-if="canWrite" label="Tambah tindakan" @click="action" /></div>
        <details v-if="data.rtp_lama"><summary>RTP dari formulir sebelumnya</summary><p>Pengendalian: {{ data.rtp_lama.pengendalian_ada }}</p><p>Celah: {{ data.rtp_lama.celah_pengendalian }}</p><p>Rencana: {{ data.rtp_lama.rencana_tindak }} · Target: {{ data.rtp_lama.target_waktu }}</p></details>
        <article v-for="r in data.tindakan" :key="r.id"><h4>{{ r.uraian }}</h4><p>{{ r.pic }} · Target {{ r.target }} · {{ r.status }}</p><p v-if="r.hasil">Hasil: {{ r.hasil }}</p><p v-if="r.bukti">Bukti: {{ r.bukti }}</p><p v-if="r.pemeriksa">{{ r.efektif?'Efektif':'Belum efektif' }} — {{ r.pemeriksa }}: {{ r.verifikasi }}</p><div class="buttons"><Button v-if="canWrite&&r.status!=='terverifikasi'" label="Catat pelaksanaan" @click="execute(r)" /><Button v-if="r.status==='selesai'&&has('upr','kepatuhan','inspektorat')&&r.pembuat!==auth.user?.username&&r.pelaksana!==auth.user?.username" label="Verifikasi" severity="secondary" @click="verify(r)" /></div></article><p v-if="!data.tindakan.length">Belum ada rincian tindakan baru.</p>
      </section>
      <section class="page-card"><div class="toolbar"><h3>Reviu & tindak lanjut</h3><Button v-if="has('kepatuhan','inspektorat')" label="Catat reviu" @click="review" /></div>
        <article v-for="r in data.reviu" :key="r.id"><h4>{{ r.jenis }} · {{ r.status }}</h4><p>{{ r.temuan }}</p><p>Rekomendasi: {{ r.rekomendasi }} · Target {{ r.target }}</p><p v-if="r.tindak_lanjut">Tindak lanjut: {{ r.tindak_lanjut }}<br>Bukti: {{ r.bukti }}</p><p v-if="r.catatan_verifikasi">Verifikasi: {{ r.catatan_verifikasi }}</p><div class="buttons"><Button v-if="canWrite&&r.status!=='ditutup'" label="Tindak lanjut" @click="followup(r)" /><Button v-if="has(r.jenis)&&r.status==='ditindaklanjuti'&&r.penindak!==auth.user?.username" label="Verifikasi tindak lanjut" @click="verify(r,'reviu')" /></div></article><p v-if="!data.reviu.length">Belum ada catatan reviu.</p>
      </section>
      <section class="page-card"><h3>Kejadian risiko</h3><p>Laporan yang telah divalidasi dan disalin ke Monitoring Event tampil di sini. Kejadian baru menjadi pengingat untuk menilai ulang pengendalian.</p><article v-for="r in data.kejadian" :key="r.id"><strong>{{ r.tanggal_terjadi }}</strong><p>Penyebab: {{ r.sebab_kejadian }}</p><p>Dampak: {{ r.dampak_kejadian }}</p></article><p v-if="!data.kejadian.length">Belum ada kejadian tercatat.</p></section>
      <section v-if="isFraud&&has('upr','inspektorat')" class="page-card"><div class="toolbar"><h3>Analisis fraud — akses terbatas</h3><Button label="Catat skenario" @click="fraud" /></div><p>Skenario merupakan potensi risiko yang perlu diverifikasi.</p><dl v-if="fraudData"><dt>Skenario</dt><dd>{{ fraudData.skenario }}</dd><dt>Proses rawan</dt><dd>{{ fraudData.proses_rawan }}</dd><dt>Kelemahan</dt><dd>{{ fraudData.kelemahan }}</dd><dt>Indikator</dt><dd>{{ fraudData.indikator }}</dd></dl></section>
    </template>
    <GovernanceForm v-model:visible="visible" :title="title" :fields="fields" :initial="initial" :busy="busy" :error="formError" @submit="form.submit" />
  </div>
</template>
<style scoped>
.page-card{margin:16px 0}.toolbar,.buttons{display:flex;align-items:center;justify-content:space-between;gap:12px}.buttons{justify-content:flex-start;flex-wrap:wrap}dl{display:grid;grid-template-columns:160px 1fr;gap:10px}dt{font-weight:600}dd{margin:0;white-space:pre-wrap}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse}td,th{padding:10px;border:1px solid #e2e8f0;text-align:left}th{background:#f1f5f9}small{display:block;color:#475569}article{border-top:1px solid #cbd5e1;padding:12px 0}p{white-space:pre-wrap}.error{color:#b91c1c}.notice{padding:12px;background:#fff7ed}@media(max-width:600px){dl{grid-template-columns:1fr}.toolbar{align-items:flex-start;flex-direction:column}}
</style>
