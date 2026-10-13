"""Captcha sederhana, mandiri (tanpa layanan eksternal).

Kode acak dirender sebagai SVG terdistorsi. Jawaban disimpan sementara di
memori server (sekali-pakai, kedaluwarsa 5 menit) — cocok untuk deployment
uvicorn satu worker. Bila kelak dijalankan multi-worker, ganti _STORE dengan
penyimpanan bersama (mis. Redis).
"""
from __future__ import annotations

import random
import secrets
import time

# Hindari karakter ambigu (0/O, 1/I/L).
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_LENGTH = 5
_TTL = 300  # detik
_MAX_ENTRIES = 5000

# id -> (jawaban_upper, expires_at)
_STORE: dict[str, tuple[str, float]] = {}


def _cleanup(now: float) -> None:
    expired = [k for k, (_, exp) in _STORE.items() if exp < now]
    for k in expired:
        _STORE.pop(k, None)
    # Jaga-jaga agar tidak tumbuh tak terbatas.
    if len(_STORE) > _MAX_ENTRIES:
        for k in list(_STORE)[: len(_STORE) - _MAX_ENTRIES]:
            _STORE.pop(k, None)


def _svg(code: str) -> str:
    w, h = 150, 52
    colors = ["#1e293b", "#1d4ed8", "#b91c1c", "#047857", "#7c3aed", "#b45309"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="captcha">',
        f'<rect width="{w}" height="{h}" fill="#f1f5f9" rx="8"/>',
    ]
    # Garis-garis noise.
    for _ in range(5):
        x1, y1, x2, y2 = (
            random.randint(0, w), random.randint(0, h),
            random.randint(0, w), random.randint(0, h),
        )
        c = random.choice(colors)
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{c}" stroke-width="1" opacity="0.35"/>'
        )
    # Titik-titik noise.
    for _ in range(18):
        parts.append(
            f'<circle cx="{random.randint(0, w)}" cy="{random.randint(0, h)}" '
            f'r="1.2" fill="{random.choice(colors)}" opacity="0.4"/>'
        )
    # Karakter.
    step = (w - 20) / len(code)
    for i, ch in enumerate(code):
        x = 14 + i * step + random.uniform(-3, 3)
        y = h / 2 + random.uniform(-3, 5)
        rot = random.uniform(-24, 24)
        size = random.randint(26, 32)
        c = random.choice(colors)
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="Georgia,serif" '
            f'font-size="{size}" font-weight="700" fill="{c}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({rot:.1f} {x:.1f} {y:.1f})">{ch}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def generate() -> dict[str, str]:
    """Buat captcha baru. Kembalikan {id, svg}."""
    now = time.time()
    _cleanup(now)
    code = "".join(random.choice(_ALPHABET) for _ in range(_LENGTH))
    cid = secrets.token_urlsafe(16)
    _STORE[cid] = (code.upper(), now + _TTL)
    return {"id": cid, "svg": _svg(code)}


def verify(cid: str | None, answer: str | None) -> bool:
    """Verifikasi & konsumsi captcha (sekali pakai)."""
    if not cid or not answer:
        return False
    item = _STORE.pop(cid, None)  # sekali pakai
    if not item:
        return False
    expected, exp = item
    if exp < time.time():
        return False
    return answer.strip().upper() == expected
