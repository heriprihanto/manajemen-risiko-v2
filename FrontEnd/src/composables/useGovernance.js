import { ref } from 'vue'
import api from '@/api'
export function useGovernance(reload) {
  const visible = ref(false), title = ref(''), fields = ref([]), initial = ref({}), busy = ref(false), error = ref('')
  let action
  function open(label, inputs, callback, defaults = {}) {
    title.value = label; fields.value = inputs; action = callback; initial.value = defaults; error.value = ''; visible.value = true
  }
  async function submit(data) {
    busy.value = true; error.value = ''
    try { await action(data); visible.value = false; await reload() }
    catch (e) { error.value = message(e) }
    finally { busy.value = false }
  }
  function decision(path, obj, label = 'Keputusan') {
    open(label, [
      { key: 'keputusan', label: 'Keputusan', type: 'select', options: [{value:'disetujui',label:'Setujui'}, {value:'ditolak',label:'Tolak'}] },
      { key: 'catatan', label: 'Dasar keputusan / catatan', type: 'textarea' },
    ], data => api.post(`/tata-kelola/${path}/${obj.id}/keputusan`, data))
  }
  return { visible, title, fields, initial, busy, error, open, submit, decision }
}
export function message(e) {
  const detail = e.response?.data?.detail
  return Array.isArray(detail) ? detail.map(d => `${d.loc?.slice(1).join('.')}: ${d.msg}`).join('; ') : detail || e.message || 'Permintaan gagal'
}
export const field = (key, label, type = 'text', extra = {}) => ({ key, label, type, ...extra })
