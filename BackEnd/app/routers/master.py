"""Endpoint master/referensi: OPD, katalog kuesioner CEE, item dokumen CEE."""
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import text
from sqlmodel import Session, select

from app.core.security import AdminDep
from app.db import get_session
from app.models import (
    CeeDokumenItem,
    CeeJawaban,
    KuesionerKategori,
    KuesionerPertanyaan,
    Opd,
    RefBidangUrusan,
)

router = APIRouter(prefix="/master", tags=["master"])


def _id_pd(session: Session, opd_id: int) -> int | None:
    """Peta opd_id aplikasi (ta_opd.id_sub_pd) ke id_pd yang dipakai tabel renstra."""
    return session.exec(
        select(Opd.id_pd).where(Opd.id_sub_pd == opd_id)
    ).first()


@router.get("/opd")
def list_opd(aktif_only: bool = True, session: Session = Depends(get_session)):
    stmt = select(Opd)
    if aktif_only:
        stmt = stmt.where(Opd.aktif == 1)
    stmt = stmt.order_by(Opd.nama_pd)
    opds = session.exec(stmt).all()
    parent_map = {o.id_sub_pd: o.kode_risk for o in opds if o.kode_risk}
    res = []
    for o in opds:
        d = o.model_dump()
        if not d.get("kode_risk") and d.get("id_pd") in parent_map:
            d["kode_risk"] = parent_map[d["id_pd"]]
        res.append(d)
    return res


@router.get("/opd/{opd_id}")
def get_opd(opd_id: int, session: Session = Depends(get_session)):
    opd = session.get(Opd, opd_id)
    if not opd:
        return None
    d = opd.model_dump()
    if not d.get("kode_risk") and d.get("id_pd"):
        parent_kr = session.exec(
            select(Opd.kode_risk).where(Opd.id_sub_pd == d["id_pd"])
        ).first()
        if parent_kr:
            d["kode_risk"] = parent_kr
    return d


@router.get("/bidang-urusan")
def list_bidang_urusan(session: Session = Depends(get_session)):
    """Daftar referensi bidang urusan pemerintah daerah (ref_bidang_urusan)."""
    stmt = select(RefBidangUrusan).order_by(
        RefBidangUrusan.kode_risk, RefBidangUrusan.kode_bidang_urusan
    )
    return session.exec(stmt).all()


@router.get("/opd/{opd_id}/print-context")
def opd_print_context(opd_id: int, session: Session = Depends(get_session)):
    """Data kop & tanda tangan cetak Form 2.b.

    `bidang_urusan` (text[]) hanya terisi di baris PD induk (id_sub_pd = id_pd),
    jadi diresolusi lewat join ke baris induk lalu digabung jadi satu string.
    """
    row = session.exec(
        text(
            "SELECT o.nama_pd, o.nama_kepala, o.nip_kepala, o.jabatan_kepala, "
            "       COALESCE(p.bidang_urusan, o.bidang_urusan) AS bidang_urusan "
            "FROM ta_opd o "
            "LEFT JOIN ta_opd p ON p.id_sub_pd = o.id_pd "
            "WHERE o.id_sub_pd = :opd_id"
        ).bindparams(opd_id=opd_id)
    ).first()
    if not row:
        return {}
    bu = row.bidang_urusan
    bidang = ", ".join(bu) if isinstance(bu, (list, tuple)) else (bu or "")
    return {
        "nama_pd": row.nama_pd,
        "nama_kepala": row.nama_kepala,
        "nip_kepala": row.nip_kepala,
        "jabatan_kepala": row.jabatan_kepala,
        "bidang_urusan": bidang,
    }


