-- Migration: kolom prioritas pembangunan daerah pada konteks strategis Pemda
-- Tanggal   : 2026-07-28
--
-- Revisi Form 2.a memisahkan "Prioritas Pembangunan Daerah" (ref_prioritas)
-- dari "Program Prioritas" (rpjmd_program). Kolom lama `prioritas_program`
-- dipakai untuk Program Prioritas, kolom baru untuk prioritas pembangunan.
--
-- Jalankan: psql "<database_url>" -f migrations/2026_07_28_konteks_pemda_prioritas.sql

BEGIN;

-- tr_konteks_strategis_pemda (app/models/konteks.py) -- Form 2.a
ALTER TABLE tr_konteks_strategis_pemda
    ADD COLUMN IF NOT EXISTS prioritas_pembangunan varchar;

COMMIT;
