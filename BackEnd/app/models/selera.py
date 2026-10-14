"""Ketetapan selera risiko per entitas/pemilik; setiap perubahan adalah versi baru."""
from datetime import datetime
from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel
from app.core.datetime_utils import now_wib


class SeleraRisiko(SQLModel, table=True):
    __tablename__ = "mr_selera_risiko"
    __table_args__ = (
        CheckConstraint("ambang >= 1 AND ambang <= skala_maksimum", name="ck_selera_ambang"),
        Index("ix_selera_scope", "opd_id", "tahun", "pemilik_key", "id"),
    )
    id: int | None = Field(default=None, primary_key=True)
    opd_id: int = Field(foreign_key="ta_opd.id_sub_pd")
    tahun: int
    # Key kosong = ketetapan tingkat entitas, berlaku jika pemilik belum memiliki ketetapan khusus.
    pemilik_key: str = Field(default="", max_length=500)
    pemilik_risiko: str | None = Field(default=None, max_length=500)
    ambang: int
    skala_maksimum: int
    penetap: str
    pertimbangan_sumber_daya: str
    dasar_penetapan: str | None = None
    dicatat_oleh: str
    created_at: datetime = Field(default_factory=now_wib)