@router.get("/renja/subkegiatan")
def list_renja_subkegiatan(
    opd_id: int, tahun: int, session: Session = Depends(get_session)
):
    """Data checklist Form 2.c: subkegiatan (+indikator lvl-7 keluaran) dan
    indikator program (lvl-5) yang bisa dicentang sendiri. `id_sub_pd` renja =
    opd_id aplikasi (tanpa peta). Mengembalikan {subkegiatan, indikator_program}."""
    subs = session.exec(
        text(
            "SELECT idsubkegiatan, idprogram, idkegiatan, kode_sub_kegiatan, "
            "       nm_program, nm_kegiatan, nm_sub_kegiatan "
            "FROM renja_subkegiatan "
            "WHERE id_sub_pd = :opd_id AND tahun = :tahun "
            "ORDER BY kode_sub_kegiatan"
        ).bindparams(opd_id=opd_id, tahun=tahun)
    ).all()
    # nama & induk per id (untuk melabeli indikator program/kegiatan).
    prog_nama = {str(s.idprogram): s.nm_program for s in subs}
    keg_nama = {str(s.idkegiatan): s.nm_kegiatan for s in subs}
    keg_prog = {str(s.idkegiatan): str(s.idprogram) for s in subs}

    def _tgt(target, satuan):
        return " ".join(x for x in (target, satuan) if x)

    def _label(tolok, satuan, target):
        extra = _tgt(target, satuan)
        return f"{tolok} ({extra})" if extra else tolok

    # Indikator level-7 = keluaran subkegiatan (id_parent = idsubkegiatan).
    ind_sub = session.exec(
        text(
            "SELECT ri.id_parent, ri.tolok_ukur, ri.satuan, ri.target "
            "FROM renja_indikator ri "
            "JOIN renja_subkegiatan sk ON sk.idsubkegiatan = ri.id_parent "
            "WHERE sk.id_sub_pd = :opd_id AND sk.tahun = :tahun AND ri.lvl = 7 "
            "ORDER BY ri.nomor"
        ).bindparams(opd_id=opd_id, tahun=tahun)
    ).all()
    by_sub: dict[str, list[str]] = {}
    by_sub_list: dict[str, list[dict]] = {}  # terstruktur untuk cetak
    for r in ind_sub:
        if r.tolok_ukur:
            by_sub.setdefault(str(r.id_parent), []).append(
                _label(r.tolok_ukur, r.satuan, r.target)
            )
            by_sub_list.setdefault(str(r.id_parent), []).append(
                {"tolok": r.tolok_ukur, "target": _tgt(r.target, r.satuan)}
            )

    # Indikator level-5 = indikator program (id_parent = idprogram) & level-6 =
    # indikator kegiatan (id_parent = idkegiatan); tiap baris punya id sendiri
    # agar bisa dicentang terpisah.
    ind_prog = session.exec(
        text(
            "SELECT ri.id, ri.id_parent, ri.tolok_ukur, ri.satuan, ri.target "
            "FROM renja_indikator ri "
            "WHERE ri.lvl = 5 AND ri.id_parent IN ("
            "  SELECT DISTINCT idprogram FROM renja_subkegiatan "
            "  WHERE id_sub_pd = :opd_id AND tahun = :tahun) "
            "ORDER BY ri.nomor"
        ).bindparams(opd_id=opd_id, tahun=tahun)
    ).all()
    ind_keg = session.exec(
        text(
            "SELECT ri.id, ri.id_parent, ri.tolok_ukur, ri.satuan, ri.target "
            "FROM renja_indikator ri "
            "WHERE ri.lvl = 6 AND ri.id_parent IN ("
            "  SELECT DISTINCT idkegiatan FROM renja_subkegiatan "
            "  WHERE id_sub_pd = :opd_id AND tahun = :tahun) "
            "ORDER BY ri.nomor"
        ).bindparams(opd_id=opd_id, tahun=tahun)
    ).all()

    subkegiatan = [
        {
            "idsubkegiatan": str(s.idsubkegiatan),
            "idprogram": str(s.idprogram),
            "idkegiatan": str(s.idkegiatan),
            "kode_sub_kegiatan": s.kode_sub_kegiatan,
            "nm_program": s.nm_program,
            "nm_kegiatan": s.nm_kegiatan,
            "nm_sub_kegiatan": s.nm_sub_kegiatan,
            "indikator": "; ".join(by_sub.get(str(s.idsubkegiatan), [])),
            "indikator_list": by_sub_list.get(str(s.idsubkegiatan), []),
        }
        for s in subs
    ]
    indikator_program = [
        {
            "id": str(r.id),
            "idprogram": str(r.id_parent),
            "nm_program": prog_nama.get(str(r.id_parent)),
            "label": _label(r.tolok_ukur, r.satuan, r.target),
            "tolok": r.tolok_ukur,
            "target": _tgt(r.target, r.satuan),
        }
        for r in ind_prog
        if r.tolok_ukur
    ]
    indikator_kegiatan = [
        {
            "id": str(r.id),
            "idkegiatan": str(r.id_parent),
            "idprogram": keg_prog.get(str(r.id_parent)),
            "nm_program": prog_nama.get(keg_prog.get(str(r.id_parent))),
            "nm_kegiatan": keg_nama.get(str(r.id_parent)),
            "label": _label(r.tolok_ukur, r.satuan, r.target),
            "tolok": r.tolok_ukur,
            "target": _tgt(r.target, r.satuan),
        }
        for r in ind_keg
        if r.tolok_ukur
    ]
    return {
        "subkegiatan": subkegiatan,
        "indikator_program": indikator_program,
        "indikator_kegiatan": indikator_kegiatan,
    }


