-- Migration: tabel pengaturan aplikasi (tahun default & jadwal survei CEE)
-- Tanggal   : 2026-07-29
--
-- Satu baris saja (id = 1). Dibuat otomatis oleh SQLModel.create_all lewat
-- init_db(), skrip ini untuk penerapan manual di server.
--
-- Jalankan: psql "<database_url>" -f migrations/2026_07_29_pengaturan.sql

BEGIN;

CREATE TABLE IF NOT EXISTS tr_pengaturan (
    id                  integer PRIMARY KEY,
    tahun_default       integer,
    survei_mulai        date,
    survei_selesai      date,
    survei_aktif        integer NOT NULL DEFAULT 1,
    survei_pesan_tutup  varchar,
    updated_at          timestamp without time zone NOT NULL DEFAULT now(),
    updated_by          varchar
);

-- Baris awal; tahun_default dibiarkan null = ikut TAHUN_ANGGARAN pada .env.
INSERT INTO tr_pengaturan (id, survei_aktif)
VALUES (1, 1)
ON CONFLICT (id) DO NOTHING;

COMMIT;
