# Login bersama e-Monev dan Manajemen Risiko

Implementasi ini menggunakan JWT di cookie `__Host-emonev_sso` dengan `Secure`,
`HttpOnly`, `SameSite=Lax`, `Path=/`, tanpa atribut Domain. e-Monev menerbitkan
JWT khusus browser dengan audience `emonev-sso` dan mencatat hash token pada
`sso_browser_sessions`. Token tidak disimpan pada localStorage saat mode SSO.

Manajemen Risiko memeriksa sesi melalui backend e-Monev pada setiap request
terproteksi (satu pemeriksaan untuk dependency dalam request yang sama).
Tidak ada kunci JWT e-Monev di Manajemen Risiko dan tidak ada fallback ke JWT
lokal ketika SSO aktif. Timeout atau respons penerbit yang tidak valid menghasilkan
503; sesi hilang/kedaluwarsa/dicabut menghasilkan 401; akun diblokir menghasilkan
403. Role dan OPD diambil dari akun terbaru, bukan klaim role yang lama.

## Pengembangan lokal di http://localhost:5173/

Gunakan konfigurasi berikut pada `BackEnd/.env` selama pengembangan lokal:

```dotenv
ENVIRONMENT=local
SSO_ENABLED=false
```

Restart backend setelah mengubah `.env`, lalu muat ulang halaman browser.
Frontend membaca mode autentikasi dari `/api/auth/config` saat pertama dibuka;
respons lokal harus berisi `sso_enabled: false`. Pada mode ini pengguna masuk
melalui halaman login internal MR. Autentikasi dan pembatasan OPD tetap berlaku.
Tidak ada akun otomatis atau bypass login.

Cookie login dari `monevrkpd.tegalkota.go.id` tidak dikirim oleh browser ke
`localhost`. Karena itu mengaktifkan SSO dengan login produksi pada frontend
localhost tidak dapat menyelesaikan alur login bersama. Uji SSO dilakukan pada
host HTTPS yang melayani kedua aplikasi, sesuai konfigurasi deployment di bawah.
`ENVIRONMENT=local` saja tidak menonaktifkan SSO; pilih `SSO_ENABLED=false` secara
eksplisit. Nilai `SSO_LOGIN_URL` produksi boleh tetap tersimpan karena tidak
digunakan ketika SSO dinonaktifkan.

## Persiapan deployment

1. Backup konfigurasi dan database e-Monev. Deploy backend e-Monev baru dengan
   `SSO_ENABLED=false` terlebih dahulu.
2. Jalankan `Backend/migrations/20261112_sso_browser_sessions.sql` pada database
   e-Monev menggunakan prosedur migrasi yang biasa digunakan. Tidak ada migrasi
   tambahan pada database Manajemen Risiko.
3. Tambahkan konfigurasi berikut pada `.env` backend e-Monev:

   ```dotenv
   SSO_ENABLED=true
   SSO_COOKIE_NAME=__Host-emonev_sso
   SSO_PUBLIC_ORIGIN=https://monevrkpd.tegalkota.go.id
   ```

4. Tambahkan konfigurasi berikut pada `BackEnd/.env` Manajemen Risiko:

   ```dotenv
   SSO_ENABLED=true
   SSO_COOKIE_NAME=__Host-emonev_sso
   SSO_SESSION_URL=http://127.0.0.1:9999/api/v1/auth/session
   SSO_PUBLIC_ORIGIN=https://monevrkpd.tegalkota.go.id
   SSO_LOGIN_URL=https://monevrkpd.tegalkota.go.id/emonev2027/admin/login
   ```

   Sesuaikan port/alamat backend e-Monev yang sebenarnya. Default 9999 mengikuti
   entry point source e-Monev; ini belum memverifikasi port server produksi.
   Alamat HTTP hanya boleh dipakai melalui loopback/jaringan privat yang
   dipercaya; untuk lintas server gunakan HTTPS yang tervalidasi. Jangan arahkan
   URL ini ke endpoint redirect. Tidak perlu membagikan secret JWT ke MR.

5. Pastikan `id_opds` akun e-Monev merujuk `ta_opd.id_sub_pd` yang sama pada database
   MR. Source registrasi e-Monev dan model MR memakai referensi tersebut, tetapi
   kesamaan data antar-database produksi tetap harus diverifikasi. Pemetaan
   langsung `id_opds -> opds` digunakan; role 1 adalah admin, role lain dibatasi OPD.
