"""Pembangun workbook Excel (.xlsx) untuk Laporan Rekapitulasi:
Sheet 1: Rekap Kuesioner
Sheet 2: Rekap Konteks Risiko
Sheet 3: Rekap Kategori Risiko
Sheet 4: Rekap Level Risiko
"""
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.services import rekapitulasi as rk

_THIN = Side(style="thin", color="000000")
BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
FILL_HEAD = PatternFill("solid", fgColor="E2E8F0")
FILL_SUBHEAD = PatternFill("solid", fgColor="F1F5F9")
FILL_TOTAL = PatternFill("solid", fgColor="E2E8F0")

FONT_NAME = "Calibri"
FONT_NORMAL = Font(name=FONT_NAME, size=10)
FONT_BOLD = Font(name=FONT_NAME, size=10, bold=True)
FONT_TITLE = Font(name=FONT_NAME, size=12, bold=True)
FONT_SUBTITLE = Font(name=FONT_NAME, size=10, italic=True)

ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")


def _style_cell(cell, font=FONT_NORMAL, align=ALIGN_LEFT, fill=None, border=BORDER):
    cell.font = font
    cell.alignment = align
    if fill:
        cell.fill = fill
    if border:
        cell.border = border


def build_rekap_kuesioner_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 45, 18, 15, 15, 15, 15, 12, 16]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Judul
    ws.merge_cells("A1:I1")
    ws["A1"] = "REKAPITULASI HASIL KUESIONER CEE PER PERANGKAT DAERAH"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:I2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    # Header Baris 4 & 5
    ws.merge_cells("A4:A5")
    ws["A4"] = "No"
    ws.merge_cells("B4:B5")
    ws["B4"] = "Nama OPD"
    ws.merge_cells("C4:C5")
    ws["C4"] = "Jumlah Responden"

    ws.merge_cells("D4:G4")
    ws["D4"] = "Distribusi Nilai Jawaban Responden"

    ws["D5"] = "Nilai 1"
    ws["E5"] = "Nilai 2"
    ws["F5"] = "Nilai 3"
    ws["G5"] = "Nilai 4"

    ws.merge_cells("H4:H5")
    ws["H4"] = "Modus"
    ws.merge_cells("I4:I5")
    ws["I4"] = "Simpulan"

    for r in range(4, 6):
        for c in range(1, 10):
            _style_cell(ws.cell(r, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    # Data baris
    curr_row = 6
    for it in data["items"]:
        ws.cell(curr_row, 1, it["no"])
        ws.cell(curr_row, 2, it["nama_opd"])
        ws.cell(curr_row, 3, it["jumlah_responden"])
        ws.cell(curr_row, 4, f"{it['nilai_1']} ({it['persen_1']}%)" if it["total_jawaban"] else "-")
        ws.cell(curr_row, 5, f"{it['nilai_2']} ({it['persen_2']}%)" if it["total_jawaban"] else "-")
        ws.cell(curr_row, 6, f"{it['nilai_3']} ({it['persen_3']}%)" if it["total_jawaban"] else "-")
        ws.cell(curr_row, 7, f"{it['nilai_4']} ({it['persen_4']}%)" if it["total_jawaban"] else "-")
        ws.cell(curr_row, 8, it["modus"] if it["modus"] is not None else "-")
        ws.cell(curr_row, 9, it["simpulan"])

        _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
        _style_cell(ws.cell(curr_row, 3), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 4), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 5), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 6), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 7), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 8), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 9), align=ALIGN_CENTER)
        curr_row += 1

    # Baris Total
    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:B{curr_row}")
    ws.cell(curr_row, 1, "TOTAL KESELURUHAN")
    ws.cell(curr_row, 3, s["total_responden"])
    ws.cell(curr_row, 4, f"{s['nilai_1']} ({s['persen_1']}%)" if s["total_jawaban"] else "-")
    ws.cell(curr_row, 5, f"{s['nilai_2']} ({s['persen_2']}%)" if s["total_jawaban"] else "-")
    ws.cell(curr_row, 6, f"{s['nilai_3']} ({s['persen_3']}%)" if s["total_jawaban"] else "-")
    ws.cell(curr_row, 7, f"{s['nilai_4']} ({s['persen_4']}%)" if s["total_jawaban"] else "-")
    ws.cell(curr_row, 8, s["modus"] if s["modus"] is not None else "-")
    ws.cell(curr_row, 9, s["simpulan"])

    for c in range(1, 10):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)
    _style_cell(ws.cell(curr_row, 1), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)


