"""Isian RTP; bukti baru disimpan bersama RTP dalam satu transaksi."""
from datetime import date
from typing import Annotated, Literal
from urllib.parse import urlsplit
from pydantic import Field, StringConstraints, model_validator
from app.schemas.tata_kelola import Input

Text = Annotated[str, StringConstraints(strip_whitespace=True, max_length=10000)]
RESPON_LABEL = {
    "kurangi_kemungkinan": "Mengurangi kemungkinan terjadinya Risiko",
    "kurangi_dampak": "Mengurangi dampak Risiko",
    "bagi": "Membagi Risiko",
    "hindari": "Menghindari Risiko",
    "terima": "Menerima Risiko",
}
STATUS_LABEL = {"sudah_ada": "Sudah ada kegiatan pengendalian", "tidak_ada": "Tidak ada Kegiatan Pengendalian"}
MAX_BUKTI = 5 * 1024 * 1024

class BuktiUpload(Input):
    nama: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    base64: Annotated[str, Field(max_length=((MAX_BUKTI + 2) // 3) * 4)]

class RtpInput(Input):
    risiko_id: Annotated[int, Field(strict=True, gt=0)]
    status_pengendalian: Literal["sudah_ada", "tidak_ada"]
    respon_risiko: Literal["kurangi_kemungkinan", "kurangi_dampak", "bagi", "hindari", "terima"]
    pengendalian_ada: Text | None = None
    bukti_judul: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None = None
    bukti_link: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] | None = None
    bukti_berkas_id: Annotated[int, Field(strict=True, gt=0)] | None = None
    bukti_upload: BuktiUpload | None = None
    celah_pengendalian: Text | None = None
    rencana_tindak: Text | None = None
    target_mulai: date | None = None
    target_selesai: date | None = None
    target_waktu: date | None = None  # Kompatibilitas klien tanggal tunggal.
    keterangan: Text | None = None

    @model_validator(mode="after")
    def evidence(self):
        if bool(self.target_mulai) != bool(self.target_selesai):
            raise ValueError("Isi Dari tanggal dan Sampai tanggal secara lengkap")
        if self.target_mulai and self.target_selesai < self.target_mulai:
            raise ValueError("Sampai tanggal tidak boleh sebelum Dari tanggal")
        if self.target_mulai and self.target_waktu:
            raise ValueError("Gunakan rentang tanggal atau target tanggal tunggal, bukan keduanya")
        if self.status_pengendalian == "sudah_ada":
            if not self.pengendalian_ada or not self.bukti_judul:
                raise ValueError("Uraian pengendalian dan judul berkas wajib diisi")
            if sum(bool(x) for x in [self.bukti_link, self.bukti_berkas_id, self.bukti_upload]) != 1:
                raise ValueError("Pilih satu bukti: unggah berkas atau link")
            if self.bukti_link:
                try:
                    url = urlsplit(self.bukti_link)
                    valid = url.scheme in {"http", "https"} and url.hostname and not url.username and not url.password
                except ValueError:
                    valid = False
                if not valid:
                    raise ValueError("Link harus berupa URL http/https yang valid")
        elif any([self.pengendalian_ada, self.bukti_judul, self.bukti_link, self.bukti_berkas_id, self.bukti_upload]):
            raise ValueError("Bukti hanya diisi untuk kegiatan pengendalian yang sudah ada")
        return self
