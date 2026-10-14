"""Alur Perwal: kebijakan, pengendalian, penilaian ulang, reviu dan laporan tetap."""
import calendar
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.datetime_utils import now_wib
from app.core.security import UserDep, AdminDep, ensure_opd_access
from app.services import selera
from app.db import get_session
from app.models import AnalisisRisiko, Risiko, RtpRisiko, MonitoringRiskEvent, LaporKejadian, Opd
from app.models.kamus import KamusRisiko
from app.models.tata_kelola import (
    PenugasanRisiko, KebijakanRisiko, PenilaianRiwayat, ResponsRisiko,
    TindakanRisiko, ReviuRisiko, LaporanBerkala, AuditRisiko, UsulanKamus, FraudRisiko, UrutanPrioritas,
)
from app.schemas.tata_kelola import (
    PenugasanInput, KebijakanInput, KeputusanInput, PenilaianInput, ResponsInput,
    TindakanInput, PelaksanaanInput, VerifikasiInput, ReviuInput, TindakLanjutInput,
    LaporanInput, UsulanInput, FraudInput, UrutanInput,
)
from app.services import tata_kelola as svc
from app.services.analisis import MATRIKS_SKALA

router = APIRouter(prefix="/tata-kelola", tags=["tata-kelola"])


def get_locked(session, model, oid):
    obj = session.exec(select(model).where(model.id == oid).with_for_update()).first()
    if not obj:
        raise HTTPException(404, "Data tidak ditemukan")
    return obj


def simpan(session, user, obj, aksi, opd_id, tahun, rid=None):
    session.add(obj)
    svc.audit(session, user, obj, aksi, opd_id, tahun, rid)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/akses")
def akses(opd_id: int, session: Session = Depends(get_session), user: dict = UserDep):
    return {"peran": sorted(svc.peran(session, user, opd_id)), "pilihan_peran": sorted(svc.PERAN),
            "boleh_tulis": svc.hak_tulis(session, user, opd_id)}


