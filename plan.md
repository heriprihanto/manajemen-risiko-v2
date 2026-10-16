Buat Web App Manajemen Risiko
backend : python, fastapi, sqlalchemy, sqlmodel
database : postgresql, configurasi di @BackEnd/.env
frontend : VueJS, PrimeVue
Transform file Excel @Kertas Kerja Manajemen Risiko.xls menjadi aplikasi manajemen risiko
Sheet Form 1.a CEE persepsi merupakan hasil kuisioner ( sheet KUISIONER), koolom R1, R2 - R29 dinamis merupakan nilai hasil kuisioner,
sheet lainnya saling terhubung satu sama lain
data per OPD (Organisasi Perangkat Daerah), sudah ada tabel ta_opd di database


buat Authentifikasi, Login dengan JWT
sudah ada tabel sso_users untuk data pengguna
login menggunakan query SELECT * FROM public.sso_users u WHERE u.username = :username  AND password = encode_passwd(:username, :password)
field role_id merupakan role pengguna 1 Admin, 4 OPD
field opds merupakan array dari id OPD, karena satu pengguna bisa lebih dari satu OPD

Halaman Form 2.b — Konteks Strategis OPD
Form Entri :
Field Tujuan pilih dari tabel renstra_tujuan
Field Sasaran pilih dari tabel renstra_sasaran
Field Program pilih dari tabel renstra_program

Halaman Form 2.b — Konteks Strategis OPD
Form Entri :
field periode dinilai pilih dari tabel renstra_tahap

Halaman Form 2.b — Konteks Strategis OPD
Form Entri :
field IKU Renstra pilih dari tabel renstra_indikator_tujuan_sasaran where iku=1

Halaman Form 2.b — Konteks Strategis OPD
hapus field Urusan Pemerintahan
Penetapan Konteks (T/S/IKU/Program)

Printout cetak seperti contoh PDF
perhatikan blok warna hijau, adalah semua yang ada di tabel renstra
blok kuning hanya data yang dientri di Form 2.b — Konteks Strategis OPD
Bidang urusan dari field bidang_urusan tabel ta_opd


Revisi printout Form 2.b — Konteks Strategis OPD :
Tujuan Strategis, Sasaran Strategis, IKU Renstra OPD, Program adalah semua data yang ada di tabel renstra
"Tujuan, Sasaran, IKU dan Program yang akan dilakukan penilaian risiko" adalah data yang dientri di Form 2.b — Konteks Strategis OPD


Revisi printout Form 2.b — Konteks Strategis OPD :
Kolom "Tujuan, Sasaran, IKU dan Program yang akan dilakukan penilaian risiko" adalah data yang hanya dientri di Form 2.b — Konteks Strategis OPD bukan semua data yang ada di renstra

Revisi Entri Form 2.c — Konteks Operasional OPD
hanya memilih indikator pada tabel renja_indikator, centang subkegiatan yang dipilih yang akan dilakukan penilaian risiko
renja_indikator berelasi dengan tabel renja_subkegiatan dengan id_parent = idsubkegiatan

Revisi Entri Form 2.c — Konteks Operasional OPD
indikator kegiatan bisa dicentang sebagai  indikator yang dipilih yang akan dilakukan penilaian risiko
renja_indikator berelasi dengan tabel renja_subkegiatan dengan id_parent = idkegiatan


Pisahkan Form 3.a, 3.b, 3.c menjadi menu tersendiri jangan digabung


Form 3.b — Identifikasi Risiko Strategis OPD
menggunakan data dari Form 2.b — Konteks Strategis OPD, pengguna hanya melengkapi :
Risiko :
- Uraian Risiko
- Kode Risiko
- Pemilik Risiko

Sebab :
- Uraian 
- Sumber : Internal, Eksternal, Internal / Eksternal
- C/ UC

Dampak :
- Uraian
- Pihak yang Terkena

Form 3.b — Identifikasi Risiko Strategis OPD :
pilihan Tujuan/Sasaran/IKU/Program tambahkan data dari indikator program pada Form 2.c — Konteks Operasional OPD

