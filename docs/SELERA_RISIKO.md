# Selera Risiko

Menu **Pengelolaan Risiko → Selera Risiko** mencatat ambang yang ditetapkan Pemilik Risiko berdasarkan sumber daya entitas/unit kerja.

1. Pilih OPD dan tahun pada bagian atas aplikasi.
2. Ketetapan pada form otomatis berlaku pada tingkat entitas/OPD dan tahun terpilih.
3. Pilih bilangan bulat 1–nilai maksimum matriks. Matriks aplikasi saat ini 5×5, sehingga maksimum 25.
4. Isi pertimbangan sumber daya: SDM, anggaran, sarana, kemampuan pengendalian. Referensi dokumen opsional. Akun pencatat tersimpan otomatis; nama/jabatan penetap tidak perlu diisi.
5. Periksa pratinjau dan simpan ketetapan.

Ketetapan khusus pemilik yang sudah tersimpan tetap mengesampingkan ketetapan entitas. Form saat ini hanya mengelola ketetapan entitas. Nama pemilik dicocokkan tanpa membedakan huruf besar/kecil dan spasi berulang. Pengelola OPD dengan hak tulis mencatat keputusan; nama pemilik pada register belum terhubung dengan akun SSO. Penugasan pemantauan saja tidak memberi hak mengubah ketetapan.

## Aturan penerimaan

- Skor **≤ ambang** berada dalam area penerimaan dan tidak memerlukan pengendalian tambahan.
- Skor **> ambang** memerlukan pengendalian dan masuk daftar prioritas.
- Ambang 1 menerima skor 1 saja; ambang 25 menerima seluruh skor pada matriks sekarang.
- Warna level tetap mengikuti skala matriks, terpisah dari ambang penerimaan.
- Tanpa ketetapan, status penerimaan belum ditentukan dan penilaian baru belum dapat disimpan. Tidak ada pengisian otomatis dari aturan lama.

Prioritas pada Form Analisis dihitung otomatis. Matriks menampilkan garis batas sesuai ambang; bila ambang antar pemilik berbeda, pilih pemilik untuk menampilkan garisnya. Dashboard gabungan tidak menggambar satu garis yang menyesatkan untuk ambang yang berbeda.

## Perubahan dan riwayat

Setiap penyimpanan membuat versi baru, mencatat waktu serta akun pencatat, dan memperbarui prioritas analisis saat ini. Ketetapan entitas tidak menimpa ketetapan khusus pemilik. Riwayat awal/target/residual menyimpan salinan ketetapan pada saat penilaian. Laporan berkala menyimpan seluruh ketetapan aktif sumber laporan.

Perubahan tidak menghapus RTP, tindakan, riwayat penilaian, atau laporan tersimpan. Jika risiko keluar dari prioritas, RTP lama masih dapat dilihat melalui detail risiko/laporan. Pengajuan dan persetujuan respons memerlukan penilaian menggunakan versi ketetapan yang masih berlaku. Alur keputusan respons tetap mengikuti penugasan yang ada.

Tabel `mr_selera_risiko` dibuat melalui `init_db()` saat backend dimulai. Jalankan ulang backend setelah pembaruan dan gunakan hasil build frontend. Data lama tidak diberi ambang secara otomatis; Pemilik Risiko perlu menetapkannya untuk setiap OPD/tahun yang digunakan.

## Verifikasi pengembangan

Pengujian API: 50 skenario pada SQLite (47 lulus, 3 khusus PostgreSQL dilewati); seluruh 32 skenario tata kelola pada PostgreSQL sementara lulus, termasuk pembaruan ambang bersamaan dengan penilaian. Browser diperiksa dengan data sintetis untuk pratinjau ambang 1/25, simpan dan muat ulang, prioritas otomatis, matriks/dashboard, keutuhan laporan lama, dan tampilan ponsel. Build frontend berhasil.
