"""JWT untuk autentikasi pengguna internal (tabel sso_users).

Login memverifikasi kredensial lewat fungsi database ``encode_passwd`` lalu
menerbitkan JWT HS256 yang ditandatangani dengan ``settings.SECRET_KEY``.
Dependency :func:`current_user` mem-parse Bearer token untuk endpoint terproteksi.
"""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.config import settings


def create_access_token(subject: dict) -> str:
    """Terbitkan JWT berisi identitas pengguna (id, username, role_id, opds)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {**subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(401, "Sesi berakhir, silakan login kembali") from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(401, "Token tidak valid") from exc


def current_user(authorization: str = Header(default="")) -> dict:
    """Dependency FastAPI: verifikasi Bearer token, kembalikan klaim pengguna."""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Authorization Bearer token diperlukan")
    token = authorization.split(" ", 1)[1].strip()
    claims = decode_access_token(token)
    return {
        "id": claims.get("id"),
        "username": claims.get("username"),
        "role_id": claims.get("role_id"),
        "opds": claims.get("opds") or [],
        "display_name": claims.get("display_name"),
    }


def require_admin(user: dict = Depends(current_user)) -> dict:
    """Dependency: hanya izinkan pengguna dengan role Admin (role_id = 1)."""
    if user.get("role_id") != 1:
        raise HTTPException(403, "Akses khusus Admin")
    return user


def is_admin(user: dict) -> bool:
    return user.get("role_id") == 1


def ensure_opd_access(user: dict, opd_id: int | None) -> None:
    """Admin bebas; pengguna OPD hanya boleh mengakses OPD miliknya (field opds)."""
    if is_admin(user):
        return
    if opd_id is None or opd_id not in (user.get("opds") or []):
        raise HTTPException(403, "Anda tidak memiliki akses ke OPD ini")


def guard_record(user: dict, obj, label: str = "Data"):
    """Pastikan record ada dan (bila non-admin) milik OPD pengguna via obj.opd_id."""
    if obj is None:
        raise HTTPException(404, f"{label} tidak ditemukan")
    ensure_opd_access(user, getattr(obj, "opd_id", None))
    return obj


async def opd_scope(request: Request, user: dict = Depends(current_user)) -> dict:
    """Dependency level-router: verifikasi token + validasi opd_id yang dikirim.

    Mengambil opd_id dari query string atau body JSON dan memastikan pengguna OPD
    hanya menyentuh OPD miliknya. Endpoint tanpa opd_id (mis. konteks Pemda) hanya
    tervalidasi autentikasinya; akses per-record diperiksa di masing-masing handler.
    """
    raw = request.query_params.get("opd_id")
    if raw is None and request.method in ("POST", "PUT", "PATCH"):
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001 - body kosong / bukan JSON
            body = None
        if isinstance(body, dict) and body.get("opd_id") is not None:
            raw = body.get("opd_id")
    if raw is not None:
        try:
            opd_id = int(raw)
        except (TypeError, ValueError) as exc:
            raise HTTPException(400, "opd_id tidak valid") from exc
        ensure_opd_access(user, opd_id)
    return user


UserDep = Depends(current_user)
AdminDep = Depends(require_admin)
OpdScopeDep = Depends(opd_scope)
