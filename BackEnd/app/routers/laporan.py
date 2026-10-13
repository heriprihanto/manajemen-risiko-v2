"""Ekspor laporan ke Excel (.xlsx) — isi & tampilan mengikuti Cetak Laporan."""
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.db import get_session
from app.models.master import Opd
from app.services.docx_rtp import ALL_FORMS, generate_rtp_docx
from app.services.excel_laporan import SECTION_KEYS, build_workbook

router = APIRouter(prefix="/laporan", tags=["laporan"])

XLSX_MIME = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
DOCX_MIME = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


@router.get("/excel")
def export_excel(
    opd_id: int,
    tahun: int,
    forms: str | None = None,
    session: Session = Depends(get_session),
):
    """Unduh laporan sebagai workbook: satu sheet per form.

    `forms` = daftar kunci bagian dipisah koma (mis. `f3a,f3b`); kosong = semua.
    """
    keys = [k.strip() for k in (forms or "").split(",") if k.strip()]
    unknown = [k for k in keys if k not in SECTION_KEYS]
    if unknown:
        raise HTTPException(400, f"Form tidak dikenal: {', '.join(unknown)}")

    buf = build_workbook(session, opd_id, tahun, keys or None)
    nama = f"Laporan Manajemen Risiko {tahun}.xlsx"
    return StreamingResponse(
        buf,
        media_type=XLSX_MIME,
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{quote(nama)}"
            )
        },
    )


@router.get("/rtp-docx")
def export_rtp_docx(
    opd_id: int,
    tahun: int,
    forms: str | None = None,
    include_main: bool = True,
    session: Session = Depends(get_session),
):
    """Generate dan unduh Dokumen Rencana Tindak Pengendalian (RTP) dalam format Word (.docx).

    Menggabungkan template dokumen utama (Cover, Bab I - V, Cover Kertas Kerja)
    dengan lampiran printout Form 1.a sampai Form 10.
    """
    keys = [k.strip() for k in (forms or "").split(",") if k.strip()]
    unknown = [k for k in keys if k not in ALL_FORMS]
    if unknown:
        raise HTTPException(400, f"Form tidak dikenal: {', '.join(unknown)}")

    buf = generate_rtp_docx(session, opd_id, tahun, keys or None, include_main_doc=include_main)
    opd = session.get(Opd, opd_id)
    opd_str = (opd.nama_pd if opd and opd.nama_pd else f"OPD_{opd_id}").replace(" ", "_")
    nama = f"Dokumen_RTP_{opd_str}_{tahun}.docx"
    return StreamingResponse(
        buf,
        media_type=DOCX_MIME,
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{quote(nama)}"
            )
        },
    )

