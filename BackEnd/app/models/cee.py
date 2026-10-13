"""CEE (Control Environment Evaluation) — Form 1.a, 1.b, 1.c, Form 6."""
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.datetime_utils import now_wib


class CeeResponden(SQLModel, table=True):
    """Form 1.a — kolom R1..Rn dinamis (jumlah responden bervariasi per OPD)."""
    __tablename__ = "tr_cee_responden"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    kode_responden: str  # R1, R2, ...
    nama_responden: str | None = None
    jabatan: str | None = None
    kategori_jabatan: str | None = None
    nip: str | None = None
    no_hp: str | None = None
    token_id: str | None = Field(default=None, unique=True, index=True, exclude=True)
    invited_at: datetime | None = None
    whatsapp_invited_at: datetime | None = None
    submitted_at: datetime | None = None
    # Identitas responden; firebase_uid dipertahankan untuk data lama.
    email: str | None = Field(default=None, index=True)
    firebase_uid: str | None = Field(default=None, index=True)
    sumber: str = "admin"  # 'admin' | 'survei'
    narasi: str | None = None  # narasi lain terkait kondisi lingkungan pengendalian
    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime = Field(default_factory=now_wib)


class CeeJawaban(SQLModel, table=True):
    """Nilai jawaban (1-4) tiap responden untuk tiap pertanyaan."""
    __tablename__ = "tr_cee_jawaban"

    id: int | None = Field(default=None, primary_key=True)
    responden_id: int = Field(foreign_key="tr_cee_responden.id", index=True)
    pertanyaan_id: int = Field(foreign_key="mr_kuesioner_pertanyaan.id", index=True)
    nilai: int  # 1..4


class CeeDokumenNilai(SQLModel, table=True):
    """Form 1.b — hasil reviu dokumen per aspek (Memadai/Kurang Memadai)."""
    __tablename__ = "tr_cee_dokumen_nilai"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    item_id: int = Field(foreign_key="tr_cee_dokumen_item.id", index=True)
    nilai: int | None = None  # 1=Memadai, 0=Kurang Memadai
    sumber_data: str | None = None  # dokumen/data yang direviu
    keterangan: str | None = None  # legacy; uraian kelemahan kini di tabel terpisah
    updated_at: datetime = Field(default_factory=now_wib)


class CeeDokumenKelemahan(SQLModel, table=True):
    """Form 1.b — uraian kelemahan per aspek (boleh lebih dari satu entri)."""
    __tablename__ = "tr_cee_dokumen_kelemahan"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    item_id: int = Field(foreign_key="tr_cee_dokumen_item.id", index=True)
    uraian: str
    urutan: int = 0
    updated_at: datetime = Field(default_factory=now_wib)


class CeeSimpulan(SQLModel, table=True):
    """Form 1.c — simpulan gabungan persepsi + dokumen per sub-unsur."""
    __tablename__ = "tr_cee_simpulan"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    kategori_id: int = Field(foreign_key="mr_kuesioner_kategori.id", index=True)
    rata_persepsi: float | None = None
    rata_dokumen: float | None = None
    rata_gabungan: float | None = None
    predikat: str | None = None
    penjelasan: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)


class RtpCee(SQLModel, table=True):
    """Form 6 — RTP atas CEE (kondisi lingkungan pengendalian yang kurang memadai)."""
    __tablename__ = "tr_rtp_cee"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    no_urut: str | None = None
    aspek_cee: str | None = None
    kondisi_kerentanan: str | None = None
    pengendalian_ada: str | None = None
    celah_pengendalian: str | None = None
    rencana_tindak: str | None = None
    pemilik_penanggung_jawab: str | None = None
    target_waktu: str | None = None
    realisasi_waktu: str | None = None
    keterangan: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)
