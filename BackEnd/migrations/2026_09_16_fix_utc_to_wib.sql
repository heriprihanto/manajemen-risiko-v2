-- Migrasi penyesuaian data timestamp yang sebelumnya tersimpan dalam UTC (datetime.utcnow)
-- menjadi waktu lokal Waktu Indonesia Barat (WIB / Asia/Jakarta, +7 jam).

BEGIN;

UPDATE tr_cee_responden
SET created_at = created_at + interval '7 hours',
    updated_at = updated_at + interval '7 hours';

UPDATE tr_pengaturan
SET updated_at = updated_at + interval '7 hours';

UPDATE tr_cee_dokumen_nilai
SET updated_at = updated_at + interval '7 hours';

UPDATE tr_analisis_risiko
SET updated_at = updated_at + interval '7 hours';

UPDATE tr_risiko
SET created_at = created_at + interval '7 hours',
    updated_at = updated_at + interval '7 hours';

COMMIT;