@router.get("/kuesioner")
def list_kuesioner(session: Session = Depends(get_session)):
    """Kategori (sub-unsur) beserta daftar pertanyaannya."""
    kats = session.exec(
        select(KuesionerKategori).order_by(KuesionerKategori.urutan)
    ).all()
    pers = session.exec(
        select(KuesionerPertanyaan)
        .where(KuesionerPertanyaan.aktif == 1)
        .order_by(KuesionerPertanyaan.urutan)
    ).all()
    by_kat: dict[int, list] = {}
    for p in pers:
        by_kat.setdefault(p.kategori_id, []).append(p)
    return [
        {
            "id": k.id,
            "kode": k.kode,
            "nama": k.nama,
            "urutan": k.urutan,
            "pertanyaan": by_kat.get(k.id, []),
        }
        for k in kats
    ]


# --------- Kelola pertanyaan kuesioner (khusus Admin) -------------------------
@router.get("/kuesioner/manage")
def list_kuesioner_manage(session: Session = Depends(get_session), user: dict = AdminDep):
    """Semua kategori + seluruh pertanyaan (termasuk non-aktif) untuk kelola admin.

    Berbeda dari GET /kuesioner yang hanya mengembalikan pertanyaan aktif
    (dipublish) untuk survei & Form 1.a.
    """
    kats = session.exec(
        select(KuesionerKategori).order_by(KuesionerKategori.urutan)
    ).all()
    pers = session.exec(
        select(KuesionerPertanyaan).order_by(
            KuesionerPertanyaan.urutan, KuesionerPertanyaan.id
        )
    ).all()
    by_kat: dict[int, list] = {}
    for p in pers:
        by_kat.setdefault(p.kategori_id, []).append(p)
    return [
        {
            "id": k.id,
            "kode": k.kode,
            "nama": k.nama,
            "urutan": k.urutan,
            "pertanyaan": by_kat.get(k.id, []),
        }
        for k in kats
    ]


@router.post("/kuesioner/pertanyaan")
def create_pertanyaan(
    payload: dict = Body(...),
    session: Session = Depends(get_session),
    user: dict = AdminDep,
):
    kategori_id = payload.get("kategori_id")
    if not session.get(KuesionerKategori, kategori_id):
        raise HTTPException(404, "Kategori tidak ditemukan")
    teks = (payload.get("pertanyaan") or "").strip()
    if not teks:
        raise HTTPException(400, "Teks pertanyaan wajib diisi")
    obj = KuesionerPertanyaan(
        kategori_id=kategori_id,
        nomor=(payload.get("nomor") or "").strip(),
        pertanyaan=teks,
        urutan=int(payload.get("urutan") or 0),
        aktif=1 if payload.get("aktif", True) else 0,
    )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/kuesioner/pertanyaan/{pid}")
