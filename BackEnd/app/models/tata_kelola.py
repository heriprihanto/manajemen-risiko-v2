"""Tabel tambahan Perwal 1/2026; tidak mengubah atau menghapus data formulir lama."""
from datetime import date, datetime
from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel
from app.core.datetime_utils import now_wib


class PenugasanRisiko(SQLModel, table=True):
    __tablename__ = "mr_penugasan_risiko"
    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    username: str = Field(index=True)
    nama: str
    peran: str
    mulai: date
    selesai: date
    dasar: str
    aktif: bool = True


class KebijakanRisiko(SQLModel, table=True):
    __tablename__ = "mr_kebijakan_risiko"
    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    nama: str
    dasar: str
    berlaku: date
    # Nilai matriks yang diterima menurut selera dan toleransi; tidak disamakan dengan warna.
    selera: list[int] = Field(sa_column=Column(JSON, nullable=False))
    toleransi: list[int] = Field(sa_column=Column(JSON, nullable=False))
    kriteria: dict = Field(sa_column=Column(JSON, nullable=False))
    matriks: dict = Field(sa_column=Column(JSON, nullable=False))
    status: str = "diajukan"
    pembuat: str
    penyetuju: str | None = None
    catatan: str | None = None
    created_at: datetime = Field(default_factory=now_wib)
    decided_at: datetime | None = None


class PenilaianRiwayat(SQLModel, table=True):
    __tablename__ = "tr_penilaian_riwayat"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True)
    tahap: str  # awal, target, residual
    dampak: int
    kemungkinan: int
    skor: int
    prioritas: bool
    di_luar_toleransi: bool
    kebijakan_id: int | None = Field(default=None, foreign_key="mr_kebijakan_risiko.id")
    kebijakan_snapshot: dict = Field(sa_column=Column(JSON, nullable=False))
    alasan: str
    bukti: str | None = None
    pembuat: str
    created_at: datetime = Field(default_factory=now_wib)


class ResponsRisiko(SQLModel, table=True):
    __tablename__ = "tr_respons_risiko"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True)
    penilaian_id: int = Field(foreign_key="tr_penilaian_riwayat.id")
    opsi: list[str] = Field(sa_column=Column(JSON, nullable=False))
    alasan: str
    peran_penyetuju: str
    status: str = "diajukan"
    pembuat: str
    penyetuju: str | None = None
    catatan: str | None = None
    created_at: datetime = Field(default_factory=now_wib)
    decided_at: datetime | None = None


class TindakanRisiko(SQLModel, table=True):
    __tablename__ = "tr_tindakan_risiko"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True)
    uraian: str
    pic: str
    target: date
    status: str = "direncanakan"
    hasil: str | None = None
    bukti: str | None = None
    efektif: bool | None = None
    verifikasi: str | None = None
    pemeriksa: str | None = None
    pembuat: str
    pelaksana: str | None = None
    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime = Field(default_factory=now_wib)


class ReviuRisiko(SQLModel, table=True):
    __tablename__ = "tr_reviu_risiko"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True)
    jenis: str
    temuan: str
    rekomendasi: str
    target: date
    status: str = "terbuka"
    tindak_lanjut: str | None = None
    bukti: str | None = None
    pemeriksa: str
    penindak: str | None = None
    catatan_verifikasi: str | None = None
    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime = Field(default_factory=now_wib)


class LaporanBerkala(SQLModel, table=True):
    __tablename__ = "tr_laporan_berkala"
    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    periode: str
    jenis: str
    ringkasan: str
    penerima: str = "Wali Kota"
    tembusan: str
    snapshot: dict = Field(sa_column=Column(JSON, nullable=False))
    status: str = "diajukan"
    pembuat: str
    penyetuju: str | None = None
    catatan: str | None = None
    created_at: datetime = Field(default_factory=now_wib)
    decided_at: datetime | None = None


class AuditRisiko(SQLModel, table=True):
    __tablename__ = "tr_audit_risiko"
    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    risiko_id: int | None = Field(default=None, index=True)
    entitas: str
    entitas_id: int
    aksi: str
    pelaku: str
    data: dict = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=now_wib)


class UsulanKamus(SQLModel, table=True):
    __tablename__ = "tr_usulan_kamus"
    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int
    nama: str
    kategori: str
    deskripsi: str
    status: str = "diajukan"
    pembuat: str
    penyetuju: str | None = None
    catatan: str | None = None
    kamus_id: int | None = Field(default=None, foreign_key="mr_kamus_risiko.id")
    created_at: datetime = Field(default_factory=now_wib)


class FraudRisiko(SQLModel, table=True):
    __tablename__ = "tr_fraud_risiko"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", unique=True)
    skenario: str
    proses_rawan: str
    kelemahan: str
    indikator: str
    updated_at: datetime = Field(default_factory=now_wib)


class UrutanPrioritas(SQLModel, table=True):
    __tablename__ = "tr_urutan_prioritas"
    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", unique=True)
    area_dampak: str
    urutan_pimpinan: int = 9999
    alasan: str
    pembuat: str
    updated_at: datetime = Field(default_factory=now_wib)


class KejadianTautan(SQLModel, table=True):
    __tablename__ = "tr_kejadian_tautan"
    __table_args__ = (UniqueConstraint("laporan_id"),)
    id: int | None = Field(default=None, primary_key=True)
    laporan_id: int = Field(foreign_key="tr_lapor_kejadian.id")
    event_id: int = Field(foreign_key="tr_monitoring_risk_event.id")
