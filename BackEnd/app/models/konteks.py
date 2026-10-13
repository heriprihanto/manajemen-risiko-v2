"""Penetapan konteks risiko — Form 2a (Pemda), 2b (Strategis OPD), 2c (Operasional OPD)."""
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.datetime_utils import now_wib


class KonteksStrategisPemda(SQLModel, table=True):
    """Form 2a — penetapan konteks risiko strategis pemerintah daerah (per tahun).

    Field pilihan RPJMD (misi, tujuan, sasaran, IKU, prioritas, program) boleh
    berisi lebih dari satu nilai; disimpan sebagai teks pilihan yang dipisah
    newline agar tetap terbaca apa adanya di laporan.
    """
    __tablename__ = "tr_konteks_strategis_pemda"

    id: int | None = Field(default=None, primary_key=True)
    tahun: int = Field(index=True)
    periode_dinilai: str | None = None       # 'RPJMD 2025 - 2029'
    visi: str | None = None                  # rpjmd_visi
    misi_strategis: str | None = None        # rpjmd_misi (multi)
    penetapan_konteks_tujuan: str | None = None   # rpjmd_tujuan (multi)
    penetapan_konteks_sasaran: str | None = None  # rpjmd_sasaran (multi)
    penetapan_konteks_iku: str | None = None      # renja_indikator lvl<3, iku=1 (multi)
    prioritas_pembangunan: str | None = None      # ref_prioritas (multi)
    prioritas_program: str | None = None          # rpjmd_program — Program Prioritas (multi)
    # Kolom lama sebelum revisi Form 2.a; tidak lagi dientri lewat form, tetap
    # ada agar data historis tidak hilang.
    penetapan_konteks_misi: str | None = None
    tujuan_strategis: str | None = None
    sasaran_rpd: str | None = None
    iku_sasaran: str | None = None
    urusan_pemerintahan: str | None = None
    sumber_data: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)


class KonteksStrategisOpd(SQLModel, table=True):
    """Form 2b — penetapan konteks risiko strategis OPD."""
    __tablename__ = "tr_konteks_strategis_opd"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    sumber_data: str | None = None
    tujuan_strategis: str | None = None
    sasaran_strategis: str | None = None
    iku_renstra: str | None = None
    program: str | None = None
    tujuan_sasaran_iku_program: str | None = None
    urusan_pemerintahan: str | None = None
    periode_dinilai: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)


class KonteksOperasionalOpd(SQLModel, table=True):
    """Form 2c — penetapan konteks risiko operasional OPD."""
    __tablename__ = "tr_konteks_operasional_opd"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    sumber_data: str | None = None
    tujuan_strategis: str | None = None
    program: str | None = None
    indikator_program: str | None = None  # indikator lvl-5 (id_parent=idprogram)
    keluaran_hasil_kegiatan: str | None = None
    keluaran_sub_kegiatan: str | None = None
    urusan_pemerintahan: str | None = None
    periode_dinilai: str | None = None
    # Referensi centang renja Form 2.c (salah satu terisi):
    #   ref_subkegiatan = renja_subkegiatan.idsubkegiatan (baris subkegiatan)
    #   ref_indikator   = renja_indikator.id (baris indikator program lvl-5)
    # Keduanya null = entri manual lama.
    ref_subkegiatan: str | None = Field(default=None, index=True)
    ref_indikator: str | None = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=now_wib)