@router.get("/penugasan")
def penugasan(opd_id: int, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    return session.exec(select(PenugasanRisiko).where(PenugasanRisiko.opd_id == opd_id)).all()


@router.post("/penugasan")
def tambah_penugasan(body: PenugasanInput, session: Session = Depends(get_session), user: dict = AdminDep):
    if body.peran not in svc.PERAN:
        raise HTTPException(422, "Peran tidak dikenal")
    if not session.get(Opd, body.opd_id):
        raise HTTPException(404, "OPD tidak ditemukan")
    obj = PenugasanRisiko(**body.model_dump())
    return simpan(session, user, obj, "ditugaskan", body.opd_id, body.mulai.year)


@router.post("/penugasan/{oid}/nonaktif")
def nonaktif_penugasan(oid: int, session: Session = Depends(get_session), user: dict = AdminDep):
    obj = get_locked(session, PenugasanRisiko, oid)
    obj.aktif = False
    return simpan(session, user, obj, "dinonaktifkan", obj.opd_id, now_wib().year)


@router.get("/kebijakan")
def kebijakan(opd_id: int, tahun: int, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    pid, aktif = svc.snapshot_kebijakan(session, opd_id, tahun)
    return {"aktif_id": pid, "aktif": aktif, "items": session.exec(select(KebijakanRisiko).where(
        KebijakanRisiko.opd_id == opd_id, KebijakanRisiko.tahun == tahun).order_by(KebijakanRisiko.id.desc())).all()}


@router.post("/kebijakan")
def ajukan_kebijakan(body: KebijakanInput, session: Session = Depends(get_session), user: dict = UserDep):
    svc.boleh_tulis(session, user, body.opd_id)
    data = body.model_dump(exclude={"dampak", "kemungkinan", "area_dampak", "kategori_prioritas"})
    setting = selera.effective(session, body.opd_id, body.tahun)
    data["selera"] = list(range(1, setting.ambang + 1)) if setting else []
    data["toleransi"] = data["selera"]
    obj = KebijakanRisiko(**data, pembuat=svc.identitas(user),
        kriteria=body.model_dump(include={"dampak", "kemungkinan", "area_dampak", "kategori_prioritas"}),
        matriks={f"{k}-{d}": v for (k, d), v in MATRIKS_SKALA.items()})
    return simpan(session, user, obj, "diajukan", obj.opd_id, obj.tahun)


@router.post("/kebijakan/{oid}/keputusan")
def putus_kebijakan(oid: int, body: KeputusanInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, KebijakanRisiko, oid)
    svc.putuskan(session, user, obj, body.keputusan, body.catatan, obj.opd_id, {"upr_pemda"})
    return simpan(session, user, obj, body.keputusan, obj.opd_id, obj.tahun)


@router.get("/risiko/{rid}")
def detail(rid: int, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid)
    out = {"risiko": r, "analisis": session.exec(select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == rid)).first(),
           "rtp_lama": session.exec(select(RtpRisiko).where(RtpRisiko.risiko_id == rid)).first(),
           "urutan": session.exec(select(UrutanPrioritas).where(UrutanPrioritas.risiko_id == rid)).first(),
           "kebijakan": svc.snapshot_kebijakan(session, r.opd_id, r.tahun, r.pemilik_risiko)[1]}
    for key, model in [("penilaian", PenilaianRiwayat), ("respons", ResponsRisiko), ("tindakan", TindakanRisiko),
                       ("reviu", ReviuRisiko), ("kejadian", MonitoringRiskEvent)]:
        out[key] = session.exec(select(model).where(model.risiko_id == rid).order_by(model.id.desc())).all()
    # Data pelapor dan skenario fraud tidak ikut keluar dalam detail umum.
    return out


@router.post("/risiko/{rid}/penilaian")
def tambah_penilaian(rid: int, body: PenilaianInput, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid, tulis=True)
    if body.tahap == "residual" and not body.bukti:
        raise HTTPException(422, "Penilaian ulang memerlukan referensi bukti efektivitas")
    data = svc.nilai(session, r, body.dampak, body.kemungkinan)
    obj = PenilaianRiwayat(risiko_id=rid, **body.model_dump(), **data, pembuat=svc.identitas(user))
    if body.tahap == "awal":
        a = session.exec(select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == rid)).first()
        if not a:
            a = AnalisisRisiko(risiko_id=rid)
        a.skala_dampak, a.skala_kemungkinan = body.dampak, body.kemungkinan
        a.skala_risiko, a.is_prioritas = data["skor"], data["prioritas"]
        a.updated_at = now_wib()
        session.add(a)
    return simpan(session, user, obj, "dinilai", r.opd_id, r.tahun, rid)


@router.post("/risiko/{rid}/respons")
def ajukan_respons(rid: int, body: ResponsInput, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid, tulis=True)
    p = session.get(PenilaianRiwayat, body.penilaian_id)
    if not p or p.risiko_id != rid:
        raise HTTPException(422, "Penilaian tidak berasal dari risiko ini")
    if not p.kebijakan_snapshot.get("selera_risiko"):
        raise HTTPException(409, "Tetapkan Selera Risiko dan buat penilaian baru sebelum mengajukan respons")
    current = selera.effective(session, r.opd_id, r.tahun, r.pemilik_risiko)
    if not current or current.id != p.kebijakan_snapshot["selera_risiko"]["id"]:
        raise HTTPException(409, "Selera Risiko telah berubah; buat penilaian baru sebelum mengajukan respons")
    luar_selera = p.skor > current.ambang
    if "terima" in body.opsi and (len(body.opsi) > 1 or p.prioritas or luar_selera or p.di_luar_toleransi):
        raise HTTPException(422, "Penerimaan hanya untuk risiko dalam selera/toleransi dan tidak digabung opsi lain")
    eskalasi = bool(set(body.opsi) & {"bagi", "hindari"}) or (
        p.tahap in {"target", "residual"} and (p.prioritas or luar_selera or p.di_luar_toleransi))
    role = "upr_atasan" if eskalasi else ("atasan" if "terima" in body.opsi else "upr")
    obj = ResponsRisiko(risiko_id=rid, **body.model_dump(), peran_penyetuju=role, pembuat=svc.identitas(user))
    return simpan(session, user, obj, "diajukan", r.opd_id, r.tahun, rid)


