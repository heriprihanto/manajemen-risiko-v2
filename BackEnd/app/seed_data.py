"""Data seed kuesioner CEE & item dokumen (diekstrak dari Kertas Kerja Manajemen Risiko.xls)."""

# (kode, nama)
KATEGORI = [
    ('A', 'Penegakan Integritas dan Nilai Etika'),
    ('B', 'Komitmen terhadap Kompetensi'),
    ('C', 'Kepemimpinan yang Kondusif'),
    ('D', 'Pembentukan Struktur Organisasi yang Sesuai Kebutuhan'),
    ('E', 'Pendelegasian Wewenang dan Tanggung Jawab yang Tepat'),
    ('F', 'Penyusunan dan Penerapan Kebijakan yang Sehat tentang Pembinaan SDM'),
    ('G', 'Perwujudan Peran APIP yang Efektif'),
    ('H', 'Hubungan Kerja yang Baik dengan Instansi Pemerintah Terkait'),
]

# (kode_kategori, nomor, pertanyaan)
PERTANYAAN = [
    ('A', 'A.1', 'Pegawai mendapatkan pesan integritas & nilai etika secara rutin dari pimpinan instansi (Misalnya keteladanan, pesan moral dll)'),
    ('A', 'A.2', 'Pemda telah memiliki aturan perilaku (misalnya kode etik, pakta integritas, dan aturan perilaku pegawai) yang telah dikomunikasikan kepada seluruh pegawai'),
    ('A', 'A.3', 'Telah terdapat fungsi khusus di dalam instansi yang melayani pengaduan masyarakat atas pelanggaran aturan perilaku/kode etik'),
    ('A', 'A.4', 'Pelanggaran aturan perilaku/kode etik telah ditindaklanjuti sesuai ketentuan yang berlaku'),
    ('B', 'B.1', 'Standar kompetensi setiap pegawai/posisi jabatan telah ditentukan'),
    ('B', 'B.2', 'Pegawai yang kompeten telah secara tepat mengisi posisi/jabatan'),
    ('B', 'B.3', 'Pemda telah memiliki dan menerapkan strategi peningkatan kompetensi pegawai'),
    ('B', 'B.4', 'Terdapat pelatihan terkait pengelolaan risiko, baik pelatihan khusus maupun pelatihan terintegrasi secara berkala.'),
    ('C', 'C.1', 'Pimpinan telah menetapkan kebijakan pengelolaan risiko yang memberikan kejelasan arah pengelolaan risiko'),
    ('C', 'C.2', 'Pimpinan menerapkan pengelolaan risiko dan pengendalian dalam pelaksanaan tugas dan pengambilan keputusan'),
    ('C', 'C.3', 'Pimpinan membangun komunikasi yang baik dengan anggota organisasi untuk berani mengungkapkan risiko dan secara terbuka menerima/menggali pelaporan risiko/masalah'),
    ('C', 'C.4', 'Gaya pimpinan dapat mendorong pegawai untuk meningkatkan kinerja'),
    ('C', 'C.5', 'Pimpinan menetapkan Sasaran strategis yang selaras dengan visi dan misi Pemda'),
    ('C', 'C.6', 'Rencana/sasaran strategis pemda telah dijabarkan ke dalam sasaran OPD dan tingkat operasioanl OPD (cascading)'),
    ('C', 'C.7', 'Rencana strategis dan rencana kerja pemda telah menyajikan informasi mengenai risiko'),
    ('C', 'C.8', 'Pimpinan berperan serta dan mengikutsertakan pejabat dan pegawai terkait dalam proses pengelolaan risiko'),
    ('D', 'D.1', 'Setiap Urusan telah dilaksanakan oleh OPD dan unit kerja yang tepat'),
    ('D', 'D.2', 'Masing-masing pihak dalam organisasi telah memperoleh kejelasan dan memahami peran dan tanggung jawab masing-masing dalam pengelolaan risiko'),
    ('D', 'D.3', 'Pegawai  yang bertugas di OPD  merupakan pegawai tetap dan bukan pegawai yang bersifat adhoc (sementara)'),
    ('D', 'D.4', 'Adanya transparansi dan ketepatan waktu pelaporan pelaksanaan peran dan tanggung jawab masing-masing dalam pengelolaan risiko'),
    ('E', 'E.1', 'Kriteria pendelegasian wewenang telah ditentukan dengan tepat'),
    ('E', 'E.2', 'Pendelegasian wewenang dan tanggung jawab dilaksanakan secara tepat'),
    ('E', 'E.3', 'Kewenangan direviu secara periodik'),
    ('F', 'F.1', 'Pemda telah memiliki Kebijakan dan prosedur pengelolaan SDM yang lengkap (sejak rekrutmen sampai dengan pemberhentian pegawai)'),
    ('F', 'F.2', 'Rekruitmen, retensi, mutasi, maupun promosi pemilihan SDM  telah dilakukan dengan baik'),
    ('F', 'F.3', 'Insentif pegawai telah sesuai dengan tanggung jawab dan kinerja'),
    ('F', 'F.4', 'Pemda telah menginternalisasi budaya sadar risiko'),
    ('F', 'F.5', 'Adanya pemberian reward dan/atau punishment atas pengelolaan risiko (Misalnya mempertimbangkan pertanggungjawaban pengelolaan risiko dalam penilaian kinerja)'),
    ('F', 'F.6', 'Terdapat evaluasi kinerja pegawai, dan telah dipertimbangkan dalam perhitungan penghasilan'),
    ('F', 'F.7', 'Instansi telah mengalokasikan anggaran yang memadai untuk pengembangan SDM'),
    ('G', 'G.1', 'Inspektorat Daerah  melakukan reviu atas efisiensi/ efektivitas pelaksanaan setiap urusan/program Secara periodik'),
    ('G', 'G.2', 'Inspektorat Daerah  melakukan reviu atas kepatuhan hukum dan aturan lainnya'),
    ('G', 'G.3', 'Inspektorat Daerah memberikan layanan fasilitasi penerapan pengelolaan risiko dan penyelenggaraan SPIP'),
    ('G', 'G.4', 'APIP telah melaksanakan pengawasan berbasis risiko.'),
    ('G', 'G.5', 'Temuan dan saran/rekomendasi pengawasan APIP telah ditindaklanjuti'),
    ('H', 'H.1', 'Hubungan kerja yang baik dengan instansi/organisasi lain yang memiliki keterkaitan operasional telah terbangun'),
    ('H', 'H.2', 'Hubungan kerja yang baik dengan instansi yang terkait atas fungsi pengawasan/peemriksaan (inspektorat, BPKP, dan BPK) telah terbangun'),
]

# (nomor, aspek) — 8 aspek CEE berbasis dokumen, sejajar sub-unsur A..H
DOKUMEN_ITEM = [
    ('1.0', 'Penegakan Integritas dan Nilai Etika'),
    ('2.0', 'Komitmen terhadap Kompetensi'),
    ('3.0', 'Kepemimpinan yang Kondusif'),
    ('4.0', 'Pembentukan Struktur Organisasi yang Sesuai Kebutuhan'),
    ('5.0', 'Pendelegasian Wewenang dan Tanggung Jawab yang Tepat'),
    ('6.0', 'Penyusunan dan Penerapan Kebijakan yang Sehat tentang Pembinaan SDM'),
    ('7.0', 'Perwujudan Peran APIP yang Efektif'),
    ('8.0', 'Hubungan Kerja yang Baik dengan Instansi Pemerintah Terkait'),
]
