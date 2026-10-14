"""Analisis risiko (Form 4), matriks risiko, dan penentuan prioritas (Form 5).

Skala risiko mengikuti Matriks Analisis Risiko 5x5: 1..25.
Level risiko:
    Sangat Tinggi (5) : skala 20 s.d 25 (Merah)
    Tinggi (4)        : skala 16 s.d 19 (Oranye)
    Sedang (3)        : skala 11 s.d 15 (Kuning)
    Rendah (2)        : skala 6 s.d 10  (Hijau Muda)
    Sangat Rendah (1) : skala 1 s.d 5   (Hijau Tua)

Ambang selera risiko ditetapkan per OPD/tahun dan Pemilik Risiko.
Penilaian baru mengikuti kebijakan berversi di services/tata_kelola.py.
"""

DAMPAK_LABEL = {
    1: "Tidak signifikan",
    2: "Minor",
    3: "Moderat",
    4: "Signifikan",
    5: "Sangat Signifikan",
}

KEMUNGKINAN_LABEL = {
    1: "Hampir tidak terjadi",
    2: "Jarang terjadi",
    3: "Kadang terjadi",
    4: "Sering terjadi",
    5: "Hampir pasti terjadi",
}

# Pemetaan Matriks Analisis Risiko 5x5: (kemungkinan, dampak) -> nilai level risiko (1..25)
MATRIKS_SKALA: dict[tuple[int, int], int] = {
    (5, 1): 11, (5, 2): 15, (5, 3): 18, (5, 4): 23, (5, 5): 25,
    (4, 1): 6,  (4, 2): 12, (4, 3): 16, (4, 4): 19, (4, 5): 24,
    (3, 1): 4,  (3, 2): 8,  (3, 3): 14, (3, 4): 17, (3, 5): 22,
    (2, 1): 2,  (2, 2): 7,  (2, 3): 10, (2, 4): 13, (2, 5): 21,
    (1, 1): 1,  (1, 2): 3,  (1, 3): 5,  (1, 4): 9,  (1, 5): 20,
}

LEVEL_SANGAT_RENDAH = "Sangat Rendah (1)"
LEVEL_RENDAH = "Rendah (2)"
LEVEL_SEDANG = "Sedang (3)"
LEVEL_TINGGI = "Tinggi (4)"
LEVEL_SANGAT_TINGGI = "Sangat Tinggi (5)"



def hitung_skala(dampak: int | None, kemungkinan: int | None) -> float | None:
    if dampak is None or kemungkinan is None:
        return None
    val = MATRIKS_SKALA.get((kemungkinan, dampak))
    return float(val) if val is not None else None


def level_risiko(skala: float | None) -> str | None:
    if skala is None:
        return None
    if skala >= 20:
        return LEVEL_SANGAT_TINGGI
    if skala >= 16:
        return LEVEL_TINGGI
    if skala >= 11:
        return LEVEL_SEDANG
    if skala >= 6:
        return LEVEL_RENDAH
    return LEVEL_SANGAT_RENDAH


def warna_level(level: str | None) -> str:
    return {
        LEVEL_SANGAT_RENDAH: "#15803d",
        "Sangat Rendah": "#15803d",
        LEVEL_RENDAH: "#22c55e",
        "Rendah": "#22c55e",
        LEVEL_SEDANG: "#eab308",
        "Sedang": "#eab308",
        LEVEL_TINGGI: "#f97316",
        "Tinggi": "#f97316",
        LEVEL_SANGAT_TINGGI: "#ef4444",
        "Sangat Tinggi": "#ef4444",
    }.get(level, "#9ca3af")


def keterangan_penanganan(level: str | None) -> str:
    # Warna/level saja tidak menentukan keputusan penerimaan.
    return "Penanganan mengikuti selera, toleransi, dan keputusan UPR" if level else ""
