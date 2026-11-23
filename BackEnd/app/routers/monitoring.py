"""Form 8 (Infokom), Form 9 (Monitoring PI), Form 10 (Risk Event & RTP)."""
import json
from datetime import date, datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import UserDep, guard_record
from app.db import get_session
from app.models import Infokom, MonitoringPi, MonitoringRiskEvent, RealisasiRtp, Risiko, RtpRisiko


def _event_risiko(session: Session, user: dict, eid: int) -> MonitoringRiskEvent:
    """Ambil event + verifikasi akses OPD lewat risiko induknya."""
    obj = session.get(MonitoringRiskEvent, eid)
    if not obj:
        raise HTTPException(404, "Event tidak ditemukan")
    guard_record(user, session.get(Risiko, obj.risiko_id), "Risiko")
    return obj
from app.routers.crud_helper import make_opd_tahun_router

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Form 8: Infokom (sinkronisasi dari RTP Form 7)
@router.get("/infokom")
def list_infokom(
    opd_id: int,
    tahun: int,
    session: Session = Depends(get_session),
):
    """Form 8: sinkronisasi dan daftar pengkomunikasian kegiatan pengendalian dari RTP."""
    from app.routers.risiko import list_rtp

    rtp_rows = list_rtp(opd_id, tahun, session)
    rtp_by_risk: dict[int, dict] = {}
    for r in rtp_rows:
        rt = r.get("rtp")
        if rt and (rt.get("rencana_tindak") or "").strip():
            rtp_by_risk[r["id"]] = r

    existing_items = session.exec(
        select(Infokom).where(Infokom.opd_id == opd_id, Infokom.tahun == tahun).order_by(Infokom.no_urut, Infokom.id)
    ).all()

    existing_by_risk: dict[int, Infokom] = {}
    unlinked_items: list[Infokom] = []
    for it in existing_items:
        if it.risiko_id:
            existing_by_risk[it.risiko_id] = it
        else:
            unlinked_items.append(it)

    changed = False
    for unlinked in unlinked_items:
        for rid, rdata in rtp_by_risk.items():
            if rid not in existing_by_risk:
                rt_tindak = rdata["rtp"]["rencana_tindak"].strip()
                if (unlinked.kegiatan_pengendalian or "").strip() == rt_tindak:
                    unlinked.risiko_id = rid
                    existing_by_risk[rid] = unlinked
                    changed = True
                    break

    current_no = 1
    for rid, rdata in rtp_by_risk.items():
        rt = rdata["rtp"]
        kegiatan = rt["rencana_tindak"].strip()
        if rid in existing_by_risk:
            inf = existing_by_risk[rid]
            if inf.kegiatan_pengendalian != kegiatan:
                inf.kegiatan_pengendalian = kegiatan
                changed = True
            if not inf.no_urut:
                inf.no_urut = str(current_no)
                changed = True
            if not inf.rencana_mulai and rt.get("target_mulai"):
                inf.rencana_mulai = rt.get("target_mulai")
                changed = True
            if not inf.rencana_selesai and rt.get("target_selesai"):
                inf.rencana_selesai = rt.get("target_selesai")
                changed = True
            if not inf.rencana_waktu and rt.get("target_waktu"):
                inf.rencana_waktu = rt.get("target_waktu")
                changed = True
        else:
            inf = Infokom(
                opd_id=opd_id,
                tahun=tahun,
                risiko_id=rid,
                no_urut=str(current_no),
                kegiatan_pengendalian=kegiatan,
                rencana_mulai=rt.get("target_mulai"),
                rencana_selesai=rt.get("target_selesai"),
                rencana_waktu=rt.get("target_waktu"),
            )
            session.add(inf)
            existing_by_risk[rid] = inf
            changed = True
        current_no += 1

    if changed:
        session.commit()

    all_infokom = session.exec(
        select(Infokom).where(Infokom.opd_id == opd_id, Infokom.tahun == tahun).order_by(Infokom.no_urut, Infokom.id)
    ).all()

    rids = [i.risiko_id for i in all_infokom if i.risiko_id]
    risk_info = {}
    if rids:
        for r in session.exec(select(Risiko).where(Risiko.id.in_(rids))).all():
            risk_info[r.id] = {
                "kode_risiko": r.kode_risiko,
                "uraian_risiko": r.uraian_risiko,
                "pemilik_risiko": r.pemilik_risiko,
                "jenis_risiko": r.jenis_risiko,
            }

    out = []
    for i, it in enumerate(all_infokom):
        d = it.model_dump()
        r = risk_info.get(it.risiko_id, {})
        d["kode_risiko"] = r.get("kode_risiko")
        d["uraian_risiko"] = r.get("uraian_risiko")
        d["pemilik_risiko"] = r.get("pemilik_risiko")
        d["jenis_risiko"] = r.get("jenis_risiko")
        if not d.get("no_urut"):
            d["no_urut"] = str(i + 1)
        out.append(d)
    return out


