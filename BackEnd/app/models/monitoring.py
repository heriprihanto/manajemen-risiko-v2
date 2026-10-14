"""Komunikasi & pemantauan — Form 8 (Infokom), Form 9 (Monitoring PI), Form 10 (Risk Event)."""
from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.datetime_utils import now_wib


class Infokom(SQLModel, table=True):
    """Form 8 — rencana & realisasi pengkomunikasian pengendalian."""
    __tablename__ = "tr_infokom"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    risiko_id: int | None = Field(default=None, foreign_key="tr_risiko.id", index=True)
    no_urut: str | None = None
    kegiatan_pengendalian: str | None = None
    media_bentuk: str | None = None
    penyedia_informasi: str | None = None
    penerima_informasi: str | None = None
    rencana_mulai: date | None = None
    rencana_selesai: date | None = None
    rencana_waktu: str | None = None
    realisasi_waktu: str | None = None
    keterangan: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)


class MonitoringPi(SQLModel, table=True):
    """Form 9 — rencana & realisasi pemantauan atas kegiatan pengendalian."""
    __tablename__ = "tr_monitoring_pi"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(index=True)
    tahun: int = Field(index=True)
    risiko_id: int | None = Field(default=None, foreign_key="tr_risiko.id", index=True)
    no_urut: str | None = None
    jenis_risiko: str | None = None  # strategis_pemda / strategis_opd / operasional_opd
    kegiatan_pengendalian: str | None = None
    metode_pemantauan: str | None = None
    penanggung_jawab: str | None = None
    rencana_mulai: date | None = None
    rencana_selesai: date | None = None
    rencana_waktu: str | None = None
    realisasi_waktu: str | None = None
    keterangan: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)


class MonitoringRiskEvent(SQLModel, table=True):
    """Form 10 — pencatatan kejadian risiko & pelaksanaan RTP."""
    __tablename__ = "tr_monitoring_risk_event"

    id: int | None = Field(default=None, primary_key=True)
    risiko_id: int = Field(foreign_key="tr_risiko.id", index=True)
    no_urut: str | None = None
    tanggal_terjadi: date | None = None
    sebab_kejadian: str | None = None
    dampak_kejadian: str | None = None
    keterangan_kejadian: str | None = None
    rtp: str | None = None
    rencana_pelaksanaan_rtp: str | None = None
    realisasi_pelaksanaan_rtp: str | None = None
    keterangan_rtp: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)
