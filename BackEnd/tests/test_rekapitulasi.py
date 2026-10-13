import unittest
from sqlmodel import Session, SQLModel, create_engine
from app.models import Opd, Pengaturan
from app.routers import rekapitulasi


class RekapitulasiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.session.add_all([
            Opd(id_sub_pd=1, kode='1.01', nama_pd='Dinas Kesehatan', aktif=1),
            Opd(id_sub_pd=2, kode='1.02', nama_pd='Dinas Pendidikan', aktif=1),
            Pengaturan(id=1, tahun_default=2027),
        ])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_rekapitulasi_endpoints(self):
        tahun = 2027

        # 1. Kuesioner
        res_kuesioner = rekapitulasi.rekap_kuesioner(tahun, session=self.session)
        self.assertIn('items', res_kuesioner)
        self.assertEqual(len(res_kuesioner['items']), 2)

        # 2. Konteks
        res_konteks = rekapitulasi.rekap_konteks(tahun, session=self.session)
        self.assertIn('items', res_konteks)
        self.assertEqual(len(res_konteks['items']), 2)

        # 3. Identifikasi
        res_identifikasi = rekapitulasi.rekap_identifikasi(tahun, session=self.session)
        self.assertIn('items', res_identifikasi)
        self.assertEqual(len(res_identifikasi['items']), 2)

        # 4. Level Risiko
        res_level = rekapitulasi.rekap_level_risiko(tahun, session=self.session)
        self.assertIn('items', res_level)
        self.assertEqual(len(res_level['items']), 2)

        # 5. Kepatuhan
        res_kepatuhan = rekapitulasi.rekap_kepatuhan(tahun, session=self.session)
        self.assertIn('items', res_kepatuhan)
        self.assertEqual(len(res_kepatuhan['items']), 2)

        # 6. Realisasi RTP
        res_rtp = rekapitulasi.rekap_realisasi_rtp(tahun, session=self.session)
        self.assertIn('items', res_rtp)
        self.assertEqual(len(res_rtp['items']), 2)

        # 7. Risk Event
        res_event = rekapitulasi.rekap_risk_event(tahun, session=self.session)
        self.assertIn('items', res_event)
        self.assertEqual(len(res_event['items']), 2)

        # 8. Export Excel
        res_excel = rekapitulasi.export_excel(tahun, jenis='all', session=self.session)
        self.assertEqual(res_excel.media_type, rekapitulasi.XLSX_MIME)


if __name__ == '__main__':
    unittest.main()