@router.put("/infokom/{item_id}")
def update_infokom(
    item_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(Infokom, item_id))
    fields = Infokom.model_fields
    if "rencana_mulai" in payload or "rencana_selesai" in payload:
        mulai = payload.get("rencana_mulai")
        selesai = payload.get("rencana_selesai")
        if mulai and selesai:
            payload["rencana_waktu"] = f"{mulai} s.d. {selesai}" if mulai != selesai else str(mulai)
        elif mulai:
            payload["rencana_waktu"] = str(mulai)

    if "realisasi_mulai" in payload or "realisasi_selesai" in payload:
        r_mulai = payload.get("realisasi_mulai")
        r_selesai = payload.get("realisasi_selesai")
        if r_mulai and r_selesai:
            payload["realisasi_waktu"] = f"{r_mulai} s.d. {r_selesai}" if r_mulai != r_selesai else str(r_mulai)
        elif r_mulai:
            payload["realisasi_waktu"] = str(r_mulai)
        elif r_mulai is None and r_selesai is None and "realisasi_waktu" not in payload:
            payload["realisasi_waktu"] = None

    if "bukti_dukung" in payload:
        raw_bukti = payload.get("bukti_dukung")
        if isinstance(raw_bukti, list):
            items = []
            for b in raw_bukti:
                if isinstance(b, dict):
                    nm = (b.get("nama") or "").strip()
                    lk = (b.get("link") or "").strip()
                    if lk:
                        items.append({"nama": nm or "Bukti Dukung", "link": lk})
                elif isinstance(b, str) and b.strip():
                    items.append({"nama": "Bukti Dukung", "link": b.strip()})
            payload["bukti_dukung"] = json.dumps(items) if items else None
            if items and not payload.get("bukti_nama"):
                payload["bukti_nama"] = items[0]["nama"]
            elif not items:
                payload["bukti_nama"] = None
        elif isinstance(raw_bukti, str):
            payload["bukti_dukung"] = raw_bukti.strip() or None

    for key, value in payload.items():
        if key in fields and key not in ("id", "opd_id", "tahun", "risiko_id"):
            setattr(obj, key, value)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.post("/infokom")
def create_infokom(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
):
    obj = Infokom()
    fields = Infokom.model_fields
    if "rencana_mulai" in payload or "rencana_selesai" in payload:
        mulai = payload.get("rencana_mulai")
        selesai = payload.get("rencana_selesai")
        if mulai and selesai:
            payload["rencana_waktu"] = f"{mulai} s.d. {selesai}" if mulai != selesai else str(mulai)
        elif mulai:
            payload["rencana_waktu"] = str(mulai)

    if "realisasi_mulai" in payload or "realisasi_selesai" in payload:
        r_mulai = payload.get("realisasi_mulai")
        r_selesai = payload.get("realisasi_selesai")
        if r_mulai and r_selesai:
            payload["realisasi_waktu"] = f"{r_mulai} s.d. {r_selesai}" if r_mulai != r_selesai else str(r_mulai)
        elif r_mulai:
            payload["realisasi_waktu"] = str(r_mulai)
        elif r_mulai is None and r_selesai is None and "realisasi_waktu" not in payload:
            payload["realisasi_waktu"] = None

    if "bukti_dukung" in payload:
        raw_bukti = payload.get("bukti_dukung")
        if isinstance(raw_bukti, list):
            items = []
            for b in raw_bukti:
                if isinstance(b, dict):
                    nm = (b.get("nama") or "").strip()
                    lk = (b.get("link") or "").strip()
                    if lk:
                        items.append({"nama": nm or "Bukti Dukung", "link": lk})
                elif isinstance(b, str) and b.strip():
                    items.append({"nama": "Bukti Dukung", "link": b.strip()})
            payload["bukti_dukung"] = json.dumps(items) if items else None
            if items and not payload.get("bukti_nama"):
                payload["bukti_nama"] = items[0]["nama"]
            elif not items:
                payload["bukti_nama"] = None
        elif isinstance(raw_bukti, str):
            payload["bukti_dukung"] = raw_bukti.strip() or None

    for key, value in payload.items():
        if key in fields and key != "id":
            setattr(obj, key, value)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/infokom/{item_id}")
