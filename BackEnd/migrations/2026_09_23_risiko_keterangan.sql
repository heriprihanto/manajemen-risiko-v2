-- Tambah kolom keterangan_risiko pada tr_risiko (Keterangan Uraian Risiko Form 3.a/3.b/3.c)
ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS keterangan_risiko TEXT;
