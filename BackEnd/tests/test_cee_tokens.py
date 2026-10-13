import unittest
from unittest.mock import patch
import smtplib

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from app.models import CeeResponden, CeeJawaban, Opd, Pengaturan, KuesionerKategori, KuesionerPertanyaan
from app.routers import cee, survei
from app.core.security import require_admin


class TokenSurveyTests(unittest.TestCase):
    def setUp(self):
        self.wa_mock = patch("app.services.whatsapp.send_whatsapp_invitation").start()
        self.addCleanup(patch.stopall)
        self.engine = create_engine('sqlite://')
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.session.add_all([
            Opd(id_sub_pd=1, nama_pd='OPD Uji'),
            Pengaturan(id=1, tahun_default=2027),
            KuesionerKategori(id=1, kode='A', nama='Kategori'),
            KuesionerPertanyaan(id=1, kategori_id=1, nomor='1', pertanyaan='Pertanyaan'),
        ])
        self.session.commit()
        self.payload = dict(opd_id=1, tahun=2027, nip='001234', nama_responden='Responden',
                            jabatan='Staf', email='responden@example.com', no_hp='08123456789')
        self.resp = cee.create_responden(self.payload, self.session, {'role_id': 1})

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_token_identity_and_submission(self):
        self.assertTrue(self.resp.token_id)
        self.assertNotIn('token_id', self.resp.model_dump())
        resp = survei.token_responden('Bearer ' + self.resp.token_id, self.session)
        survei.submit({'jawaban': {'1': 4}, 'opd_id': 999, 'nama_responden': 'Forged', 'narasi': 'Perlu perbaikan SOP'}, resp, self.session)
        self.assertEqual(resp.opd_id, 1)
        self.assertEqual(resp.nama_responden, 'Responden')
        self.assertEqual(resp.narasi, 'Perlu perbaikan SOP')
        stat = survei.survey_status(resp, self.session)
        self.assertTrue(stat['submitted'])
        self.assertEqual(stat['narasi'], 'Perlu perbaikan SOP')
        with self.assertRaises(HTTPException) as error:
            survei.submit({'jawaban': {'1': 1}}, resp, self.session)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(len(self.session.exec(select(CeeJawaban)).all()), 1)

    def test_submitted_respondent_cannot_be_edited_or_deleted(self):
        survei.submit({'jawaban': {'1': 4}}, self.resp, self.session)
        rid = self.resp.id
        for legacy in (False, True):
            if legacy:
                self.resp.submitted_at = None
                self.session.add(self.resp)
                self.session.commit()
            with self.assertRaises(HTTPException) as error:
                cee.update_responden(rid, {'nama_responden': 'Diubah'}, self.session, {'role_id': 1})
            self.assertEqual(error.exception.status_code, 409)
            with self.assertRaises(HTTPException) as error:
                cee.delete_responden(rid, self.session, {'role_id': 1})
            self.assertEqual(error.exception.status_code, 409)
            self.assertEqual(self.session.get(CeeResponden, rid).nama_responden, 'Responden')
            self.assertEqual(len(self.session.exec(select(CeeJawaban)).all()), 1)

    def test_pending_respondent_can_be_deleted(self):
        rid = self.resp.id
        cee.delete_responden(rid, self.session, {'role_id': 1})
        self.assertIsNone(self.session.get(CeeResponden, rid))

    def test_invalid_token(self):
        for header in ('', 'Bearer invalid', 'Basic anything'):
            with self.assertRaises(HTTPException) as error:
                survei.token_responden(header, self.session)
            self.assertEqual(error.exception.status_code, 401)

    def test_invalid_answers_do_not_submit(self):
        for answers in ({}, {'1': True}, {'1': 1.5}, {'1': 5}, {'999': 3}, []):
            with self.assertRaises(HTTPException):
                survei.submit({'jawaban': answers}, self.resp, self.session)
            self.assertIsNone(self.resp.submitted_at)
        self.assertFalse(self.session.exec(select(CeeJawaban)).all())

    def test_closed_and_wrong_year(self):
        config = self.session.get(Pengaturan, 1)
        for year, active in ((2026, 1), (2027, 0)):
            config.tahun_default, config.survei_aktif = year, active
            self.session.add(config)
            self.session.commit()
            with self.assertRaises(HTTPException) as error:
                survei.submit({'jawaban': {'1': 3}}, self.resp, self.session)
            self.assertEqual(error.exception.status_code, 403)

    def test_duplicate_identity_and_admin_access(self):
        with self.assertRaises(HTTPException) as error:
            cee.create_responden(self.payload, self.session, {'role_id': 1})
        self.assertEqual(error.exception.status_code, 409)
        with self.assertRaises(HTTPException) as error:
            require_admin({'role_id': 2})
        self.assertEqual(error.exception.status_code, 403)

    def test_invitation_success_failure_and_token_rotation(self):
        with patch.object(cee.settings, 'SMTP_HOST', 'smtp.example.com'), patch.object(cee.settings, 'SMTP_FROM', 'admin@example.com'):
            with patch.object(cee, 'send_invitation', side_effect=smtplib.SMTPException('failed')):
                result = cee.invite_responden(1, 2027, self.session, {'role_id': 1})
                self.assertEqual(len(result['gagal']), 1)
                self.assertIsNone(self.resp.invited_at)
                self.wa_mock.assert_not_called()
                self.assertIsNone(self.resp.whatsapp_invited_at)
            with patch.object(cee, 'send_invitation') as send:
                result = cee.invite_responden(1, 2027, self.session, {'role_id': 1})
                self.assertEqual(result['terkirim'], 1)
                send.assert_called_once()
                self.wa_mock.assert_not_called()
                self.assertIsNotNone(self.resp.invited_at)
        token = self.resp.token_id
        cee.update_responden(self.resp.id, {'email': 'new@example.com'}, self.session, {'role_id': 1})
        self.assertNotEqual(token, self.resp.token_id)
        with self.assertRaises(HTTPException):
            survei.token_responden('Bearer ' + token, self.session)

    def test_invitation_whatsapp(self):
        # Batch WhatsApp
        result = cee.invite_responden(1, 2027, self.session, {'role_id': 1}, channel='whatsapp')
        self.assertEqual(result['terkirim'], 1)
        self.wa_mock.assert_called_once()
        self.assertIsNotNone(self.resp.whatsapp_invited_at)

        # Single WhatsApp
        res_single = cee.invite_single_responden(self.resp.id, self.session, {'role_id': 1}, channel='whatsapp')
        self.assertTrue(res_single['ok'])

        # Error when no_hp missing
        self.resp.no_hp = ''
        self.session.add(self.resp)
        self.session.commit()
        with self.assertRaises(HTTPException) as err:
            cee.invite_single_responden(self.resp.id, self.session, {'role_id': 1}, channel='whatsapp')
        self.assertEqual(err.exception.status_code, 400)


if __name__ == '__main__':
    unittest.main()
