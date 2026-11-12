"""Validasi sesi di penerbit; MR tidak menyimpan kunci JWT e-Monev."""
import httpx
from fastapi import HTTPException, Request

from app.core.config import settings


def check_origin(request: Request) -> None:
    if request.headers.get("origin") != settings.SSO_PUBLIC_ORIGIN:
        raise HTTPException(403, "Origin permintaan tidak diizinkan")


def session_request(request: Request, method: str = "GET") -> dict:
    token = request.cookies.get(settings.SSO_COOKIE_NAME)
    if not token:
        if method == "DELETE":
            return {}
        raise HTTPException(401, "Silakan login melalui e-Monev")
    try:
        with httpx.Client(timeout=5, follow_redirects=False, trust_env=False) as client:
            response = client.request(
                method, settings.SSO_SESSION_URL,
                cookies={settings.SSO_COOKIE_NAME: token},
                headers={"Origin": settings.SSO_PUBLIC_ORIGIN},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Layanan sesi e-Monev belum tersedia") from exc
    if method == "DELETE" and response.status_code == 204:
        return {}
    if response.status_code in (401, 403):
        raise HTTPException(response.status_code, "Sesi e-Monev tidak berlaku atau akun tidak diizinkan")
    if response.status_code != 200:
        raise HTTPException(503, "Layanan sesi e-Monev belum siap")
    try:
        user = response.json()
        # Kedua aplikasi memakai ta_opd.id_sub_pd. Identitas selalu dari server.
        if not isinstance(user, dict) or not user.get("id") or not user.get("username"):
            raise ValueError("Identitas tidak lengkap")
        role = user["role_id"]
        opds = user.get("id_opds") or []
        if type(role) is not int or not isinstance(opds, list) or any(type(i) is not int for i in opds):
            raise ValueError("Hak akses tidak valid")
        return {"id": str(user["id"]), "username": user["username"],
                "role_id": role, "opds": opds,
                "display_name": user.get("nama") or user["username"]}
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(503, "Respons sesi e-Monev tidak valid") from exc
