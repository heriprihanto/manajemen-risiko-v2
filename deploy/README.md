# Deploy — Manajemen Risiko (SPIP) Kota Tegal

Aplikasi dilayani di sub-path:
**https://monevrkpd.tegalkota.go.id/manajemen-risiko/**

- Frontend: Vue SPA (Vite), base `/manajemen-risiko/`
- Backend: FastAPI/uvicorn di `127.0.0.1:8077` (prefix internal `/api`)
- Nginx me-reverse-proxy `/manajemen-risiko/api/` → backend (mengupas prefix)

## Berkas di folder ini
| Berkas | Fungsi |
|---|---|
| `apache-manajemen-risiko.conf` | Blok VirtualHost untuk **Apache httpd** (reverse proxy) |
| `nginx-manajemen-risiko.conf` | Blok `location` (dan contoh `server{}`) untuk Nginx |
| `manajemen-risiko-api.supervisor.conf` | Program **Supervisor** untuk backend uvicorn |
| `manajemen-risiko-api.service` | systemd unit (alternatif Supervisor) |

> Pilih **salah satu** web server (Apache **atau** Nginx) dan **salah satu**
> process manager (Supervisor **atau** systemd).

## Langkah deploy

### 1. Backend
```bash
cd BackEnd
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # bila ada; isi kredensial POSTGRES_*, SECRET_KEY, dll.
.venv/bin/python init_db.py            # buat tabel + seed (sekali di awal)
# migrasi kolom tambahan (idempotent):
psql "$DATABASE_URL" -f migrations/2026_07_27_konteks_ref_columns.sql
# unique index: satu email hanya boleh mengisi survei sekali per tahun
psql "$DATABASE_URL" -f migrations/2026_07_27_cee_responden_email_unique.sql
```
Jalankan sebagai service — **Supervisor** (utama):
```bash
sudo apt install supervisor   # bila belum ada
sudo cp deploy/manajemen-risiko-api.supervisor.conf \
        /etc/supervisor/conf.d/manajemen-risiko-api.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status manajemen-risiko-api
# restart setelah update kode: sudo supervisorctl restart manajemen-risiko-api
```

Alternatif **systemd**:
```bash
sudo cp deploy/manajemen-risiko-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now manajemen-risiko-api
systemctl status manajemen-risiko-api
```

### 2. Frontend
```bash
cd FrontEnd
npm ci
npm run build          # menghasilkan dist/ dengan base /manajemen-risiko/
sudo mkdir -p /var/www/manajemen-risiko
sudo cp -r dist /var/www/manajemen-risiko/dist
```

### 3. Web server (pilih salah satu)

**Apache httpd** (sesuai lingkungan saat ini):
```bash
sudo a2enmod proxy proxy_http headers rewrite expires deflate
```
Sisipkan blok dari `apache-manajemen-risiko.conf` ke `<VirtualHost *:443>`
domain `monevrkpd.tegalkota.go.id`, lalu:
```bash
sudo apachectl configtest && sudo systemctl reload apache2
```

**Nginx** (alternatif):
Sisipkan dua blok `location` dari `nginx-manajemen-risiko.conf` ke dalam
`server{}` domain, lalu:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## Verifikasi
- `https://monevrkpd.tegalkota.go.id/manajemen-risiko/` → halaman login tampil.
- `.../manajemen-risiko/api/auth/captcha` → JSON `{id, svg}` (backend hidup).
- Refresh di halaman dalam (mis. `/manajemen-risiko/form4`) tidak 404 (SPA fallback OK).

## Catatan
- **Satu origin** (frontend & API di domain yang sama) → tidak perlu CORS khusus.
- Bila backend dipindah ke origin/host lain: set `VITE_API_BASE` saat build
  (lihat `FrontEnd/.env.production`) dan tambahkan origin frontend ke
  `BACKEND_CORS_ORIGINS` di `BackEnd/.env`.
- Bila reverse-proxy TIDAK mengupas prefix (backend menerima
  `/manajemen-risiko/api/...`), set `root_path="/manajemen-risiko/api"` pada
  `FastAPI(...)` di `app/main.py`.
- Backend memakai penyimpanan captcha in-memory → jalankan uvicorn **satu worker**
  (default unit ini). Untuk multi-worker, ganti store captcha ke Redis.
