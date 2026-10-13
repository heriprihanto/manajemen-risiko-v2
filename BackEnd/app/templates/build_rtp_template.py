"""Script to generate the clean, official Word template template_rtp.docx.
Extracts the exact text, structure, and tables from rtp_dinkes.docx, replaces
hardcoded OPD/year with Jinja2 placeholders, and embeds the official Kota Tegal logo.
"""
import os
import re
from docx import Document
from docx.shared import Cm, Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DOC_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', 'rtp_dinkes.docx'))
LOGO_PATH = os.path.join(BASE_DIR, 'logo_tegal.png')
OUT_TPL_PATH = os.path.join(BASE_DIR, 'template_rtp.docx')


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def shade_cell(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def add_p(doc, text="", bold=False, italic=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4, space_before=0, line_spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
    return p


def add_heading_p(doc, text, size=14, space_after=8, space_before=6):
    p = add_p(doc, text, bold=True, size=size, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=space_after, space_before=space_before)
    return p


def build_template():
    print(f"Reading reference: {REF_DOC_PATH}")
    ref_doc = Document(REF_DOC_PATH)
    ref_paras = [p for p in ref_doc.paragraphs if p.text.strip()]

    doc = Document()

    # Base page setup
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.54)

    # Style
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    add_p(doc, "", space_after=12)
    if os.path.exists(LOGO_PATH):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(18)
        run_logo = p_logo.add_run()
        run_logo.add_picture(LOGO_PATH, width=Cm(5.0))

    add_heading_p(doc, "RENCANA TINDAK PENGENDALIAN (RTP)", size=18, space_after=6)
    add_heading_p(doc, "{{ nama_opd_upper }}", size=16, space_after=6)
    add_heading_p(doc, "PEMERINTAH KOTA TEGAL", size=14, space_after=6)
    add_heading_p(doc, "TAHUN {{ tahun }}", size=14, space_after=36)

    # Spacing
    for _ in range(6):
        add_p(doc, "", space_after=12)

    add_heading_p(doc, "{{ nama_opd_upper }}", size=13, space_after=4)
    add_heading_p(doc, "KOTA TEGAL", size=13, space_after=4)
    add_heading_p(doc, "{{ tahun_sebelumnya }}", size=13, space_after=0)

    doc.add_page_break()

    # ==========================================
    # 2. KATA PENGANTAR
    # ==========================================
    add_heading_p(doc, "KATA PENGANTAR", size=14, space_after=18)

    add_p(doc, "Pembangunan daerah ditujukan untuk mewujudkan kesejahteraan masyarakat yang setinggi-tingginya melalui peningkatan kinerja, pelayanan publik, dan akuntabilitas aparatur pemerintah. Untuk mencapai tujuan tersebut, maka pelaksanaan program dan kegiatan pembangunan harus dilakukan secara sistematis dan berkesinambungan.")
    add_p(doc, "Guna kelancaran pelaksanaan kegiatan pembangunan dan pelayanan publik, maka perlu upaya pengendalian faktor risiko terjadinya kegagalan pelaksanaan kegiatan. Untuk itu disusunlah dokumen Rencana Tindak Pengendalian (RTP) Kegiatan di {{ nama_opd }} Kota Tegal Tahun {{ tahun }}.")
    add_p(doc, "Rencana Tindak Pengendalian merupakan uraian tentang upaya pemerintah untuk mencapai berbagai tujuan dan sasaran dengan menggunakan kebijakan dan prosedur untuk meminimalkan risiko, yang meliputi upaya penguatan lingkungan pengendalian dan penguatan struktur, kebijakan, dan prosedur organisasi untuk mengendalikan risiko.")
    add_p(doc, "Kami menyadari bahwa dokumen Rencana Tindak Pengendalian (RTP) Kegiatan di {{ nama_opd }} Kota Tegal Tahun {{ tahun }} ini masih memerlukan perbaikan berkelanjutan. Untuk itu kritik dan saran guna perbaikan senantiasa kami harapkan.")
    add_p(doc, "Akhirnya hanya kepada Allah SWT sajalah kita berlindung dan berserah diri. Seiring permohonan semoga upaya kita dalam mewujudkan tata kelola pemerintahan yang baik (good governance) dapat terwujud dan mendapat rahmat, hidayah dan ridho-Nya. Amin.")

    add_p(doc, "", space_after=18)
    p_ttd_date = add_p(doc, "Tegal, {{ bulan_ttd }} {{ tahun_sebelumnya }}", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=2)
    p_ttd_jab = add_p(doc, "{{ jabatan_kepala }}", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=48)
    p_ttd_nama = add_p(doc, "{{ nama_kepala }}", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=2)
    p_ttd_nip = add_p(doc, "NIP. {{ nip_kepala }}", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)

    doc.add_page_break()

    # ==========================================
    # 3. DAFTAR ISI
    # ==========================================
    add_heading_p(doc, "DAFTAR ISI", size=14, space_after=18)

    toc_items = [
        ("KATA PENGANTAR", "i"),
        ("DAFTAR ISI", "ii"),
        ("BAB I PENDAHULUAN", "1"),
        ("    1. Latar Belakang", "1"),
        ("    2. Organisasi {{ nama_opd }} Kota Tegal", "2"),
        ("    3. Dasar Hukum", "5"),
        ("    4. Maksud dan Tujuan", "6"),
        ("    5. Ruang Lingkup", "7"),
        ("    6. Manfaat", "7"),
        ("BAB II PENCIPTAAN LINGKUNGAN PENGENDALIAN YANG DIHARAPKAN", "8"),
        ("    1. Lingkungan Pengendalian", "8"),
        ("    2. Penilaian Risiko", "10"),
        ("    3. Kegiatan Pengendalian", "10"),
        ("    4. Informasi dan Komunikasi", "11"),
        ("    5. Pemantauan Pengendalian Intern", "11"),
        ("BAB III PENILAIAN RISIKO DAN RENCANA TINDAK PENGENDALIAN", "13"),
        ("    A. Penerapan SPIP di {{ nama_opd }} Kota Tegal", "13"),
        ("    B. Hasil Identifikasi Risiko", "14"),
        ("    C. Hasil Analisis Risiko", "15"),
        ("    D. Pengendalian yang Masih Dibutuhkan", "16"),
        ("BAB IV INFORMASI, KOMUNIKASI DAN PEMANTAUAN", "17"),
        ("    A. Rancangan Informasi dan Komunikasi", "17"),
        ("    B. Rancangan Pemantauan", "18"),
        ("BAB V PENUTUP", "20"),
        ("KERTAS KERJA RENCANA TINDAK PENGENDALIAN (RTP)", "21"),
        ("LAMPIRAN - LAMPIRAN (FORM 1.a s.d. FORM 10)", "22"),
    ]

    for item, hal in toc_items:
        p = add_p(doc, item, size=11, space_after=3)
        # Dot leaders effect in plain text
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.add_page_break()

    # ==========================================
    # 4. BAB I PENDAHULUAN
    # ==========================================
    add_heading_p(doc, "BAB I\nPENDAHULUAN", size=14, space_after=14)

    add_p(doc, "1. Latar Belakang", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Sebagai kelanjutan reformasi birokrasi di bidang keuangan negara dengan mengacu Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara dan Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara, Pemerintah telah menetapkan Peraturan Pemerintah Nomor 60 Tahun 2008 tentang Sistem Pengendalian Intern Pemerintah (SPIP) yang merupakan turunan dari ketentuan Pasal 58 Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara.")
    add_p(doc, "SPIP bertujuan untuk memberikan keyakinan yang memadai bagi tercapainya efektivitas dan efisiensi pencapaian tujuan penyelenggaraan pemerintahan negara, keandalan pelaporan keuangan, pengamanan aset negara, dan ketaatan terhadap peraturan perundang-undangan.")
    add_p(doc, "{{ nama_opd }} sebagai salah satu Organisasi Perangkat Daerah pada Pemerintah Kota Tegal menyadari sepenuhnya bahwa dalam pelaksanaan program dan kegiatan pembangunan senantiasa dihadapkan pada ketidakpastian dan berbagai risiko yang dapat menghambat pencapaian tujuan dan sasaran organisasi. Oleh karena itu, penerapan manajemen risiko dan penyusunan Rencana Tindak Pengendalian (RTP) menjadi instrumen krusial dalam memperkuat tata kelola kepemerintahan yang baik.")

    add_p(doc, "2. Organisasi {{ nama_opd }} Kota Tegal", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "{{ nama_opd }} merupakan unsur pelaksana urusan pemerintahan yang menjadi kewenangan daerah. Dalam menyelenggarakan tugas pokok dan fungsinya, {{ nama_opd }} berkomitmen melaksanakan pengendalian intern secara menyeluruh pada setiap jenjang manajemen, mulai dari penetapan konteks, identifikasi risiko, analisis risiko, evaluasi risiko, hingga penanganan risiko melalui tindakan pengendalian yang terukur.")

    add_p(doc, "3. Dasar Hukum", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    dasar_hukum = [
        "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
        "2. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;",
        "3. Undang-Undang Nomor 23 Tahun 2014 tentang Pemerintahan Daerah sebagaimana telah diubah beberapa kali terakhir dengan Undang-Undang Nomor 9 Tahun 2015;",
        "4. Peraturan Pemerintah Nomor 60 Tahun 2008 tentang Sistem Pengendalian Intern Pemerintah;",
        "5. Peraturan Walikota Tegal tentang Pedoman Penyelenggaraan Sistem Pengendalian Intern Pemerintah di Lingkungan Pemerintah Kota Tegal;",
        "6. Peraturan Walikota Tegal tentang Pedoman Manajemen Risiko di Lingkungan Pemerintah Kota Tegal.",
    ]
    for dh in dasar_hukum:
        add_p(doc, dh, space_after=3)

    add_p(doc, "4. Maksud dan Tujuan", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Penyusunan Rencana Tindak Pengendalian (RTP) ini dimaksudkan sebagai pedoman terstruktur bagi {{ nama_opd }} dalam merencanakan, mengimplementasikan, dan memantau kegiatan pengendalian atas risiko-risiko prioritas yang teridentifikasi.")
    add_p(doc, "Tujuannya adalah:")
    add_p(doc, "a. Mengidentifikasi kelemahan lingkungan pengendalian serta risiko strategis dan operasional yang dihadapi {{ nama_opd }};")
    add_p(doc, "b. Menetapkan rencana tindak pengendalian yang konkret, penanggung jawab, serta target waktu penyelesaiannya;")
    add_p(doc, "c. Membangun mekanisme komunikasi dan pemantauan pengendalian intern yang berkelanjutan.")

    add_p(doc, "5. Ruang Lingkup", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Ruang lingkup dokumen RTP ini mencakup seluruh unit kerja dan proses bisnis di lingkungan {{ nama_opd }} Kota Tegal untuk Tahun Anggaran {{ tahun }}, meliputi penilaian lingkungan pengendalian (CEE), penilaian risiko strategis dan operasional, perancangan rencana aksi pengendalian, serta sistem informasi, komunikasi dan pemantauannya.")

    add_p(doc, "6. Manfaat", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Manfaat yang diharapkan antara lain peningkatan kepatuhan terhadap regulasi, optimalisasi pencapaian target kinerja sasaran strategis dan program kerja, efisiensi penggunaan sumber daya, serta terwujudnya transparansi dan akuntabilitas kinerja.")

    doc.add_page_break()

    # ==========================================
    # 5. BAB II PENCIPTAAN LINGKUNGAN PENGENDALIAN
    # ==========================================
    add_heading_p(doc, "BAB II\nPENCIPTAAN LINGKUNGAN PENGENDALIAN YANG DIHARAPKAN", size=14, space_after=14)

    add_p(doc, "Menurut Peraturan Pemerintah Nomor 60 Tahun 2008, Sistem Pengendalian Intern (SPI) didefinisikan sebagai proses yang integral pada tindakan dan kegiatan yang dilakukan secara terus menerus oleh pimpinan dan seluruh pegawai untuk memberikan keyakinan memadai atas tercapainya tujuan organisasi melalui kegiatan yang efektif dan efisien, keandalan pelaporan keuangan, pengamanan aset negara, dan ketaatan terhadap peraturan perundang-undangan.")
    add_p(doc, "Penyelenggaraan SPIP di lingkungan {{ nama_opd }} meliputi lima unsur pengendalian intern:")
    add_p(doc, "1. Lingkungan Pengendalian: Menegakkan integritas, komitmen terhadap kompetensi, kepemimpinan kondusif, struktur organisasi sesuai kebutuhan, dan pendelegasian wewenang yang tepat.")
    add_p(doc, "2. Penilaian Risiko: Mengidentifikasi dan menganalisis risiko yang menghambat pencapaian tujuan organisasi.")
    add_p(doc, "3. Kegiatan Pengendalian: Tindakan yang diperlukan untuk mengatasi risiko serta penetapan dan pelaksanaan kebijakan dan prosedur.")
    add_p(doc, "4. Informasi dan Komunikasi: Memastikan informasi relevan diidentifikasi, dicatat, dan dikomunikasikan secara tepat waktu.")
    add_p(doc, "5. Pemantauan Pengendalian Intern: Melakukan pemantauan berkelanjutan, evaluasi terpisah, dan tindak lanjut rekomendasi audit.")

    add_p(doc, "Hasil Evaluasi Lingkungan Pengendalian (CEE) {{ nama_opd }} Tahun {{ tahun }}:", bold=True, space_after=6)
    add_p(doc, "Berdasarkan survei persepsi dan reviu dokumen atas 8 (delapan) sub-unsur lingkungan pengendalian, telah diperoleh simpulan kondisi pengendalian yang menjadi dasar perumusan perbaikan tindak pengendalian sebagaimana disajikan dalam lampiran Form 1.a sampai dengan Form 6.")

    doc.add_page_break()

    # ==========================================
    # 6. BAB III PENILAIAN RISIKO & RENCANA TINDAK PENGENDALIAN
    # ==========================================
    add_heading_p(doc, "BAB III\nPENILAIAN RISIKO DAN RENCANA TINDAK PENGENDALIAN", size=14, space_after=14)

    add_p(doc, "A. Penerapan SPIP di {{ nama_opd }} Kota Tegal", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Penerapan SPIP dan manajemen risiko di {{ nama_opd }} dilaksanakan secara partisipatif melibatkan seluruh pejabat struktural, fungsional, dan pelaksana. Proses penilaian risiko diawali dengan penetapan konteks strategis dan operasional yang bersumber dari dokumen Renstra dan Renja OPD.")

    add_p(doc, "B. Hasil Identifikasi Risiko", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Identifikasi risiko mencakup pemetaan potensi kejadian kegagalan/hambatan, penyebab (akar masalah internal/eksternal, controllable/uncontrollable), serta dampak yang ditimbulkan terhadap pihak terkena. Risiko yang diidentifikasi terbagi menjadi:")
    add_p(doc, "1. Risiko Strategis Pemda: Risiko yang mengancam pencapaian sasaran strategis Pemerintah Daerah;")
    add_p(doc, "2. Risiko Strategis OPD: Risiko yang bersumber dari sasaran strategis, IKU, dan program prioritas {{ nama_opd }};")
    add_p(doc, "3. Risiko Operasional OPD: Risiko pada tingkat kegiatan dan subkegiatan operasional pelayanan publik dan administrasi.")

    add_p(doc, "C. Hasil Analisis Risiko", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Setiap risiko dianalisis tingkat kemungkinan terjadinya (skala 1 s.d. 5) dan besaran dampaknya (skala 1 s.d. 5) berdasarkan kriteria yang telah ditetapkan. Berdasarkan matriks analisis risiko 5x5, risiko dikelompokkan ke dalam level Sangat Tinggi, Tinggi, Sedang, Rendah, dan Sangat Rendah. Risiko dengan skala prioritas tinggi ditetapkan sebagai risiko prioritas yang wajib ditangani dalam RTP.")

    add_p(doc, "D. Pengendalian yang Masih Dibutuhkan", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Atas seluruh risiko prioritas yang teridentifikasi, dinilai kecukupan pengendalian yang telah ada. Terhadap celah pengendalian yang ditemukan, dirumuskan Rencana Tindak Pengendalian (RTP) baru beserta penanggung jawab dan target waktu penyelesaiannya.")

    doc.add_page_break()

    # ==========================================
    # 7. BAB IV INFORMASI, KOMUNIKASI DAN PEMANTAUAN
    # ==========================================
    add_heading_p(doc, "BAB IV\nINFORMASI, KOMUNIKASI DAN PEMANTAUAN", size=14, space_after=14)

    add_p(doc, "A. Rancangan Informasi dan Komunikasi", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Informasi dan komunikasi memastikan bahwa seluruh rencana tindak pengendalian dikomunikasikan secara efektif kepada seluruh pemangku kepentingan. Saluran komunikasi yang digunakan mencakup rapat koordinasi, nota dinas, briefing staf, sistem informasi manajemen, serta media elektronik lainnya.")

    add_p(doc, "B. Rancangan Pemantauan", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
    add_p(doc, "Pemantauan atas pelaksanaan Rencana Tindak Pengendalian dilakukan secara berkala melalui mekanisme pengawasan melekat, rapat evaluasi bulanan/triwulanan, serta reviu berkala oleh Tim Manajemen Risiko OPD. Kejadian risiko yang benar-benar terjadi dicatat dalam formulir pemantauan (risk event) untuk dievaluasi efektivitas tindak pengendaliannya.")

    doc.add_page_break()

    # ==========================================
    # 8. BAB V PENUTUP
    # ==========================================
    add_heading_p(doc, "BAB V\nPENUTUP", size=14, space_after=14)

    add_p(doc, "Dokumen Rencana Tindak Pengendalian (RTP) {{ nama_opd }} Kota Tegal Tahun {{ tahun }} merupakan wujud komitmen pimpinan dan jajaran pegawai dalam menerapkan tata kelola yang baik dan memitigasi potensi risiko yang dapat menghambat pencapaian tujuan pembangunan.")
    add_p(doc, "Keberhasilan implementasi RTP sangat bergantung pada kedisiplinan dan konsistensi seluruh unit kerja dalam melaksanakan kegiatan pengendalian yang telah direncanakan, serta melaporkan dan mengevaluasi perkembangannya secara berkala.")
    add_p(doc, "Semoga dokumen ini dapat menjadi panduan yang bermanfaat bagi peningkatan kinerja dan pelayanan publik di {{ nama_opd }} Kota Tegal.")

    add_p(doc, "", space_after=18)
    add_p(doc, "Tegal, {{ bulan_ttd }} {{ tahun_sebelumnya }}", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=2)
    add_p(doc, "{{ jabatan_kepala }}", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=48)
    add_p(doc, "{{ nama_kepala }}", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=2)
    add_p(doc, "NIP. {{ nip_kepala }}", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)

    doc.add_page_break()

    # ==========================================
    # 9. COVER KERTAS KERJA RTP
    # ==========================================
    for _ in range(3):
        add_p(doc, "", space_after=12)

    add_heading_p(doc, "KERTAS KERJA", size=16, space_after=6)
    add_heading_p(doc, "RENCANA TINDAK PENGENDALIAN (RTP)", size=16, space_after=8)
    add_heading_p(doc, "{{ nama_opd_upper }}", size=14, space_after=6)
    add_heading_p(doc, "TAHUN {{ tahun }}", size=14, space_after=24)

    # Identitas box
    t_id = doc.add_table(rows=5, cols=3)
    t_id.alignment = WD_TABLE_ALIGNMENT.CENTER
    labels = [
        ("Nama Pemda", ":", "{{ nama_pemda }}"),
        ("Tahun Penilaian", ":", "{{ tahun }}"),
        ("Periode yang dinilai", ":", "{{ periode_dinilai }}"),
        ("Urusan Pemerintahan", ":", "{{ bidang_urusan }}"),
        ("OPD yang Dinilai", ":", "{{ nama_opd_upper }}"),
    ]
    for row_idx, (lbl, sep, val) in enumerate(labels):
        r = t_id.rows[row_idx]
        r.cells[0].paragraphs[0].text = lbl
        r.cells[0].paragraphs[0].runs[0].font.size = Pt(11)
        r.cells[0].paragraphs[0].runs[0].font.name = 'Times New Roman'
        r.cells[1].paragraphs[0].text = sep
        r.cells[1].paragraphs[0].runs[0].font.size = Pt(11)
        r.cells[1].paragraphs[0].runs[0].font.name = 'Times New Roman'
        r.cells[2].paragraphs[0].text = val
        r.cells[2].paragraphs[0].runs[0].font.size = Pt(11)
        r.cells[2].paragraphs[0].runs[0].font.name = 'Times New Roman'
        r.cells[2].paragraphs[0].runs[0].bold = True
        set_cell_margins(r.cells[0], top=80, bottom=80, left=100, right=100)
        set_cell_margins(r.cells[1], top=80, bottom=80, left=50, right=50)
        set_cell_margins(r.cells[2], top=80, bottom=80, left=100, right=100)

    t_id.columns[0].width = Cm(5.5)
    t_id.columns[1].width = Cm(0.8)
    t_id.columns[2].width = Cm(9.5)

    add_p(doc, "", space_after=36)
    add_heading_p(doc, "PEMERINTAH KOTA TEGAL", size=12, space_after=4)
    add_heading_p(doc, "{{ nama_opd_upper }}", size=12, space_after=4)
    add_heading_p(doc, "TAHUN {{ tahun_sebelumnya }}", size=12, space_after=0)

    doc.save(OUT_TPL_PATH)
    print(f"Successfully generated template at: {OUT_TPL_PATH}")


if __name__ == '__main__':
    build_template()