def build_rekap_konteks_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 45, 34, 34, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:E1")
    ws["A1"] = "REKAPITULASI PENETAPAN KONTEKS RISIKO PER PERANGKAT DAERAH"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:E2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    ws["A4"] = "No"
    ws["B4"] = "Nama OPD"
    ws["C4"] = "Jumlah Konteks Risiko Strategis OPD"
    ws["D4"] = "Jumlah Konteks Risiko Operasional OPD"
    ws["E4"] = "Total Konteks"

    for c in range(1, 6):
        _style_cell(ws.cell(4, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    curr_row = 5
    for it in data["items"]:
        ws.cell(curr_row, 1, it["no"])
        ws.cell(curr_row, 2, it["nama_opd"])
        ws.cell(curr_row, 3, it["jumlah_strategis_opd"])
        ws.cell(curr_row, 4, it["jumlah_operasional_opd"])
        ws.cell(curr_row, 5, it["total_konteks"])

        _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
        _style_cell(ws.cell(curr_row, 3), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 4), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 5), font=FONT_BOLD, align=ALIGN_CENTER)
        curr_row += 1

    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:B{curr_row}")
    ws.cell(curr_row, 1, "TOTAL KESELURUHAN")
    ws.cell(curr_row, 3, s["total_strategis_opd"])
    ws.cell(curr_row, 4, s["total_operasional_opd"])
    ws.cell(curr_row, 5, s["grand_total"])

    for c in range(1, 6):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)


def build_rekap_identifikasi_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 42, 30, 18, 18, 15]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:F1")
    ws["A1"] = "REKAPITULASI IDENTIFIKASI RISIKO (KATEGORI RISIKO) PER PERANGKAT DAERAH"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:F2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    ws["A4"] = "No"
    ws["B4"] = "Nama OPD"
    ws["C4"] = "Kategori Risiko"
    ws["D4"] = "Strategis OPD"
    ws["E4"] = "Operasional OPD"
    ws["F4"] = "Total"

    for c in range(1, 7):
        _style_cell(ws.cell(4, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    curr_row = 5
    for it in data["items"]:
        k_list = it["kategori_list"]
        start_r = curr_row
        for idx, k in enumerate(k_list):
            if idx == 0:
                ws.cell(curr_row, 1, it["no"])
                ws.cell(curr_row, 2, it["nama_opd"])
            ws.cell(curr_row, 3, k["kategori_risiko"])
            ws.cell(curr_row, 4, k["strategis_opd"])
            ws.cell(curr_row, 5, k["operasional_opd"])
            ws.cell(curr_row, 6, k["total"])

            _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
            _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
            _style_cell(ws.cell(curr_row, 3), align=ALIGN_LEFT)
            _style_cell(ws.cell(curr_row, 4), align=ALIGN_CENTER)
            _style_cell(ws.cell(curr_row, 5), align=ALIGN_CENTER)
            _style_cell(ws.cell(curr_row, 6), align=ALIGN_CENTER)
            curr_row += 1

        end_r = curr_row - 1
        if end_r > start_r:
            ws.merge_cells(start_row=start_r, start_column=1, end_row=end_r, end_column=1)
            ws.merge_cells(start_row=start_r, start_column=2, end_row=end_r, end_column=2)

    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:C{curr_row}")
    ws.cell(curr_row, 1, "TOTAL KESELURUHAN")
    ws.cell(curr_row, 4, s["total_strategis_opd"])
    ws.cell(curr_row, 5, s["total_operasional_opd"])
    ws.cell(curr_row, 6, s["grand_total"])

    for c in range(1, 7):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)


def build_rekap_level_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 42, 16, 14, 14, 14, 16, 16, 15]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:I1")
    ws["A1"] = "REKAPITULASI LEVEL RISIKO PER PERANGKAT DAERAH"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:I2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A4:A5")
    ws["A4"] = "No"
    ws.merge_cells("B4:B5")
    ws["B4"] = "Nama OPD"
    ws.merge_cells("C4:H4")
    ws["C4"] = "Level Risiko"

    ws["C5"] = "Sangat Tinggi (5)"
    ws["D5"] = "Tinggi (4)"
    ws["E5"] = "Sedang (3)"
    ws["F5"] = "Rendah (2)"
    ws["G5"] = "Sangat Rendah (1)"
    ws["H5"] = "Belum Dianalisis"

    ws.merge_cells("I4:I5")
    ws["I4"] = "Total Risiko"

    for r in range(4, 6):
        for c in range(1, 10):
            _style_cell(ws.cell(r, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    curr_row = 6
    for it in data["items"]:
        ws.cell(curr_row, 1, it["no"])
        ws.cell(curr_row, 2, it["nama_opd"])
        ws.cell(curr_row, 3, it["sangat_tinggi"])
        ws.cell(curr_row, 4, it["tinggi"])
        ws.cell(curr_row, 5, it["sedang"])
        ws.cell(curr_row, 6, it["rendah"])
        ws.cell(curr_row, 7, it["sangat_rendah"])
        ws.cell(curr_row, 8, it["belum_analisis"])
        ws.cell(curr_row, 9, it["total_risiko"])

        _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
        _style_cell(ws.cell(curr_row, 3), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 4), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 5), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 6), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 7), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 8), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 9), font=FONT_BOLD, align=ALIGN_CENTER)
        curr_row += 1

    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:B{curr_row}")
    ws.cell(curr_row, 1, "TOTAL KESELURUHAN")
    ws.cell(curr_row, 3, s["sangat_tinggi"])
    ws.cell(curr_row, 4, s["tinggi"])
    ws.cell(curr_row, 5, s["sedang"])
    ws.cell(curr_row, 6, s["rendah"])
    ws.cell(curr_row, 7, s["sangat_rendah"])
    ws.cell(curr_row, 8, s["belum_analisis"])
    ws.cell(curr_row, 9, s["grand_total"])

    for c in range(1, 10):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)


