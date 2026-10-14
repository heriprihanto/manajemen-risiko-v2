"""Router CRUD untuk Kamus Risiko (mr_kamus_risiko)."""
import re
from datetime import datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.security import UserDep, AdminDep
from app.db import get_session
from app.models.kamus import KamusRisiko

router = APIRouter(prefix="/kamus-risiko", tags=["kamus-risiko"])


@router.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    """Mengambil ringkasan statistik kamus risiko."""
    total = session.exec(select(func.count(KamusRisiko.id))).one()
    aktif = session.exec(
        select(func.count(KamusRisiko.id)).where(KamusRisiko.aktif == 1)
    ).one()
    nonaktif = session.exec(
        select(func.count(KamusRisiko.id)).where(KamusRisiko.aktif == 0)
    ).one()
    kategori_count = session.exec(
        select(func.count(func.distinct(KamusRisiko.kategori_risiko)))
    ).one()
    return {
        "total": total,
        "aktif": aktif,
        "nonaktif": nonaktif,
        "kategori_count": kategori_count,
    }


@router.get("/kategori")
def list_kategori(session: Session = Depends(get_session)):
    """Daftar kategori risiko unik untuk filter & pilihan formulir."""
    stmt = (
        select(KamusRisiko.kategori_risiko)
        .where(KamusRisiko.kategori_risiko.is_not(None))
        .distinct()
        .order_by(KamusRisiko.kategori_risiko)
    )
    categories = session.exec(stmt).all()
    return [c for c in categories if c]


PREFIX_MAP = {
    "Risiko Operasional": "RO",
    "Risiko Fraud": "RF",
    "Risiko Kebijakan": "RK",
    "Risiko Kepatuhan": "RKP",
    "Risiko Stakeholder": "RS",
    "Risiko Bencana": "RB",
}


def get_prefix_for_kategori(kategori: str | None) -> str:
    if not kategori:
        return "RO"
    kat = kategori.strip()
    if kat in PREFIX_MAP:
        return PREFIX_MAP[kat]
    words = [w for w in kat.split() if w]
    if len(words) >= 2:
        return f"{words[0][0]}{words[1][0]}".upper()
    elif len(words) == 1:
        return words[0][:2].upper()
    return "KR"


@router.get("/next-code")
def get_next_code(
    kategori: str | None = Query(None, description="Kategori risiko untuk menghitung kode ber-prefix"),
    session: Session = Depends(get_session),
):
    """Mengusulkan kode risiko dan nomor urut berikutnya berdasarkan format Kategori-nomor."""
    max_no = session.exec(select(func.max(KamusRisiko.no))).one() or 0
    next_no = int(max_no) + 1

    prefix = get_prefix_for_kategori(kategori)

    # Cari nomor kode risiko tertinggi dari format <Prefix>-xxx
    stmt = select(KamusRisiko.kode_risiko).where(
        KamusRisiko.kode_risiko.is_not(None),
        KamusRisiko.kode_risiko.like(f"{prefix}-%"),
    )
    codes = session.exec(stmt).all()
    max_num = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)", re.IGNORECASE)
    for code in codes:
        if code:
            m = pattern.search(code.strip())
            if m:
                val = int(m.group(1))
                if val > max_num:
                    max_num = val

    next_code = f"{prefix}-{max_num + 1:03d}"

    return {
        "prefix": prefix,
        "next_no": next_no,
        "next_kode_risiko": next_code,
    }


@router.get("")
def list_kamus_risiko(
    q: str | None = Query(None, description="Pencarian nama, kode, atau deskripsi"),
    kategori: str | None = Query(None, description="Filter kategori risiko"),
    aktif: int | None = Query(None, description="Filter status aktif (1/0)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=500),
    all_data: bool = Query(False, description="Ambil seluruh data tanpa paginasi"),
    session: Session = Depends(get_session),
):
    """Menampilkan daftar kamus risiko dengan pencarian, filter, dan paginasi."""
    stmt = select(KamusRisiko)

    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                KamusRisiko.nama_risiko.ilike(term),
                KamusRisiko.kode_risiko.ilike(term),
                KamusRisiko.deskripsi.ilike(term),
            )
        )

    if kategori and kategori.strip():
        stmt = stmt.where(KamusRisiko.kategori_risiko == kategori.strip())

    if aktif is not None:
        stmt = stmt.where(KamusRisiko.aktif == aktif)

    # Hitung total hasil filter
    total = session.exec(select(func.count()).select_from(stmt.subquery())).one()

    # Urutkan berdasarkan no atau id
    stmt = stmt.order_by(KamusRisiko.no.asc().nulls_last(), KamusRisiko.id.asc())

    if not all_data:
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

    items = session.exec(stmt).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page if not all_data else total,
        "pages": (total + per_page - 1) // per_page if (per_page and not all_data) else 1,
    }


