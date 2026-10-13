# Walkthrough: Revisi Identifikasi Risiko & Dashboard Eksekutif Summary 2026

## 1. Revisi Dashboard: Executive Summary & Interactive Heatmap 4×4

Halaman Dashboard ([`FrontEnd/src/views/Dashboard.vue`](file:///home/herry/1_Project/2026/MANAJEMEN_RISIKO_2026/FrontEnd/src/views/Dashboard.vue)) dan API Summary ([`BackEnd/app/routers/dashboard.py`](file:///home/herry/1_Project/2026/MANAJEMEN_RISIKO_2026/BackEnd/app/routers/dashboard.py)) telah dirombak menyeluruh menjadi **Executive Summary Manajemen Risiko** yang lengkap, informatif, dan interaktif:

### Fitur Utama Dashboard Baru:
1. **Executive Header**:
   - Menampilkan identitas Perangkat Daerah (OPD), tahun penilaian aktif (2026), status kepatuhan, tombol *Segarkan*, dan tautan cepat ke *Form 7 (RTP)*.
2. **6 Kartu Eksekutif (KPI Stat Cards)**:
   - **Total Risiko Teridentifikasi**: Breakdown risiko Strategis Pemda vs Risiko OPD.
   - **Progres Analisis (Form 4)**: Persentase risiko yang telah dinilai kemungkinan & dampaknya dengan visual progress bar.
   - **Risiko Prioritas**: Jumlah risiko berlevel Tinggi & Sangat Tinggi yang memerlukan mitigasi.
   - **Tindak Pengendalian (RTP)**: Rasio risiko prioritas yang telah memiliki RTP vs belum memiliki RTP (peringatan merah jika ada yang belum).
   - **Profil Kendali (C / UC)**: Rasio risiko *Controllable* (bisa dikendalikan OPD) vs *Uncontrollable* (perlu koordinasi lintas pemda).
   - **Responden Kuesioner CEE**: Partisipasi survei Lingkungan Pengendalian OPD.
3. **Smart Executive Recommendations Engine (Rekomendasi Strategis Eksekutif)**:
   - Alert rekomendasi otomatis berbasis data riil dengan 4 tingkatan urgensi:
     - **Kritis (Merah)**: Jika terdapat risiko prioritas yang belum memiliki Rencana Tindak Pengendalian (Form 7) + tombol aksi langsung menuju penyusunan RTP.
     - **Perhatian (Kuning)**: Peringatan untuk risiko *Uncontrollable* (UC) berdampak tinggi yang membutuhkan eskalasi atau contingency plan, serta peringatan risiko yang belum dianalisis (Form 4).
     - **Informasi (Biru/Ungu)**: Rekomendasi mitigasi berdasarkan Kategori Risiko dominan (Kamus Risiko) dan status survei CEE.
     - **Sukses (Hijau)**: Konfirmasi bila seluruh risiko prioritas telah terlindungi RTP.
4. **Matriks Analisis Risiko Interaktif (Heatmap 4×4 BPKP)**:
   - Sumbu Y: Skala Kemungkinan 4 (Hampir Pasti), 3 (Sering), 2 (Kadang-kadang), 1 (Jarang).
   - Sumbu X: Skala Dampak 1 (Rendah), 2 (Sedang), 3 (Besar), 4 (Sangat Besar).
   - Penataan warna gradasi standar BPKP:
     - Merah: Sangat Tinggi (Skor 12 – 16)
     - Oranye: Tinggi (Skor 8 – 9)
     - Kuning: Sedang (Skor 4 – 6)
     - Hijau: Rendah (Skor 1 – 3)
   - Filter jenis risiko: *Semua*, *Form 3.a (Strategis Pemda)*, *Form 3.b (Strategis OPD)*, *Form 3.c (Operasional OPD)*.
   - **Interaktif Drill-Down**: Mengklik kotak sel pada heatmap langsung membuka modal dialog PrimeVue yang menampilkan seluruh risiko di sel tersebut, lengkap dengan kode risiko, uraian, kategori, pemilik, status RTP, dan tautan langsung ke Form Analisis.
5. **Sebaran Komposisi Risiko**:
   - **Sebaran Level Risiko**: Progress bar persentase level Sangat Tinggi, Tinggi, Sedang, dan Rendah.
   - **Sebaran Kategori Risiko (Kamus Risiko)**: Breakdown 6 kategori risiko terbanyak.
6. **Pipeline Roadmap Tahapan SPIP (6 Langkah)**:
   - Visualisasi tahapan manajemen risiko terintegrasi:
     1. Lingkungan Pengendalian (CEE)
     2. Penetapan Konteks
     3. Identifikasi Risiko
     4. Analisis & Evaluasi
     5. Rencana Tindak Pengendalian (RTP)
     6. Pemantauan & Evaluasi
   - Menampilkan status (Selesai / Proses / Belum) dan tautan langsung ke formulir terkait.
7. **Top 10 Risk Register (Risiko Prioritas Utama)**:
   - Tabel prioritas utama dengan kolom: Kode Risiko, Uraian Risiko, Kategori & C/UC, Dampak × Kemungkinan, Skor & Badge Level, Status RTP (Sudah / Belum), dan Pemilik / Rencana Tindak Pengendalian.

---

## 2. Revisi Identifikasi Risiko Form 3.a, Form 3.b & Form 3.c

1. **Kategori Risiko Read-Only (Otomatis dari Kamus Risiko)**:
   - Kolom `kategori_risiko` tersimpan di database (`tr_risiko`).
   - Pada form dialog entri risiko, field **Kategori Risiko** bersifat **read-only** (hanya baca).
   - Nilai field Kategori Risiko terisi secara otomatis ketika pengguna memilih atau mengetik uraian risiko yang cocok dengan entri pada **Kamus Risiko**.
   - Kolom **Kategori** ditampilkan di tabel data dengan badge warna kategori.
2. **Format Penomoran Kode Risiko Otomatis**:
   - **Form 3.a (Strategis Pemda)**: `RSP.26.00.01.001` (selalu kode `01` untuk Pemda)
   - **Form 3.b (Strategis OPD)**: `RSO.26.00.05.001` (`05` = kode risiko OPD dari `ta_opd`)
   - **Form 3.c (Operasional OPD)**: `ROO.26.00.05.001` (`05` = kode risiko OPD dari `ta_opd`)
3. **Combobox Bidang Urusan**:
   - Tersedia di seluruh form identifikasi risiko (Form 3.a, 3.b, dan 3.c) bersumber dari tabel referensi `ref_bidang_urusan`.
   - Mengubah pilihan Bidang Urusan langsung memperbarui Kode Risiko secara dinamis.
   - Kolom **Bidang Urusan** tampil pada tabel data untuk semua form identifikasi.

---

## Verifikasi & Pengujian
- **Frontend Build**: `npm run build` berhasil dikompilasi 100% tanpa error (`dist/assets/Dashboard-Sta_mvGZ.js` dan CSS siap saji).
- **Backend API**: Endpoint `GET /api/dashboard/summary` terintegrasi lengkap dengan data agregasi, heatmap cells, top prioritas, rekomendasi cerdas, dan tahapan progress.
