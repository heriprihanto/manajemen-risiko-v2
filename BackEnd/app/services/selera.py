"""Satu sumber ambang penerimaan: ketetapan pemilik, lalu ketetapan entitas."""
from sqlmodel import select
from app.models.selera import SeleraRisiko
from app.services.analisis import MATRIKS_SKALA


def skala_maksimum():
    return max(MATRIKS_SKALA.values())


def pemilik_key(value):
    return " ".join((value or "").split()).casefold()


def daftar_aktif(session, opd_id, tahun):
    result = {}
    for row in session.exec(select(SeleraRisiko).where(
        SeleraRisiko.opd_id == opd_id, SeleraRisiko.tahun == tahun,
    ).order_by(SeleraRisiko.id.desc())).all():
        result.setdefault(row.pemilik_key, row)
    return result


def resolve(aktif, pemilik=None):
    return aktif.get(pemilik_key(pemilik)) or aktif.get("")


def effective(session, opd_id, tahun, pemilik=None):
    return resolve(daftar_aktif(session, opd_id, tahun), pemilik)


def as_dict(setting):
    return setting.model_dump(mode="json") if setting else None


def status(skor, setting):
    if setting is None or skor is None:
        return None
    return skor > setting.ambang


def visual(aktif, pemilik=None, semua=False, pemilik_terdaftar=()):
    """Jangan menggambar satu garis untuk gabungan pemilik dengan ambang berbeda."""
    if semua:
        settings = [resolve(aktif, name) for name in pemilik_terdaftar]
        if not settings:
            settings = [resolve(aktif)]
        ambangs = {s.ambang if s else None for s in settings}
        ambang = next(iter(ambangs)) if len(ambangs) == 1 else None
        beragam = len(ambangs) > 1
    else:
        setting = resolve(aktif, pemilik)
        ambang, beragam = (setting.ambang if setting else None), False
    return {
        "ambang": ambang, "beragam": beragam,
        "ditetapkan": ambang is not None,
        "diterima": list(range(1, ambang + 1)) if ambang is not None else None,
        "skala_maksimum": skala_maksimum(),
    }
