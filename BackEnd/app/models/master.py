"""Master / reference tables (OPD, kuesioner catalogue, CEE document items)."""
from sqlmodel import Field, SQLModel


class Opd(SQLModel, table=True):
    __tablename__ = "ta_opd"

    id_sub_pd: int = Field(primary_key=True)
    id_pd: int | None = None
    kode: str | None = None
    nama_pd: str | None = None
    nama_pd_singkat: str | None = None
    nip_kepala: str | None = None
    nama_kepala: str | None = None
    jabatan_kepala: str | None = None
    is_pd: int | None = None
    bidangurusan: str | None = None
    alamat: str | None = None
    telp: str | None = None
    email: str | None = None
    aktif: int | None = 1
    bludbos: int | None = None
    kode_risk: str | None = None


class RefBidangUrusan(SQLModel, table=True):
    """Tabel referensi bidang urusan pemerintah daerah."""
    __tablename__ = "ref_bidang_urusan"

    id: int = Field(primary_key=True)
    id_urusan: int | None = None
    id_fungsi: int | None = None
    kode_bidang_urusan: str | None = None
    nama_bidang_urusan: str | None = None
    bidang_urusan_alias: str | None = None
    kode_risk: str | None = None


class KuesionerKategori(SQLModel, table=True):
    """8 sub-unsur lingkungan pengendalian (A..H)."""
    __tablename__ = "mr_kuesioner_kategori"

    id: int | None = Field(default=None, primary_key=True)
    kode: str
    nama: str
    urutan: int = 0


class KuesionerPertanyaan(SQLModel, table=True):
    __tablename__ = "mr_kuesioner_pertanyaan"

    id: int | None = Field(default=None, primary_key=True)
    kategori_id: int = Field(foreign_key="mr_kuesioner_kategori.id", index=True)
    nomor: str
    pertanyaan: str
    urutan: int = 0
    aktif: int = 1


class CeeDokumenItem(SQLModel, table=True):
    """8 aspek penilaian CEE berbasis dokumen (Form 1.b / 1.c)."""
    __tablename__ = "tr_cee_dokumen_item"

    id: int | None = Field(default=None, primary_key=True)
    nomor: str
    aspek: str
    urutan: int = 0