@router.post("/respons/{oid}/keputusan")
def putus_respons(oid: int, body: KeputusanInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, ResponsRisiko, oid)
    r = svc.risiko_akses(session, user, obj.risiko_id)
    session.exec(select(Opd).where(Opd.id_sub_pd == r.opd_id).with_for_update()).first()
    if body.keputusan == "disetujui":
        p = session.get(PenilaianRiwayat, obj.penilaian_id)
        current = selera.effective(session, r.opd_id, r.tahun, r.pemilik_risiko)
        if not current or (p.kebijakan_snapshot.get("selera_risiko") or {}).get("id") != current.id:
            raise HTTPException(409, "Selera Risiko berubah; buat penilaian dan pengajuan respons baru")
    svc.putuskan(session, user, obj, body.keputusan, body.catatan, r.opd_id, {obj.peran_penyetuju})
    return simpan(session, user, obj, body.keputusan, r.opd_id, r.tahun, r.id)


@router.post("/risiko/{rid}/tindakan")
def tambah_tindakan(rid: int, body: TindakanInput, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid, tulis=True)
    obj = TindakanRisiko(risiko_id=rid, **body.model_dump(), pembuat=svc.identitas(user))
    return simpan(session, user, obj, "direncanakan", r.opd_id, r.tahun, rid)


@router.post("/tindakan/{oid}/pelaksanaan")
def pelaksanaan(oid: int, body: PelaksanaanInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, TindakanRisiko, oid)
    r = svc.risiko_akses(session, user, obj.risiko_id, tulis=True)
    if obj.status == "terverifikasi":
        raise HTTPException(409, "Tindakan sudah diverifikasi; buat tindakan lanjutan")
    if body.status == "selesai" and not body.bukti:
        raise HTTPException(422, "Penyelesaian memerlukan referensi bukti")
    obj.status, obj.hasil, obj.bukti = body.status, body.hasil, body.bukti
    obj.efektif, obj.verifikasi, obj.pemeriksa = None, None, None
    obj.pelaksana = svc.identitas(user)
    obj.updated_at = now_wib()
    return simpan(session, user, obj, "pelaksanaan", r.opd_id, r.tahun, r.id)


@router.post("/tindakan/{oid}/verifikasi")
def verifikasi(oid: int, body: VerifikasiInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, TindakanRisiko, oid)
    r = svc.risiko_akses(session, user, obj.risiko_id)
    svc.wajib_peran(session, user, r.opd_id, {"upr", "kepatuhan", "inspektorat"})
    if obj.status != "selesai":
        raise HTTPException(409, "Hanya tindakan selesai yang dapat diverifikasi")
    if svc.identitas(user) in {obj.pembuat, obj.pelaksana}:
        raise HTTPException(403, "Verifikasi harus dilakukan oleh pengguna lain")
    obj.efektif, obj.verifikasi = body.efektif, body.catatan
    obj.pemeriksa, obj.status = svc.identitas(user), "terverifikasi"
    obj.updated_at = now_wib()
    return simpan(session, user, obj, "diverifikasi", r.opd_id, r.tahun, r.id)


@router.post("/risiko/{rid}/reviu")
def tambah_reviu(rid: int, body: ReviuInput, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid)
    svc.wajib_peran(session, user, r.opd_id, {body.jenis})
    obj = ReviuRisiko(risiko_id=rid, **body.model_dump(), pemeriksa=svc.identitas(user))
    return simpan(session, user, obj, "dibuka", r.opd_id, r.tahun, rid)