Form 3.c — Identifikasi Risiko Operasional OPD
data dari pilihan indikator subkegiatan yang dipilih pada Form 2.c — Konteks Operasional OPD

Form 3.c — Identifikasi Risiko Operasional OPD
field tahap dibuat select : Pelaksanaan, Pertanggungjawaban


Form 3.c — Identifikasi Risiko Operasional OPD
field kode risiko dibuat otomatis dengan format :
RSO.


Pemilik / Penanggug jawab yang sudah dientri di Form 3.b — Identifikasi Risiko Strategis OPD akan tersimpan selalu sama untuk Form selanjutnya


Print Out / cetak Form 9, tambahkan grouping by jenis risiko


Print Out / cetak Form 10, tambahkan grouping by jenis risiko

Buat menu (hanya untuk admin) untuk manajemen daftar pertanyaan yang akan dipublish untuk kuisioner 
tambahkan chaptcha pada login

sidebar menu, background dengan gradasi

text pada sidebar menu lebih kontras dengan background supaya lebih jelas terbaca

kuisioner hanya boleh satu email satu tahun  



Revisi Form 2.a — Konteks Strategis Pemda
Periode yang dinilai : combobox : RPJMD 2025 - 2029  
Visi : pilih dari tabel rpjmd_visi
Misi Strategis RPJMD : pilih dari tabel rpjmd_misi (bisa pilih lebih dari satu)
Penetapan Konteks Tujuan Risiko Strategis Pemda : pilih dari tabel rpjmd_tujuan (bisa pilih lebih dari satu)
Penetapan Konteks Sasaran  Risiko Strategis Pemda : pilih dari tabel rpjmd_sasaran (bisa pilih lebih dari satu)
Penetapan konteks IKU Risiko Strategis Pemda : pilih dari tabel renja_indikator where lvl < 3 and iku=1 (bisa pilih lebih dari satu)
Prioritas pembangunan Daerah : pilih dari tabel ref_prioritas (bisa pilih lebih dari satu)
Program Prioritas : pilih dari tabel rpjmd_program (bisa pilih lebih dari satu)


buat halaman Kamus Risiko dibawah Menu Pengelolaan Risiko
CRUD dari tabel mr_kamus_risiko

Jadikan satu di menu Penetapan Konteks
jadikan Tab
Form 2.a — Konteks Strategis Pemda
Form 2.b — Konteks Strategis OPD
Form 2.c — Konteks Operasional OPD

Jadikan satu di menu Identifikasi Risiko
jadikan Tab
Form 3.a — Identifikasi Risiko Strategis Pemda
Risiko Strategis OPD (Form 3.b) 
Risiko Operasional OPD (Form 3.c)

Kamus Risiko
Edit kode risiko
format : Kategori-nomor urut
contoh Kategori Risiko Operasional, kode risiko RO-001
Kategori Risiko Fraud, kode risiko RF-001
Kategori Risiko Kebijakan, kode risiko RK-001

Tambah


Kode Risiko  pada (Form 3.a / 3.b / 3.c) Otomatis dengan Format : RSO.26.00.05.001

RSO = Kode Jenis Risiko 
    RSP : Strategis Pemda
    RSO : Strategis OPD 
    ROO : Operasional OPD 
26 = Tahun pelaksanaan penilaian risiko adalah 2026
00 = Kode urusan wajib/pilihan (untuk risiko strategis Perangkat Daerah dan Operasional) atau tujuan strategis (untuk risiko strategis Pemerintah Daerah).

05 = Kode Pemerintah Daerah yang menilai (untuk risiko strategis Pemerintah Daerah) atau kode Perangkat Daerah yang menilai (untuk risiko strategis Perangkat Daerah dan Operasional) 
        
01 = Nomor urut risiko


Revisi Identifikasi Risiko Operasional OPD (Form 3.c)

Tambah field combobox Bidang Urusan, data dari ref_bidang_urusan
Kode Risiko otomatis dengan format : ROO.26.00.05.001
ROO : Operasional OPD 
26 = Tahun pelaksanaan penilaian risiko adalah 2026
00 = Kode bidang urusan, dari field Bidang Urusan /  tabel ref_bidang_urusan -> field kode_risk
05 = kode_risk pada tabel ta_opd pada OPD tersebut
01 = Nomor urut risiko, berdasarkan nomor urut risiko yang sudah ada


