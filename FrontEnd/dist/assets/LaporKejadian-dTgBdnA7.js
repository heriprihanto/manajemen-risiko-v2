import{_ as Bn,a2 as Fn,h as D,Z as jn,c as S,x as $n,a as u,q as I,l as y,s as oe,a3 as ht,t as P,g as Hn,d as w,a4 as ft,L as Ue,a5 as pt,e as Wn,F as zn,r as Gn,i as xe,a1 as Kn,o as E,b as qn,a7 as Jn}from"./index-LsPIulEd.js";import{s as Yn}from"./index-D_tsf8NC.js";import{s as mt}from"./index-QiBA7Mry.js";import{a as Xn}from"./date-BzCcEzfS.js";import"./index-BfE4U8jF.js";import"./index-jZ1fxmFM.js";const Qn=()=>{};var gt={};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ht=function(n){const e=[];let t=0;for(let i=0;i<n.length;i++){let r=n.charCodeAt(i);r<128?e[t++]=r:r<2048?(e[t++]=r>>6|192,e[t++]=r&63|128):(r&64512)===55296&&i+1<n.length&&(n.charCodeAt(i+1)&64512)===56320?(r=65536+((r&1023)<<10)+(n.charCodeAt(++i)&1023),e[t++]=r>>18|240,e[t++]=r>>12&63|128,e[t++]=r>>6&63|128,e[t++]=r&63|128):(e[t++]=r>>12|224,e[t++]=r>>6&63|128,e[t++]=r&63|128)}return e},Zn=function(n){const e=[];let t=0,i=0;for(;t<n.length;){const r=n[t++];if(r<128)e[i++]=String.fromCharCode(r);else if(r>191&&r<224){const s=n[t++];e[i++]=String.fromCharCode((r&31)<<6|s&63)}else if(r>239&&r<365){const s=n[t++],a=n[t++],c=n[t++],o=((r&7)<<18|(s&63)<<12|(a&63)<<6|c&63)-65536;e[i++]=String.fromCharCode(55296+(o>>10)),e[i++]=String.fromCharCode(56320+(o&1023))}else{const s=n[t++],a=n[t++];e[i++]=String.fromCharCode((r&15)<<12|(s&63)<<6|a&63)}}return e.join("")},Wt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(n,e){if(!Array.isArray(n))throw Error("encodeByteArray takes an array as a parameter");this.init_();const t=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,i=[];for(let r=0;r<n.length;r+=3){const s=n[r],a=r+1<n.length,c=a?n[r+1]:0,o=r+2<n.length,h=o?n[r+2]:0,d=s>>2,g=(s&3)<<4|c>>4;let v=(c&15)<<2|h>>6,T=h&63;o||(T=64,a||(v=64)),i.push(t[d],t[g],t[v],t[T])}return i.join("")},encodeString(n,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(n):this.encodeByteArray(Ht(n),e)},decodeString(n,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(n):Zn(this.decodeStringToByteArray(n,e))},decodeStringToByteArray(n,e){this.init_();const t=e?this.charToByteMapWebSafe_:this.charToByteMap_,i=[];for(let r=0;r<n.length;){const s=t[n.charAt(r++)],c=r<n.length?t[n.charAt(r)]:0;++r;const h=r<n.length?t[n.charAt(r)]:64;++r;const g=r<n.length?t[n.charAt(r)]:64;if(++r,s==null||c==null||h==null||g==null)throw new ei;const v=s<<2|c>>4;if(i.push(v),h!==64){const T=c<<4&240|h>>2;if(i.push(T),g!==64){const k=h<<6&192|g;i.push(k)}}}return i},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let n=0;n<this.ENCODED_VALS.length;n++)this.byteToCharMap_[n]=this.ENCODED_VALS.charAt(n),this.charToByteMap_[this.byteToCharMap_[n]]=n,this.byteToCharMapWebSafe_[n]=this.ENCODED_VALS_WEBSAFE.charAt(n),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[n]]=n,n>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(n)]=n,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(n)]=n)}}};class ei extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const ti=function(n){const e=Ht(n);return Wt.encodeByteArray(e,!0)},zt=function(n){return ti(n).replace(/\./g,"")},Gt=function(n){try{return Wt.decodeString(n,!0)}catch(e){console.error("base64Decode failed: ",e)}return null};/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ni(){if(typeof self<"u")return self;if(typeof window<"u")return window;if(typeof global<"u")return global;throw new Error("Unable to locate global object.")}/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ii=()=>ni().__FIREBASE_DEFAULTS__,ri=()=>{if(typeof process>"u"||typeof gt>"u")return;const n=gt.__FIREBASE_DEFAULTS__;if(n)return JSON.parse(n)},si=()=>{if(typeof document>"u")return;let n;try{n=document.cookie.match(/__FIREBASE_DEFAULTS__=([^;]+)/)}catch{return}const e=n&&Gt(n[1]);return e&&JSON.parse(e)},Qe=()=>{try{return Qn()||ii()||ri()||si()}catch(n){console.info(`Unable to get __FIREBASE_DEFAULTS__ due to: ${n}`);return}},ai=n=>{var e,t;return(t=(e=Qe())==null?void 0:e.emulatorHosts)==null?void 0:t[n]},Kt=()=>{var n;return(n=Qe())==null?void 0:n.config},qt=n=>{var e;return(e=Qe())==null?void 0:e[`_${n}`]};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class oi{constructor(){this.reject=()=>{},this.resolve=()=>{},this.promise=new Promise((e,t)=>{this.resolve=e,this.reject=t})}wrapCallback(e){return(t,i)=>{t?this.reject(t):this.resolve(i),typeof e=="function"&&(this.promise.catch(()=>{}),e.length===1?e(t):e(t,i))}}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function b(){return typeof navigator<"u"&&typeof navigator.userAgent=="string"?navigator.userAgent:""}function ci(){return typeof window<"u"&&!!(window.cordova||window.phonegap||window.PhoneGap)&&/ios|iphone|ipod|ipad|android|blackberry|iemobile/i.test(b())}function li(){return typeof navigator<"u"&&navigator.userAgent==="Cloudflare-Workers"}function ui(){const n=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof n=="object"&&n.id!==void 0}function di(){return typeof navigator=="object"&&navigator.product==="ReactNative"}function hi(){const n=b();return n.indexOf("MSIE ")>=0||n.indexOf("Trident/")>=0}function fi(){try{return typeof indexedDB=="object"}catch{return!1}}function pi(){return new Promise((n,e)=>{try{let t=!0;const i="validate-browser-context-for-indexeddb-analytics-module",r=self.indexedDB.open(i);r.onsuccess=()=>{r.result.close(),t||self.indexedDB.deleteDatabase(i),n(!0)},r.onupgradeneeded=()=>{t=!1},r.onerror=()=>{var s;e(((s=r.error)==null?void 0:s.message)||"")}}catch(t){e(t)}})}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const mi="FirebaseError";class z extends Error{constructor(e,t,i){super(t),this.code=e,this.customData=i,this.name=mi,Object.setPrototypeOf(this,z.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,he.prototype.create)}}class he{constructor(e,t,i){this.service=e,this.serviceName=t,this.errors=i}create(e,...t){const i=t[0]||{},r=`${this.service}/${e}`,s=this.errors[e],a=s?gi(s,i):"Error",c=`${this.serviceName}: ${a} (${r}).`;return new z(r,c,i)}}function gi(n,e){return n.replace(_i,(t,i)=>{const r=e[i];return r!=null?String(r):`<${i}?>`})}const _i=/\{\$([^}]+)}/g;function vi(n){for(const e in n)if(Object.prototype.hasOwnProperty.call(n,e))return!1;return!0}function ne(n,e){if(n===e)return!0;const t=Object.keys(n),i=Object.keys(e);for(const r of t){if(!i.includes(r))return!1;const s=n[r],a=e[r];if(_t(s)&&_t(a)){if(!ne(s,a))return!1}else if(s!==a)return!1}for(const r of i)if(!t.includes(r))return!1;return!0}function _t(n){return n!==null&&typeof n=="object"}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function fe(n){const e=[];for(const[t,i]of Object.entries(n))Array.isArray(i)?i.forEach(r=>{e.push(encodeURIComponent(t)+"="+encodeURIComponent(r))}):e.push(encodeURIComponent(t)+"="+encodeURIComponent(i));return e.length?"&"+e.join("&"):""}function yi(n,e){const t=new Ii(n,e);return t.subscribe.bind(t)}class Ii{constructor(e,t){this.observers=[],this.unsubscribes=[],this.observerCount=0,this.task=Promise.resolve(),this.finalized=!1,this.onNoObservers=t,this.task.then(()=>{e(this)}).catch(i=>{this.error(i)})}next(e){this.forEachObserver(t=>{t.next(e)})}error(e){this.forEachObserver(t=>{t.error(e)}),this.close(e)}complete(){this.forEachObserver(e=>{e.complete()}),this.close()}subscribe(e,t,i){let r;if(e===void 0&&t===void 0&&i===void 0)throw new Error("Missing Observer.");bi(e,["next","error","complete"])?r=e:r={next:e,error:t,complete:i},r.next===void 0&&(r.next=Ve),r.error===void 0&&(r.error=Ve),r.complete===void 0&&(r.complete=Ve);const s=this.unsubscribeOne.bind(this,this.observers.length);return this.finalized&&this.task.then(()=>{try{this.finalError?r.error(this.finalError):r.complete()}catch{}}),this.observers.push(r),s}unsubscribeOne(e){this.observers===void 0||this.observers[e]===void 0||(delete this.observers[e],this.observerCount-=1,this.observerCount===0&&this.onNoObservers!==void 0&&this.onNoObservers(this))}forEachObserver(e){if(!this.finalized)for(let t=0;t<this.observers.length;t++)this.sendOne(t,e)}sendOne(e,t){this.task.then(()=>{if(this.observers!==void 0&&this.observers[e]!==void 0)try{t(this.observers[e])}catch(i){typeof console<"u"&&console.error&&console.error(i)}})}close(e){this.finalized||(this.finalized=!0,e!==void 0&&(this.finalError=e),this.task.then(()=>{this.observers=void 0,this.onNoObservers=void 0}))}}function bi(n,e){if(typeof n!="object"||n===null)return!1;for(const t of e)if(t in n&&typeof n[t]=="function")return!0;return!1}function Ve(){}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function G(n){return n&&n._delegate?n._delegate:n}/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ze(n){try{return(n.startsWith("http://")||n.startsWith("https://")?new URL(n).hostname:n).endsWith(".cloudworkstations.dev")}catch{return!1}}async function wi(n){return(await fetch(n,{credentials:"include"})).ok}class ie{constructor(e,t,i){this.name=e,this.instanceFactory=t,this.type=i,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const q="[DEFAULT]";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ki{constructor(e,t){this.name=e,this.container=t,this.component=null,this.instances=new Map,this.instancesDeferred=new Map,this.instancesOptions=new Map,this.onInitCallbacks=new Map}get(e){const t=this.normalizeInstanceIdentifier(e);if(!this.instancesDeferred.has(t)){const i=new oi;if(this.instancesDeferred.set(t,i),this.isInitialized(t)||this.shouldAutoInitialize())try{const r=this.getOrInitializeService({instanceIdentifier:t});r&&i.resolve(r)}catch{}}return this.instancesDeferred.get(t).promise}getImmediate(e){const t=this.normalizeInstanceIdentifier(e==null?void 0:e.identifier),i=(e==null?void 0:e.optional)??!1;if(this.isInitialized(t)||this.shouldAutoInitialize())try{return this.getOrInitializeService({instanceIdentifier:t})}catch(r){if(i)return null;throw r}else{if(i)return null;throw Error(`Service ${this.name} is not available`)}}getComponent(){return this.component}setComponent(e){if(e.name!==this.name)throw Error(`Mismatching Component ${e.name} for Provider ${this.name}.`);if(this.component)throw Error(`Component for ${this.name} has already been provided`);if(this.component=e,!!this.shouldAutoInitialize()){if(Ti(e))try{this.getOrInitializeService({instanceIdentifier:q})}catch{}for(const[t,i]of this.instancesDeferred.entries()){const r=this.normalizeInstanceIdentifier(t);try{const s=this.getOrInitializeService({instanceIdentifier:r});i.resolve(s)}catch{}}}}clearInstance(e=q){this.instancesDeferred.delete(e),this.instancesOptions.delete(e),this.instances.delete(e)}async delete(){const e=Array.from(this.instances.values());await Promise.all([...e.filter(t=>"INTERNAL"in t).map(t=>t.INTERNAL.delete()),...e.filter(t=>"_delete"in t).map(t=>t._delete())])}isComponentSet(){return this.component!=null}isInitialized(e=q){return this.instances.has(e)}getOptions(e=q){return this.instancesOptions.get(e)||{}}initialize(e={}){const{options:t={}}=e,i=this.normalizeInstanceIdentifier(e.instanceIdentifier);if(this.isInitialized(i))throw Error(`${this.name}(${i}) has already been initialized`);if(!this.isComponentSet())throw Error(`Component ${this.name} has not been registered yet`);const r=this.getOrInitializeService({instanceIdentifier:i,options:t});for(const[s,a]of this.instancesDeferred.entries()){const c=this.normalizeInstanceIdentifier(s);i===c&&a.resolve(r)}return r}onInit(e,t){const i=this.normalizeInstanceIdentifier(t),r=this.onInitCallbacks.get(i)??new Set;r.add(e),this.onInitCallbacks.set(i,r);const s=this.instances.get(i);return s&&e(s,i),()=>{r.delete(e)}}invokeOnInitCallbacks(e,t){const i=this.onInitCallbacks.get(t);if(i)for(const r of i)try{r(e,t)}catch{}}getOrInitializeService({instanceIdentifier:e,options:t={}}){let i=this.instances.get(e);if(!i&&this.component&&(i=this.component.instanceFactory(this.container,{instanceIdentifier:Ei(e),options:t}),this.instances.set(e,i),this.instancesOptions.set(e,t),this.invokeOnInitCallbacks(i,e),this.component.onInstanceCreated))try{this.component.onInstanceCreated(this.container,e,i)}catch{}return i||null}normalizeInstanceIdentifier(e=q){return this.component?this.component.multipleInstances?e:q:e}shouldAutoInitialize(){return!!this.component&&this.component.instantiationMode!=="EXPLICIT"}}function Ei(n){return n===q?void 0:n}function Ti(n){return n.instantiationMode==="EAGER"}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Si{constructor(e){this.name=e,this.providers=new Map}addComponent(e){const t=this.getProvider(e.name);if(t.isComponentSet())throw new Error(`Component ${e.name} has already been registered with ${this.name}`);t.setComponent(e)}addOrOverwriteComponent(e){this.getProvider(e.name).isComponentSet()&&this.providers.delete(e.name),this.addComponent(e)}getProvider(e){if(this.providers.has(e))return this.providers.get(e);const t=new ki(e,this);return this.providers.set(e,t),t}getProviders(){return Array.from(this.providers.values())}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var _;(function(n){n[n.DEBUG=0]="DEBUG",n[n.VERBOSE=1]="VERBOSE",n[n.INFO=2]="INFO",n[n.WARN=3]="WARN",n[n.ERROR=4]="ERROR",n[n.SILENT=5]="SILENT"})(_||(_={}));const Ai={debug:_.DEBUG,verbose:_.VERBOSE,info:_.INFO,warn:_.WARN,error:_.ERROR,silent:_.SILENT},Ci=_.INFO,Pi={[_.DEBUG]:"log",[_.VERBOSE]:"log",[_.INFO]:"info",[_.WARN]:"warn",[_.ERROR]:"error"},Ri=(n,e,...t)=>{if(e<n.logLevel)return;const i=new Date().toISOString(),r=Pi[e];if(r)console[r](`[${i}]  ${n.name}:`,...t);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class Jt{constructor(e){this.name=e,this._logLevel=Ci,this._logHandler=Ri,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in _))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?Ai[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,_.DEBUG,...e),this._logHandler(this,_.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,_.VERBOSE,...e),this._logHandler(this,_.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,_.INFO,...e),this._logHandler(this,_.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,_.WARN,...e),this._logHandler(this,_.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,_.ERROR,...e),this._logHandler(this,_.ERROR,...e)}}const Oi=(n,e)=>e.some(t=>n instanceof t);let vt,yt;function Ni(){return vt||(vt=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Di(){return yt||(yt=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Yt=new WeakMap,ze=new WeakMap,Xt=new WeakMap,Be=new WeakMap,et=new WeakMap;function Li(n){const e=new Promise((t,i)=>{const r=()=>{n.removeEventListener("success",s),n.removeEventListener("error",a)},s=()=>{t(H(n.result)),r()},a=()=>{i(n.error),r()};n.addEventListener("success",s),n.addEventListener("error",a)});return e.then(t=>{t instanceof IDBCursor&&Yt.set(t,n)}).catch(()=>{}),et.set(e,n),e}function Mi(n){if(ze.has(n))return;const e=new Promise((t,i)=>{const r=()=>{n.removeEventListener("complete",s),n.removeEventListener("error",a),n.removeEventListener("abort",a)},s=()=>{t(),r()},a=()=>{i(n.error||new DOMException("AbortError","AbortError")),r()};n.addEventListener("complete",s),n.addEventListener("error",a),n.addEventListener("abort",a)});ze.set(n,e)}let Ge={get(n,e,t){if(n instanceof IDBTransaction){if(e==="done")return ze.get(n);if(e==="objectStoreNames")return n.objectStoreNames||Xt.get(n);if(e==="store")return t.objectStoreNames[1]?void 0:t.objectStore(t.objectStoreNames[0])}return H(n[e])},set(n,e,t){return n[e]=t,!0},has(n,e){return n instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in n}};function Ui(n){Ge=n(Ge)}function xi(n){return n===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...t){const i=n.call(Fe(this),e,...t);return Xt.set(i,e.sort?e.sort():[e]),H(i)}:Di().includes(n)?function(...e){return n.apply(Fe(this),e),H(Yt.get(this))}:function(...e){return H(n.apply(Fe(this),e))}}function Vi(n){return typeof n=="function"?xi(n):(n instanceof IDBTransaction&&Mi(n),Oi(n,Ni())?new Proxy(n,Ge):n)}function H(n){if(n instanceof IDBRequest)return Li(n);if(Be.has(n))return Be.get(n);const e=Vi(n);return e!==n&&(Be.set(n,e),et.set(e,n)),e}const Fe=n=>et.get(n);function Bi(n,e,{blocked:t,upgrade:i,blocking:r,terminated:s}={}){const a=indexedDB.open(n,e),c=H(a);return i&&a.addEventListener("upgradeneeded",o=>{i(H(a.result),o.oldVersion,o.newVersion,H(a.transaction),o)}),t&&a.addEventListener("blocked",o=>t(o.oldVersion,o.newVersion,o)),c.then(o=>{s&&o.addEventListener("close",()=>s()),r&&o.addEventListener("versionchange",h=>r(h.oldVersion,h.newVersion,h))}).catch(()=>{}),c}const Fi=["get","getKey","getAll","getAllKeys","count"],ji=["put","add","delete","clear"],je=new Map;function It(n,e){if(!(n instanceof IDBDatabase&&!(e in n)&&typeof e=="string"))return;if(je.get(e))return je.get(e);const t=e.replace(/FromIndex$/,""),i=e!==t,r=ji.includes(t);if(!(t in(i?IDBIndex:IDBObjectStore).prototype)||!(r||Fi.includes(t)))return;const s=async function(a,...c){const o=this.transaction(a,r?"readwrite":"readonly");let h=o.store;return i&&(h=h.index(c.shift())),(await Promise.all([h[t](...c),r&&o.done]))[0]};return je.set(e,s),s}Ui(n=>({...n,get:(e,t,i)=>It(e,t)||n.get(e,t,i),has:(e,t)=>!!It(e,t)||n.has(e,t)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class $i{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(t=>{if(Hi(t)){const i=t.getImmediate();return`${i.library}/${i.version}`}else return null}).filter(t=>t).join(" ")}}function Hi(n){const e=n.getComponent();return(e==null?void 0:e.type)==="VERSION"}const Ke="@firebase/app",bt="0.15.0";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const x=new Jt("@firebase/app"),Wi="@firebase/app-compat",zi="@firebase/analytics-compat",Gi="@firebase/analytics",Ki="@firebase/app-check-compat",qi="@firebase/app-check",Ji="@firebase/auth",Yi="@firebase/auth-compat",Xi="@firebase/database",Qi="@firebase/data-connect",Zi="@firebase/database-compat",er="@firebase/functions",tr="@firebase/functions-compat",nr="@firebase/installations",ir="@firebase/installations-compat",rr="@firebase/messaging",sr="@firebase/messaging-compat",ar="@firebase/performance",or="@firebase/performance-compat",cr="@firebase/remote-config",lr="@firebase/remote-config-compat",ur="@firebase/storage",dr="@firebase/storage-compat",hr="@firebase/firestore",fr="@firebase/ai",pr="@firebase/firestore-compat",mr="firebase",gr="12.15.0";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const qe="[DEFAULT]",_r={[Ke]:"fire-core",[Wi]:"fire-core-compat",[Gi]:"fire-analytics",[zi]:"fire-analytics-compat",[qi]:"fire-app-check",[Ki]:"fire-app-check-compat",[Ji]:"fire-auth",[Yi]:"fire-auth-compat",[Xi]:"fire-rtdb",[Qi]:"fire-data-connect",[Zi]:"fire-rtdb-compat",[er]:"fire-fn",[tr]:"fire-fn-compat",[nr]:"fire-iid",[ir]:"fire-iid-compat",[rr]:"fire-fcm",[sr]:"fire-fcm-compat",[ar]:"fire-perf",[or]:"fire-perf-compat",[cr]:"fire-rc",[lr]:"fire-rc-compat",[ur]:"fire-gcs",[dr]:"fire-gcs-compat",[hr]:"fire-fst",[pr]:"fire-fst-compat",[fr]:"fire-vertex","fire-js":"fire-js",[mr]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Te=new Map,vr=new Map,Je=new Map;function wt(n,e){try{n.container.addComponent(e)}catch(t){x.debug(`Component ${e.name} failed to register with FirebaseApp ${n.name}`,t)}}function le(n){const e=n.name;if(Je.has(e))return x.debug(`There were multiple attempts to register component ${e}.`),!1;Je.set(e,n);for(const t of Te.values())wt(t,n);for(const t of vr.values())wt(t,n);return!0}function Qt(n,e){const t=n.container.getProvider("heartbeat").getImmediate({optional:!0});return t&&t.triggerHeartbeat(),n.container.getProvider(e)}function R(n){return n==null?!1:n.settings!==void 0}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const yr={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},W=new he("app","Firebase",yr);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Ir{constructor(e,t,i){this._isDeleted=!1,this._options={...e},this._config={...t},this._name=t.name,this._automaticDataCollectionEnabled=t.automaticDataCollectionEnabled,this._container=i,this.container.addComponent(new ie("app",()=>this,"PUBLIC"))}get automaticDataCollectionEnabled(){return this.checkDestroyed(),this._automaticDataCollectionEnabled}set automaticDataCollectionEnabled(e){this.checkDestroyed(),this._automaticDataCollectionEnabled=e}get name(){return this.checkDestroyed(),this._name}get options(){return this.checkDestroyed(),this._options}get config(){return this.checkDestroyed(),this._config}get container(){return this._container}get isDeleted(){return this._isDeleted}set isDeleted(e){this._isDeleted=e}checkDestroyed(){if(this.isDeleted)throw W.create("app-deleted",{appName:this._name})}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const pe=gr;function Zt(n,e={}){let t=n;typeof e!="object"&&(e={name:e});const i={name:qe,automaticDataCollectionEnabled:!0,...e},r=i.name;if(typeof r!="string"||!r)throw W.create("bad-app-name",{appName:String(r)});if(t||(t=Kt()),!t)throw W.create("no-options");const s=Te.get(r);if(s){if(ne(t,s.options)&&ne(i,s.config))return s;throw W.create("duplicate-app",{appName:r})}const a=new Si(r);for(const o of Je.values())a.addComponent(o);const c=new Ir(t,i,a);return Te.set(r,c),c}function br(n=qe){const e=Te.get(n);if(!e&&n===qe&&Kt())return Zt();if(!e)throw W.create("no-app",{appName:n});return e}function Q(n,e,t){let i=_r[n]??n;t&&(i+=`-${t}`);const r=i.match(/\s|\//),s=e.match(/\s|\//);if(r||s){const a=[`Unable to register library "${i}" with version "${e}":`];r&&a.push(`library name "${i}" contains illegal characters (whitespace or "/")`),r&&s&&a.push("and"),s&&a.push(`version name "${e}" contains illegal characters (whitespace or "/")`),x.warn(a.join(" "));return}le(new ie(`${i}-version`,()=>({library:i,version:e}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const wr="firebase-heartbeat-database",kr=1,ue="firebase-heartbeat-store";let $e=null;function en(){return $e||($e=Bi(wr,kr,{upgrade:(n,e)=>{switch(e){case 0:try{n.createObjectStore(ue)}catch(t){console.warn(t)}}}}).catch(n=>{throw W.create("idb-open",{originalErrorMessage:n.message})})),$e}async function Er(n){try{const t=(await en()).transaction(ue),i=await t.objectStore(ue).get(tn(n));return await t.done,i}catch(e){if(e instanceof z)x.warn(e.message);else{const t=W.create("idb-get",{originalErrorMessage:e==null?void 0:e.message});x.warn(t.message)}}}async function kt(n,e){try{const i=(await en()).transaction(ue,"readwrite");await i.objectStore(ue).put(e,tn(n)),await i.done}catch(t){if(t instanceof z)x.warn(t.message);else{const i=W.create("idb-set",{originalErrorMessage:t==null?void 0:t.message});x.warn(i.message)}}}function tn(n){return`${n.name}!${n.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Tr=1024,Sr=30;class Ar{constructor(e){this.container=e,this._heartbeatsCache=null;const t=this.container.getProvider("app").getImmediate();this._storage=new Pr(t),this._heartbeatsCachePromise=this._storage.read().then(i=>(this._heartbeatsCache=i,i))}async triggerHeartbeat(){var e,t;try{const r=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=Et();if(((e=this._heartbeatsCache)==null?void 0:e.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((t=this._heartbeatsCache)==null?void 0:t.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(a=>a.date===s))return;if(this._heartbeatsCache.heartbeats.push({date:s,agent:r}),this._heartbeatsCache.heartbeats.length>Sr){const a=Rr(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(a,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(i){x.warn(i)}}async getHeartbeatsHeader(){var e;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((e=this._heartbeatsCache)==null?void 0:e.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const t=Et(),{heartbeatsToSend:i,unsentEntries:r}=Cr(this._heartbeatsCache.heartbeats),s=zt(JSON.stringify({version:2,heartbeats:i}));return this._heartbeatsCache.lastSentHeartbeatDate=t,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}catch(t){return x.warn(t),""}}}function Et(){return new Date().toISOString().substring(0,10)}function Cr(n,e=Tr){const t=[];let i=n.slice();for(const r of n){const s=t.find(a=>a.agent===r.agent);if(s){if(s.dates.push(r.date),Tt(t)>e){s.dates.pop();break}}else if(t.push({agent:r.agent,dates:[r.date]}),Tt(t)>e){t.pop();break}i=i.slice(1)}return{heartbeatsToSend:t,unsentEntries:i}}class Pr{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return fi()?pi().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const t=await Er(this.app);return t!=null&&t.heartbeats?t:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(e){if(await this._canUseIndexedDBPromise){const i=await this.read();return kt(this.app,{lastSentHeartbeatDate:e.lastSentHeartbeatDate??i.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){if(await this._canUseIndexedDBPromise){const i=await this.read();return kt(this.app,{lastSentHeartbeatDate:e.lastSentHeartbeatDate??i.lastSentHeartbeatDate,heartbeats:[...i.heartbeats,...e.heartbeats]})}else return}}function Tt(n){return zt(JSON.stringify({version:2,heartbeats:n})).length}function Rr(n){if(n.length===0)return-1;let e=0,t=n[0].date;for(let i=1;i<n.length;i++)n[i].date<t&&(t=n[i].date,e=i);return e}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Or(n){le(new ie("platform-logger",e=>new $i(e),"PRIVATE")),le(new ie("heartbeat",e=>new Ar(e),"PRIVATE")),Q(Ke,bt,n),Q(Ke,bt,"esm2020"),Q("fire-js","")}Or("");function nn(){return{"dependent-sdk-initialized-before-auth":"Another Firebase SDK was initialized and is trying to use Auth before Auth is initialized. Please be sure to call `initializeAuth` or `getAuth` before starting any other Firebase SDK."}}const Nr=nn,rn=new he("auth","Firebase",nn());/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Se=new Jt("@firebase/auth");function Dr(n,...e){Se.logLevel<=_.WARN&&Se.warn(`Auth (${pe}): ${n}`,...e)}function be(n,...e){Se.logLevel<=_.ERROR&&Se.error(`Auth (${pe}): ${n}`,...e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function N(n,...e){throw nt(n,...e)}function C(n,...e){return nt(n,...e)}function tt(n,e,t){const i={...Nr(),[e]:t};return new he("auth","Firebase",i).create(e,{appName:n.name})}function Y(n){return tt(n,"operation-not-supported-in-this-environment","Operations that alter the current user are not supported in conjunction with FirebaseServerApp")}function Lr(n,e,t){const i=t;if(!(e instanceof i))throw i.name!==e.constructor.name&&N(n,"argument-error"),tt(n,"argument-error",`Type of ${e.constructor.name} does not match expected instance.Did you pass a reference from a different Auth SDK?`)}function nt(n,...e){if(typeof n!="string"){const t=e[0],i=[...e.slice(1)];return i[0]&&(i[0].appName=n.name),n._errorFactory.create(t,...i)}return rn.create(n,...e)}function f(n,e,...t){if(!n)throw nt(e,...t)}function M(n){const e="INTERNAL ASSERTION FAILED: "+n;throw be(e),new Error(e)}function V(n,e){n||M(e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ye(){var n;return typeof self<"u"&&((n=self.location)==null?void 0:n.href)||""}function Mr(){return St()==="http:"||St()==="https:"}function St(){var n;return typeof self<"u"&&((n=self.location)==null?void 0:n.protocol)||null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ur(){return typeof navigator<"u"&&navigator&&"onLine"in navigator&&typeof navigator.onLine=="boolean"&&(Mr()||ui()||"connection"in navigator)?navigator.onLine:!0}function xr(){if(typeof navigator>"u")return null;const n=navigator;return n.languages&&n.languages[0]||n.language||null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class me{constructor(e,t){this.shortDelay=e,this.longDelay=t,V(t>e,"Short delay should be less than long delay!"),this.isMobile=ci()||di()}get(){return Ur()?this.isMobile?this.longDelay:this.shortDelay:Math.min(5e3,this.shortDelay)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function it(n,e){V(n.emulator,"Emulator should always be set here");const{url:t}=n.emulator;return e?`${t}${e.startsWith("/")?e.slice(1):e}`:t}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class sn{static initialize(e,t,i){this.fetchImpl=e,t&&(this.headersImpl=t),i&&(this.responseImpl=i)}static fetch(){if(this.fetchImpl)return this.fetchImpl;if(typeof self<"u"&&"fetch"in self)return self.fetch;if(typeof globalThis<"u"&&globalThis.fetch)return globalThis.fetch;if(typeof fetch<"u")return fetch;M("Could not find fetch implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static headers(){if(this.headersImpl)return this.headersImpl;if(typeof self<"u"&&"Headers"in self)return self.Headers;if(typeof globalThis<"u"&&globalThis.Headers)return globalThis.Headers;if(typeof Headers<"u")return Headers;M("Could not find Headers implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}static response(){if(this.responseImpl)return this.responseImpl;if(typeof self<"u"&&"Response"in self)return self.Response;if(typeof globalThis<"u"&&globalThis.Response)return globalThis.Response;if(typeof Response<"u")return Response;M("Could not find Response implementation, make sure you call FetchProvider.initialize() with an appropriate polyfill")}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Vr={CREDENTIAL_MISMATCH:"custom-token-mismatch",MISSING_CUSTOM_TOKEN:"internal-error",INVALID_IDENTIFIER:"invalid-email",MISSING_CONTINUE_URI:"internal-error",INVALID_PASSWORD:"wrong-password",MISSING_PASSWORD:"missing-password",INVALID_LOGIN_CREDENTIALS:"invalid-credential",EMAIL_EXISTS:"email-already-in-use",PASSWORD_LOGIN_DISABLED:"operation-not-allowed",INVALID_IDP_RESPONSE:"invalid-credential",INVALID_PENDING_TOKEN:"invalid-credential",FEDERATED_USER_ID_ALREADY_LINKED:"credential-already-in-use",MISSING_REQ_TYPE:"internal-error",EMAIL_NOT_FOUND:"user-not-found",RESET_PASSWORD_EXCEED_LIMIT:"too-many-requests",EXPIRED_OOB_CODE:"expired-action-code",INVALID_OOB_CODE:"invalid-action-code",MISSING_OOB_CODE:"internal-error",CREDENTIAL_TOO_OLD_LOGIN_AGAIN:"requires-recent-login",INVALID_ID_TOKEN:"invalid-user-token",TOKEN_EXPIRED:"user-token-expired",USER_NOT_FOUND:"user-token-expired",TOO_MANY_ATTEMPTS_TRY_LATER:"too-many-requests",PASSWORD_DOES_NOT_MEET_REQUIREMENTS:"password-does-not-meet-requirements",INVALID_CODE:"invalid-verification-code",INVALID_SESSION_INFO:"invalid-verification-id",INVALID_TEMPORARY_PROOF:"invalid-credential",MISSING_SESSION_INFO:"missing-verification-id",SESSION_EXPIRED:"code-expired",MISSING_ANDROID_PACKAGE_NAME:"missing-android-pkg-name",UNAUTHORIZED_DOMAIN:"unauthorized-continue-uri",INVALID_OAUTH_CLIENT_ID:"invalid-oauth-client-id",ADMIN_ONLY_OPERATION:"admin-restricted-operation",INVALID_MFA_PENDING_CREDENTIAL:"invalid-multi-factor-session",MFA_ENROLLMENT_NOT_FOUND:"multi-factor-info-not-found",MISSING_MFA_ENROLLMENT_ID:"missing-multi-factor-info",MISSING_MFA_PENDING_CREDENTIAL:"missing-multi-factor-session",SECOND_FACTOR_EXISTS:"second-factor-already-in-use",SECOND_FACTOR_LIMIT_EXCEEDED:"maximum-second-factor-count-exceeded",BLOCKING_FUNCTION_ERROR_RESPONSE:"internal-error",RECAPTCHA_NOT_ENABLED:"recaptcha-not-enabled",MISSING_RECAPTCHA_TOKEN:"missing-recaptcha-token",INVALID_RECAPTCHA_TOKEN:"invalid-recaptcha-token",INVALID_RECAPTCHA_ACTION:"invalid-recaptcha-action",MISSING_CLIENT_TYPE:"missing-client-type",MISSING_RECAPTCHA_VERSION:"missing-recaptcha-version",INVALID_RECAPTCHA_VERSION:"invalid-recaptcha-version",INVALID_REQ_TYPE:"invalid-req-type"};/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Br=["/v1/accounts:signInWithCustomToken","/v1/accounts:signInWithEmailLink","/v1/accounts:signInWithIdp","/v1/accounts:signInWithPassword","/v1/accounts:signInWithPhoneNumber","/v1/token"],Fr=new me(3e4,6e4);function rt(n,e){return n.tenantId&&!e.tenantId?{...e,tenantId:n.tenantId}:e}async function se(n,e,t,i,r={}){return an(n,r,async()=>{let s={},a={};i&&(e==="GET"?a=i:s={body:JSON.stringify(i)});const c=fe({...a,key:n.config.apiKey}).slice(1),o=await n._getAdditionalHeaders();o["Content-Type"]="application/json",n.languageCode&&(o["X-Firebase-Locale"]=n.languageCode);const h={method:e,headers:o,...s};return li()||(h.referrerPolicy="strict-origin-when-cross-origin"),n.emulatorConfig&&Ze(n.emulatorConfig.host)&&(h.credentials="include"),sn.fetch()(await on(n,n.config.apiHost,t,c),h)})}async function an(n,e,t){n._canInitEmulator=!1;const i={...Vr,...e};try{const r=new $r(n),s=await Promise.race([t(),r.promise]);r.clearNetworkTimeout();const a=await s.json();if("needConfirmation"in a)throw Ie(n,"account-exists-with-different-credential",a);if(s.ok&&!("errorMessage"in a))return a;{const c=s.ok?a.errorMessage:a.error.message,[o,h]=c.split(" : ");if(o==="FEDERATED_USER_ID_ALREADY_LINKED")throw Ie(n,"credential-already-in-use",a);if(o==="EMAIL_EXISTS")throw Ie(n,"email-already-in-use",a);if(o==="USER_DISABLED")throw Ie(n,"user-disabled",a);const d=i[o]||o.toLowerCase().replace(/[_\s]+/g,"-");if(h)throw tt(n,d,h);N(n,d)}}catch(r){if(r instanceof z)throw r;N(n,"network-request-failed",{message:String(r)})}}async function jr(n,e,t,i,r={}){const s=await se(n,e,t,i,r);return"mfaPendingCredential"in s&&N(n,"multi-factor-auth-required",{_serverResponse:s}),s}async function on(n,e,t,i){const r=`${e}${t}?${i}`,s=n,a=s.config.emulator?it(n.config,r):`${n.config.apiScheme}://${r}`;return Br.includes(t)&&(await s._persistenceManagerAvailable,s._getPersistenceType()==="COOKIE")?s._getPersistence()._getFinalTarget(a).toString():a}class $r{clearNetworkTimeout(){clearTimeout(this.timer)}constructor(e){this.auth=e,this.timer=null,this.promise=new Promise((t,i)=>{this.timer=setTimeout(()=>i(C(this.auth,"network-request-failed")),Fr.get())})}}function Ie(n,e,t){const i={appName:n.name};t.email&&(i.email=t.email),t.phoneNumber&&(i.phoneNumber=t.phoneNumber);const r=C(n,e,i);return r.customData._tokenResponse=t,r}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Hr(n,e){return se(n,"POST","/v1/accounts:delete",e)}async function Ae(n,e){return se(n,"POST","/v1/accounts:lookup",e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ce(n){if(n)try{const e=new Date(Number(n));if(!isNaN(e.getTime()))return e.toUTCString()}catch{}}async function Wr(n,e=!1){const t=G(n),i=await t.getIdToken(e),r=st(i);f(r&&r.exp&&r.auth_time&&r.iat,t.auth,"internal-error");const s=typeof r.firebase=="object"?r.firebase:void 0,a=s==null?void 0:s.sign_in_provider;return{claims:r,token:i,authTime:ce(He(r.auth_time)),issuedAtTime:ce(He(r.iat)),expirationTime:ce(He(r.exp)),signInProvider:a||null,signInSecondFactor:(s==null?void 0:s.sign_in_second_factor)||null}}function He(n){return Number(n)*1e3}function st(n){const[e,t,i]=n.split(".");if(e===void 0||t===void 0||i===void 0)return be("JWT malformed, contained fewer than 3 sections"),null;try{const r=Gt(t);return r?JSON.parse(r):(be("Failed to decode base64 JWT payload"),null)}catch(r){return be("Caught error parsing JWT payload as JSON",r==null?void 0:r.toString()),null}}function At(n){const e=st(n);return f(e,"internal-error"),f(typeof e.exp<"u","internal-error"),f(typeof e.iat<"u","internal-error"),Number(e.exp)-Number(e.iat)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function de(n,e,t=!1){if(t)return e;try{return await e}catch(i){throw i instanceof z&&zr(i)&&n.auth.currentUser===n&&await n.auth.signOut(),i}}function zr({code:n}){return n==="auth/user-disabled"||n==="auth/user-token-expired"}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Gr{constructor(e){this.user=e,this.isRunning=!1,this.timerId=null,this.errorBackoff=3e4}_start(){this.isRunning||(this.isRunning=!0,this.schedule())}_stop(){this.isRunning&&(this.isRunning=!1,this.timerId!==null&&clearTimeout(this.timerId))}getInterval(e){if(e){const t=this.errorBackoff;return this.errorBackoff=Math.min(this.errorBackoff*2,96e4),t}else{this.errorBackoff=3e4;const i=(this.user.stsTokenManager.expirationTime??0)-Date.now()-3e5;return Math.max(0,i)}}schedule(e=!1){if(!this.isRunning)return;const t=this.getInterval(e);this.timerId=setTimeout(async()=>{await this.iteration()},t)}async iteration(){try{await this.user.getIdToken(!0)}catch(e){(e==null?void 0:e.code)==="auth/network-request-failed"&&this.schedule(!0);return}this.schedule()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Xe{constructor(e,t){this.createdAt=e,this.lastLoginAt=t,this._initializeTime()}_initializeTime(){this.lastSignInTime=ce(this.lastLoginAt),this.creationTime=ce(this.createdAt)}_copy(e){this.createdAt=e.createdAt,this.lastLoginAt=e.lastLoginAt,this._initializeTime()}toJSON(){return{createdAt:this.createdAt,lastLoginAt:this.lastLoginAt}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Ce(n){var g;const e=n.auth,t=await n.getIdToken(),i=await de(n,Ae(e,{idToken:t}));f(i==null?void 0:i.users.length,e,"internal-error");const r=i.users[0];n._notifyReloadListener(r);const s=(g=r.providerUserInfo)!=null&&g.length?cn(r.providerUserInfo):[],a=qr(n.providerData,s),c=n.isAnonymous,o=!(n.email&&r.passwordHash)&&!(a!=null&&a.length),h=c?o:!1,d={uid:r.localId,displayName:r.displayName||null,photoURL:r.photoUrl||null,email:r.email||null,emailVerified:r.emailVerified||!1,phoneNumber:r.phoneNumber||null,tenantId:r.tenantId||null,providerData:a,metadata:new Xe(r.createdAt,r.lastLoginAt),isAnonymous:h};Object.assign(n,d)}async function Kr(n){const e=G(n);await Ce(e),await e.auth._persistUserIfCurrent(e),e.auth._notifyListenersIfCurrent(e)}function qr(n,e){return[...n.filter(i=>!e.some(r=>r.providerId===i.providerId)),...e]}function cn(n){return n.map(({providerId:e,...t})=>({providerId:e,uid:t.rawId||"",displayName:t.displayName||null,email:t.email||null,phoneNumber:t.phoneNumber||null,photoURL:t.photoUrl||null}))}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Jr(n,e){const t=await an(n,{},async()=>{const i=fe({grant_type:"refresh_token",refresh_token:e}).slice(1),{tokenApiHost:r,apiKey:s}=n.config,a=await on(n,r,"/v1/token",`key=${s}`),c=await n._getAdditionalHeaders();c["Content-Type"]="application/x-www-form-urlencoded";const o={method:"POST",headers:c,body:i};return n.emulatorConfig&&Ze(n.emulatorConfig.host)&&(o.credentials="include"),sn.fetch()(a,o)});return{accessToken:t.access_token,expiresIn:t.expires_in,refreshToken:t.refresh_token}}async function Yr(n,e){return se(n,"POST","/v2/accounts:revokeToken",rt(n,e))}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Z{constructor(){this.refreshToken=null,this.accessToken=null,this.expirationTime=null}get isExpired(){return!this.expirationTime||Date.now()>this.expirationTime-3e4}updateFromServerResponse(e){f(e.idToken,"internal-error"),f(typeof e.idToken<"u","internal-error"),f(typeof e.refreshToken<"u","internal-error");const t="expiresIn"in e&&typeof e.expiresIn<"u"?Number(e.expiresIn):At(e.idToken);this.updateTokensAndExpiration(e.idToken,e.refreshToken,t)}updateFromIdToken(e){f(e.length!==0,"internal-error");const t=At(e);this.updateTokensAndExpiration(e,null,t)}async getToken(e,t=!1){return!t&&this.accessToken&&!this.isExpired?this.accessToken:(f(this.refreshToken,e,"user-token-expired"),this.refreshToken?(await this.refresh(e,this.refreshToken),this.accessToken):null)}clearRefreshToken(){this.refreshToken=null}async refresh(e,t){const{accessToken:i,refreshToken:r,expiresIn:s}=await Jr(e,t);this.updateTokensAndExpiration(i,r,Number(s))}updateTokensAndExpiration(e,t,i){this.refreshToken=t||null,this.accessToken=e||null,this.expirationTime=Date.now()+i*1e3}static fromJSON(e,t){const{refreshToken:i,accessToken:r,expirationTime:s}=t,a=new Z;return i&&(f(typeof i=="string","internal-error",{appName:e}),a.refreshToken=i),r&&(f(typeof r=="string","internal-error",{appName:e}),a.accessToken=r),s&&(f(typeof s=="number","internal-error",{appName:e}),a.expirationTime=s),a}toJSON(){return{refreshToken:this.refreshToken,accessToken:this.accessToken,expirationTime:this.expirationTime}}_assign(e){this.accessToken=e.accessToken,this.refreshToken=e.refreshToken,this.expirationTime=e.expirationTime}_clone(){return Object.assign(new Z,this.toJSON())}_performRefresh(){return M("not implemented")}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function B(n,e){f(typeof n=="string"||typeof n>"u","internal-error",{appName:e})}class A{constructor({uid:e,auth:t,stsTokenManager:i,...r}){this.providerId="firebase",this.proactiveRefresh=new Gr(this),this.reloadUserInfo=null,this.reloadListener=null,this.uid=e,this.auth=t,this.stsTokenManager=i,this.accessToken=i.accessToken,this.displayName=r.displayName||null,this.email=r.email||null,this.emailVerified=r.emailVerified||!1,this.phoneNumber=r.phoneNumber||null,this.photoURL=r.photoURL||null,this.isAnonymous=r.isAnonymous||!1,this.tenantId=r.tenantId||null,this.providerData=r.providerData?[...r.providerData]:[],this.metadata=new Xe(r.createdAt||void 0,r.lastLoginAt||void 0)}async getIdToken(e){const t=await de(this,this.stsTokenManager.getToken(this.auth,e));return f(t,this.auth,"internal-error"),this.accessToken!==t&&(this.accessToken=t,await this.auth._persistUserIfCurrent(this),this.auth._notifyListenersIfCurrent(this)),t}getIdTokenResult(e){return Wr(this,e)}reload(){return Kr(this)}_assign(e){this!==e&&(f(this.uid===e.uid,this.auth,"internal-error"),this.displayName=e.displayName,this.photoURL=e.photoURL,this.email=e.email,this.emailVerified=e.emailVerified,this.phoneNumber=e.phoneNumber,this.isAnonymous=e.isAnonymous,this.tenantId=e.tenantId,this.providerData=e.providerData.map(t=>({...t})),this.metadata._copy(e.metadata),this.stsTokenManager._assign(e.stsTokenManager))}_clone(e){const t=new A({...this,auth:e,stsTokenManager:this.stsTokenManager._clone()});return t.metadata._copy(this.metadata),t}_onReload(e){f(!this.reloadListener,this.auth,"internal-error"),this.reloadListener=e,this.reloadUserInfo&&(this._notifyReloadListener(this.reloadUserInfo),this.reloadUserInfo=null)}_notifyReloadListener(e){this.reloadListener?this.reloadListener(e):this.reloadUserInfo=e}_startProactiveRefresh(){this.proactiveRefresh._start()}_stopProactiveRefresh(){this.proactiveRefresh._stop()}async _updateTokensIfNecessary(e,t=!1){let i=!1;e.idToken&&e.idToken!==this.stsTokenManager.accessToken&&(this.stsTokenManager.updateFromServerResponse(e),i=!0),t&&await Ce(this),await this.auth._persistUserIfCurrent(this),i&&this.auth._notifyListenersIfCurrent(this)}async delete(){if(R(this.auth.app))return Promise.reject(Y(this.auth));const e=await this.getIdToken();return await de(this,Hr(this.auth,{idToken:e})),this.stsTokenManager.clearRefreshToken(),this.auth.signOut()}toJSON(){return{uid:this.uid,email:this.email||void 0,emailVerified:this.emailVerified,displayName:this.displayName||void 0,isAnonymous:this.isAnonymous,photoURL:this.photoURL||void 0,phoneNumber:this.phoneNumber||void 0,tenantId:this.tenantId||void 0,providerData:this.providerData.map(e=>({...e})),stsTokenManager:this.stsTokenManager.toJSON(),_redirectEventId:this._redirectEventId,...this.metadata.toJSON(),apiKey:this.auth.config.apiKey,appName:this.auth.name}}get refreshToken(){return this.stsTokenManager.refreshToken||""}static _fromJSON(e,t){const i=t.displayName??void 0,r=t.email??void 0,s=t.phoneNumber??void 0,a=t.photoURL??void 0,c=t.tenantId??void 0,o=t._redirectEventId??void 0,h=t.createdAt??void 0,d=t.lastLoginAt??void 0,{uid:g,emailVerified:v,isAnonymous:T,providerData:k,stsTokenManager:ve}=t;f(g&&ve,e,"internal-error");const ye=Z.fromJSON(this.name,ve);f(typeof g=="string",e,"internal-error"),B(i,e.name),B(r,e.name),f(typeof v=="boolean",e,"internal-error"),f(typeof T=="boolean",e,"internal-error"),B(s,e.name),B(a,e.name),B(c,e.name),B(o,e.name),B(h,e.name),B(d,e.name);const ae=new A({uid:g,auth:e,email:r,emailVerified:v,displayName:i,isAnonymous:T,photoURL:a,phoneNumber:s,tenantId:c,stsTokenManager:ye,createdAt:h,lastLoginAt:d});return k&&Array.isArray(k)&&(ae.providerData=k.map(Me=>({...Me}))),o&&(ae._redirectEventId=o),ae}static async _fromIdTokenResponse(e,t,i=!1){const r=new Z;r.updateFromServerResponse(t);const s=new A({uid:t.localId,auth:e,stsTokenManager:r,isAnonymous:i});return await Ce(s),s}static async _fromGetAccountInfoResponse(e,t,i){const r=t.users[0];f(r.localId!==void 0,"internal-error");const s=r.providerUserInfo!==void 0?cn(r.providerUserInfo):[],a=!(r.email&&r.passwordHash)&&!(s!=null&&s.length),c=new Z;c.updateFromIdToken(i);const o=new A({uid:r.localId,auth:e,stsTokenManager:c,isAnonymous:a}),h={uid:r.localId,displayName:r.displayName||null,photoURL:r.photoUrl||null,email:r.email||null,emailVerified:r.emailVerified||!1,phoneNumber:r.phoneNumber||null,tenantId:r.tenantId||null,providerData:s,metadata:new Xe(r.createdAt,r.lastLoginAt),isAnonymous:!(r.email&&r.passwordHash)&&!(s!=null&&s.length)};return Object.assign(o,h),o}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ct=new Map;function U(n){V(n instanceof Function,"Expected a class definition");let e=Ct.get(n);return e?(V(e instanceof n,"Instance stored in cache mismatched with class"),e):(e=new n,Ct.set(n,e),e)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ln{constructor(){this.type="NONE",this.storage={}}async _isAvailable(){return!0}async _set(e,t){this.storage[e]=t}async _get(e){const t=this.storage[e];return t===void 0?null:t}async _remove(e){delete this.storage[e]}_addListener(e,t){}_removeListener(e,t){}}ln.type="NONE";const Pt=ln;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function we(n,e,t){return`firebase:${n}:${e}:${t}`}class ee{constructor(e,t,i){this.persistence=e,this.auth=t,this.userKey=i;const{config:r,name:s}=this.auth;this.fullUserKey=we(this.userKey,r.apiKey,s),this.fullPersistenceKey=we("persistence",r.apiKey,s),this.boundEventHandler=t._onStorageEvent.bind(t),this.persistence._addListener(this.fullUserKey,this.boundEventHandler)}setCurrentUser(e){return this.persistence._set(this.fullUserKey,e.toJSON())}async getCurrentUser(){const e=await this.persistence._get(this.fullUserKey);if(!e)return null;if(typeof e=="string"){const t=await Ae(this.auth,{idToken:e}).catch(()=>{});return t?A._fromGetAccountInfoResponse(this.auth,t,e):null}return A._fromJSON(this.auth,e)}removeCurrentUser(){return this.persistence._remove(this.fullUserKey)}savePersistenceForRedirect(){return this.persistence._set(this.fullPersistenceKey,this.persistence.type)}async setPersistence(e){if(this.persistence===e)return;const t=await this.getCurrentUser();if(await this.removeCurrentUser(),this.persistence=e,t)return this.setCurrentUser(t)}delete(){this.persistence._removeListener(this.fullUserKey,this.boundEventHandler)}static async create(e,t,i="authUser"){if(!t.length)return new ee(U(Pt),e,i);const r=(await Promise.all(t.map(async h=>{if(await h._isAvailable())return h}))).filter(h=>h);let s=r[0]||U(Pt);const a=we(i,e.config.apiKey,e.name);let c=null;for(const h of t)try{const d=await h._get(a);if(d){let g;if(typeof d=="string"){const v=await Ae(e,{idToken:d}).catch(()=>{});if(!v)break;g=await A._fromGetAccountInfoResponse(e,v,d)}else g=A._fromJSON(e,d);h!==s&&(c=g),s=h;break}}catch{}const o=r.filter(h=>h._shouldAllowMigration);return!s._shouldAllowMigration||!o.length?new ee(s,e,i):(s=o[0],c&&await s._set(a,c.toJSON()),await Promise.all(t.map(async h=>{if(h!==s)try{await h._remove(a)}catch{}})),new ee(s,e,i))}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Rt(n){const e=n.toLowerCase();if(e.includes("opera/")||e.includes("opr/")||e.includes("opios/"))return"Opera";if(fn(e))return"IEMobile";if(e.includes("msie")||e.includes("trident/"))return"IE";if(e.includes("edge/"))return"Edge";if(un(e))return"Firefox";if(e.includes("silk/"))return"Silk";if(mn(e))return"Blackberry";if(gn(e))return"Webos";if(dn(e))return"Safari";if((e.includes("chrome/")||hn(e))&&!e.includes("edge/"))return"Chrome";if(pn(e))return"Android";{const t=/([a-zA-Z\d\.]+)\/[a-zA-Z\d\.]*$/,i=n.match(t);if((i==null?void 0:i.length)===2)return i[1]}return"Other"}function un(n=b()){return/firefox\//i.test(n)}function dn(n=b()){const e=n.toLowerCase();return e.includes("safari/")&&!e.includes("chrome/")&&!e.includes("crios/")&&!e.includes("android")}function hn(n=b()){return/crios\//i.test(n)}function fn(n=b()){return/iemobile/i.test(n)}function pn(n=b()){return/android/i.test(n)}function mn(n=b()){return/blackberry/i.test(n)}function gn(n=b()){return/webos/i.test(n)}function at(n=b()){return/iphone|ipad|ipod/i.test(n)||/macintosh/i.test(n)&&/mobile/i.test(n)}function Xr(n=b()){var e;return at(n)&&!!((e=window.navigator)!=null&&e.standalone)}function Qr(){return hi()&&document.documentMode===10}function _n(n=b()){return at(n)||pn(n)||gn(n)||mn(n)||/windows phone/i.test(n)||fn(n)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function vn(n,e=[]){let t;switch(n){case"Browser":t=Rt(b());break;case"Worker":t=`${Rt(b())}-${n}`;break;default:t=n}const i=e.length?e.join(","):"FirebaseCore-web";return`${t}/JsCore/${pe}/${i}`}/**
 * @license
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Zr{constructor(e){this.auth=e,this.queue=[]}pushCallback(e,t){const i=s=>new Promise((a,c)=>{try{const o=e(s);a(o)}catch(o){c(o)}});i.onAbort=t,this.queue.push(i);const r=this.queue.length-1;return()=>{this.queue[r]=()=>Promise.resolve()}}async runMiddleware(e){if(this.auth.currentUser===e)return;const t=[];try{for(const i of this.queue)await i(e),i.onAbort&&t.push(i.onAbort)}catch(i){t.reverse();for(const r of t)try{r()}catch{}throw this.auth._errorFactory.create("login-blocked",{originalMessage:i==null?void 0:i.message})}}}/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function es(n,e={}){return se(n,"GET","/v2/passwordPolicy",rt(n,e))}/**
 * @license
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ts=6;class ns{constructor(e){var i;const t=e.customStrengthOptions;this.customStrengthOptions={},this.customStrengthOptions.minPasswordLength=t.minPasswordLength??ts,t.maxPasswordLength&&(this.customStrengthOptions.maxPasswordLength=t.maxPasswordLength),t.containsLowercaseCharacter!==void 0&&(this.customStrengthOptions.containsLowercaseLetter=t.containsLowercaseCharacter),t.containsUppercaseCharacter!==void 0&&(this.customStrengthOptions.containsUppercaseLetter=t.containsUppercaseCharacter),t.containsNumericCharacter!==void 0&&(this.customStrengthOptions.containsNumericCharacter=t.containsNumericCharacter),t.containsNonAlphanumericCharacter!==void 0&&(this.customStrengthOptions.containsNonAlphanumericCharacter=t.containsNonAlphanumericCharacter),this.enforcementState=e.enforcementState,this.enforcementState==="ENFORCEMENT_STATE_UNSPECIFIED"&&(this.enforcementState="OFF"),this.allowedNonAlphanumericCharacters=((i=e.allowedNonAlphanumericCharacters)==null?void 0:i.join(""))??"",this.forceUpgradeOnSignin=e.forceUpgradeOnSignin??!1,this.schemaVersion=e.schemaVersion}validatePassword(e){const t={isValid:!0,passwordPolicy:this};return this.validatePasswordLengthOptions(e,t),this.validatePasswordCharacterOptions(e,t),t.isValid&&(t.isValid=t.meetsMinPasswordLength??!0),t.isValid&&(t.isValid=t.meetsMaxPasswordLength??!0),t.isValid&&(t.isValid=t.containsLowercaseLetter??!0),t.isValid&&(t.isValid=t.containsUppercaseLetter??!0),t.isValid&&(t.isValid=t.containsNumericCharacter??!0),t.isValid&&(t.isValid=t.containsNonAlphanumericCharacter??!0),t}validatePasswordLengthOptions(e,t){const i=this.customStrengthOptions.minPasswordLength,r=this.customStrengthOptions.maxPasswordLength;i&&(t.meetsMinPasswordLength=e.length>=i),r&&(t.meetsMaxPasswordLength=e.length<=r)}validatePasswordCharacterOptions(e,t){this.updatePasswordCharacterOptionsStatuses(t,!1,!1,!1,!1);let i;for(let r=0;r<e.length;r++)i=e.charAt(r),this.updatePasswordCharacterOptionsStatuses(t,i>="a"&&i<="z",i>="A"&&i<="Z",i>="0"&&i<="9",this.allowedNonAlphanumericCharacters.includes(i))}updatePasswordCharacterOptionsStatuses(e,t,i,r,s){this.customStrengthOptions.containsLowercaseLetter&&(e.containsLowercaseLetter||(e.containsLowercaseLetter=t)),this.customStrengthOptions.containsUppercaseLetter&&(e.containsUppercaseLetter||(e.containsUppercaseLetter=i)),this.customStrengthOptions.containsNumericCharacter&&(e.containsNumericCharacter||(e.containsNumericCharacter=r)),this.customStrengthOptions.containsNonAlphanumericCharacter&&(e.containsNonAlphanumericCharacter||(e.containsNonAlphanumericCharacter=s))}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class is{constructor(e,t,i,r){this.app=e,this.heartbeatServiceProvider=t,this.appCheckServiceProvider=i,this.config=r,this.currentUser=null,this.emulatorConfig=null,this.operations=Promise.resolve(),this.authStateSubscription=new Ot(this),this.idTokenSubscription=new Ot(this),this.beforeStateQueue=new Zr(this),this.redirectUser=null,this.isProactiveRefreshEnabled=!1,this.EXPECTED_PASSWORD_POLICY_SCHEMA_VERSION=1,this._canInitEmulator=!0,this._isInitialized=!1,this._deleted=!1,this._initializationPromise=null,this._popupRedirectResolver=null,this._errorFactory=rn,this._agentRecaptchaConfig=null,this._tenantRecaptchaConfigs={},this._projectPasswordPolicy=null,this._tenantPasswordPolicies={},this._resolvePersistenceManagerAvailable=void 0,this.lastNotifiedUid=void 0,this.languageCode=null,this.tenantId=null,this.settings={appVerificationDisabledForTesting:!1},this.frameworks=[],this.name=e.name,this.clientVersion=r.sdkClientVersion,this._persistenceManagerAvailable=new Promise(s=>this._resolvePersistenceManagerAvailable=s)}_initializeWithPersistence(e,t){return t&&(this._popupRedirectResolver=U(t)),this._initializationPromise=this.queue(async()=>{var i,r,s;if(!this._deleted&&(this.persistenceManager=await ee.create(this,e),(i=this._resolvePersistenceManagerAvailable)==null||i.call(this),!this._deleted)){if((r=this._popupRedirectResolver)!=null&&r._shouldInitProactively)try{await this._popupRedirectResolver._initialize(this)}catch{}await this.initializeCurrentUser(t),this.lastNotifiedUid=((s=this.currentUser)==null?void 0:s.uid)||null,!this._deleted&&(this._isInitialized=!0)}}),this._initializationPromise}async _onStorageEvent(){if(this._deleted)return;const e=await this.assertedPersistence.getCurrentUser();if(!(!this.currentUser&&!e)){if(this.currentUser&&e&&this.currentUser.uid===e.uid){this._currentUser._assign(e),await this.currentUser.getIdToken();return}await this._updateCurrentUser(e,!0)}}async initializeCurrentUserFromIdToken(e){try{const t=await Ae(this,{idToken:e}),i=await A._fromGetAccountInfoResponse(this,t,e);await this.directlySetCurrentUser(i)}catch(t){console.warn("FirebaseServerApp could not login user with provided authIdToken: ",t),await this.directlySetCurrentUser(null)}}async initializeCurrentUser(e){var s;if(R(this.app)){const a=this.app.settings.authIdToken;return a?new Promise(c=>{setTimeout(()=>this.initializeCurrentUserFromIdToken(a).then(c,c))}):this.directlySetCurrentUser(null)}const t=await this.assertedPersistence.getCurrentUser();let i=t,r=!1;if(e&&this.config.authDomain){await this.getOrInitRedirectPersistenceManager();const a=(s=this.redirectUser)==null?void 0:s._redirectEventId,c=i==null?void 0:i._redirectEventId,o=await this.tryRedirectSignIn(e);(!a||a===c)&&(o!=null&&o.user)&&(i=o.user,r=!0)}if(!i)return this.directlySetCurrentUser(null);if(!i._redirectEventId){if(r)try{await this.beforeStateQueue.runMiddleware(i)}catch(a){i=t,this._popupRedirectResolver._overrideRedirectResult(this,()=>Promise.reject(a))}return i?this.reloadAndSetCurrentUserOrClear(i):this.directlySetCurrentUser(null)}return f(this._popupRedirectResolver,this,"argument-error"),await this.getOrInitRedirectPersistenceManager(),this.redirectUser&&this.redirectUser._redirectEventId===i._redirectEventId?this.directlySetCurrentUser(i):this.reloadAndSetCurrentUserOrClear(i)}async tryRedirectSignIn(e){let t=null;try{t=await this._popupRedirectResolver._completeRedirectFn(this,e,!0)}catch{await this._setRedirectUser(null)}return t}async reloadAndSetCurrentUserOrClear(e){try{await Ce(e)}catch(t){if((t==null?void 0:t.code)!=="auth/network-request-failed")return this.directlySetCurrentUser(null)}return this.directlySetCurrentUser(e)}useDeviceLanguage(){this.languageCode=xr()}async _delete(){this._deleted=!0}async updateCurrentUser(e){if(R(this.app))return Promise.reject(Y(this));const t=e?G(e):null;return t&&f(t.auth.config.apiKey===this.config.apiKey,this,"invalid-user-token"),this._updateCurrentUser(t&&t._clone(this))}async _updateCurrentUser(e,t=!1){if(!this._deleted)return e&&f(this.tenantId===e.tenantId,this,"tenant-id-mismatch"),t||await this.beforeStateQueue.runMiddleware(e),this.queue(async()=>{await this.directlySetCurrentUser(e),this.notifyAuthListeners()})}async signOut(){return R(this.app)?Promise.reject(Y(this)):(await this.beforeStateQueue.runMiddleware(null),(this.redirectPersistenceManager||this._popupRedirectResolver)&&await this._setRedirectUser(null),this._updateCurrentUser(null,!0))}setPersistence(e){return R(this.app)?Promise.reject(Y(this)):this.queue(async()=>{await this.assertedPersistence.setPersistence(U(e))})}_getRecaptchaConfig(){return this.tenantId==null?this._agentRecaptchaConfig:this._tenantRecaptchaConfigs[this.tenantId]}async validatePassword(e){this._getPasswordPolicyInternal()||await this._updatePasswordPolicy();const t=this._getPasswordPolicyInternal();return t.schemaVersion!==this.EXPECTED_PASSWORD_POLICY_SCHEMA_VERSION?Promise.reject(this._errorFactory.create("unsupported-password-policy-schema-version",{})):t.validatePassword(e)}_getPasswordPolicyInternal(){return this.tenantId===null?this._projectPasswordPolicy:this._tenantPasswordPolicies[this.tenantId]}async _updatePasswordPolicy(){const e=await es(this),t=new ns(e);this.tenantId===null?this._projectPasswordPolicy=t:this._tenantPasswordPolicies[this.tenantId]=t}_getPersistenceType(){return this.assertedPersistence.persistence.type}_getPersistence(){return this.assertedPersistence.persistence}_updateErrorMap(e){this._errorFactory=new he("auth","Firebase",e())}onAuthStateChanged(e,t,i){return this.registerStateListener(this.authStateSubscription,e,t,i)}beforeAuthStateChanged(e,t){return this.beforeStateQueue.pushCallback(e,t)}onIdTokenChanged(e,t,i){return this.registerStateListener(this.idTokenSubscription,e,t,i)}authStateReady(){return new Promise((e,t)=>{if(this.currentUser)e();else{const i=this.onAuthStateChanged(()=>{i(),e()},t)}})}async revokeAccessToken(e){if(this.currentUser){const t=await this.currentUser.getIdToken(),i={providerId:"apple.com",tokenType:"ACCESS_TOKEN",token:e,idToken:t};this.tenantId!=null&&(i.tenantId=this.tenantId),await Yr(this,i)}}toJSON(){var e;return{apiKey:this.config.apiKey,authDomain:this.config.authDomain,appName:this.name,currentUser:(e=this._currentUser)==null?void 0:e.toJSON()}}async _setRedirectUser(e,t){const i=await this.getOrInitRedirectPersistenceManager(t);return e===null?i.removeCurrentUser():i.setCurrentUser(e)}async getOrInitRedirectPersistenceManager(e){if(!this.redirectPersistenceManager){const t=e&&U(e)||this._popupRedirectResolver;f(t,this,"argument-error"),this.redirectPersistenceManager=await ee.create(this,[U(t._redirectPersistence)],"redirectUser"),this.redirectUser=await this.redirectPersistenceManager.getCurrentUser()}return this.redirectPersistenceManager}async _redirectUserForId(e){var t,i;return this._isInitialized&&await this.queue(async()=>{}),((t=this._currentUser)==null?void 0:t._redirectEventId)===e?this._currentUser:((i=this.redirectUser)==null?void 0:i._redirectEventId)===e?this.redirectUser:null}async _persistUserIfCurrent(e){if(e===this.currentUser)return this.queue(async()=>this.directlySetCurrentUser(e))}_notifyListenersIfCurrent(e){e===this.currentUser&&this.notifyAuthListeners()}_key(){return`${this.config.authDomain}:${this.config.apiKey}:${this.name}`}_startProactiveRefresh(){this.isProactiveRefreshEnabled=!0,this.currentUser&&this._currentUser._startProactiveRefresh()}_stopProactiveRefresh(){this.isProactiveRefreshEnabled=!1,this.currentUser&&this._currentUser._stopProactiveRefresh()}get _currentUser(){return this.currentUser}notifyAuthListeners(){var t;if(!this._isInitialized)return;this.idTokenSubscription.next(this.currentUser);const e=((t=this.currentUser)==null?void 0:t.uid)??null;this.lastNotifiedUid!==e&&(this.lastNotifiedUid=e,this.authStateSubscription.next(this.currentUser))}registerStateListener(e,t,i,r){if(this._deleted)return()=>{};const s=typeof t=="function"?t:t.next.bind(t);let a=!1;const c=this._isInitialized?Promise.resolve():this._initializationPromise;if(f(c,this,"internal-error"),c.then(()=>{a||s(this.currentUser)}),typeof t=="function"){const o=e.addObserver(t,i,r);return()=>{a=!0,o()}}else{const o=e.addObserver(t);return()=>{a=!0,o()}}}async directlySetCurrentUser(e){this.currentUser&&this.currentUser!==e&&this._currentUser._stopProactiveRefresh(),e&&this.isProactiveRefreshEnabled&&e._startProactiveRefresh(),this.currentUser=e,e?await this.assertedPersistence.setCurrentUser(e):await this.assertedPersistence.removeCurrentUser()}queue(e){return this.operations=this.operations.then(e,e),this.operations}get assertedPersistence(){return f(this.persistenceManager,this,"internal-error"),this.persistenceManager}_logFramework(e){!e||this.frameworks.includes(e)||(this.frameworks.push(e),this.frameworks.sort(),this.clientVersion=vn(this.config.clientPlatform,this._getFrameworks()))}_getFrameworks(){return this.frameworks}async _getAdditionalHeaders(){var r;const e={"X-Client-Version":this.clientVersion};this.app.options.appId&&(e["X-Firebase-gmpid"]=this.app.options.appId);const t=await((r=this.heartbeatServiceProvider.getImmediate({optional:!0}))==null?void 0:r.getHeartbeatsHeader());t&&(e["X-Firebase-Client"]=t);const i=await this._getAppCheckToken();return i&&(e["X-Firebase-AppCheck"]=i),e}async _getAppCheckToken(){var t;if(R(this.app)&&this.app.settings.appCheckToken)return this.app.settings.appCheckToken;const e=await((t=this.appCheckServiceProvider.getImmediate({optional:!0}))==null?void 0:t.getToken());return e!=null&&e.error&&Dr(`Error while retrieving App Check token: ${e.error}`),e==null?void 0:e.token}}function Ne(n){return G(n)}class Ot{constructor(e){this.auth=e,this.observer=null,this.addObserver=yi(t=>this.observer=t)}get next(){return f(this.observer,this.auth,"internal-error"),this.observer.next.bind(this.observer)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */let ot={async loadJS(){throw new Error("Unable to load external scripts")},recaptchaV2Script:"",recaptchaEnterpriseScript:"",gapiScript:""};function rs(n){ot=n}function ss(n){return ot.loadJS(n)}function as(){return ot.gapiScript}function os(n){return`__${n}${Math.floor(Math.random()*1e6)}`}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function cs(n,e){const t=Qt(n,"auth");if(t.isInitialized()){const r=t.getImmediate(),s=t.getOptions();if(ne(s,e??{}))return r;N(r,"already-initialized")}return t.initialize({options:e})}function ls(n,e){const t=(e==null?void 0:e.persistence)||[],i=(Array.isArray(t)?t:[t]).map(U);e!=null&&e.errorMap&&n._updateErrorMap(e.errorMap),n._initializeWithPersistence(i,e==null?void 0:e.popupRedirectResolver)}function us(n,e,t){const i=Ne(n);f(/^https?:\/\//.test(e),i,"invalid-emulator-scheme");const r=!1,s=yn(e),{host:a,port:c}=ds(e),o=c===null?"":`:${c}`,h={url:`${s}//${a}${o}/`},d=Object.freeze({host:a,port:c,protocol:s.replace(":",""),options:Object.freeze({disableWarnings:r})});if(!i._canInitEmulator){f(i.config.emulator&&i.emulatorConfig,i,"emulator-config-failed"),f(ne(h,i.config.emulator)&&ne(d,i.emulatorConfig),i,"emulator-config-failed");return}i.config.emulator=h,i.emulatorConfig=d,i.settings.appVerificationDisabledForTesting=!0,Ze(a)?wi(`${s}//${a}${o}`):hs()}function yn(n){const e=n.indexOf(":");return e<0?"":n.substr(0,e+1)}function ds(n){const e=yn(n),t=/(\/\/)?([^?#/]+)/.exec(n.substr(e.length));if(!t)return{host:"",port:null};const i=t[2].split("@").pop()||"",r=/^(\[[^\]]+\])(:|$)/.exec(i);if(r){const s=r[1];return{host:s,port:Nt(i.substr(s.length+1))}}else{const[s,a]=i.split(":");return{host:s,port:Nt(a)}}}function Nt(n){if(!n)return null;const e=Number(n);return isNaN(e)?null:e}function hs(){function n(){const e=document.createElement("p"),t=e.style;e.innerText="Running in emulator mode. Do not use with production credentials.",t.position="fixed",t.width="100%",t.backgroundColor="#ffffff",t.border=".1em solid #000000",t.color="#b50000",t.bottom="0px",t.left="0px",t.margin="0px",t.zIndex="10000",t.textAlign="center",e.classList.add("firebase-emulator-warning"),document.body.appendChild(e)}typeof console<"u"&&typeof console.info=="function"&&console.info("WARNING: You are using the Auth Emulator, which is intended for local testing only.  Do not use with production credentials."),typeof window<"u"&&typeof document<"u"&&(document.readyState==="loading"?window.addEventListener("DOMContentLoaded",n):n())}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class In{constructor(e,t){this.providerId=e,this.signInMethod=t}toJSON(){return M("not implemented")}_getIdTokenResponse(e){return M("not implemented")}_linkToIdToken(e,t){return M("not implemented")}_getReauthenticationResolver(e){return M("not implemented")}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function te(n,e){return jr(n,"POST","/v1/accounts:signInWithIdp",rt(n,e))}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const fs="http://localhost";class X extends In{constructor(){super(...arguments),this.pendingToken=null}static _fromParams(e){const t=new X(e.providerId,e.signInMethod);return e.idToken||e.accessToken?(e.idToken&&(t.idToken=e.idToken),e.accessToken&&(t.accessToken=e.accessToken),e.nonce&&!e.pendingToken&&(t.nonce=e.nonce),e.pendingToken&&(t.pendingToken=e.pendingToken)):e.oauthToken&&e.oauthTokenSecret?(t.accessToken=e.oauthToken,t.secret=e.oauthTokenSecret):N("argument-error"),t}toJSON(){return{idToken:this.idToken,accessToken:this.accessToken,secret:this.secret,nonce:this.nonce,pendingToken:this.pendingToken,providerId:this.providerId,signInMethod:this.signInMethod}}static fromJSON(e){const t=typeof e=="string"?JSON.parse(e):e,{providerId:i,signInMethod:r,...s}=t;if(!i||!r)return null;const a=new X(i,r);return a.idToken=s.idToken||void 0,a.accessToken=s.accessToken||void 0,a.secret=s.secret,a.nonce=s.nonce,a.pendingToken=s.pendingToken||null,a}_getIdTokenResponse(e){const t=this.buildRequest();return te(e,t)}_linkToIdToken(e,t){const i=this.buildRequest();return i.idToken=t,te(e,i)}_getReauthenticationResolver(e){const t=this.buildRequest();return t.autoCreate=!1,te(e,t)}buildRequest(){const e={requestUri:fs,returnSecureToken:!0};if(this.pendingToken)e.pendingToken=this.pendingToken;else{const t={};this.idToken&&(t.id_token=this.idToken),this.accessToken&&(t.access_token=this.accessToken),this.secret&&(t.oauth_token_secret=this.secret),t.providerId=this.providerId,this.nonce&&!this.pendingToken&&(t.nonce=this.nonce),e.postBody=fe(t)}return e}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ct{constructor(e){this.providerId=e,this.defaultLanguageCode=null,this.customParameters={}}setDefaultLanguage(e){this.defaultLanguageCode=e}setCustomParameters(e){return this.customParameters=e,this}getCustomParameters(){return this.customParameters}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ge extends ct{constructor(){super(...arguments),this.scopes=[]}addScope(e){return this.scopes.includes(e)||this.scopes.push(e),this}getScopes(){return[...this.scopes]}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class F extends ge{constructor(){super("facebook.com")}static credential(e){return X._fromParams({providerId:F.PROVIDER_ID,signInMethod:F.FACEBOOK_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return F.credentialFromTaggedObject(e)}static credentialFromError(e){return F.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return F.credential(e.oauthAccessToken)}catch{return null}}}F.FACEBOOK_SIGN_IN_METHOD="facebook.com";F.PROVIDER_ID="facebook.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class L extends ge{constructor(){super("google.com"),this.addScope("profile")}static credential(e,t){return X._fromParams({providerId:L.PROVIDER_ID,signInMethod:L.GOOGLE_SIGN_IN_METHOD,idToken:e,accessToken:t})}static credentialFromResult(e){return L.credentialFromTaggedObject(e)}static credentialFromError(e){return L.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthIdToken:t,oauthAccessToken:i}=e;if(!t&&!i)return null;try{return L.credential(t,i)}catch{return null}}}L.GOOGLE_SIGN_IN_METHOD="google.com";L.PROVIDER_ID="google.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class j extends ge{constructor(){super("github.com")}static credential(e){return X._fromParams({providerId:j.PROVIDER_ID,signInMethod:j.GITHUB_SIGN_IN_METHOD,accessToken:e})}static credentialFromResult(e){return j.credentialFromTaggedObject(e)}static credentialFromError(e){return j.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e||!("oauthAccessToken"in e)||!e.oauthAccessToken)return null;try{return j.credential(e.oauthAccessToken)}catch{return null}}}j.GITHUB_SIGN_IN_METHOD="github.com";j.PROVIDER_ID="github.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class $ extends ge{constructor(){super("twitter.com")}static credential(e,t){return X._fromParams({providerId:$.PROVIDER_ID,signInMethod:$.TWITTER_SIGN_IN_METHOD,oauthToken:e,oauthTokenSecret:t})}static credentialFromResult(e){return $.credentialFromTaggedObject(e)}static credentialFromError(e){return $.credentialFromTaggedObject(e.customData||{})}static credentialFromTaggedObject({_tokenResponse:e}){if(!e)return null;const{oauthAccessToken:t,oauthTokenSecret:i}=e;if(!t||!i)return null;try{return $.credential(t,i)}catch{return null}}}$.TWITTER_SIGN_IN_METHOD="twitter.com";$.PROVIDER_ID="twitter.com";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class re{constructor(e){this.user=e.user,this.providerId=e.providerId,this._tokenResponse=e._tokenResponse,this.operationType=e.operationType}static async _fromIdTokenResponse(e,t,i,r=!1){const s=await A._fromIdTokenResponse(e,i,r),a=Dt(i);return new re({user:s,providerId:a,_tokenResponse:i,operationType:t})}static async _forOperation(e,t,i){await e._updateTokensIfNecessary(i,!0);const r=Dt(i);return new re({user:e,providerId:r,_tokenResponse:i,operationType:t})}}function Dt(n){return n.providerId?n.providerId:"phoneNumber"in n?"phone":null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Pe extends z{constructor(e,t,i,r){super(t.code,t.message),this.operationType=i,this.user=r,Object.setPrototypeOf(this,Pe.prototype),this.customData={appName:e.name,tenantId:e.tenantId??void 0,_serverResponse:t.customData._serverResponse,operationType:i}}static _fromErrorAndOperation(e,t,i,r){return new Pe(e,t,i,r)}}function bn(n,e,t,i){return(e==="reauthenticate"?t._getReauthenticationResolver(n):t._getIdTokenResponse(n)).catch(s=>{throw s.code==="auth/multi-factor-auth-required"?Pe._fromErrorAndOperation(n,s,e,i):s})}async function ps(n,e,t=!1){const i=await de(n,e._linkToIdToken(n.auth,await n.getIdToken()),t);return re._forOperation(n,"link",i)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function ms(n,e,t=!1){const{auth:i}=n;if(R(i.app))return Promise.reject(Y(i));const r="reauthenticate";try{const s=await de(n,bn(i,r,e,n),t);f(s.idToken,i,"internal-error");const a=st(s.idToken);f(a,i,"internal-error");const{sub:c}=a;return f(n.uid===c,i,"user-mismatch"),re._forOperation(n,r,s)}catch(s){throw(s==null?void 0:s.code)==="auth/user-not-found"&&N(i,"user-mismatch"),s}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function gs(n,e,t=!1){if(R(n.app))return Promise.reject(Y(n));const i="signIn",r=await bn(n,i,e),s=await re._fromIdTokenResponse(n,i,r);return t||await n._updateCurrentUser(s.user),s}function _s(n,e,t,i){return G(n).onIdTokenChanged(e,t,i)}function vs(n,e,t){return G(n).beforeAuthStateChanged(e,t)}function ys(n,e,t,i){return G(n).onAuthStateChanged(e,t,i)}function Is(n){return G(n).signOut()}const Re="__sak";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class wn{constructor(e,t){this.storageRetriever=e,this.type=t}_isAvailable(){try{return this.storage?(this.storage.setItem(Re,"1"),this.storage.removeItem(Re),Promise.resolve(!0)):Promise.resolve(!1)}catch{return Promise.resolve(!1)}}_set(e,t){return this.storage.setItem(e,JSON.stringify(t)),Promise.resolve()}_get(e){const t=this.storage.getItem(e);return Promise.resolve(t?JSON.parse(t):null)}_remove(e){return this.storage.removeItem(e),Promise.resolve()}get storage(){return this.storageRetriever()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const bs=1e3,ws=10;class kn extends wn{constructor(){super(()=>window.localStorage,"LOCAL"),this.boundEventHandler=(e,t)=>this.onStorageEvent(e,t),this.listeners={},this.localCache={},this.pollTimer=null,this.fallbackToPolling=_n(),this._shouldAllowMigration=!0}forAllChangedKeys(e){for(const t of Object.keys(this.listeners)){const i=this.storage.getItem(t),r=this.localCache[t];i!==r&&e(t,r,i)}}onStorageEvent(e,t=!1){if(!e.key){this.forAllChangedKeys((a,c,o)=>{this.notifyListeners(a,o)});return}const i=e.key;t?this.detachListener():this.stopPolling();const r=()=>{const a=this.storage.getItem(i);!t&&this.localCache[i]===a||this.notifyListeners(i,a)},s=this.storage.getItem(i);Qr()&&s!==e.newValue&&e.newValue!==e.oldValue?setTimeout(r,ws):r()}notifyListeners(e,t){this.localCache[e]=t;const i=this.listeners[e];if(i)for(const r of Array.from(i))r(t&&JSON.parse(t))}startPolling(){this.stopPolling(),this.pollTimer=setInterval(()=>{this.forAllChangedKeys((e,t,i)=>{this.onStorageEvent(new StorageEvent("storage",{key:e,oldValue:t,newValue:i}),!0)})},bs)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}attachListener(){window.addEventListener("storage",this.boundEventHandler)}detachListener(){window.removeEventListener("storage",this.boundEventHandler)}_addListener(e,t){Object.keys(this.listeners).length===0&&(this.fallbackToPolling?this.startPolling():this.attachListener()),this.listeners[e]||(this.listeners[e]=new Set,this.localCache[e]=this.storage.getItem(e)),this.listeners[e].add(t)}_removeListener(e,t){this.listeners[e]&&(this.listeners[e].delete(t),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&(this.detachListener(),this.stopPolling())}async _set(e,t){await super._set(e,t),this.localCache[e]=JSON.stringify(t)}async _get(e){const t=await super._get(e);return this.localCache[e]=JSON.stringify(t),t}async _remove(e){await super._remove(e),delete this.localCache[e]}}kn.type="LOCAL";const ks=kn;/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class En extends wn{constructor(){super(()=>window.sessionStorage,"SESSION")}_addListener(e,t){}_removeListener(e,t){}}En.type="SESSION";const Tn=En;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Es(n){return Promise.all(n.map(async e=>{try{return{fulfilled:!0,value:await e}}catch(t){return{fulfilled:!1,reason:t}}}))}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class De{constructor(e){this.eventTarget=e,this.handlersMap={},this.boundEventHandler=this.handleEvent.bind(this)}static _getInstance(e){const t=this.receivers.find(r=>r.isListeningto(e));if(t)return t;const i=new De(e);return this.receivers.push(i),i}isListeningto(e){return this.eventTarget===e}async handleEvent(e){const t=e,{eventId:i,eventType:r,data:s}=t.data,a=this.handlersMap[r];if(!(a!=null&&a.size))return;t.ports[0].postMessage({status:"ack",eventId:i,eventType:r});const c=Array.from(a).map(async h=>h(t.origin,s)),o=await Es(c);t.ports[0].postMessage({status:"done",eventId:i,eventType:r,response:o})}_subscribe(e,t){Object.keys(this.handlersMap).length===0&&this.eventTarget.addEventListener("message",this.boundEventHandler),this.handlersMap[e]||(this.handlersMap[e]=new Set),this.handlersMap[e].add(t)}_unsubscribe(e,t){this.handlersMap[e]&&t&&this.handlersMap[e].delete(t),(!t||this.handlersMap[e].size===0)&&delete this.handlersMap[e],Object.keys(this.handlersMap).length===0&&this.eventTarget.removeEventListener("message",this.boundEventHandler)}}De.receivers=[];/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function lt(n="",e=10){let t="";for(let i=0;i<e;i++)t+=Math.floor(Math.random()*10);return n+t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Ts{constructor(e){this.target=e,this.handlers=new Set}removeMessageHandler(e){e.messageChannel&&(e.messageChannel.port1.removeEventListener("message",e.onMessage),e.messageChannel.port1.close()),this.handlers.delete(e)}async _send(e,t,i=50){const r=typeof MessageChannel<"u"?new MessageChannel:null;if(!r)throw new Error("connection_unavailable");let s,a;return new Promise((c,o)=>{const h=lt("",20);r.port1.start();const d=setTimeout(()=>{o(new Error("unsupported_event"))},i);a={messageChannel:r,onMessage(g){const v=g;if(v.data.eventId===h)switch(v.data.status){case"ack":clearTimeout(d),s=setTimeout(()=>{o(new Error("timeout"))},3e3);break;case"done":clearTimeout(s),c(v.data.response);break;default:clearTimeout(d),clearTimeout(s),o(new Error("invalid_response"));break}}},this.handlers.add(a),r.port1.addEventListener("message",a.onMessage),this.target.postMessage({eventType:e,eventId:h,data:t},[r.port2])}).finally(()=>{a&&this.removeMessageHandler(a)})}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function O(){return window}function Ss(n){O().location.href=n}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Sn(){return typeof O().WorkerGlobalScope<"u"&&typeof O().importScripts=="function"}async function As(){if(!(navigator!=null&&navigator.serviceWorker))return null;try{return(await navigator.serviceWorker.ready).active}catch{return null}}function Cs(){var n;return((n=navigator==null?void 0:navigator.serviceWorker)==null?void 0:n.controller)||null}function Ps(){return Sn()?self:null}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const An="firebaseLocalStorageDb",Rs=1,Oe="firebaseLocalStorage",Cn="fbase_key";class _e{constructor(e){this.request=e}toPromise(){return new Promise((e,t)=>{this.request.addEventListener("success",()=>{e(this.request.result)}),this.request.addEventListener("error",()=>{t(this.request.error)})})}}function Le(n,e){return n.transaction([Oe],e?"readwrite":"readonly").objectStore(Oe)}function Os(){const n=indexedDB.deleteDatabase(An);return new _e(n).toPromise()}function Pn(){const n=indexedDB.open(An,Rs);return new Promise((e,t)=>{n.addEventListener("error",()=>{t(n.error)}),n.addEventListener("upgradeneeded",()=>{const i=n.result;try{i.createObjectStore(Oe,{keyPath:Cn})}catch(r){t(r)}}),n.addEventListener("success",async()=>{const i=n.result;i.objectStoreNames.contains(Oe)?e(i):(i.close(),await Os(),e(await Pn()))})})}async function Lt(n,e,t){const i=Le(n,!0).put({[Cn]:e,value:t});return new _e(i).toPromise()}async function Ns(n,e){const t=Le(n,!1).get(e),i=await new _e(t).toPromise();return i===void 0?null:i.value}function Mt(n,e){const t=Le(n,!0).delete(e);return new _e(t).toPromise()}const Ds=800,Ls=3;class Rn{constructor(){this.type="LOCAL",this.dbPromise=null,this._shouldAllowMigration=!0,this.listeners={},this.localCache={},this.pollTimer=null,this.pendingWrites=0,this.receiver=null,this.sender=null,this.serviceWorkerReceiverAvailable=!1,this.activeServiceWorker=null,this._workerInitializationPromise=this.initializeServiceWorkerMessaging().then(()=>{},()=>{})}async _openDb(){return this.dbPromise?this.dbPromise:(this.dbPromise=Pn(),this.dbPromise.catch(()=>{this.dbPromise=null}),this.dbPromise)}async _withRetries(e){let t=0;for(;;)try{const i=await this._openDb();return await e(i)}catch(i){if(t++>Ls)throw i;this.dbPromise&&((await this.dbPromise).close(),this.dbPromise=null)}}async initializeServiceWorkerMessaging(){return Sn()?this.initializeReceiver():this.initializeSender()}async initializeReceiver(){this.receiver=De._getInstance(Ps()),this.receiver._subscribe("keyChanged",async(e,t)=>({keyProcessed:(await this._poll()).includes(t.key)})),this.receiver._subscribe("ping",async(e,t)=>["keyChanged"])}async initializeSender(){var t,i;if(this.activeServiceWorker=await As(),!this.activeServiceWorker)return;this.sender=new Ts(this.activeServiceWorker);const e=await this.sender._send("ping",{},800);e&&(t=e[0])!=null&&t.fulfilled&&(i=e[0])!=null&&i.value.includes("keyChanged")&&(this.serviceWorkerReceiverAvailable=!0)}async notifyServiceWorker(e){if(!(!this.sender||!this.activeServiceWorker||Cs()!==this.activeServiceWorker))try{await this.sender._send("keyChanged",{key:e},this.serviceWorkerReceiverAvailable?800:50)}catch{}}async _isAvailable(){try{return indexedDB?(await this._withRetries(async e=>{await Lt(e,Re,"1"),await Mt(e,Re)}),!0):!1}catch{}return!1}async _withPendingWrite(e){this.pendingWrites++;try{await e()}finally{this.pendingWrites--}}async _set(e,t){return this._withPendingWrite(async()=>(await this._withRetries(i=>Lt(i,e,t)),this.localCache[e]=t,this.notifyServiceWorker(e)))}async _get(e){const t=await this._withRetries(i=>Ns(i,e));return this.localCache[e]=t,t}async _remove(e){return this._withPendingWrite(async()=>(await this._withRetries(t=>Mt(t,e)),delete this.localCache[e],this.notifyServiceWorker(e)))}async _poll(){const e=await this._withRetries(r=>{const s=Le(r,!1).getAll();return new _e(s).toPromise()});if(!e)return[];if(this.pendingWrites!==0)return[];const t=[],i=new Set;if(e.length!==0)for(const{fbase_key:r,value:s}of e)i.add(r),JSON.stringify(this.localCache[r])!==JSON.stringify(s)&&(this.notifyListeners(r,s),t.push(r));for(const r of Object.keys(this.localCache))this.localCache[r]&&!i.has(r)&&(this.notifyListeners(r,null),t.push(r));return t}notifyListeners(e,t){this.localCache[e]=t;const i=this.listeners[e];if(i)for(const r of Array.from(i))r(t)}startPolling(){this.stopPolling(),this.pollTimer=setInterval(async()=>this._poll(),Ds)}stopPolling(){this.pollTimer&&(clearInterval(this.pollTimer),this.pollTimer=null)}_addListener(e,t){Object.keys(this.listeners).length===0&&this.startPolling(),this.listeners[e]||(this.listeners[e]=new Set,this._get(e)),this.listeners[e].add(t)}_removeListener(e,t){this.listeners[e]&&(this.listeners[e].delete(t),this.listeners[e].size===0&&delete this.listeners[e]),Object.keys(this.listeners).length===0&&this.stopPolling()}}Rn.type="LOCAL";const Ms=Rn;new me(3e4,6e4);/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function On(n,e){return e?U(e):(f(n._popupRedirectResolver,n,"argument-error"),n._popupRedirectResolver)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ut extends In{constructor(e){super("custom","custom"),this.params=e}_getIdTokenResponse(e){return te(e,this._buildIdpRequest())}_linkToIdToken(e,t){return te(e,this._buildIdpRequest(t))}_getReauthenticationResolver(e){return te(e,this._buildIdpRequest())}_buildIdpRequest(e){const t={requestUri:this.params.requestUri,sessionId:this.params.sessionId,postBody:this.params.postBody,tenantId:this.params.tenantId,pendingToken:this.params.pendingToken,returnSecureToken:!0,returnIdpCredential:!0};return e&&(t.idToken=e),t}}function Us(n){return gs(n.auth,new ut(n),n.bypassAuthState)}function xs(n){const{auth:e,user:t}=n;return f(t,e,"internal-error"),ms(t,new ut(n),n.bypassAuthState)}async function Vs(n){const{auth:e,user:t}=n;return f(t,e,"internal-error"),ps(t,new ut(n),n.bypassAuthState)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Nn{constructor(e,t,i,r,s=!1){this.auth=e,this.resolver=i,this.user=r,this.bypassAuthState=s,this.pendingPromise=null,this.eventManager=null,this.filter=Array.isArray(t)?t:[t]}execute(){return new Promise(async(e,t)=>{this.pendingPromise={resolve:e,reject:t};try{this.eventManager=await this.resolver._initialize(this.auth),await this.onExecution(),this.eventManager.registerConsumer(this)}catch(i){this.reject(i)}})}async onAuthEvent(e){const{urlResponse:t,sessionId:i,postBody:r,tenantId:s,error:a,type:c}=e;if(a){this.reject(a);return}const o={auth:this.auth,requestUri:t,sessionId:i,tenantId:s||void 0,postBody:r||void 0,user:this.user,bypassAuthState:this.bypassAuthState};try{this.resolve(await this.getIdpTask(c)(o))}catch(h){this.reject(h)}}onError(e){this.reject(e)}getIdpTask(e){switch(e){case"signInViaPopup":case"signInViaRedirect":return Us;case"linkViaPopup":case"linkViaRedirect":return Vs;case"reauthViaPopup":case"reauthViaRedirect":return xs;default:N(this.auth,"internal-error")}}resolve(e){V(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.resolve(e),this.unregisterAndCleanUp()}reject(e){V(this.pendingPromise,"Pending promise was never set"),this.pendingPromise.reject(e),this.unregisterAndCleanUp()}unregisterAndCleanUp(){this.eventManager&&this.eventManager.unregisterConsumer(this),this.pendingPromise=null,this.cleanUp()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Bs=new me(2e3,1e4);async function Fs(n,e,t){if(R(n.app))return Promise.reject(C(n,"operation-not-supported-in-this-environment"));const i=Ne(n);Lr(n,e,ct);const r=On(i,t);return new J(i,"signInViaPopup",e,r).executeNotNull()}class J extends Nn{constructor(e,t,i,r,s){super(e,t,r,s),this.provider=i,this.authWindow=null,this.pollId=null,J.currentPopupAction&&J.currentPopupAction.cancel(),J.currentPopupAction=this}async executeNotNull(){const e=await this.execute();return f(e,this.auth,"internal-error"),e}async onExecution(){V(this.filter.length===1,"Popup operations only handle one event");const e=lt();this.authWindow=await this.resolver._openPopup(this.auth,this.provider,this.filter[0],e),this.authWindow.associatedEvent=e,this.resolver._originValidation(this.auth).catch(t=>{this.reject(t)}),this.resolver._isIframeWebStorageSupported(this.auth,t=>{t||this.reject(C(this.auth,"web-storage-unsupported"))}),this.pollUserCancellation()}get eventId(){var e;return((e=this.authWindow)==null?void 0:e.associatedEvent)||null}cancel(){this.reject(C(this.auth,"cancelled-popup-request"))}cleanUp(){this.authWindow&&this.authWindow.close(),this.pollId&&window.clearTimeout(this.pollId),this.authWindow=null,this.pollId=null,J.currentPopupAction=null}pollUserCancellation(){const e=()=>{var t,i;if((i=(t=this.authWindow)==null?void 0:t.window)!=null&&i.closed){this.pollId=window.setTimeout(()=>{this.pollId=null,this.reject(C(this.auth,"popup-closed-by-user"))},8e3);return}this.pollId=window.setTimeout(e,Bs.get())};e()}}J.currentPopupAction=null;/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const js="pendingRedirect",ke=new Map;class $s extends Nn{constructor(e,t,i=!1){super(e,["signInViaRedirect","linkViaRedirect","reauthViaRedirect","unknown"],t,void 0,i),this.eventId=null}async execute(){let e=ke.get(this.auth._key());if(!e){try{const i=await Hs(this.resolver,this.auth)?await super.execute():null;e=()=>Promise.resolve(i)}catch(t){e=()=>Promise.reject(t)}ke.set(this.auth._key(),e)}return this.bypassAuthState||ke.set(this.auth._key(),()=>Promise.resolve(null)),e()}async onAuthEvent(e){if(e.type==="signInViaRedirect")return super.onAuthEvent(e);if(e.type==="unknown"){this.resolve(null);return}if(e.eventId){const t=await this.auth._redirectUserForId(e.eventId);if(t)return this.user=t,super.onAuthEvent(e);this.resolve(null)}}async onExecution(){}cleanUp(){}}async function Hs(n,e){const t=Gs(e),i=zs(n);if(!await i._isAvailable())return!1;const r=await i._get(t)==="true";return await i._remove(t),r}function Ws(n,e){ke.set(n._key(),e)}function zs(n){return U(n._redirectPersistence)}function Gs(n){return we(js,n.config.apiKey,n.name)}async function Ks(n,e,t=!1){if(R(n.app))return Promise.reject(Y(n));const i=Ne(n),r=On(i,e),a=await new $s(i,r,t).execute();return a&&!t&&(delete a.user._redirectEventId,await i._persistUserIfCurrent(a.user),await i._setRedirectUser(null,e)),a}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const qs=600*1e3;class Js{constructor(e){this.auth=e,this.cachedEventUids=new Set,this.consumers=new Set,this.queuedRedirectEvent=null,this.hasHandledPotentialRedirect=!1,this.lastProcessedEventTime=Date.now()}registerConsumer(e){this.consumers.add(e),this.queuedRedirectEvent&&this.isEventForConsumer(this.queuedRedirectEvent,e)&&(this.sendToConsumer(this.queuedRedirectEvent,e),this.saveEventToCache(this.queuedRedirectEvent),this.queuedRedirectEvent=null)}unregisterConsumer(e){this.consumers.delete(e)}onEvent(e){if(this.hasEventBeenHandled(e))return!1;let t=!1;return this.consumers.forEach(i=>{this.isEventForConsumer(e,i)&&(t=!0,this.sendToConsumer(e,i),this.saveEventToCache(e))}),this.hasHandledPotentialRedirect||!Ys(e)||(this.hasHandledPotentialRedirect=!0,t||(this.queuedRedirectEvent=e,t=!0)),t}sendToConsumer(e,t){var i;if(e.error&&!Dn(e)){const r=((i=e.error.code)==null?void 0:i.split("auth/")[1])||"internal-error";t.onError(C(this.auth,r))}else t.onAuthEvent(e)}isEventForConsumer(e,t){const i=t.eventId===null||!!e.eventId&&e.eventId===t.eventId;return t.filter.includes(e.type)&&i}hasEventBeenHandled(e){return Date.now()-this.lastProcessedEventTime>=qs&&this.cachedEventUids.clear(),this.cachedEventUids.has(Ut(e))}saveEventToCache(e){this.cachedEventUids.add(Ut(e)),this.lastProcessedEventTime=Date.now()}}function Ut(n){return[n.type,n.eventId,n.sessionId,n.tenantId].filter(e=>e).join("-")}function Dn({type:n,error:e}){return n==="unknown"&&(e==null?void 0:e.code)==="auth/no-auth-event"}function Ys(n){switch(n.type){case"signInViaRedirect":case"linkViaRedirect":case"reauthViaRedirect":return!0;case"unknown":return Dn(n);default:return!1}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Xs(n,e={}){return se(n,"GET","/v1/projects",e)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Qs=/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,Zs=/^https?/;async function ea(n){if(n.config.emulator)return;const{authorizedDomains:e}=await Xs(n);for(const t of e)try{if(ta(t))return}catch{}N(n,"unauthorized-domain")}function ta(n){const e=Ye(),{protocol:t,hostname:i}=new URL(e);if(n.startsWith("chrome-extension://")){const a=new URL(n);return a.hostname===""&&i===""?t==="chrome-extension:"&&n.replace("chrome-extension://","")===e.replace("chrome-extension://",""):t==="chrome-extension:"&&a.hostname===i}if(!Zs.test(t))return!1;if(Qs.test(n))return i===n;const r=n.replace(/\./g,"\\.");return new RegExp("^(.+\\."+r+"|"+r+")$","i").test(i)}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const na=new me(3e4,6e4);function xt(){const n=O().___jsl;if(n!=null&&n.H){for(const e of Object.keys(n.H))if(n.H[e].r=n.H[e].r||[],n.H[e].L=n.H[e].L||[],n.H[e].r=[...n.H[e].L],n.CP)for(let t=0;t<n.CP.length;t++)n.CP[t]=null}}function ia(n){return new Promise((e,t)=>{var r,s,a;function i(){xt(),gapi.load("gapi.iframes",{callback:()=>{e(gapi.iframes.getContext())},ontimeout:()=>{xt(),t(C(n,"network-request-failed"))},timeout:na.get()})}if((s=(r=O().gapi)==null?void 0:r.iframes)!=null&&s.Iframe)e(gapi.iframes.getContext());else if((a=O().gapi)!=null&&a.load)i();else{const c=os("iframefcb");return O()[c]=()=>{gapi.load?i():t(C(n,"network-request-failed"))},ss(`${as()}?onload=${c}`).catch(o=>t(o))}}).catch(e=>{throw Ee=null,e})}let Ee=null;function ra(n){return Ee=Ee||ia(n),Ee}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const sa=new me(5e3,15e3),aa="__/auth/iframe",oa="emulator/auth/iframe",ca={style:{position:"absolute",top:"-100px",width:"1px",height:"1px"},"aria-hidden":"true",tabindex:"-1"},la=new Map([["identitytoolkit.googleapis.com","p"],["staging-identitytoolkit.sandbox.googleapis.com","s"],["test-identitytoolkit.sandbox.googleapis.com","t"]]);function ua(n){const e=n.config;f(e.authDomain,n,"auth-domain-config-required");const t=e.emulator?it(e,oa):`https://${n.config.authDomain}/${aa}`,i={apiKey:e.apiKey,appName:n.name,v:pe},r=la.get(n.config.apiHost);r&&(i.eid=r);const s=n._getFrameworks();return s.length&&(i.fw=s.join(",")),`${t}?${fe(i).slice(1)}`}async function da(n){const e=await ra(n),t=O().gapi;return f(t,n,"internal-error"),e.open({where:document.body,url:ua(n),messageHandlersFilter:t.iframes.CROSS_ORIGIN_IFRAMES_FILTER,attributes:ca,dontclear:!0},i=>new Promise(async(r,s)=>{await i.restyle({setHideOnLeave:!1});const a=C(n,"network-request-failed"),c=O().setTimeout(()=>{s(a)},sa.get());function o(){O().clearTimeout(c),r(i)}i.ping(o).then(o,()=>{s(a)})}))}/**
 * @license
 * Copyright 2020 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ha={location:"yes",resizable:"yes",statusbar:"yes",toolbar:"no"},fa=500,pa=600,ma="_blank",ga="http://localhost";class Vt{constructor(e){this.window=e,this.associatedEvent=null}close(){if(this.window)try{this.window.close()}catch{}}}function _a(n,e,t,i=fa,r=pa){const s=Math.max((window.screen.availHeight-r)/2,0).toString(),a=Math.max((window.screen.availWidth-i)/2,0).toString();let c="";const o={...ha,width:i.toString(),height:r.toString(),top:s,left:a},h=b().toLowerCase();t&&(c=hn(h)?ma:t),un(h)&&(e=e||ga,o.scrollbars="yes");const d=Object.entries(o).reduce((v,[T,k])=>`${v}${T}=${k},`,"");if(Xr(h)&&c!=="_self")return va(e||"",c),new Vt(null);const g=window.open(e||"",c,d);f(g,n,"popup-blocked");try{g.focus()}catch{}return new Vt(g)}function va(n,e){const t=document.createElement("a");t.href=n,t.target=e;const i=document.createEvent("MouseEvent");i.initMouseEvent("click",!0,!0,window,1,0,0,0,0,!1,!1,!1,!1,1,null),t.dispatchEvent(i)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ya="__/auth/handler",Ia="emulator/auth/handler",ba=encodeURIComponent("fac");async function Bt(n,e,t,i,r,s){f(n.config.authDomain,n,"auth-domain-config-required"),f(n.config.apiKey,n,"invalid-api-key");const a={apiKey:n.config.apiKey,appName:n.name,authType:t,redirectUrl:i,v:pe,eventId:r};if(e instanceof ct){e.setDefaultLanguage(n.languageCode),a.providerId=e.providerId||"",vi(e.getCustomParameters())||(a.customParameters=JSON.stringify(e.getCustomParameters()));for(const[d,g]of Object.entries({}))a[d]=g}if(e instanceof ge){const d=e.getScopes().filter(g=>g!=="");d.length>0&&(a.scopes=d.join(","))}n.tenantId&&(a.tid=n.tenantId);const c=a;for(const d of Object.keys(c))c[d]===void 0&&delete c[d];const o=await n._getAppCheckToken(),h=o?`#${ba}=${encodeURIComponent(o)}`:"";return`${wa(n)}?${fe(c).slice(1)}${h}`}function wa({config:n}){return n.emulator?it(n,Ia):`https://${n.authDomain}/${ya}`}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const We="webStorageSupport";class ka{constructor(){this.eventManagers={},this.iframes={},this.originValidationPromises={},this._redirectPersistence=Tn,this._completeRedirectFn=Ks,this._overrideRedirectResult=Ws}async _openPopup(e,t,i,r){var a;V((a=this.eventManagers[e._key()])==null?void 0:a.manager,"_initialize() not called before _openPopup()");const s=await Bt(e,t,i,Ye(),r);return _a(e,s,lt())}async _openRedirect(e,t,i,r){await this._originValidation(e);const s=await Bt(e,t,i,Ye(),r);return Ss(s),new Promise(()=>{})}_initialize(e){const t=e._key();if(this.eventManagers[t]){const{manager:r,promise:s}=this.eventManagers[t];return r?Promise.resolve(r):(V(s,"If manager is not set, promise should be"),s)}const i=this.initAndGetManager(e);return this.eventManagers[t]={promise:i},i.catch(()=>{delete this.eventManagers[t]}),i}async initAndGetManager(e){const t=await da(e),i=new Js(e);return t.register("authEvent",r=>(f(r==null?void 0:r.authEvent,e,"invalid-auth-event"),{status:i.onEvent(r.authEvent)?"ACK":"ERROR"}),gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER),this.eventManagers[e._key()]={manager:i},this.iframes[e._key()]=t,i}_isIframeWebStorageSupported(e,t){this.iframes[e._key()].send(We,{type:We},r=>{var a;const s=(a=r==null?void 0:r[0])==null?void 0:a[We];s!==void 0&&t(!!s),N(e,"internal-error")},gapi.iframes.CROSS_ORIGIN_IFRAMES_FILTER)}_originValidation(e){const t=e._key();return this.originValidationPromises[t]||(this.originValidationPromises[t]=ea(e)),this.originValidationPromises[t]}get _shouldInitProactively(){return _n()||dn()||at()}}const Ea=ka;var Ft="@firebase/auth",jt="1.13.3";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Ta{constructor(e){this.auth=e,this.internalListeners=new Map}getUid(){var e;return this.assertAuthConfigured(),((e=this.auth.currentUser)==null?void 0:e.uid)||null}async getToken(e){return this.assertAuthConfigured(),await this.auth._initializationPromise,this.auth.currentUser?{accessToken:await this.auth.currentUser.getIdToken(e)}:null}addAuthTokenListener(e){if(this.assertAuthConfigured(),this.internalListeners.has(e))return;const t=this.auth.onIdTokenChanged(i=>{e((i==null?void 0:i.stsTokenManager.accessToken)||null)});this.internalListeners.set(e,t),this.updateProactiveRefresh()}removeAuthTokenListener(e){this.assertAuthConfigured();const t=this.internalListeners.get(e);t&&(this.internalListeners.delete(e),t(),this.updateProactiveRefresh())}assertAuthConfigured(){f(this.auth._initializationPromise,"dependent-sdk-initialized-before-auth")}updateProactiveRefresh(){this.internalListeners.size>0?this.auth._startProactiveRefresh():this.auth._stopProactiveRefresh()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Sa(n){switch(n){case"Node":return"node";case"ReactNative":return"rn";case"Worker":return"webworker";case"Cordova":return"cordova";case"WebExtension":return"web-extension";default:return}}function Aa(n){le(new ie("auth",(e,{options:t})=>{const i=e.getProvider("app").getImmediate(),r=e.getProvider("heartbeat"),s=e.getProvider("app-check-internal"),{apiKey:a,authDomain:c}=i.options;f(a&&!a.includes(":"),"invalid-api-key",{appName:i.name});const o={apiKey:a,authDomain:c,clientPlatform:n,apiHost:"identitytoolkit.googleapis.com",tokenApiHost:"securetoken.googleapis.com",apiScheme:"https",sdkClientVersion:vn(n)},h=new is(i,r,s,o);return ls(h,t),h},"PUBLIC").setInstantiationMode("EXPLICIT").setInstanceCreatedCallback((e,t,i)=>{e.getProvider("auth-internal").initialize()})),le(new ie("auth-internal",e=>{const t=Ne(e.getProvider("auth").getImmediate());return(i=>new Ta(i))(t)},"PRIVATE").setInstantiationMode("EXPLICIT")),Q(Ft,jt,Sa(n)),Q(Ft,jt,"esm2020")}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ca=300,Pa=qt("authIdTokenMaxAge")||Ca;let $t=null;const Ra=n=>async e=>{const t=e&&await e.getIdTokenResult(),i=t&&(new Date().getTime()-Date.parse(t.issuedAtTime))/1e3;if(i&&i>Pa)return;const r=t==null?void 0:t.token;$t!==r&&($t=r,await fetch(n,{method:r?"POST":"DELETE",headers:r?{Authorization:`Bearer ${r}`}:{}}))};function Oa(n=br()){const e=Qt(n,"auth");if(e.isInitialized())return e.getImmediate();const t=cs(n,{popupRedirectResolver:Ea,persistence:[Ms,ks,Tn]}),i=qt("authTokenSyncURL");if(i&&typeof isSecureContext=="boolean"&&isSecureContext){const s=new URL(i,location.origin);if(location.origin===s.origin){const a=Ra(s.toString());vs(t,a,()=>a(t.currentUser)),_s(t,c=>a(c))}}const r=ai("auth");return r&&us(t,`http://${r}`),t}function Na(){var n;return((n=document.getElementsByTagName("head"))==null?void 0:n[0])??document}rs({loadJS(n){return new Promise((e,t)=>{const i=document.createElement("script");i.setAttribute("src",n),i.onload=e,i.onerror=r=>{const s=C("internal-error");s.customData=r,t(s)},i.type="text/javascript",i.charset="UTF-8",Na().appendChild(i)})},gapiScript:"https://apis.google.com/js/api.js",recaptchaV2Script:"https://www.google.com/recaptcha/api.js",recaptchaEnterpriseScript:"https://www.google.com/recaptcha/enterprise.js?render="});Aa("Browser");var Da="firebase",La="12.15.0";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */Q(Da,La,"app");const Ma={apiKey:"AIzaSyDls91HFIf1_E0X6JJ1kuE7V8I6z8tW68A",authDomain:"manajemen-risiko-98127.firebaseapp.com",projectId:"manajemen-risiko-98127",storageBucket:"manajemen-risiko-98127.firebasestorage.app",messagingSenderId:"465214376439",appId:"1:465214376439:web:73469cafb36d37c2b886f2",measurementId:"G-FLYRRYCXEX"},Ua=Zt(Ma),dt=Oa(Ua),xa=new L;function Va(){return Fs(dt,xa)}function Ba(){return Is(dt)}const Fa={class:"lapor-container"},ja={key:1,class:"auth-gate-card"},$a={class:"hero-brand"},Ha={class:"auth-box"},Wa={key:2,class:"lapor-main"},za={class:"user-bar"},Ga={class:"user-meta"},Ka={class:"user-avatar"},qa=["src"],Ja={key:1,class:"pi pi-user"},Ya={class:"user-name"},Xa={class:"user-email"},Qa={class:"user-actions"},Za={class:"main-form-card"},eo={class:"form-grid"},to={class:"field-item"},no={class:"field-item"},io={class:"field-item"},ro={class:"field-item"},so={class:"field-item"},ao={class:"field-item"},oo={class:"field-item full-width"},co={class:"field-item full-width"},lo={class:"form-actions"},uo={class:"my-reports-card"},ho={class:"reports-header"},fo={key:0,class:"loading-state"},po={key:1,class:"empty-reports"},mo={key:2,class:"reports-list"},go={class:"report-top"},_o={class:"report-opd-badge"},vo={class:"report-meta-grid"},yo={class:"report-content-body"},Io={class:"content-row"},bo={class:"content-val"},wo={class:"content-row"},ko={class:"content-val"},Eo={key:0,class:"report-feedback"},To={__name:"LaporKejadian",setup(n){const e=Fn(),t=D(null),i=D(""),r=D(!0),s=D(!1),a=D(!1),c=D([]),o=D([]),h=D(!1),d=D({tahun:new Date().getFullYear(),opd_id:null,no_hp:"",nama_lengkap:"",waktu_kejadian:null,tempat:"",uraian_kejadian:"",pemicu:""});function g(p){if(!p)return"";if(p instanceof Date){const l=Vn=>String(Vn).padStart(2,"0"),K=p.getFullYear(),m=l(p.getMonth()+1),Mn=l(p.getDate()),Un=l(p.getHours()),xn=l(p.getMinutes());return`${K}-${m}-${Mn} ${Un}:${xn}`}return String(p)}const v=[{label:"2025",value:2025},{label:"2026",value:2026},{label:"2027",value:2027}];async function T(){try{const p=await xe.get("/lapor-kejadian/opd-list");c.value=p.data||[]}catch{c.value=[]}}async function k(){if(i.value){h.value=!0;try{const p=await xe.get("/lapor-kejadian/my",{headers:{Authorization:`Bearer ${i.value}`}});o.value=p.data||[]}catch{o.value=[]}finally{h.value=!1}}}jn(()=>{T(),ys(dt,async p=>{if(t.value=p,p)try{i.value=await p.getIdToken(),d.value.nama_lengkap||(d.value.nama_lengkap=p.displayName||""),await k()}catch{i.value=""}else i.value="",o.value=[];r.value=!1})});async function ve(){s.value=!0;try{const p=await Va();t.value=p.user,i.value=await p.user.getIdToken(),d.value.nama_lengkap=p.user.displayName||"",e.add({severity:"success",summary:"Login Berhasil",detail:`Selamat datang, ${p.user.displayName||p.user.email}`,life:3e3}),await k()}catch(p){e.add({severity:"error",summary:"Gagal Login",detail:p.message||"Tidak dapat menyelesaikan login Firebase",life:4e3})}finally{s.value=!1}}async function ye(){try{await Ba(),t.value=null,i.value="",o.value=[],e.add({severity:"info",summary:"Logout Berhasil",detail:"Sesi telah ditutup",life:3e3})}catch{e.add({severity:"error",summary:"Error",detail:"Gagal logout",life:3e3})}}async function ae(){var p,l;if(!d.value.tahun){e.add({severity:"warn",summary:"Validasi",detail:"Tahun anggaran wajib diisi",life:3e3});return}if(!d.value.opd_id){e.add({severity:"warn",summary:"Validasi",detail:"Pilih Organisasi Perangkat Daerah",life:3e3});return}if(!d.value.nama_lengkap.trim()){e.add({severity:"warn",summary:"Validasi",detail:"Nama lengkap pelapor wajib diisi",life:3e3});return}if(!d.value.no_hp.trim()){e.add({severity:"warn",summary:"Validasi",detail:"Nomor HP pelapor wajib diisi",life:3e3});return}if(!d.value.waktu_kejadian){e.add({severity:"warn",summary:"Validasi",detail:"Waktu kejadian wajib dipilih",life:3e3});return}if(!d.value.tempat.trim()){e.add({severity:"warn",summary:"Validasi",detail:"Tempat kejadian wajib diisi",life:3e3});return}if(!d.value.uraian_kejadian.trim()){e.add({severity:"warn",summary:"Validasi",detail:"Uraian kejadian wajib diisi",life:3e3});return}if(!d.value.pemicu.trim()){e.add({severity:"warn",summary:"Validasi",detail:"Pemicu kejadian wajib diisi",life:3e3});return}a.value=!0;try{t.value&&(i.value=await t.value.getIdToken(!0));const K={tahun:Number(d.value.tahun),opd_id:Number(d.value.opd_id),no_hp:d.value.no_hp.trim(),nama_lengkap:d.value.nama_lengkap.trim(),waktu_kejadian:g(d.value.waktu_kejadian),tempat:d.value.tempat.trim(),uraian_kejadian:d.value.uraian_kejadian.trim(),pemicu:d.value.pemicu.trim()},m=await xe.post("/lapor-kejadian",K,{headers:{Authorization:`Bearer ${i.value}`}});e.add({severity:"success",summary:"Laporan Terkirim",detail:"Laporan kejadian berhasil disimpan dan akan divalidasi oleh pengelola risiko.",life:5e3}),d.value.uraian_kejadian="",d.value.pemicu="",d.value.tempat="",d.value.waktu_kejadian=null,await k()}catch(K){e.add({severity:"error",summary:"Gagal Menyimpan",detail:((l=(p=K.response)==null?void 0:p.data)==null?void 0:l.detail)||"Terjadi kesalahan saat menyimpan laporan kejadian",life:4e3})}finally{a.value=!1}}function Me(p){return p==="disetujui"?"success":p==="ditolak"?"danger":"warn"}function Ln(p){return p==="disetujui"?"Disetujui":p==="ditolak"?"Ditolak":"Menunggu Validasi"}return(p,l)=>{const K=Kn("tooltip");return E(),S("div",Fa,[r.value?(E(),$n(Jn,{key:0,label:"Memeriksa autentikasi Firebase…"})):t.value?(E(),S("div",Wa,[u("div",za,[u("div",Ga,[u("div",Ka,[t.value.photoURL?(E(),S("img",{key:0,src:t.value.photoURL,alt:"Profile"},null,8,qa)):(E(),S("i",Ja))]),u("div",null,[u("div",Ya,P(t.value.displayName||"Pegawai OPD"),1),u("div",Xa,P(t.value.email),1)])]),u("div",Qa,[I(y(oe),{label:"Logout",icon:"pi pi-sign-out",severity:"secondary",outlined:"",size:"small",class:"btn-logout",onClick:ye})])]),u("div",Za,[l[22]||(l[22]=ht('<div class="form-header" data-v-bbfca122><div class="form-header-left" data-v-bbfca122><div class="form-icon" data-v-bbfca122><i class="pi pi-file-edit" data-v-bbfca122></i></div><div data-v-bbfca122><h2 class="form-title" data-v-bbfca122>Formulir Lapor Kejadian</h2><p class="form-subtitle" data-v-bbfca122> Isi data rincian kejadian risiko dengan lengkap dan jelas. Semua laporan akan masuk ke menu Approval Kejadian. </p></div></div></div>',1)),u("form",{onSubmit:Hn(ae,["prevent"]),class:"form-body"},[u("div",eo,[u("div",to,[l[14]||(l[14]=u("label",{for:"tahun",class:"field-label"},[w("Tahun Anggaran "),u("span",{class:"req"},"*")],-1)),I(y(ft),{id:"tahun",modelValue:d.value.tahun,"onUpdate:modelValue":l[0]||(l[0]=m=>d.value.tahun=m),options:v,optionLabel:"label",optionValue:"value",placeholder:"Pilih Tahun",class:"w-full"},null,8,["modelValue"])]),u("div",no,[l[15]||(l[15]=u("label",{for:"opd",class:"field-label"},[w("Organisasi Perangkat Daerah (OPD) "),u("span",{class:"req"},"*")],-1)),I(y(ft),{id:"opd",modelValue:d.value.opd_id,"onUpdate:modelValue":l[1]||(l[1]=m=>d.value.opd_id=m),options:c.value,optionLabel:"nama",optionValue:"id",filter:"",placeholder:"Pilih OPD Tempat Kejadian",class:"w-full"},null,8,["modelValue","options"])]),u("div",io,[l[16]||(l[16]=u("label",{for:"nama_lengkap",class:"field-label"},[w("Nama Lengkap Pelapor "),u("span",{class:"req"},"*")],-1)),I(y(Ue),{id:"nama_lengkap",modelValue:d.value.nama_lengkap,"onUpdate:modelValue":l[2]||(l[2]=m=>d.value.nama_lengkap=m),placeholder:"Masukkan nama lengkap Anda",class:"w-full"},null,8,["modelValue"])]),u("div",ro,[l[17]||(l[17]=u("label",{for:"no_hp",class:"field-label"},[w("No. HP / WhatsApp "),u("span",{class:"req"},"*")],-1)),I(y(Ue),{id:"no_hp",modelValue:d.value.no_hp,"onUpdate:modelValue":l[3]||(l[3]=m=>d.value.no_hp=m),placeholder:"Contoh: 081234567890",class:"w-full"},null,8,["modelValue"])]),u("div",so,[l[18]||(l[18]=u("label",{for:"waktu_kejadian",class:"field-label"},[w("Waktu Kejadian "),u("span",{class:"req"},"*")],-1)),I(y(Yn),{id:"waktu_kejadian",modelValue:d.value.waktu_kejadian,"onUpdate:modelValue":l[4]||(l[4]=m=>d.value.waktu_kejadian=m),dateFormat:"dd-mm-yy",showTime:"",hourFormat:"24",showIcon:"",showButtonBar:"",fluid:"",placeholder:"Pilih tanggal & waktu kejadian"},null,8,["modelValue"])]),u("div",ao,[l[19]||(l[19]=u("label",{for:"tempat",class:"field-label"},[w("Tempat Kejadian "),u("span",{class:"req"},"*")],-1)),I(y(Ue),{id:"tempat",modelValue:d.value.tempat,"onUpdate:modelValue":l[5]||(l[5]=m=>d.value.tempat=m),placeholder:"Contoh: Ruang Pelayanan / Lab / Lokasi Proyek",class:"w-full"},null,8,["modelValue"])]),u("div",oo,[l[20]||(l[20]=u("label",{for:"uraian",class:"field-label"},[w("Uraian Kejadian "),u("span",{class:"req"},"*")],-1)),I(y(pt),{id:"uraian",modelValue:d.value.uraian_kejadian,"onUpdate:modelValue":l[6]||(l[6]=m=>d.value.uraian_kejadian=m),rows:"4",placeholder:"Jelaskan secara kronologis kejadian risiko yang terjadi, kendala, atau dampak kerugian yang ditimbulkan...",class:"w-full"},null,8,["modelValue"])]),u("div",co,[l[21]||(l[21]=u("label",{for:"pemicu",class:"field-label"},[w("Pemicu Kejadian "),u("span",{class:"req"},"*")],-1)),I(y(pt),{id:"pemicu",modelValue:d.value.pemicu,"onUpdate:modelValue":l[7]||(l[7]=m=>d.value.pemicu=m),rows:"3",placeholder:"Jelaskan faktor pemicu atau penyebab terjadinya kejadian risiko tersebut (misal: cuaca ekstrem, sistem server down, kelalaian prosedur, dll.)...",class:"w-full"},null,8,["modelValue"])])]),u("div",lo,[I(y(oe),{label:"Simpan Laporan Kejadian",icon:"pi pi-check",size:"large",type:"submit",class:"btn-submit",loading:a.value},null,8,["loading"]),I(y(oe),{label:"Logout",icon:"pi pi-sign-out",severity:"secondary",outlined:"",size:"large",class:"btn-logout-bottom",onClick:ye})])],32)]),u("div",uo,[u("div",ho,[l[23]||(l[23]=u("span",{class:"reports-title"},[u("i",{class:"pi pi-history card-icon"}),w(" Riwayat Laporan Saya ")],-1)),Wn(I(y(oe),{icon:"pi pi-refresh",size:"small",text:"",severity:"secondary",onClick:k},null,512),[[K,"Segarkan Riwayat"]])]),h.value?(E(),S("div",fo,[...l[24]||(l[24]=[u("i",{class:"pi pi-spin pi-spinner"},null,-1),w(" Memuat riwayat laporan… ",-1)])])):o.value.length?(E(),S("div",mo,[(E(!0),S(zn,null,Gn(o.value,m=>(E(),S("div",{key:m.id,class:"report-box"},[u("div",go,[u("div",_o,[l[26]||(l[26]=u("i",{class:"pi pi-building"},null,-1)),w(" "+P(m.nama_opd)+" (Tahun "+P(m.tahun)+") ",1)]),I(y(mt),{value:Ln(m.status),severity:Me(m.status)},null,8,["value","severity"])]),u("div",vo,[u("div",null,[l[27]||(l[27]=u("strong",null,"Waktu:",-1)),w(" "+P(m.waktu_kejadian),1)]),u("div",null,[l[28]||(l[28]=u("strong",null,"Tempat:",-1)),w(" "+P(m.tempat),1)]),u("div",null,[l[29]||(l[29]=u("strong",null,"Dilaporkan:",-1)),w(" "+P(y(Xn)(m.created_at)),1)])]),u("div",yo,[u("div",Io,[l[30]||(l[30]=u("span",{class:"content-lbl"},"Uraian Kejadian:",-1)),u("p",bo,P(m.uraian_kejadian),1)]),u("div",wo,[l[31]||(l[31]=u("span",{class:"content-lbl"},"Pemicu:",-1)),u("p",ko,P(m.pemicu),1)])]),m.catatan_validasi?(E(),S("div",Eo,[l[33]||(l[33]=u("i",{class:"pi pi-comment feedback-icon"},null,-1)),u("div",null,[l[32]||(l[32]=u("strong",null,"Catatan Validasi Pengelola:",-1)),u("p",null,P(m.catatan_validasi),1)])])):qn("",!0)]))),128))])):(E(),S("div",po,[...l[25]||(l[25]=[u("i",{class:"pi pi-inbox empty-icon"},null,-1),u("p",null,"Belum ada laporan kejadian yang Anda kirimkan.",-1)])]))])])):(E(),S("div",ja,[u("div",$a,[l[8]||(l[8]=u("div",{class:"brand-icon-wrap"},[u("i",{class:"pi pi-shield"})],-1)),I(y(mt),{value:"LAYANAN PUBLIK OPD",severity:"info",class:"badge-tag"}),l[9]||(l[9]=u("h1",{class:"hero-title"},"Lapor Kejadian Risiko",-1)),l[10]||(l[10]=u("p",{class:"hero-desc"}," Saluran pelaporan resmi bagi seluruh pegawai di lingkungan Pemerintah Kota Tegal untuk mencatat potensi insiden, hambatan pelaksanaan tugas, dan kejadian risiko secara cepat, akurat, dan terverifikasi. ",-1))]),u("div",Ha,[l[11]||(l[11]=u("p",{class:"auth-box-msg"}," Silakan masuk menggunakan akun Google Anda untuk memulai pelaporan kejadian risiko: ",-1)),I(y(oe),{label:"Masuk dengan Google Akun",icon:"pi pi-google",size:"large",class:"btn-google-login",loading:s.value,onClick:ve},null,8,["loading"]),l[12]||(l[12]=u("div",{class:"auth-guarantee"},[u("i",{class:"pi pi-lock lock-icon"}),u("span",null,"Autentikasi aman melalui Google Akun")],-1))]),l[13]||(l[13]=ht('<div class="features-preview" data-v-bbfca122><div class="feat-card" data-v-bbfca122><i class="pi pi-send feat-icon" data-v-bbfca122></i><h3 data-v-bbfca122>Pelaporan Cepat</h3><p data-v-bbfca122>Catat kronologi kejadian, waktu, tempat, dan pemicu risiko langsung dari perangkat Anda.</p></div><div class="feat-card" data-v-bbfca122><i class="pi pi-check-circle feat-icon" data-v-bbfca122></i><h3 data-v-bbfca122>Approval Pengelola</h3><p data-v-bbfca122>Laporan langsung masuk ke dashboard Approval Kejadian untuk divalidasi oleh tim Manajemen Risiko OPD.</p></div><div class="feat-card" data-v-bbfca122><i class="pi pi-history feat-icon" data-v-bbfca122></i><h3 data-v-bbfca122>Pantau Status</h3><p data-v-bbfca122>Lihat perkembangan validasi laporan Anda secara transparan kapan saja.</p></div></div>',1))]))])}}},No=Bn(To,[["__scopeId","data-v-bbfca122"]]);export{No as default};
