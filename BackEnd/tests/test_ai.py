import json
import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.db import engine
from app.models.kamus import KamusRisiko
from app.models.pengaturan import Pengaturan, SETTINGS_ID
from app.core.security import current_user


class TestAiRiskAssist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        with Session(engine) as session:
            # Seed settings with active provider
            settings = session.get(Pengaturan, SETTINGS_ID)
            if not settings:
                settings = Pengaturan(id=SETTINGS_ID, ai_provider="openai", ai_api_key="sk-test-key", ai_model="o4-mini")
                session.add(settings)
            else:
                settings.ai_provider = "openai"
                settings.ai_api_key = "sk-test-key"
                settings.ai_model = "o4-mini"
                session.add(settings)

            # Seed an active Kamus Risiko for matching
            k = session.query(KamusRisiko).filter(KamusRisiko.kode_risiko == 'KMS-AI-01').first()
            if not k:
                k = KamusRisiko(
                    kode_risiko='KMS-AI-01',
                    nama_risiko='Keterlambatan penyelesaian proyek infrastruktur',
                    kategori_risiko='Operasional',
                    deskripsi='Risiko keterlambatan fisik',
                    aktif=1,
                )
                session.add(k)
            session.commit()

        # Mock current_user
        mock_user = {"id": 1, "username": "admin", "role_id": 1, "opds": [], "display_name": "Admin"}
        app.dependency_overrides[current_user] = lambda: mock_user

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(current_user, None)

    @patch('app.routers.ai.call_llm', new_callable=AsyncMock)
    def test_generate_risk_enrichment(self, mock_call):
        ai_payload = [
            {
                "uraian_risiko": "Keterlambatan penyelesaian proyek infrastruktur",
                "keterangan_risiko": "Keterlambatan akibat kendala pengadaan material",
                "penyebab": "Rantai pasok material terhambat",
                "sebab_sumber": "Eksternal",
                "cuc": "UC",
                "dampak": "Penyerapan anggaran tertunda dan layanan masyarakat terganggu",
                "dampak_pihak_terkena": "Masyarakat pengguna jalan",
                "kategori": "Operasional",
                "pemilik_risiko": "Kepala Bidang Bina Marga"
            }
        ]
        mock_call.return_value = json.dumps(ai_payload)

        res = self.client.post(
            "/api/ai/generate-risk",
            json={
                "sasaran": "Peningkatan infrastruktur jalan daerah",
                "jenis": "operasional_opd"
            }
        )
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        suggestions = data.get("suggestions", [])
        self.assertEqual(len(suggestions), 1)
        item = suggestions[0]
        self.assertEqual(item["uraian_risiko"], "Keterlambatan penyelesaian proyek infrastruktur")
        self.assertEqual(item["cuc"], "UC")
        self.assertEqual(item["sebab_sumber"], "Eksternal")
        self.assertEqual(item["dampak_pihak_terkena"], "Masyarakat pengguna jalan")


if __name__ == '__main__':
    unittest.main()
