"""Model data untuk Lapor Kejadian publik dan approval kejadian."""
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.datetime_utils import now_wib


class LaporKejadian(SQLModel, table=True):
    """Laporan kejadian risiko dari pegawai OPD (login Firebase)."""
    __tablename__ = "tr_lapor_kejadian"

    id: int | None = Field(default=None, primary_key=True)
    tahun: int = Field(index=True)
    opd_id: int = Field(index=True)
    no_hp: str
    nama_lengkap: str
    uraian_kejadian: str
    waktu_kejadian: str  # Teks/ISO datetime waktu kejadian terjadi
    tempat: str
    pemicu: str

    # Akun pelapor Firebase
    reporter_email: str | None = Field(default=None, index=True)
    reporter_uid: str | None = Field(default=None, index=True)

    # Status approval oleh pengelola risiko: 'pending', 'disetujui', 'ditolak'
    status: str = Field(default="pending", index=True)
    catatan_validasi: str | None = None
    risiko_id: int | None = Field(default=None, index=True)  # Referensi opsional ke tr_risiko
    validated_by: int | None = None  # user id internal sso_users yang memvalidasi
    validated_by_name: str | None = None
    validated_at: datetime | None = None

    created_at: datetime = Field(default_factory=now_wib)
    updated_at: datetime = Field(default_factory=now_wib)