def delete_infokom(
    item_id: int,
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(Infokom, item_id))
    session.delete(obj)
    session.commit()
    return {"ok": True}


# Form 9: Pemantauan PI (sinkronisasi dari RTP Form 7)
@router.get("/pi")
def list_monitoring_pi(
    opd_id: int,
    tahun: int,
    session: Session = Depends(get_session),
):
    """Form 9: sinkronisasi dan daftar rencana pemantauan kegiatan pengendalian dari RTP."""
    from app.routers.risiko import list_rtp

    rtp_rows = list_rtp(opd_id, tahun, session)
    rtp_by_risk: dict[int, dict] = {}
    for r in rtp_rows:
        rt = r.get("rtp")
        if rt and (rt.get("rencana_tindak") or "").strip():
            rtp_by_risk[r["id"]] = r

    existing_items = session.exec(
        select(MonitoringPi).where(MonitoringPi.opd_id == opd_id, MonitoringPi.tahun == tahun).order_by(MonitoringPi.no_urut, MonitoringPi.id)
    ).all()

    existing_by_risk: dict[int, MonitoringPi] = {}
    unlinked_items: list[MonitoringPi] = []
    for it in existing_items:
        if it.risiko_id:
            existing_by_risk[it.risiko_id] = it
        else:
            unlinked_items.append(it)

    changed = False
    for unlinked in unlinked_items:
        for rid, rdata in rtp_by_risk.items():
            if rid not in existing_by_risk:
                rt_tindak = rdata["rtp"]["rencana_tindak"].strip()
                if (unlinked.kegiatan_pengendalian or "").strip() == rt_tindak:
                    unlinked.risiko_id = rid
                    existing_by_risk[rid] = unlinked
                    changed = True
                    break

    current_no = 1
    for rid, rdata in rtp_by_risk.items():
        rt = rdata["rtp"]
        kegiatan = rt["rencana_tindak"].strip()
        penanggung = rdata.get("pemilik_risiko") or rt.get("pemilik_penanggung_jawab")
        jenis = rdata.get("jenis_risiko")
        if rid in existing_by_risk:
            pi_item = existing_by_risk[rid]
            if pi_item.kegiatan_pengendalian != kegiatan:
                pi_item.kegiatan_pengendalian = kegiatan
                changed = True
            if not pi_item.jenis_risiko and jenis:
                pi_item.jenis_risiko = jenis
                changed = True
            if not pi_item.penanggung_jawab and penanggung:
                pi_item.penanggung_jawab = penanggung
                changed = True
            if not pi_item.no_urut:
                pi_item.no_urut = str(current_no)
                changed = True
            if not pi_item.rencana_mulai and rt.get("target_mulai"):
                pi_item.rencana_mulai = rt.get("target_mulai")
                changed = True
            if not pi_item.rencana_selesai and rt.get("target_selesai"):
                pi_item.rencana_selesai = rt.get("target_selesai")
                changed = True
            if not pi_item.rencana_waktu and rt.get("target_waktu"):
                pi_item.rencana_waktu = rt.get("target_waktu")
                changed = True
        else:
            pi_item = MonitoringPi(
                opd_id=opd_id,
                tahun=tahun,
                risiko_id=rid,
                no_urut=str(current_no),
                jenis_risiko=jenis,
                kegiatan_pengendalian=kegiatan,
                penanggung_jawab=penanggung,
                rencana_mulai=rt.get("target_mulai"),
                rencana_selesai=rt.get("target_selesai"),
                rencana_waktu=rt.get("target_waktu"),
            )
            session.add(pi_item)
            existing_by_risk[rid] = pi_item
            changed = True
        current_no += 1

    if changed:
        session.commit()

    all_pi = session.exec(
        select(MonitoringPi).where(MonitoringPi.opd_id == opd_id, MonitoringPi.tahun == tahun).order_by(MonitoringPi.no_urut, MonitoringPi.id)
    ).all()

    rids = [i.risiko_id for i in all_pi if i.risiko_id]
    risk_info = {}
    if rids:
        for r in session.exec(select(Risiko).where(Risiko.id.in_(rids))).all():
            risk_info[r.id] = {"kode_risiko": r.kode_risiko, "uraian_risiko": r.uraian_risiko}

    out = []
    for i, it in enumerate(all_pi):
        d = it.model_dump()
        r = risk_info.get(it.risiko_id, {})
        d["kode_risiko"] = r.get("kode_risiko")
        d["uraian_risiko"] = r.get("uraian_risiko")
        if not d.get("no_urut"):
            d["no_urut"] = str(i + 1)
        out.append(d)
    return out


