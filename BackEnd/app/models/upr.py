"""Model Unit Pemilik Risiko (mr_upr)."""
from datetime import datetime
from sqlmodel import Field, SQLModel
from app.core.datetime_utils import now_wib


class Upr(SQLModel, table=True):
    """Data personil/pejabat Unit Pemilik Risiko (UPR)."""
    __tablename__ = "mr_upr"

    id: int | None = Field(default=None, primary_key=True)
    opd_id: int | None = Field(default=None, index=True)
    nip: str = Field(index=True)
    nama: str = Field(index=True)
    jabatan: str
    eselon: str = Field(default="Non-Eselon")
    tingkat_organisasi: str = Field(default="UPR tingkat unit Eselon II", index=True)
    jabatan_upr: str = Field(default="Anggota", index=True)
    status: str = Field(default="Aktif")
    keterangan: str | None = None
    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime = Field(default_factory=now_wib)
