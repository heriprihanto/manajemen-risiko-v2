import{I as E,a9 as A,N,o,c as m,H as _,V as U,d as w,t as d,b as F,_ as L,u as G,a2 as M,h as P,w as z,Z as W,a,a3 as K,q as g,l as u,s as V,x as H,F as Z,r as q,i as C,j as O,m as J,g as X,a7 as Q}from"./index-LsPIulEd.js";import{s as T}from"./index-DmbB7-e7.js";import{s as Y}from"./index-QiBA7Mry.js";var aa=`
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
`,ea={root:function(r){var c=r.instance;return["p-progressbar p-component",{"p-progressbar-determinate":c.determinate,"p-progressbar-indeterminate":c.indeterminate}]},value:"p-progressbar-value",label:"p-progressbar-label"},na=E.extend({name:"progressbar",style:aa,classes:ea}),sa={name:"BaseProgressBar",extends:A,props:{value:{type:Number,default:null},mode:{type:String,default:"determinate"},showValue:{type:Boolean,default:!0}},style:na,provide:function(){return{$pcProgressBar:this,$parentInstance:this}}},j={name:"ProgressBar",extends:sa,inheritAttrs:!1,computed:{progressStyle:function(){return{width:this.value+"%",display:"flex"}},indeterminate:function(){return this.mode==="indeterminate"},determinate:function(){return this.mode==="determinate"},dataP:function(){return N({determinate:this.determinate,indeterminate:this.indeterminate})}}},ta=["aria-valuenow","data-p"],ia=["data-p"],ra=["data-p"],la=["data-p"];function da(n,r,c,f,k,i){return o(),m("div",_({role:"progressbar",class:n.cx("root"),"aria-valuemin":"0","aria-valuenow":n.value,"aria-valuemax":"100","data-p":i.dataP},n.ptmi("root")),[i.determinate?(o(),m("div",_({key:0,class:n.cx("value"),style:i.progressStyle,"data-p":i.dataP},n.ptm("value")),[n.value!=null&&n.value!==0&&n.showValue?(o(),m("div",_({key:0,class:n.cx("label"),"data-p":i.dataP},n.ptm("label")),[U(n.$slots,"default",{},function(){return[w(d(n.value+"%"),1)]})],16,ra)):F("",!0)],16,ia)):i.indeterminate?(o(),m("div",_({key:1,class:n.cx("value"),"data-p":i.dataP},n.ptm("value")),null,16,la)):F("",!0)],16,ta)}j.render=da;const oa={class:"generate-rtp-page"},ca={class:"page-header"},pa={class:"header-actions"},ua={key:1,class:"content-grid"},ma={class:"panel-left"},va={class:"card meta-card"},ga={class:"card-header"},fa={class:"meta-list"},ka={class:"meta-row"},ba={class:"meta-value highlight"},ha={class:"meta-row"},ya={class:"meta-value"},Pa={class:"meta-row"},_a={class:"meta-value"},wa={class:"meta-row"},Ia={class:"meta-value"},Ra={class:"meta-row"},Da={class:"meta-value text-small"},Ta={class:"card structure-card"},Fa={class:"card-header"},Ba={class:"panel-right"},xa={class:"card attachments-card"},Sa={class:"card-header"},Ka={class:"selection-control"},Va={for:"selectAllForms",class:"label-select-all"},Ca={class:"forms-grid"},Oa=["onClick"],ja={class:"item-check"},$a={class:"item-info"},Ea={class:"item-top"},Aa={class:"item-code"},Na={class:"item-title"},Ua={class:"item-desc"},La={class:"card summary-action-card"},Ga={class:"summary-details"},Ma={class:"stat-box"},za={class:"stat-num"},Wa={class:"stat-box"},Ha={class:"stat-num"},Za={class:"action-btn-row"},qa={key:0,class:"generating-progress"},Ja={__name:"GenerateRtp",setup(n){const r=G(),c=M(),f=P(!1),k=P(!1),i=P(null),v=P(!0),b=[{key:"f1a",form:"Form 1.a",label:"Rekap Kuesioner CEE (Persepsi)",desc:"Hasil survei persepsi responden terhadap 8 sub-unsur CEE"},{key:"f1b",form:"Form 1.b",label:"Reviu Dokumen CEE",desc:"Analisis kondisi kerentanan berdasarkan reviu dokumen"},{key:"f1c",form:"Form 1.c",label:"Simpulan CEE",desc:"Simpulan gabungan survei persepsi dan reviu dokumen"},{key:"f6",form:"Form 6",label:"RTP atas CEE",desc:"Rencana tindak pengendalian atas kelemahan lingkungan pengendalian"},{key:"f2a",form:"Form 2.a",label:"Konteks Strategis Pemda",desc:"Visi, misi, sasaran, dan prioritas pembangunan Kota Tegal"},{key:"f2b",form:"Form 2.b",label:"Konteks Strategis OPD",desc:"Tujuan, sasaran, IKU, dan program strategis perangkat daerah"},{key:"f2c",form:"Form 2.c",label:"Konteks Operasional OPD",desc:"Pemetaan subkegiatan dan indikator operasional Renja"},{key:"f3a",form:"Form 3.a",label:"Identifikasi Risiko Strategis Pemda",desc:"Daftar risiko strategis Pemerintah Kota Tegal"},{key:"f3b",form:"Form 3.b",label:"Identifikasi Risiko Strategis OPD",desc:"Identifikasi risiko strategis perangkat daerah"},{key:"f3c",form:"Form 3.c",label:"Identifikasi Risiko Operasional OPD",desc:"Identifikasi risiko kegiatan dan subkegiatan operasional"},{key:"f4",form:"Form 4",label:"Analisis Risiko",desc:"Penilaian kemungkinan, dampak, skala, dan level risiko 5x5"},{key:"f5",form:"Form 5",label:"Daftar Risiko Prioritas",desc:"Risiko-risiko prioritas yang wajib ditangani dalam RTP"},{key:"f7",form:"Form 7",label:"RTP atas Risiko",desc:"Rencana tindak mitigasi dan pengendalian risiko prioritas"},{key:"f8",form:"Form 8",label:"Informasi & Komunikasi",desc:"Rencana sarana dan media pengkomunikasian pengendalian"},{key:"f9",form:"Form 9",label:"Rencana Pemantauan PI",desc:"Metode dan penanggung jawab pemantauan pengendalian intern"},{key:"f10",form:"Form 10",label:"Monitoring Event & RTP",desc:"Pencatatan kejadian risiko nyata dan pelaksanaan mitigasi"}],s=P(b.map(l=>l.key)),I=O({get:()=>s.value.length===b.length,set:l=>{s.value=l?b.map(e=>e.key):[]}}),R=O(()=>{var l,e;return((l=i.value)==null?void 0:l.nama_pd)||((e=r.opd)==null?void 0:e.nama_pd)||"-"});async function B(){if(r.opdId){f.value=!0;try{const l=await C.get("/master/opd-print-context",{params:{opd_id:r.opdId}});i.value=l.data||{}}catch{i.value={}}finally{f.value=!1}}}z([()=>r.opdId,()=>r.tahun],B),W(B);async function x(){if(!r.opdId){c.add({severity:"warn",summary:"Pilih OPD",detail:"Silakan pilih OPD terlebih dahulu",life:3e3});return}if(!v.value&&!s.value.length){c.add({severity:"warn",summary:"Tidak Ada Konten",detail:"Pilih minimal satu bagian atau sertakan Dokumen Utama",life:3e3});return}k.value=!0;try{const l=await C.get("/laporan/rtp-docx",{params:{opd_id:r.opdId,tahun:r.tahun,forms:s.value.join(","),include_main:v.value},responseType:"blob"}),h=`Dokumen_RTP_${R.value.replace(/[^a-zA-Z0-9_-]/g,"_")}_${r.tahun}.docx`,y=window.URL.createObjectURL(new Blob([l.data])),p=document.createElement("a");p.href=y,p.setAttribute("download",h),document.body.appendChild(p),p.click(),p.remove(),window.URL.revokeObjectURL(y),c.add({severity:"success",summary:"Berhasil Generate RTP",detail:`File Word ${h} berhasil diunduh.`,life:4e3})}catch{c.add({severity:"error",summary:"Gagal Generate",detail:"Terjadi kesalahan saat menyusun dokumen RTP. Periksa koneksi backend.",life:5e3})}finally{k.value=!1}}return(l,e)=>{var h,y,p,S;return o(),m("div",oa,[a("div",ca,[e[3]||(e[3]=K('<div class="header-left" data-v-96c433f3><div class="header-icon-box" data-v-96c433f3><i class="pi pi-file-word" data-v-96c433f3></i></div><div data-v-96c433f3><h1 class="page-title" data-v-96c433f3>Generate Dokumen RTP</h1><p class="page-desc" data-v-96c433f3> Penyusunan Rencana Tindak Pengendalian (RTP) format Word (.docx) berbasis template resmi dengan seluruh lampiran </p></div></div>',1)),a("div",pa,[g(u(V),{label:"Generate Dokumen Word (.docx)",icon:"pi pi-download",severity:"primary",loading:k.value,disabled:f.value||!v.value&&!s.value.length,onClick:x},null,8,["loading","disabled"])])]),f.value?(o(),H(Q,{key:0,label:"Memuat profil dan konteks dokumen…"})):(o(),m("div",ua,[a("div",ma,[a("div",va,[a("div",ga,[e[4]||(e[4]=a("span",{class:"card-title"},[a("i",{class:"pi pi-id-card card-icon"}),w(" Identitas & Penandatangan Dokumen ")],-1)),g(u(Y),{value:`Tahun ${u(r).tahun}`,severity:"info",class:"year-tag"},null,8,["value"])]),a("div",fa,[a("div",ka,[e[5]||(e[5]=a("span",{class:"meta-label"},"Organisasi Perangkat Daerah",-1)),a("span",ba,d(R.value),1)]),a("div",ha,[e[6]||(e[6]=a("span",{class:"meta-label"},"Kepala OPD",-1)),a("span",ya,d(((h=i.value)==null?void 0:h.nama_kepala)||"-"),1)]),a("div",Pa,[e[7]||(e[7]=a("span",{class:"meta-label"},"NIP",-1)),a("span",_a,d(((y=i.value)==null?void 0:y.nip_kepala)||"-"),1)]),a("div",wa,[e[8]||(e[8]=a("span",{class:"meta-label"},"Jabatan Penandatangan",-1)),a("span",Ia,d(((p=i.value)==null?void 0:p.jabatan_kepala)||`Kepala ${R.value}`),1)]),a("div",Ra,[e[9]||(e[9]=a("span",{class:"meta-label"},"Bidang Urusan",-1)),a("span",Da,d(((S=i.value)==null?void 0:S.bidang_urusan)||"-"),1)])])]),a("div",Ta,[a("div",Fa,[e[10]||(e[10]=a("span",{class:"card-title"},[a("i",{class:"pi pi-book card-icon"}),w(" Dokumen Utama RTP (Word Template) ")],-1)),g(u(T),{modelValue:v.value,"onUpdate:modelValue":e[0]||(e[0]=t=>v.value=t),binary:"",inputId:"mainDocToggle"},null,8,["modelValue"])]),e[11]||(e[11]=K('<p class="section-desc" data-v-96c433f3> Menggunakan template baku Pemerintah Kota Tegal (docxtpl) dengan logo Pemkot, tipografi resmi Times New Roman, dan pembagian bab naratif: </p><div class="chapters-timeline" data-v-96c433f3><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>Cover</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>Cover &amp; Identitas Dokumen</strong><span data-v-96c433f3>Lambang Pemkot Tegal, nama OPD, dan tahun anggaran</span></div></div><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>I</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>BAB I — Pendahuluan</strong><span data-v-96c433f3>Latar belakang, tupoksi organisasi, dasar hukum, maksud, tujuan &amp; manfaat</span></div></div><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>II</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>BAB II — Lingkungan Pengendalian</strong><span data-v-96c433f3>Penciptaan lingkungan pengendalian (CEE) 8 sub-unsur</span></div></div><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>III</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>BAB III — Penilaian &amp; Pengendalian Risiko</strong><span data-v-96c433f3>Penerapan SPIP, identifikasi risiko, hasil analisis, mitigasi</span></div></div><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>IV</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>BAB IV — Informasi, Komunikasi &amp; Pemantauan</strong><span data-v-96c433f3>Sarana komunikasi, media penyampaian, dan rencana monitoring PI</span></div></div><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>V</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>BAB V — Penutup</strong><span data-v-96c433f3>Kesimpulan dan lembar pengesahan tanda tangan Kepala OPD</span></div></div><div class="chap-item" data-v-96c433f3><div class="chap-badge" data-v-96c433f3>KK</div><div class="chap-content" data-v-96c433f3><strong data-v-96c433f3>Kertas Kerja RTP</strong><span data-v-96c433f3>Halaman pembuka kertas kerja &amp; rincian identitas OPD</span></div></div></div>',2))])]),a("div",Ba,[a("div",xa,[a("div",Sa,[e[12]||(e[12]=a("div",null,[a("span",{class:"card-title"},[a("i",{class:"pi pi-paperclip card-icon"}),w(" Lampiran Kertas Kerja (Printout Form) ")]),a("p",{class:"card-subtitle"}," Tiap form disusun dengan tabel lengkap, cell shading, batas kolom terstruktur, dan tanda tangan resmi. ")],-1)),a("div",Ka,[g(u(T),{modelValue:I.value,"onUpdate:modelValue":e[1]||(e[1]=t=>I.value=t),binary:"",inputId:"selectAllForms"},null,8,["modelValue"]),a("label",Va,d(I.value?"Hapus Semua":"Pilih Semua"),1)])]),a("div",Ca,[(o(),m(Z,null,q(b,t=>a("div",{key:t.key,class:J(["form-item-box",{active:s.value.includes(t.key)}]),onClick:$=>s.value.includes(t.key)?s.value=s.value.filter(D=>D!==t.key):s.value.push(t.key)},[a("div",ja,[g(u(T),{modelValue:s.value.includes(t.key),binary:"",onClick:e[2]||(e[2]=X(()=>{},["stop"])),onChange:$=>s.value.includes(t.key)?s.value=s.value.filter(D=>D!==t.key):s.value.push(t.key)},null,8,["modelValue","onChange"])]),a("div",$a,[a("div",Ea,[a("span",Aa,d(t.form),1),a("span",Na,d(t.label),1)]),a("p",Ua,d(t.desc),1)])],10,Oa)),64))])]),a("div",La,[a("div",Ga,[a("div",Ma,[a("span",za,d(v.value?"1 Dokumen":"0"),1),e[13]||(e[13]=a("span",{class:"stat-lbl"},"Dokumen Narasi Utama",-1))]),e[15]||(e[15]=a("div",{class:"stat-divider"},null,-1)),a("div",Wa,[a("span",Ha,d(s.value.length)+" / "+d(b.length),1),e[14]||(e[14]=a("span",{class:"stat-lbl"},"Form Lampiran Terpilih",-1))]),e[16]||(e[16]=a("div",{class:"stat-divider"},null,-1)),e[17]||(e[17]=a("div",{class:"stat-box"},[a("span",{class:"stat-num"},".DOCX"),a("span",{class:"stat-lbl"},"Format Microsoft Word")],-1))]),a("div",Za,[g(u(V),{label:"Generate & Unduh Dokumen RTP (.docx)",icon:"pi pi-download",class:"btn-download-big",loading:k.value,disabled:f.value||!v.value&&!s.value.length,onClick:x},null,8,["loading","disabled"])]),k.value?(o(),m("div",qa,[g(u(j),{mode:"indeterminate",style:{height:"6px"}}),e[18]||(e[18]=a("span",{class:"progress-txt"},"Sedang menyusun dan merender dokumen Word via docxtpl…",-1))])):F("",!0)])])]))])}}},ae=L(Ja,[["__scopeId","data-v-96c433f3"]]);export{ae as default};
