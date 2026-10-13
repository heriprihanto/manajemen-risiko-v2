"""Generate the RTP DOCX template with Jinja2 placeholders for docxtpl.

The template follows the structure of rtp_dinkes.docx.
Tables with dynamic rows use docxtpl's row-loop convention:
  - First data row contains Jinja2 tags
  - The row is replicated per iteration
"""
from docx import Document
from docx.shared import Cm, Pt, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import os

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))


def _shade(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def _cell_text(cell, text, bold=False, size=10, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = 'Times New Roman'
    return run


def _add_para(doc, text, bold=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
              space_after=Pt(6)):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_after = space_after
    pf.space_before = Pt(0)
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = 'Times New Roman'
    return p


def _heading(doc, text, size=14):
    return _add_para(doc, text, bold=True, size=size,
                     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(8))


def _make_table(doc, headers, col_widths_cm, data_cells_jinja, loop_var='items',
                sub_header=None):
    """Create a table with styled header, optional sub-header,
    and a template data row that docxtpl will loop over.

    data_cells_jinja: list of (text, bold, align) per column in data row.
    """
    n = len(headers)
    extra_rows = 1  # data row
    if sub_header:
        extra_rows += 1
    table = doc.add_table(rows=1 + extra_rows, cols=n)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    # Header
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        _cell_text(cell, h, bold=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        _shade(cell, 'D9E2F3')

    row_idx = 1
    if sub_header:
        for i, sh in enumerate(sub_header):
            cell = table.rows[row_idx].cells[i]
            _cell_text(cell, sh, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        row_idx += 1

    # Data row (will be looped by docxtpl)
    data_row = table.rows[row_idx]
    for i, (txt, bld, aln) in enumerate(data_cells_jinja):
        _cell_text(data_row.cells[i], txt, bold=bld, size=10, align=aln)

    # Set column widths
    for i, w in enumerate(col_widths_cm):
        for row in table.rows:
            row.cells[i].width = Cm(w)

    return table


def build():
    doc = Document()

    # Default style
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.space_before = Pt(0)

    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.54)
    sec.bottom_margin = Cm(1.5)
    sec.left_margin = Cm(3)
    sec.right_margin = Cm(2.54)

    # ===== COVER =====
    for _ in range(5):
        doc.add_paragraph()
    _heading(doc, 'RENCANA TINDAK PENGENDALIAN (RTP)', 16)
    _heading(doc, '{{ nama_opd_upper }}', 14)
    _heading(doc, 'PEMERINTAH KOTA TEGAL', 14)
    _heading(doc, 'TAHUN {{ tahun }}', 14)
    for _ in range(8):
        doc.add_paragraph()
    _heading(doc, '{{ nama_opd_upper }}', 12)
    _heading(doc, 'KOTA TEGAL', 12)
    _heading(doc, '{{ tahun_sebelumnya }}', 12)

    doc.add_page_break()

    # ===== KATA PENGANTAR =====
    _heading(doc, 'KATA PENGANTAR', 14)
    doc.add_paragraph()
    # Rich text paragraphs
    _add_para(doc, '{{r kata_pengantar_rt }}')
    doc.add_paragraph()
    doc.add_paragraph()
    _add_para(doc, 'Tegal,      {{ bulan_ttd }}  {{ tahun_sebelumnya }}',
              align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_para(doc, '{{ jabatan_kepala }}', align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        doc.add_paragraph()
    _add_para(doc, '{{ nama_kepala }}', bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_para(doc, 'NIP. {{ nip_kepala }}', align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_page_break()

    # ===== DAFTAR ISI =====
    _heading(doc, 'DAFTAR ISI', 14)
    doc.add_paragraph()
    for item in [
        'KATA PENGANTAR', 'DAFTAR ISI',
        'BAB I PENDAHULUAN',
        'BAB II PENCIPTAAN LINGKUNGAN PENGENDALIAN YANG DIHARAPKAN',
        'BAB III PENILAIAN RISIKO DAN KEGIATAN PENGENDALIAN YANG DIBUTUHKAN',
        'BAB IV INFORMASI, KOMUNIKASI DAN PEMANTAUAN',
        'BAB V PENUTUP',
        'LAMPIRAN',
    ]:
        _add_para(doc, item, size=11, space_after=Pt(3),
                  align=WD_ALIGN_PARAGRAPH.LEFT)

    doc.add_page_break()

    # ===== BAB I PENDAHULUAN =====
    _heading(doc, 'BAB I', 14)
    _heading(doc, 'PENDAHULUAN', 14)
    doc.add_paragraph()
    _add_para(doc, '1.  Latar Belakang', bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()
    _add_para(doc, '{{r latar_belakang_rt }}')
    doc.add_paragraph()
    _add_para(doc, '2.  Organisasi {{ nama_opd }}', bold=True,
              align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()
    _add_para(doc, '{{r organisasi_opd_rt }}')

    doc.add_page_break()

    # ===== BAB II =====
    _heading(doc, 'BAB II', 14)
    _heading(doc, 'PENCIPTAAN LINGKUNGAN PENGENDALIAN YANG DIHARAPKAN', 14)
    doc.add_paragraph()
    _add_para(doc, '{{r bab2_isi_rt }}')
    doc.add_paragraph()

    # Tabel Simpulan CEE
    _add_para(doc, 'Hasil Simpulan CEE {{ nama_opd }} Tahun {{ tahun }}:',
              bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()

    tbl_cee = doc.add_table(rows=2, cols=3)
    tbl_cee.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cee.style = 'Table Grid'
    # Header
    for i, h in enumerate(['No', 'Sub Unsur', 'Kondisi (*)']):
        _cell_text(tbl_cee.rows[0].cells[i], h, bold=True, size=10,
                   align=WD_ALIGN_PARAGRAPH.CENTER)
        _shade(tbl_cee.rows[0].cells[i], 'D9E2F3')
    # Data row (looped by docxtpl)
    r = tbl_cee.rows[1]
    _cell_text(r.cells[0], '{{ item.no }}', size=10,
               align=WD_ALIGN_PARAGRAPH.CENTER)
    _cell_text(r.cells[1], '{{ item.sub_unsur }}', size=10)
    _cell_text(r.cells[2], '{{ item.kondisi }}', size=10,
               align=WD_ALIGN_PARAGRAPH.CENTER)
    tbl_cee.rows[0].cells[0].width = Cm(1.5)
    tbl_cee.rows[0].cells[1].width = Cm(10)
    tbl_cee.rows[0].cells[2].width = Cm(4)

    doc.add_paragraph()
    _add_para(doc, '{{r bab2_penutup_rt }}')

    doc.add_page_break()

    # ===== BAB III =====
    _heading(doc, 'BAB III', 14)
    _heading(doc, 'PENILAIAN RISIKO DAN KEGIATAN PENGENDALIAN\nYANG DIBUTUHKAN', 14)
    doc.add_paragraph()

    _add_para(doc, 'A.  Penetapan Konteks', bold=True,
              align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()
    _add_para(doc, '{{r penetapan_konteks_rt }}')
    doc.add_paragraph()

    _add_para(doc, 'B.  Penilaian Risiko', bold=True,
              align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()
    _add_para(doc, '{{r penilaian_risiko_rt }}')
    doc.add_paragraph()

    _add_para(doc, 'C.  Analisa Risiko', bold=True,
              align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()
    _add_para(doc, '{{r analisa_risiko_rt }}')
    doc.add_paragraph()

    _add_para(doc, 'D.  Pengendalian yang masih dibutuhkan', bold=True,
              align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()
    _add_para(doc, 'Kegiatan pengendalian yang masih dibutuhkan {{ nama_opd }}:')
    doc.add_paragraph()

    # Daftar pengendalian dibutuhkan - simple numbered list
    tbl_ctrl = doc.add_table(rows=2, cols=2)
    tbl_ctrl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_ctrl.style = 'Table Grid'
    _cell_text(tbl_ctrl.rows[0].cells[0], 'No', bold=True, size=10,
               align=WD_ALIGN_PARAGRAPH.CENTER)
    _shade(tbl_ctrl.rows[0].cells[0], 'D9E2F3')
    _cell_text(tbl_ctrl.rows[0].cells[1], 'Kegiatan Pengendalian yang Dibutuhkan',
               bold=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    _shade(tbl_ctrl.rows[0].cells[1], 'D9E2F3')
    r = tbl_ctrl.rows[1]
    _cell_text(r.cells[0], '{{ item.no }}', size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    _cell_text(r.cells[1], '{{ item.kegiatan }}', size=10)
    tbl_ctrl.rows[0].cells[0].width = Cm(1.5)
    tbl_ctrl.rows[0].cells[1].width = Cm(14)

    doc.add_page_break()

    # ===== BAB IV =====
    _heading(doc, 'BAB IV', 14)
    _heading(doc, 'INFORMASI, KOMUNIKASI DAN PEMANTAUAN', 14)
    doc.add_paragraph()

    _heading(doc, 'RANCANGAN INFORMASI DAN KOMUNIKASI', 12)
    doc.add_paragraph()
    _add_para(doc, '{{r rancangan_infokom_rt }}')
    doc.add_paragraph()

    # Tabel Infokom
    tbl_ik = doc.add_table(rows=3, cols=3)
    tbl_ik.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_ik.style = 'Table Grid'
    for i, h in enumerate(['No', 'Kegiatan Pengendalian yang Dibutuhkan',
                           'Media / Bentuk Sarana Pengkomunikasian']):
        _cell_text(tbl_ik.rows[0].cells[i], h, bold=True, size=10,
                   align=WD_ALIGN_PARAGRAPH.CENTER)
        _shade(tbl_ik.rows[0].cells[i], 'D9E2F3')
    for i, h in enumerate(['a', 'b', 'c']):
        _cell_text(tbl_ik.rows[1].cells[i], h, size=9,
                   align=WD_ALIGN_PARAGRAPH.CENTER)
    r = tbl_ik.rows[2]
    _cell_text(r.cells[0], '{{ item.no }}', size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    _cell_text(r.cells[1], '{{ item.kegiatan }}', size=10)
    _cell_text(r.cells[2], '{{ item.media }}', size=10)
    tbl_ik.rows[0].cells[0].width = Cm(1.5)
    tbl_ik.rows[0].cells[1].width = Cm(8)
    tbl_ik.rows[0].cells[2].width = Cm(6)

    doc.add_paragraph()
    doc.add_paragraph()

    _heading(doc, 'RANCANGAN PEMANTAUAN', 12)
    doc.add_paragraph()
    _add_para(doc, '{{r rancangan_pemantauan_rt }}')
    doc.add_paragraph()

    # Tabel Pemantauan
    tbl_pm = doc.add_table(rows=3, cols=3)
    tbl_pm.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pm.style = 'Table Grid'
    for i, h in enumerate(['No', 'Kegiatan Pengendalian yang Dibutuhkan',
                           'Bentuk/Metode Pemantauan yang Diperlukan']):
        _cell_text(tbl_pm.rows[0].cells[i], h, bold=True, size=10,
                   align=WD_ALIGN_PARAGRAPH.CENTER)
        _shade(tbl_pm.rows[0].cells[i], 'D9E2F3')
    for i, h in enumerate(['a', 'b', 'c']):
        _cell_text(tbl_pm.rows[1].cells[i], h, size=9,
                   align=WD_ALIGN_PARAGRAPH.CENTER)
    r = tbl_pm.rows[2]
    _cell_text(r.cells[0], '{{ item.no }}', size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    _cell_text(r.cells[1], '{{ item.kegiatan }}', size=10)
    _cell_text(r.cells[2], '{{ item.metode }}', size=10)
    tbl_pm.rows[0].cells[0].width = Cm(1.5)
    tbl_pm.rows[0].cells[1].width = Cm(8)
    tbl_pm.rows[0].cells[2].width = Cm(6)

    doc.add_page_break()

    # ===== BAB V PENUTUP =====
    _heading(doc, 'BAB V PENUTUP', 14)
    doc.add_paragraph()
    _add_para(doc, '{{r bab5_penutup_rt }}')
    doc.add_paragraph()
    doc.add_paragraph()
    _add_para(doc, 'Tegal,       {{ bulan_ttd }}  {{ tahun_sebelumnya }}',
              align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()
    _add_para(doc, '{{ jabatan_kepala }}', align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        doc.add_paragraph()
    _add_para(doc, '{{ nama_kepala }}', bold=True,
              align=WD_ALIGN_PARAGRAPH.CENTER)
    _add_para(doc, 'NIP. {{ nip_kepala }}', align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_page_break()

    # ===== LAMPIRAN KERTAS KERJA =====
    _heading(doc, 'KERTAS KERJA', 14)
    _heading(doc, 'RENCANA TINDAK PENGENDALIAN (RTP)', 14)
    doc.add_paragraph()
    _heading(doc, '{{ nama_opd_upper }} TAHUN {{ tahun }}', 12)
    doc.add_paragraph()

    # Info identitas
    for label, val in [
        ('Nama Pemda', '{{ nama_pemda }}'),
        ('Tahun Penilaian', '{{ tahun }}'),
        ('Periode yang dinilai', '{{ periode_dinilai }}'),
        ('Urusan Pemerintahan', '{{ urusan_pemerintahan }}'),
        ('OPD yang Dinilai', '{{ nama_opd }}'),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(f'{label:<35}: ')
        run.font.size = Pt(11)
        run.font.name = 'Times New Roman'
        run2 = p.add_run(val)
        run2.font.size = Pt(11)
        run2.font.name = 'Times New Roman'

    path = os.path.join(TEMPLATE_DIR, 'rtp_template.docx')
    doc.save(path)
    print(f'Template saved to {path}')


if __name__ == '__main__':
    build()