Revisi Identifikasi Risiko Strategis Pemda (Form 3.a) 
Tambah field combobox Bidang Urusan, data dari ref_bidang_urusan
Kode Risiko otomatis dengan format : RSP.26.00.05.001
RSP : Risiko Strategis Pemda
26 = Tahun pelaksanaan penilaian risiko adalah 2026
00 = Kode bidang urusan, dari field Bidang Urusan /  tabel ref_bidang_urusan -> field kode_risk
01 = selalu pakai kode 01 untuk Risiko Strategis Pemda
01 = Nomor urut risiko, berdasarkan nomor urut risiko yang sudah ada



Revisi Identifikasi Risiko  pada (Form 3.a / 3.b / 3.c), simpan juga Kategori Risiko yang diambil dari Kamus Risiko


Revisi Identifikasi Risiko  pada (Form 3.a / 3.b / 3.c), Kategori Risiko read only, otomatis dari Kamus Risiko

Revisi halaman dashboard, lebih komplit,  informatif, sebagai eksekutif summary. bisa heatmap atau berikan rekomendasi yang lebih bagus

Form 4 — Analisis Risiko
revisi option pada :
Combobox Kemungkinan :  1 Hampir tidak terjadi
                        2 Jarang terjadi
                        3 Kadang terjadi
                        4 Sering terjadi
                        5 Hampir pasti terjadi

Combobox Dampak :   1 Tidak signifikan  
                    2 Minor
                    3 Moderate
                    4 Signifikan
                    5 Sangat Signifikan

Ubah Juga Matriks Analis Risiko / Heat Map menjadi 5x5 dengan Kemungkinan dan Dampak diatas
Level Risiko	    Besaran risiko	Warna
Sangat Tinggi (5)	20 s.d 25	    Merah
Tinggi (4)	        16 s.d 19	    Oranye
Sedang (3)	        11 s.d 15	    Kuning
Rendah (2)	        6 s.d 10	    Hijau Muda
Sangat Rendah (1)	1 s.d 5	        Hijau Tua


Revisi Matriks Analis Risiko / Heat Map, sesuai gambar
Nilai level risiko bukan lagi hail perkalian Kemungkinan x Dampak, tetapi nilai level risiko sesuai di gambar,
perhatikan gambar Heat map, nilai level risiko 


Form 4 — Analisis Risiko
Tetakan sebagai prioritas jika Skala > 11
                       

Revisi Kode Risiko  pada (Form 3.a / 3.b / 3.c) Otomatis dengan Format : RSO.26.00.01.05.001

RSO = Kode Jenis Risiko 
    RSP : Strategis Pemda
    RSO : Strategis OPD 
    ROO : Operasional OPD 
26 = Tahun pelaksanaan penilaian risiko adalah 2026
01 : Jenis Risiko :
    RSP : 01
    RSO : 02 
    ROO : 03 
01 = Kode urusan wajib/pilihan (untuk risiko strategis Perangkat Daerah dan Operasional) atau tujuan strategis (untuk risiko strategis Pemerintah Daerah).

05 = Kode Pemerintah Daerah yang menilai (untuk risiko strategis Pemerintah Daerah) atau kode Perangkat Daerah yang menilai (untuk risiko strategis Perangkat Daerah dan Operasional) 
        
01 = Nomor urut risiko



Identifikasi Risiko
(Form 3.a / 3.b / 3.c) 
Tambah field Keterangan Uraian Risiko dibawah Uraian Risiko


Identifikasi Risiko
(Form 3.a / 3.b / 3.c) 
Uraian Risiko harus pilih dari Kamus Risiko, tidak bisa mengetik sendiri



PERUBAHAN FLOW PENGISIAN SURVEY CEE
Admin entri daftar calon Responden dengan isian : NIP | Nama | Jabatan | email | no HP
Admin mengirim email ke semua responden dengan pemberitahuan untuk mengisi survey pada link dengan token ID yang sudah digenerate pada masing-masing responden saat admin entri calon responden 
Responden membuka link survey, tidak perlu login hanya memasukkan token ID yang sudah dikirim via email


