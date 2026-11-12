"""Router CRUD untuk Unit Pemilik Risiko (UPR)."""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.datetime_utils import now_wib
from app.core.security import UserDep
from app.db import get_session
from app.models.master import Opd
from app.models.upr import Upr

router = APIRouter(prefix="/upr", tags=["upr"])

STANDARD_ESELON = [
    "Eselon II.a",
    "Eselon II.b",
    "Eselon III.a",
    "Eselon III.b",
    "Eselon IV.a",
    "Eselon IV.b",
    "Non-Eselon / JF",
]

STANDARD_TINGKAT_ORGANISASI = [
    "UPR tingkat pemerintah daerah",
    "UPR tingkat unit Eselon II",
    "UPR tingkat unit Eselon III dan IV",
]

STANDARD_JABATAN_UPR = [
    "Ketua",
    "Koordinator Teknis",
    "Anggota",
]


@router.get("/stats")
def get_upr_stats(opd_id: int | None = None, session: Session = Depends(get_session)):
    """Mengambil ringkasan statistik Unit Pemilik Risiko (UPR)."""
    stmt = select(Upr)
    if opd_id:
        stmt = stmt.where(Upr.opd_id == opd_id)
    all_rows = session.exec(stmt).all()

    total = len(all_rows)
    aktif = sum(1 for r in all_rows if (r.status or "").lower() == "aktif")
    tidak_aktif = sum(1 for r in all_rows if (r.status or "").lower() != "aktif")

    eselon_ii = sum(1 for r in all_rows if (r.eselon or "").startswith("Eselon II.") or (r.eselon or "") == "Eselon II")
    eselon_iii = sum(1 for r in all_rows if (r.eselon or "").startswith("Eselon III.") or (r.eselon or "") == "Eselon III")
    eselon_iv = sum(1 for r in all_rows if (r.eselon or "").startswith("Eselon IV.") or (r.eselon or "") == "Eselon IV")
    non_eselon = total - (eselon_ii + eselon_iii + eselon_iv)

    return {
        "total": total,
        "aktif": aktif,
        "tidak_aktif": tidak_aktif,
        "eselon_ii": eselon_ii,
        "eselon_iii": eselon_iii,
        "eselon_iv": eselon_iv,
        "non_eselon": non_eselon,
    }


@router.get("/options")
def get_upr_options():
    """Daftar standar opsi pilihan untuk form & filter UPR."""
    return {
        "eselon": STANDARD_ESELON,
        "tingkat_organisasi": STANDARD_TINGKAT_ORGANISASI,
        "jabatan_upr": STANDARD_JABATAN_UPR,
    }


@router.get("")
def list_upr(
    opd_id: int | None = None,
    search: str | None = None,
    eselon: str | None = None,
    tingkat_organisasi: str | None = None,
    jabatan_upr: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    session: Session = Depends(get_session),
):
    """Mengambil daftar personil/pejabat UPR dengan filter pencarian dan OPD."""
    stmt = (
        select(Upr, Opd.nama_pd, Opd.nama_pd_singkat)
        .outerjoin(Opd, Upr.opd_id == Opd.id_sub_pd)
    )

    if opd_id:
        stmt = stmt.where(Upr.opd_id == opd_id)

    if search:
        s = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Upr.nip.ilike(s),
                Upr.nama.ilike(s),
                Upr.jabatan.ilike(s),
                Upr.tingkat_organisasi.ilike(s),
                Upr.jabatan_upr.ilike(s),
                Upr.keterangan.ilike(s),
                Opd.nama_pd.ilike(s),
            )
        )

    if eselon:
        stmt = stmt.where(Upr.eselon == eselon)

    if tingkat_organisasi:
        stmt = stmt.where(Upr.tingkat_organisasi == tingkat_organisasi)

    if jabatan_upr:
        stmt = stmt.where(Upr.jabatan_upr == jabatan_upr)

    if status:
        stmt = stmt.where(Upr.status == status)

    stmt = stmt.order_by(Upr.tingkat_organisasi.asc(), Upr.eselon.asc(), Upr.nama.asc())

    # Total count
    count_stmt = select(func.count(Upr.id))
    if opd_id:
        count_stmt = count_stmt.where(Upr.opd_id == opd_id)
    if search:
        s = f"%{search.strip()}%"
        count_stmt = (
            count_stmt.outerjoin(Opd, Upr.opd_id == Opd.id_sub_pd)
            .where(
                or_(
                    Upr.nip.ilike(s),
                    Upr.nama.ilike(s),
                    Upr.jabatan.ilike(s),
                    Upr.tingkat_organisasi.ilike(s),
                    Upr.jabatan_upr.ilike(s),
                    Upr.keterangan.ilike(s),
                    Opd.nama_pd.ilike(s),
                )
            )
        )
    if eselon:
        count_stmt = count_stmt.where(Upr.eselon == eselon)
    if tingkat_organisasi:
        count_stmt = count_stmt.where(Upr.tingkat_organisasi == tingkat_organisasi)
    if jabatan_upr:
        count_stmt = count_stmt.where(Upr.jabatan_upr == jabatan_upr)
    if status:
        count_stmt = count_stmt.where(Upr.status == status)

    total = session.exec(count_stmt).one()

    # Pagination
    p = page if isinstance(page, int) else 1
    pp = per_page if isinstance(per_page, int) else 50
    offset = (p - 1) * pp
    stmt = stmt.offset(offset).limit(pp)

    results = session.exec(stmt).all()
    items = []
    for upr_obj, nama_pd, nama_pd_singkat in results:
        d = upr_obj.model_dump()
        d["nama_pd"] = nama_pd or "Pemerintah Daerah / Umum"
        d["nama_pd_singkat"] = nama_pd_singkat or ""
        items.append(d)

    return {
        "items": items,
        "total": total,
        "page": p,
        "per_page": pp,
    }


