"""Pengaturan aplikasi: tahun penilaian default & jadwal survei CEE.

Baca: seluruh pengguna terautentikasi (dipakai frontend untuk tahun default).
Tulis: khusus Admin (role_id = 1).
"""
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session

from app.core.config import settings
from app.core.datetime_utils import now_wib, today_wib, to_wib_iso
from app.core.security import AdminDep
from app.db import get_session
from app.models import SETTINGS_ID, Pengaturan
from app.services.cee_invitation import (
    DEFAULT_TEMPLATE_EMAIL,
    DEFAULT_TEMPLATE_EMAIL_SUBJECT,
    DEFAULT_TEMPLATE_WA,
)

router = APIRouter(prefix="/pengaturan", tags=["pengaturan"])


def get_pengaturan(session: Session) -> Pengaturan:
    """Ambil baris pengaturan; dibuat dengan nilai bawaan bila belum ada."""
    obj = session.get(Pengaturan, SETTINGS_ID)
    if not obj:
        obj = Pengaturan(id=SETTINGS_ID, tahun_default=settings.TAHUN_ANGGARAN)
        session.add(obj)
        session.commit()
        session.refresh(obj)
    return obj


def survei_window(obj: Pengaturan) -> dict[str, Any]:
    """Status jadwal survei hari ini.

    `alasan` = None bila terbuka; selain itu berisi pesan siap tampil.
    Batas tanggal bersifat inklusif dan boleh kosong (berarti tanpa batas).
    """
    hari_ini = today_wib()
    mulai, selesai = obj.survei_mulai, obj.survei_selesai
    if not obj.survei_aktif:
        alasan = obj.survei_pesan_tutup or "Survei sedang ditutup oleh admin."
    elif mulai and hari_ini < mulai:
        alasan = f"Survei dibuka mulai {mulai.strftime('%d-%m-%Y')}."
    elif selesai and hari_ini > selesai:
        alasan = f"Survei telah ditutup pada {selesai.strftime('%d-%m-%Y')}."
    else:
        alasan = None
    return {
        "dibuka": alasan is None,
        "alasan": alasan,
        "mulai": mulai.isoformat() if mulai else None,
        "selesai": selesai.isoformat() if selesai else None,
    }


def tahun_aktif(session: Session) -> int:
    """Tahun penilaian default (fallback ke TAHUN_ANGGARAN pada .env)."""
    return get_pengaturan(session).tahun_default or settings.TAHUN_ANGGARAN


def _to_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        raise HTTPException(400, f"Tanggal tidak valid: {value}") from None


@router.get("")
def read(session: Session = Depends(get_session)):
    obj = get_pengaturan(session)
    data = obj.model_dump()
    data["updated_at"] = to_wib_iso(obj.updated_at)
    return {
        **data,
        "default_template_email_subject": DEFAULT_TEMPLATE_EMAIL_SUBJECT,
        "default_template_email": DEFAULT_TEMPLATE_EMAIL,
        "default_template_wa": DEFAULT_TEMPLATE_WA,
        "survei_status": survei_window(obj),
    }


@router.put("")
def update(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = AdminDep,
):
    obj = get_pengaturan(session)

    if "tahun_default" in payload:
        raw = payload.get("tahun_default")
        if raw in (None, ""):
            obj.tahun_default = None
        else:
            try:
                tahun = int(raw)
            except (TypeError, ValueError):
                raise HTTPException(400, "Tahun tidak valid") from None
            if not 2000 <= tahun <= 2100:
                raise HTTPException(400, "Tahun harus antara 2000 dan 2100")
            obj.tahun_default = tahun

    if "survei_mulai" in payload:
        obj.survei_mulai = _to_date(payload.get("survei_mulai"))
    if "survei_selesai" in payload:
        obj.survei_selesai = _to_date(payload.get("survei_selesai"))
    if obj.survei_mulai and obj.survei_selesai and obj.survei_mulai > obj.survei_selesai:
        raise HTTPException(400, "Tanggal mulai tidak boleh melewati tanggal selesai")

    if "survei_aktif" in payload:
        obj.survei_aktif = 1 if payload.get("survei_aktif") else 0
    if "survei_pesan_tutup" in payload:
        pesan = (payload.get("survei_pesan_tutup") or "").strip()
        obj.survei_pesan_tutup = pesan or None

    if "template_email_subject" in payload:
        val = (payload.get("template_email_subject") or "").strip()
        obj.template_email_subject = val or None
    if "template_email" in payload:
        val = (payload.get("template_email") or "").strip()
        obj.template_email = val or None
    if "template_wa" in payload:
        val = (payload.get("template_wa") or "").strip()
        obj.template_wa = val or None

    if "ai_provider" in payload:
        val = (payload.get("ai_provider") or "").strip()
        obj.ai_provider = val or None
    if "ai_model" in payload:
        val = (payload.get("ai_model") or "").strip()
        obj.ai_model = val or None
    if "ai_api_key" in payload:
        val = payload.get("ai_api_key")
        if val is not None:
            val = str(val).strip()
            if val == "":
                obj.ai_api_key = None
            elif not val.startswith("••••"):
                obj.ai_api_key = val

    obj.updated_at = now_wib()
    obj.updated_by = user.get("username")
    session.add(obj)
    session.commit()
    session.refresh(obj)
    data = obj.model_dump()
    data["updated_at"] = to_wib_iso(obj.updated_at)
    return {
        **data,
        "default_template_email_subject": DEFAULT_TEMPLATE_EMAIL_SUBJECT,
        "default_template_email": DEFAULT_TEMPLATE_EMAIL,
        "default_template_wa": DEFAULT_TEMPLATE_WA,
        "survei_status": survei_window(obj),
    }
