import unittest
from types import SimpleNamespace
from sqlmodel import Session, SQLModel, create_engine
from app.models import Pengaturan, SETTINGS_ID, Opd
from app.services.cee_invitation import build_invitation, DEFAULT_TEMPLATE_EMAIL_SUBJECT
from app.services.whatsapp import send_whatsapp_invitation
from app.routers import pengaturan
from unittest.mock import patch, MagicMock


class PengaturanTemplateTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.session.add_all([
            Opd(id_sub_pd=1, kode='1.01', nama_pd='Dinas Kesehatan', aktif=1),
            Pengaturan(
                id=SETTINGS_ID,
                tahun_default=2027,
                template_email_subject='Undangan CEE {tahun} untuk {nama}',
                template_email='Halo {nama} ({jabatan}) di {opd}, klik {link} token: {token}',
                template_wa='*Halo {nama}*, ini token CEE Anda: *{token}* di {link}',
            ),
        ])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_custom_templates_rendered(self):
        resp = SimpleNamespace(
            opd_id=1,
            tahun=2027,
            nama_responden='Budi Santoso',
            nip='198001012005011001',
            jabatan='Sekretaris Dinas',
            email='budi@example.com',
            no_hp='081234567890',
            token_id='TOKEN-BUDI-123',
        )

        # Email invitation
        email_msg = build_invitation(resp, session=self.session)
        self.assertEqual(email_msg['Subject'], 'Undangan CEE 2027 untuk Budi Santoso')
        plain_body = email_msg.get_body(preferencelist=('plain',)).get_content()
        self.assertIn('Halo Budi Santoso (Sekretaris Dinas) di Dinas Kesehatan', plain_body)
        self.assertIn('token: TOKEN-BUDI-123', plain_body)

        # WhatsApp invitation
        response_mock = MagicMock()
        response_mock.status = 200
        response_mock.read.return_value = b'{"code":"SUCCESS"}'

        with patch('app.services.whatsapp.settings.WHATSAPP_GATEWAY_URL', 'http://gateway.test/send/message'), \
             patch('app.services.whatsapp.settings.WHATSAPP_DEVICE_ID', 'test-device'), \
             patch('app.services.whatsapp.urlopen') as mock_url:
            mock_url.return_value.__enter__.return_value = response_mock
            send_whatsapp_invitation(resp, session=self.session)
            req = mock_url.call_args.args[0]
            import json
            payload = json.loads(req.data)
            self.assertEqual(payload['phone'], '6281234567890@s.whatsapp.net')
            self.assertEqual(payload['message'], '*Halo Budi Santoso*, ini token CEE Anda: *TOKEN-BUDI-123* di http://localhost:5173/survei')

    def test_router_read_and_update_templates(self):
        data = pengaturan.read(session=self.session)
        self.assertIn('default_template_email_subject', data)
        self.assertEqual(data['template_email_subject'], 'Undangan CEE {tahun} untuk {nama}')

        # Update templates
        pengaturan.update(
            payload={
                'template_email_subject': 'New Subject {tahun}',
                'template_wa': 'Pesan WA Baru {token}',
            },
            session=self.session,
            user={'username': 'admin'},
        )
        updated_data = pengaturan.read(session=self.session)
        self.assertEqual(updated_data['template_email_subject'], 'New Subject {tahun}')
        self.assertEqual(updated_data['template_wa'], 'Pesan WA Baru {token}')


if __name__ == '__main__':
    unittest.main()
