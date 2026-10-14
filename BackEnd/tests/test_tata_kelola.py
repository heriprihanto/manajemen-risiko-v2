"""Pengujian API dengan database terisolasi: hak akses, riwayat, keputusan, snapshot."""
from datetime import date, timedelta
import os
import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from app.core.datetime_utils import now_wib
from app.core.security import create_access_token, UserDep, OpdScopeDep
from app.db import get_session
from app.models import Opd, Risiko, AnalisisRisiko, MonitoringRiskEvent, LaporKejadian
from app.models.tata_kelola import PenugasanRisiko, PenilaianRiwayat, AuditRisiko
from app.routers import tata_kelola, risiko, lapor_kejadian, selera


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        key = patch("app.core.security.settings.SECRET_KEY", "test-only-signing-key-for-governance-2026")
        key.start()
        self.addCleanup(key.stop)
        url = os.environ.get("MR_TEST_DATABASE_URL")
        self.engine = create_engine(url) if url else create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        if url and not (self.engine.url.database or "").startswith("mr_test_"):
            raise RuntimeError("Gunakan database sementara bernama mr_test_*; pengujian menghapus tabelnya")
        if not url:
            @event.listens_for(self.engine, "connect")
            def foreign_keys(conn, _):
                conn.execute("PRAGMA foreign_keys=ON")
        SQLModel.metadata.create_all(self.engine)
        self.year = now_wib().year
        self.today = now_wib().date()
        self.users = {
            "operator": {"id": 1, "username": "operator", "role_id": 4, "opds": [1]},
            "reviewer": {"id": 2, "username": "reviewer", "role_id": 4, "opds": [1]},
            "admin": {"id": 3, "username": "admin", "role_id": 1, "opds": []},
            "outsider": {"id": 4, "username": "outsider", "role_id": 4, "opds": [2]},
        }
        with Session(self.engine) as s:
            s.add_all([Opd(id_sub_pd=1, nama_pd="Dinas Uji", aktif=1), Opd(id_sub_pd=2, nama_pd="Dinas Lain", aktif=1)])
            s.flush()
            r = Risiko(opd_id=1, tahun=self.year, jenis_risiko="strategis_opd", uraian_risiko="Layanan terhenti", kode_risiko="RSO.TEST.001", kategori_risiko="Risiko Fraud/Kecurangan")
            other = Risiko(opd_id=2, tahun=self.year, jenis_risiko="strategis_opd", uraian_risiko="Risiko luar OPD")
            s.add_all([r, other]); s.commit(); s.refresh(r); s.refresh(other)
            self.rid, self.other_rid = r.id, other.id
            for role in ["upr_pemda", "upr", "atasan", "upr_atasan", "kepatuhan", "inspektorat", "komite"]:
                s.add(PenugasanRisiko(opd_id=1, username="reviewer", nama="Pemeriksa", peran=role,
                    mulai=date(self.year,1,1), selesai=date(self.year,12,31), dasar="SK pengujian"))
            s.commit()
        app = FastAPI()
        app.include_router(selera.router, prefix="/api", dependencies=[UserDep])
        app.include_router(tata_kelola.router, prefix="/api", dependencies=[UserDep])
        app.include_router(risiko.router, prefix="/api", dependencies=[OpdScopeDep])
        app.include_router(lapor_kejadian.router, prefix="/api")
        def session():
            with Session(self.engine) as s:
                yield s
        app.dependency_overrides[get_session] = session
        self.client = TestClient(app)
        self.post('/selera-risiko', {"opd_id":1, "tahun":self.year, "ambang":10,
            "penetap":"Kepala Dinas", "pertimbangan_sumber_daya":"Kapasitas anggaran dan SDM tersedia"})

    def tearDown(self):
        self.client.close()
        # MR_TEST_DATABASE_URL hanya untuk database sementara khusus pengujian.
        SQLModel.metadata.drop_all(self.engine)
        self.engine.dispose()

    def call(self, method, path, data=None, user="operator"):
        headers = {"Authorization": "Bearer " + create_access_token(self.users[user])} if user else {}
        return self.client.request(method, "/api" + path, json=data, headers=headers)

    def post(self, path, data, user="operator", expected=200):
        response = self.call("POST", path, data, user)
        self.assertEqual(response.status_code, expected, response.text)
        return response.json()

    def policy(self, accept=True):
        p = self.post("/tata-kelola/kebijakan", {
            "opd_id":1, "tahun":self.year, "nama":"Kebijakan uji", "dasar":"Berita acara FGD dan SK", "berlaku":f"{self.year}-01-01",
            "dampak":[f"Dampak tingkat {i}" for i in range(1,6)], "kemungkinan":[f"Frekuensi tingkat {i}" for i in range(1,6)],
            "area_dampak":["Layanan", "Keuangan"], "kategori_prioritas":["Risiko Fraud/Kecurangan", "Risiko Operasional"],
        })
        if accept:
            p = self.post(f'/tata-kelola/kebijakan/{p["id"]}/keputusan', {"keputusan":"disetujui", "catatan":"Disetujui sesuai SK"}, "reviewer")
        return p

    def assessment(self, tahap="awal", dampak=5, kemungkinan=1):
        return self.post(f"/tata-kelola/risiko/{self.rid}/penilaian", {
            "tahap":tahap, "dampak":dampak, "kemungkinan":kemungkinan, "alasan":"Hasil analisis bukti", "bukti":"Dokumen evaluasi 01"})

    def test_auth_and_cross_opd_are_enforced(self):
        self.assertEqual(self.call("GET",f"/tata-kelola/risiko/{self.rid}",user=None).status_code,401)
        self.assertEqual(self.call("GET",f"/tata-kelola/risiko/{self.rid}",user="outsider").status_code,403)
        self.assertEqual(self.call("GET",f"/tata-kelola/risiko/{self.other_rid}").status_code,403)
        self.assertEqual(self.call("GET",f"/tata-kelola/laporan?opd_id=2&tahun={self.year}").status_code,403)

    def test_policy_admin_cannot_approve_without_assignment(self):
        p=self.policy(False)
        self.post(f'/tata-kelola/kebijakan/{p["id"]}/keputusan', {"keputusan":"disetujui", "catatan":"Coba admin"}, "admin",403)
        self.post(f'/tata-kelola/kebijakan/{p["id"]}/keputusan', {"keputusan":"disetujui", "catatan":"Sesuai SK"}, "reviewer")
        self.post(f'/tata-kelola/kebijakan/{p["id"]}/keputusan', {"keputusan":"ditolak", "catatan":"Tidak boleh ulang"}, "reviewer",409)

    def test_self_approval_is_forbidden_even_with_assignment(self):
        self.policy()
        p=self.assessment(dampak=1)
        proposal=self.post(f"/tata-kelola/risiko/{self.rid}/respons", {"penilaian_id":p["id"],"opsi":["terima"],"alasan":"Dalam kemampuan penerimaan"},"reviewer")
        self.post(f'/tata-kelola/respons/{proposal["id"]}/keputusan', {"keputusan":"disetujui","catatan":"Setuju sendiri"},"reviewer",403)

    def test_matrix_and_score_11_policy(self):
        self.policy()
        rare=self.assessment(dampak=5,kemungkinan=1)
        self.assertEqual(rare["skor"],20)
        eleven=self.assessment(dampak=1,kemungkinan=5)
        self.assertEqual(eleven["skor"],11)
        self.assertTrue(eleven["prioritas"])
        self.assertTrue(eleven["di_luar_toleransi"])

    def test_owner_appetite_can_authorize_response_without_criteria_policy(self):
        p=self.assessment(dampak=1,kemungkinan=1)
        self.assertIsNone(p["kebijakan_id"])
        self.assertFalse(p["prioritas"])
        self.assertEqual(p["kebijakan_snapshot"]["selera_risiko"]["ambang"],10)
        self.post(f"/tata-kelola/risiko/{self.rid}/respons",{"penilaian_id":p["id"],"opsi":["terima"],"alasan":"Dalam batas selera pemilik"})

    def test_analysis_history_preserved_and_residual_does_not_replace_initial(self):
        p=self.policy()
        initial=self.assessment()
        self.assessment("residual",1,1)
        with Session(self.engine) as s:
            a=s.exec(select(AnalisisRisiko).where(AnalisisRisiko.risiko_id==self.rid)).one()
            self.assertEqual(a.skala_risiko,20)
            self.assertEqual(s.get(PenilaianRiwayat,initial["id"]).kebijakan_snapshot["id"],p["id"])
        response=self.call("DELETE",f"/risiko/{self.rid}")
        self.assertEqual(response.status_code,409)

    def test_form4_cannot_override_owner_appetite(self):
        self.policy()
        body={"risiko_id":self.rid,"skala_dampak":1,"skala_kemungkinan":5}
        self.assertTrue(self.post('/risiko/analisis',body)["is_prioritas"])
        self.post('/risiko/analisis',{**body,"is_prioritas":False},expected=422)
        self.post('/risiko/analisis',{**body,"is_prioritas":False},user="reviewer",expected=422)
        self.post('/risiko/analisis',{**body,"is_prioritas":False,"alasan":"Keputusan prioritas pimpinan"},user="reviewer",expected=422)
        with Session(self.engine) as s:
            self.assertEqual(len(s.exec(select(PenilaianRiwayat)).all()),1)

    def test_invalid_scores_residual_evidence_and_extra_fields(self):
        body={"tahap":"awal","dampak":6,"kemungkinan":1,"alasan":"Alasan lengkap"}
        self.post(f"/tata-kelola/risiko/{self.rid}/penilaian",body,expected=422)
        self.post(f"/tata-kelola/risiko/{self.rid}/penilaian",{**body,"dampak":True},expected=422)
        self.post(f"/tata-kelola/risiko/{self.rid}/penilaian",{**body,"dampak":1,"tahap":"residual"},expected=422)
        self.post(f"/tata-kelola/risiko/{self.rid}/penilaian",{**body,"dampak":1,"opd_id":2},expected=422)

    def test_response_escalation_and_acceptance_rules(self):
        self.policy()
        p=self.assessment("residual")
        r=self.post(f"/tata-kelola/risiko/{self.rid}/respons",{"penilaian_id":p["id"],"opsi":["kurangi_dampak"],"alasan":"Perlu pengendalian lanjut"})
        self.assertEqual(r["peran_penyetuju"],"upr_atasan")
        self.post(f"/tata-kelola/risiko/{self.rid}/respons",{"penilaian_id":p["id"],"opsi":["terima"],"alasan":"Coba menerima risiko utama"},expected=422)
        self.post(f'/tata-kelola/respons/{r["id"]}/keputusan',{"keputusan":"disetujui","catatan":"UPR atas menyetujui"},"reviewer")

    def test_multiple_actions_evidence_and_verification(self):
        def add():
            return self.post(f"/tata-kelola/risiko/{self.rid}/tindakan",{"uraian":"Perbaiki prosedur", "pic":"Petugas layanan","target":str(self.today)})
        a,b=add(),add()
        self.assertNotEqual(a["id"],b["id"])
        self.post(f'/tata-kelola/tindakan/{a["id"]}/pelaksanaan',{"status":"selesai","hasil":"Prosedur dibuat"},expected=422)
        self.post(f'/tata-kelola/tindakan/{a["id"]}/pelaksanaan',{"status":"selesai","hasil":"Prosedur dibuat","bukti":"SOP nomor 01"})
        self.post(f'/tata-kelola/tindakan/{a["id"]}/verifikasi',{"efektif":True,"catatan":"Telah diuji"},"reviewer")
        self.post(f'/tata-kelola/tindakan/{a["id"]}/pelaksanaan',{"status":"berjalan","hasil":"Ubah lagi"},expected=409)

    def test_reviewer_cannot_write_without_operator_role(self):
        with Session(self.engine) as s:
            s.add(PenugasanRisiko(opd_id=1,username="operator",nama="Pemantau",peran="kepatuhan",mulai=self.today,selesai=self.today,dasar="SK uji"));s.commit()
        self.post(f"/tata-kelola/risiko/{self.rid}/tindakan",{"uraian":"Perbaiki prosedur","pic":"Petugas","target":str(self.today)},expected=403)

    def test_reviu_followup_and_closure(self):
        r=self.post(f"/tata-kelola/risiko/{self.rid}/reviu",{"jenis":"inspektorat","temuan":"Bukti belum lengkap","rekomendasi":"Lengkapi dokumen","target":str(self.today)},"reviewer")
        self.post(f'/tata-kelola/reviu/{r["id"]}/verifikasi',{"efektif":True,"catatan":"Belum ada tindak lanjut"},"reviewer",409)
        self.post(f'/tata-kelola/reviu/{r["id"]}/tindak-lanjut',{"tindak_lanjut":"Dokumen dilengkapi","bukti":"Berkas nomor 03"})
        closed=self.post(f'/tata-kelola/reviu/{r["id"]}/verifikasi',{"efektif":True,"catatan":"Dokumen memadai"},"reviewer")
        self.assertEqual(closed["status"],"ditutup")

    def test_report_snapshot_and_period_filter(self):
        self.assessment()
        with Session(self.engine) as s:
            s.add_all([MonitoringRiskEvent(risiko_id=self.rid,tanggal_terjadi=date(self.year,1,2)),MonitoringRiskEvent(risiko_id=self.rid,tanggal_terjadi=date(self.year,4,1))]);s.commit()
        report=self.post('/tata-kelola/laporan',{"opd_id":1,"tahun":self.year,"periode":"TW1","jenis":"upr","ringkasan":"Laporan triwulan satu"})
        self.assertEqual(len(report["snapshot"]["kejadian"]),1)
        with Session(self.engine) as s:
            r=s.get(Risiko,self.rid);r.uraian_risiko="Nama sudah berubah";s.add(r);s.commit()
        saved=self.call("GET",f'/tata-kelola/laporan/{report["id"]}').json()
        self.assertEqual(saved["snapshot"]["risiko"][0]["uraian_risiko"],"Layanan terhenti")
        self.assertEqual(self.call("GET",f'/tata-kelola/laporan/{report["id"]}',user="outsider").status_code,403)

    def test_fraud_is_restricted_and_audit_omits_sensitive_data(self):
        body={"skenario":"Skenario terbatas", "proses_rawan":"Pengadaan barang","kelemahan":"Kontrol belum kuat","indikator":"Transaksi berulang"}
        self.assertEqual(self.call("PUT",f"/tata-kelola/risiko/{self.rid}/fraud",body).status_code,403)
        self.assertEqual(self.call("PUT",f"/tata-kelola/risiko/{self.rid}/fraud",body,"reviewer").status_code,200)
        self.assertEqual(self.call("GET",f"/tata-kelola/risiko/{self.rid}/fraud").status_code,403)
        logs=self.call("GET",f"/tata-kelola/audit?opd_id=1&tahun={self.year}").json()
        self.assertTrue(logs);self.assertNotIn("data",logs[0])
        self.assertNotIn("Skenario terbatas",self.call("GET",f"/tata-kelola/risiko/{self.rid}").text)

    def test_kamus_proposal_publishes_once(self):
        p=self.post('/tata-kelola/usulan-kamus',{"opd_id":1,"tahun":self.year,"nama":"Kegagalan jaringan","kategori":"Risiko SPBE","deskripsi":"Gangguan akses layanan"})
        result=self.post(f'/tata-kelola/usulan-kamus/{p["id"]}/keputusan',{"keputusan":"disetujui","catatan":"Layak dipublikasikan"},"reviewer")
        self.assertIsNotNone(result["kamus_id"])
        self.post(f'/tata-kelola/usulan-kamus/{p["id"]}/keputusan',{"keputusan":"disetujui","catatan":"Coba ulang"},"reviewer",409)

    def test_incident_scope_and_idempotent_copy(self):
        with Session(self.engine) as s:
            item=LaporKejadian(opd_id=1,tahun=self.year,no_hp="08000",nama_lengkap="Pelapor",uraian_kejadian="Gangguan layanan",waktu_kejadian=str(self.today),tempat="Kantor",pemicu="Jaringan terputus")
            s.add(item);s.commit();s.refresh(item);iid=item.id
        body={"status":"disetujui","risiko_id":self.other_rid,"salin_ke_form10":True}
        self.assertEqual(self.call("PUT",f"/approval-kejadian/{iid}/status",body).status_code,422)
        body["risiko_id"]=self.rid
        for _ in range(2):
            response=self.call("PUT",f"/approval-kejadian/{iid}/status",body)
            self.assertEqual(response.status_code,200,response.text)
        with Session(self.engine) as s:
            self.assertEqual(len(s.exec(select(MonitoringRiskEvent)).all()),1)
        summary=self.call("GET",f"/tata-kelola/ringkasan?opd_id=1&tahun={self.year}").json()
        self.assertEqual(summary["perlu_penilaian_ulang"],1)

    def test_priority_ties_use_area_category_then_leader(self):
        self.policy()
        self.assessment()
        response=self.call("PUT",f"/tata-kelola/risiko/{self.rid}/urutan",{
            "area_dampak":"Layanan","urutan_pimpinan":1,"alasan":"Layanan publik didahulukan"},"reviewer")
        self.assertEqual(response.status_code,200,response.text)
        with Session(self.engine) as s:
            second=Risiko(opd_id=1,tahun=self.year,jenis_risiko="strategis_opd",uraian_risiko="Risiko prioritas lain",kategori_risiko="Risiko Operasional")
            s.add(second);s.flush()
            s.add(AnalisisRisiko(risiko_id=second.id,skala_dampak=5,skala_kemungkinan=1,skala_risiko=20,is_prioritas=True));s.commit()
        grouped=self.call("GET",f"/risiko/form5?opd_id=1&tahun={self.year}").json()
        self.assertEqual(grouped[1]["items"][0]["id"],self.rid)

    def test_postgres_startup_is_idempotent_and_preserves_existing_rows(self):
        if self.engine.dialect.name != "postgresql":
            self.skipTest("Memerlukan PostgreSQL sementara")
        from app.db import init_db
        with patch("app.db.engine",self.engine):
            init_db();init_db()
        with Session(self.engine) as s:
            self.assertEqual(s.get(Risiko,self.rid).uraian_risiko,"Layanan terhenti")

    def test_postgres_concurrent_decision_is_applied_once(self):
        if self.engine.dialect.name != "postgresql":
            self.skipTest("Memerlukan PostgreSQL sementara")
        from concurrent.futures import ThreadPoolExecutor
        p=self.policy(False)
        def decide():
            return self.call("POST",f'/tata-kelola/kebijakan/{p["id"]}/keputusan',{"keputusan":"disetujui","catatan":"Persetujuan bersamaan"},"reviewer").status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(lambda _:decide(),range(2)))
        self.assertEqual(sorted(outcomes),[200,409])

    def test_consolidated_report_only_includes_authorized_strategic_pemda(self):
        body={"opd_id":1,"tahun":self.year,"periode":"TW1","jenis":"upr","ringkasan":"Kompilasi strategis daerah","cakupan":"pemda","opd_ids":[1,2]}
        self.post('/tata-kelola/laporan',body,"reviewer",403)
        self.users['reviewer']['opds']=[1,2]
        with Session(self.engine) as s:
            s.add_all([Risiko(opd_id=1,tahun=self.year,jenis_risiko="strategis_pemda",uraian_risiko="Target daerah satu"),
                Risiko(opd_id=2,tahun=self.year,jenis_risiko="strategis_pemda",uraian_risiko="Target daerah dua")]);s.commit()
        report=self.post('/tata-kelola/laporan',body,"reviewer")
        self.assertEqual(len(report['snapshot']['risiko']),2)
        self.assertEqual(report['snapshot']['opd_ids'],[1,2])
        self.assertEqual(self.call('GET',f'/tata-kelola/laporan/{report["id"]}').status_code,403)
        self.assertEqual(self.call('GET',f'/tata-kelola/laporan?opd_id=1&tahun={self.year}').json(),[])

    def test_expired_assignment_cannot_approve(self):
        p=self.policy(False)
        with Session(self.engine) as s:
            for assignment in s.exec(select(PenugasanRisiko)).all():
                assignment.selesai=self.today-timedelta(days=1);s.add(assignment)
            s.commit()
        self.post(f'/tata-kelola/kebijakan/{p["id"]}/keputusan',{"keputusan":"disetujui","catatan":"Masa tugas berakhir"},"reviewer",403)

    def test_new_policy_does_not_change_old_assessment_snapshot(self):
        p=self.policy();old=self.assessment()
        newer=self.policy()
        self.assertNotEqual(p['id'],newer['id'])
        with Session(self.engine) as s:
            history=s.get(PenilaianRiwayat,old['id'])
            self.assertEqual(history.kebijakan_id,p['id'])
            self.assertEqual(history.kebijakan_snapshot['id'],p['id'])

    def test_legacy_approved_incident_reuses_matching_event(self):
        with Session(self.engine) as s:
            item=LaporKejadian(opd_id=1,tahun=self.year,no_hp="08000",nama_lengkap="Pelapor",uraian_kejadian="Gangguan lama",waktu_kejadian=str(self.today),tempat="Kantor",pemicu="Jaringan",status="disetujui",risiko_id=self.rid)
            s.add(item)
            s.add(MonitoringRiskEvent(risiko_id=self.rid,tanggal_terjadi=self.today,sebab_kejadian="Jaringan",dampak_kejadian="Gangguan lama",keterangan_kejadian="Tempat: Kantor. Dilaporkan oleh: Pelapor (08000)"))
            s.commit();s.refresh(item);iid=item.id
        response=self.call("PUT",f"/approval-kejadian/{iid}/status",{"status":"disetujui","risiko_id":self.rid,"salin_ke_form10":True})
        self.assertEqual(response.status_code,200,response.text)
        with Session(self.engine) as s:
            self.assertEqual(len(s.exec(select(MonitoringRiskEvent)).all()),1)


    def set_appetite(self, ambang, owner=None, **kwargs):
        return self.post('/selera-risiko', {"opd_id":1,"tahun":self.year,"ambang":ambang,
            "pemilik_risiko":owner,"penetap":"Kepala Dinas","pertimbangan_sumber_daya":"Evaluasi kapasitas SDM dan anggaran"}, **kwargs)

    def test_appetite_strict_range_and_scope(self):
        for invalid in [0,26,-1,True,1.5,"12",None]:
            with self.subTest(ambang=invalid):
                self.set_appetite(invalid,expected=422)
        self.set_appetite(15,user='outsider',expected=403)
        self.assertEqual(self.call('GET',f'/selera-risiko?opd_id=1&tahun={self.year}',user='outsider').status_code,403)
        self.assertEqual(self.call('GET',f'/selera-risiko?opd_id=1&tahun={self.year}',user=None).status_code,401)
        with Session(self.engine) as s:
            s.add(PenugasanRisiko(opd_id=1,username='operator',nama='Pemantau',peran='kepatuhan',
                mulai=date(self.year,1,1),selesai=date(self.year,12,31),dasar='SK pemantauan'))
            s.commit()
        self.set_appetite(15,expected=403)
        result=self.call('GET',f'/selera-risiko?opd_id=1&tahun={self.year}').json()
        self.assertFalse(result['boleh_tulis'])

    def test_appetite_missing_blocks_new_assessment_without_invented_default(self):
        from app.models.selera import SeleraRisiko
        with Session(self.engine) as s:
            for row in s.exec(select(SeleraRisiko)).all(): s.delete(row)
            s.commit()
        self.post('/risiko/analisis',{'risiko_id':self.rid,'skala_dampak':1,'skala_kemungkinan':1},expected=409)
        matrix=self.call('GET',f'/risiko/matriks?opd_id=1&tahun={self.year}').json()
        self.assertIsNone(matrix['selera']['ambang'])
        self.assertIsNone(matrix['kebijakan']['selera'])
        self.assertIsNone(self.call('GET',f'/risiko?opd_id=1&tahun={self.year}').json()[0]['analisis']['is_prioritas'])
        self.assertEqual(self.call('GET',f'/tata-kelola/ringkasan?opd_id=1&tahun={self.year}').status_code,200)
        self.set_appetite(11)
        self.assertFalse(self.assessment(dampak=1,kemungkinan=5)['prioritas'])

    def test_appetite_boundary_one_twentyfive_and_score_equal(self):
        self.set_appetite(1)
        self.assertFalse(self.assessment(dampak=1,kemungkinan=1)['prioritas'])
        self.assertTrue(self.assessment(dampak=1,kemungkinan=2)['prioritas'])
        self.set_appetite(25)
        self.assertFalse(self.assessment(dampak=5,kemungkinan=5)['prioritas'])
        self.assertEqual(self.call('GET',f'/risiko/matriks?opd_id=1&tahun={self.year}').json()['selera']['diterima'],list(range(1,26)))

    def test_appetite_owner_override_and_entity_fallback(self):
        self.assertEqual(self.call('PUT',f'/risiko/{self.rid}',{'pemilik_risiko':'Kepala Bidang A'}).status_code,200)
        self.set_appetite(20,'  KEPALA   BIDANG A  ')
        self.assertFalse(self.assessment()['prioritas'])
        self.set_appetite(5)
        rows=self.call('GET',f'/risiko?opd_id=1&tahun={self.year}').json()
        self.assertEqual(rows[0]['selera_risiko']['ambang'],20)
        self.assertFalse(rows[0]['analisis']['is_prioritas'])
        with Session(self.engine) as s:
            self.assertFalse(s.exec(select(AnalisisRisiko)).one().is_prioritas)
            s.add(Risiko(opd_id=1,tahun=self.year,jenis_risiko='strategis_opd',pemilik_risiko='Kepala Bidang B',uraian_risiko='Risiko lain'))
            s.commit()
        matrix=self.call('GET',f'/risiko/matriks?opd_id=1&tahun={self.year}').json()
        self.assertTrue(matrix['selera']['beragam'])
        self.assertIsNone(matrix['selera']['diterima'])
        matrix=self.call('GET',f'/risiko/matriks?opd_id=1&tahun={self.year}&pemilik=Kepala%20Bidang%20A').json()
        self.assertEqual(matrix['selera']['ambang'],20)
        self.assertEqual(len(matrix['cells']['1-5']),1)
        other_year=self.call('GET',f'/selera-risiko?opd_id=1&tahun={self.year+1}').json()
        self.assertEqual(other_year['aktif'],[])
        other_opd=self.call('GET',f'/selera-risiko?opd_id=2&tahun={self.year}',user='outsider').json()
        self.assertEqual(other_opd['aktif'],[])

    def test_appetite_change_reclassifies_current_but_preserves_archive_and_rtp(self):
        old=self.assessment()
        self.post('/risiko/rtp',{'risiko_id':self.rid,'rencana_tindak':'Rencana tetap tersimpan','status_pengendalian':'tidak_ada','respon_risiko':'kurangi_dampak'})
        report=self.post('/tata-kelola/laporan',{'opd_id':1,'tahun':self.year,'periode':'TW1','jenis':'upr','ringkasan':'Laporan sebelum revisi'})
        changed=self.set_appetite(20)
        self.assertEqual(changed['analisis_diperbarui'],1)
        rows=self.call('GET',f'/risiko?opd_id=1&tahun={self.year}').json()
        self.assertFalse(rows[0]['analisis']['is_prioritas'])
        self.assertEqual(self.call('GET',f'/risiko/form5?opd_id=1&tahun={self.year}').json()[1]['items'],[])
        with Session(self.engine) as s:
            from app.models import RtpRisiko
            history=s.get(PenilaianRiwayat,old['id'])
            self.assertTrue(history.prioritas)
            self.assertEqual(history.kebijakan_snapshot['selera_risiko']['ambang'],10)
            self.assertEqual(len(s.exec(select(RtpRisiko)).all()),1)
            self.assertFalse(s.exec(select(AnalisisRisiko)).one().is_prioritas)
        archived=self.call('GET',f'/tata-kelola/laporan/{report["id"]}').json()
        self.assertEqual(archived['snapshot'],report['snapshot'])
        self.assertEqual(archived['snapshot']['selera_risiko']['1'][0]['ambang'],10)
        self.post(f'/tata-kelola/risiko/{self.rid}/respons',{'penilaian_id':old['id'],'opsi':['terima'],'alasan':'Batas sudah berubah'},expected=409)

    def test_appetite_owner_change_reclassifies_analysis(self):
        self.assessment()
        self.set_appetite(25,'Pemilik Baru')
        result=self.call('PUT',f'/risiko/{self.rid}',{'pemilik_risiko':'Pemilik Baru'})
        self.assertEqual(result.status_code,200,result.text)
        with Session(self.engine) as s:
            self.assertFalse(s.exec(select(AnalisisRisiko)).one().is_prioritas)

    def test_appetite_dashboard_uses_threshold_instead_of_color(self):
        from app.routers import dashboard
        self.client.app.include_router(dashboard.router,prefix='/api',dependencies=[OpdScopeDep])
        self.set_appetite(25)
        self.assessment(dampak=5,kemungkinan=5)
        result=self.call('GET',f'/dashboard/summary?opd_id=1&tahun={self.year}')
        self.assertEqual(result.status_code,200,result.text)
        cells=result.json()['heatmap']['cells']
        self.assertFalse(cells['5-5'][0]['is_prioritas'])
        self.assertEqual(cells['5-5'][0]['ambang_selera'],25)

    def test_postgres_appetite_and_assessment_concurrency(self):
        if self.engine.dialect.name != 'postgresql':
            self.skipTest('Memerlukan PostgreSQL sementara')
        from concurrent.futures import ThreadPoolExecutor
        self.assessment()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(self.set_appetite,25),pool.submit(self.assessment)]
            for f in futures: f.result(timeout=15)
        with Session(self.engine) as s:
            self.assertFalse(s.exec(select(AnalisisRisiko)).one().is_prioritas)

    def test_appetite_change_blocks_approval_of_stale_response(self):
        p=self.assessment(dampak=1,kemungkinan=2)
        response=self.post(f'/tata-kelola/risiko/{self.rid}/respons',{'penilaian_id':p['id'],'opsi':['terima'],'alasan':'Di dalam selera saat ini'})
        self.set_appetite(1)
        self.post(f'/tata-kelola/respons/{response["id"]}/keputusan',{'keputusan':'disetujui','catatan':'Belum memperhitungkan revisi'},user='reviewer',expected=409)
        self.post(f'/tata-kelola/respons/{response["id"]}/keputusan',{'keputusan':'ditolak','catatan':'Ajukan ulang sesuai revisi'},user='reviewer')

    def rtp_body(self, **changes):
        return {'risiko_id':self.rid,'status_pengendalian':'sudah_ada','respon_risiko':'kurangi_kemungkinan',
            'pengendalian_ada':'SOP pemeriksaan harian','bukti_judul':'Dokumen SOP',
            'bukti_link':'https://example.org/sop.pdf','target_waktu':f'{self.year}-12-31',**changes}

    def test_rtp_existing_control_requires_description_title_and_evidence(self):
        for changes in [{'pengendalian_ada':' '},{'bukti_judul':''},{'bukti_link':None},
                        {'bukti_link':'javascript:alert(1)'},{'bukti_link':'https://'},
                        {'respon_risiko':'lain'},{'status_pengendalian':'lain'},{'target_waktu':'Triwulan IV'}]:
            with self.subTest(changes=changes):
                self.post('/risiko/rtp',self.rtp_body(**changes),expected=422)
        self.post('/risiko/rtp',self.rtp_body(),user='outsider',expected=403)
        result=self.post('/risiko/rtp',self.rtp_body())
        self.assertEqual(result['bukti_judul'],'Dokumen SOP')
        self.assertEqual(result['target_waktu'],f'{self.year}-12-31')

    def test_rtp_upload_download_and_cross_risk_protection(self):
        import base64
        from app.models.risiko import RtpBukti
        content=b'%PDF-1.4\nExample test file'
        result=self.post('/risiko/rtp',self.rtp_body(bukti_link=None,bukti_upload={
            'nama':'../bukti.pdf','base64':base64.b64encode(content).decode()}))
        bid=result['bukti_berkas_id']
        self.assertEqual(result['bukti_nama'],'bukti.pdf')
        path=f'/risiko/rtp/{self.rid}/berkas/{bid}'
        response=self.call('GET',path)
        self.assertEqual(response.content,content)
        self.assertIn('attachment;',response.headers['content-disposition'])
        self.assertEqual(self.call('GET',path,user='outsider').status_code,403)
        self.assertEqual(self.call('GET',path,user=None).status_code,401)
        self.assertEqual(self.call('GET',f'/risiko/rtp/{self.other_rid}/berkas/{bid}',user='outsider').status_code,404)
        self.post('/risiko/rtp',self.rtp_body(risiko_id=self.other_rid,bukti_link=None,bukti_berkas_id=bid),user='outsider',expected=422)
        self.post('/risiko/rtp',self.rtp_body(bukti_link=None,bukti_berkas_id=bid))
        self.post('/risiko/rtp',self.rtp_body(bukti_link=None,bukti_upload={'nama':'bad.pdf','base64':'invalid@@'}),expected=422)
        self.post('/risiko/rtp',self.rtp_body(bukti_link=None,bukti_upload={'nama':'empty.pdf','base64':''}),expected=422)
        with Session(self.engine) as s:
            self.assertEqual(len(s.exec(select(RtpBukti)).all()),1)
            audits=s.exec(select(AuditRisiko).where(AuditRisiko.aksi=='rtp_diperbarui')).all()
            self.assertNotIn('konten',audits[-1].data)

    def test_rtp_no_control_clears_active_evidence_and_preserves_realization(self):
        from app.models import RtpRisiko
        self.post('/risiko/rtp',self.rtp_body())
        with Session(self.engine) as s:
            r=s.exec(select(RtpRisiko)).one();r.realisasi_waktu='Data realisasi lama';s.add(r);s.commit()
        result=self.post('/risiko/rtp',{'risiko_id':self.rid,'status_pengendalian':'tidak_ada','respon_risiko':'hindari','target_waktu':None})
        self.assertIsNone(result['pengendalian_ada'])
        self.assertIsNone(result['bukti_link'])
        self.assertIsNone(result['bukti_judul'])
        self.assertEqual(result['realisasi_waktu'],'Data realisasi lama')
        for option in ['kurangi_kemungkinan','kurangi_dampak','bagi','hindari','terima']:
            self.post('/risiko/rtp',{'risiko_id':self.rid,'status_pengendalian':'tidak_ada','respon_risiko':option})
        self.post('/risiko/rtp',self.rtp_body(status_pengendalian='tidak_ada'),expected=422)

    def test_postgres_rtp_migration_preserves_legacy_dates(self):
        if self.engine.dialect.name != 'postgresql':
            self.skipTest('Memerlukan PostgreSQL sementara')
        from app.db import init_db
        from app.models import RtpRisiko
        from sqlmodel import text
        with Session(self.engine) as s:
            s.add(RtpRisiko(risiko_id=self.rid, target_waktu='Triwulan IV', realisasi_waktu='Selesai sebelumnya'))
            s.commit()
        with self.engine.begin() as conn:
            for name in ['status_pengendalian','respon_risiko','bukti_judul','bukti_link','bukti_berkas_id','bukti_nama','target_mulai','target_selesai']:
                conn.execute(text('ALTER TABLE tr_rtp_risiko DROP COLUMN ' + name))
        with patch('app.db.engine',self.engine):
            init_db();init_db()
        with Session(self.engine) as s:
            row=s.exec(select(RtpRisiko)).one()
            self.assertEqual(row.target_waktu,'Triwulan IV')
            self.assertEqual(row.realisasi_waktu,'Selesai sebelumnya')
            self.assertIsNone(row.status_pengendalian)

    def test_rtp_target_date_range(self):
        body=self.rtp_body(target_waktu=None,target_mulai=f'{self.year}-04-01',target_selesai=f'{self.year}-06-30')
        result=self.post('/risiko/rtp',body)
        self.assertEqual(result['target_mulai'],f'{self.year}-04-01')
        self.assertEqual(result['target_selesai'],f'{self.year}-06-30')
        self.assertEqual(result['target_waktu'],f'{self.year}-04-01 s.d. {self.year}-06-30')
        self.assessment()
        row=self.call('GET',f'/risiko/rtp?opd_id=1&tahun={self.year}').json()[0]
        self.assertEqual(row['rtp']['target_mulai'],result['target_mulai'])
        for changes in [{'target_selesai':None},{'target_mulai':None},
                        {'target_selesai':f'{self.year}-03-31'}, {'target_mulai':'invalid'}]:
            self.post('/risiko/rtp',{**body,**changes},expected=422)
        self.post('/risiko/rtp',{**body,'target_selesai':body['target_mulai']})
        old=self.post('/risiko/rtp',self.rtp_body())
        self.assertEqual(old['target_mulai'],old['target_waktu'])
        self.assertEqual(old['target_selesai'],old['target_waktu'])


if __name__ == '__main__':
    unittest.main()
