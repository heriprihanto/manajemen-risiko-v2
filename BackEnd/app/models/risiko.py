"""Identifikasi & analisis risiko — Form 3a/3b/3c, Form 4, Form 5, Form 7."""
from datetime import date, datetime

from sqlalchemy import Column, LargeBinary
from sqlmodel import Field, SQLModel

from app.core.datetime_utils import now_wib

# jenis_risiko values
JENIS_STRATEGIS_PEMDA = "strategis_pemda"   # Form 3.a
JENIS_STRATEGIS_OPD = "strategis_opd"       # Form 3.b
JENIS_OPERASIONAL_OPD = "operasional_opd"   # Form 3.c
JENIS_RISIKO = (JENIS_STRATEGIS_PEMDA, JENIS_STRATEGIS_OPD, JENIS_OPERASIONAL_OPD)


class Risiko(SQLModel, table=True):
    """Form 3.a/3.b/3.c — identifikasi risiko. Dibedakan oleh `jenis_risiko`."""
    __tablename__ = "tr_risiko"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    jenis_risiko: str = Field(index=True)  # see JENIS_* above
    no_urut: str | None = None
    id_bidang_urusan: int | None = Field(default=None, index=True)

    # Konteks (strategis: tujuan/sasaran; operasional: kegiatan/tahap)
    # Form 3.b: referensi baris sumber konteks. konteks_sumber menandai tabel asal:
    #   'b' = tr_konteks_strategis_opd (Form 2.b)
    #   'c' = tr_konteks_operasional_opd (Form 2.c, indikator program)
    konteks_id: int | None = Field(default=None, index=True)
    konteks_sumber: str | None = None
    tujuan_sasaran: str | None = None
    indikator_kinerja: str | None = None
    kegiatan: str | None = None          # Form 3.c kolom b
    tahap_kegiatan: str | None = None    # Form 3.c kolom (tahap)
    indikator_keluaran: str | None = None  # Form 3.c kolom c

    # Risiko
    kategori_risiko: str | None = None
    uraian_risiko: str | None = None
    keterangan_risiko: str | None = None  # Keterangan Uraian Risiko
    kode_risiko: str | None = None
    pemilik_risiko: str | None = None

    # Sebab
    sebab_uraian: str | None = None
    sebab_sumber: str | None = None  # Internal/Eksternal

    cuc: str | None = None  # C / UC

    # Dampak
    dampak_uraian: str | None = None
    dampak_pihak_terkena: str | None = None

    urutan: int = 0
    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime = Field(default_factory=now_wib)


class AnalisisRisiko(SQLModel, table=True):
    """Form 4 — hasil penilaian awal menggunakan tabel matriks Perwal 1/2026."""
    __tablename__ = "tr_analisis_risiko"

    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True, unique=True)
    skala_dampak: int | None = None        # 1..5
    skala_kemungkinan: int | None = None   # 1..5
    skala_risiko: float | None = None      # Nilai level risiko 1..25 berdasarkan Matriks 5x5
    is_prioritas: bool = False
    updated_at: datetime = Field(default_factory=now_wib)


class RtpRisiko(SQLModel, table=True):
    """Form 7 — RTP atas hasil identifikasi risiko (per risiko prioritas)."""
    __tablename__ = "tr_rtp_risiko"

    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True, unique=True)
    status_pengendalian: str | None = None
    respon_risiko: str | None = None
    bukti_judul: str | None = None
    bukti_link: str | None = None
    bukti_berkas_id: int | None = Field(default=None, foreign_key="tr_rtp_bukti.id")
    bukti_nama: str | None = None
    pengendalian_ada: str | None = None
    celah_pengendalian: str | None = None
    rencana_tindak: str | None = None
    pemilik_penanggung_jawab: str | None = None
    target_mulai: date | None = None
    target_selesai: date | None = None
    target_waktu: str | None = None
    realisasi_waktu: str | None = None
    keterangan: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)


class RtpBukti(SQLModel, table=True):
    """Berkas privat berversi; konten tidak disertakan dalam audit/snapshot RTP."""
    __tablename__ = "tr_rtp_bukti"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int | None = Field(default=None, foreign_key="tr_risiko.id", index=True)
    rtp_cee_id: int | None = Field(default=None, foreign_key="tr_rtp_cee.id", index=True)
    nama: str
    konten: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    ukuran: int
    pembuat: str
    created_at: datetime = Field(default_factory=now_wib)


class TreatedRisk(SQLModel, table=True):
    """Tingkat risiko setelah adanya kegiatan pengendalian terpasang dan RTP (Treated Risk)."""
    __tablename__ = "tr_treated_risk"

    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True, unique=True)
    dampak_treated: int | None = None          # 1..5
    kemungkinan_treated: int | None = None     # 1..5
    skala_treated: float | None = None         # 1..25 berdasarkan Matriks 5x5
    justifikasi: str | None = None             # Dasar pertimbangan & justifikasi koreksi nilai
    updated_at: datetime = Field(default_factory=now_wib)
    updated_by: str | None = None


class RealisasiRtp(SQLModel, table=True):
    """Realisasi Rencana Tindak Pengendalian (RTP) beserta tanggal dan berkas bukti dukung."""
    __tablename__ = "tr_realisasi_rtp"

    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int | None = Field(default=None, foreign_key="tr_risiko.id", index=True)
    rtp_cee_id: int | None = Field(default=None, foreign_key="tr_rtp_cee.id", index=True)
    status_realisasi: str = Field(default="belum")  # "belum", "proses", "selesai"
    tanggal_realisasi: date | None = None
    uraian_hasil: str | None = None
    hambatan: str | None = None
    bukti_berkas_id: int | None = Field(default=None, foreign_key="tr_rtp_bukti.id")
    bukti_nama: str | None = None
    bukti_link: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)
    updated_by: str | None = None

