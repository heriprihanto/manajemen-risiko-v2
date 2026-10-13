-- Migrasi penambahan kolom kategori_risiko pada tr_risiko untuk Form 3.a / 3.b / 3.c
ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS kategori_risiko character varying(150);