6. Build dan deploy frontend kedua aplikasi, lalu restart backend keduanya.
   Pengguna perlu login sekali lagi di e-Monev untuk memperoleh cookie baru.
   Frontend MR membaca konfigurasi mode melalui `/auth/config`, tanpa build flag.

Jangan ubah reverse proxy agar menyembunyikan header Cookie/Set-Cookie. Dua
aplikasi dilayani oleh origin HTTPS yang sama. Jangan cache respons `/auth/*`.
SSO cookie memerlukan HTTPS, termasuk ketika diuji melalui browser lokal.

## Alur dan batasan

- MR memanggil `/auth/me`, lalu memakai pengguna yang dikembalikan server.
  Jika belum login, pengunjung diarahkan ke e-Monev dengan parameter `return_to`.
  e-Monev hanya menerima tujuan pada origin yang sama dan path `/manajemen-risiko/`.
- Login internal MR dan captcha internal ditolak saat SSO aktif. Endpoint publik
  survei undangan dan Firebase laporan kejadian tetap memakai autentikasinya sendiri.
- Operasi dengan cookie yang mengubah data memerlukan header Origin yang persis
  sama dengan `SSO_PUBLIC_ORIGIN`. SameSite saja bukan satu-satunya kontrol CSRF.
- Logout dari kedua aplikasi mencabut hash sesi di e-Monev dan menghapus cookie.
  Request berikutnya dari tab lain ditolak; data yang sudah tampil tidak otomatis
  hilang sebelum tab tersebut melakukan request/navigasi berikutnya.
- Jika layanan pusat gagal, logout menampilkan kegagalan dan tidak mengklaim
  berhasil. Pengguna bisa mencoba kembali setelah layanan tersedia.
- Sesi berakhir sesuai `ACCESS_TOKEN_EXPIRE_MINUTES` e-Monev. Tidak ada refresh
  otomatis; pengguna login kembali sesudah kedaluwarsa.
- Klien lama (misalnya FrontendSimlaba) tetap bisa meminta bearer token melalui
  login lama. FrontendEmonev mengirim `X-Emonev-SSO: 1` untuk memilih sesi browser.
  Logout bersama mencabut sesi browser SSO ini, bukan semua bearer token lama
  atau sesi perangkat lain. JWT browser memiliki audience terpisah sehingga
  tidak dapat dipakai sebagai bearer lama untuk melewati pencabutan sesi.
- Semua aplikasi pada host ini harus dipercaya; cookie Path bukan batas keamanan
  antar-aplikasi pada origin yang sama.

## Verifikasi sebelum membuka akses produksi

- Login e-Monev, buka MR langsung, refresh, lalu buka URL detail MR langsung.
- Buka MR tanpa cookie: login e-Monev lalu kembali ke halaman yang dituju.
- Uji akun admin, akun OPD A, dan akun OPD B. A tidak boleh mengakses data B,
  termasuk request API langsung dengan ID yang diubah.
- Uji akun diblokir/nonaktif/dihapus setelah login, dan perubahan role/OPD.
- Logout dari MR maupun e-Monev; request di tab lainnya harus ditolak. Ulangi
  request dengan salinan cookie yang dicabut: harus 401.
- Uji cookie kedaluwarsa, tanda tangan salah, penerbit tidak tersedia (503),
  request mutasi dengan Origin hilang/asing (403), dan return_to eksternal.
- Pastikan survei publik, login Firebase, dan klien bearer lama tetap berjalan.

Pengujian unit memakai identitas dummy dan issuer HTTP tiruan, tanpa database
atau endpoint produksi. Uji browser/proxy/database di atas tetap diperlukan.

## Rollback

Kembalikan `SSO_ENABLED=false` pada kedua backend dan restart keduanya. Frontend
mendeteksi mode lama dan MR kembali menyediakan login internal. Cookie lama
bukan kredensial MR pada mode ini. Tabel sesi boleh tetap ada untuk menghindari
penghapusan data saat rollback. Jangan melakukan rollback hanya satu aplikasi
selama pengguna masih memakai alur login bersama.
