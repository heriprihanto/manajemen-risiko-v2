import{s as st,a as k}from"./index-H8lFLJtc.js";import{J as M,ab as U,ac as J,O as Y,ad as N,a2 as G,i as Q,o as g,c as h,a,W as K,q as dt,I as S,f as A,t as u,ae as j,af as P,A as ut,F as $,r as R,y as V,ag as ct,B as m,_ as pt,b as gt,x as bt,a3 as ft,aa as vt,w as ht,$ as yt,d as mt,u as p,e as f,s as H,l as q,k as T,m as L,g as F,a7 as kt}from"./index-BRxXQnbS.js";import{s as W}from"./index-B6edba4s.js";import{a as _t}from"./date-BzCcEzfS.js";import"./index-gojs8wwy.js";import"./index-AYI8lfOn.js";import"./index-tVZ6xh2g.js";var St=`
    .p-togglebutton {
        display: inline-flex;
        cursor: pointer;
        user-select: none;
        overflow: hidden;
        position: relative;
        color: dt('togglebutton.color');
        background: dt('togglebutton.background');
        border: 1px solid dt('togglebutton.border.color');
        padding: dt('togglebutton.padding');
        font-size: 1rem;
        font-family: inherit;
        font-feature-settings: inherit;
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
        border-radius: dt('togglebutton.border.radius');
        outline-color: transparent;
        font-weight: dt('togglebutton.font.weight');
    }

    .p-togglebutton-content {
        display: inline-flex;
        flex: 1 1 auto;
        align-items: center;
        justify-content: center;
        gap: dt('togglebutton.gap');
        padding: dt('togglebutton.content.padding');
        background: transparent;
        border-radius: dt('togglebutton.content.border.radius');
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover {
        background: dt('togglebutton.hover.background');
        color: dt('togglebutton.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked {
        background: dt('togglebutton.checked.background');
        border-color: dt('togglebutton.checked.border.color');
        color: dt('togglebutton.checked.color');
    }

    .p-togglebutton-checked .p-togglebutton-content {
        background: dt('togglebutton.content.checked.background');
        box-shadow: dt('togglebutton.content.checked.shadow');
    }

    .p-togglebutton:focus-visible {
        box-shadow: dt('togglebutton.focus.ring.shadow');
        outline: dt('togglebutton.focus.ring.width') dt('togglebutton.focus.ring.style') dt('togglebutton.focus.ring.color');
        outline-offset: dt('togglebutton.focus.ring.offset');
    }

    .p-togglebutton.p-invalid {
        border-color: dt('togglebutton.invalid.border.color');
    }

    .p-togglebutton:disabled {
        opacity: 1;
        cursor: default;
        background: dt('togglebutton.disabled.background');
        border-color: dt('togglebutton.disabled.border.color');
        color: dt('togglebutton.disabled.color');
    }

    .p-togglebutton-label,
    .p-togglebutton-icon {
        position: relative;
        transition: none;
    }

    .p-togglebutton-icon {
        color: dt('togglebutton.icon.color');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover .p-togglebutton-icon {
        color: dt('togglebutton.icon.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked .p-togglebutton-icon {
        color: dt('togglebutton.icon.checked.color');
    }

    .p-togglebutton:disabled .p-togglebutton-icon {
        color: dt('togglebutton.icon.disabled.color');
    }

    .p-togglebutton-sm {
        padding: dt('togglebutton.sm.padding');
        font-size: dt('togglebutton.sm.font.size');
    }

    .p-togglebutton-sm .p-togglebutton-content {
        padding: dt('togglebutton.content.sm.padding');
    }

    .p-togglebutton-lg {
        padding: dt('togglebutton.lg.padding');
        font-size: dt('togglebutton.lg.font.size');
    }

    .p-togglebutton-lg .p-togglebutton-content {
        padding: dt('togglebutton.content.lg.padding');
    }

    .p-togglebutton-fluid {
        width: 100%;
    }
`,wt={root:function(e){var n=e.instance,s=e.props;return["p-togglebutton p-component",{"p-togglebutton-checked":n.active,"p-invalid":n.$invalid,"p-togglebutton-fluid":s.fluid,"p-togglebutton-sm p-inputfield-sm":s.size==="small","p-togglebutton-lg p-inputfield-lg":s.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},xt=M.extend({name:"togglebutton",style:St,classes:wt}),Lt={name:"BaseToggleButton",extends:J,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:xt,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}};function O(t){"@babel/helpers - typeof";return O=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},O(t)}function Ot(t,e,n){return(e=Bt(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Bt(t){var e=Pt(t,"string");return O(e)=="symbol"?e:e+""}function Pt(t,e){if(O(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var s=n.call(t,e);if(O(s)!="object")return s;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var X={name:"ToggleButton",extends:Lt,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(e){var n=e==="root"?this.ptmi:this.ptm;return n(e,{context:{active:this.active,disabled:this.disabled}})},onChange:function(e){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,e),this.$emit("change",e))},onBlur:function(e){var n,s;(n=(s=this.formField).onBlur)===null||n===void 0||n.call(s,e)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return N(this.onLabel)&&N(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "},dataP:function(){return Y(Ot({checked:this.active,invalid:this.$invalid},this.size,this.size))}},directives:{ripple:U}},Tt=["tabindex","disabled","aria-pressed","aria-label","aria-labelledby","data-p-checked","data-p-disabled","data-p"],At=["data-p"];function $t(t,e,n,s,v,o){var c=G("ripple");return Q((g(),h("button",S({type:"button",class:t.cx("root"),tabindex:t.tabindex,disabled:t.disabled,"aria-pressed":t.d_value,onClick:e[0]||(e[0]=function(){return o.onChange&&o.onChange.apply(o,arguments)}),onBlur:e[1]||(e[1]=function(){return o.onBlur&&o.onBlur.apply(o,arguments)})},o.getPTOptions("root"),{"aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"data-p-checked":o.active,"data-p-disabled":t.disabled,"data-p":o.dataP}),[a("span",S({class:t.cx("content")},o.getPTOptions("content"),{"data-p":o.dataP}),[K(t.$slots,"default",{},function(){return[K(t.$slots,"icon",{value:t.d_value,class:dt(t.cx("icon"))},function(){return[t.onIcon||t.offIcon?(g(),h("span",S({key:0,class:[t.cx("icon"),t.d_value?t.onIcon:t.offIcon]},o.getPTOptions("icon")),null,16)):A("",!0)]}),a("span",S({class:t.cx("label")},o.getPTOptions("label")),u(o.label),17)]})],16,At)],16,Tt)),[[c]])}X.render=$t;var Vt=`
    .p-selectbutton {
        display: inline-flex;
        user-select: none;
        vertical-align: bottom;
        outline-color: transparent;
        border-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton .p-togglebutton {
        border-radius: 0;
        border-width: 1px 1px 1px 0;
    }

    .p-selectbutton .p-togglebutton:focus-visible {
        position: relative;
        z-index: 1;
    }

    .p-selectbutton .p-togglebutton:first-child {
        border-inline-start-width: 1px;
        border-start-start-radius: dt('selectbutton.border.radius');
        border-end-start-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton .p-togglebutton:last-child {
        border-start-end-radius: dt('selectbutton.border.radius');
        border-end-end-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton.p-invalid {
        outline: 1px solid dt('selectbutton.invalid.border.color');
        outline-offset: 0;
    }

    .p-selectbutton-fluid {
        width: 100%;
    }
    
    .p-selectbutton-fluid .p-togglebutton {
        flex: 1 1 0;
    }
`,It={root:function(e){var n=e.props,s=e.instance;return["p-selectbutton p-component",{"p-invalid":s.$invalid,"p-selectbutton-fluid":n.fluid}]}},Ct=M.extend({name:"selectbutton",style:Vt,classes:It}),jt={name:"BaseSelectButton",extends:J,props:{options:Array,optionLabel:null,optionValue:null,optionDisabled:null,multiple:Boolean,allowEmpty:{type:Boolean,default:!0},dataKey:null,ariaLabelledby:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:Ct,provide:function(){return{$pcSelectButton:this,$parentInstance:this}}};function Kt(t,e){var n=typeof Symbol<"u"&&t[Symbol.iterator]||t["@@iterator"];if(!n){if(Array.isArray(t)||(n=Z(t))||e){n&&(t=n);var s=0,v=function(){};return{s:v,n:function(){return s>=t.length?{done:!0}:{done:!1,value:t[s++]}},e:function(y){throw y},f:v}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var o,c=!0,r=!1;return{s:function(){n=n.call(t)},n:function(){var y=n.next();return c=y.done,y},e:function(y){r=!0,o=y},f:function(){try{c||n.return==null||n.return()}finally{if(r)throw o}}}}function Rt(t){return Et(t)||Dt(t)||Z(t)||zt()}function zt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Z(t,e){if(t){if(typeof t=="string")return z(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?z(t,e):void 0}}function Dt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Et(t){if(Array.isArray(t))return z(t)}function z(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,s=Array(e);n<e;n++)s[n]=t[n];return s}var tt={name:"SelectButton",extends:jt,inheritAttrs:!1,emits:["change"],methods:{getOptionLabel:function(e){return this.optionLabel?P(e,this.optionLabel):e},getOptionValue:function(e){return this.optionValue?P(e,this.optionValue):e},getOptionRenderKey:function(e){return this.dataKey?P(e,this.dataKey):this.getOptionLabel(e)},isOptionDisabled:function(e){return this.optionDisabled?P(e,this.optionDisabled):!1},isOptionReadonly:function(e){if(this.allowEmpty)return!1;var n=this.isSelected(e);return this.multiple?n&&this.d_value.length===1:n},onOptionSelect:function(e,n,s){var v=this;if(!(this.disabled||this.isOptionDisabled(n)||this.isOptionReadonly(n))){var o=this.isSelected(n),c=this.getOptionValue(n),r;if(this.multiple)if(o){if(r=this.d_value.filter(function(b){return!j(b,c,v.equalityKey)}),!this.allowEmpty&&r.length===0)return}else r=this.d_value?[].concat(Rt(this.d_value),[c]):[c];else{if(o&&!this.allowEmpty)return;r=o?null:c}this.writeValue(r,e),this.$emit("change",{originalEvent:e,value:r})}},isSelected:function(e){var n=!1,s=this.getOptionValue(e);if(this.multiple){if(this.d_value){var v=Kt(this.d_value),o;try{for(v.s();!(o=v.n()).done;){var c=o.value;if(j(c,s,this.equalityKey)){n=!0;break}}}catch(r){v.e(r)}finally{v.f()}}}else n=j(this.d_value,s,this.equalityKey);return n}},computed:{equalityKey:function(){return this.optionValue?null:this.dataKey},dataP:function(){return Y({invalid:this.$invalid})}},directives:{ripple:U},components:{ToggleButton:X}},Nt=["aria-labelledby","data-p"];function Ht(t,e,n,s,v,o){var c=ut("ToggleButton");return g(),h("div",S({class:t.cx("root"),role:"group","aria-labelledby":t.ariaLabelledby},t.ptmi("root"),{"data-p":o.dataP}),[(g(!0),h($,null,R(t.options,function(r,b){return g(),V(c,{key:o.getOptionRenderKey(r),modelValue:o.isSelected(r),onLabel:o.getOptionLabel(r),offLabel:o.getOptionLabel(r),disabled:t.disabled||o.isOptionDisabled(r),unstyled:t.unstyled,size:t.size,readonly:o.isOptionReadonly(r),onChange:function(I){return o.onOptionSelect(I,r,b)},pt:t.ptm("pcToggleButton")},ct({_:2},[t.$slots.option?{name:"default",fn:m(function(){return[K(t.$slots,"option",{option:r,index:b},function(){return[a("span",S({ref_for:!0},t.ptm("pcToggleButton").label),u(o.getOptionLabel(r)),17)]})]}),key:"0"}:void 0]),1032,["modelValue","onLabel","offLabel","disabled","unstyled","size","readonly","onChange","pt"])}),128))],16,Nt)}tt.render=Ht;const qt={class:"survei-hasil-page"},Ft={class:"page-header"},Wt={class:"header-actions"},Mt={class:"ctx-chip",title:"Konteks Penilaian Aktif"},Ut={class:"stat-grid",style:{"margin-bottom":"16px"}},Jt={class:"stat"},Yt={class:"v"},Gt={class:"stat"},Qt={class:"v"},Xt={class:"stat"},Zt={class:"v"},te={class:"page-card",style:{padding:"0"}},ee={style:{display:"flex","align-items":"center",gap:"6px"}},ne={key:0,class:"pi pi-comment",style:{color:"#2563eb","font-size":"0.85rem"}},ae={class:"muted"},oe={class:"muted"},le={class:"detail"},ie={key:0,class:"narasi-box"},re={class:"narasi-body"},se={class:"detail-head"},de={class:"detail-table"},ue={class:"c muted",style:{width:"32px"}},ce={class:"c",style:{width:"150px"}},pe={key:1,class:"muted"},ge={__name:"SurveiHasil",setup(t){const e=gt(),n=bt(),s=ft(),v=vt(),o=L(()=>n.isAdmin),c=T(!0),r=T(null),b=T([]),y=T("all"),I=[{label:"Semua",value:"all"},{label:"Survei Publik",value:"survei"},{label:"Input Admin",value:"admin"}],et={1:"Tidak Setuju",2:"Kurang Setuju",3:"Setuju",4:"Sangat Setuju"},C=L(()=>{var l;const d=((l=r.value)==null?void 0:l.responden)||[];return y.value==="all"?d:d.filter(w=>w.sumber===y.value)}),nt=L(()=>C.value.length),at=L(()=>{const d=C.value.map(l=>l.rata_rata).filter(l=>l!=null);return d.length?(d.reduce((l,w)=>l+w,0)/d.length).toFixed(2):"–"}),D=L(()=>{var d;return((d=r.value)==null?void 0:d.total_pertanyaan)||0});function ot(d){return _t(d,{})}function lt(d){return d==null?"secondary":d>=3?"success":"danger"}function it(d){v.require({message:`Hapus hasil survei responden "${d.kode_responden}${d.nama_responden?" — "+d.nama_responden:""}"? Tindakan ini tidak dapat dibatalkan.`,header:"Konfirmasi Hapus",icon:"pi pi-exclamation-triangle",acceptClass:"p-button-danger",accept:async()=>{await q.delete(`/cee/survei-hasil/${d.id}`),await B(),s.add({severity:"success",summary:"Hasil survei dihapus",life:1800})}})}async function B(){c.value=!0,b.value=[];const{data:d}=await q.get("/cee/survei-hasil",{params:{opd_id:e.opdId,tahun:e.tahun}});r.value=d,c.value=!1}return ht([()=>e.opdId,()=>e.tahun],B),yt(B),(d,l)=>{var E;const w=G("tooltip");return g(),h("div",qt,[a("div",Ft,[l[4]||(l[4]=mt('<div class="header-left" data-v-4ea7bce8><div class="header-icon-box" data-v-4ea7bce8><i class="pi pi-users" data-v-4ea7bce8></i></div><div data-v-4ea7bce8><h1 class="page-title" data-v-4ea7bce8>Rincian Hasil Survei CEE</h1><p class="page-desc" data-v-4ea7bce8> Rincian jawaban setiap responden terhadap pertanyaan survei persepsi Lingkungan Pengendalian Intern </p></div></div>',1)),a("div",Wt,[a("div",Mt,[l[2]||(l[2]=a("i",{class:"pi pi-building"},null,-1)),a("span",null,u(((E=p(e).opd)==null?void 0:E.nama_pd)||"Semua OPD"),1),l[3]||(l[3]=a("span",{class:"chip-dot"},"•",-1)),a("span",null,"Tahun "+u(p(e).tahun),1)]),f(p(tt),{modelValue:y.value,"onUpdate:modelValue":l[0]||(l[0]=i=>y.value=i),options:I,optionLabel:"label",optionValue:"value"},null,8,["modelValue"]),f(p(H),{label:"Segarkan",icon:"pi pi-refresh",severity:"secondary",variant:"outlined",loading:c.value,onClick:B},null,8,["loading"])])]),c.value?(g(),V(kt,{key:0,label:"Memuat rincian hasil survei…"})):(g(),h($,{key:1},[a("div",Ut,[a("div",Jt,[a("div",Yt,u(nt.value),1),l[5]||(l[5]=a("div",{class:"l"},"Responden",-1))]),a("div",Gt,[a("div",Qt,u(D.value),1),l[6]||(l[6]=a("div",{class:"l"},"Pertanyaan per Responden",-1))]),a("div",Xt,[a("div",Zt,u(at.value),1),l[7]||(l[7]=a("div",{class:"l"},"Rata-rata Skor (1–4)",-1))])]),a("div",te,[f(p(st),{expandedRows:b.value,"onUpdate:expandedRows":l[1]||(l[1]=i=>b.value=i),value:C.value,dataKey:"id",size:"small",stripedRows:"",scrollable:""},{expansion:m(({data:i})=>[a("div",le,[i.narasi?(g(),h("div",ie,[l[8]||(l[8]=a("div",{class:"narasi-head"},[a("i",{class:"pi pi-comment"}),a("span",null,"Narasi Lain Terkait Kondisi Lingkungan Pengendalian:")],-1)),a("div",re,u(i.narasi),1)])):A("",!0),(g(!0),h($,null,R(r.value.kategori,x=>(g(),h("div",{key:x.id,class:"detail-kat"},[a("div",se,u(x.kode)+". "+u(x.nama),1),a("table",de,[a("tbody",null,[(g(!0),h($,null,R(x.pertanyaan,(_,rt)=>(g(),h("tr",{key:_.id},[a("td",ue,u(rt+1),1),a("td",null,u(_.pertanyaan),1),a("td",ce,[i.jawaban[_.id]!=null?(g(),V(p(W),{key:0,value:`${i.jawaban[_.id]} — ${et[i.jawaban[_.id]]}`,severity:lt(i.jawaban[_.id])},null,8,["value","severity"])):(g(),h("span",pe,"Belum dijawab"))])]))),128))])])]))),128))])]),empty:m(()=>[...l[9]||(l[9]=[a("div",{class:"muted",style:{padding:"14px"}},"Belum ada responden survei.",-1)])]),default:m(()=>[f(p(k),{expander:"",style:{width:"42px"}}),f(p(k),{field:"kode_responden",header:"Kode",style:{width:"70px"}}),f(p(k),{header:"Nama Responden",style:{minWidth:"180px"}},{body:m(({data:i})=>[a("div",ee,[a("span",null,u(i.nama_responden||"–"),1),i.narasi?Q((g(),h("i",ne,null,512)),[[w,"Ada narasi kondisi lingkungan pengendalian",void 0,{top:!0}]]):A("",!0)])]),_:1}),f(p(k),{header:"Jabatan",style:{minWidth:"150px"}},{body:m(({data:i})=>[F(u(i.jabatan||"–"),1)]),_:1}),f(p(k),{header:"Email",style:{minWidth:"190px"}},{body:m(({data:i})=>[a("span",ae,u(i.email||"–"),1)]),_:1}),f(p(k),{header:"Sumber",style:{width:"120px"}},{body:m(({data:i})=>[f(p(W),{value:i.sumber==="survei"?"Survei Publik":"Input Admin",severity:i.sumber==="survei"?"info":"secondary"},null,8,["value","severity"])]),_:1}),f(p(k),{header:"Terisi",style:{width:"90px"}},{body:m(({data:i})=>[F(u(i.jumlah_jawaban)+" / "+u(D.value),1)]),_:1}),f(p(k),{header:"Rata-rata",style:{width:"90px"}},{body:m(({data:i})=>[a("strong",null,u(i.rata_rata??"–"),1)]),_:1}),f(p(k),{header:"Waktu Pengisian",style:{minWidth:"160px"}},{body:m(({data:i})=>[a("span",oe,u(ot(i.submitted_at)),1)]),_:1}),o.value?(g(),V(p(k),{key:0,header:"",style:{width:"56px"},class:"no-print"},{body:m(({data:i})=>[f(p(H),{icon:"pi pi-trash",text:"",rounded:"",size:"small",severity:"danger",onClick:x=>it(i)},null,8,["onClick"])]),_:1})):A("",!0)]),_:1},8,["expandedRows","value"])])],64))])}}},_e=pt(ge,[["__scopeId","data-v-4ea7bce8"]]);export{_e as default};
