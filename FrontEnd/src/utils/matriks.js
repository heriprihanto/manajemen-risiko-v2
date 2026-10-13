/**
 * Utilitas Matriks Analisis Risiko 5x5
 * Sesuai standar BPKP / ISO 31000
 */

export const MATRIKS_SKALA = {
  // Kemungkinan 5 (Hampir pasti terjadi)
  '5-1': 11, '5-2': 15, '5-3': 18, '5-4': 23, '5-5': 25,
  // Kemungkinan 4 (Sering terjadi)
  '4-1': 6,  '4-2': 12, '4-3': 16, '4-4': 19, '4-5': 24,
  // Kemungkinan 3 (Kadang terjadi)
  '3-1': 4,  '3-2': 8,  '3-3': 14, '3-4': 17, '3-5': 22,
  // Kemungkinan 2 (Jarang terjadi)
  '2-1': 2,  '2-2': 7,  '2-3': 10, '2-4': 13, '2-5': 21,
  // Kemungkinan 1 (Hampir tidak terjadi)
  '1-1': 1,  '1-2': 3,  '1-3': 5,  '1-4': 9,  '1-5': 20,
}

export const LEVEL_COLORS = {
  'Sangat Rendah (1)': '#16a34a', // Hijau Tua
  'Sangat Rendah': '#16a34a',
  'Rendah (2)': '#65a30d',        // Hijau Muda / Lime
  'Rendah': '#65a30d',
  'Sedang (3)': '#eab308',        // Kuning
  'Sedang': '#eab308',
  'Tinggi (4)': '#ea580c',        // Oranye
  'Tinggi': '#ea580c',
  'Sangat Tinggi (5)': '#dc2626', // Merah
  'Sangat Tinggi': '#dc2626',
}

export const LEVEL_BG_COLORS = {
  'Sangat Rendah (1)': '#dcfce7',
  'Sangat Rendah': '#dcfce7',
  'Rendah (2)': '#ecfccb',
  'Rendah': '#ecfccb',
  'Sedang (3)': '#fef9c3',
  'Sedang': '#fef9c3',
  'Tinggi (4)': '#ffedd5',
  'Tinggi': '#ffedd5',
  'Sangat Tinggi (5)': '#fee2e2',
  'Sangat Tinggi': '#fee2e2',
}

// Warna sel heatmap yang lebih solid sesuai gambar referensi
export const CELL_SOLID_COLORS = {
  'Sangat Rendah (1)': '#10b981', // Hijau Tua / Emerald
  'Rendah (2)': '#84cc16',        // Hijau Muda
  'Sedang (3)': '#facc15',        // Kuning
  'Tinggi (4)': '#f97316',        // Oranye
  'Sangat Tinggi (5)': '#ef4444', // Merah
}

export const DAMPAK_OPTIONS = [
  { value: 1, label: '1 Tidak signifikan', short: 'Tdk Signifikan' },
  { value: 2, label: '2 Minor', short: 'Minor' },
  { value: 3, label: '3 Moderat', short: 'Moderat' },
  { value: 4, label: '4 Signifikan', short: 'Signifikan' },
  { value: 5, label: '5 Sangat Signifikan', short: 'Sgt Signifikan' },
]

export const KEMUNGKINAN_OPTIONS = [
  { value: 5, label: '5 Hampir pasti terjadi', short: 'Hampir Pasti' },
  { value: 4, label: '4 Sering terjadi', short: 'Sering' },
  { value: 3, label: '3 Kadang terjadi', short: 'Kadang' },
  { value: 2, label: '2 Jarang terjadi', short: 'Jarang' },
  { value: 1, label: '1 Hampir tidak terjadi', short: 'Hampir Tidak' },
]

export function getMatrixScore(k, d) {
  if (!k || !d) return null
  return MATRIKS_SKALA[`${k}-${d}`] ?? null
}

export function getLevelByScore(score) {
  if (score === null || score === undefined) return null
  if (score >= 20) return 'Sangat Tinggi (5)'
  if (score >= 16) return 'Tinggi (4)'
  if (score >= 11) return 'Sedang (3)'
  if (score >= 6) return 'Rendah (2)'
  return 'Sangat Rendah (1)'
}

export function getMatrixLevel(k, d) {
  const score = getMatrixScore(k, d)
  return getLevelByScore(score)
}

export function getMatrixColor(k, d) {
  const lvl = getMatrixLevel(k, d)
  return LEVEL_COLORS[lvl] || '#9ca3af'
}

export function getMatrixSolidColor(k, d) {
  const lvl = getMatrixLevel(k, d)
  return CELL_SOLID_COLORS[lvl] || '#9ca3af'
}

/**
 * Mengembalikan styling batas toleransi risiko (garis ungu pada gambar referensi).
 * Memisahkan risiko diterima (<= 10) dengan risiko ditangani (>= 11).
 */
export function getToleranceBorderStyles(k, d) {
  const styles = {}
  const purpleBorder = '3.5px solid #7c3aed'

  // Garis vertikal di kanan (4,1), (3,2), (2,3), (1,4)
  if ((k === 4 && d === 1) || (k === 3 && d === 2) || (k === 2 && d === 3) || (k === 1 && d === 4)) {
    styles.borderRight = purpleBorder
  }

  // Garis horizontal di bawah (4,2), (3,3), (2,4)
  if ((k === 4 && d === 2) || (k === 3 && d === 3) || (k === 2 && d === 4)) {
    styles.borderBottom = purpleBorder
  }

  return styles
}