@router.post("/reviu/{oid}/tindak-lanjut")
def tindak_lanjut(oid: int, body: TindakLanjutInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, ReviuRisiko, oid)
    r = svc.risiko_akses(session, user, obj.risiko_id, tulis=True)
    if obj.status == "ditutup":
        raise HTTPException(409, "Reviu sudah ditutup")
    obj.tindak_lanjut, obj.bukti = body.tindak_lanjut, body.bukti
    obj.status, obj.penindak, obj.updated_at = "ditindaklanjuti", svc.identitas(user), now_wib()
    return simpan(session, user, obj, "ditindaklanjuti", r.opd_id, r.tahun, r.id)


@router.post("/reviu/{oid}/verifikasi")
def tutup_reviu(oid: int, body: VerifikasiInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, ReviuRisiko, oid)
    r = svc.risiko_akses(session, user, obj.risiko_id)
    svc.wajib_peran(session, user, r.opd_id, {obj.jenis})
    if obj.status != "ditindaklanjuti":
        raise HTTPException(409, "Belum ada tindak lanjut yang dapat diverifikasi")
    if obj.penindak == svc.identitas(user):
        raise HTTPException(403, "Penindak lanjut tidak dapat memverifikasi sendiri")
    obj.status = "ditutup" if body.efektif else "terbuka"
    obj.catatan_verifikasi, obj.updated_at = body.catatan, now_wib()
    return simpan(session, user, obj, "diverifikasi", r.opd_id, r.tahun, r.id)


def batas_periode(tahun, periode):
    q = int(periode[-1]) if periode != "TAHUNAN" else 4
    bulan = q * 3
    return date(tahun, 1 if periode == "TAHUNAN" else bulan - 2, 1), date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])


