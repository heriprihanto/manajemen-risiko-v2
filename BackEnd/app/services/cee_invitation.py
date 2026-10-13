"""Send one private survey invitation through the configured SMTP server."""
import smtplib
import ssl
from email.message import EmailMessage
from html import escape
from app.core.config import settings


DEFAULT_TEMPLATE_EMAIL_SUBJECT = "Permohonan Partisipasi Pengisian Kuesioner CEE Tahun {tahun}"

DEFAULT_TEMPLATE_EMAIL = (
    "Yth. Bapak/Ibu {nama}, Aparatur Sipil Negara (ASN) di Pemerintah Kota Tegal\n\n"
    "Dalam rangka pelaksanaan Penilaian Lingkungan Pengendalian Intern (CEE) Tahun {tahun}, "
    "kami memohon dukungan Bapak/Ibu untuk berpartisipasi dalam pengisian kuesioner "
    "sebagai bagian dari evaluasi penguatan integritas, tata kelola, dan efektivitas "
    "sistem pengendalian pada lingkungan organisasi.\n\n"
    "Partisipasi Bapak/Ibu akan memberikan kontribusi penting dalam menyediakan "
    "data yang akurat untuk analisis, sekaligus menjadi dasar perumusan rekomendasi "
    "perbaikan lingkungan pengendalian di Pemerintah Kota Tegal.\n\n"
    "Tautan Kuesioner: {link}\n\n"
    "Token Akses Responden: {token}\n\n"
    "Masukkan token akses di atas saat membuka kuesioner, tanpa perlu login. "
    "Token bersifat pribadi dan jawaban hanya dapat dikirim satu kali.\n\n"
    "Apabila dibutuhkan informasi tambahan, mohon menghubungi: "
    "Heri P | (+62-812-8320-3050) "
    "Tunjung | (+62-813-1882-9382)\n\n"
    "Kami mengucapkan terima kasih atas kerja sama dan kontribusi Bapak/Ibu "
    "dalam mendukung peningkatan kualitas pengendalian intern dan tata kelola "
    "di Pemerintah Kota Tegal."
)

DEFAULT_TEMPLATE_WA = (
    "Yth. Bapak/Ibu {nama},\n\n"
    "Dalam rangka pelaksanaan Penilaian Lingkungan Pengendalian Intern (CEE) Pemerintah Kota Tegal Tahun {tahun}, "
    "kami memohon kesediaan Bapak/Ibu untuk berpartisipasi dalam pengisian kuesioner survei persepsi.\n\n"
    "*Tautan Kuesioner:*\n"
    "{link}\n\n"
    "*Token Akses Responden:*\n"
    "*{token}*\n\n"
    "_Petunjuk:_ Masukkan token akses di atas saat membuka kuesioner tanpa perlu login. "
    "Token bersifat pribadi dan jawaban hanya dapat dikirim satu kali.\n\n"
    "Narahubung:\n"
    "Heri P (+62-812-8320-3050)\n"
    "Tunjung (+62-813-1882-9382)\n\n"
    "Terima kasih atas kerja sama dan kontribusi Bapak/Ibu dalam mendukung penguatan pengendalian intern di Pemerintah Kota Tegal."
)


def render_placeholders(text: str, resp, opd_nama: str = "") -> str:
    if not text:
        return ""
    url = settings.SURVEI_PUBLIC_URL
    token = str(getattr(resp, "token_id", "") or "")
    tahun = str(getattr(resp, "tahun", "") or "")
    nama = str(getattr(resp, "nama_responden", "") or "")
    nip = str(getattr(resp, "nip", "") or "-")
    jabatan = str(getattr(resp, "jabatan", "") or "-")
    mapping = {
        "{nama}": nama,
        "{nama_responden}": nama,
        "{nip}": nip,
        "{jabatan}": jabatan,
        "{opd}": opd_nama,
        "{tahun}": tahun,
        "{link}": url,
        "{url}": url,
        "{token}": token,
    }
    res = text
    for k, v in mapping.items():
        res = res.replace(k, v)
    return res


def build_invitation(resp, session=None):
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

    subject_tpl = (cfg.template_email_subject if cfg and cfg.template_email_subject else None) or DEFAULT_TEMPLATE_EMAIL_SUBJECT
    body_tpl = (cfg.template_email if cfg and cfg.template_email else None) or DEFAULT_TEMPLATE_EMAIL

    subject = render_placeholders(subject_tpl, resp, opd_nama)
    plain_text = render_placeholders(body_tpl, resp, opd_nama)

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = settings.SMTP_FROM
    message['To'] = getattr(resp, 'email', '') or ''
    message.set_content(plain_text)

    url = escape(settings.SURVEI_PUBLIC_URL, quote=True)
    token = escape(str(getattr(resp, "token_id", "") or ""))
    paragraphs_html = "".join(f"<p style='margin:0 0 16px;'>{escape(p)}</p>" for p in plain_text.split("\n\n") if p.strip())

    html_content = f"""<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="margin:0;padding:0;background-color:#eaf5f9;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eaf5f9;">
<tr><td align="center" style="padding:40px 16px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:628px;background-color:#ffffff;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
<tr><td style="padding:32px 28px 38px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#334155;">
{paragraphs_html}
<div style="text-align:center;padding:24px 0 28px;">
  <a href="{url}" style="display:inline-block;padding:12px 28px;background-color:#30394a;color:#ffffff;border-radius:5px;font-family:Arial,sans-serif;font-size:15px;font-weight:bold;text-decoration:none;letter-spacing:0.5px;">Buka Link Kuesioner</a>
</div>
<div style="background-color:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;padding:14px;text-align:center;margin-bottom:20px;">
  <div style="font-size:12px;color:#64748b;font-weight:600;margin-bottom:6px;text-transform:uppercase;letter-spacing:1px;">Token Akses Responden:</div>
  <div style="font-family:Consolas,monospace;font-size:19px;font-weight:bold;color:#0f172a;letter-spacing:1.5px;word-break:break-all;">{token}</div>
</div>
<p style="margin:0;font-size:12px;color:#94a3b8;word-break:break-all;">Jika tombol di atas tidak dapat diklik, salin tautan berikut ke browser:<br><a href="{url}" style="color:#4f46e5;">{url}</a></p>
</td></tr></table>
</td></tr></table>
</body></html>"""
    message.add_alternative(html_content, subtype='html')
    return message


def send_invitation(resp, session=None):
    message = build_invitation(resp, session=session)
    factory = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    kwargs = {'context': ssl.create_default_context()} if settings.SMTP_SSL else {}
    with factory(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20, **kwargs) as smtp:
        if settings.SMTP_STARTTLS and not settings.SMTP_SSL:
            smtp.starttls(context=ssl.create_default_context())
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)
