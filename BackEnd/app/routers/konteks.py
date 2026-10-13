"""Form 2a (konteks strategis Pemda — per tahun), 2b (strategis OPD), 2c (operasional OPD)."""
from datetime import datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import KonteksOperasionalOpd, KonteksStrategisOpd, KonteksStrategisPemda
from app.routers.crud_helper import make_opd_tahun_router

router = APIRouter(prefix="/konteks", tags=["konteks"])


# ----------------------- Form 2a: Konteks Strategis Pemda ---------------------
@router.get("/pemda")
def get_pemda(tahun: int, session: Session = Depends(get_session)):
    obj = session.exec(
        select(KonteksStrategisPemda).where(KonteksStrategisPemda.tahun == tahun)
    ).first()
    return obj


@router.post("/pemda")
def save_pemda(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session)
):
    tahun = payload["tahun"]
    obj = session.exec(
        select(KonteksStrategisPemda).where(KonteksStrategisPemda.tahun == tahun)
    ).first()
    if not obj:
        obj = KonteksStrategisPemda(tahun=tahun)
    fields = KonteksStrategisPemda.model_fields
    for k, v in payload.items():
        if k in fields and k not in ("id", "tahun"):
            setattr(obj, k, v)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


# Form 2b & 2c — per OPD & tahun (umumnya satu baris, tapi diizinkan banyak)
router.include_router(
    make_opd_tahun_router(
        model=KonteksStrategisOpd, prefix="/strategis-opd", tag="konteks"
    )
)
router.include_router(
    make_opd_tahun_router(
        model=KonteksOperasionalOpd, prefix="/operasional-opd", tag="konteks"
    )
)


# Form 2.c — sinkronisasi centang renja (subkegiatan & indikator program) yang
# akan dinilai risikonya. Mengganti seluruh baris berbasis-renja (punya
# ref_subkegiatan atau ref_indikator) untuk OPD & tahun; entri manual lama
# (kedua ref null) dibiarkan.
@router.post("/operasional-opd/sync")
def sync_operasional_opd(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session)
):
    opd_id = payload["opd_id"]
    tahun = payload["tahun"]
    items = payload.get("items", [])
    existing = session.exec(
        select(KonteksOperasionalOpd).where(
            KonteksOperasionalOpd.opd_id == opd_id,
            KonteksOperasionalOpd.tahun == tahun,
        )
    ).all()
    for obj in existing:
        if obj.ref_subkegiatan is not None or obj.ref_indikator is not None:
            session.delete(obj)
    for it in items:
        session.add(
            KonteksOperasionalOpd(
                opd_id=opd_id,
                tahun=tahun,
                ref_subkegiatan=it.get("ref_subkegiatan"),
                ref_indikator=it.get("ref_indikator"),
                program=it.get("program"),
                indikator_program=it.get("indikator_program"),
                keluaran_hasil_kegiatan=it.get("keluaran_hasil_kegiatan"),
                keluaran_sub_kegiatan=it.get("keluaran_sub_kegiatan"),
            )
        )
    session.commit()
    return {"ok": True, "count": len(items)}
