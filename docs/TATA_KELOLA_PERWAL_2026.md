# Implementasi tata kelola risiko — Perwal Kota Tegal 1/2026

Tanggal implementasi: 13 Oktober 2026. Dokumen ini melengkapi analisis awal pada [PERWAL.md](PERWAL.md).

## Modul yang tersedia

Buka **Beranda → Tata Kelola Risiko**. Pilih OPD dan tahun pada bagian atas aplikasi.

| Menu | Fungsi |
|---|---|
| Pemantauan | Register risiko, skor awal/residual, keterlambatan tindakan, pengajuan respons dan kebutuhan penilaian ulang setelah kejadian |
| Lintas OPD | Ringkasan OPD dalam cakupan akses SSO, kelengkapan penilaian dan tindak lanjut |
| Kebijakan Penilaian | Pengajuan dan persetujuan kriteria berversi: lima kriteria dampak/kemungkinan, urutan area dampak dan kategori |
| Struktur & Penugasan | Pejabat/petugas per OPD, username SSO, peran, masa penugasan dan dasar SK |
| Laporan Berkala | Laporan penilaian, UPR, Unit Kepatuhan dan pembinaan; triwulanan/tahunan; kompilasi strategis Pemda |
| Usulan Kamus | Pengajuan, reviu dan publikasi entri kamus. Pengubahan langsung master kamus dibatasi admin |
| Riwayat Aktivitas | Pelaku, waktu, jenis aktivitas dan referensi, maksimal 200 aktivitas terbaru per OPD/tahun |

Klik kode/uraian risiko pada Pemantauan, Form Analisis, atau Form Prioritas untuk membuka **Detail Pengelolaan Risiko**. Halaman ini menyatukan identifikasi, penilaian, respons, tindakan, reviu, kejadian dan analisis fraud yang dibatasi aksesnya.

## Urutan penggunaan pertama

1. Admin mencatat penugasan sesuai SK. Username harus merujuk akun SSO yang digunakan pejabat. Cakupan OPD tetap berasal dari `sso_users.opds`; penugasan tidak memperluas akses SSO.
2. Pengelola mengajukan kebijakan. Isi dasar penetapan/FGD, tanggal berlaku pada tahun yang sama, serta kriteria operasional skala 1–5. Melalui menu Selera Risiko, catat ambang 1–25 sesuai keputusan Pemilik Risiko beserta pertimbangan sumber dayanya.
3. Pengguna lain dengan penugasan `upr_pemda` pada OPD tersebut meninjau dan menyetujui kebijakan. Admin teknis tidak mendapat hak persetujuan otomatis.
4. Lakukan penilaian awal melalui Form Analisis atau detail risiko. Skor dihitung oleh backend; riwayat menyimpan salinan kebijakan dan alasan penilaian.
5. Tetapkan area dampak serta urutan pimpinan untuk pemeringkatan risiko yang memiliki skor sama.
6. Ajukan respons berdasarkan riwayat penilaian. Tambahkan satu atau beberapa tindakan pengendalian beserta PIC dan tanggal target.
7. Catat pelaksanaan. Status selesai memerlukan referensi bukti, kemudian diverifikasi oleh pengguna lain yang berwenang.
8. Catat penilaian residual dengan bukti evaluasi. Ajukan respons lanjutan bila risiko masih melampaui selera/toleransi.
9. Unit Kepatuhan atau Inspektorat mencatat temuan dan rekomendasi. Pengelola mengisi tindak lanjut; pemeriksa memverifikasi sebelum menutupnya.
10. Susun laporan sesuai periode. Tinjau halaman laporan terlebih dahulu, kemudian penyetuju yang berwenang memberikan keputusan. Cetak melalui browser atau simpan sebagai PDF.

## Peran dan keputusan