Form 1.a — Kuesioner CEE (Persepsi)
Daftar Calon Responden dan hasil kuisioner dibuat layout Tab, jangan bertumpukan atas bawah

undangan survei juga dikirim via whatsapp :
Whatsapp gateway  :
url = "http://localhost:3000/send/message"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Device-Id": "eMonev",
        }

        payload = {
            "phone": f"{wa_numb}@s.whatsapp.net",
            "message": f"{message}",
        }

Pada survei, tambahkan isian textarea narasi lain terkait kondisi lingkungan pengendalian

Form 1.a — Kuesioner CEE (Persepsi)
Buat button menu Kirim Undangan :
                - Kirim Undangan via Email
                - Kirim Undangan via WhatsApp

Template Undangan via Email & WhatsApp bisa diatur di pengaturan aplikasi

Buat Halaman Publik Lapor Kejadian
Lapor kejadian dapat diakses oleh seluruh pegawai di OPD. login dengan firebase
Pada halaman lapor kejadian, buat button simpan dan logout
Field yang diisi :
Tahun, 
Organisasi Perangkat Daerah,
No. HP
Nama Lengkap
Uraian Kejadian 
Waktu Kejadian
Tempat
Pemicu

Semua informasi lapor kejadian akan masuk di Menu Approval Kejadian dan akan divalidasi oleh pengelola risiko


## Implementasi rekomendasi Perwal 1/2026 — 13 Oktober 2026

Panduan lengkap: [Tata Kelola Perwal 1/2026](docs/TATA_KELOLA_PERWAL_2026.md).

- [x] Kebijakan penilaian berversi: selera, toleransi, kriteria skala dan dasar penetapan; persetujuan UPR Pemda.
- [x] Matriks 5×5 dan prioritas mengikuti kebijakan; aturan >11 hanya fallback lama yang diberi label.
- [x] Penugasan pejabat per OPD dan masa tugas; admin teknis tidak otomatis menjadi penyetuju.
- [x] Riwayat penilaian awal, target dan residual dengan salinan kebijakan.
- [x] Pengajuan respons, persetujuan sesuai peran, eskalasi dan larangan persetujuan sendiri.
- [x] Beberapa tindakan per risiko, PIC, tenggat, referensi bukti dan verifikasi efektivitas.
- [x] Reviu Unit Kepatuhan/Inspektorat, tindak lanjut dan verifikasi penutupan.
- [x] Detail risiko terpadu, pemantauan keterlambatan dan kebutuhan penilaian ulang setelah kejadian.
- [x] Validasi OPD/tahun kejadian dan pencegahan penyalinan berulang ke Monitoring Event.
- [x] Usulan kamus → reviu → publikasi; CRUD langsung master hanya admin.
- [x] Analisis skenario fraud dengan akses terbatas UPR/Inspektorat.
- [x] Laporan triwulanan/tahunan dengan snapshot tetap, persetujuan internal dan cetak PDF.
- [x] Pemantauan lintas OPD dan kompilasi risiko strategis Pemda sesuai cakupan SSO.
- [x] Pemeringkatan berdasarkan skor, area dampak, kategori dan keputusan pimpinan.
- [x] Padanan cetak Form 7/8/9 aplikasi dengan Form 10/11/12 lampiran; README dan manual diselaraskan.
- [x] Pengujian backend, PostgreSQL sementara, build frontend dan alur browser dengan data sintetis.

Aktivasi operasional: jalankan ulang backend dan gunakan hasil build frontend, lalu isi penugasan berdasarkan SK serta ajukan/disahkan kebijakan resmi. Tidak ada penugasan atau keputusan kebijakan resmi yang diisi otomatis. Pengujian tidak mengubah database aplikasi.

Batas implementasi: bukti berbentuk referensi dokumen; persetujuan merupakan pencatatan internal, belum TTE tersertifikasi/pengiriman laporan. Laporan menyimpan keadaan saat pengajuan dengan kejadian difilter per periode, bukan rekonstruksi otomatis keadaan akhir triwulan yang telah lewat.

