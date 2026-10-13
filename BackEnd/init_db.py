"""Inisialisasi database db_manajemen_risiko.

- Membuat seluruh tabel (SQLModel metadata).
- Seed master kuesioner CEE (kategori, pertanyaan) & item dokumen.
- Menyalin master OPD (ta_opd) dari database sumber bila tabel masih kosong.

Jalankan: python init_db.py
"""
import psycopg
from sqlmodel import Session, select

from app.core.config import settings
from app.db import engine, init_db
from app.models import CeeDokumenItem, KuesionerKategori, KuesionerPertanyaan, Opd
from app.seed_data import DOKUMEN_ITEM, KATEGORI, PERTANYAAN

# Database sumber yang sudah berisi master OPD (server yang sama dengan target).
SOURCE_OPD_DB = "manajemen_risiko"


def seed_kuesioner(session: Session) -> None:
    if session.exec(select(KuesionerKategori)).first():
        print("  - kategori/pertanyaan sudah ada, lewati seed kuesioner")
        return

    kode_to_id: dict[str, int] = {}
    for urut, (kode, nama) in enumerate(KATEGORI, start=1):
        kat = KuesionerKategori(kode=kode, nama=nama, urutan=urut)
        session.add(kat)
        session.flush()
        kode_to_id[kode] = kat.id

    for urut, (kode_kat, nomor, teks) in enumerate(PERTANYAAN, start=1):
        session.add(
            KuesionerPertanyaan(
                kategori_id=kode_to_id[kode_kat],
                nomor=nomor,
                pertanyaan=teks,
                urutan=urut,
                aktif=1,
            )
        )
    session.commit()
    print(f"  - seed {len(KATEGORI)} kategori, {len(PERTANYAAN)} pertanyaan")


def seed_dokumen_item(session: Session) -> None:
    if session.exec(select(CeeDokumenItem)).first():
        print("  - dokumen item sudah ada, lewati")
        return
    for urut, (nomor, aspek) in enumerate(DOKUMEN_ITEM, start=1):
        session.add(CeeDokumenItem(nomor=nomor, aspek=aspek, urutan=urut))
    session.commit()
    print(f"  - seed {len(DOKUMEN_ITEM)} item dokumen CEE")


def copy_opd(session: Session) -> None:
    if session.exec(select(Opd)).first():
        print("  - ta_opd sudah berisi data, lewati copy")
        return
    try:
        src = psycopg.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=SOURCE_OPD_DB,
            connect_timeout=10,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  ! gagal koneksi DB sumber '{SOURCE_OPD_DB}' untuk copy OPD: {exc}")
        return

    cols = [
        "id_sub_pd", "id_pd", "kode", "nama_pd", "nama_pd_singkat", "nip_kepala",
        "nama_kepala", "jabatan_kepala", "is_pd", "bidangurusan", "alamat", "telp",
        "email", "aktif", "bludbos",
    ]
    with src:
        cur = src.cursor()
        cur.execute(f"select {', '.join(cols)} from ta_opd")
        rows = cur.fetchall()
    src.close()

    for row in rows:
        session.add(Opd(**dict(zip(cols, row))))
    session.commit()
    print(f"  - copy {len(rows)} OPD dari '{SOURCE_OPD_DB}'")


def main() -> None:
    print(f"Target DB: {settings.POSTGRES_DB} @ {settings.POSTGRES_SERVER}")
    print("Membuat tabel ...")
    init_db()
    print("Seeding ...")
    with Session(engine) as session:
        seed_kuesioner(session)
        seed_dokumen_item(session)
        copy_opd(session)
    print("Selesai.")


if __name__ == "__main__":
    main()
