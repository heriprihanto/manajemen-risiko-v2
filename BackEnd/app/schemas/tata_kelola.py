from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Teks = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=10000)]
Skala = Annotated[int, Field(strict=True, ge=1, le=5)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PenugasanInput(Input):
    opd_id: int
    username: Teks
    nama: Teks
    peran: str
    mulai: date
    selesai: date
    dasar: Teks

    @model_validator(mode="after")
    def dates(self):
        if self.selesai < self.mulai:
            raise ValueError("Tanggal selesai harus setelah tanggal mulai")
        return self


class KebijakanInput(Input):
    opd_id: int
    tahun: Annotated[int, Field(ge=2026, le=2100)]
    nama: Teks
    dasar: Teks
    berlaku: date
    # Lima deskripsi operasional untuk masing-masing skala, disepakati lewat FGD.
    dampak: list[Teks] = Field(min_length=5, max_length=5)
    kemungkinan: list[Teks] = Field(min_length=5, max_length=5)
    area_dampak: list[Teks] = Field(min_length=1, max_length=30)
    kategori_prioritas: list[Teks] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def scope(self):
        if self.berlaku.year != self.tahun:
            raise ValueError("Tanggal berlaku harus pada tahun kebijakan")
        return self


class KeputusanInput(Input):
    keputusan: Literal["disetujui", "ditolak"]
    catatan: Teks


class PenilaianInput(Input):
    tahap: Literal["awal", "target", "residual"]
    dampak: Skala
    kemungkinan: Skala
    alasan: Teks
    bukti: Teks | None = None


class ResponsInput(Input):
    penilaian_id: int
    opsi: list[Literal["kurangi_kemungkinan", "kurangi_dampak", "bagi", "hindari", "terima"]] = Field(min_length=1, max_length=5)
    alasan: Teks


class TindakanInput(Input):
    uraian: Teks
    pic: Teks
    target: date


class PelaksanaanInput(Input):
    status: Literal["berjalan", "selesai"]
    hasil: Teks
    bukti: Teks | None = None


class VerifikasiInput(Input):
    efektif: bool
    catatan: Teks


class ReviuInput(Input):
    jenis: Literal["kepatuhan", "inspektorat"]
    temuan: Teks
    rekomendasi: Teks
    target: date


class TindakLanjutInput(Input):
    tindak_lanjut: Teks
    bukti: Teks


class LaporanInput(Input):
    opd_id: int
    tahun: Annotated[int, Field(ge=2026, le=2100)]
    periode: Literal["TW1", "TW2", "TW3", "TW4", "TAHUNAN"]
    jenis: Literal["penilaian", "upr", "kepatuhan", "pembinaan"]
    ringkasan: Teks
    cakupan: Literal["opd", "pemda"] = "opd"
    opd_ids: list[int] = Field(default_factory=list, max_length=300)


class UsulanInput(Input):
    opd_id: int
    tahun: int
    nama: Teks
    kategori: Teks
    deskripsi: Teks


class FraudInput(Input):
    skenario: Teks
    proses_rawan: Teks
    kelemahan: Teks
    indikator: Teks


class UrutanInput(Input):
    area_dampak: Teks
    urutan_pimpinan: Annotated[int, Field(ge=1, le=9999)]
    alasan: Teks