def update_pertanyaan(
    pid: int,
    payload: dict = Body(...),
    session: Session = Depends(get_session),
    user: dict = AdminDep,
):
    obj = session.get(KuesionerPertanyaan, pid)
    if not obj:
        raise HTTPException(404, "Pertanyaan tidak ditemukan")
    if "kategori_id" in payload and payload["kategori_id"]:
        if not session.get(KuesionerKategori, payload["kategori_id"]):
            raise HTTPException(404, "Kategori tidak ditemukan")
        obj.kategori_id = payload["kategori_id"]
    if "nomor" in payload:
        obj.nomor = (payload.get("nomor") or "").strip()
    if "pertanyaan" in payload:
        teks = (payload.get("pertanyaan") or "").strip()
        if not teks:
            raise HTTPException(400, "Teks pertanyaan wajib diisi")
        obj.pertanyaan = teks
    if "urutan" in payload:
        obj.urutan = int(payload.get("urutan") or 0)
    if "aktif" in payload:
        obj.aktif = 1 if payload["aktif"] else 0
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/kuesioner/pertanyaan/{pid}")
def delete_pertanyaan(
    pid: int, session: Session = Depends(get_session), user: dict = AdminDep
):
    obj = session.get(KuesionerPertanyaan, pid)
    if not obj:
        raise HTTPException(404, "Pertanyaan tidak ditemukan")
    dipakai = session.exec(
        select(CeeJawaban).where(CeeJawaban.pertanyaan_id == pid)
    ).first()
    if dipakai:
        raise HTTPException(
            400,
            "Pertanyaan sudah memiliki jawaban responden — nonaktifkan (unpublish) "
            "saja, jangan dihapus.",
        )
    session.delete(obj)
    session.commit()
    return {"ok": True}


@router.get("/dokumen-item")
def list_dokumen_item(session: Session = Depends(get_session)):
    return session.exec(
        select(CeeDokumenItem).order_by(CeeDokumenItem.urutan)
    ).all()


# --------------------- Renstra OPD (sumber pilihan Form 2.b) -------------------
# Opsi dikembalikan sbg {value,label}; value = teks uraian yang disimpan apa
# adanya di kolom konteks (agar laporan tetap terbaca), label = versi bernomor.
@router.get("/renstra/tujuan")
def list_renstra_tujuan(
    opd_id: int, tahun: int, session: Session = Depends(get_session)
):
    id_pd = _id_pd(session, opd_id)
    if id_pd is None:
        return []
    rows = session.exec(
        text(
            "SELECT nomor, uraitujuan FROM renstra_tujuan "
            "WHERE id_pd = :pd "
            "ORDER BY nomor"
        ).bindparams(pd=id_pd)
    ).all()
    return [
        {"value": r.uraitujuan, "label": f"{r.nomor}. {r.uraitujuan}"}
        for r in rows
        if r.uraitujuan
    ]


@router.get("/renstra/sasaran")
def list_renstra_sasaran(
    opd_id: int, tahun: int, session: Session = Depends(get_session)
):
    """Menyertakan `tujuan_strategis` (uraian tujuan induk) untuk cascading."""
    id_pd = _id_pd(session, opd_id)
    if id_pd is None:
        return []
    rows = session.exec(
        text(
            "SELECT s.nomor, s.uraisasaran, t.uraitujuan "
            "FROM renstra_sasaran s "
            "JOIN renstra_tujuan t ON t.idtujuan = s.idtujuan "
            "WHERE s.id_pd = :pd "
            "ORDER BY t.nomor, s.nomor"
        ).bindparams(pd=id_pd)
    ).all()
    return [
        {
            "value": r.uraisasaran,
            "label": f"{r.nomor}. {r.uraisasaran}",
            "tujuan_strategis": r.uraitujuan,
        }
        for r in rows
        if r.uraisasaran
    ]