@router.put("/pi/{item_id}")
def update_monitoring_pi(
    item_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(MonitoringPi, item_id))
    fields = MonitoringPi.model_fields
    if "rencana_mulai" in payload or "rencana_selesai" in payload:
        mulai = payload.get("rencana_mulai")
        selesai = payload.get("rencana_selesai")
        if mulai and selesai:
            payload["rencana_waktu"] = f"{mulai} s.d. {selesai}" if mulai != selesai else str(mulai)
        elif mulai:
            payload["rencana_waktu"] = str(mulai)

    for key, value in payload.items():
        if key in fields and key not in ("id", "opd_id", "tahun", "risiko_id"):
            setattr(obj, key, value)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.post("/pi")
def create_monitoring_pi(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
):
    obj = MonitoringPi()
    fields = MonitoringPi.model_fields
    if "rencana_mulai" in payload or "rencana_selesai" in payload:
        mulai = payload.get("rencana_mulai")
        selesai = payload.get("rencana_selesai")
        if mulai and selesai:
            payload["rencana_waktu"] = f"{mulai} s.d. {selesai}" if mulai != selesai else str(mulai)
        elif mulai:
            payload["rencana_waktu"] = str(mulai)
    for key, value in payload.items():
        if key in fields and key != "id":
            setattr(obj, key, value)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/pi/{item_id}")
def delete_monitoring_pi(
    item_id: int,
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(MonitoringPi, item_id))
    session.delete(obj)
    session.commit()
    return {"ok": True}


