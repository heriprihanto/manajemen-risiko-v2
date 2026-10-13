"""Form 3a/3b/3c (identifikasi risiko), Form 4 (analisis), Form 5 (prioritas),
Matriks Risiko, Form 7 (RTP risiko)."""
from datetime import datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, func, select

from app.core.security import UserDep, ensure_opd_access, guard_record
from app.db import get_session
from app.models import AnalisisRisiko, Opd, RefBidangUrusan, Risiko, RtpRisiko
from app.models.kamus import KamusRisiko
from app.models.risiko import (
    JENIS_OPERASIONAL_OPD,
    JENIS_RISIKO,
    JENIS_STRATEGIS_OPD,
    JENIS_STRATEGIS_PEMDA,
)
from app.services import analisis as an

router = APIRouter(prefix="/risiko", tags=["risiko"])

JENIS_LABEL = {
    "strategis_pemda": "Risiko Strategis Pemda (Form 3.a)",
    "strategis_opd": "Risiko Strategis OPD (Form 3.b)",
    "operasional_opd": "Risiko Operasional OPD (Form 3.c)",
}


def _analisis_dict(a: AnalisisRisiko | None) -> dict[str, Any]:
    if not a:
        return {
            "skala_dampak": None,
            "skala_kemungkinan": None,
            "skala_risiko": None,
            "level": None,
            "is_prioritas": False,
        }
    return {
        "skala_dampak": a.skala_dampak,
        "skala_kemungkinan": a.skala_kemungkinan,
        "skala_risiko": a.skala_risiko,
        "level": an.level_risiko(a.skala_risiko),
        "is_prioritas": a.is_prioritas,
    }


