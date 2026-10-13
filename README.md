# Web App Manajemen Risiko — Pemerintah Kota Tegal

Aplikasi penyelenggaraan **Manajemen Risiko SPIP**, hasil transformasi dari
`Kertas Kerja Manajemen Risiko.xls` menjadi aplikasi web per OPD (Organisasi
Perangkat Daerah).

- **Backend**: Python · FastAPI · SQLModel/SQLAlchemy · PostgreSQL
- **Frontend**: Vue 3 · PrimeVue (Vite)
- **Data**: per OPD (`ta_opd`) dan per Tahun Penilaian
- **Dokumentasi & Panduan Pengguna**: [MANUAL_BOOK.md](MANUAL_BOOK.md)

## Alur / Form yang didukung

| Menu | Sumber Excel | Keterangan |
|------|--------------|-----------|
| Dashboard | — | Ringkasan responden, jumlah & level risiko, prioritas |
| Form 1.a Kuesioner | `Form 1.a CEE persepsi` + `KUESIONER` | Input responden **R1..Rn dinamis** & jawaban 1–4, **modus** & simpulan otomatis |
| Form 1.b Reviu Dokumen | `Form 1.b` | Penilaian Memadai/Kurang Memadai per aspek |
| Form 1.c Simpulan CEE | `Form 1.c` | Gabungan persepsi + dokumen (otomatis) |
| Form 6 RTP atas CEE | `Form 6 RTP CE` | Rencana tindak pengendalian lingkungan |
| Form 2.a/2.b/2.c Konteks | `Form 2a/2b/2c` | Konteks strategis Pemda / strategis OPD / operasional OPD |
| Form 3 Identifikasi | `Form 3a/3b/3c` | Identifikasi risiko strategis Pemda, strategis OPD, operasional OPD |
| Form 4 Analisis | `Form 4` | Skala dampak × kemungkinan → skala & level risiko |
| Matriks Risiko | `Matrik Risiko` | Heatmap 4×4 sebaran risiko |
| Form 5 Prioritas | `Form 5` | Daftar risiko prioritas (skala > 4) — otomatis |
| Form 7 RTP Risiko | `Form 7` | RTP atas risiko prioritas |
| Form 8 Info & Komunikasi | `Form 8` | Pengkomunikasian pengendalian |
| Form 9 Rencana Pemantauan | `Form 9` | Pemantauan kegiatan pengendalian |
| Form 10 Monitoring Event | `Form 10` | Pencatatan kejadian risiko & realisasi RTP |
| Cetak Laporan | semua | Print preview / cetak ke PDF, pilih form |
| **Survei Publik** (`/survei`) | `Form 1.a` | Form kuesioner CEE untuk responden terdaftar, akses token tanpa login |

## Survei Publik (Token Undangan)

Admin mendaftarkan calon responden melalui Form 1.a, secara manual atau impor
Excel, lalu mengirim email berisi tautan dan token pribadi. Responden membuka
`/survei` tanpa login, memasukkan token, dan mengirim jawaban satu kali. OPD dan
tahun mengikuti undangan. Pengiriman WhatsApp dinonaktifkan.

Panduan lengkap tersedia di [Dokumentasi Perubahan Alur Kuesioner CEE](docs/PERUBAHAN_FLOW_KUESIONER_CEE.md).

### Logika perhitungan utama
- **Simpulan kuesioner**: simpulan pertanyaan *Memadai* bila **modus** jawaban 3/4,
  *Kurang Memadai* bila 1/2. Sub-unsur *Memadai* bila seluruh pertanyaannya Memadai.
- **Skala risiko** = skala dampak (1–4) × skala kemungkinan (1–4). Level: Rendah (1–3),
  Sedang (4–6), Tinggi (8–9), Sangat Tinggi (12–16). Risiko **prioritas** bila skala > 4.

## Menjalankan

### 1. Backend (port 8077)
Konfigurasi database ada di `BackEnd/.env` (target: `db_manajemen_risiko`).

