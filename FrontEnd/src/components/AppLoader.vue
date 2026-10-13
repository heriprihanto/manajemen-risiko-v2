<script setup>
// Loader tunggal untuk seluruh keadaan "sedang memuat" di aplikasi.
defineProps({
  label: { type: String, default: 'Memuat…' },
  size: { type: [Number, String], default: 34 },
  // `inline` = loader kecil sebaris dengan teks (mis. di dalam toolbar/kartu);
  // default = blok, dipakai saat isi halaman belum bisa ditampilkan.
  inline: Boolean,
})
</script>

<template>
  <div class="app-loader no-print" :class="{ inline }" role="status" aria-live="polite">
    <span
      class="ring"
      :style="{ width: `${size}px`, height: `${size}px` }"
      aria-hidden="true"
    />
    <span v-if="label" class="label">{{ label }}</span>
  </div>
</template>

<style scoped>
.app-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 44px 12px;
  color: var(--text-muted);
  font-size: 0.86rem;
}
.app-loader.inline {
  flex-direction: row;
  justify-content: flex-start;
  gap: 8px;
  padding: 10px 0;
}
.ring {
  display: block;
  border-radius: 50%;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-right-color: #8b5cf6;
  animation: app-loader-spin 0.75s linear infinite;
}
.label {
  animation: app-loader-fade 1.4s ease-in-out infinite;
}
@keyframes app-loader-spin {
  to { transform: rotate(360deg); }
}
@keyframes app-loader-fade {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.55; }
}
/* Hormati preferensi kurangi animasi: diperlambat, bukan dihentikan — spinner
   yang diam justru terbaca sebagai macet. */
@media (prefers-reduced-motion: reduce) {
  .ring { animation-duration: 2.2s; }
  .label { animation: none; }
}
</style>