# ------------------------ Form 10: Risk Event (per risiko) --------------------
@router.get("/risk-event")
def list_event(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    risiko = session.exec(
        select(Risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    ids = [r.id for r in risiko]
    events: dict[int, list[MonitoringRiskEvent]] = {}
    rtp_map: dict[int, RtpRisiko] = {}
    realisasi_map: dict[int, RealisasiRtp] = {}

    if ids:
        for e in session.exec(
            select(MonitoringRiskEvent).where(MonitoringRiskEvent.risiko_id.in_(ids))
        ).all():
            events.setdefault(e.risiko_id, []).append(e)

        for rt in session.exec(
            select(RtpRisiko).where(RtpRisiko.risiko_id.in_(ids))
        ).all():
            rtp_map[rt.risiko_id] = rt

        for rel in session.exec(
            select(RealisasiRtp).where(RealisasiRtp.risiko_id.in_(ids))
        ).all():
            realisasi_map[rel.risiko_id] = rel

    out = []
    for r in risiko:
        rtp_obj = rtp_map.get(r.id)
        rel_obj = realisasi_map.get(r.id)

        # Uraian RTP dari master RTP risiko
        rtp_text = rtp_obj.rencana_tindak if rtp_obj and rtp_obj.rencana_tindak else None

        # Tanggal Realisasi RTP dari master Realisasi RTP risiko
        tanggal_realisasi_text = None
        if rel_obj:
            if rel_obj.tanggal_mulai and rel_obj.tanggal_selesai and rel_obj.tanggal_mulai != rel_obj.tanggal_selesai:
                tanggal_realisasi_text = f"{rel_obj.tanggal_mulai.strftime('%d/%m/%Y')} s.d. {rel_obj.tanggal_selesai.strftime('%d/%m/%Y')}"
            elif rel_obj.tanggal_mulai:
                tanggal_realisasi_text = rel_obj.tanggal_mulai.strftime('%d/%m/%Y')
            elif rel_obj.tanggal_realisasi:
                tanggal_realisasi_text = rel_obj.tanggal_realisasi.strftime('%d/%m/%Y')
        elif rtp_obj and rtp_obj.realisasi_waktu:
            tanggal_realisasi_text = str(rtp_obj.realisasi_waktu)

        ev_list = []
        for e in events.get(r.id, []):
            dump = e.model_dump()
            if not dump.get("rtp"):
                dump["rtp"] = rtp_text
            # Kolom Realisasi RTP diisi dengan tanggal realisasi RTP
            if not dump.get("realisasi_pelaksanaan_rtp"):
                dump["realisasi_pelaksanaan_rtp"] = tanggal_realisasi_text or "—"
            ev_list.append(dump)

        out.append(
            {
                "id": r.id,
                "risiko_id": r.id,
                "jenis_risiko": r.jenis_risiko,
                "kode_risiko": r.kode_risiko,
                "uraian_risiko": r.uraian_risiko,
                "pemilik_risiko": r.pemilik_risiko,
                "rtp": rtp_text,
                "realisasi_rtp": tanggal_realisasi_text or "—",
                "tanggal_realisasi_rtp": tanggal_realisasi_text or "—",
                "rtp_data": {
                    "rencana_tindak": rtp_obj.rencana_tindak if rtp_obj else None,
                    "target_waktu": rtp_obj.target_waktu if rtp_obj else None,
                    "penanggung_jawab": rtp_obj.pemilik_penanggung_jawab if rtp_obj else None,
                } if rtp_obj else None,
                "realisasi_data": {
                    "status_realisasi": rel_obj.status_realisasi if rel_obj else "belum",
                    "uraian_hasil": rel_obj.uraian_hasil if rel_obj else None,
                    "hambatan": rel_obj.hambatan if rel_obj else None,
                    "tanggal_realisasi": rel_obj.tanggal_realisasi.isoformat() if rel_obj and rel_obj.tanggal_realisasi else None,
                    "tanggal_mulai": rel_obj.tanggal_mulai.isoformat() if rel_obj and rel_obj.tanggal_mulai else None,
                    "tanggal_selesai": rel_obj.tanggal_selesai.isoformat() if rel_obj and rel_obj.tanggal_selesai else None,
                    "bukti_nama": rel_obj.bukti_nama if rel_obj else None,
                    "bukti_link": rel_obj.bukti_link if rel_obj else None,
                } if rel_obj else None,
                "events": ev_list,
            }
        )
    return out


@router.post("/risk-event")
def create_event(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    guard_record(user, session.get(Risiko, payload.get("risiko_id")), "Risiko")
    if "tanggal_terjadi" in payload and payload["tanggal_terjadi"] and not payload.get("waktu_kejadian"):
        payload["waktu_kejadian"] = str(payload["tanggal_terjadi"])
    elif "waktu_kejadian" in payload and payload["waktu_kejadian"] and not payload.get("tanggal_terjadi"):
        try:
            payload["tanggal_terjadi"] = date.fromisoformat(str(payload["waktu_kejadian"])[:10])
        except Exception:
            pass

    raw_bukti_link = payload.get("bukti_link")
    if isinstance(raw_bukti_link, list):
        items = []
        for b in raw_bukti_link:
            if isinstance(b, dict):
                nama = str(b.get("nama") or "").strip()
                link = str(b.get("link") or "").strip()
                if link:
                    items.append({"nama": nama or "Bukti Dukung", "link": link})
            elif isinstance(b, str) and b.strip():
                items.append({"nama": "Bukti Dukung", "link": b.strip()})
        payload["bukti_link"] = json.dumps(items) if items else None
        if items and not payload.get("bukti_nama"):
            payload["bukti_nama"] = items[0]["nama"]
    elif isinstance(raw_bukti_link, str):
        payload["bukti_link"] = raw_bukti_link.strip() or None

    obj = MonitoringRiskEvent()
    fields = MonitoringRiskEvent.model_fields
    for k, v in payload.items():
        if k in fields and k != "id":
            setattr(obj, k, v)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/risk-event/{eid}")
def update_event(
    eid: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = _event_risiko(session, user, eid)
    if "tanggal_terjadi" in payload and payload["tanggal_terjadi"] and not payload.get("waktu_kejadian"):
        payload["waktu_kejadian"] = str(payload["tanggal_terjadi"])
    elif "waktu_kejadian" in payload and payload["waktu_kejadian"] and not payload.get("tanggal_terjadi"):
        try:
            payload["tanggal_terjadi"] = date.fromisoformat(str(payload["waktu_kejadian"])[:10])
        except Exception:
            pass

    raw_bukti_link = payload.get("bukti_link")
    if isinstance(raw_bukti_link, list):
        items = []
        for b in raw_bukti_link:
            if isinstance(b, dict):
                nama = str(b.get("nama") or "").strip()
                link = str(b.get("link") or "").strip()
                if link:
                    items.append({"nama": nama or "Bukti Dukung", "link": link})
            elif isinstance(b, str) and b.strip():
                items.append({"nama": "Bukti Dukung", "link": b.strip()})
        payload["bukti_link"] = json.dumps(items) if items else None
        if items and not payload.get("bukti_nama"):
            payload["bukti_nama"] = items[0]["nama"]
    elif isinstance(raw_bukti_link, str):
        payload["bukti_link"] = raw_bukti_link.strip() or None

    fields = MonitoringRiskEvent.model_fields
    for k, v in payload.items():
        if k in fields and k not in ("id", "risiko_id"):
            setattr(obj, k, v)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/risk-event/{eid}")
def delete_event(
    eid: int, session: Session = Depends(get_session), user: dict = UserDep
):
    obj = _event_risiko(session, user, eid)
    session.delete(obj)
    session.commit()
    return {"ok": True}
