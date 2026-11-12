<template>
  <main style="max-width: 40rem; margin: 15vh auto; padding: 2rem">
    <h1>{{ $route.query.blocked ? 'Akses tidak diizinkan' : 'Sesi belum dapat diperiksa' }}</h1>
    <p>{{ $route.query.blocked ? 'Akun Anda tidak memiliki akses atau sedang dinonaktifkan. Hubungi administrator e-Monev.' : 'Layanan autentikasi belum tersedia. Silakan coba kembali beberapa saat lagi.' }}</p>
    <a :href="base">Coba kembali</a>
  </main>
</template>
<script setup>
const base = import.meta.env.BASE_URL
</script>
