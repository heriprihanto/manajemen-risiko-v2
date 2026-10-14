export const statusPengendalian = [
  { value: 'sudah_ada', label: 'Sudah ada kegiatan pengendalian' },
  { value: 'tidak_ada', label: 'Tidak ada Kegiatan Pengendalian' },
]
export const responRisiko = [
  { value: 'kurangi_kemungkinan', label: 'Mengurangi kemungkinan terjadinya Risiko' },
  { value: 'kurangi_dampak', label: 'Mengurangi dampak Risiko' },
  { value: 'bagi', label: 'Membagi Risiko' },
  { value: 'hindari', label: 'Menghindari Risiko' },
  { value: 'terima', label: 'Menerima Risiko' },
]
export const statusLabel = value => statusPengendalian.find(o => o.value === value)?.label || 'Belum diisi'
export const responLabel = value => responRisiko.find(o => o.value === value)?.label || 'Belum diisi'
