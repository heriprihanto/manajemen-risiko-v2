"""Pengaturan aplikasi — satu baris (id=1) yang diatur Admin."""
from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.datetime_utils import now_wib

SETTINGS_ID = 1


class Pengaturan(SQLModel, table=True):
    """Pengaturan global: tahun penilaian default & jadwal survei CEE.

    Sengaja satu baris (id selalu = 1) supaya tidak perlu tabel key-value dan
    seluruh nilai bisa dibaca sekali jalan.
    """
    __tablename__ = "tr_pengaturan"

    id: int | None = Field(default=SETTINGS_ID, primary_key=True)
    # Tahun penilaian yang dipakai sebagai default saat pengguna membuka
    # aplikasi (bisa tetap diubah manual lewat pemilih tahun di topbar).
    tahun_default: int | None = None
    # Jadwal survei publik CEE (inklusif; null = tanpa batas di sisi itu).
    survei_mulai: date | None = None
    survei_selesai: date | None = None
    # Saklar manual: 0 = survei ditutup meski masih dalam rentang tanggal.
    survei_aktif: int = 1
    # Ditampilkan pada halaman survei saat sedang tertutup.
    survei_pesan_tutup: str | None = None
    # Template undangan via Email & WhatsApp
    template_email_subject: str | None = None
    template_email: str | None = None
    template_wa: str | None = None
    updated_at: datetime = Field(default_factory=now_wib)
    updated_by: str | None = None
