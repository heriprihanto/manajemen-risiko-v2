-- Migration: satu email hanya boleh mengisi survei satu kali per tahun.
-- Tanggal   : 2026-07-27
--
-- Unique index PARSIAL: berlaku hanya untuk baris hasil survei publik
-- (sumber = 'survei') yang punya email. Baris admin (sumber='admin',
-- kode R1..Rn manual) tidak terpengaruh. Case-insensitive via lower(email).
--
-- Jalankan: psql "<database_url>" -f migrations/2026_07_27_cee_responden_email_unique.sql
--
-- Bila gagal karena sudah ada duplikat, bersihkan dulu, mis. cek:
--   SELECT lower(email), tahun, count(*)
--   FROM tr_cee_responden
--   WHERE sumber='survei' AND email IS NOT NULL
--   GROUP BY 1,2 HAVING count(*) > 1;

CREATE UNIQUE INDEX IF NOT EXISTS ux_cee_responden_email_tahun_survei
    ON tr_cee_responden (lower(email), tahun)
    WHERE sumber = 'survei' AND email IS NOT NULL;
