"""Unit test untuk modul UPR (Unit Pemilik Risiko)."""
import unittest
from sqlmodel import Session, select
from app.db import engine
from app.models.upr import Upr
from app.routers.upr import list_upr, get_upr_stats, create_upr, update_upr, delete_upr


class TestUpr(unittest.TestCase):
    def setUp(self):
        self.session = Session(engine)

    def tearDown(self):
        self.session.close()

    def test_upr_crud_flow(self):
        # 1. Create
        payload = {
            "nip": "199001012015011001",
            "nama": "TEST PEJABAT UPR, S.Kom",
            "jabatan": "Kepala Seksi Manajemen Risiko",
            "eselon": "Eselon IV.a",
            "tingkat_organisasi": "UPR tingkat unit Eselon III dan IV",
            "jabatan_upr": "Koordinator Teknis",
            "status": "Aktif",
            "keterangan": "Uji Coba Otomasi",
        }
        created = create_upr(payload, session=self.session, user={"role_id": 1})
        self.assertIsNotNone(created["id"])
        self.assertEqual(created["nip"], payload["nip"])
        self.assertEqual(created["eselon"], "Eselon IV.a")
        self.assertEqual(created["tingkat_organisasi"], "UPR tingkat unit Eselon III dan IV")
        self.assertEqual(created["jabatan_upr"], "Koordinator Teknis")
        upr_id = created["id"]

        # 2. List & Filter
        res = list_upr(
            search="TEST PEJABAT",
            eselon="Eselon IV.a",
            tingkat_organisasi="UPR tingkat unit Eselon III dan IV",
            jabatan_upr="Koordinator Teknis",
            session=self.session,
        )
        self.assertGreaterEqual(res["total"], 1)
        found = any(x["id"] == upr_id for x in res["items"])
        self.assertTrue(found)

        # 3. Update
        updated = update_upr(
            upr_id,
            {"status": "Tidak Aktif", "jabatan_upr": "Anggota", "keterangan": "Diperbarui"},
            session=self.session,
            user={"role_id": 1},
        )
        self.assertEqual(updated["status"], "Tidak Aktif")
        self.assertEqual(updated["jabatan_upr"], "Anggota")

        # 4. Stats
        stats = get_upr_stats(session=self.session)
        self.assertGreater(stats["total"], 0)
        self.assertGreater(stats["tidak_aktif"], 0)

        # 5. Delete
        del_res = delete_upr(upr_id, session=self.session, user={"role_id": 1})
        self.assertEqual(del_res["id"], upr_id)

        # Verify gone
        post_del = self.session.get(Upr, upr_id)
        self.assertIsNone(post_del)


if __name__ == "__main__":
    unittest.main()