| Peran | Kewenangan pada modul baru |
|---|---|
| operator | Menyusun penilaian, respons, tindakan dan tindak lanjut |
| upr | Menyusun/memeriksa pengelolaan OPD; menyetujui respons pengurangan; menetapkan urutan prioritas; memverifikasi tindakan; menyetujui laporan UPR dan usulan kamus |
| atasan | Memutuskan pengajuan penerimaan risiko |
| upr_atasan | Memutuskan pembagian/penghindaran risiko dan eskalasi target/residual yang melampaui batas |
| upr_pemda | Menyetujui kebijakan; menyusun/mengesahkan laporan strategis Pemda; menetapkan urutan prioritas |
| kepatuhan | Mencatat reviu kepatuhan, memverifikasi tindakan/tindak lanjut, menyusun/mengesahkan laporan pemantauan |
| inspektorat | Mencatat dan memverifikasi reviu pengawasan, memverifikasi tindakan, mereviu usulan kamus dan mengakses skenario fraud |
| komite | Menyusun/mengesahkan laporan pembinaan |
| koordinator | Menyusun kompilasi laporan strategis Pemda dari OPD yang dapat diakses |

Satu pengguna dapat memiliki beberapa penugasan. Persetujuan selalu mensyaratkan pengguna berbeda dari pengusul. Verifikasi tindakan tidak boleh dilakukan oleh pembuat atau pelaksana terakhirnya. Penugasan yang berakhir atau dinonaktifkan tidak dapat dipakai untuk menyetujui.

Akun OPD lama yang belum pernah diberi penugasan tetap dapat mengusulkan. Setelah penugasan digunakan, hak menulis mengikuti peran aktif; akun dengan hanya peran pemantauan/persetujuan tidak otomatis dapat menulis penilaian. Hak baca tetap mengikuti cakupan OPD SSO. Penugasan ulang dilakukan admin berdasarkan dokumen kewenangan, bukan dengan mengubah ID role SSO.

## Kebijakan dan matriks

Matriks mengikuti Tabel 9 Lampiran Perwal 1/2026:

| Kemungkinan \ Dampak | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 5 | 11 | 15 | 18 | 23 | 25 |
| 4 | 6 | 12 | 16 | 19 | 24 |
| 3 | 4 | 8 | 14 | 17 | 22 |
| 2 | 2 | 7 | 10 | 13 | 21 |
| 1 | 1 | 3 | 5 | 9 | 20 |

Skor tidak dihitung dengan perkalian. Level: 1–5 sangat rendah, 6–10 rendah, 11–15 sedang, 16–19 tinggi, 20–25 sangat tinggi. Warna level tidak menentukan penerimaan risiko.

Selera Risiko ditetapkan melalui menu tersendiri, berupa ambang bilangan bulat 1–25 per OPD/tahun dan Pemilik Risiko. Skor ≤ ambang diterima; skor > ambang memerlukan pengendalian. Ketetapan entitas menjadi dasar jika belum ada ketetapan khusus pemilik. Garis ungu mengikuti batas area penerimaan; untuk pemilik dengan ambang berbeda, pilih pemilik pada matriks.

Tanpa ketetapan, penilaian baru ditolak dengan petunjuk membuka menu Selera Risiko. Tidak ada ambang otomatis. Pertimbangan sumber daya wajib dicatat; akun pencatat tersimpan otomatis. Form mengelola ketetapan tingkat entitas tanpa isian cakupan dan nama/jabatan penetap. Kriteria penilaian tetap diajukan melalui Tata Kelola; kolom selera/toleransi kebijakan lama hanya menjadi arsip. [Panduan Selera Risiko](SELERA_RISIKO.md).

Kebijakan aktif dipilih berdasarkan tanggal berlaku terbaru yang tidak melampaui hari ini, lalu ID terbaru jika tanggal sama. Pengajuan yang ditolak tidak aktif. Versi kebijakan tidak diedit setelah diajukan; koreksi melalui pengajuan baru. Penilaian sebelumnya tidak dihitung ulang diam-diam.

Form Analisis tetap menyimpan ringkasan penilaian awal pada tabel lama agar formulir dan ekspor sebelumnya bekerja. Riwayat awal/target/residual disimpan terpisah. Target dan residual tidak menimpa skor awal. Prioritas saat ini dihitung otomatis dari ambang pemilik. Revisi ambang memperbarui ringkasan analisis tanpa menulis ulang riwayat penilaian atau laporan tersimpan.

