import{s as rt,a as _}from"./index-YMaJpkts.js";import{B as W,a3 as M,a9 as U,g as J,aa as N,J as Y,q as Z,o as g,c as v,a,i as I,W as st,m as S,j as $,t as u,ab as C,ac as T,r as dt,N as B,P as K,k as A,ad as ut,w as m,_ as ct,$ as pt,u as gt,L as bt,a8 as ft,n as ht,p,h,E as q,F as P,V as L,K as F,y as vt,Z as yt}from"./index-BKla1zY7.js";import{s as H}from"./index-VCKzP4ls.js";import{a as mt}from"./date-CDN1hEmW.js";import"./index-BoKuoVFG.js";import"./index-D_QqUqHO.js";import"./index-BRxCTJje.js";var _t=`
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
`,kt={root:function(e){var n=e.instance,r=e.props;return["p-togglebutton p-component",{"p-togglebutton-checked":n.active,"p-invalid":n.$invalid,"p-togglebutton-fluid":r.fluid,"p-togglebutton-sm p-inputfield-sm":r.size==="small","p-togglebutton-lg p-inputfield-lg":r.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},St=W.extend({name:"togglebutton",style:_t,classes:kt}),wt={name:"BaseToggleButton",extends:U,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:St,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}};function O(t){"@babel/helpers - typeof";return O=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},O(t)}function xt(t,e,n){return(e=Lt(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Lt(t){var e=Bt(t,"string");return O(e)=="symbol"?e:e+""}function Bt(t,e){if(O(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var r=n.call(t,e);if(O(r)!="object")return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var G={name:"ToggleButton",extends:wt,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(e){var n=e==="root"?this.ptmi:this.ptm;return n(e,{context:{active:this.active,disabled:this.disabled}})},onChange:function(e){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,e),this.$emit("change",e))},onBlur:function(e){var n,r;(n=(r=this.formField).onBlur)===null||n===void 0||n.call(r,e)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return N(this.onLabel)&&N(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "},dataP:function(){return J(xt({checked:this.active,invalid:this.$invalid},this.size,this.size))}},directives:{ripple:M}},Ot=["tabindex","disabled","aria-pressed","aria-label","aria-labelledby","data-p-checked","data-p-disabled","data-p"],Tt=["data-p"];function Pt(t,e,n,r,f,o){var c=Y("ripple");return Z((g(),v("button",S({type:"button",class:t.cx("root"),tabindex:t.tabindex,disabled:t.disabled,"aria-pressed":t.d_value,onClick:e[0]||(e[0]=function(){return o.onChange&&o.onChange.apply(o,arguments)}),onBlur:e[1]||(e[1]=function(){return o.onBlur&&o.onBlur.apply(o,arguments)})},o.getPTOptions("root"),{"aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"data-p-checked":o.active,"data-p-disabled":t.disabled,"data-p":o.dataP}),[a("span",S({class:t.cx("content")},o.getPTOptions("content"),{"data-p":o.dataP}),[I(t.$slots,"default",{},function(){return[I(t.$slots,"icon",{value:t.d_value,class:st(t.cx("icon"))},function(){return[t.onIcon||t.offIcon?(g(),v("span",S({key:0,class:[t.cx("icon"),t.d_value?t.onIcon:t.offIcon]},o.getPTOptions("icon")),null,16)):$("",!0)]}),a("span",S({class:t.cx("label")},o.getPTOptions("label")),u(o.label),17)]})],16,Tt)],16,Ot)),[[c]])}G.render=Pt;var $t=`
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
`,At={root:function(e){var n=e.props,r=e.instance;return["p-selectbutton p-component",{"p-invalid":r.$invalid,"p-selectbutton-fluid":n.fluid}]}},Vt=W.extend({name:"selectbutton",style:$t,classes:At}),jt={name:"BaseSelectButton",extends:U,props:{options:Array,optionLabel:null,optionValue:null,optionDisabled:null,multiple:Boolean,allowEmpty:{type:Boolean,default:!0},dataKey:null,ariaLabelledby:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:Vt,provide:function(){return{$pcSelectButton:this,$parentInstance:this}}};function Ct(t,e){var n=typeof Symbol<"u"&&t[Symbol.iterator]||t["@@iterator"];if(!n){if(Array.isArray(t)||(n=Q(t))||e){n&&(t=n);var r=0,f=function(){};return{s:f,n:function(){return r>=t.length?{done:!0}:{done:!1,value:t[r++]}},e:function(y){throw y},f}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var o,c=!0,i=!1;return{s:function(){n=n.call(t)},n:function(){var y=n.next();return c=y.done,y},e:function(y){i=!0,o=y},f:function(){try{c||n.return==null||n.return()}finally{if(i)throw o}}}}function It(t){return Rt(t)||zt(t)||Q(t)||Kt()}function Kt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Q(t,e){if(t){if(typeof t=="string")return z(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?z(t,e):void 0}}function zt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Rt(t){if(Array.isArray(t))return z(t)}function z(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,r=Array(e);n<e;n++)r[n]=t[n];return r}var X={name:"SelectButton",extends:jt,inheritAttrs:!1,emits:["change"],methods:{getOptionLabel:function(e){return this.optionLabel?T(e,this.optionLabel):e},getOptionValue:function(e){return this.optionValue?T(e,this.optionValue):e},getOptionRenderKey:function(e){return this.dataKey?T(e,this.dataKey):this.getOptionLabel(e)},isOptionDisabled:function(e){return this.optionDisabled?T(e,this.optionDisabled):!1},isOptionReadonly:function(e){if(this.allowEmpty)return!1;var n=this.isSelected(e);return this.multiple?n&&this.d_value.length===1:n},onOptionSelect:function(e,n,r){var f=this;if(!(this.disabled||this.isOptionDisabled(n)||this.isOptionReadonly(n))){var o=this.isSelected(n),c=this.getOptionValue(n),i;if(this.multiple)if(o){if(i=this.d_value.filter(function(b){return!C(b,c,f.equalityKey)}),!this.allowEmpty&&i.length===0)return}else i=this.d_value?[].concat(It(this.d_value),[c]):[c];else{if(o&&!this.allowEmpty)return;i=o?null:c}this.writeValue(i,e),this.$emit("change",{originalEvent:e,value:i})}},isSelected:function(e){var n=!1,r=this.getOptionValue(e);if(this.multiple){if(this.d_value){var f=Ct(this.d_value),o;try{for(f.s();!(o=f.n()).done;){var c=o.value;if(C(c,r,this.equalityKey)){n=!0;break}}}catch(i){f.e(i)}finally{f.f()}}}else n=C(this.d_value,r,this.equalityKey);return n}},computed:{equalityKey:function(){return this.optionValue?null:this.dataKey},dataP:function(){return J({invalid:this.$invalid})}},directives:{ripple:M},components:{ToggleButton:G}},Dt=["aria-labelledby","data-p"];function Et(t,e,n,r,f,o){var c=dt("ToggleButton");return g(),v("div",S({class:t.cx("root"),role:"group","aria-labelledby":t.ariaLabelledby},t.ptmi("root"),{"data-p":o.dataP}),[(g(!0),v(B,null,K(t.options,function(i,b){return g(),A(c,{key:o.getOptionRenderKey(i),modelValue:o.isSelected(i),onLabel:o.getOptionLabel(i),offLabel:o.getOptionLabel(i),disabled:t.disabled||o.isOptionDisabled(i),unstyled:t.unstyled,size:t.size,readonly:o.isOptionReadonly(i),onChange:function(V){return o.onOptionSelect(V,i,b)},pt:t.ptm("pcToggleButton")},ut({_:2},[t.$slots.option?{name:"default",fn:m(function(){return[I(t.$slots,"option",{option:i,index:b},function(){return[a("span",S({ref_for:!0},t.ptm("pcToggleButton").label),u(o.getOptionLabel(i)),17)]})]}),key:"0"}:void 0]),1032,["modelValue","onLabel","offLabel","disabled","unstyled","size","readonly","onChange","pt"])}),128))],16,Dt)}X.render=Et;const Nt={class:"toolbar no-print"},qt={class:"muted"},Ft={class:"stat-grid",style:{"margin-bottom":"16px"}},Ht={class:"stat"},Wt={class:"v"},Mt={class:"stat"},Ut={class:"v"},Jt={class:"stat"},Yt={class:"v"},Zt={class:"page-card",style:{padding:"0"}},Gt={style:{display:"flex","align-items":"center",gap:"6px"}},Qt={key:0,class:"pi pi-comment",style:{color:"#2563eb","font-size":"0.85rem"}},Xt={class:"muted"},te={class:"muted"},ee={class:"detail"},ne={key:0,class:"narasi-box"},oe={class:"narasi-body"},ae={class:"detail-head"},le={class:"detail-table"},ie={class:"c muted",style:{width:"32px"}},re={class:"c",style:{width:"150px"}},se={key:1,class:"muted"},de={__name:"SurveiHasil",setup(t){const e=pt(),n=gt(),r=bt(),f=ft(),o=L(()=>n.isAdmin),c=P(!0),i=P(null),b=P([]),y=P("all"),V=[{label:"Semua",value:"all"},{label:"Survei Publik",value:"survei"},{label:"Input Admin",value:"admin"}],tt={1:"Tidak Setuju",2:"Kurang Setuju",3:"Setuju",4:"Sangat Setuju"},j=L(()=>{var s;const d=((s=i.value)==null?void 0:s.responden)||[];return y.value==="all"?d:d.filter(w=>w.sumber===y.value)}),et=L(()=>j.value.length),nt=L(()=>{const d=j.value.map(s=>s.rata_rata).filter(s=>s!=null);return d.length?(d.reduce((s,w)=>s+w,0)/d.length).toFixed(2):"–"}),R=L(()=>{var d;return((d=i.value)==null?void 0:d.total_pertanyaan)||0});function ot(d){return mt(d,{dateStyle:"medium",timeStyle:"short"})}function at(d){return d==null?"secondary":d>=3?"success":"danger"}function lt(d){f.require({message:`Hapus hasil survei responden "${d.kode_responden}${d.nama_responden?" — "+d.nama_responden:""}"? Tindakan ini tidak dapat dibatalkan.`,header:"Konfirmasi Hapus",icon:"pi pi-exclamation-triangle",acceptClass:"p-button-danger",accept:async()=>{await q.delete(`/cee/survei-hasil/${d.id}`),await D(),r.add({severity:"success",summary:"Hasil survei dihapus",life:1800})}})}async function D(){c.value=!0,b.value=[];const{data:d}=await q.get("/cee/survei-hasil",{params:{opd_id:e.opdId,tahun:e.tahun}});i.value=d,c.value=!1}return ht(D),(d,s)=>{var E;const w=Y("tooltip");return g(),v(B,null,[a("div",Nt,[a("span",qt,u((E=p(e).opd)==null?void 0:E.nama_pd)+" — "+u(p(e).tahun),1),s[2]||(s[2]=a("div",{class:"spacer"},null,-1)),h(p(X),{modelValue:y.value,"onUpdate:modelValue":s[0]||(s[0]=l=>y.value=l),options:V,optionLabel:"label",optionValue:"value"},null,8,["modelValue"])]),c.value?(g(),A(yt,{key:0,label:"Memuat rincian hasil survei…"})):(g(),v(B,{key:1},[a("div",Ft,[a("div",Ht,[a("div",Wt,u(et.value),1),s[3]||(s[3]=a("div",{class:"l"},"Responden",-1))]),a("div",Mt,[a("div",Ut,u(R.value),1),s[4]||(s[4]=a("div",{class:"l"},"Pertanyaan per Responden",-1))]),a("div",Jt,[a("div",Yt,u(nt.value),1),s[5]||(s[5]=a("div",{class:"l"},"Rata-rata Skor (1–4)",-1))])]),a("div",Zt,[h(p(rt),{expandedRows:b.value,"onUpdate:expandedRows":s[1]||(s[1]=l=>b.value=l),value:j.value,dataKey:"id",size:"small",stripedRows:"",scrollable:""},{expansion:m(({data:l})=>[a("div",ee,[l.narasi?(g(),v("div",ne,[s[6]||(s[6]=a("div",{class:"narasi-head"},[a("i",{class:"pi pi-comment"}),a("span",null,"Narasi Lain Terkait Kondisi Lingkungan Pengendalian:")],-1)),a("div",oe,u(l.narasi),1)])):$("",!0),(g(!0),v(B,null,K(i.value.kategori,x=>(g(),v("div",{key:x.id,class:"detail-kat"},[a("div",ae,u(x.kode)+". "+u(x.nama),1),a("table",le,[a("tbody",null,[(g(!0),v(B,null,K(x.pertanyaan,(k,it)=>(g(),v("tr",{key:k.id},[a("td",ie,u(it+1),1),a("td",null,u(k.pertanyaan),1),a("td",re,[l.jawaban[k.id]!=null?(g(),A(p(H),{key:0,value:`${l.jawaban[k.id]} — ${tt[l.jawaban[k.id]]}`,severity:at(l.jawaban[k.id])},null,8,["value","severity"])):(g(),v("span",se,"Belum dijawab"))])]))),128))])])]))),128))])]),empty:m(()=>[...s[7]||(s[7]=[a("div",{class:"muted",style:{padding:"14px"}},"Belum ada responden survei.",-1)])]),default:m(()=>[h(p(_),{expander:"",style:{width:"42px"}}),h(p(_),{field:"kode_responden",header:"Kode",style:{width:"70px"}}),h(p(_),{header:"Nama Responden",style:{minWidth:"180px"}},{body:m(({data:l})=>[a("div",Gt,[a("span",null,u(l.nama_responden||"–"),1),l.narasi?Z((g(),v("i",Qt,null,512)),[[w,"Ada narasi kondisi lingkungan pengendalian",void 0,{top:!0}]]):$("",!0)])]),_:1}),h(p(_),{header:"Jabatan",style:{minWidth:"150px"}},{body:m(({data:l})=>[F(u(l.jabatan||"–"),1)]),_:1}),h(p(_),{header:"Email",style:{minWidth:"190px"}},{body:m(({data:l})=>[a("span",Xt,u(l.email||"–"),1)]),_:1}),h(p(_),{header:"Sumber",style:{width:"120px"}},{body:m(({data:l})=>[h(p(H),{value:l.sumber==="survei"?"Survei Publik":"Input Admin",severity:l.sumber==="survei"?"info":"secondary"},null,8,["value","severity"])]),_:1}),h(p(_),{header:"Terisi",style:{width:"90px"}},{body:m(({data:l})=>[F(u(l.jumlah_jawaban)+" / "+u(R.value),1)]),_:1}),h(p(_),{header:"Rata-rata",style:{width:"90px"}},{body:m(({data:l})=>[a("strong",null,u(l.rata_rata??"–"),1)]),_:1}),h(p(_),{header:"Waktu Pengisian",style:{minWidth:"160px"}},{body:m(({data:l})=>[a("span",te,u(ot(l.submitted_at)),1)]),_:1}),o.value?(g(),A(p(_),{key:0,header:"",style:{width:"56px"},class:"no-print"},{body:m(({data:l})=>[h(p(vt),{icon:"pi pi-trash",text:"",rounded:"",size:"small",severity:"danger",onClick:x=>lt(l)},null,8,["onClick"])]),_:1})):$("",!0)]),_:1},8,["expandedRows","value"])])],64))],64)}}},ve=ct(de,[["__scopeId","data-v-06466970"]]);export{ve as default};
