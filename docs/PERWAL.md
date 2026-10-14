**Arah pengembangan yang paling tepat adalah menjadikan aplikasi ini sebagai sistem pengelolaan risiko dari perencanaan sampai evaluasi efektivitas pengendalian.** Fondasi formulirnya sudah tersedia; pengembangan berikutnya perlu menekankan kewenangan pejabat, persetujuan, bukti pelaksanaan, dan pelaporan berkala.

Saya membandingkan PDF Perwal dengan `plan.md`, dokumentasi, serta model dan layanan utama aplikasi. Identitas regulasinya juga tercantum di [JDIH BPK](https://peraturan.bpk.go.id/Details/345888/perwali-kota-tegal-no-1-tahun-2026). Rujukan pasal dan lampiran di bawah berasal dari PDF yang Anda berikan; usulan fitur merupakan rekomendasi implementasi.

**1. Temuan penting terhadap aplikasi saat ini**

| Aspek | Temuan dan implikasi |
|---|---|
| Matriks risiko | Pemetaan 25 sel dalam `analisis.py` sudah sesuai Tabel 9 Perwal. Pertahankan perhitungan berdasarkan tabel tersebut. |
| Risiko berdampak besar | Kemungkinan **1** dan dampak **5** menghasilkan skor **20**, bukan 5. Risiko yang jarang terjadi tetap bisa sangat tinggi. Ini perlu dijelaskan pada formulir penilaian. |
| Penetapan prioritas | Kode menggunakan **skor >11**. Lampiran Bab II.D mengaitkan prioritas dengan **selera risiko** dan menampilkan garis toleransi. Angka >11 belum dapat dianggap sebagai ketentuan eksplisit Perwal. |
| Konsistensi aturan | Skor **11** dikategorikan sedang dan diberi keterangan “tidak dapat diterima” oleh layanan aplikasi, tetapi tidak masuk prioritas otomatis. Hubungan level, penerimaan, dan prioritas perlu diperjelas. |
| Penilaian setelah pengendalian | Model analisis menyimpan satu penilaian per risiko. Belum terlihat pemisahan penilaian awal, target setelah pengendalian, dan hasil penilaian ulang. |
| Rencana tindak pengendalian | Model RTP menyimpan satu baris per risiko. Pengembangan perlu mendukung beberapa tindakan, masing-masing dengan PIC, tenggat, dan bukti. |
| Dokumentasi dan formulir | README masih menyebut matriks 4×4. Penomoran formulir juga perlu dipetakan ulang: lampiran menyebut RTP risiko sebagai Form 10, komunikasi Form 11, dan rancangan pemantauan Form 12, sedangkan aplikasi menggunakan nomor berbeda. |

Garis toleransi pada gambar juga perlu diperiksa sebagai aturan tersendiri; **warna level risiko tidak otomatis sama dengan keputusan penerimaan risiko**.

**2. Ide fitur yang paling relevan dengan Perwal**

| Pengembangan | Bentuk fitur yang disarankan | Dasar dokumen |
|---|---|---|
| **Struktur pengelola risiko** | Kelola UPR Pemda, UPR OPD, unit kerja, Unit Kepatuhan, Inspektorat, dan Komite; lengkap dengan pejabat, masa penugasan, serta cakupan OPD. | Pasal 4, 5, dan 7 |
| **Kebijakan penilaian berversi** | Simpan matriks, kriteria dampak/kemungkinan, selera risiko, toleransi, tanggal berlaku, dan dokumen penetapan. Penilaian lama tetap memakai versi kebijakannya. | Lampiran II.D dan persiapan penilaian risiko |
| **Persetujuan respons risiko** | Pilihan mengurangi kemungkinan, mengurangi dampak, membagi, menghindari, dan menerima risiko; disertai alasan serta persetujuan sesuai kewenangan. | Lampiran II.D.3.b |
| **Risiko setelah pengendalian** | Catat target dan hasil penilaian ulang. Risiko yang masih melampaui selera/toleransi diteruskan kepada UPR lebih tinggi untuk persetujuan. | Lampiran II.D, hlm. 8 |
| **Pelaksanaan RTP berbukti** | Satu risiko memiliki beberapa tindakan; setiap tindakan mempunyai PIC, tanggal target, hasil, bukti, dan verifikasi efektivitas. | Lampiran III.B |
| **Pelaporan triwulanan dan tahunan** | Paket laporan UPR dan laporan Unit Kepatuhan dibuat terpisah, dengan periode, pengesahan, arsip versi, penerima, dan tembusan. | Pasal 20–21 |
| **Pemantauan Unit Kepatuhan** | Halaman khusus untuk memeriksa penilaian, RTP, keterlambatan, dan tindak lanjut hasil reviu/audit pada OPD binaannya. | Lampiran III.A.5 |
| **Reviu Inspektorat** | Catatan reviu, rekomendasi, tenggat tindak lanjut, dan verifikasi penyelesaian; register risiko dapat menjadi bahan perencanaan pengawasan. | Lampiran II.E dan III.A.6 |

Pemisahan peran tersebut sebaiknya berupa **hak akses berbasis penugasan**, sehingga satu pengguna bisa mempunyai kewenangan berbeda pada beberapa OPD. Admin teknis juga perlu dipisahkan dari pejabat yang berwenang mengesahkan substansi.

**3. Pengembangan yang paling terasa manfaatnya bagi pengguna**

**Halaman detail risiko yang menyatukan seluruh proses.**  
Pengguna membuka satu risiko dan melihat konteks tujuan, penyebab, dampak, penilaian, pengendalian, kejadian, bukti, dan riwayat keputusan. Formulir tetap tersedia sebagai keluaran cetak, sementara data saling terhubung.

Alur utama yang saya sarankan:

**Konteks → Identifikasi → Penilaian → Penentuan prioritas → Respons/RTP → Pelaksanaan dan bukti → Penilaian ulang → Pelaporan**

**Dashboard pimpinan yang berorientasi keputusan.**  
Tampilkan risiko utama terhadap sasaran RPJMD, risiko berdampak sangat besar, tindakan terlambat, risiko setelah pengendalian yang masih melampaui toleransi, serta keputusan yang menunggu persetujuan. Untuk perbandingan antar-OPD, gunakan kelengkapan penilaian dan efektivitas tindak lanjut; jumlah risiko yang sedikit belum tentu menunjukkan pengelolaan yang baik.

**Integrasi laporan kejadian dengan evaluasi risiko.**  
Fitur Lapor Kejadian dan Approval Kejadian sudah ada. Pengembangannya: setelah validasi, kejadian ditautkan ke risiko terdaftar atau menjadi usulan risiko baru. Kejadian berulang memicu peninjauan skor dan efektivitas RTP. Persetujuan laporan kejadian tidak otomatis berarti pengendaliannya efektif.

**Pengelolaan risiko fraud yang lebih terarah.**  
Perwal menempatkan fraud/kecurangan sebagai kategori risiko. Sebagai pengembangan, tambahkan skenario kecurangan, proses rawan, kelemahan pengendalian, indikator peringatan, serta pembatasan akses informasi sensitif. Perlakukan laporan sebagai indikasi yang perlu diverifikasi. Mekanisme ini merupakan usulan desain, bukan rincian sistem pelaporan fraud yang secara eksplisit diwajibkan dokumen.

**Kamus risiko yang dapat berkembang.**  
Karena rencana aplikasi mewajibkan pemilihan dari kamus, sediakan proses **usulan entri kamus baru → reviu → publikasi**. Ini menjaga standardisasi tanpa menghalangi pencatatan risiko baru.

**4. Urutan pengembangan yang saya rekomendasikan**

| Tahap | Fokus | Hasil yang diharapkan |
|---|---|---|
| **1 — Konsistensi kebijakan** | Selaraskan aturan prioritas, toleransi, kriteria penilaian, dokumentasi, dan pemetaan formulir. | Hasil penilaian dapat dijelaskan dan ditelusuri dasarnya. |
| **2 — Tata kelola** | Struktur UPR, hak akses, persetujuan respons, pengesahan dokumen, dan jejak perubahan. | Jelas siapa menyusun, memeriksa, dan mengambil keputusan. |
| **3 — Pelaksanaan** | Beberapa tindakan per risiko, bukti pelaksanaan, penilaian ulang, dan hubungan dengan kejadian. | Efektivitas pengendalian dapat dievaluasi. |
| **4 — Pengawasan dan laporan** | Laporan triwulanan/tahunan, halaman Unit Kepatuhan dan Inspektorat, serta dashboard pimpinan. | Pemantauan dan pelaporan lintas OPD dapat dilakukan secara konsisten. |

Secara teknis, **FastAPI, PostgreSQL, Vue, dan PrimeVue yang digunakan sekarang sudah memadai**. Perubahan utama ada pada model data dan alur kerja: tambahkan riwayat penilaian, detail tindakan pengendalian, bukti, persetujuan, dan laporan per periode. Simpan salinan data saat laporan disahkan agar perubahan berikutnya tidak mengubah laporan yang sudah diterbitkan.

Analisis ini berdasarkan pemeriksaan dokumen dan kode utama; belum mencakup pengujian aplikasi berjalan.