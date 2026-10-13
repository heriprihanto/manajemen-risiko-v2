-- Migrasi penambahan kolom id_bidang_urusan pada tr_risiko untuk Form 3.b
ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS id_bidang_urusan integer;
