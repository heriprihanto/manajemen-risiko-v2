"""Form 8 (Infokom), Form 9 (Monitoring PI), Form 10 (Risk Event & RTP)."""
from datetime import datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import UserDep, guard_record
from app.db import get_session
from app.models import Infokom, MonitoringPi, MonitoringRiskEvent, Risiko


def _event_risiko(session: Session, user: dict, eid: int) -> MonitoringRiskEvent:
    """Ambil event + verifikasi akses OPD lewat risiko induknya."""
    obj = session.get(MonitoringRiskEvent, eid)
    if not obj:
        raise HTTPException(404, "Event tidak ditemukan")
    guard_record(user, session.get(Risiko, obj.risiko_id), "Risiko")
    return obj
from app.routers.crud_helper import make_opd_tahun_router

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Form 8 & Form 9 — per OPD & tahun
router.include_router(
    make_opd_tahun_router(model=Infokom, prefix="/infokom", tag="monitoring", order_by="no_urut")
)
router.include_router(
    make_opd_tahun_router(model=MonitoringPi, prefix="/pi", tag="monitoring", order_by="no_urut")
)


# ------------------------ Form 10: Risk Event (per risiko) --------------------
@router.get("/risk-event")
def list_event(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    risiko = session.exec(
        select(Risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    ids = [r.id for r in risiko]
    events: dict[int, list[MonitoringRiskEvent]] = {}
    if ids:
        for e in session.exec(
            select(MonitoringRiskEvent).where(MonitoringRiskEvent.risiko_id.in_(ids))
        ).all():
            events.setdefault(e.risiko_id, []).append(e)
    out = []
    for r in risiko:
        out.append(
            {
                "risiko_id": r.id,
                "jenis_risiko": r.jenis_risiko,
                "kode_risiko": r.kode_risiko,
                "uraian_risiko": r.uraian_risiko,
                "events": [e.model_dump() for e in events.get(r.id, [])],
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
