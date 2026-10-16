"""Form 1.a (kuesioner persepsi), 1.b (reviu dokumen), 1.c (simpulan), Form 6 (RTP CEE)."""
from datetime import date, datetime
import re
import secrets
import smtplib
from app.core.config import settings
from app.models import Opd
from app.services.cee_invitation import send_invitation
from app.services import whatsapp
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select
from fastapi.responses import Response
from app.services import cee_excel

from app.core.datetime_utils import now_wib, to_wib_iso
from app.core.security import AdminDep, UserDep, guard_record
from app.db import get_session
from app.models import (
    CeeDokumenItem,
    CeeDokumenKelemahan,
    CeeDokumenNilai,
    CeeJawaban,
    CeeResponden,
    CeeSimpulan,
    KuesionerKategori,
    KuesionerPertanyaan,
    RtpCee,
)
from app.routers.crud_helper import make_opd_tahun_router
from app.services import cee as svc

router = APIRouter(prefix="/cee", tags=["cee"])


# ----------------------------- Form 1.a: Responden ----------------------------
@router.get("/responden")
def list_responden(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    return session.exec(
        select(CeeResponden)
        .where(CeeResponden.opd_id == opd_id, CeeResponden.tahun == tahun)
        .order_by(CeeResponden.id)
    ).all()


def _next_kode(session: Session, opd_id: int, tahun: int) -> str:
    existing = session.exec(
        select(CeeResponden.kode_responden).where(
            CeeResponden.opd_id == opd_id, CeeResponden.tahun == tahun
        )
    ).all()
    nums = []
    for k in existing:
        if k and k.upper().startswith("R") and k[1:].isdigit():
            nums.append(int(k[1:]))
    return f"R{(max(nums) + 1) if nums else 1}"


def _identity(payload):
    fields = ("nip", "nama_responden", "jabatan", "email", "no_hp")
    data = {key: str(payload.get(key) or "").strip() for key in fields}
    if not all(data.values()):
        raise HTTPException(400, "NIP, nama, jabatan, email, dan no HP wajib diisi")
    data["email"] = data["email"].lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", data["email"]):
        raise HTTPException(400, "Alamat email tidak valid")
    if not re.fullmatch(r"[0-9 +().-]{6,25}", data["no_hp"]):
        raise HTTPException(400, "Nomor HP tidak valid")
    kategori = str(payload.get("kategori_jabatan") or "").strip()
    if kategori and kategori not in cee_excel.KATEGORI_JABATAN:
        raise HTTPException(400, "Kategori jabatan tidak valid")
    data["kategori_jabatan"] = kategori or None
    return data


def _duplicate(session, data, tahun, rid=None):
    existing = session.exec(select(CeeResponden).where(CeeResponden.tahun == tahun)).all()
    if any(r.id != rid and ((r.email or "").lower() == data["email"] or r.nip == data["nip"]) for r in existing):
        raise HTTPException(409, "NIP atau email sudah terdaftar pada tahun ini")


@router.post("/responden")
def create_responden(payload: dict[str, Any] = Body(...), session: Session = Depends(get_session), user: dict = AdminDep):
    data = _identity(payload)
    try:
        opd_id, tahun = int(payload["opd_id"]), int(payload["tahun"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(400, "OPD dan tahun wajib diisi") from None
    if not session.get(Opd, opd_id):
        raise HTTPException(404, "OPD tidak ditemukan")
    _duplicate(session, data, tahun)
    obj = CeeResponden(opd_id=opd_id, tahun=tahun, kode_responden=_next_kode(session, opd_id, tahun),
                       token_id=secrets.token_urlsafe(24), **data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/responden/template")
def responden_template(user: dict = AdminDep):
    return Response(cee_excel.template(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="template-calon-responden.xlsx"'})


@router.post("/responden/import")
def import_responden(opd_id: int, tahun: int,
                     content: bytes = Body(..., media_type="application/octet-stream"),
                     session: Session = Depends(get_session), user: dict = AdminDep):
    if not session.get(Opd, opd_id):
        raise HTTPException(404, "OPD tidak ditemukan")
    if not 2000 <= tahun <= 2100:
        raise HTTPException(400, "Tahun tidak valid")
    rows = cee_excel.read_rows(content)
    existing = session.exec(select(CeeResponden).where(CeeResponden.tahun == tahun)).all()
    emails = {(r.email or '').strip().lower() for r in existing if r.email}
    nips = {r.nip for r in existing if r.nip}
    next_code = int(_next_kode(session, opd_id, tahun)[1:])
    imported, errors = 0, []
    for number, payload, error in rows:
        try:
            if error:
                raise HTTPException(400, error)
            data = _identity(payload)
            if data['email'] in emails or data['nip'] in nips:
                raise HTTPException(409, "NIP atau email sudah terdaftar pada tahun ini atau duplikat dalam file")
        except HTTPException as exc:
            errors.append({"baris": number, "alasan": exc.detail})
            continue
        session.add(CeeResponden(opd_id=opd_id, tahun=tahun, kode_responden=f"R{next_code}",
                                 token_id=secrets.token_urlsafe(24), **data))
        emails.add(data['email'])
        nips.add(data['nip'])
        next_code += 1
        imported += 1
    session.commit()
    return {"berhasil": imported, "gagal": errors, "total": len(rows)}


@router.put("/responden/{rid}")
def update_responden(rid: int, payload: dict[str, Any] = Body(...),
                     session: Session = Depends(get_session), user: dict = AdminDep):
    obj = guard_record(user, session.exec(
        select(CeeResponden).where(CeeResponden.id == rid)
        .with_for_update().execution_options(populate_existing=True)
    ).first(), "Responden")
    if obj.submitted_at or obj.sumber == "survei":
        raise HTTPException(409, "Identitas responden yang sudah mengisi tidak dapat diubah")
    data = _identity({**obj.model_dump(), **payload})
    _duplicate(session, data, obj.tahun, rid)
    if obj.email != data["email"]:
        obj.token_id = secrets.token_urlsafe(24)
        obj.invited_at = None
        obj.whatsapp_invited_at = None
    if obj.no_hp != data["no_hp"]:
        obj.whatsapp_invited_at = None
    for key, value in data.items():
        setattr(obj, key, value)
    if not obj.token_id:
        obj.token_id = secrets.token_urlsafe(24)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.post("/responden/undang")
def invite_responden(
    opd_id: int,
    tahun: int,
    session: Session = Depends(get_session),
    user: dict = AdminDep,
    channel: str = "email",
):
    rows = session.exec(select(CeeResponden).where(CeeResponden.opd_id == opd_id, CeeResponden.tahun == tahun)).all()
    sent, failed, skipped = 0, [], 0
    is_wa = channel.lower() == "whatsapp"
    for resp in rows:
        if resp.submitted_at or resp.sumber == "survei":
            skipped += 1
            continue
        try:
            _identity(resp.model_dump())
        except HTTPException:
            failed.append({"id": resp.id, "nama": resp.nama_responden, "alasan": "Lengkapi identitas responden"})
            continue
        if not resp.token_id:
            resp.token_id = secrets.token_urlsafe(24)
            session.add(resp)
            session.commit()
            session.refresh(resp)
        if is_wa:
            try:
                if not (resp.no_hp or "").strip():
                    raise ValueError("Nomor WhatsApp/HP belum diisi")
                whatsapp.send_whatsapp_invitation(resp, session=session)
                resp.whatsapp_invited_at = now_wib()
                sent += 1
            except Exception as exc:
                failed.append({"id": resp.id, "nama": resp.nama_responden, "alasan": str(exc)})
        else:
            try:
                if not settings.SMTP_HOST or not settings.SMTP_FROM:
                    raise ValueError("SMTP belum dikonfigurasi")
                send_invitation(resp, session=session)
                resp.invited_at = now_wib()
                sent += 1
            except (smtplib.SMTPException, OSError, ValueError):
                failed.append({"id": resp.id, "nama": resp.nama_responden, "alasan": "Pengiriman email gagal; periksa SMTP dan alamat email"})
        session.add(resp)
        session.commit()
    return {"terkirim": sent, "gagal": failed, "dilewati": skipped, "channel": channel}


@router.post("/responden/{rid}/undang")
def invite_single_responden(
    rid: int,
    session: Session = Depends(get_session),
    user: dict = AdminDep,
    channel: str = "email",
):
    resp = guard_record(user, session.exec(
        select(CeeResponden).where(CeeResponden.id == rid)
        .with_for_update().execution_options(populate_existing=True)
    ).first(), "Responden")
    if resp.submitted_at or resp.sumber == "survei":
        raise HTTPException(409, "Responden sudah mengisi survei")
    _identity(resp.model_dump())
    if not resp.token_id:
        resp.token_id = secrets.token_urlsafe(24)
        session.add(resp)
        session.commit()
        session.refresh(resp)
    is_wa = channel.lower() == "whatsapp"
    if is_wa:
        if not (resp.no_hp or "").strip():
            raise HTTPException(400, "Nomor WhatsApp/HP belum diisi")
        try:
            whatsapp.send_whatsapp_invitation(resp, session=session)
            resp.whatsapp_invited_at = now_wib()
        except Exception as exc:
            raise HTTPException(502, f"Gagal mengirim WhatsApp: {exc}")
    else:
        if not settings.SMTP_HOST or not settings.SMTP_FROM:
            raise HTTPException(500, "SMTP belum dikonfigurasi")
        try:
            send_invitation(resp, session=session)
            resp.invited_at = now_wib()
        except (smtplib.SMTPException, OSError, ValueError) as exc:
            raise HTTPException(502, f"Gagal mengirim email: {exc}")
    session.add(resp)
    session.commit()
    session.refresh(resp)
    return {"ok": True, "channel": channel}


@router.delete("/responden/{rid}")
def delete_responden(
    rid: int, session: Session = Depends(get_session), user: dict = AdminDep
):
    obj = guard_record(user, session.exec(
        select(CeeResponden).where(CeeResponden.id == rid)
        .with_for_update().execution_options(populate_existing=True)
    ).first(), "Responden")
    if obj.submitted_at or obj.sumber == "survei":
        raise HTTPException(409, "Responden yang sudah mengisi survei tidak dapat dihapus")
    for j in session.exec(select(CeeJawaban).where(CeeJawaban.responden_id == rid)).all():
        session.delete(j)
    session.delete(obj)
    session.commit()
    return {"ok": True}


# ----------------------------- Form 1.a: Jawaban ------------------------------
@router.post("/jawaban")
def save_jawaban(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Simpan/replace satu sel jawaban (responden x pertanyaan)."""
    rid = payload["responden_id"]
    guard_record(user, session.get(CeeResponden, rid), "Responden")
    pid = payload["pertanyaan_id"]
    nilai = payload.get("nilai")
    existing = session.exec(
        select(CeeJawaban).where(
            CeeJawaban.responden_id == rid, CeeJawaban.pertanyaan_id == pid
        )
    ).first()
    if nilai in (None, ""):
        if existing:
            session.delete(existing)
            session.commit()
        return {"ok": True, "deleted": True}
    if existing:
        existing.nilai = int(nilai)
        session.add(existing)
    else:
        session.add(CeeJawaban(responden_id=rid, pertanyaan_id=pid, nilai=int(nilai)))
    session.commit()
    return {"ok": True}


# ----------------------- Form 1.a: Matriks + simpulan -------------------------
@router.get("/form1a")
def form_1a(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Rekap kuesioner: responden (kolom R1..Rn), jawaban, modus & simpulan per
    pertanyaan dan per sub-unsur (persepsi)."""
    responden = session.exec(
        select(CeeResponden)
        .where(CeeResponden.opd_id == opd_id, CeeResponden.tahun == tahun)
        .order_by(CeeResponden.id)
    ).all()
    rid_list = [r.id for r in responden]

    jawaban_map: dict[tuple[int, int], int] = {}
    if rid_list:
        for j in session.exec(
            select(CeeJawaban).where(CeeJawaban.responden_id.in_(rid_list))
        ).all():
            jawaban_map[(j.pertanyaan_id, j.responden_id)] = j.nilai

    kats = session.exec(
        select(KuesionerKategori).order_by(KuesionerKategori.urutan)
    ).all()
    pers = session.exec(
        select(KuesionerPertanyaan)
        .where(KuesionerPertanyaan.aktif == 1)
        .order_by(KuesionerPertanyaan.urutan)
    ).all()
    per_by_kat: dict[int, list[KuesionerPertanyaan]] = {}
    for p in pers:
        per_by_kat.setdefault(p.kategori_id, []).append(p)

    kategori_out = []
    for k in kats:
        pert_out = []
        predikat_list = []
        for p in per_by_kat.get(k.id, []):
            nilai_per_responden = {
                r.id: jawaban_map.get((p.id, r.id)) for r in responden
            }
            md = svc.modus(list(nilai_per_responden.values()))
            pred = svc.predikat_dari_nilai(md)
            predikat_list.append(pred)
            pert_out.append(
                {
                    "id": p.id,
                    "nomor": p.nomor,
                    "pertanyaan": p.pertanyaan,
                    "jawaban": nilai_per_responden,
                    "modus": md,
                    "simpulan": pred,
                }
            )
        kategori_out.append(
            {
                "id": k.id,
                "kode": k.kode,
                "nama": k.nama,
                "simpulan": svc.simpulan_subunsur(predikat_list),
                "pertanyaan": pert_out,
            }
        )

    return {
        "opd_id": opd_id,
        "tahun": tahun,
        "responden": responden,
        "kategori": kategori_out,
    }


# ------------------- Rincian hasil survei (per responden) ---------------------
@router.get("/survei-hasil")
def survei_hasil(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Rincian hasil survei: tiap responden beserta identitas & jawaban per
    pertanyaan (untuk menu admin 'Rincian Hasil Survei')."""
    responden = session.exec(
        select(CeeResponden)
        .where(CeeResponden.opd_id == opd_id, CeeResponden.tahun == tahun)
        .order_by(CeeResponden.id)
    ).all()
    rid_list = [r.id for r in responden]

    jawaban_by_resp: dict[int, dict[int, int]] = {}
    if rid_list:
        for j in session.exec(
            select(CeeJawaban).where(CeeJawaban.responden_id.in_(rid_list))
        ).all():
            jawaban_by_resp.setdefault(j.responden_id, {})[j.pertanyaan_id] = j.nilai

    kats = session.exec(
        select(KuesionerKategori).order_by(KuesionerKategori.urutan)
    ).all()
    pers = session.exec(
        select(KuesionerPertanyaan)
        .where(KuesionerPertanyaan.aktif == 1)
        .order_by(KuesionerPertanyaan.urutan)
    ).all()
    per_by_kat: dict[int, list[KuesionerPertanyaan]] = {}
    for p in pers:
        per_by_kat.setdefault(p.kategori_id, []).append(p)
    kategori_out = [
        {
            "id": k.id,
            "kode": k.kode,
            "nama": k.nama,
            "pertanyaan": [
                {"id": p.id, "nomor": p.nomor, "pertanyaan": p.pertanyaan}
                for p in per_by_kat.get(k.id, [])
            ],
        }
        for k in kats
    ]

    resp_out = []
    for r in responden:
        jw = jawaban_by_resp.get(r.id, {})
        if not jw:
            continue
        nilai_list = [v for v in jw.values() if v is not None]
        rata = round(sum(nilai_list) / len(nilai_list), 2) if nilai_list else None
        resp_out.append(
            {
                "id": r.id,
                "kode_responden": r.kode_responden,
                "nama_responden": r.nama_responden,
                "jabatan": r.jabatan,
                "email": r.email,
                "sumber": r.sumber,
                "submitted_at": to_wib_iso(r.submitted_at or r.updated_at),
                "jawaban": {str(pid): nilai for pid, nilai in jw.items()},
                "jumlah_jawaban": len(nilai_list),
                "rata_rata": rata,
                "narasi": r.narasi,
            }
        )

    return {
        "opd_id": opd_id,
        "tahun": tahun,
        "total_pertanyaan": len(pers),
        "kategori": kategori_out,
        "responden": resp_out,
    }


@router.delete("/survei-hasil/{rid}")
def delete_survei_hasil(
    rid: int, session: Session = Depends(get_session), user: dict = AdminDep
):
    """Hapus satu hasil survei (responden + jawaban). Khusus Admin."""
    obj = session.get(CeeResponden, rid)
    if obj is None:
        raise HTTPException(404, "Responden tidak ditemukan")
    for j in session.exec(select(CeeJawaban).where(CeeJawaban.responden_id == rid)).all():
        session.delete(j)
    session.delete(obj)
    session.commit()
    return {"ok": True}


# --------------------------- Form 1.b: Reviu dokumen --------------------------
@router.get("/form1b")
def form_1b(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    items = session.exec(select(CeeDokumenItem).order_by(CeeDokumenItem.urutan)).all()
    nilai = {
        n.item_id: n
        for n in session.exec(
            select(CeeDokumenNilai).where(
                CeeDokumenNilai.opd_id == opd_id, CeeDokumenNilai.tahun == tahun
            )
        ).all()
    }
    # Uraian kelemahan (boleh >1 per aspek), dikelompokkan per item.
    kelemahan: dict[int, list[CeeDokumenKelemahan]] = {}
    for k in session.exec(
        select(CeeDokumenKelemahan)
        .where(
            CeeDokumenKelemahan.opd_id == opd_id,
            CeeDokumenKelemahan.tahun == tahun,
        )
        .order_by(CeeDokumenKelemahan.urutan, CeeDokumenKelemahan.id)
    ).all():
        kelemahan.setdefault(k.item_id, []).append(k)

    out = []
    for it in items:
        n = nilai.get(it.id)
        ks = kelemahan.get(it.id, [])
        # keterangan gabungan (baris per uraian) untuk Form 1.c & Laporan.
        gabungan = "\n".join(k.uraian for k in ks) or (n.keterangan if n else None)
        out.append(
            {
                "item_id": it.id,
                "nomor": it.nomor,
                "aspek": it.aspek,
                "nilai": n.nilai if n else None,
                "sumber_data": n.sumber_data if n else None,
                "keterangan": gabungan,
                "kelemahan": [
                    {"id": k.id, "uraian": k.uraian, "urutan": k.urutan} for k in ks
                ],
                "simpulan": svc.predikat_dokumen(n.nilai if n else None),
            }
        )
    return out


@router.post("/form1b")
def save_1b(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session)
):
    opd_id, tahun, item_id = payload["opd_id"], payload["tahun"], payload["item_id"]
    obj = session.exec(
        select(CeeDokumenNilai).where(
            CeeDokumenNilai.opd_id == opd_id,
            CeeDokumenNilai.tahun == tahun,
            CeeDokumenNilai.item_id == item_id,
        )
    ).first()
    if not obj:
        obj = CeeDokumenNilai(opd_id=opd_id, tahun=tahun, item_id=item_id)
    obj.nilai = payload.get("nilai")
    if "sumber_data" in payload:
        obj.sumber_data = payload.get("sumber_data")
    if "keterangan" in payload:  # uraian kelemahan kini di tabel terpisah
        obj.keterangan = payload.get("keterangan")
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    return {"ok": True}


# --------- Form 1.b: Uraian kelemahan (boleh lebih dari satu per aspek) -------
@router.post("/form1b/kelemahan")
def add_kelemahan(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session)
):
    obj = CeeDokumenKelemahan(
        opd_id=payload["opd_id"],
        tahun=payload["tahun"],
        item_id=payload["item_id"],
        uraian=(payload.get("uraian") or "").strip(),
        urutan=payload.get("urutan") or 0,
    )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/form1b/kelemahan/{kid}")
def update_kelemahan(
    kid: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(CeeDokumenKelemahan, kid), "Uraian kelemahan")
    if "uraian" in payload:
        obj.uraian = (payload.get("uraian") or "").strip()
    if "urutan" in payload:
        obj.urutan = payload["urutan"]
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/form1b/kelemahan/{kid}")
def delete_kelemahan(
    kid: int, session: Session = Depends(get_session), user: dict = UserDep
):
    obj = guard_record(user, session.get(CeeDokumenKelemahan, kid), "Uraian kelemahan")
    session.delete(obj)
    session.commit()
    return {"ok": True}


# ------------------------------ Form 1.c: Simpulan ----------------------------
@router.get("/form1c")
def form_1c(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Gabungan simpulan persepsi (1.a) + reviu dokumen (1.b) per sub-unsur."""
    f1a = form_1a(opd_id, tahun, session)
    f1b = {row["aspek"]: row for row in form_1b(opd_id, tahun, session)}

    # Override simpulan/penjelasan manual per sub-unsur.
    simpulans = {
        s.kategori_id: s
        for s in session.exec(
            select(CeeSimpulan).where(
                CeeSimpulan.opd_id == opd_id, CeeSimpulan.tahun == tahun
            )
        ).all()
    }

    out = []
    for idx, kat in enumerate(f1a["kategori"], start=1):
        persepsi = kat["simpulan"]
        dok = f1b.get(kat["nama"])
        dokumen = dok["simpulan"] if dok else None
        simpulan_auto = svc.simpulan_gabungan(persepsi, dokumen)
        stored = simpulans.get(kat["id"])
        manual_simpulan = stored.predikat if stored else None

        kelemahan_list = (dok or {}).get("kelemahan", [])
        if kelemahan_list:
            if len(kelemahan_list) == 1:
                penjelasan_auto = kelemahan_list[0]["uraian"]
            else:
                penjelasan_auto = "\n".join(
                    f"{i + 1}. {k['uraian']}" for i, k in enumerate(kelemahan_list)
                )
        else:
            penjelasan_auto = (dok or {}).get("keterangan") or ""

        penjelasan_manual = stored is not None and stored.penjelasan is not None
        penjelasan = stored.penjelasan if penjelasan_manual else penjelasan_auto

        out.append(
            {
                "no": idx,
                "kategori_id": kat["id"],
                "sub_unsur": kat["nama"],
                "hasil_persepsi": persepsi,
                "hasil_dokumen": dokumen,
                "uraian_dokumen": (dok or {}).get("keterangan"),
                "kelemahan": kelemahan_list,
                "simpulan_auto": simpulan_auto,
                "simpulan_manual": manual_simpulan is not None,
                "simpulan": manual_simpulan if manual_simpulan is not None else simpulan_auto,
                "penjelasan": penjelasan,
                "penjelasan_auto": penjelasan_auto,
                "penjelasan_manual": penjelasan_manual,
            }
        )
    return out


@router.post("/form1c/simpulan")
def save_simpulan(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session)
):
    """Simpan/override simpulan atau penjelasan Form 1.c per sub-unsur."""
    opd_id, tahun = payload["opd_id"], payload["tahun"]
    kategori_id = payload["kategori_id"]

    obj = session.exec(
        select(CeeSimpulan).where(
            CeeSimpulan.opd_id == opd_id,
            CeeSimpulan.tahun == tahun,
            CeeSimpulan.kategori_id == kategori_id,
        )
    ).first()

    if payload.get("reset_penjelasan"):
        if obj:
            obj.penjelasan = None
    elif "penjelasan" in payload:
        penjelasan_val = payload.get("penjelasan")
        if penjelasan_val is not None:
            penjelasan_val = str(penjelasan_val).strip()
        if not obj:
            obj = CeeSimpulan(opd_id=opd_id, tahun=tahun, kategori_id=kategori_id)
        obj.penjelasan = penjelasan_val

    if "simpulan" in payload:
        simpulan_val = (payload.get("simpulan") or "").strip() or None
        if not obj and simpulan_val is not None:
            obj = CeeSimpulan(opd_id=opd_id, tahun=tahun, kategori_id=kategori_id)
        if obj:
            obj.predikat = simpulan_val

    if obj:
        if obj.predikat is None and obj.penjelasan is None:
            session.delete(obj)
            session.commit()
            return {"ok": True, "simpulan_manual": False, "penjelasan_manual": False}
        else:
            obj.updated_at = now_wib()
            session.add(obj)
            session.commit()
            return {
                "ok": True,
                "simpulan_manual": obj.predikat is not None,
                "penjelasan_manual": obj.penjelasan is not None,
            }

    return {"ok": True, "simpulan_manual": False, "penjelasan_manual": False}


@router.get("/form1c/aspek")
def form1c_aspek(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Opsi Aspek/Sub-unsur CEE (Form 6) dari Form 1.c: sub-unsur yang Kurang
    Memadai atau memiliki uraian permasalahan. Kurang Memadai tampil lebih dulu."""
    seen: dict[str, bool] = {}
    for r in form_1c(opd_id, tahun, session):
        km = r["simpulan"] == svc.KURANG
        if r["kelemahan"] or r.get("penjelasan") or km:
            seen[r["sub_unsur"]] = seen.get(r["sub_unsur"], False) or km
    out = [{"label": k, "value": k, "kurang_memadai": v} for k, v in seen.items()]
    out.sort(key=lambda o: not o["kurang_memadai"])
    return out


@router.get("/form1c/permasalahan")
def form1c_permasalahan(
    opd_id: int, tahun: int, session: Session = Depends(get_session)
):
    """Opsi 'uraian permasalahan' dari Form 1.c untuk mengisi Kondisi Kurang
    Memadai di Form 6. Tiap opsi membawa aspek_cee (untuk cascading)."""
    out = []
    for r in form_1c(opd_id, tahun, session):
        if r["kelemahan"]:
            for k in r["kelemahan"]:
                out.append(
                    {
                        "label": k["uraian"],
                        "value": k["uraian"],
                        "aspek_cee": r["sub_unsur"],
                        "kurang_memadai": r["simpulan"] == svc.KURANG,
                    }
                )
        elif r.get("penjelasan"):
            out.append(
                {
                    "label": r["penjelasan"],
                    "value": r["penjelasan"],
                    "aspek_cee": r["sub_unsur"],
                    "kurang_memadai": r["simpulan"] == svc.KURANG,
                }
            )
    out.sort(key=lambda o: not o["kurang_memadai"])
    return out


# ------------------------------- Form 6: RTP CEE ------------------------------
def _sync_rtp_cee_dates(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)

    def parse_d(v):
        if not v:
            return None
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(str(v)[:10])
        except (ValueError, TypeError):
            return None

    m = parse_d(data.get("target_mulai"))
    s = parse_d(data.get("target_selesai"))

    # Fallback dari target_waktu jika pengguna mengisi teks rentang
    tw = data.get("target_waktu")
    if not m and not s and tw and isinstance(tw, str):
        if " s.d. " in tw:
            p = tw.split(" s.d. ")
            m = parse_d(p[0])
            s = parse_d(p[1])
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", tw.strip()):
            m = parse_d(tw.strip())
            s = m

    data["target_mulai"] = m
    data["target_selesai"] = s
    if m and s:
        data["target_waktu"] = f"{m.isoformat()} s.d. {s.isoformat()}"
    elif m:
        data["target_waktu"] = m.isoformat()
    elif s:
        data["target_waktu"] = s.isoformat()
    elif "target_waktu" in data and not data["target_waktu"]:
        data["target_waktu"] = None

    return data


@router.get("/rtp-cee")
def list_rtp_cee(
    opd_id: int, tahun: int, session: Session = Depends(get_session)
):
    stmt = (
        select(RtpCee)
        .where(RtpCee.opd_id == opd_id, RtpCee.tahun == tahun)
        .order_by(RtpCee.no_urut, RtpCee.id)
    )
    return session.exec(stmt).all()


@router.post("/rtp-cee")
def create_rtp_cee(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    clean = _sync_rtp_cee_dates(payload)
    obj = RtpCee()
    fields = RtpCee.model_fields
    for key, value in clean.items():
        if key in fields and key not in ("id", "created_at"):
            setattr(obj, key, value)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/rtp-cee/{item_id}")
def update_rtp_cee(
    item_id: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(RtpCee, item_id))
    clean = _sync_rtp_cee_dates(payload)
    fields = RtpCee.model_fields
    for key, value in clean.items():
        if key in fields and key not in ("id", "created_at"):
            setattr(obj, key, value)
    obj.updated_at = now_wib()
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/rtp-cee/{item_id}")
def delete_rtp_cee(
    item_id: int,
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = guard_record(user, session.get(RtpCee, item_id))
    session.delete(obj)
    session.commit()
    return {"ok": True}

