/**
 * Utilitas format tanggal & waktu Waktu Indonesia Barat (WIB / Asia/Jakarta, UTC+7).
 */

/**
 * Normalisasi string ISO naive menjadi string ber-offset WIB (+07:00).
 */
export function normalizeIsoToWib(iso) {
  if (!iso) return null
  const s = String(iso).trim()
  if (!/[zZ]|[+-]\d{2}:?\d{2}$/.test(s)) {
    return s.replace(' ', 'T') + '+07:00'
  }
  return s
}

/**
 * Format datetime ke standar bahasa Indonesia dengan zona waktu Asia/Jakarta (WIB).
 * Contoh output: "12 Jan 2027, 16.10 WIB".
 */
export function formatDateTime(
  val,
  { withSuffix = true } = {},
) {
  if (!val) return '—'
  try {
    const norm = typeof val === 'string' ? normalizeIsoToWib(val) : val
    const d = new Date(norm)
    if (isNaN(d.getTime())) return String(val)
    const formatted = d.toLocaleString('id-ID', {
      timeZone: 'Asia/Jakarta',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })
    return withSuffix ? `${formatted} WIB` : formatted
  } catch {
    return String(val)
  }
}

/**
 * Mengurai string 'YYYY-MM-DD' menjadi objek Date lokal tanpa pergeseran zona waktu UTC.
 */
export function parseDateOnly(str) {
  if (!str) return null
  if (str instanceof Date) return str
  const s = String(str).trim().slice(0, 10)
  const parts = s.split('-')
  if (parts.length === 3 && parts[0].length === 4) {
    const y = parseInt(parts[0], 10)
    const m = parseInt(parts[1], 10) - 1
    const d = parseInt(parts[2], 10)
    return new Date(y, m, d)
  }
  return new Date(str)
}

/**
 * Mengonversi objek Date lokal menjadi string 'YYYY-MM-DD'.
 * Mencegah bug toISOString() yang mengurangi tanggal 1 hari pada zona waktu positif (UTC+7).
 */
export function toDateOnlyString(date) {
  if (!date) return null
  const d = date instanceof Date ? date : new Date(date)
  if (isNaN(d.getTime())) return null
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

/**
 * Memformat string 'YYYY-MM-DD', rentang tanggal, atau Date ke format tanggal Indonesia: "12 Jan 2027".
 */
export function formatDate(val) {
  if (!val) return '—'
  const str = String(val).trim()
  if (str.includes(' s.d. ')) {
    const [start, end] = str.split(' s.d. ')
    return `${formatDate(start)} s.d. ${formatDate(end)}`
  }
  if (str.includes(' - ') && /^\d{4}-\d{2}-\d{2}\s*-\s*\d{4}-\d{2}-\d{2}$/.test(str)) {
    const [start, end] = str.split(' - ')
    return `${formatDate(start)} - ${formatDate(end)}`
  }
  const d = parseDateOnly(val)
  if (!d || isNaN(d.getTime())) return String(val)
  return d.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