@router.get("/renstra/iku")
def list_renstra_iku(opd_id: int, session: Session = Depends(get_session)):
    """Indikator Kinerja Utama (iku=1) renstra OPD untuk field IKU Renstra."""
    id_pd = _id_pd(session, opd_id)
    if id_pd is None:
        return []
    rows = session.exec(
        text(
            "SELECT indikator FROM renstra_indikator_tujuan_sasaran "
            "WHERE id_pd = :pd AND iku = '1' "
            "ORDER BY urut"
        ).bindparams(pd=id_pd)
    ).all()
    return [
        {"value": r.indikator, "label": r.indikator}
        for r in rows
        if r.indikator
    ]


@router.get("/renstra/tahap")
def list_renstra_tahap(session: Session = Depends(get_session)):
    """Periode renstra (mis. '2025 - 2029') untuk field Periode Dinilai."""
    rows = session.exec(
        text(
            "SELECT nama_renstra, periode FROM renstra_tahap "
            "ORDER BY tahun1"
        )
    ).all()
    return [
        {
            "value": r.periode,
            "label": f"{r.nama_renstra} {r.periode}".strip()
            if r.nama_renstra
            else r.periode,
        }
        for r in rows
        if r.periode
    ]


@router.get("/renstra/program")
def list_renstra_program(opd_id: int, session: Session = Depends(get_session)):
    id_pd = _id_pd(session, opd_id)
    if id_pd is None:
        return []
    rows = session.exec(
        text(
            "SELECT no, kodeprogram, uraiprogram FROM renstra_program "
            "WHERE id_pd = :pd ORDER BY no"
        ).bindparams(pd=id_pd)
    ).all()
    return [
        {"value": r.uraiprogram, "label": f"{r.kodeprogram} — {r.uraiprogram}"}
        for r in rows
        if r.uraiprogram
    ]


# ------------------ RPJMD & referensi (sumber pilihan Form 2.a) ---------------
# Sama seperti renstra: opsi {value,label}, value = teks yang disimpan di kolom
# konteks. Field multi-pilihan Form 2.a menyimpan value terpilih sebagai baris
# yang dipisah newline.
@router.get("/rpjmd/periode")
def list_rpjmd_periode(session: Session = Depends(get_session)):
    """Periode RPJMD (mis. 'RPJMD 2025 - 2029').

    Tidak ada tabel master periode, jadi diturunkan dari `idperiode` rpjmd_tujuan
    yang berformat YYYYYYYY (20252029).
    """
    rows = session.exec(
        text(
            "SELECT DISTINCT idperiode FROM rpjmd_tujuan "
            "WHERE idperiode IS NOT NULL ORDER BY idperiode"
        )
    ).all()
    out = []
    for r in rows:
        s = str(r.idperiode)
        label = f"RPJMD {s[:4]} - {s[4:]}" if len(s) == 8 else f"RPJMD {s}"
        out.append({"value": label, "label": label})
    return out


@router.get("/rpjmd/visi")
def list_rpjmd_visi(session: Session = Depends(get_session)):
    rows = session.exec(
        text("SELECT visi FROM rpjmd_visi ORDER BY idperiode")
    ).all()
    return [{"value": r.visi, "label": r.visi} for r in rows if r.visi]


@router.get("/rpjmd/misi")
def list_rpjmd_misi(session: Session = Depends(get_session)):
    rows = session.exec(
        text("SELECT no, misi FROM rpjmd_misi ORDER BY no")
    ).all()
    return [
        {"value": r.misi, "label": f"{r.no}. {r.misi}" if r.no else r.misi}
        for r in rows
        if r.misi
    ]


@router.get("/rpjmd/tujuan")
def list_rpjmd_tujuan(session: Session = Depends(get_session)):
    rows = session.exec(
        text("SELECT no, uraitujuan FROM rpjmd_tujuan ORDER BY no")
    ).all()
    return [
        {
            "value": r.uraitujuan,
            "label": f"{r.no}. {r.uraitujuan}" if r.no else r.uraitujuan,
        }
        for r in rows
        if r.uraitujuan
    ]