```bash
cd BackEnd
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python init_db.py     # buat tabel + seed kuesioner + salin ta_opd (sekali saja)
./run.sh                        # atau: .venv/bin/uvicorn app.main:app --reload --port 8077
```
Dokumentasi API: http://localhost:8077/docs

> `init_db.py` menyalin master OPD dari database `manajemen_risiko` (server yang sama)
> bila tabel `ta_opd` di database target masih kosong.

### 2. Frontend (port 5173)
```bash
cd FrontEnd
npm install
npm run dev
```
Buka http://localhost:5173 — pilih **OPD** dan **Tahun** di kanan atas; seluruh form
mengikuti konteks tersebut. Vite mem-proxy `/api` ke backend `:8077`.

## Struktur
```
BackEnd/
  app/
    core/config.py        # baca .env
    db.py                 # engine + session
    models/               # SQLModel: master, cee, konteks, risiko, monitoring
    services/             # cee.py (modus/simpulan), analisis.py (skala/level/matriks)
    routers/              # master, cee, konteks, risiko, monitoring, dashboard
    seed_data.py          # 8 kategori + 37 pertanyaan CEE (dari Excel)
  init_db.py
FrontEnd/
  src/
    stores/context.js     # OPD + Tahun aktif (persist localStorage)
    components/CrudTable.vue
    views/                # Dashboard + Form1a..Form10, Matriks
```

### Survei CEE melalui token undangan

Admin membuka **Form 1.a**, memilih OPD dan tahun, lalu menambah calon responden
berisi NIP, nama, jabatan, email, dan no HP. Token pribadi dibuat otomatis saat
penyimpanan. Data lama yang belum lengkap dapat diperbaiki melalui tombol Edit.
NIP atau email yang sudah terdaftar pada tahun yang sama ditolak.

Tombol **Kirim Email Undangan** mengirim tautan survei dan token ID kepada semua
responden yang belum mengisi pada OPD/tahun terpilih. Hasil pengiriman ditampilkan
per batch, termasuk nama responden yang gagal. Menekan tombol kembali akan
mengirim ulang undangan kepada responden yang belum mengisi. Status terkirim
berarti server SMTP menerima email, bukan jaminan email sudah masuk kotak masuk.

Responden membuka tautan `/survei`, memasukkan token dari email tanpa login,
dan menjawab seluruh pertanyaan. Identitas, OPD, serta tahun mengikuti undangan.
Jawaban disimpan sekali dalam satu transaksi; token yang sudah digunakan hanya
menampilkan hasil. Jadwal dan tahun aktif tetap mengikuti Pengaturan aplikasi.
Mengubah email calon responden akan mengganti token dan memerlukan pengiriman
ulang undangan. Token tidak dikembalikan dalam API daftar atau rekap responden.

Konfigurasi SMTP dan URL publik tersedia pada `BackEnd/.env.survei.example`.
Salin nilai yang sesuai ke `BackEnd/.env`, lalu restart backend. Untuk SMTP port
465, gunakan `SMTP_SSL=true` dan `SMTP_STARTTLS=false`. Kolom baru dan indeks
token ditambahkan otomatis oleh `init_db()` saat startup; data lama dipertahankan.
Pengiriman email membutuhkan konfigurasi SMTP yang berfungsi.

Verifikasi lokal (tanpa mengirim email sungguhan):

```sh
cd BackEnd
.venv/bin/python -m unittest discover -s tests -v
```

Pengujian menggunakan SQLite sementara dan SMTP mock. Penguncian submit serentak
menggunakan `SELECT FOR UPDATE` di PostgreSQL; skenario konkurensi PostgreSQL dan
pengiriman melalui SMTP nyata perlu diverifikasi di lingkungan deployment.

Pengiriman undangan WhatsApp dinonaktifkan. Tombol **Kirim Email Undangan**
hanya mengirim email kepada responden yang belum mengisi. Konfigurasi gateway
dan riwayat WhatsApp lama tetap tersimpan, tetapi tidak digunakan untuk pengiriman.

