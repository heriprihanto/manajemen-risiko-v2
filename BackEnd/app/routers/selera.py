"""Pencatatan ketetapan Pemilik Risiko, dengan riwayat versi yang dipertahankan."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field, StringConstraints
from sqlmodel import Session, select
from app.core.security import UserDep, ensure_opd_access
from app.db import get_session
from app.models import Opd, Risiko, AnalisisRisiko
from app.models.selera import SeleraRisiko
from app.schemas.tata_kelola import Input, Teks
from app.services import selera as svc, tata_kelola as governance

router = APIRouter(prefix="/selera-risiko", tags=["selera-risiko"])

class SeleraInput(Input):
    opd_id: Annotated[int, Field(strict=True, gt=0)]
    tahun: Annotated[int, Field(strict=True, ge=2026, le=2100)]
    pemilik_risiko: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None = None
    ambang: Annotated[int, Field(strict=True, ge=1)]
    penetap: Teks | None = None
    pertimbangan_sumber_daya: Teks
    dasar_penetapan: Teks | None = None

@router.get("")
def daftar(opd_id: int, tahun: int, session: Session = Depends(get_session), user: dict = UserDep):
    ensure_opd_access(user, opd_id)
    aktif = svc.daftar_aktif(session, opd_id, tahun)
    owners = session.exec(select(Risiko.pemilik_risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)).all()
    names = {svc.pemilik_key(n): " ".join(n.split()) for n in owners if n and n.strip()}
    names.update({k: s.pemilik_risiko for k, s in aktif.items() if k})
    return {"skala_maksimum": svc.skala_maksimum(), "boleh_tulis": governance.hak_tulis(session, user, opd_id),
        "pemilik": sorted(names.values()), "aktif": [svc.as_dict(s) for s in aktif.values()],
        "visual": svc.visual(aktif, semua=True, pemilik_terdaftar=owners),
        "riwayat": session.exec(select(SeleraRisiko).where(SeleraRisiko.opd_id == opd_id,
            SeleraRisiko.tahun == tahun).order_by(SeleraRisiko.id.desc())).all()}

@router.post("")
def tetapkan(body: SeleraInput, session: Session = Depends(get_session), user: dict = UserDep):
    governance.boleh_tulis(session, user, body.opd_id)
    if body.ambang > svc.skala_maksimum():
        raise HTTPException(422, f"Ambang harus 1–{svc.skala_maksimum()}")
    # Semua penulisan penilaian/ketetapan mengambil lock OPD terlebih dahulu.
    if not session.exec(select(Opd).where(Opd.id_sub_pd == body.opd_id).with_for_update()).first():
        raise HTTPException(404, "OPD tidak ditemukan")
    data = body.model_dump()
    # Form cukup mencatat akun pencatat; identitas penetap historis tetap dipertahankan.
    data["penetap"] = body.penetap or ""
    data["pemilik_risiko"] = " ".join((body.pemilik_risiko or "").split()) or None
    obj = SeleraRisiko(**data, pemilik_key=svc.pemilik_key(body.pemilik_risiko),
        skala_maksimum=svc.skala_maksimum(), dicatat_oleh=governance.identitas(user))
    session.add(obj)
    session.flush()
    aktif = svc.daftar_aktif(session, body.opd_id, body.tahun)
    updated = 0
    for risk, analysis in session.exec(select(Risiko, AnalisisRisiko).join(AnalisisRisiko,
            AnalisisRisiko.risiko_id == Risiko.id).where(Risiko.opd_id == body.opd_id, Risiko.tahun == body.tahun)
            .order_by(Risiko.id).with_for_update()).all():
        setting = svc.resolve(aktif, risk.pemilik_risiko)
        if setting and setting.id == obj.id and analysis.skala_risiko is not None:
            analysis.is_prioritas = svc.status(analysis.skala_risiko, setting)
            session.add(analysis)
            updated += 1
    governance.audit(session, user, obj, "selera_ditetapkan", body.opd_id, body.tahun)
    session.commit()
    session.refresh(obj)
    return {"ketetapan": obj, "analisis_diperbarui": updated}