@router.get("/rpjmd/sasaran")
def list_rpjmd_sasaran(session: Session = Depends(get_session)):
    """Label menyertakan tujuan induk agar sasaran sejenis mudah dibedakan."""
    rows = session.exec(
        text(
            "SELECT s.no, s.uraisasaran, t.uraitujuan "
            "FROM rpjmd_sasaran s "
            "LEFT JOIN rpjmd_tujuan t ON t.idtujuan = s.idtujuan "
            "ORDER BY t.no, s.no"
        )
    ).all()
    return [
        {
            "value": r.uraisasaran,
            "label": f"{r.no}. {r.uraisasaran}" if r.no else r.uraisasaran,
            "induk": r.uraitujuan,
            "induk_jenis": "Tujuan",
        }
        for r in rows
        if r.uraisasaran
    ]


@router.get("/rpjmd/iku")
def list_rpjmd_iku(tahun: int | None = None, session: Session = Depends(get_session)):
    """IKU Pemda = indikator renja tingkat daerah (lvl < 3) ber-flag iku=1.

    Induk indikator ikut dikembalikan (`induk`, `induk_jenis`) agar Form 2.a &
    3.a bisa menampilkan/menurunkan tujuan/sasaran RPJMD-nya:
      lvl 1 -> id_parent = rpjmd_tujuan.idtujuan
      lvl 2 -> id_parent = rpjmd_sasaran.idsasaran

    Difilter per tahun bila diminta; bila tahun tsb belum punya data renja,
    kembali ke seluruh tahun (didedup per tolok ukur) agar pilihan tidak kosong.
    """
    sql = (
        "SELECT ri.lvl, ri.tolok_ukur, ri.satuan, ri.target, "
        "       COALESCE(t.uraitujuan, s.uraisasaran) AS induk "
        "FROM renja_indikator ri "
        "LEFT JOIN rpjmd_tujuan  t ON ri.lvl = 1 AND t.idtujuan  = ri.id_parent "
        "LEFT JOIN rpjmd_sasaran s ON ri.lvl = 2 AND s.idsasaran = ri.id_parent "
        "WHERE ri.lvl < 3 AND ri.iku = 1"
    )

    def _query(with_tahun: bool):
        if with_tahun:
            return session.exec(
                text(sql + " AND ri.tahun = :tahun ORDER BY ri.lvl, ri.nomor")
                .bindparams(tahun=tahun)
            ).all()
        return session.exec(text(sql + " ORDER BY ri.lvl, ri.nomor")).all()

    rows = _query(tahun is not None)
    if tahun is not None and not rows:
        rows = _query(False)
    out, seen = [], set()
    for r in rows:
        if not r.tolok_ukur or r.tolok_ukur in seen:
            continue
        seen.add(r.tolok_ukur)
        extra = " ".join(x for x in (r.target, r.satuan) if x)
        out.append(
            {
                "value": r.tolok_ukur,
                "label": f"{r.tolok_ukur} ({extra})" if extra else r.tolok_ukur,
                "induk": r.induk,
                "induk_jenis": "Tujuan" if r.lvl == 1 else "Sasaran",
            }
        )
    return out


@router.get("/rpjmd/program")
def list_rpjmd_program(session: Session = Depends(get_session)):
    rows = session.exec(
        text(
            "SELECT DISTINCT kode_program, nama_program FROM rpjmd_program "
            "WHERE nama_program IS NOT NULL ORDER BY kode_program"
        )
    ).all()
    return [
        {"value": r.nama_program, "label": f"{r.kode_program} — {r.nama_program}"}
        for r in rows
    ]


@router.get("/ref/prioritas")
def list_ref_prioritas(session: Session = Depends(get_session)):
    """Prioritas pembangunan daerah (Form 2.a)."""
    rows = session.exec(
        text("SELECT id, prioritas FROM ref_prioritas ORDER BY id")
    ).all()
    return [
        {"value": r.prioritas, "label": f"{r.id}. {r.prioritas}"}
        for r in rows
        if r.prioritas
    ]
