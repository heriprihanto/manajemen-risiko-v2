"""Utilitas tanggal dan waktu Waktu Indonesia Barat (WIB / Asia/Jakarta, UTC+7)."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")


def now_wib() -> datetime:
    """Mengembalikan objek datetime saat ini dengan timezone WIB."""
    return datetime.now(WIB)


def today_wib() -> date:
    """Mengembalikan objek date hari ini berdasarkan waktu WIB."""
    return datetime.now(WIB).date()


def to_wib_iso(dt: datetime | None) -> str | None:
    """Mengonversi datetime (baik naive maupun timezone-aware) ke format ISO 8601 ber-offset WIB (+07:00)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Jika naive dari database lokal, asumsikan bernilai waktu WIB
        dt = dt.replace(tzinfo=WIB)
    else:
        dt = dt.astimezone(WIB)
    return dt.isoformat()
