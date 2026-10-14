# Form 7 — RTP atas Risiko

Form 7 menampilkan risiko prioritas dari Form 5. Klik ikon pensil untuk mengisi RTP.

- **Status Kegiatan Pengendalian**: pilih “Sudah ada kegiatan pengendalian” atau “Tidak ada Kegiatan Pengendalian”.
- Jika **sudah ada**, wajib mengisi uraian pengendalian, judul berkas, dan satu bukti berupa **unggahan berkas** (maksimal 5 MB, tidak kosong) atau **link HTTP/HTTPS**. Berkas yang tersimpan dapat dipakai kembali saat mengedit.
- Jika **tidak ada**, isian uraian dan bukti disembunyikan dan tidak disimpan sebagai pengendalian aktif. Riwayat perubahan serta berkas versi sebelumnya tetap dipertahankan.
- **Respon Risiko**: mengurangi kemungkinan, mengurangi dampak, membagi, menghindari, atau menerima risiko. Ini mencatat rencana respons pada RTP; proses persetujuan formal pada Detail Risiko tetap terpisah.
- **Target Waktu** memakai dua pemilih tanggal: **Dari tanggal** dan **Sampai tanggal**. Keduanya harus diisi bersama; tanggal akhir tidak boleh mendahului tanggal awal. Masing-masing tersimpan dalam format `YYYY-MM-DD`, dan laporan menampilkan rentangnya. Untuk target lama berupa teks, form menampilkan teks asal dan meminta rentang tanggal pengganti sebelum menyimpan perubahan.
- **Realisasi Waktu** disembunyikan dari form. Nilai realisasi lama tetap disimpan dan masih tersedia dalam laporan historis.

Data mengikuti OPD dan tahun terpilih. Pemilik/Penanggung Jawab otomatis mengikuti Identifikasi Risiko. Cetak Form 7, ekspor Excel/Word, dan laporan berkala menyertakan status, bukti, serta respons risiko.

## Penyimpanan dan pembaruan backend

Restart backend untuk menjalankan migrasi idempoten kolom tambahan (termasuk `target_mulai` dan `target_selesai`) pada `tr_rtp_risiko` dan membuat tabel `tr_rtp_bukti`. Kolom lama tidak dihapus atau diubah tipenya. Berkas disimpan sebagai data biner privat di database, dalam transaksi yang sama dengan perubahan RTP; backup database mencakup berkas. API unggah mengirim base64 dalam JSON, dengan batas berkas 5 MB. Konfigurasi Nginx repositori sudah memiliki batas request 20 MB.

Unduhan menggunakan autentikasi dan pemeriksaan akses OPD serta kepemilikan berkas terhadap risiko; tidak menggunakan direktori publik. Nama berkas tidak dipakai sebagai path penyimpanan. Audit dan snapshot menyimpan metadata/referensi bukti, bukan isi biner. Berkas selalu diunduh sebagai attachment.

API `POST /risiko/rtp` kini memerlukan `status_pengendalian` dan `respon_risiko`. Isian baru divalidasi backend; `realisasi_waktu` tidak diterima sebagai isian form. Tidak ada perubahan otomatis pada status persetujuan respons risiko.
