INSERT INTO renja_subkegiatan (
        idsubkegiatan,
        id_sub_kegiatan,
        tahun,
        id_sub_pd,
        kode_bidang_urusan,
        kode_program,
        kode_kegiatan,
        kode_sub_kegiatan,
        nm_program,
        nm_kegiatan,
        nm_sub_kegiatan,
        anggaran,
        id_pd,
        kodeskpd
) 
SELECT  
        uuid_generate_v7(),
        id_sub_giat,
        tahun,
        id_sub_skpd,
        kode_bidang_urusan,
        kode_program,
        kode_giat,
        kode_sub_giat,
        nama_program,
        nama_giat,
        nama_sub_giat,
        rincian,
        id_unit,
        kode_sub_skpd
FROM sipdri_subkegiatan WHERE tahun=2027;


WITH program_group AS (
    SELECT
        id_sub_pd,
        kode_program,
       uuid_generate_v7() as idprogram_baru
    FROM renja_subkegiatan
    WHERE kode_program IS NOT NULL AND tahun=2027
    GROUP BY
        id_sub_pd,
        kode_program
)
UPDATE renja_subkegiatan r
SET idprogram = g.idprogram_baru
FROM program_group g
WHERE r.id_sub_pd = g.id_sub_pd
  AND r.kode_program = g.kode_program
  AND r.tahun=2027;


WITH program_group AS (
    SELECT
        id_sub_pd,
        kode_program,
        kode_kegiatan,
       uuid_generate_v7() as idkegiatan_baru
    FROM renja_subkegiatan
    WHERE kode_program IS NOT NULL AND tahun=2027
    GROUP BY
        id_sub_pd,
        kode_program,
        kode_kegiatan
)
UPDATE renja_subkegiatan r
SET idkegiatan = g.idkegiatan_baru
FROM program_group g
WHERE r.id_sub_pd = g.id_sub_pd
  AND r.kode_program = g.kode_program
  AND r.kode_kegiatan = g.kode_kegiatan
  AND r.tahun=2027;




INSERT INTO renja_indikator (
  id,
  lvl,
  id_parent,
  tahun,
  id_sub_pd,
  kode,
  nomor,
  tolok_ukur,
  satuan,
  idformula,
  idjenis,
  iskota,
  target,
  tipedata
)
SELECT 
	uuid_generate_v7() as id,
    7 as lvl,
	sk.idsubkegiatan,
    sk.tahun,
    sk.id_sub_pd,
    1 as kode,
    1 as nomor,
    o.tolak_ukur,
	o.satuan,
	1 as idformula,
	1 as idjenis,
	0 as iskota,
    o.target,
    1 as tipedata
FROM
  public.sipdri_subkegiatan_output o
  INNER JOIN public.renja_subkegiatan sk ON (o.tahun = sk.tahun)
  AND (o.id_sub_skpd = sk.id_sub_pd)
  AND (o.id_sub_giat = sk.id_sub_kegiatan)
  WHERE sk.tahun=2027;


INSERT INTO renja_indikator (
  id,
  lvl,
  id_parent,
  tahun,
  id_sub_pd,
  kode,
  nomor,
  tolok_ukur,
  satuan,
  idformula,
  idjenis,
  iskota,
  target,
  tipedata
)
SELECT 
uuid_generate_v7() as id,
5 as lvl,
sk.idprogram as  id_parent,
sk.tahun,
  sk.id_sub_pd,
  ip.urut as kode,
  ip.no as nomor,
  ip.uraiindikator as tolok_ukur,
  ip.satuan,
  1 as idformula,
  1 as idjenis,
  0 as iskota,
  ip.target2 as target,
  1 as tipedata
FROM
  public.renstra_indikator_program ip
  INNER JOIN (SELECT DISTINCT s.idprogram,s.kodeskpd,s.kode_program,s.id_sub_pd,s.tahun FROM  public.renja_subkegiatan s WHERE s.tahun=2027) sk ON (ip.kodeskpd = sk.kodeskpd)
  AND (ip.kodeprogram = sk.kode_program)