# ----------------------- Form 3a/3b/3c: Identifikasi --------------------------
@router.get("")
def list_risiko(
    opd_id: int,
    tahun: int,
    jenis: str | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(Risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    if jenis:
        stmt = stmt.where(Risiko.jenis_risiko == jenis)
    stmt = stmt.order_by(Risiko.jenis_risiko, Risiko.urutan, Risiko.id)
    risiko = session.exec(stmt).all()

    ids = [r.id for r in risiko]
    amap: dict[int, AnalisisRisiko] = {}
    if ids:
        amap = {
            a.risiko_id: a
            for a in session.exec(
                select(AnalisisRisiko).where(AnalisisRisiko.risiko_id.in_(ids))
            ).all()
        }

    bu_ids = [r.id_bidang_urusan for r in risiko if r.id_bidang_urusan]
    bu_map: dict[int, RefBidangUrusan] = {}
    if bu_ids:
        bu_map = {
            b.id: b
            for b in session.exec(
                select(RefBidangUrusan).where(RefBidangUrusan.id.in_(bu_ids))
            ).all()
        }

    out = []
    for r in risiko:
        d = r.model_dump()
        d["analisis"] = _analisis_dict(amap.get(r.id))
        bu = bu_map.get(r.id_bidang_urusan) if r.id_bidang_urusan else None
        d["bidang_urusan"] = (
            {
                "id": bu.id,
                "kode_bidang_urusan": bu.kode_bidang_urusan,
                "nama_bidang_urusan": bu.nama_bidang_urusan,
                "bidang_urusan_alias": bu.bidang_urusan_alias,
                "kode_risk": bu.kode_risk,
            }
            if bu
            else None
        )
        out.append(d)
    return out


def generate_kode_risiko(
    jenis_risiko: str,
    tahun: int,
    id_bidang_urusan: int | None,
    opd_id: int,
    session: Session,
) -> str:
    jenis_map = {
        JENIS_STRATEGIS_PEMDA: ("RSP", "01"),
        JENIS_STRATEGIS_OPD: ("RSO", "02"),
        JENIS_OPERASIONAL_OPD: ("ROO", "03"),
    }
    j_prefix, j_code = jenis_map.get(jenis_risiko, ("RSK", "00"))
    th2 = f"{tahun % 100:02d}"

    bu_code = "00"
    if id_bidang_urusan:
        bu = session.get(RefBidangUrusan, id_bidang_urusan)
        if bu and bu.kode_risk:
            bu_code = str(bu.kode_risk).strip().zfill(2)

    if jenis_risiko == JENIS_STRATEGIS_PEMDA:
        opd_code = "01"
    else:
        opd_code = "00"
        opd = session.exec(select(Opd).where(Opd.id_sub_pd == opd_id)).first()
        if opd and opd.kode_risk:
            opd_code = str(opd.kode_risk).strip().zfill(2)

    prefix = f"{j_prefix}.{th2}.{j_code}.{bu_code}.{opd_code}."

    existing = session.exec(
        select(Risiko.kode_risiko).where(
            Risiko.opd_id == opd_id,
            Risiko.tahun == tahun,
            Risiko.kode_risiko.like(f"{prefix}%"),
        )
    ).all()
    max_seq = 0
    for k in existing:
        if k and k.startswith(prefix):
            try:
                seq = int(k[len(prefix) :])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
    return f"{prefix}{max_seq + 1:03d}"


@router.post("")
def create_risiko(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session)
):
    if payload.get("jenis_risiko") not in JENIS_RISIKO:
        raise HTTPException(400, f"jenis_risiko harus salah satu dari {JENIS_RISIKO}")

    uraian = (payload.get("uraian_risiko") or "").strip()
    if not uraian:
        raise HTTPException(400, "Uraian risiko wajib diisi dan dipilih dari Kamus Risiko.")

    kamus_item = session.exec(
        select(KamusRisiko).where(
            func.lower(func.trim(KamusRisiko.nama_risiko)) == func.lower(uraian)
        )
    ).first()
    if not kamus_item:
        raise HTTPException(
            400, "Uraian risiko harus dipilih dari Kamus Risiko, tidak bisa mengetik sendiri."
        )

    obj = Risiko()
    fields = Risiko.model_fields
    for k, v in payload.items():
        if k in fields and k not in ("id", "created_at"):
            setattr(obj, k, v)
    obj.uraian_risiko = kamus_item.nama_risiko
    if not obj.kategori_risiko:
        obj.kategori_risiko = kamus_item.kategori_risiko

    if not obj.kode_risiko or not str(obj.kode_risiko).strip():
        obj.kode_risiko = generate_kode_risiko(
            obj.jenis_risiko,
            obj.tahun,
            obj.id_bidang_urusan,
            obj.opd_id,
            session,
        )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/{rid}")
def update_risiko(
    rid: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(Risiko, rid), "Risiko")
    fields = Risiko.model_fields

    if "uraian_risiko" in payload:
        uraian = (payload.get("uraian_risiko") or "").strip()
        if not uraian:
            raise HTTPException(400, "Uraian risiko wajib diisi dan dipilih dari Kamus Risiko.")
        kamus_item = session.exec(
            select(KamusRisiko).where(
                func.lower(func.trim(KamusRisiko.nama_risiko)) == func.lower(uraian)
            )
        ).first()
        if not kamus_item:
            raise HTTPException(
                400, "Uraian risiko harus dipilih dari Kamus Risiko, tidak bisa mengetik sendiri."
            )
        payload["uraian_risiko"] = kamus_item.nama_risiko
        if not payload.get("kategori_risiko"):
            payload["kategori_risiko"] = kamus_item.kategori_risiko

    for k, v in payload.items():
        if k in fields and k not in ("id", "created_at", "opd_id"):
            setattr(obj, k, v)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/{rid}")
def delete_risiko(
    rid: int, session: Session = Depends(get_session), user: dict = UserDep
):
    obj = guard_record(user, session.get(Risiko, rid), "Risiko")
    for a in session.exec(
        select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == rid)
    ).all():
        session.delete(a)
    for rt in session.exec(select(RtpRisiko).where(RtpRisiko.risiko_id == rid)).all():
        session.delete(rt)
    session.delete(obj)
    session.commit()
    return {"ok": True}


# ----------------------------- Form 4: Analisis ------------------------------
@router.post("/analisis")
def save_analisis(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    risiko_id = payload["risiko_id"]
    guard_record(user, session.get(Risiko, risiko_id), "Risiko")
    dampak = payload.get("skala_dampak")
    kemungkinan = payload.get("skala_kemungkinan")
    skala = an.hitung_skala(dampak, kemungkinan)

    obj = session.exec(
        select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == risiko_id)
    ).first()
    if not obj:
        obj = AnalisisRisiko(risiko_id=risiko_id)
    obj.skala_dampak = dampak
    obj.skala_kemungkinan = kemungkinan
    obj.skala_risiko = skala
    # is_prioritas: pakai nilai eksplisit bila dikirim, kalau tidak gunakan default.
    if "is_prioritas" in payload and payload["is_prioritas"] is not None:
        obj.is_prioritas = bool(payload["is_prioritas"])
    else:
        obj.is_prioritas = an.is_prioritas_default(skala)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return _analisis_dict(obj)