@router.get("/laporan")
def laporan(opd_id: int, tahun: int, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    rows = session.exec(select(LaporanBerkala).where(LaporanBerkala.opd_id == opd_id, LaporanBerkala.tahun == tahun)
                        .order_by(LaporanBerkala.id.desc())).all()
    return [{**r.model_dump(exclude={"snapshot"}), "cakupan": r.snapshot.get("cakupan", "opd")} for r in rows
            if user.get("role_id") == 1 or set(r.snapshot.get("opd_ids", [r.opd_id])).issubset(user.get("opds") or [])]


@router.get("/laporan/{oid}")
def detail_laporan(oid: int, session: Session = Depends(get_session), user: dict = UserDep):
    obj = session.get(LaporanBerkala, oid)
    if not obj:
        raise HTTPException(404, "Laporan tidak ditemukan")
    ensure_opd_access(user, obj.opd_id)
    for oid in obj.snapshot.get("opd_ids", [obj.opd_id]):
        ensure_opd_access(user, oid)
    return obj


@router.post("/laporan")
def buat_laporan(body: LaporanInput, session: Session = Depends(get_session), user: dict = UserDep):
    role = {"kepatuhan": "kepatuhan", "pembinaan": "komite"}.get(body.jenis)
    if role:
        svc.wajib_peran(session, user, body.opd_id, {role})
    elif body.cakupan != "pemda":
        svc.boleh_tulis(session, user, body.opd_id)
    opd_ids = [body.opd_id]
    if body.cakupan == "pemda":
        svc.wajib_peran(session, user, body.opd_id, {"koordinator", "upr_pemda"})
        if not body.opd_ids or body.jenis not in {"upr", "penilaian"}:
            raise HTTPException(422, "Kompilasi Pemda memerlukan OPD sumber dan jenis laporan UPR/penilaian")
        opd_ids = sorted(set(body.opd_ids))
        for oid in opd_ids:
            ensure_opd_access(user, oid)
            if not session.get(Opd, oid):
                raise HTTPException(404, "OPD sumber tidak ditemukan")
    for oid in sorted(opd_ids):
        session.exec(select(Opd).where(Opd.id_sub_pd == oid).with_for_update()).first()
    awal, akhir = batas_periode(body.tahun, body.periode)
    if awal > now_wib().date():
        raise HTTPException(422, "Periode laporan belum dimulai")
    stmt = select(Risiko).where(Risiko.opd_id.in_(opd_ids), Risiko.tahun == body.tahun)
    if body.cakupan == "pemda":
        stmt = stmt.where(Risiko.jenis_risiko == "strategis_pemda")
    risks = session.exec(stmt.order_by(Risiko.opd_id, Risiko.id)).all()
    ids = [r.id for r in risks]
    snap = {"dicatat_pada": now_wib().isoformat(), "awal": str(awal), "akhir": str(akhir), "cakupan": body.cakupan,
            "opd_ids": opd_ids, "opd_sumber": [session.get(Opd, oid).model_dump(mode="json") for oid in opd_ids if session.get(Opd, oid)],
            "catatan": "Register dan status pengendalian saat pengajuan; kejadian difilter sesuai periode. Bukan rekonstruksi historis akhir triwulan.",
            "opd": session.get(Opd, body.opd_id).model_dump(mode="json") if session.get(Opd, body.opd_id) else {},
            "risiko": [r.model_dump(mode="json") for r in risks]}
    for key, model in [("analisis", AnalisisRisiko), ("rtp_lama", RtpRisiko), ("penilaian", PenilaianRiwayat),
                       ("respons", ResponsRisiko), ("tindakan", TindakanRisiko), ("reviu", ReviuRisiko), ("urutan", UrutanPrioritas), ("kejadian", MonitoringRiskEvent)]:
        stmt = select(model).where(model.risiko_id.in_(ids)).order_by(model.id)
        if key == "kejadian":
            stmt = stmt.where(model.tanggal_terjadi >= awal, model.tanggal_terjadi <= akhir)
        snap[key] = [x.model_dump(mode="json") for x in session.exec(stmt).all()] if ids else []
    snap["selera_risiko"] = {str(oid): [selera.as_dict(x) for x in selera.daftar_aktif(session, oid, body.tahun).values()] for oid in opd_ids}
    risk_map = {r.id: r for r in risks}
    for a in snap["analisis"]:
        r = risk_map[a["risiko_id"]]
        a["is_prioritas"] = selera.status(a["skala_risiko"], selera.effective(session, r.opd_id, r.tahun, r.pemilik_risiko))
    snap["kebijakan"] = svc.snapshot_kebijakan(session, body.opd_id, body.tahun)[1]
    snap["kebijakan_opd"] = {str(oid): svc.snapshot_kebijakan(session, oid, body.tahun)[1] for oid in opd_ids}
    obj = LaporanBerkala(**body.model_dump(exclude={"cakupan", "opd_ids"}), snapshot=snap, pembuat=svc.identitas(user),
        tembusan="Sekretaris Daerah" if body.jenis in {"kepatuhan", "pembinaan"} else "Sekretaris Daerah; Unit Kepatuhan")
    return simpan(session, user, obj, "diajukan", obj.opd_id, obj.tahun)


@router.post("/laporan/{oid}/keputusan")
def putus_laporan(oid: int, body: KeputusanInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, LaporanBerkala, oid)
    roles = {"kepatuhan": {"kepatuhan"}, "pembinaan": {"komite"}}.get(obj.jenis, {"upr", "upr_pemda"})
    if obj.snapshot.get("cakupan") == "pemda":
        roles = {"upr_pemda"}
        for oid in obj.snapshot["opd_ids"]:
            ensure_opd_access(user, oid)
    svc.putuskan(session, user, obj, body.keputusan, body.catatan, obj.opd_id, roles)
    return simpan(session, user, obj, body.keputusan, obj.opd_id, obj.tahun)


@router.get("/konsolidasi")
def konsolidasi(tahun: int, session: Session = Depends(get_session), user: dict = UserDep):
    stmt = select(Opd).where(Opd.aktif == 1).order_by(Opd.nama_pd)
    if user.get("role_id") != 1:
        stmt = stmt.where(Opd.id_sub_pd.in_(user.get("opds") or []))
    results = []
    for opd in session.exec(stmt).all():
        summary = ringkasan(opd.id_sub_pd, tahun, session, user)
        summary.update(opd_id=opd.id_sub_pd, nama=opd.nama_pd,
            risiko=len(summary["items"]), belum_dinilai=sum(i["skor_awal"] is None for i in summary["items"]))
        results.append(summary)
    return results


@router.get("/ringkasan")
def ringkasan(opd_id: int, tahun: int, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    risks = session.exec(select(Risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)).all()
    ids = [r.id for r in risks]
    if not ids:
        return {"items": [], "terlambat": 0, "menunggu": 0, "residual_melampaui": 0, "perlu_penilaian_ulang": 0}
    histories = session.exec(select(PenilaianRiwayat).where(PenilaianRiwayat.risiko_id.in_(ids)).order_by(PenilaianRiwayat.id)).all()
    residual = {p.risiko_id: p for p in histories if p.tahap == "residual"}
    acts = session.exec(select(TindakanRisiko).where(TindakanRisiko.risiko_id.in_(ids))).all()
    responses = session.exec(select(ResponsRisiko).where(ResponsRisiko.risiko_id.in_(ids))).all()
    events = session.exec(select(MonitoringRiskEvent).where(MonitoringRiskEvent.risiko_id.in_(ids))).all()
    analysis = {a.risiko_id: a for a in session.exec(select(AnalisisRisiko).where(AnalisisRisiko.risiko_id.in_(ids))).all()}
    aktif = selera.daftar_aktif(session, opd_id, tahun)
    items = []
    for r in risks:
        p, a = residual.get(r.id), analysis.get(r.id)
        ev = [e for e in events if e.risiko_id == r.id]
        needs_review = bool(ev) and (p is None or any(e.updated_at > p.created_at for e in ev))
        items.append({"id": r.id, "kode": r.kode_risiko, "uraian": r.uraian_risiko,
            "sasaran": r.tujuan_sasaran or r.kegiatan, "pemilik": r.pemilik_risiko,
            "skor_awal": a.skala_risiko if a else None, "residual": p.skor if p else None,
            "melampaui": selera.status(p.skor if p else None, selera.resolve(aktif, r.pemilik_risiko)),
            "terlambat": sum(t.risiko_id == r.id and t.target < now_wib().date() and t.status in {"direncanakan", "berjalan"} for t in acts),
            "menunggu": sum(s.risiko_id == r.id and s.status == "diajukan" for s in responses),
            "kejadian": len(ev), "perlu_penilaian_ulang": needs_review})
    items.sort(key=lambda x: (bool(x["melampaui"]), x["skor_awal"] or 0), reverse=True)
    return {"items": items, "terlambat": sum(i["terlambat"] for i in items),
        "menunggu": sum(i["menunggu"] for i in items), "residual_melampaui": sum(bool(i["melampaui"]) for i in items),
        "perlu_penilaian_ulang": sum(i["perlu_penilaian_ulang"] for i in items)}


@router.get("/audit")
def audit(opd_id: int, tahun: int, risiko_id: int | None = None, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    stmt = select(AuditRisiko).where(AuditRisiko.opd_id == opd_id, AuditRisiko.tahun == tahun)
    if risiko_id:
        stmt = stmt.where(AuditRisiko.risiko_id == risiko_id)
    # Metadata saja: payload internal dapat memuat skenario fraud dan laporan besar.
    return [x.model_dump(exclude={"data"}) for x in session.exec(stmt.order_by(AuditRisiko.id.desc()).limit(200)).all()]


@router.get("/usulan-kamus")
def usulan(opd_id: int, tahun: int, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    return session.exec(select(UsulanKamus).where(UsulanKamus.opd_id == opd_id, UsulanKamus.tahun == tahun)).all()


@router.post("/usulan-kamus")
def ajukan_usulan(body: UsulanInput, session: Session = Depends(get_session), user: dict = UserDep):
    svc.boleh_tulis(session, user, body.opd_id)
    obj = UsulanKamus(**body.model_dump(), pembuat=svc.identitas(user))
    return simpan(session, user, obj, "diajukan", obj.opd_id, obj.tahun)


@router.post("/usulan-kamus/{oid}/keputusan")
def putus_usulan(oid: int, body: KeputusanInput, session: Session = Depends(get_session), user: dict = UserDep):
    obj = get_locked(session, UsulanKamus, oid)
    svc.putuskan(session, user, obj, body.keputusan, body.catatan, obj.opd_id, {"upr", "inspektorat"})
    if body.keputusan == "disetujui":
        existing = session.exec(select(KamusRisiko).where(KamusRisiko.nama_risiko == obj.nama, KamusRisiko.kategori_risiko == obj.kategori)).first()
        if not existing:
            existing = KamusRisiko(nama_risiko=obj.nama, kategori_risiko=obj.kategori, deskripsi=obj.deskripsi, aktif=1)
            session.add(existing)
            session.flush()
            # ID global memberi kode unik tanpa perlombaan nomor urut antar-pengajuan.
            from app.routers.kamus import get_prefix_for_kategori
            existing.kode_risiko = f"{get_prefix_for_kategori(obj.kategori)}-U{existing.id:04d}"
        elif not existing.aktif:
            raise HTTPException(409, "Entri kamus sudah ada tetapi nonaktif; reviu entri tersebut dahulu")
        obj.kamus_id = existing.id
    return simpan(session, user, obj, body.keputusan, obj.opd_id, obj.tahun)


@router.get("/risiko/{rid}/fraud")
def fraud(rid: int, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid)
    svc.wajib_peran(session, user, r.opd_id, {"upr", "inspektorat"})
    return session.exec(select(FraudRisiko).where(FraudRisiko.risiko_id == rid)).first()


@router.put("/risiko/{rid}/fraud")
def simpan_fraud(rid: int, body: FraudInput, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid)
    svc.wajib_peran(session, user, r.opd_id, {"upr", "inspektorat"})
    if not any(x in (r.kategori_risiko or "").lower() for x in ("fraud", "kecurangan")):
        raise HTTPException(422, "Risiko harus berkategori fraud/kecurangan")
    # Serialisasi pembaruan per risiko termasuk penyimpanan pertama.
    session.exec(select(Risiko).where(Risiko.id == rid).with_for_update()).first()
    obj = session.exec(select(FraudRisiko).where(FraudRisiko.risiko_id == rid)).first()
    if not obj:
        obj = FraudRisiko(risiko_id=rid, **body.model_dump())
    else:
        for k, v in body.model_dump().items():
            setattr(obj, k, v)
    obj.updated_at = now_wib()
    return simpan(session, user, obj, "diperbarui", r.opd_id, r.tahun, rid)


@router.put("/risiko/{rid}/urutan")
def simpan_urutan(rid: int, body: UrutanInput, session: Session = Depends(get_session), user: dict = UserDep):
    r = svc.risiko_akses(session, user, rid)
    svc.wajib_peran(session, user, r.opd_id, {"upr", "upr_pemda"})
    policy = svc.kebijakan_aktif(session, r.opd_id, r.tahun)
    if not policy or body.area_dampak not in policy.kriteria["area_dampak"]:
        raise HTTPException(422, "Pilih area dampak dari kebijakan aktif")
    session.exec(select(Risiko).where(Risiko.id == rid).with_for_update()).first()
    obj = session.exec(select(UrutanPrioritas).where(UrutanPrioritas.risiko_id == rid)).first()
    if not obj:
        obj = UrutanPrioritas(risiko_id=rid, **body.model_dump(), pembuat=svc.identitas(user))
    else:
        for key, value in body.model_dump().items():
            setattr(obj, key, value)
        obj.pembuat, obj.updated_at = svc.identitas(user), now_wib()
    return simpan(session, user, obj, "diperingkat", r.opd_id, r.tahun, rid)
