"""Otorisasi penugasan dan kebijakan yang disimpan bersama setiap penilaian."""
from fastapi import HTTPException
from sqlmodel import Session, select
from app.core.datetime_utils import now_wib
from app.core.security import ensure_opd_access
from app.models import Risiko, Opd
from app.models.tata_kelola import AuditRisiko, KebijakanRisiko, PenugasanRisiko, UrutanPrioritas
from app.services import analisis, selera

PERAN = {"operator", "upr", "atasan", "upr_atasan", "upr_pemda", "kepatuhan", "inspektorat", "komite", "koordinator"}
PENULIS = {"operator", "upr", "upr_pemda"}


def identitas(user):
    return user.get("username") or str(user.get("id"))


def peran(session, user, opd_id):
    # Penugasan melengkapi, bukan memperluas cakupan OPD SSO.
    ensure_opd_access(user, opd_id)
    today = now_wib().date()
    return set(session.exec(select(PenugasanRisiko.peran).where(
        PenugasanRisiko.opd_id == opd_id,
        PenugasanRisiko.username == identitas(user),
        PenugasanRisiko.aktif == True,
        PenugasanRisiko.mulai <= today,
        PenugasanRisiko.selesai >= today,
    )).all())


def wajib_peran(session, user, opd_id, roles):
    if not peran(session, user, opd_id).intersection(roles):
        raise HTTPException(403, "Memerlukan penugasan aktif: " + ", ".join(sorted(roles)))


def hak_tulis(session, user, opd_id):
    roles = peran(session, user, opd_id)
    pernah_ditugaskan = session.exec(select(PenugasanRisiko.id).where(
        PenugasanRisiko.opd_id == opd_id, PenugasanRisiko.username == identitas(user))).first() is not None
    return bool(roles.intersection(PENULIS)) or (not roles and not pernah_ditugaskan)


def boleh_tulis(session, user, opd_id):
    if not hak_tulis(session, user, opd_id):
        raise HTTPException(403, "Penugasan Anda hanya untuk pemantauan atau persetujuan")
    # Pengelola OPD lama tetap dapat mengusulkan; admin tidak otomatis berhak mengesahkan.


def risiko_akses(session, user, rid, tulis=False):
    obj = session.get(Risiko, rid)
    if obj and tulis:
        ensure_opd_access(user, obj.opd_id)
        session.exec(select(Opd).where(Opd.id_sub_pd == obj.opd_id).with_for_update()).first()
        obj = session.exec(select(Risiko).where(Risiko.id == rid).with_for_update().execution_options(populate_existing=True)).first()
    if not obj:
        raise HTTPException(404, "Risiko tidak ditemukan")
    ensure_opd_access(user, obj.opd_id)
    if tulis:
        boleh_tulis(session, user, obj.opd_id)
    return obj


def kebijakan_aktif(session, opd_id, tahun):
    return session.exec(select(KebijakanRisiko).where(
        KebijakanRisiko.opd_id == opd_id, KebijakanRisiko.tahun == tahun,
        KebijakanRisiko.status == "disetujui", KebijakanRisiko.berlaku <= now_wib().date(),
    ).order_by(KebijakanRisiko.berlaku.desc(), KebijakanRisiko.id.desc())).first()


def snapshot_kebijakan(session, opd_id, tahun, pemilik=None):
    policy = kebijakan_aktif(session, opd_id, tahun)
    snapshot = policy.model_dump(mode="json") if policy else {
        "nama": "Matriks 5×5 — kriteria penilaian belum disahkan",
        "matriks": {f"{k}-{d}": v for (k, d), v in analisis.MATRIKS_SKALA.items()},
    }
    setting = selera.effective(session, opd_id, tahun, pemilik)
    snapshot.update(selera_risiko=selera.as_dict(setting),
        selera=list(range(1, setting.ambang + 1)) if setting else None,
        toleransi=list(range(1, setting.ambang + 1)) if setting else None)
    return policy.id if policy else None, snapshot


def nilai(session, risiko, dampak, kemungkinan):
    if type(dampak) is not int or type(kemungkinan) is not int or not (1 <= dampak <= 5 and 1 <= kemungkinan <= 5):
        raise HTTPException(422, "Dampak dan kemungkinan harus bilangan bulat 1–5")
    pid, policy = snapshot_kebijakan(session, risiko.opd_id, risiko.tahun, risiko.pemilik_risiko)
    if policy["selera"] is None:
        raise HTTPException(409, "Tetapkan Selera Risiko untuk entitas atau Pemilik Risiko sebelum melakukan penilaian")
    skor = policy["matriks"][f"{kemungkinan}-{dampak}"]
    prioritas = skor not in policy["selera"]
    luar = policy["toleransi"] is not None and skor not in policy["toleransi"]
    return dict(skor=skor, prioritas=prioritas, di_luar_toleransi=luar,
                kebijakan_id=pid, kebijakan_snapshot=policy)


def audit(session, user, obj, aksi, opd_id, tahun, risiko_id=None):
    session.flush()
    session.add(AuditRisiko(opd_id=opd_id, tahun=tahun, risiko_id=risiko_id,
        entitas=obj.__tablename__, entitas_id=obj.id, aksi=aksi,
        pelaku=identitas(user), data=obj.model_dump(mode="json")))


def putuskan(session, user, obj, keputusan, catatan, opd_id, roles):
    wajib_peran(session, user, opd_id, roles)
    if obj.pembuat == identitas(user):
        raise HTTPException(403, "Pembuat tidak dapat menyetujui atau menolak pengajuannya sendiri")
    if obj.status != "diajukan":
        raise HTTPException(409, "Pengajuan sudah diputuskan; buat pengajuan baru untuk revisi")
    obj.status = keputusan
    obj.penyetuju = identitas(user)
    obj.catatan = catatan
    if hasattr(obj, "decided_at"):
        obj.decided_at = now_wib()
    session.add(obj)


def urutkan_prioritas(session, rows, opd_id, tahun):
    policy = kebijakan_aktif(session, opd_id, tahun)
    criteria = policy.kriteria if policy else {}
    areas = {v: i for i, v in enumerate(criteria.get("area_dampak", []))}
    categories = {v: i for i, v in enumerate(criteria.get("kategori_prioritas", []))}
    ids = [r["id"] for r in rows]
    ranks = {x.risiko_id: x for x in session.exec(select(UrutanPrioritas).where(UrutanPrioritas.risiko_id.in_(ids))).all()} if ids else {}
    def key(r):
        rank = ranks.get(r["id"])
        return (-(r["analisis"]["skala_risiko"] or 0),
                areas.get(rank.area_dampak if rank else None, 9999),
                categories.get(r.get("kategori_risiko"), 9999),
                rank.urutan_pimpinan if rank else 9999, r["id"])
    rows.sort(key=key)
    return rows
