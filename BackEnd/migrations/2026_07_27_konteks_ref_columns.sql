-- Migration: kolom referensi konteks operasional & sumber konteks risiko
-- Tanggal   : 2026-07-27
--
-- create_all tidak mengubah tabel yang sudah ada, jadi kolom baru pada
-- model diterapkan lewat ALTER idempotent (aman dijalankan berulang).
--
-- Jalankan: psql "<database_url>" -f migrations/2026_07_27_konteks_ref_columns.sql

BEGIN;

-- tr_risiko (app/models/risiko.py) -- Form 3.b: referensi baris sumber konteks
ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS konteks_id integer;
ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS konteks_sumber varchar;

-- tr_konteks_operasional_opd (app/models/konteks.py) -- Form 2.c
ALTER TABLE tr_konteks_operasional_opd ADD COLUMN IF NOT EXISTS indikator_program varchar;
ALTER TABLE tr_konteks_operasional_opd ADD COLUMN IF NOT EXISTS ref_subkegiatan varchar;
ALTER TABLE tr_konteks_operasional_opd ADD COLUMN IF NOT EXISTS ref_indikator varchar;

CREATE INDEX IF NOT EXISTS ix_tr_risiko_konteks_id
    ON tr_risiko (konteks_id);
CREATE INDEX IF NOT EXISTS ix_tr_konteks_operasional_opd_ref_subkegiatan
    ON tr_konteks_operasional_opd (ref_subkegiatan);
CREATE INDEX IF NOT EXISTS ix_tr_konteks_operasional_opd_ref_indikator
    ON tr_konteks_operasional_opd (ref_indikator);

COMMIT;
