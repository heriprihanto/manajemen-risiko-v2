"""Model data untuk Kamus Risiko (tabel mr_kamus_risiko)."""
from datetime import datetime
from sqlmodel import Field, SQLModel
from app.core.datetime_utils import now_wib


class KamusRisiko(SQLModel, table=True):
    __tablename__ = "mr_kamus_risiko"

    id: int | None = Field(default=None, primary_key=True)
    no: int | None = None
    nama_klp: str = Field(default="Kota Tegal", max_length=150)
    kategori_risiko: str = Field(max_length=100)
    nama_risiko: str
    deskripsi: str | None = None
    aktif: int = Field(default=1)
    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime | None = None
    kode_risiko: str | None = Field(default=None, max_length=50)