@router.get("/{id}")
def get_kamus_risiko(id: int, session: Session = Depends(get_session)):
    """Mengambil satu item kamus risiko berdasarkan ID."""
    obj = session.get(KamusRisiko, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kamus risiko tidak ditemukan")
    return obj


@router.post("")
def create_kamus_risiko(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = AdminDep,
):
    """Menambah data kamus risiko baru."""
    nama_risiko = (payload.get("nama_risiko") or "").strip()
    kategori_risiko = (payload.get("kategori_risiko") or "").strip()
    if not nama_risiko:
        raise HTTPException(status_code=400, detail="Nama risiko wajib diisi")
    if not kategori_risiko:
        raise HTTPException(status_code=400, detail="Kategori risiko wajib diisi")

    # Nomor urut otomatis bila tidak disediakan
    no_val = payload.get("no")
    if no_val is None:
        max_no = session.exec(select(func.max(KamusRisiko.no))).one() or 0
        no_val = int(max_no) + 1

    # Kode risiko otomatis bila tidak disediakan (format: Kategori-nomor urut)
    kode_risiko = payload.get("kode_risiko")
    if not kode_risiko or not str(kode_risiko).strip():
        prefix = get_prefix_for_kategori(kategori_risiko)
        stmt = select(KamusRisiko.kode_risiko).where(
            KamusRisiko.kode_risiko.is_not(None),
            KamusRisiko.kode_risiko.like(f"{prefix}-%"),
        )
        codes = session.exec(stmt).all()
        max_num = 0
        pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)", re.IGNORECASE)
        for code in codes:
            if code:
                m = pattern.search(code.strip())
                if m:
                    val = int(m.group(1))
                    if val > max_num:
                        max_num = val
        kode_risiko = f"{prefix}-{max_num + 1:03d}"
    else:
        kode_risiko = str(kode_risiko).strip()

    obj = KamusRisiko(
        no=int(no_val),
        nama_klp=(payload.get("nama_klp") or "Kota Tegal").strip(),
        kategori_risiko=kategori_risiko,
        nama_risiko=nama_risiko,
        deskripsi=payload.get("deskripsi") or None,
        aktif=1 if payload.get("aktif") in (1, True, "1", "true") else 0,
        kode_risiko=kode_risiko,
        created_at=now_wib(),
        updated_at=None,
    )

    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/{id}")
def update_kamus_risiko(
    id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = AdminDep,
):
    """Memperbarui data kamus risiko."""
    obj = session.get(KamusRisiko, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kamus risiko tidak ditemukan")

    if "nama_risiko" in payload:
        val = (payload["nama_risiko"] or "").strip()
        if not val:
            raise HTTPException(status_code=400, detail="Nama risiko wajib diisi")
        obj.nama_risiko = val

    if "kategori_risiko" in payload:
        val = (payload["kategori_risiko"] or "").strip()
        if not val:
            raise HTTPException(status_code=400, detail="Kategori risiko wajib diisi")
        obj.kategori_risiko = val

    if "deskripsi" in payload:
        obj.deskripsi = payload["deskripsi"] or None

    if "kode_risiko" in payload:
        obj.kode_risiko = payload["kode_risiko"].strip() if payload["kode_risiko"] else None

    if "nama_klp" in payload:
        obj.nama_klp = (payload["nama_klp"] or "Kota Tegal").strip()

    if "no" in payload and payload["no"] is not None:
        obj.no = int(payload["no"])

    if "aktif" in payload:
        obj.aktif = 1 if payload["aktif"] in (1, True, "1", "true") else 0

    obj.updated_at = now_wib()

    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/{id}")
def delete_kamus_risiko(
    id: int,
    session: Session = Depends(get_session),
    user: dict = AdminDep,
):
    """Menghapus data kamus risiko."""
    obj = session.get(KamusRisiko, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kamus risiko tidak ditemukan")

    session.delete(obj)
    session.commit()
    return {"message": "Kamus risiko berhasil dihapus", "id": id}
