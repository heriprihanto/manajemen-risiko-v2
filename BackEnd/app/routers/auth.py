"""Autentikasi pengguna internal (Admin / OPD) berbasis tabel sso_users + JWT."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import Session

from app.core import captcha
from app.core.security import UserDep, create_access_token
from app.db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

# Verifikasi kredensial lewat fungsi database encode_passwd(username, password).
LOGIN_SQL = text(
    """
    SELECT id, username, role_id, opds, display_name, deleted, banned, active
    FROM public.sso_users u
    WHERE u.username = :username
      AND u.password = encode_passwd(:username, :password)
    LIMIT 1
    """
)


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_id: str | None = None
    captcha_answer: str | None = None


def _user_payload(row) -> dict:
    return {
        "id": row.id,
        "username": row.username,
        "role_id": row.role_id,
        # opds: array id OPD (id_sub_pd). Admin (role_id=1) tak dibatasi OPD.
        "opds": list(row.opds) if row.opds else [],
        "display_name": row.display_name,
    }


@router.get("/captcha")
def get_captcha():
    """Terbitkan captcha baru (id + gambar SVG). Publik."""
    return captcha.generate()


@router.post("/login")
def login(body: LoginRequest, session: Session = Depends(get_session)):
    # Verifikasi captcha lebih dulu (sekali pakai) sebelum cek kredensial.
    if not captcha.verify(body.captcha_id, body.captcha_answer):
        raise HTTPException(400, "Kode captcha salah atau kedaluwarsa")
    row = session.execute(
        LOGIN_SQL, {"username": body.username, "password": body.password}
    ).first()
    if row is None:
        raise HTTPException(401, "Username atau password salah")
    if row.deleted:
        raise HTTPException(403, "Akun telah dihapus")
    if row.banned:
        raise HTTPException(403, "Akun diblokir")
    if row.active is not None and row.active == 0:
        raise HTTPException(403, "Akun belum aktif")

    user = _user_payload(row)
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me")
def me(user: dict = UserDep):
    return user