Form Prioritas diurutkan dalam setiap jenis risiko menurut skor menurun, urutan area dampak, urutan kategori, kemudian urutan keputusan pimpinan. Nilai yang belum dipetakan ditempatkan setelah nilai yang telah ditetapkan.

## Pengendalian, kejadian dan fraud

- Beberapa tindakan dapat ditambahkan pada satu risiko; RTP lama tetap tampil sebagai referensi.
- Status tindakan: direncanakan → berjalan/selesai → terverifikasi. Hasil tidak efektif tetap dicatat dan dapat ditindaklanjuti dengan tindakan baru.
- Bukti saat ini berupa referensi/nomor/lokasi dokumen yang diisi sebagai teks, bukan unggahan berkas. Jangan menaruh kredensial atau token tautan rahasia di dalamnya.
- Laporan kejadian hanya dapat ditautkan ke risiko pada OPD dan tahun yang sama. Penyalinan baru ke Monitoring Event bersifat idempoten melalui tabel tautan. Pengulangan validasi tidak membuat kejadian baru. Duplikasi yang sudah ada sebelum pembaruan tidak dihapus atau digabung otomatis.
- Laporan yang telah ditautkan tidak dapat dihapus/dipindah risiko melalui endpoint approval. Kejadian setelah penilaian residual terakhir menjadi indikator kebutuhan penilaian ulang di dashboard.
- Skenario fraud, proses rawan, kelemahan dan indikator hanya tersedia untuk penugasan UPR/Inspektorat. Data skenario tersebut tidak masuk detail umum, laporan umum, atau payload riwayat aktivitas yang dikirim ke browser. Catatan merupakan potensi/indikasi, bukan kesimpulan pelanggaran.

## Laporan dan arsip

Tiga keluaran utama sesuai Pasal 20–21 tersedia: laporan pelaksanaan penilaian, laporan berkala UPR, serta laporan berkala Unit Kepatuhan. Laporan pembinaan Komite ditambahkan sebagai keluaran tersendiri.

Data laporan dibekukan saat **pengajuan**, sehingga yang diperiksa dan disahkan adalah data yang sama. Tidak ada endpoint untuk mengubah isi snapshot laporan. Pengajuan revisi menghasilkan dokumen dengan ID baru; versi lama tetap tersimpan. Persetujuan/penolakan berulang ditolak.

Register, penilaian dan status tindakan menggambarkan keadaan saat pengajuan. Hanya kejadian yang difilter menggunakan tanggal awal/akhir triwulan atau tahun. Laporan yang disusun terlambat **bukan rekonstruksi keadaan historis pada akhir triwulan**; keterangan ini dicetak pada dokumen. Periode mendatang yang belum dimulai ditolak.

Kompilasi Pemda mengumpulkan **risiko strategis Pemda** dari OPD sumber yang dipilih. Semua OPD sumber harus berada dalam cakupan SSO penyusun/pembaca/penyetuju. Penyusun membutuhkan peran koordinator atau UPR Pemda, penyetuju membutuhkan UPR Pemda. Laporan disimpan pada OPD koordinator yang sedang dipilih. Laporan OPD biasa mencakup risiko pada OPD tersebut.

Penerima laporan UPR/penilaian adalah Wali Kota, dengan tembusan Sekretaris Daerah dan Unit Kepatuhan. Laporan Unit Kepatuhan/pembinaan mencantumkan tembusan Sekretaris Daerah. Aplikasi mencatat persetujuan internal dan menghasilkan cetakan; belum mengirim laporan ke penerima atau membubuhkan TTE tersertifikasi.

## Padanan formulir

Identitas route/data lama dipertahankan. Cetak HTML, Word dan kepala lembar Excel mencantumkan padanan berikut:

| Menu/form aplikasi | Padanan pada lampiran Perwal |
|---|---|
| Form 7 — RTP risiko | Form 10 |
| Form 8 — Informasi dan komunikasi | Form 11 |
| Form 9 — Rencana pemantauan | Form 12 |
| Form 10 — Catatan kejadian | Tetap berlabel catatan kejadian/form aplikasi; tidak disamakan dengan Form 10 RTP pada lampiran |

Lampiran juga menyebut Form 12 pada uraian catatan kejadian. Karena rujukan tersebut bertumpang tindih dengan rancangan pemantauan, nama fungsi digunakan untuk membedakannya. Pemetaan ini tidak mengklaim seluruh tata letak cetak lama identik dengan lampiran.

## Instalasi dan aktivasi

Backend mempertahankan pola startup `init_db()` yang sudah ada. Model baru diimpor sebelum `SQLModel.metadata.create_all()`. Tabel baru menggunakan nama `mr_selera_risiko`, `mr_penugasan_risiko`, `mr_kebijakan_risiko`, `tr_penilaian_riwayat`, `tr_respons_risiko`, `tr_tindakan_risiko`, `tr_reviu_risiko`, `tr_laporan_berkala`, `tr_audit_risiko`, `tr_usulan_kamus`, `tr_fraud_risiko`, `tr_urutan_prioritas`, dan `tr_kejadian_tautan`.

Tidak ada migrasi yang menghapus data lama atau menyalin skor historis seolah-olah dinilai dengan kebijakan baru. Tabel baru dibuat saat backend dijalankan ulang. Pengujian pengembangan memakai database terisolasi; konfigurasi dan isi database aplikasi tidak diubah oleh pengujian.

```bash
cd BackEnd
.venv/bin/python -m pip install -r requirements.txt
# Jalankan ulang backend dengan mekanisme deployment yang digunakan.
```

Dependensi laporan Word `python-docx` dan `docxtpl` kini dicantumkan pada requirements karena modul laporan mengimpornya saat startup.

```bash
cd FrontEnd
npm run build
```

Setelah backend/frontend diperbarui, admin mengisi penugasan dan pejabat mengesahkan kebijakan. Nilai kebijakan resmi serta dasar SK harus berasal dari pengelola yang berwenang, bukan dari contoh pengujian.

## Verifikasi pengembangan

```bash
cd BackEnd
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
bash tests/run_postgres.sh
```

Pengujian biasa menggunakan SQLite sementara. Skrip PostgreSQL membuat cluster sementara di `/tmp`, memakai Unix socket terpisah dan database `mr_test_governance`, lalu menghentikan serta menghapus cluster saat selesai. Skrip membutuhkan `initdb`, `pg_ctl`, dan `createdb`. Jangan arahkan `MR_TEST_DATABASE_URL` ke database aplikasi: pengujian menghapus tabel database pengujiannya. Nama database eksternal untuk pengujian dibatasi awalan `mr_test_`.

Skenario mencakup otorisasi antar-OPD, peran dan masa tugas, larangan persetujuan sendiri, matriks 5×5, skor 11, pengambilan kebijakan, keutuhan riwayat, beberapa tindakan, bukti wajib, reviu, usulan kamus, pembatasan fraud, snapshot laporan, kompilasi Pemda, kejadian idempoten, startup PostgreSQL berulang dan persetujuan serentak.

Pemeriksaan browser menggunakan data sintetis dan API lokal terisolasi: perpindahan tab, dialog kebijakan, penyimpanan tindakan, penilaian residual, halaman laporan/cetak PDF, tampilan mobile, dan Form Analisis. Pengujian ini tidak mengirim email/WhatsApp dan tidak menggunakan data pengguna sebenarnya.

Hasil verifikasi 13 Oktober 2026: 41 pengujian backend berhasil dijalankan (2 skenario PostgreSQL dilewati pada SQLite), 23 pengujian tata kelola pada PostgreSQL sementara lulus, build produksi frontend lulus, dan alur browser selesai tanpa kesalahan JavaScript. Startup/OpenAPI backend juga berhasil dimuat. Pengujian PostgreSQL mencakup startup berulang serta persetujuan serentak.