Batas Toleransi Risiko (Selera Risiko) masih hardcode, sekarang buat menu baru untuk menentukan Selera risiko. Selera risiko     adalah ambang batas besaran level risiko yang berada dalam area
penerimaan risiko dan tidak perlu dilakukan kegiatan pengendalian. Selera risiko
ditetapkan oleh masing-masing Pemilik Risiko.
Pemilik Risiko menentukan selera risiko dengan mempertimbangkan semua
sumber daya yang dimiliki oleh entitas atau unit kerja.
Pilihan skala risiko untuk tingkat entitas dengan memilih angka dari 1 hingga nilai
terbesar. Nilai terbesar tersebut akan ditentukan oleh skala risiko yang digunakan.
Jika menggunakan skala 5 x 5, maka nilai selera risiko bisa dipilih antar 1 sampai
dengan 25.



Form 7 — RTP atas Risiko

Tambahkan Opsi Status Kegiatan Pengendalian : 
1. Sudah ada kegiatan pengendalian 
2. Tidak ada Kegiatan Pengendalian 

jika pilih Sudah ada kegiatan pengendalian, harus entri :
- Uraian Pengendalian yang Sudah Ada
- Unggah berkas / link
- judul berkas

Tambahkan field Respon Risiko, opsi :
1. Mengurangi kemungkinan terjadinya Risiko
2. Mengurangi dampak Risiko
3. Membagi Risiko
4. Menghindari Risiko
5. Menerima Risiko

field Target Waktu diganti menjadi datepicker

sembunyikan Realisasi Waktu

Form 8 — Informasi & Komunikasi
Pada tampilan tabel, sudah tersedia data Kegiatan Pengendalian dari Respon Risiko (RTP) 
User hanya menambahkan data pada form:
- Media/Bentuk Sarana 
- Penyedia Informasi
- Penerima Informasi
- Rencana Waktu (datepicker dari tanggal sampai tanggal)
- Keterangan

Form 9 — Rencana Pemantauan PI
Pada tampilan tabel, sudah tersedia data Kegiatan Pengendalian dari Respon Risiko (RTP) 
User hanya menambahkan data pada form:
- Bentuk/Metode Pemantauan
- Penanggung Jawab
- Rencana Waktu (datepicker dari tanggal sampai tanggal)
- Keterangan

Status: Selesai diimplementasikan.
- Backend `tr_monitoring_pi` tersinkronisasi otomatis dengan RTP Form 7 (`rencana_tindak`), kolom `risiko_id`, `rencana_mulai`, dan `rencana_selesai`.
- Frontend Form9.vue menampilkan tabel RTP dan modal dialog form entri.

### Penggabungan Respon Risiko (RTP), Form 8 — Informasi & Komunikasi, dan Form 9 — Rencana Pemantauan PI
- **Tampilan Terpadu (Form 7 / Respon Risiko)**:
  - Tabel menampilkan risiko prioritas beserta ringkasan Respon Risiko (RTP), Informasi & Komunikasi, serta Rencana Pemantauan PI.
  - Kolom **Aksi** pada tabel menggunakan dropdown popup menu (`PrimeVue Menu`):
    - `Respon Risiko`: membuka dialog modal pengisian Respon Risiko (RTP)
    - `Informasi & Komunikasi`: membuka dialog modal pengisian Form 8 (Media/Bentuk Sarana, Penyedia Informasi, Penerima Informasi, Rencana Waktu range, Keterangan)
    - `Rencana Pemantauan PI`: membuka dialog modal pengisian Form 9 (Bentuk/Metode Pemantauan, Penanggung Jawab, Rencana Waktu range, Keterangan)
- **Sinkronisasi Backend & Database**:
  - `GET /risiko/rtp` memuat data gabungan `rtp`, `infokom`, dan `monitoring_pi` per risiko prioritas dalam satu panggilan.
  - Form dialog masing-masing terhubung ke API backend (`/risiko/rtp`, `/monitoring/infokom`, `/monitoring/pi`) sehingga data tersimpan ke tabel `tr_infokom` dan `tr_monitoring_pi` untuk kompatibilitas cetak & laporan.
