"""Router API untuk Laporan Rekapitulasi:
1. Rekapitulasi Kuesioner (/api/rekapitulasi/kuesioner)
2. Rekapitulasi Konteks Risiko (/api/rekapitulasi/konteks)
3. Rekapitulasi Identifikasi Risiko (/api/rekapitulasi/identifikasi)
4. Rekapitulasi Level Risiko (/api/rekapitulasi/level-risiko)
5. Ekspor Excel (/api/rekapitulasi/excel)
"""
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.db import get_session
from app.services import rekapitulasi as svc
from app.services.excel_rekapitulasi import build_rekap_workbook

router = APIRouter(prefix="/rekapitulasi", tags=["rekapitulasi"])

XLSX_MIME = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def _clean(val: Any) -> int | None:
    return val if isinstance(val, int) else None


@router.get("/kuesioner")
def rekap_kuesioner(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """1. Rekapitulasi Kuisioner (nilai jawaban dan persentase per OPD)."""
    return svc.get_rekap_kuesioner(session, tahun, _clean(opd_id))


@router.get("/konteks")
def rekap_konteks(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """2. Rekapitulasi Konteks Risiko (Strategis OPD & Operasional OPD)."""
    return svc.get_rekap_konteks(session, tahun, _clean(opd_id))


@router.get("/identifikasi")
def rekap_identifikasi(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """3. Rekapitulasi Identifikasi Risiko (Kategori Risiko, Strategis OPD, Operasional OPD)."""
    return svc.get_rekap_identifikasi(session, tahun, _clean(opd_id))


@router.get("/level-risiko")
def rekap_level_risiko(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """4. Rekapitulasi Identifikasi Risiko (Level Risiko per OPD)."""
    return svc.get_rekap_level_risiko(session, tahun, _clean(opd_id))


@router.get("/kepatuhan")
def rekap_kepatuhan(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """5. Rekapitulasi Kepatuhan & Progres Pengisian OPD (6 Tahapan)."""
    return svc.get_rekap_kepatuhan(session, tahun, _clean(opd_id))


@router.get("/realisasi-rtp")
def rekap_realisasi_rtp(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """6. Rekapitulasi Realisasi RTP (Tingkat Tindak Lanjut)."""
    return svc.get_rekap_realisasi_rtp(session, tahun, _clean(opd_id))


@router.get("/risk-event")
def rekap_risk_event(
    tahun: int = Query(..., description="Tahun penilaian"),
    opd_id: int | None = Query(None, description="Filter ID OPD (opsional)"),
    session: Session = Depends(get_session),
):
    """7. Rekapitulasi Keterjadian Risiko (Risk Event Log)."""
    return svc.get_rekap_risk_event(session, tahun, _clean(opd_id))


@router.get("/excel")
def export_excel(
    tahun: int = Query(..., description="Tahun penilaian"),
    jenis: str = Query("all", description="Jenis rekap: all, kuesioner, konteks, identifikasi, level, kepatuhan, rtp, event"),
    session: Session = Depends(get_session),
):
    """Unduh laporan rekapitulasi sebagai file Excel (.xlsx)."""
    valid_jenis = (
        "all", "kuesioner", "konteks", "identifikasi", "level",
        "kepatuhan", "rtp", "realisasi-rtp", "event", "risk-event", "keterjadian"
    )
    if jenis not in valid_jenis:
        raise HTTPException(400, f"Parameter jenis tidak valid: {jenis}")

    buf = build_rekap_workbook(session, tahun, jenis)
    nama = f"Laporan Rekapitulasi Manajemen Risiko {tahun}.xlsx"
    return StreamingResponse(
        buf,
        media_type=XLSX_MIME,
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{quote(nama)}"
            )
        },
    )
