import{I as E,a8 as A,N as L,o,c as m,H as _,V as N,d as w,t as l,b as F,_ as U,u as M,a2 as G,h as P,w as z,Z as W,a,a3 as K,q as f,l as u,s as V,x as H,F as Z,r as q,i as C,j as O,m as J,g as X,a6 as Q}from"./index-B_qXiYdG.js";import{s as T}from"./index-DAfFIxXY.js";import{s as Y}from"./index-Cb8EUOr-.js";var aa=`
    .p-progressbar {
        display: block;
        position: relative;
        overflow: hidden;
        height: dt('progressbar.height');
        background: dt('progressbar.background');
        border-radius: dt('progressbar.border.radius');
    }

    .p-progressbar-value {
        margin: 0;
        background: dt('progressbar.value.background');
    }

    .p-progressbar-label {
        color: dt('progressbar.label.color');
        font-size: dt('progressbar.label.font.size');
        font-weight: dt('progressbar.label.font.weight');
    }

    .p-progressbar-determinate .p-progressbar-value {
        height: 100%;
        width: 0%;
        position: absolute;
        display: none;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        transition: width 1s ease-in-out;
    }

    .p-progressbar-determinate .p-progressbar-label {
        display: inline-flex;
    }

    .p-progressbar-indeterminate .p-progressbar-value::before {
        content: '';
        position: absolute;
        background: inherit;
        inset-block-start: 0;
        inset-inline-start: 0;
        inset-block-end: 0;
        will-change: inset-inline-start, inset-inline-end;
        animation: p-progressbar-indeterminate-anim 2.1s cubic-bezier(0.65, 0.815, 0.735, 0.395) infinite;
    }

    .p-progressbar-indeterminate .p-progressbar-value::after {
        content: '';
        position: absolute;
        background: inherit;
        inset-block-start: 0;
        inset-inline-start: 0;
        inset-block-end: 0;
        will-change: inset-inline-start, inset-inline-end;
        animation: p-progressbar-indeterminate-anim-short 2.1s cubic-bezier(0.165, 0.84, 0.44, 1) infinite;
        animation-delay: 1.15s;
    }

    @keyframes p-progressbar-indeterminate-anim {
        0% {
            inset-inline-start: -35%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
        100% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
    }
    @-webkit-keyframes p-progressbar-indeterminate-anim {
        0% {
            inset-inline-start: -35%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
        100% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
    }

    @keyframes p-progressbar-indeterminate-anim-short {
        0% {
            inset-inline-start: -200%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
        100% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
    }
    @-webkit-keyframes p-progressbar-indeterminate-anim-short {
        0% {
            inset-inline-start: -200%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
        100% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
    }
`,ea={root:function(d){var p=d.instance;return["p-progressbar p-component",{"p-progressbar-determinate":p.determinate,"p-progressbar-indeterminate":p.indeterminate}]},value:"p-progressbar-value",label:"p-progressbar-label"},na=E.extend({name:"progressbar",style:aa,classes:ea}),sa={name:"BaseProgressBar",extends:A,props:{value:{type:Number,default:null},mode:{type:String,default:"determinate"},showValue:{type:Boolean,default:!0}},style:na,provide:function(){return{$pcProgressBar:this,$parentInstance:this}}},j={name:"ProgressBar",extends:sa,inheritAttrs:!1,computed:{progressStyle:function(){return{width:this.value+"%",display:"flex"}},indeterminate:function(){return this.mode==="indeterminate"},determinate:function(){return this.mode==="determinate"},dataP:function(){return L({determinate:this.determinate,indeterminate:this.indeterminate})}}},ta=["aria-valuenow","data-p"],ia=["data-p"],da=["data-p"],ra=["data-p"];function la(n,d,p,b,g,i){return o(),m("div",_({role:"progressbar",class:n.cx("root"),"aria-valuemin":"0","aria-valuenow":n.value,"aria-valuemax":"100","data-p":i.dataP},n.ptmi("root")),[i.determinate?(o(),m("div",_({key:0,class:n.cx("value"),style:i.progressStyle,"data-p":i.dataP},n.ptm("value")),[n.value!=null&&n.value!==0&&n.showValue?(o(),m("div",_({key:0,class:n.cx("label"),"data-p":i.dataP},n.ptm("label")),[N(n.$slots,"default",{},function(){return[w(l(n.value+"%"),1)]})],16,da)):F("",!0)],16,ia)):i.indeterminate?(o(),m("div",_({key:1,class:n.cx("value"),"data-p":i.dataP},n.ptm("value")),null,16,ra)):F("",!0)],16,ta)}j.render=la;const oa={class:"generate-rtp-page"},pa={class:"header-card"},ca={class:"header-actions"},ua={key:1,class:"content-grid"},ma={class:"panel-left"},va={class:"card meta-card"},fa={class:"card-header"},ba={class:"meta-list"},ga={class:"meta-row"},ka={class:"meta-value highlight"},ha={class:"meta-row"},ya={class:"meta-value"},Pa={class:"meta-row"},_a={class:"meta-value"},wa={class:"meta-row"},Ia={class:"meta-value"},Ra={class:"meta-row"},Da={class:"meta-value text-small"},Ta={class:"card structure-card"},Fa={class:"card-header"},Ba={class:"panel-right"},xa={class:"card attachments-card"},Sa={class:"card-header"},Ka={class:"selection-control"},Va={for:"selectAllForms",class:"label-select-all"},Ca={class:"forms-grid"},Oa=["onClick"],ja={class:"item-check"},$a={class:"item-info"},Ea={class:"item-top"},Aa={class:"item-code"},La={class:"item-title"},Na={class:"item-desc"},Ua={class:"card summary-action-card"},Ma={class:"summary-details"},Ga={class:"stat-box"},za={class:"stat-num"},Wa={class:"stat-box"},Ha={class:"stat-num"},Za={class:"action-btn-row"},qa={key:0,class:"generating-progress"},Ja={__name:"GenerateRtp",setup(n){const d=M(),p=G(),b=P(!1),g=P(!1),i=P(null),v=P(!0),k=[{key:"f1a",form:"Form 1.a",label:"Rekap Kuesioner CEE (Persepsi)",desc:"Hasil survei persepsi responden terhadap 8 sub-unsur CEE"},{key:"f1b",form:"Form 1.b",label:"Reviu Dokumen CEE",desc:"Analisis kondisi kerentanan berdasarkan reviu dokumen"},{key:"f1c",form:"Form 1.c",label:"Simpulan CEE",desc:"Simpulan gabungan survei persepsi dan reviu dokumen"},{key:"f6",form:"Form 6",label:"RTP atas CEE",desc:"Rencana tindak pengendalian atas kelemahan lingkungan pengendalian"},{key:"f2a",form:"Form 2.a",label:"Konteks Strategis Pemda",desc:"Visi, misi, sasaran, dan prioritas pembangunan Kota Tegal"},{key:"f2b",form:"Form 2.b",label:"Konteks Strategis OPD",desc:"Tujuan, sasaran, IKU, dan program strategis perangkat daerah"},{key:"f2c",form:"Form 2.c",label:"Konteks Operasional OPD",desc:"Pemetaan subkegiatan dan indikator operasional Renja"},{key:"f3a",form:"Form 3.a",label:"Identifikasi Risiko Strategis Pemda",desc:"Daftar risiko strategis Pemerintah Kota Tegal"},{key:"f3b",form:"Form 3.b",label:"Identifikasi Risiko Strategis OPD",desc:"Identifikasi risiko strategis perangkat daerah"},{key:"f3c",form:"Form 3.c",label:"Identifikasi Risiko Operasional OPD",desc:"Identifikasi risiko kegiatan dan subkegiatan operasional"},{key:"f4",form:"Form 4",label:"Analisis Risiko",desc:"Penilaian kemungkinan, dampak, skala, dan level risiko 5x5"},{key:"f5",form:"Form 5",label:"Daftar Risiko Prioritas",desc:"Risiko-risiko prioritas yang wajib ditangani dalam RTP"},{key:"f7",form:"Form 7",label:"RTP atas Risiko",desc:"Rencana tindak mitigasi dan pengendalian risiko prioritas"},{key:"f8",form:"Form 8",label:"Informasi & Komunikasi",desc:"Rencana sarana dan media pengkomunikasian pengendalian"},{key:"f9",form:"Form 9",label:"Rencana Pemantauan PI",desc:"Metode dan penanggung jawab pemantauan pengendalian intern"},{key:"f10",form:"Form 10",label:"Monitoring Event & RTP",desc:"Pencatatan kejadian risiko nyata dan pelaksanaan mitigasi"}],s=P(k.map(r=>r.key)),I=O({get:()=>s.value.length===k.length,set:r=>{s.value=r?k.map(e=>e.key):[]}}),R=O(()=>{var r,e;return((r=i.value)==null?void 0:r.nama_pd)||((e=d.opd)==null?void 0:e.nama_pd)||"-"});async function B(){if(d.opdId){b.value=!0;try{const r=await C.get("/master/opd-print-context",{params:{opd_id:d.opdId}});i.value=r.data||{}}catch{i.value={}}finally{b.value=!1}}}z([()=>d.opdId,()=>d.tahun],B),W(B);async function x(){if(!d.opdId){p.add({severity:"warn",summary:"Pilih OPD",detail:"Silakan pilih OPD terlebih dahulu",life:3e3});return}if(!v.value&&!s.value.length){p.add({severity:"warn",summary:"Tidak Ada Konten",detail:"Pilih minimal satu bagian atau sertakan Dokumen Utama",life:3e3});return}g.value=!0;try{const r=await C.get("/laporan/rtp-docx",{params:{opd_id:d.opdId,tahun:d.tahun,forms:s.value.join(","),include_main:v.value},responseType:"blob"}),h=`Dokumen_RTP_${R.value.replace(/[^a-zA-Z0-9_-]/g,"_")}_${d.tahun}.docx`,y=window.URL.createObjectURL(new Blob([r.data])),c=document.createElement("a");c.href=y,c.setAttribute("download",h),document.body.appendChild(c),c.click(),c.remove(),window.URL.revokeObjectURL(y),p.add({severity:"success",summary:"Berhasil Generate RTP",detail:`File Word ${h} berhasil diunduh.`,life:4e3})}catch{p.add({severity:"error",summary:"Gagal Generate",detail:"Terjadi kesalahan saat menyusun dokumen RTP. Periksa koneksi backend.",life:5e3})}finally{g.value=!1}}return(r,e)=>{var h,y,c,S;return o(),m("div",oa,[a("div",pa,[e[3]||(e[3]=K('<div class="header-left" data-v-df498fba><div class="icon-wrap" data-v-df498fba><i class="pi pi-file-word" data-v-df498fba></i></div><div data-v-df498fba><h1 class="page-title" data-v-df498fba>Generate Dokumen RTP</h1><p class="page-subtitle" data-v-df498fba> Penyusunan Rencana Tindak Pengendalian (RTP) Resmi format Microsoft Word (.docx) berbasis template docxtpl dilengkapi seluruh Lampiran Form 1.a sampai Form 10. </p></div></div>',1)),a("div",ca,[f(u(V),{label:"Generate Dokumen Word (.docx)",icon:"pi pi-download",size:"large",class:"btn-generate-main",loading:g.value,disabled:b.value||!v.value&&!s.value.length,onClick:x},null,8,["loading","disabled"])])]),b.value?(o(),H(Q,{key:0,label:"Memuat profil dan konteks dokumen…"})):(o(),m("div",ua,[a("div",ma,[a("div",va,[a("div",fa,[e[4]||(e[4]=a("span",{class:"card-title"},[a("i",{class:"pi pi-id-card card-icon"}),w(" Identitas & Penandatangan Dokumen ")],-1)),f(u(Y),{value:`Tahun ${u(d).tahun}`,severity:"info",class:"year-tag"},null,8,["value"])]),a("div",ba,[a("div",ga,[e[5]||(e[5]=a("span",{class:"meta-label"},"Organisasi Perangkat Daerah",-1)),a("span",ka,l(R.value),1)]),a("div",ha,[e[6]||(e[6]=a("span",{class:"meta-label"},"Kepala OPD",-1)),a("span",ya,l(((h=i.value)==null?void 0:h.nama_kepala)||"-"),1)]),a("div",Pa,[e[7]||(e[7]=a("span",{class:"meta-label"},"NIP",-1)),a("span",_a,l(((y=i.value)==null?void 0:y.nip_kepala)||"-"),1)]),a("div",wa,[e[8]||(e[8]=a("span",{class:"meta-label"},"Jabatan Penandatangan",-1)),a("span",Ia,l(((c=i.value)==null?void 0:c.jabatan_kepala)||`Kepala ${R.value}`),1)]),a("div",Ra,[e[9]||(e[9]=a("span",{class:"meta-label"},"Bidang Urusan",-1)),a("span",Da,l(((S=i.value)==null?void 0:S.bidang_urusan)||"-"),1)])])]),a("div",Ta,[a("div",Fa,[e[10]||(e[10]=a("span",{class:"card-title"},[a("i",{class:"pi pi-book card-icon"}),w(" Dokumen Utama RTP (Word Template) ")],-1)),f(u(T),{modelValue:v.value,"onUpdate:modelValue":e[0]||(e[0]=t=>v.value=t),binary:"",inputId:"mainDocToggle"},null,8,["modelValue"])]),e[11]||(e[11]=K('<p class="section-desc" data-v-df498fba> Menggunakan template baku Pemerintah Kota Tegal (docxtpl) dengan logo Pemkot, tipografi resmi Times New Roman, dan pembagian bab naratif: </p><div class="chapters-timeline" data-v-df498fba><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>Cover</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>Cover &amp; Identitas Dokumen</strong><span data-v-df498fba>Lambang Pemkot Tegal, nama OPD, dan tahun anggaran</span></div></div><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>I</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>BAB I — Pendahuluan</strong><span data-v-df498fba>Latar belakang, tupoksi organisasi, dasar hukum, maksud, tujuan &amp; manfaat</span></div></div><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>II</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>BAB II — Lingkungan Pengendalian</strong><span data-v-df498fba>Penciptaan lingkungan pengendalian (CEE) 8 sub-unsur</span></div></div><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>III</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>BAB III — Penilaian &amp; Pengendalian Risiko</strong><span data-v-df498fba>Penerapan SPIP, identifikasi risiko, hasil analisis, mitigasi</span></div></div><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>IV</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>BAB IV — Informasi, Komunikasi &amp; Pemantauan</strong><span data-v-df498fba>Sarana komunikasi, media penyampaian, dan rencana monitoring PI</span></div></div><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>V</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>BAB V — Penutup</strong><span data-v-df498fba>Kesimpulan dan lembar pengesahan tanda tangan Kepala OPD</span></div></div><div class="chap-item" data-v-df498fba><div class="chap-badge" data-v-df498fba>KK</div><div class="chap-content" data-v-df498fba><strong data-v-df498fba>Kertas Kerja RTP</strong><span data-v-df498fba>Halaman pembuka kertas kerja &amp; rincian identitas OPD</span></div></div></div>',2))])]),a("div",Ba,[a("div",xa,[a("div",Sa,[e[12]||(e[12]=a("div",null,[a("span",{class:"card-title"},[a("i",{class:"pi pi-paperclip card-icon"}),w(" Lampiran Kertas Kerja (Printout Form) ")]),a("p",{class:"card-subtitle"}," Tiap form disusun dengan tabel lengkap, cell shading, batas kolom terstruktur, dan tanda tangan resmi. ")],-1)),a("div",Ka,[f(u(T),{modelValue:I.value,"onUpdate:modelValue":e[1]||(e[1]=t=>I.value=t),binary:"",inputId:"selectAllForms"},null,8,["modelValue"]),a("label",Va,l(I.value?"Hapus Semua":"Pilih Semua"),1)])]),a("div",Ca,[(o(),m(Z,null,q(k,t=>a("div",{key:t.key,class:J(["form-item-box",{active:s.value.includes(t.key)}]),onClick:$=>s.value.includes(t.key)?s.value=s.value.filter(D=>D!==t.key):s.value.push(t.key)},[a("div",ja,[f(u(T),{modelValue:s.value.includes(t.key),binary:"",onClick:e[2]||(e[2]=X(()=>{},["stop"])),onChange:$=>s.value.includes(t.key)?s.value=s.value.filter(D=>D!==t.key):s.value.push(t.key)},null,8,["modelValue","onChange"])]),a("div",$a,[a("div",Ea,[a("span",Aa,l(t.form),1),a("span",La,l(t.label),1)]),a("p",Na,l(t.desc),1)])],10,Oa)),64))])]),a("div",Ua,[a("div",Ma,[a("div",Ga,[a("span",za,l(v.value?"1 Dokumen":"0"),1),e[13]||(e[13]=a("span",{class:"stat-lbl"},"Dokumen Narasi Utama",-1))]),e[15]||(e[15]=a("div",{class:"stat-divider"},null,-1)),a("div",Wa,[a("span",Ha,l(s.value.length)+" / "+l(k.length),1),e[14]||(e[14]=a("span",{class:"stat-lbl"},"Form Lampiran Terpilih",-1))]),e[16]||(e[16]=a("div",{class:"stat-divider"},null,-1)),e[17]||(e[17]=a("div",{class:"stat-box"},[a("span",{class:"stat-num"},".DOCX"),a("span",{class:"stat-lbl"},"Format Microsoft Word")],-1))]),a("div",Za,[f(u(V),{label:"Generate & Unduh Dokumen RTP (.docx)",icon:"pi pi-download",class:"btn-download-big",loading:g.value,disabled:b.value||!v.value&&!s.value.length,onClick:x},null,8,["loading","disabled"])]),g.value?(o(),m("div",qa,[f(u(j),{mode:"indeterminate",style:{height:"6px"}}),e[18]||(e[18]=a("span",{class:"progress-txt"},"Sedang menyusun dan merender dokumen Word via docxtpl…",-1))])):F("",!0)])])]))])}}},ae=U(Ja,[["__scopeId","data-v-df498fba"]]);export{ae as default};
