<script setup>
import { ref, watch } from 'vue'
import { statusLabel, responLabel } from '@/utils/rtp'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import { message } from '@/composables/useGovernance'
import { formatDate, formatDateTime } from '@/utils/date'
const route=useRoute(), report=ref(null), error=ref(''), loading=ref(false)
let serial=0
async function load(){
  const s=++serial; loading.value=true; error.value=''; report.value=null
  try{const {data}=await api.get(`/tata-kelola/laporan/${route.params.id}`);if(s===serial)report.value=data}
  catch(e){if(s===serial)error.value=message(e)}finally{if(s===serial)loading.value=false}
}
watch(()=>route.params.id,load,{immediate:true})
const print=()=>window.print()
function risk(id){return report.value?.snapshot.risiko.find(r=>r.id===id)?.kode_risiko || `#${id}`}
const sections=[
  {key:'urutan',title:'Dasar pemeringkatan prioritas',columns:[['risiko_id','Risiko'],['area_dampak','Area dampak'],['urutan_pimpinan','Urutan pimpinan'],['alasan','Dasar keputusan'],['pembuat','Pejabat']]},
  {key:'risiko',title:'Register risiko',columns:[['opd_id','OPD'],['kode_risiko','Kode'],['jenis_risiko','Tingkat'],['tujuan_sasaran','Tujuan / sasaran'],['kegiatan','Kegiatan'],['uraian_risiko','Risiko'],['pemilik_risiko','Pemilik'],['sebab_uraian','Penyebab'],['dampak_uraian','Dampak']]},
  {key:'analisis',title:'Penilaian awal terkini',columns:[['risiko_id','Risiko'],['skala_dampak','Dampak'],['skala_kemungkinan','Kemungkinan'],['skala_risiko','Skor'],['is_prioritas','Prioritas']]},
  {key:'penilaian',title:'Riwayat penilaian dan risiko residual',columns:[['risiko_id','Risiko'],['tahap','Tahap'],['skor','Skor'],['prioritas','Prioritas'],['di_luar_toleransi','Melampaui toleransi'],['alasan','Dasar penilaian'],['bukti','Bukti'],['created_at','Waktu']]},
  {key:'respons',title:'Respons dan keputusan',columns:[['risiko_id','Risiko'],['opsi','Opsi'],['alasan','Alasan'],['status','Status'],['penyetuju','Penyetuju'],['catatan','Catatan']]},
  {key:'rtp_lama',title:'RTP dari formulir sebelumnya',columns:[['risiko_id','Risiko'],['status_pengendalian','Status kegiatan'],['pengendalian_ada','Pengendalian'],['bukti_judul','Judul bukti'],['bukti_link','Link bukti'],['bukti_nama','Berkas bukti'],['respon_risiko','Respon Risiko'],['celah_pengendalian','Celah'],['rencana_tindak','Rencana'],['target_waktu','Target'],['realisasi_waktu','Realisasi']]},
  {key:'tindakan',title:'Pelaksanaan dan efektivitas pengendalian',columns:[['risiko_id','Risiko'],['uraian','Tindakan'],['pic','PIC'],['target','Target'],['status','Status'],['hasil','Hasil'],['bukti','Bukti'],['efektif','Efektif'],['verifikasi','Verifikasi']]},
  {key:'reviu',title:'Pemantauan, reviu, dan tindak lanjut',columns:[['risiko_id','Risiko'],['jenis','Pelaksana'],['temuan','Temuan'],['rekomendasi','Rekomendasi'],['target','Target'],['tindak_lanjut','Tindak lanjut'],['bukti','Bukti'],['status','Status'],['catatan_verifikasi','Verifikasi']]},
  {key:'kejadian',title:'Kejadian dalam periode laporan',columns:[['risiko_id','Risiko'],['tanggal_terjadi','Tanggal'],['sebab_kejadian','Penyebab'],['dampak_kejadian','Dampak'],['realisasi_pelaksanaan_rtp','Pelaksanaan RTP']]},
]
function value(row,key){
  if(key==='status_pengendalian')return row[key]?statusLabel(row[key]):'—';
  if(key==='respon_risiko')return row[key]?responLabel(row[key]):'—';
  if(key==='risiko_id')return risk(row[key]);
  if(key==='opd_id')return report.value.snapshot.opd_sumber?.find(o=>o.id_sub_pd===row[key])?.nama_pd || row[key];
  if(key==='tanggal_terjadi'||key==='target_waktu'||key==='realisasi_waktu')return row[key]?formatDate(row[key]):'—';
  if(key==='created_at'||key==='decided_at')return row[key]?formatDateTime(row[key]):'—';
  const v=row[key];
  if(typeof v==='boolean')return v?'Ya':'Tidak';
  return Array.isArray(v)?v.join(', '):(v??'—')
}
</script>
<template>
  <div class="report">
    <div class="no-print toolbar"><router-link :to="{name:'tata-kelola'}">← Tata Kelola Risiko</router-link><Button label="Cetak / simpan PDF" icon="pi pi-print" :disabled="!report" @click="print" /></div>
    <p v-if="error" role="alert">{{ error }}</p><p v-if="loading">Memuat laporan…</p>
    <template v-if="report">
      <header><p>PEMERINTAH KOTA TEGAL</p><h2>{{ report.snapshot.opd?.nama_pd }}</h2><h3>Laporan {{ {penilaian:'Pelaksanaan Penilaian Risiko',upr:'Pengelolaan Risiko oleh UPR',kepatuhan:'Pemantauan Unit Kepatuhan',pembinaan:'Pembinaan Komite'}[report.jenis] }}</h3><p>{{ report.periode }} · {{ report.tahun }} · Dokumen #{{ report.id }}</p><strong>{{ report.status==='disetujui'?'DISETUJUI SECARA INTERNAL':report.status.toUpperCase()+' — BELUM DISAHKAN' }}</strong></header>
      <p>Kepada: {{ report.penerima }}<br>Tembusan: {{ report.tembusan }}</p>
      <h3>Ringkasan</h3><p class="narrative">{{ report.ringkasan }}</p>
      <p v-if="report.snapshot.cakupan==='pemda'">Kompilasi risiko strategis Pemda. OPD sumber: {{ report.snapshot.opd_sumber.map(o=>o.nama_pd).join('; ') }}.</p>
      <p>Kebijakan: {{ report.snapshot.kebijakan?.nama }}<br>Periode kejadian: {{ formatDate(report.snapshot.awal) }} – {{ formatDate(report.snapshot.akhir) }}<br>Data dicatat pada: {{ formatDateTime(report.snapshot.dicatat_pada) }}</p>
      <p class="note">{{ report.snapshot.catatan }}</p>
      <section v-if="report.snapshot.selera_risiko"><h3>Selera Risiko saat laporan dibuat</h3><template v-for="(settings,opd) in report.snapshot.selera_risiko" :key="opd"><p>{{ report.snapshot.opd_sumber?.find(o=>String(o.id_sub_pd)===opd)?.nama_pd || opd }}</p><p v-if="!settings.length">Belum ditetapkan.</p><ul><li v-for="s in settings" :key="s.id">{{ s.pemilik_risiko || 'Tingkat entitas' }}: ambang {{ s.ambang }} · Penetap: {{ s.penetap }} · Pertimbangan: {{ s.pertimbangan_sumber_daya }}</li></ul></template></section>
      <section v-for="s in sections" :key="s.key"><h3>{{ s.title }}</h3><div class="table-wrap"><table v-if="report.snapshot[s.key]?.length"><thead><tr><th v-for="c in s.columns" :key="c[0]">{{ c[1] }}</th></tr></thead><tbody><tr v-for="(r,i) in report.snapshot[s.key]" :key="i"><td v-for="c in s.columns" :key="c[0]">{{ value(r,c[0]) }}</td></tr></tbody></table><p v-else>Belum ada data tercatat.</p></div></section>
      <footer><p>Disusun oleh: {{ report.pembuat }} pada {{ formatDateTime(report.created_at) }}</p><p v-if="report.penyetuju">Keputusan oleh: {{ report.penyetuju }} pada {{ formatDateTime(report.decided_at) }}<br>{{ report.catatan }}</p><p>Persetujuan internal aplikasi tercatat dalam riwayat aktivitas. Dokumen ini tidak memuat tanda tangan elektronik tersertifikasi.</p></footer>

    </template>
  </div>
</template>
<style scoped>
.report{background:white;padding:24px;color:#0f172a}.toolbar{display:flex;justify-content:space-between;gap:12px}header{text-align:center;border-bottom:2px solid #334155;padding:20px}section{margin:26px 0}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:.8rem;border:1px solid #e2e8f0}td,th{border:1px solid #e2e8f0;padding:8px;text-align:left;vertical-align:top;overflow-wrap:anywhere;white-space:pre-wrap}th{background:#f8fafc;color:#1e293b;font-weight:600}tbody tr:nth-child(even){background:#f8fafc}tbody tr:hover{background:#f1f5f9}.narrative{white-space:pre-wrap}.note,footer{font-size:.85rem;color:#475569}@media print{.report{padding:0}.table-wrap{overflow:visible}table{font-size:8pt}thead{display:table-header-group}tr{break-inside:avoid}h3{break-after:avoid}.no-print{display:none}}
</style>