@router.get("/form4")
def form_4(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Hasil analisis risiko, dikelompokkan per jenis."""
    rows = list_risiko(opd_id, tahun, None, session)
    grouped: dict[str, list] = {j: [] for j in JENIS_RISIKO}
    for r in rows:
        grouped.setdefault(r["jenis_risiko"], []).append(r)
    return [
        {"jenis": j, "label": JENIS_LABEL[j], "items": grouped.get(j, [])}
        for j in JENIS_RISIKO
    ]


# ------------------------------ Matriks Risiko -------------------------------
@router.get("/matriks")
def matriks(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Sebaran risiko dalam matriks 5x5 (Kemungkinan vs Dampak)."""
    rows = list_risiko(opd_id, tahun, None, session)
    cells: dict[str, list] = {}
    for r in rows:
        a = r["analisis"]
        d, k = a["skala_dampak"], a["skala_kemungkinan"]
        if d and k:
            cells.setdefault(f"{k}-{d}", []).append(
                {"kode": r.get("kode_risiko"), "uraian": r.get("uraian_risiko")}
            )
    return {
        "dampak_label": an.DAMPAK_LABEL,
        "kemungkinan_label": an.KEMUNGKINAN_LABEL,
        "matriks_skala": {
            f"{k}-{d}": an.MATRIKS_SKALA.get((k, d))
            for k in range(1, 6)
            for d in range(1, 6)
        },
        "cells": cells,
    }


# ------------------------------ Form 5: Prioritas ----------------------------
@router.get("/form5")
def form_5(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Daftar risiko prioritas (is_prioritas=True), diurutkan skala menurun."""
    rows = list_risiko(opd_id, tahun, None, session)
    prioritas = [r for r in rows if r["analisis"]["is_prioritas"]]
    prioritas.sort(key=lambda r: r["analisis"]["skala_risiko"] or 0, reverse=True)
    grouped: dict[str, list] = {j: [] for j in JENIS_RISIKO}
    for r in prioritas:
        grouped.setdefault(r["jenis_risiko"], []).append(r)
    return [
        {"jenis": j, "label": JENIS_LABEL[j], "items": grouped.get(j, [])}
        for j in JENIS_RISIKO
    ]


# ------------------------------ Form 7: RTP Risiko ---------------------------
@router.get("/rtp")
def list_rtp(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Risiko prioritas + RTP-nya (Form 7)."""
    rows = list_risiko(opd_id, tahun, None, session)
    prioritas = [r for r in rows if r["analisis"]["is_prioritas"]]
    ids = [r["id"] for r in prioritas]
    rtp_map: dict[int, RtpRisiko] = {}
    if ids:
        rtp_map = {
            rt.risiko_id: rt
            for rt in session.exec(
                select(RtpRisiko).where(RtpRisiko.risiko_id.in_(ids))
            ).all()
        }
    out = []
    for r in prioritas:
        rt = rtp_map.get(r["id"])
        rtp = rt.model_dump() if rt else None
        if rtp is not None:
            # Pemilik/penanggung jawab selalu mengikuti Form 3.b (satu sumber
            # data) — tampilkan nilai terkini meski RTP disimpan lebih dulu.
            rtp["pemilik_penanggung_jawab"] = r.get("pemilik_risiko")
        out.append({**r, "rtp": rtp})
    return out


@router.post("/rtp")
def save_rtp(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    risiko_id = payload["risiko_id"]
    risiko = session.get(Risiko, risiko_id)
    guard_record(user, risiko, "Risiko")
    obj = session.exec(
        select(RtpRisiko).where(RtpRisiko.risiko_id == risiko_id)
    ).first()
    if not obj:
        obj = RtpRisiko(risiko_id=risiko_id)
    fields = RtpRisiko.model_fields
    # pemilik_penanggung_jawab tidak diambil dari client — selalu ikut Form 3.b.
    for k, v in payload.items():
        if k in fields and k not in ("id", "risiko_id", "pemilik_penanggung_jawab"):
            setattr(obj, k, v)
    obj.pemilik_penanggung_jawab = risiko.pemilik_risiko
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
