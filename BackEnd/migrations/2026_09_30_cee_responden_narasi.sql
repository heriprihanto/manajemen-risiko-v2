-- Tambah kolom narasi pada tr_cee_responden (narasi lain terkait kondisi lingkungan pengendalian pada survei CEE)
ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS narasi TEXT;