- **Navigasi & Routing**:
  - Rute `/form8` dan `/form9` dialihkan (redirect) ke `/form7`, dan menu sidebar disederhanakan.
- **Revamp Tampilan (UI/UX Visual Excellence)**:
  - Hero banner bergradasi modern dengan deskripsi jelas dan tombol aksi segarkan data.
  - Kartu KPI ringkasan progres kelengkapan: Total Risiko Prioritas, RTP Terisi, Info & Komunikasi Terisi, dan Pemantauan PI Terisi dengan indikator persentase penyelesaian.
  - Toolbar pencarian interaktif instan (kode, uraian, pemilik, tindak lanjut, media, metode) dan filter multi-status (Semua, Perlu Dilengkapi, Lengkap 3/3, atau per formulir).
  - Tabel terpadu dengan tipografi modern, badge kode & jenis risiko, level risiko berwarna standar, serta kartu status ringkas untuk Form 8 dan Form 9.
  - Shortcut langsung pada tabel (tombol dashed "+ Isi") serta menu dropdown "Aksi" pada setiap baris.
  - Desain modal dialog bertema khusus (RTP = Indigo, Form 8 = Teal, Form 9 = Purple) dilengkapi konteks risiko prioritas di bagian atas.
- Status: **Selesai diimplementasikan dan direvamp penuh**.

Buat Menu Baru Treated Risk
Level Treated Risk adalah tingkat risiko setelah adanya kegiatan pengendalian. Jadi, nilai risiko melekat (inheren) yang kemudian nilainya bisa bergeser/berkurang apabila terdapat kegiatan pengendalian terpasang (existing control), nilainya akan kembali terkoreksi setelah adanya Rencana Tindak Pengendalian.

Catatan :
a.Pada saat menetapkan tingkat kemungkinan maupun dampak, agar disesuaikan dengan karakteristik Rencana Tindak Pengendalian (RTP), apakah RTР tersebut memiliki karakteristik mengurangi kemungkinan, mengurangi dampak atau mengurangi kemungkinan dan dampak.
b.Selain itu, pastikan untuk melihat tabel dampak dan tabel kemungkinan yang ada dalam Kebijakan Manajemen Risiko masing-masing untuk membantu akurasi penetapan tingkat kemungkinan dan dampak setelah adanya RTP.

Buat Menu Baru Realisasi RTP
Apabila Rencana Tindak Pengendalian sudah direalisasikan, 
maka unggah berkas bukti dukung pelaksanaan realisasi RTP dan isi tanggal realisasi



Form entri Form 6 — RTP atas CEE
field target waktu, ganti dengan datepicker dari tangal sampai tanggal
sembunyikan field realisasi


Realisasi Rencana Tindak Pengendalian (RTP), tambahkan juga data dari RTP atas CEE


revamp semua tampilan data tabel supaya seragam, 
tabel header #f8fafc, 
border 1px solid #e2e8f0,
stripped / zebra style 

Status: **Selesai diimplementasikan secara menyeluruh**.
- Preset tema PrimeVue (`AppPreset` di `main.js`) dikonfigurasi dengan `headerCell.background: #f8fafc`, `borderColor: #e2e8f0`, dan `row.stripedBackground: #f8fafc`.
- Standar global CSS di `style.css` diterapkan secara authoritative:
  - Seluruh PrimeVue DataTable (`.p-datatable`): header `#f8fafc` tebal (font-weight 600), seluruh border sel `1px solid #e2e8f0`, alternating zebra rows (`#ffffff` & `#f8fafc`), dan hover row highlight (`#f1f5f9`).
  - Form HTML Grid Tables (`.grid-table` pada Form 1a, 1b, 1c, 4, 5, 10): header `#f8fafc`, border `1px solid #e2e8f0`, dan zebra rows.
  - Rekapitulasi Tables (`.rekap-table` pada seluruh 7 komponen Rekapitulasi): header `#f8fafc`, border `1px solid #e2e8f0`, dan zebra rows.
  - Table Wrappers & Reports (`.table-wrap table`, `table.rpt`, `table.history`): diseragamkan dengan header `#f8fafc`, border `1px solid #e2e8f0`, dan zebra rows. 
