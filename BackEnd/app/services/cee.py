"""Perhitungan CEE: modus jawaban responden, simpulan per pertanyaan / sub-unsur,
dan simpulan gabungan persepsi + dokumen (Form 1.a, 1.b, 1.c).

Aturan (lihat keterangan sheet KUESIONER / Form 1.a):
- Simpulan tiap pertanyaan: "Memadai" bila modus jawaban responden adalah 3 atau 4,
  "Kurang Memadai" bila modus adalah 1 atau 2.
- Simpulan sub-unsur (persepsi): "Memadai" bila SELURUH pertanyaan pada sub-unsur
  "Memadai"; "Kurang Memadai" bila ada satu saja yang "Kurang Memadai".
- Form 1.c menggabungkan hasil persepsi (Form 1.a) dengan hasil reviu dokumen (Form 1.b).
  Simpulan akhir "Kurang Memadai" bila salah satu dari persepsi/dokumen Kurang Memadai.
"""
from collections import Counter

MEMADAI = "Memadai"
KURANG = "Kurang Memadai"


def modus(values: list[int]) -> int | None:
    """Modus (nilai yang paling sering muncul). Bila seri, ambil nilai tertinggi."""
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    counts = Counter(vals)
    top = max(counts.values())
    candidates = [v for v, c in counts.items() if c == top]
    return max(candidates)


def predikat_dari_nilai(nilai: int | None) -> str | None:
    if nilai is None:
        return None
    return MEMADAI if nilai >= 3 else KURANG


def simpulan_subunsur(predikat_pertanyaan: list[str]) -> str | None:
    """Memadai hanya bila semua pertanyaan Memadai."""
    valid = [p for p in predikat_pertanyaan if p]
    if not valid:
        return None
    return MEMADAI if all(p == MEMADAI for p in valid) else KURANG


def predikat_dokumen(nilai: int | None) -> str | None:
    """Form 1.b: nilai 1 = Memadai, 0 = Kurang Memadai."""
    if nilai is None:
        return None
    return MEMADAI if nilai >= 1 else KURANG


def simpulan_gabungan(persepsi: str | None, dokumen: str | None) -> str | None:
    """Form 1.c kolom g: Kurang Memadai bila salah satu Kurang Memadai."""
    parts = [p for p in (persepsi, dokumen) if p]
    if not parts:
        return None
    return MEMADAI if all(p == MEMADAI for p in parts) else KURANG
