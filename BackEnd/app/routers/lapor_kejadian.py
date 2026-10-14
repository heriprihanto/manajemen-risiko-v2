"""Router untuk Halaman Publik Lapor Kejadian dan Menu Approval Kejadian."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.datetime_utils import now_wib
from app.core.security import current_user as internal_user
from app.db import get_session
from app.models import (
    LaporKejadian,
    MonitoringRiskEvent,
    Opd,
    Risiko,
)
from app.services.firebase_auth import current_user as fb_user
from app.models.tata_kelola import KejadianTautan

router = APIRouter(tags=["lapor-kejadian"])


# ==============================================================================
# SCHEMAS
# ==============================================================================

class LaporKejadianCreate(BaseModel):
    tahun: int
    opd_id: int
    no_hp: str
    nama_lengkap: str
    uraian_kejadian: str
    waktu_kejadian: str
    tempat: str
    pemicu: str


class ApprovalUpdate(BaseModel):
    status: Literal["pending", "disetujui", "ditolak"]
    catatan_validasi: str | None = None
    risiko_id: int | None = None
    salin_ke_form10: bool = False


# ==============================================================================
# 1. ENDPOINT PUBLIK / PEGAWAI OPD (FIREBASE AUTH)
# ==============================================================================

@router.get("/lapor-kejadian/opd-list")
def list_opd_public(session: Session = Depends(get_session)):
    """Daftar OPD aktif untuk dropdown pilihan di form publik."""
    rows = session.exec(
        select(Opd)
        .where(Opd.aktif == 1)
        .order_by(Opd.nama_pd)
    ).all()
    return [
        {"id": r.id_sub_pd, "nama": r.nama_pd, "kode": r.kode}
        for r in rows
    ]


@router.post("/lapor-kejadian")
def submit_laporan_kejadian(
    body: LaporKejadianCreate,
    user: dict = Depends(fb_user),
    session: Session = Depends(get_session),
):
    """Kirim laporan kejadian risiko oleh pegawai OPD (login Firebase)."""
    # Validasi keberadaan OPD
    opd = session.get(Opd, body.opd_id)
    if not opd:
        raise HTTPException(404, "OPD tidak ditemukan")

    item = LaporKejadian(
        tahun=body.tahun,
        opd_id=body.opd_id,
        no_hp=body.no_hp.strip(),
        nama_lengkap=body.nama_lengkap.strip(),
        uraian_kejadian=body.uraian_kejadian.strip(),
        waktu_kejadian=body.waktu_kejadian.strip(),
        tempat=body.tempat.strip(),
        pemicu=body.pemicu.strip(),
        reporter_email=user.get("email"),
        reporter_uid=user.get("uid"),
        status="pending",
        created_at=now_wib(),
        updated_at=now_wib(),
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return {
        "status": "success",
        "message": "Laporan kejadian berhasil dikirim dan menunggu validasi pengelola risiko",
        "data": item,
    }


@router.get("/lapor-kejadian/my")
def get_my_laporan(
    user: dict = Depends(fb_user),
    session: Session = Depends(get_session),
):
    """Riwayat laporan yang dikirimkan oleh pengguna Firebase saat ini."""
    uid = user.get("uid")
    email = user.get("email")

    query = select(LaporKejadian).where(
        (LaporKejadian.reporter_uid == uid) | (LaporKejadian.reporter_email == email)
    ).order_by(LaporKejadian.created_at.desc())

    items = session.exec(query).all()
    result = []
    for it in items:
        opd = session.get(Opd, it.opd_id)
        d = it.model_dump()
        d["nama_opd"] = opd.nama_pd if opd else "-"
        result.append(d)
    return result


# ==============================================================================
# 2. ENDPOINT INTERNAL (MENU APPROVAL KEJADIAN)
# ==============================================================================

@router.get("/approval-kejadian")
def list_approval_kejadian(
    tahun: int | None = None,
    opd_id: int | None = None,
    status: str | None = None,
    user: dict = Depends(internal_user),
    session: Session = Depends(get_session),
):
    """Daftar laporan kejadian masuk untuk divalidasi oleh pengelola risiko."""
    query = select(LaporKejadian)

    # Scoping per OPD jika bukan admin
    is_admin = user.get("role_id") == 1
    allowed_opds = user.get("opds") or []

    if not is_admin:
        if not allowed_opds:
            return []
        if opd_id and opd_id in allowed_opds:
            query = query.where(LaporKejadian.opd_id == opd_id)
        else:
            query = query.where(LaporKejadian.opd_id.in_(allowed_opds))
    elif opd_id:
        query = query.where(LaporKejadian.opd_id == opd_id)

    if tahun:
        query = query.where(LaporKejadian.tahun == tahun)

    if status and status != "all":
        query = query.where(LaporKejadian.status == status)

    query = query.order_by(LaporKejadian.created_at.desc())
    items = session.exec(query).all()

    result = []
    for it in items:
        opd = session.get(Opd, it.opd_id)
        risiko = session.get(Risiko, it.risiko_id) if it.risiko_id else None
        d = it.model_dump()
        d["nama_opd"] = opd.nama_pd if opd else "-"
        d["uraian_risiko"] = risiko.uraian_risiko if risiko else None
        d["kode_risiko"] = risiko.kode_risiko if risiko else None
        result.append(d)
    return result


@router.get("/approval-kejadian/{id}")
def get_detail_approval(
    id: int,
    user: dict = Depends(internal_user),
    session: Session = Depends(get_session),
):
    """Ambil rincian laporan kejadian."""
    item = session.get(LaporKejadian, id)
    if not item:
        raise HTTPException(404, "Laporan kejadian tidak ditemukan")

    # Hak akses OPD
    is_admin = user.get("role_id") == 1
    allowed_opds = user.get("opds") or []
    if not is_admin and item.opd_id not in allowed_opds:
        raise HTTPException(403, "Anda tidak memiliki akses ke OPD ini")

    opd = session.get(Opd, item.opd_id)
    risiko = session.get(Risiko, item.risiko_id) if item.risiko_id else None
    d = item.model_dump()
    d["nama_opd"] = opd.nama_pd if opd else "-"
    d["uraian_risiko"] = risiko.uraian_risiko if risiko else None
    d["kode_risiko"] = risiko.kode_risiko if risiko else None
    return d


@router.put("/approval-kejadian/{id}/status")
def update_status_approval(
    id: int,
    body: ApprovalUpdate,
    user: dict = Depends(internal_user),
    session: Session = Depends(get_session),
):
    """Validasi status laporan kejadian (Disetujui / Ditolak) oleh pengelola risiko."""
    item = session.exec(select(LaporKejadian).where(LaporKejadian.id == id).with_for_update()).first()
    if not item:
        raise HTTPException(404, "Laporan kejadian tidak ditemukan")

    is_admin = user.get("role_id") == 1
    allowed_opds = user.get("opds") or []
    if not is_admin and item.opd_id not in allowed_opds:
        raise HTTPException(403, "Anda tidak memiliki akses ke OPD ini")

    if body.risiko_id:
        risk = session.get(Risiko, body.risiko_id)
        if not risk or risk.opd_id != item.opd_id or risk.tahun != item.tahun:
            raise HTTPException(422, "Risiko harus berasal dari OPD dan tahun laporan yang sama")
    linked = session.exec(select(KejadianTautan).where(KejadianTautan.laporan_id == id)).first()
    if linked and (body.risiko_id != item.risiko_id or body.status != "disetujui"):
        raise HTTPException(409, "Laporan sudah menjadi kejadian terverifikasi; tautan dan status harus dipertahankan")
    was_approved = item.status == "disetujui" and item.risiko_id == body.risiko_id
    item.status = body.status
    item.catatan_validasi = body.catatan_validasi
    item.risiko_id = body.risiko_id
    item.validated_by = user.get("id")
    item.validated_by_name = user.get("display_name") or user.get("username")
    item.validated_at = now_wib()
    item.updated_at = now_wib()

    # Jika disetujui dan dipilih salin ke Form 10 (Monitoring Risk Event)
    if body.status == "disetujui" and body.salin_ke_form10 and body.risiko_id and not linked:
        description = f"Tempat: {item.tempat}. Dilaporkan oleh: {item.nama_lengkap} ({item.no_hp})"
        try:
            tgl = datetime.strptime(item.waktu_kejadian[:10], "%Y-%m-%d").date()
        except ValueError:
            tgl = now_wib().date()
        # Kenali salinan versi lama yang belum mempunyai baris tautan.
        legacy = session.exec(select(MonitoringRiskEvent).where(
            MonitoringRiskEvent.risiko_id == body.risiko_id,
            MonitoringRiskEvent.tanggal_terjadi == tgl,
            MonitoringRiskEvent.sebab_kejadian == item.pemicu,
            MonitoringRiskEvent.dampak_kejadian == item.uraian_kejadian,
            MonitoringRiskEvent.keterangan_kejadian == description,
        )).all() if was_approved else []
        if len(legacy) > 1:
            raise HTTPException(409, "Terdapat beberapa salinan kejadian lama; periksa duplikasi sebelum menautkan")
        event = legacy[0] if legacy else MonitoringRiskEvent(
            risiko_id=body.risiko_id,
            tanggal_terjadi=tgl,
            sebab_kejadian=item.pemicu,
            dampak_kejadian=item.uraian_kejadian,
            keterangan_kejadian=description,
            updated_at=now_wib(),
        )
        session.add(event)
        session.flush()
        session.add(KejadianTautan(laporan_id=id, event_id=event.id))

    session.add(item)
    session.commit()
    session.refresh(item)
    return {
        "status": "success",
        "message": f"Status laporan berhasil diperbarui menjadi {item.status}",
        "data": item,
    }


@router.delete("/approval-kejadian/{id}")
def delete_approval_kejadian(
    id: int,
    user: dict = Depends(internal_user),
    session: Session = Depends(get_session),
):
    """Hapus laporan kejadian."""
    item = session.get(LaporKejadian, id)
    if not item:
        raise HTTPException(404, "Laporan kejadian tidak ditemukan")

    is_admin = user.get("role_id") == 1
    allowed_opds = user.get("opds") or []
    if not is_admin and item.opd_id not in allowed_opds:
        raise HTTPException(403, "Anda tidak memiliki akses ke OPD ini")

    if session.exec(select(KejadianTautan).where(KejadianTautan.laporan_id == id)).first():
        raise HTTPException(409, "Laporan sudah ditautkan ke kejadian; riwayat harus dipertahankan")
    session.delete(item)
    session.commit()
    return {"status": "success", "message": "Laporan kejadian berhasil dihapus"}
