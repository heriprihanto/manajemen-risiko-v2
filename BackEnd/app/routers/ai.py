"""Router AI Assistant — endpoint untuk fitur AI bantu rumus risiko, saran RTP, dan chat copilot.

Semua endpoint memerlukan autentikasi. Konfigurasi AI (provider, API key, model)
disimpan di tr_pengaturan dan dikelola Admin lewat halaman Pengaturan Aplikasi.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session

from app.core.security import UserDep
from app.db import get_session
from app.models import Pengaturan
from app.models.pengaturan import SETTINGS_ID
from app.services.ai_assistant import (
    build_chat_messages,
    build_risk_prompt,
    build_rtp_prompt,
    call_llm,
    parse_json_from_llm,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


def _get_ai_config(session: Session) -> dict:
    """Ambil konfigurasi AI dari pengaturan. Raise 503 bila belum dikonfigurasi."""
    obj = session.get(Pengaturan, SETTINGS_ID)
    if not obj:
        raise HTTPException(503, "Pengaturan aplikasi belum diinisialisasi")

    provider = getattr(obj, "ai_provider", None)
    api_key = getattr(obj, "ai_api_key", None)
    model = getattr(obj, "ai_model", None)

    if provider == "hermes":
        return {
            "provider": "hermes",
            "api_key": api_key or "local",
            "model": model or "gpt-6-astra",
        }

    if not provider or not api_key:
        raise HTTPException(
            503,
            "Fitur AI belum dikonfigurasi. Admin perlu mengatur Provider dan API Key di halaman Pengaturan.",
        )

    return {
        "provider": provider,
        "api_key": api_key,
        "model": model or "",
    }


@router.get("/status")
def ai_status(session: Session = Depends(get_session)):
    """Cek apakah AI sudah dikonfigurasi (tanpa membocorkan API key)."""
    obj = session.get(Pengaturan, SETTINGS_ID)
    provider = getattr(obj, "ai_provider", None) if obj else None
    api_key = getattr(obj, "ai_api_key", None) if obj else None
    model = getattr(obj, "ai_model", None) if obj else None
    configured = bool((provider == "hermes") or (provider and api_key))
    return {
        "configured": configured,
        "provider": provider if configured else None,
        "model": (model or "gpt-6-astra") if provider == "hermes" else (model if configured else None),
    }


@router.post("/generate-risk")
async def generate_risk(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Generate rumusan risiko dari sasaran/kegiatan menggunakan AI.

    Body: { sasaran: str, context?: { opd, jenis_risiko, tahun } }
    """
    sasaran = (payload.get("sasaran") or "").strip()
    if not sasaran:
        raise HTTPException(400, "Sasaran/kegiatan tidak boleh kosong")

    config = _get_ai_config(session)
    context = payload.get("context")
    messages = build_risk_prompt(sasaran, context)

    try:
        raw = await call_llm(
            provider=config["provider"],
            api_key=config["api_key"],
            model=config["model"],
            messages=messages,
        )
    except Exception as e:
        logger.exception("AI generate-risk error")
        raise HTTPException(502, f"Gagal menghubungi layanan AI: {e}") from e

    parsed = parse_json_from_llm(raw)
    return {"suggestions": parsed or [], "raw": raw}


@router.post("/suggest-rtp")
async def suggest_rtp(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Saran Rencana Tindak Pengendalian (RTP) berdasarkan data risiko.

    Body: { risk_data: { uraian_risiko, kode_risiko, level_risiko, pemilik_risiko,
                          celah_pengendalian, pengendalian_ada },
            context?: { opd, tahun } }
    """
    risk_data = payload.get("risk_data")
    if not risk_data or not risk_data.get("uraian_risiko"):
        raise HTTPException(400, "Data risiko (uraian_risiko) tidak boleh kosong")

    config = _get_ai_config(session)
    context = payload.get("context")
    messages = build_rtp_prompt(risk_data, context)

    try:
        raw = await call_llm(
            provider=config["provider"],
            api_key=config["api_key"],
            model=config["model"],
            messages=messages,
        )
    except Exception as e:
        logger.exception("AI suggest-rtp error")
        raise HTTPException(502, f"Gagal menghubungi layanan AI: {e}") from e

    parsed = parse_json_from_llm(raw)
    return {"suggestions": parsed or [], "raw": raw}


@router.post("/suggest-treated-risk")
async def suggest_treated_risk(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Saran Level Treated Risk (Kemungkinan & Dampak) setelah adanya RTP.

    Body: { risk_data: { uraian_risiko, level_inheren, kemungkinan_inheren, dampak_inheren,
                          pengendalian_ada, respon_risiko, rencana_tindak },
            context?: { opd, tahun } }
    """
    risk_data = payload.get("risk_data")
    if not risk_data or not risk_data.get("uraian_risiko"):
        raise HTTPException(400, "Data risiko tidak boleh kosong")

    config = _get_ai_config(session)
    context = payload.get("context")
    from app.services.ai_assistant import build_treated_prompt
    messages = build_treated_prompt(risk_data, context)

    try:
        raw = await call_llm(
            provider=config["provider"],
            api_key=config["api_key"],
            model=config["model"],
            messages=messages,
        )
    except Exception as e:
        logger.exception("AI suggest-treated-risk error")
        raise HTTPException(502, f"Gagal menghubungi layanan AI: {e}") from e

    parsed = parse_json_from_llm(raw)
    result = parsed[0] if isinstance(parsed, list) and parsed else parsed
    return {"suggestion": result or {}, "raw": raw}


@router.post("/chat")
async def chat(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Chat copilot: tanya jawab umum tentang manajemen risiko.

    Body: { message: str, history?: [{ role, content }], context?: { opd, tahun, ... } }
    """
    user_message = (payload.get("message") or "").strip()
    if not user_message:
        raise HTTPException(400, "Pesan tidak boleh kosong")

    config = _get_ai_config(session)
    history = payload.get("history")
    context = payload.get("context")
    messages = build_chat_messages(user_message, history, context)

    try:
        reply = await call_llm(
            provider=config["provider"],
            api_key=config["api_key"],
            model=config["model"],
            messages=messages,
        )
    except Exception as e:
        logger.exception("AI chat error")
        raise HTTPException(502, f"Gagal menghubungi layanan AI: {e}") from e

    return {"reply": reply}


@router.post("/test-connection")
async def test_connection(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Tes koneksi ke AI provider dengan kredensial yang diberikan atau yang tersimpan."""
    provider = payload.get("provider")
    api_key = payload.get("api_key")
    model = payload.get("model") or ""

    # Jika api_key tidak dikirim (misal tetap bertopeng ••••), ambil dari database
    if not api_key or str(api_key).startswith("••••"):
        obj = session.get(Pengaturan, SETTINGS_ID)
        if obj and obj.ai_api_key:
            api_key = obj.ai_api_key
            if not provider and obj.ai_provider:
                provider = obj.ai_provider

    if provider == "hermes":
        api_key = api_key or "local"
        if not model:
            model = "gpt-6-astra"

    if not provider or not api_key:
        raise HTTPException(400, "Provider dan API Key harus diisi untuk pengujian")

    try:
        reply = await call_llm(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=[
                {"role": "system", "content": "Jawab singkat dalam satu kalimat."},
                {"role": "user", "content": "Koneksi berhasil! Katakan halo Manajemen Risiko."},
            ],
            max_tokens=100,
        )
        return {"success": True, "message": "Koneksi ke AI provider berhasil!", "reply": reply}
    except Exception as e:
        logger.exception("AI test connection error")
        raise HTTPException(400, f"Koneksi gagal: {str(e)}") from e
