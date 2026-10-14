<script setup>
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
const props = defineProps({ visible: Boolean, title: String, fields: Array, initial: Object, busy: Boolean, error: String })
const emit = defineEmits(['update:visible', 'submit'])
const values = ref({})
watch(() => props.visible, (v) => {
  if (v) values.value = Object.fromEntries((props.fields || []).map(f => [f.key, props.initial?.[f.key] ?? f.default ?? (f.type === 'multi' || f.type === 'scores' ? [] : '')]))
})
function submit() {
  const data = { ...values.value }
  for (const f of props.fields || []) {
    if (f.type === 'lines') data[f.key] = String(data[f.key]).split('\n').map(s => s.trim()).filter(Boolean)
    if (f.type === 'number') data[f.key] = Number(data[f.key])
    if (f.optional && data[f.key] === '') data[f.key] = null
  }
  emit('submit', data)
}
</script>
<template>
  <Dialog :visible="visible" @update:visible="emit('update:visible', $event)" :header="title" modal :closable="!busy" :style="{ width: '680px', maxWidth: '95vw' }">
    <form class="gov-form" @submit.prevent="submit">
      <p v-if="error" role="alert" class="error">{{ error }}</p>
      <div v-for="f in fields" :key="f.key" class="field">
        <label :for="'gov-' + f.key">{{ f.label }}{{ f.optional ? ' (opsional)' : '' }}</label>
        <small v-if="f.help">{{ f.help }}</small>
        <textarea v-if="['textarea', 'lines'].includes(f.type)" :id="'gov-' + f.key" v-model="values[f.key]" :required="!f.optional" rows="4" maxlength="10000" />
        <select v-else-if="f.type === 'select'" :id="'gov-' + f.key" v-model="values[f.key]" :required="!f.optional">
          <option disabled value="">Pilih…</option><option v-for="o in f.options" :key="o.value ?? o" :value="o.value ?? o">{{ o.label ?? o }}</option>
        </select>
        <div v-else-if="f.type === 'multi' || f.type === 'scores'" class="choices" :class="{ scores: f.type === 'scores' }">
          <label v-for="o in (f.type === 'scores' ? Array.from({ length: 25 }, (_, i) => i + 1) : f.options)" :key="o.value ?? o">
            <input type="checkbox" v-model="values[f.key]" :value="o.value ?? o" />{{ o.label ?? o }}
          </label>
        </div>
        <input v-else :id="'gov-' + f.key" v-model="values[f.key]" :type="f.type || 'text'" :required="!f.optional" :min="f.min" :max="f.max" maxlength="10000" />
      </div>
      <div class="buttons"><Button label="Batal" severity="secondary" :disabled="busy" @click="emit('update:visible', false)" /><Button type="submit" label="Simpan" :loading="busy" /></div>
    </form>
  </Dialog>
</template>
<style scoped>
.gov-form{display:grid;gap:18px}.field{display:grid;gap:6px}.field>label{font-weight:600}small{color:#475569}input:not([type=checkbox]),textarea,select{padding:10px;border:1px solid #94a3b8;border-radius:6px;width:100%;font:inherit;background:white;color:#0f172a}.choices{display:flex;flex-wrap:wrap;gap:12px}.choices label{display:flex;align-items:center;gap:6px}.scores{display:grid;grid-template-columns:repeat(5,1fr)}.buttons{display:flex;justify-content:flex-end;gap:10px}.error{color:#b91c1c;background:#fef2f2;padding:12px}
</style>
