"""WhatsApp invitations through the configured local gateway."""
import json
import re
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.services.cee_invitation import build_invitation


def normalize_phone(value):
    raw = str(value or '').strip()
    if not re.fullmatch(r'\+?[0-9 ().-]+', raw):
        raise ValueError('Nomor WhatsApp tidak valid')
    number = re.sub(r'\D', '', raw)
    if number.startswith('0'):
        number = '62' + number[1:]
    elif number.startswith('8'):
        number = '62' + number
    if not re.fullmatch(r'628\d{7,11}', number):
        raise ValueError('Gunakan nomor seluler Indonesia: 08…, 628…, atau +628…')
    return number


def send_whatsapp_invitation(resp, session=None):
    if not settings.WHATSAPP_GATEWAY_URL.strip() or not settings.WHATSAPP_DEVICE_ID.strip():
        raise ValueError("WHATSAPP_GATEWAY_URL dan WHATSAPP_DEVICE_ID belum dikonfigurasi")

    from app.services.cee_invitation import render_placeholders, DEFAULT_TEMPLATE_WA
    from app.models.pengaturan import Pengaturan, SETTINGS_ID
    from app.models.master import Opd

    cfg = None
    opd_nama = ""
    if session:
        try:
            cfg = session.get(Pengaturan, SETTINGS_ID)
            if getattr(resp, "opd_id", None):
                opd = session.get(Opd, resp.opd_id)
                if opd:
                    opd_nama = opd.nama_pd or ""
        except Exception:
            pass

    tpl = (cfg.template_wa if cfg and cfg.template_wa else None) or DEFAULT_TEMPLATE_WA
    msg = render_placeholders(tpl, resp, opd_nama)

    payload = {
        'phone': normalize_phone(resp.no_hp) + '@s.whatsapp.net',
        'message': msg,
    }
    request = Request(settings.WHATSAPP_GATEWAY_URL,
                      data=json.dumps(payload).encode('utf-8'), method='POST',
                      headers={'Accept': 'application/json', 'Content-Type': 'application/json',
                               'X-Device-Id': settings.WHATSAPP_DEVICE_ID})
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read())
            if not 200 <= response.status < 300 or not isinstance(result, dict):
                raise ValueError('Respons gateway WhatsApp tidak valid')
            code = result.get('code')
            if (result.get('success') is False or result.get('status') in ('error', 'failed', False)
                    or (code is not None and str(code) not in ('SUCCESS', '200', '201', '202'))):
                safe_code = re.sub(r'[^a-zA-Z0-9_-]', '', str(code or 'UNKNOWN'))[:60]
                raise ValueError(f'Gateway WhatsApp menolak pengiriman (kode {safe_code}); periksa perangkat dan nomor penerima')
    except HTTPError as exc:
        body_text = None
        try:
            body_bytes = exc.read()
            if body_bytes:
                body_json = json.loads(body_bytes.decode('utf-8'))
                if isinstance(body_json, dict):
                    body_text = body_json.get('message') or body_json.get('error') or body_json.get('code')
        except Exception:
            pass

        if body_text:
            if "not on whatsapp" in str(body_text).lower():
                raise ValueError(f"Nomor WhatsApp {resp.no_hp} tidak terdaftar di WhatsApp ({body_text})") from exc
            raise ValueError(f"Gateway WhatsApp ({exc.code}): {body_text}") from exc

        reasons = {
            400: 'Permintaan ditolak; periksa nomor penerima dan status perangkat gateway',
            401: 'Gateway membutuhkan autentikasi',
            403: 'Akses ke gateway ditolak',
            404: 'Endpoint atau perangkat WhatsApp tidak ditemukan',
            429: 'Batas pengiriman gateway tercapai; coba lagi nanti',
            500: 'Gateway mengalami kesalahan; periksa log gateway dan koneksi perangkat',
            503: 'Gateway atau perangkat WhatsApp belum siap',
        }
        raise ValueError(f'WhatsApp HTTP {exc.code}: {reasons.get(exc.code, "Gateway gagal memproses pengiriman")}') from exc
    except URLError as exc:
        if isinstance(exc.reason, ConnectionRefusedError):
            reason = 'Koneksi gateway ditolak; pastikan layanan gateway berjalan'
        elif isinstance(exc.reason, socket.gaierror):
            reason = 'Alamat gateway tidak dapat ditemukan (DNS)'
        elif isinstance(exc.reason, (TimeoutError, socket.timeout)):
            reason = 'Gateway tidak merespons dalam 30 detik; status pengiriman belum diketahui'
        else:
            reason = 'Tidak dapat terhubung ke gateway; periksa jaringan backend'
        raise ValueError(reason) from exc
    except TimeoutError as exc:
        raise ValueError('Gateway tidak merespons dalam 30 detik; status pengiriman belum diketahui') from exc
    except json.JSONDecodeError as exc:
        raise ValueError('Gateway mengembalikan respons bukan JSON; periksa URL endpoint') from exc