@router.get("/{id}")
def get_upr_detail(id: int, session: Session = Depends(get_session)):
    """Mengambil detail satu pejabat UPR."""
    row = session.exec(
        select(Upr, Opd.nama_pd)
        .outerjoin(Opd, Upr.opd_id == Opd.id_sub_pd)
        .where(Upr.id == id)
    ).first()
    if not row:
        raise HTTPException(404, "Data UPR tidak ditemukan")
    upr_obj, nama_pd = row
    d = upr_obj.model_dump()
    d["nama_pd"] = nama_pd
    return d


@router.post("")
def create_upr(
    payload: dict = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Menambahkan data pejabat UPR baru."""
    nip = (payload.get("nip") or "").strip()
    nama = (payload.get("nama") or "").strip()
    jabatan = (payload.get("jabatan") or "").strip()
    eselon = (payload.get("eselon") or "Non-Eselon").strip()
    tingkat_organisasi = (payload.get("tingkat_organisasi") or "UPR tingkat unit Eselon II").strip()
    jabatan_upr = (payload.get("jabatan_upr") or "Anggota").strip()
    status = (payload.get("status") or "Aktif").strip()
    opd_id = payload.get("opd_id")
    keterangan = payload.get("keterangan")

    if not nip:
        raise HTTPException(400, "NIP wajib diisi")
    if not nama:
        raise HTTPException(400, "Nama wajib diisi")
    if not jabatan:
        raise HTTPException(400, "Jabatan wajib diisi")

    upr = Upr(
        opd_id=opd_id if opd_id and opd_id != 0 else None,
        nip=nip,
        nama=nama,
        jabatan=jabatan,
        eselon=eselon,
        tingkat_organisasi=tingkat_organisasi,
        jabatan_upr=jabatan_upr,
        status=status,
        keterangan=keterangan.strip() if keterangan else None,
        created_at=now_wib(),
        updated_at=now_wib(),
    )
    session.add(upr)
    session.commit()
    session.refresh(upr)

    d = upr.model_dump()
    if upr.opd_id:
        opd = session.get(Opd, upr.opd_id)
        d["nama_pd"] = opd.nama_pd if opd else None
    return d


@router.put("/{id}")
def update_upr(
    id: int,
    payload: dict = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Memperbarui data pejabat UPR."""
    upr = session.get(Upr, id)
    if not upr:
        raise HTTPException(404, "Data UPR tidak ditemukan")

    if "nip" in payload:
        nip = (payload.get("nip") or "").strip()
        if not nip:
            raise HTTPException(400, "NIP tidak boleh kosong")
        upr.nip = nip

    if "nama" in payload:
        nama = (payload.get("nama") or "").strip()
        if not nama:
            raise HTTPException(400, "Nama tidak boleh kosong")
        upr.nama = nama

    if "jabatan" in payload:
        jabatan = (payload.get("jabatan") or "").strip()
        if not jabatan:
            raise HTTPException(400, "Jabatan tidak boleh kosong")
        upr.jabatan = jabatan

    if "eselon" in payload:
        upr.eselon = (payload.get("eselon") or "Non-Eselon").strip()

    if "tingkat_organisasi" in payload:
        upr.tingkat_organisasi = (payload.get("tingkat_organisasi") or "UPR tingkat unit Eselon II").strip()

    if "jabatan_upr" in payload:
        upr.jabatan_upr = (payload.get("jabatan_upr") or "Anggota").strip()

    if "status" in payload:
        upr.status = (payload.get("status") or "Aktif").strip()

    if "opd_id" in payload:
        opd_id = payload.get("opd_id")
        upr.opd_id = opd_id if opd_id and opd_id != 0 else None

    if "keterangan" in payload:
        ket = payload.get("keterangan")
        upr.keterangan = ket.strip() if ket else None

    upr.updated_at = now_wib()
    session.add(upr)
    session.commit()
    session.refresh(upr)

    d = upr.model_dump()
    if upr.opd_id:
        opd = session.get(Opd, upr.opd_id)
        d["nama_pd"] = opd.nama_pd if opd else None
    return d


@router.delete("/{id}")
def delete_upr(
    id: int,
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Menghapus data pejabat UPR."""
    upr = session.get(Upr, id)
    if not upr:
        raise HTTPException(404, "Data UPR tidak ditemukan")
    session.delete(upr)
    session.commit()
    return {"message": "Data UPR berhasil dihapus", "id": id}


@router.post("/sync-from-opd")
def sync_upr_from_opd(
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Sinkronisasi data Kepala OPD aktif dari ta_opd ke mr_upr sebagai anggota UPR."""
    opds = session.exec(
        select(Opd).where(Opd.aktif == 1).order_by(Opd.nama_pd)
    ).all()

    existing_rows = session.exec(select(Upr.nip, Upr.opd_id, Upr.nama, Upr.id)).all()
    existing_keys = set()
    existing_map = {}
    for r in existing_rows:
        if r[0] and r[0].strip() and r[0].strip() != "-":
            k = r[0].replace(" ", "").lower()
            existing_keys.add(k)
            existing_map[k] = r[3]
        if r[1] and r[2]:
            k2 = (r[1], r[2].strip().lower())
            existing_keys.add(k2)
            existing_map[k2] = r[3]

    added = 0
    updated = 0
    for o in opds:
        nama = (o.nama_kepala or "").strip()
        nip = (o.nip_kepala or "").strip()
        if not nama or nama == "-":
            continue

        clean_nip = nip.replace(" ", "").lower() if nip else ""

        # Tentukan perkiraan tingkat organisasi, eselon, jabatan UPR
        nama_pd_lower = (o.nama_pd or "").lower()
        jabatan_lower = (o.jabatan_kepala or "").lower()

        if "sekretaris daerah" in nama_pd_lower or "sekretaris daerah" in jabatan_lower:
            eselon = "Eselon II.a"
            tingkat_org = "UPR tingkat pemerintah daerah"
            jabatan_upr = "Ketua"
        elif any(k in nama_pd_lower for k in ["dinas", "badan", "satuan polisi", "inspektorat"]):
            eselon = "Eselon II.b"
            tingkat_org = "UPR tingkat unit Eselon II"
            jabatan_upr = "Ketua"
        elif any(k in nama_pd_lower for k in ["kecamatan", "bagian"]):
            eselon = "Eselon III.a"
            tingkat_org = "UPR tingkat unit Eselon III dan IV"
            jabatan_upr = "Ketua"
        else:
            eselon = "Eselon II.b"
            tingkat_org = "UPR tingkat unit Eselon II"
            jabatan_upr = "Ketua"

        # Cek jika sudah ada: update tingkat_organisasi dan jabatan_upr jika masih default
        matched_id = existing_map.get(clean_nip) or existing_map.get((o.id_sub_pd, nama.lower()))
        if matched_id:
            existing_upr = session.get(Upr, matched_id)
            if existing_upr:
                existing_upr.tingkat_organisasi = tingkat_org
                existing_upr.jabatan_upr = jabatan_upr
                session.add(existing_upr)
                updated += 1
            continue

        jabatan = o.jabatan_kepala or f"Kepala {o.nama_pd}"
        upr_item = Upr(
            opd_id=o.id_sub_pd,
            nip=nip or "-",
            nama=nama,
            jabatan=jabatan,
            eselon=eselon,
            tingkat_organisasi=tingkat_org,
            jabatan_upr=jabatan_upr,
            status="Aktif",
            keterangan=f"Kepala {o.nama_pd_singkat or o.nama_pd} (Sinkronisasi Otomatis OPD)",
            created_at=now_wib(),
            updated_at=now_wib(),
        )
        session.add(upr_item)
        if clean_nip:
            existing_keys.add(clean_nip)
        existing_keys.add((o.id_sub_pd, nama.lower()))
        added += 1

    session.commit()
    msg = f"Berhasil menyinkronkan data pimpinan OPD ke UPR ({added} baru, {updated} diperbarui)"
    return {
        "synced": added + updated,
        "added": added,
        "updated": updated,
        "message": msg,
    }
