"""Survei CEE publik menggunakan token undangan responden."""
from typing import Any

from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.datetime_utils import now_wib, to_wib_iso
from app.db import get_session
from app.models import (
    CeeJawaban,
    CeeResponden,
    KuesionerKategori,
    KuesionerPertanyaan,
    Opd,
)
from app.routers.pengaturan import get_pengaturan, survei_window

router = APIRouter(prefix="/survei", tags=["survei"])


@router.get("/info")
def info(session: Session = Depends(get_session)):
    n = len(
        session.exec(
            select(KuesionerPertanyaan).where(KuesionerPertanyaan.aktif == 1)
        ).all()
    )
    # Tahun & jadwal mengikuti Pengaturan yang diatur Admin.
    p = get_pengaturan(session)
    return {
        "judul": "Survei Penilaian Lingkungan Pengendalian Intern (CEE)",
        "instansi": settings.PROJECT_NAME,
        "tahun": p.tahun_default or settings.TAHUN_ANGGARAN,
        "jadwal": survei_window(p),
        "jumlah_pertanyaan": n,
        "skala": [
            {"nilai": 1, "label": "Tidak Setuju"},
            {"nilai": 2, "label": "Kurang Setuju"},
            {"nilai": 3, "label": "Setuju"},
            {"nilai": 4, "label": "Sangat Setuju"},
        ],
    }


@router.get("/opd")
def opd_list(session: Session = Depends(get_session)):
    rows = session.exec(
        select(Opd).where(Opd.aktif == 1).order_by(Opd.nama_pd)
    ).all()
    return [{"id_sub_pd": o.id_sub_pd, "nama_pd": o.nama_pd} for o in rows]


@router.get("/kuesioner")
def kuesioner(session: Session = Depends(get_session)):
    kats = session.exec(
        select(KuesionerKategori).order_by(KuesionerKategori.urutan)
    ).all()
    pers = session.exec(
        select(KuesionerPertanyaan)
        .where(KuesionerPertanyaan.aktif == 1)
        .order_by(KuesionerPertanyaan.urutan)
    ).all()
    by_kat: dict[int, list] = {}
    for p in pers:
        by_kat.setdefault(p.kategori_id, []).append(
            {"id": p.id, "nomor": p.nomor, "pertanyaan": p.pertanyaan}
        )
    return [
        {"id": k.id, "kode": k.kode, "nama": k.nama, "pertanyaan": by_kat.get(k.id, [])}
        for k in kats
    ]


def token_responden(authorization: str = Header(default=""), session: Session = Depends(get_session)):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(401, "Masukkan token ID dari email undangan")
    resp = session.exec(select(CeeResponden).where(CeeResponden.token_id == token.strip())).first()
    if not resp:
        raise HTTPException(401, "Token ID tidak valid")
    return resp


@router.get("/status")
def survey_status(resp: CeeResponden = Depends(token_responden), session: Session = Depends(get_session)):
    jawaban = {j.pertanyaan_id: j.nilai for j in session.exec(
        select(CeeJawaban).where(CeeJawaban.responden_id == resp.id)).all()}
    opd = session.get(Opd, resp.opd_id)
    return {
        "submitted": resp.submitted_at is not None or resp.sumber == "survei",
        "kode_responden": resp.kode_responden, "opd_id": resp.opd_id,
        "opd_nama": opd.nama_pd if opd else None, "tahun": resp.tahun,
        "nama_responden": resp.nama_responden, "jabatan": resp.jabatan,
        "nip": resp.nip, "submitted_at": to_wib_iso(resp.submitted_at or resp.updated_at),
        "jawaban": jawaban,
        "narasi": resp.narasi,
    }


@router.post("/submit")
def submit(payload: dict[str, Any] = Body(...), resp: CeeResponden = Depends(token_responden),
           session: Session = Depends(get_session)):
    pengaturan = get_pengaturan(session)
    # Lock the invitation so simultaneous requests cannot submit it twice.
    resp = session.exec(select(CeeResponden).where(CeeResponden.id == resp.id)
                        .with_for_update().execution_options(populate_existing=True)).one()
    if resp.submitted_at is not None or resp.sumber == "survei":
        raise HTTPException(409, "Survei dengan token ini sudah dikirim")
    if resp.tahun != (pengaturan.tahun_default or settings.TAHUN_ANGGARAN):
        raise HTTPException(403, "Token bukan untuk tahun survei aktif")
    jadwal = survei_window(pengaturan)
    if not jadwal["dibuka"]:
        raise HTTPException(403, jadwal["alasan"])
    valid_pids = {p.id for p in session.exec(select(KuesionerPertanyaan)
                  .where(KuesionerPertanyaan.aktif == 1)).all()}
    jawaban = payload.get("jawaban")
    if not isinstance(jawaban, dict):
        raise HTTPException(400, "Jawaban wajib diisi")
    clean = {}
    for pid, nilai in jawaban.items():
        try:
            pid_i = int(pid)
        except (ValueError, TypeError):
            raise HTTPException(400, "Pertanyaan tidak valid") from None
        if pid_i not in valid_pids or type(nilai) is not int or not 1 <= nilai <= 4:
            raise HTTPException(400, "Jawaban tidak valid (skala 1–4)")
        clean[pid_i] = nilai
    if not valid_pids or set(clean) != valid_pids:
        raise HTTPException(400, "Lengkapi semua pertanyaan")
    for old in session.exec(select(CeeJawaban).where(CeeJawaban.responden_id == resp.id)).all():
        session.delete(old)
    for pid, nilai in clean.items():
        session.add(CeeJawaban(responden_id=resp.id, pertanyaan_id=pid, nilai=nilai))
    narasi = payload.get("narasi")
    if narasi is not None:
        resp.narasi = str(narasi).strip() or None
    resp.submitted_at = resp.updated_at = now_wib()
    resp.sumber = "survei"
    session.add(resp)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Email ini sudah mengisi survei tahun ini") from None
    return {"ok": True, "kode_responden": resp.kode_responden, "jumlah_jawaban": len(clean)}
