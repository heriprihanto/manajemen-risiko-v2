import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from app.services.whatsapp import normalize_phone, send_whatsapp_invitation
from app.core.config import settings


class WhatsAppTests(unittest.TestCase):
    def test_phone(self):
        for phone in ('0812-3456-7890', '+62 812 3456 7890', '6281234567890', '81234567890'):
            self.assertEqual(normalize_phone(phone), '6281234567890')
        for phone in ('', 'abc081234567890', '123', '08123,08124'):
            with self.assertRaises(ValueError):
                normalize_phone(phone)

    def test_payload_and_failure(self):
        resp = SimpleNamespace(no_hp='081234567890', tahun=2027, nama_responden='Uji',
                               email='test@example.com', token_id='TOKEN-UJI')
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"code":"SUCCESS"}'
        with patch.object(settings, 'WHATSAPP_GATEWAY_URL', 'http://gateway.test/send/message'), \
             patch.object(settings, 'WHATSAPP_DEVICE_ID', 'test-device'), \
             patch('app.services.whatsapp.urlopen') as send:
            send.return_value.__enter__.return_value = response
            send_whatsapp_invitation(resp)
            request = send.call_args.args[0]
            payload = json.loads(request.data)
            self.assertEqual(payload['phone'], '6281234567890@s.whatsapp.net')
            self.assertIn('TOKEN-UJI', payload['message'])
            self.assertEqual(request.get_header('X-device-id'), 'test-device')
            self.assertEqual(request.full_url, 'http://gateway.test/send/message')
            response.read.return_value = b'{"success":false}'
            with self.assertRaises(ValueError):
                send_whatsapp_invitation(resp)