def build_rekap_kepatuhan_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 42, 16, 16, 16, 16, 16, 18, 14, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:J1")
    ws["A1"] = "REKAPITULASI KEPATUHAN & PROGRES PENGISIAN MANAJEMEN RISIKO PER OPD"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:J2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    headers = [
        "No", "Nama OPD", "CEE (Form 1)", "Konteks (Form 2)",
        "Identifikasi (Form 3)", "Analisis (Form 4)", "RTP (Form 7)",
        "Pemantauan (Form 8-10)", "Progres (%)", "Status Kepatuhan"
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(4, c, h)
        _style_cell(ws.cell(4, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    curr_row = 5
    for it in data["items"]:
        ws.cell(curr_row, 1, it["no"])
        ws.cell(curr_row, 2, it["nama_opd"])
        ws.cell(curr_row, 3, f"Ada ({it['cee_count']})" if it["cee_count"] else "Belum")
        ws.cell(curr_row, 4, f"Ada ({it['konteks_count']})" if it["konteks_count"] else "Belum")
        ws.cell(curr_row, 5, f"Ada ({it['identifikasi_count']})" if it["identifikasi_count"] else "Belum")
        ws.cell(curr_row, 6, f"Ada ({it['analisis_count']})" if it["analisis_count"] else "Belum")
        ws.cell(curr_row, 7, f"Ada ({it['rtp_count']})" if it["rtp_count"] else "Belum")
        ws.cell(curr_row, 8, f"Ada ({it['pemantauan_count']})" if it["pemantauan_count"] else "Belum")
        ws.cell(curr_row, 9, f"{it['persen_progres']}%")
        ws.cell(curr_row, 10, it["status_kepatuhan"])

        _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
        for col_idx in range(3, 11):
            _style_cell(ws.cell(curr_row, col_idx), align=ALIGN_CENTER)
        curr_row += 1

    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:H{curr_row}")
    ws.cell(curr_row, 1, f"RATA-RATA PROGRES DAERAH: {s['rata_progres']}%  |  Lengkap: {s['lengkap']} OPD, Sebagian: {s['sebagian']} OPD, Belum: {s['belum_mengisi']} OPD")
    ws.cell(curr_row, 9, f"{s['rata_progres']}%")
    ws.cell(curr_row, 10, "Lengkap" if s['rata_progres'] == 100 else "Sebagian")

    for c in range(1, 11):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)


def build_rekap_realisasi_rtp_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 42, 14, 16, 14, 16, 18, 18, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:I1")
    ws["A1"] = "REKAPITULASI REALISASI RENCANA TINDAK PENGENDALIAN (RTP) PER OPD"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:I2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    headers = [
        "No", "Nama OPD", "Total Risiko", "Risiko Prioritas",
        "Target RTP", "Realisasi Selesai", "Dalam Proses / Belum",
        "Tingkat Realisasi (%)", "Status Tindak Lanjut"
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(4, c, h)
        _style_cell(ws.cell(4, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    curr_row = 5
    for it in data["items"]:
        ws.cell(curr_row, 1, it["no"])
        ws.cell(curr_row, 2, it["nama_opd"])
        ws.cell(curr_row, 3, it["total_risiko"])
        ws.cell(curr_row, 4, it["risiko_prioritas"])
        ws.cell(curr_row, 5, it["target_rtp"])
        ws.cell(curr_row, 6, it["realisasi_selesai"])
        ws.cell(curr_row, 7, it["dalam_proses"])
        ws.cell(curr_row, 8, f"{it['tingkat_realisasi']}%")
        ws.cell(curr_row, 9, it["status_tindak_lanjut"])

        _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
        for col_idx in range(3, 10):
            _style_cell(ws.cell(curr_row, col_idx), align=ALIGN_CENTER)
        curr_row += 1

    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:B{curr_row}")
    ws.cell(curr_row, 1, "TOTAL KESELURUHAN")
    ws.cell(curr_row, 3, s["total_risiko"])
    ws.cell(curr_row, 4, s["total_prioritas"])
    ws.cell(curr_row, 5, s["total_target_rtp"])
    ws.cell(curr_row, 6, s["total_realisasi_selesai"])
    ws.cell(curr_row, 7, s["total_dalam_proses"])
    ws.cell(curr_row, 8, f"{s['tingkat_realisasi_daerah']}%")
    ws.cell(curr_row, 9, f"Selesai: {s['opd_selesai']}, Proses: {s['opd_proses']}")

    for c in range(1, 10):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)


def build_rekap_risk_event_sheet(ws, data: dict):
    ws.views.sheetView[0].showGridLines = True
    col_widths = [6, 42, 14, 26, 18, 18]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.merge_cells("A1:F1")
    ws["A1"] = "REKAPITULASI KETERJADIAN RISIKO (RISK EVENT LOG) PER OPD"
    _style_cell(ws["A1"], font=FONT_TITLE, align=ALIGN_CENTER, border=None)

    ws.merge_cells("A2:F2")
    ws["A2"] = f"Tahun Penilaian: {data['tahun']}"
    _style_cell(ws["A2"], font=FONT_SUBTITLE, align=ALIGN_CENTER, border=None)

    headers = [
        "No", "Nama OPD", "Total Risiko", "Risiko Mengalami Kejadian",
        "Total Kejadian (Events)", "Status Keterjadian"
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(4, c, h)
        _style_cell(ws.cell(4, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)

    curr_row = 5
    for it in data["items"]:
        ws.cell(curr_row, 1, it["no"])
        ws.cell(curr_row, 2, it["nama_opd"])
        ws.cell(curr_row, 3, it["total_risiko"])
        ws.cell(curr_row, 4, it["risiko_terkena"])
        ws.cell(curr_row, 5, it["total_events"])
        ws.cell(curr_row, 6, it["status"])

        _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
        _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
        for col_idx in range(3, 7):
            _style_cell(ws.cell(curr_row, col_idx), align=ALIGN_CENTER)
        curr_row += 1

    s = data["summary"]
    ws.merge_cells(f"A{curr_row}:B{curr_row}")
    ws.cell(curr_row, 1, "TOTAL KESELURUHAN")
    ws.cell(curr_row, 3, s["total_risiko"])
    ws.cell(curr_row, 4, s["total_risiko_terjadi"])
    ws.cell(curr_row, 5, s["total_events"])
    ws.cell(curr_row, 6, f"Ada Kejadian: {s['opd_ada_kejadian']} OPD, Nihil: {s['opd_nihil_kejadian']} OPD")

    for c in range(1, 7):
        _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_TOTAL)

    # Jika ada log kejadian rinci, buat bagian tabel log di bawahnya
    log_rows = data.get("log_rows", [])
    if log_rows:
        curr_row += 3
        ws.cell(curr_row, 1, "LOG RINCIAN KEJADIAN RISIKO (RISK EVENT DETAIL)")
        ws.cell(curr_row, 1).font = FONT_BOLD
        curr_row += 1

        log_headers = [
            "No", "Nama OPD", "Kode Risiko", "Uraian Risiko",
            "Tanggal Kejadian", "Sebab Kejadian", "Dampak Kejadian", "Realisasi RTP"
        ]
        for c, h in enumerate(log_headers, 1):
            ws.cell(curr_row, c, h)
            _style_cell(ws.cell(curr_row, c), font=FONT_BOLD, align=ALIGN_CENTER, fill=FILL_HEAD)
        curr_row += 1

        for lr in log_rows:
            ws.cell(curr_row, 1, lr["no"])
            ws.cell(curr_row, 2, lr["nama_opd"])
            ws.cell(curr_row, 3, lr["kode_risiko"])
            ws.cell(curr_row, 4, lr["uraian_risiko"])
            ws.cell(curr_row, 5, lr["tanggal_terjadi"])
            ws.cell(curr_row, 6, lr["sebab_kejadian"])
            ws.cell(curr_row, 7, lr["dampak_kejadian"])
            ws.cell(curr_row, 8, lr["realisasi_rtp"])

            _style_cell(ws.cell(curr_row, 1), align=ALIGN_CENTER)
            _style_cell(ws.cell(curr_row, 2), align=ALIGN_LEFT)
            _style_cell(ws.cell(curr_row, 3), align=ALIGN_CENTER)
            _style_cell(ws.cell(curr_row, 4), align=ALIGN_LEFT)
            _style_cell(ws.cell(curr_row, 5), align=ALIGN_CENTER)
            _style_cell(ws.cell(curr_row, 6), align=ALIGN_LEFT)
            _style_cell(ws.cell(curr_row, 7), align=ALIGN_LEFT)
            _style_cell(ws.cell(curr_row, 8), align=ALIGN_LEFT)
            curr_row += 1


def build_rekap_workbook(session, tahun: int, jenis: str | None = None) -> BytesIO:
    wb = Workbook()
    default_sheet = wb.active

    if not jenis or jenis in ("all", "kuesioner"):
        ws1 = wb.create_sheet(title="Rekap Kuesioner")
        data1 = rk.get_rekap_kuesioner(session, tahun)
        build_rekap_kuesioner_sheet(ws1, data1)

    if not jenis or jenis in ("all", "konteks"):
        ws2 = wb.create_sheet(title="Rekap Konteks")
        data2 = rk.get_rekap_konteks(session, tahun)
        build_rekap_konteks_sheet(ws2, data2)

    if not jenis or jenis in ("all", "identifikasi"):
        ws3 = wb.create_sheet(title="Rekap Kategori Risiko")
        data3 = rk.get_rekap_identifikasi(session, tahun)
        build_rekap_identifikasi_sheet(ws3, data3)

    if not jenis or jenis in ("all", "level"):
        ws4 = wb.create_sheet(title="Rekap Level Risiko")
        data4 = rk.get_rekap_level_risiko(session, tahun)
        build_rekap_level_sheet(ws4, data4)

    if not jenis or jenis in ("all", "kepatuhan"):
        ws5 = wb.create_sheet(title="Rekap Kepatuhan OPD")
        data5 = rk.get_rekap_kepatuhan(session, tahun)
        build_rekap_kepatuhan_sheet(ws5, data5)

    if not jenis or jenis in ("all", "rtp", "realisasi-rtp"):
        ws6 = wb.create_sheet(title="Rekap Realisasi RTP")
        data6 = rk.get_rekap_realisasi_rtp(session, tahun)
        build_rekap_realisasi_rtp_sheet(ws6, data6)

    if not jenis or jenis in ("all", "event", "risk_event", "risk-event", "keterjadian", "log"):
        ws7 = wb.create_sheet(title="Rekap Keterjadian Risiko")
        data7 = rk.get_rekap_risk_event(session, tahun)
        build_rekap_risk_event_sheet(ws7, data7)

    # Buang sheet default pertama
    if default_sheet in wb.worksheets:
        wb.remove(default_sheet)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
