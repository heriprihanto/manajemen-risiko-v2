"""Form 3a/3b/3c (identifikasi risiko), Form 4 (analisis), Form 5 (prioritas),
Matriks Risiko, Form 7 (RTP risiko)."""
import base64
import binascii
from urllib.parse import quote
from datetime import datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import Response
from app.models.risiko import RtpBukti
from app.schemas.rtp import RtpInput, MAX_BUKTI
from sqlmodel import Session, func, select

from app.core.security import UserDep, ensure_opd_access, guard_record
from app.db import get_session
from app.models import AnalisisRisiko, Opd, RefBidangUrusan, Risiko, RtpRisiko, MonitoringRiskEvent, Infokom, MonitoringPi
from app.models.kamus import KamusRisiko
from app.models.risiko import (
    JENIS_OPERASIONAL_OPD,
    JENIS_RISIKO,
    JENIS_STRATEGIS_OPD,
    JENIS_STRATEGIS_PEMDA,
)
from app.services import analisis as an
from app.services import selera
from app.services import tata_kelola as governance
from app.models.tata_kelola import PenilaianRiwayat, TindakanRisiko, ReviuRisiko, ResponsRisiko, UrutanPrioritas, FraudRisiko

router = APIRouter(prefix="/risiko", tags=["risiko"])

JENIS_LABEL = {
    "strategis_pemda": "Risiko Strategis Pemda (Form 3.a)",
    "strategis_opd": "Risiko Strategis OPD (Form 3.b)",
    "operasional_opd": "Risiko Operasional OPD (Form 3.c)",
}


def _analisis_dict(a: AnalisisRisiko | None) -> dict[str, Any]:
    if not a:
        return {
            "skala_dampak": None,
            "skala_kemungkinan": None,
            "skala_risiko": None,
            "level": None,
            "is_prioritas": False,
        }
    return {
        "skala_dampak": a.skala_dampak,
        "skala_kemungkinan": a.skala_kemungkinan,
        "skala_risiko": a.skala_risiko,
        "level": an.level_risiko(a.skala_risiko),
        "is_prioritas": a.is_prioritas,
    }


# ----------------------- Form 3a/3b/3c: Identifikasi --------------------------
@router.get("")
def list_risiko(
    opd_id: int,
    tahun: int,
    jenis: str | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(Risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    if jenis:
        stmt = stmt.where(Risiko.jenis_risiko == jenis)
    stmt = stmt.order_by(Risiko.jenis_risiko, Risiko.urutan, Risiko.id)
    risiko = session.exec(stmt).all()

    ids = [r.id for r in risiko]
    amap: dict[int, AnalisisRisiko] = {}
    if ids:
        amap = {
            a.risiko_id: a
            for a in session.exec(
                select(AnalisisRisiko).where(AnalisisRisiko.risiko_id.in_(ids))
            ).all()
        }

    bu_ids = [r.id_bidang_urusan for r in risiko if r.id_bidang_urusan]
    bu_map: dict[int, RefBidangUrusan] = {}
    if bu_ids:
        bu_map = {
            b.id: b
            for b in session.exec(
                select(RefBidangUrusan).where(RefBidangUrusan.id.in_(bu_ids))
            ).all()
        }

    aktif = selera.daftar_aktif(session, opd_id, tahun)
    out = []
    for r in risiko:
        d = r.model_dump()
        d["analisis"] = _analisis_dict(amap.get(r.id))
        setting = selera.resolve(aktif, r.pemilik_risiko)
        d["selera_risiko"] = selera.as_dict(setting)
        d["analisis"]["is_prioritas"] = selera.status(d["analisis"]["skala_risiko"], setting)
        bu = bu_map.get(r.id_bidang_urusan) if r.id_bidang_urusan else None
        d["bidang_urusan"] = (
            {
                "id": bu.id,
                "kode_bidang_urusan": bu.kode_bidang_urusan,
                "nama_bidang_urusan": bu.nama_bidang_urusan,
                "bidang_urusan_alias": bu.bidang_urusan_alias,
                "kode_risk": bu.kode_risk,
            }
            if bu
            else None
        )
        out.append(d)
    return out


def generate_kode_risiko(
    jenis_risiko: str,
    tahun: int,
    id_bidang_urusan: int | None,
    opd_id: int,
    session: Session,
) -> str:
    jenis_map = {
        JENIS_STRATEGIS_PEMDA: ("RSP", "01"),
        JENIS_STRATEGIS_OPD: ("RSO", "02"),
        JENIS_OPERASIONAL_OPD: ("ROO", "03"),
    }
    j_prefix, j_code = jenis_map.get(jenis_risiko, ("RSK", "00"))
    th2 = f"{tahun % 100:02d}"

    bu_code = "00"
    if id_bidang_urusan:
        bu = session.get(RefBidangUrusan, id_bidang_urusan)
        if bu and bu.kode_risk:
            bu_code = str(bu.kode_risk).strip().zfill(2)

    if jenis_risiko == JENIS_STRATEGIS_PEMDA:
        opd_code = "01"
    else:
        opd_code = "00"
        opd = session.exec(select(Opd).where(Opd.id_sub_pd == opd_id)).first()
        if opd and opd.kode_risk:
            opd_code = str(opd.kode_risk).strip().zfill(2)

    prefix = f"{j_prefix}.{th2}.{j_code}.{bu_code}.{opd_code}."

    existing = session.exec(
        select(Risiko.kode_risiko).where(
            Risiko.opd_id == opd_id,
            Risiko.tahun == tahun,
            Risiko.kode_risiko.like(f"{prefix}%"),
        )
    ).all()
    max_seq = 0
    for k in existing:
        if k and k.startswith(prefix):
            try:
                seq = int(k[len(prefix) :])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
    return f"{prefix}{max_seq + 1:03d}"


@router.post("")
def create_risiko(
    payload: dict[str, Any] = Body(...), session: Session = Depends(get_session), user: dict = UserDep
):
    governance.boleh_tulis(session, user, payload.get("opd_id"))
    if payload.get("jenis_risiko") not in JENIS_RISIKO:
        raise HTTPException(400, f"jenis_risiko harus salah satu dari {JENIS_RISIKO}")

    uraian = (payload.get("uraian_risiko") or "").strip()
    if not uraian:
        raise HTTPException(400, "Uraian risiko wajib diisi dan dipilih dari Kamus Risiko.")

    kamus_item = session.exec(
        select(KamusRisiko).where(
            KamusRisiko.aktif == 1,
            func.lower(func.trim(KamusRisiko.nama_risiko)) == func.lower(uraian)
        )
    ).first()
    if not kamus_item:
        raise HTTPException(
            400, "Uraian risiko harus dipilih dari Kamus Risiko, tidak bisa mengetik sendiri."
        )

    obj = Risiko()
    fields = Risiko.model_fields
    for k, v in payload.items():
        if k in fields and k not in ("id", "created_at"):
            setattr(obj, k, v)
    obj.uraian_risiko = kamus_item.nama_risiko
    obj.kategori_risiko = kamus_item.kategori_risiko

    if not obj.kode_risiko or not str(obj.kode_risiko).strip():
        obj.kode_risiko = generate_kode_risiko(
            obj.jenis_risiko,
            obj.tahun,
            obj.id_bidang_urusan,
            obj.opd_id,
            session,
        )
    session.add(obj)
    session.flush()
    governance.audit(session, user, obj, "dibuat", obj.opd_id, obj.tahun, obj.id)
    session.commit()
    session.refresh(obj)
    return obj


@router.put("/{rid}")
def update_risiko(
    rid: int,
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    obj = governance.risiko_akses(session, user, rid, tulis=True)
    if payload.get("tahun", obj.tahun) != obj.tahun:
        raise HTTPException(409, "Tahun risiko tidak dapat dipindahkan; buat penilaian pada tahun baru")
    old_owner = selera.pemilik_key(obj.pemilik_risiko)
    fields = Risiko.model_fields

    if "uraian_risiko" in payload:
        uraian = (payload.get("uraian_risiko") or "").strip()
        if not uraian:
            raise HTTPException(400, "Uraian risiko wajib diisi dan dipilih dari Kamus Risiko.")
        kamus_item = session.exec(
            select(KamusRisiko).where(
                KamusRisiko.aktif == 1,
                func.lower(func.trim(KamusRisiko.nama_risiko)) == func.lower(uraian)
            )
        ).first()
        if not kamus_item:
            raise HTTPException(
                400, "Uraian risiko harus dipilih dari Kamus Risiko, tidak bisa mengetik sendiri."
            )
        payload["uraian_risiko"] = kamus_item.nama_risiko
        payload["kategori_risiko"] = kamus_item.kategori_risiko
    elif "kategori_risiko" in payload:
        payload.pop("kategori_risiko")

    for k, v in payload.items():
        if k in fields and k not in ("id", "created_at", "opd_id"):
            setattr(obj, k, v)
    obj.updated_at = now_wib()
    analysis = session.exec(select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == rid)).first()
    if analysis and old_owner != selera.pemilik_key(obj.pemilik_risiko):
        setting = selera.effective(session, obj.opd_id, obj.tahun, obj.pemilik_risiko)
        if not setting and analysis.skala_risiko is not None:
            raise HTTPException(409, "Tetapkan Selera Risiko pemilik tujuan sebelum mengubah Pemilik Risiko")
        analysis.is_prioritas = bool(selera.status(analysis.skala_risiko, setting))
        session.add(analysis)
    session.add(obj)
    governance.audit(session, user, obj, "diperbarui", obj.opd_id, obj.tahun, obj.id)
    session.commit()
    session.refresh(obj)
    return obj


@router.delete("/{rid}")
def delete_risiko(
    rid: int, session: Session = Depends(get_session), user: dict = UserDep
):
    obj = guard_record(user, session.get(Risiko, rid), "Risiko")
    governance.boleh_tulis(session, user, obj.opd_id)
    for model in (RtpBukti, PenilaianRiwayat, TindakanRisiko, ReviuRisiko, ResponsRisiko, UrutanPrioritas, FraudRisiko, MonitoringRiskEvent):
        if session.exec(select(model.id).where(model.risiko_id == rid)).first():
            raise HTTPException(409, "Risiko memiliki riwayat tata kelola; data harus dipertahankan")
    for a in session.exec(
        select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == rid)
    ).all():
        session.delete(a)
    for rt in session.exec(select(RtpRisiko).where(RtpRisiko.risiko_id == rid)).all():
        session.delete(rt)
    governance.audit(session, user, obj, "dihapus", obj.opd_id, obj.tahun, obj.id)
    session.delete(obj)
    session.commit()
    return {"ok": True}


# ----------------------------- Form 4: Analisis ------------------------------
@router.post("/analisis")
def save_analisis(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    risiko_id = payload.get("risiko_id")
    if type(risiko_id) is not int or risiko_id <= 0:
        raise HTTPException(422, "risiko_id harus bilangan bulat positif")
    risiko = governance.risiko_akses(session, user, risiko_id, tulis=True)
    dampak = payload.get("skala_dampak")
    kemungkinan = payload.get("skala_kemungkinan")
    evaluated = governance.nilai(session, risiko, dampak, kemungkinan)
    skala = evaluated["skor"]
    requested = payload.get("is_prioritas", evaluated["prioritas"])
    if type(requested) is not bool:
        raise HTTPException(422, "Prioritas harus berupa boolean")
    alasan = str(payload.get("alasan") or "Penilaian awal melalui Form Analisis").strip()
    if requested != evaluated["prioritas"]:
        raise HTTPException(422, "Prioritas dihitung dari Selera Risiko; ubah ambang melalui menu Selera Risiko")

    obj = session.exec(
        select(AnalisisRisiko).where(AnalisisRisiko.risiko_id == risiko_id)
    ).first()
    if not obj:
        obj = AnalisisRisiko(risiko_id=risiko_id)
    obj.skala_dampak = dampak
    obj.skala_kemungkinan = kemungkinan
    obj.skala_risiko = skala
    obj.is_prioritas = evaluated["prioritas"]
    obj.updated_at = now_wib()
    session.add(obj)
    history = PenilaianRiwayat(risiko_id=risiko_id, tahap="awal", dampak=dampak,
        kemungkinan=kemungkinan, **evaluated, alasan=alasan, pembuat=governance.identitas(user))
    session.add(history)
    governance.audit(session, user, history, "dinilai", risiko.opd_id, risiko.tahun, risiko_id)
    session.commit()
    session.refresh(obj)
    return _analisis_dict(obj)


@router.get("/form4")
def form_4(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Hasil analisis risiko, dikelompokkan per jenis."""
    rows = list_risiko(opd_id, tahun, None, session)
    grouped: dict[str, list] = {j: [] for j in JENIS_RISIKO}
    for r in rows:
        grouped.setdefault(r["jenis_risiko"], []).append(r)
    return [
        {"jenis": j, "label": JENIS_LABEL[j], "items": grouped.get(j, [])}
        for j in JENIS_RISIKO
    ]


# ------------------------------ Matriks Risiko -------------------------------
@router.get("/matriks")
def matriks(opd_id: int, tahun: int, session: Session = Depends(get_session), pemilik: str | None = None):
    """Sebaran risiko dalam matriks 5x5 (Kemungkinan vs Dampak)."""
    rows = list_risiko(opd_id, tahun, None, session)
    owners = sorted({r.get("pemilik_risiko") or "" for r in rows})
    aktif = selera.daftar_aktif(session, opd_id, tahun)
    visual = selera.visual(aktif, pemilik, semua=pemilik is None, pemilik_terdaftar=owners)
    if pemilik is not None:
        rows = [r for r in rows if selera.pemilik_key(r.get("pemilik_risiko")) == selera.pemilik_key(pemilik)]
    cells: dict[str, list] = {}
    for r in rows:
        a = r["analisis"]
        d, k = a["skala_dampak"], a["skala_kemungkinan"]
        if d and k:
            cells.setdefault(f"{k}-{d}", []).append(
                {"kode": r.get("kode_risiko"), "uraian": r.get("uraian_risiko")}
            )
    return {
        "kebijakan": governance.snapshot_kebijakan(session, opd_id, tahun)[1],
        "selera": visual, "pemilik": owners,
        "dampak_label": an.DAMPAK_LABEL,
        "kemungkinan_label": an.KEMUNGKINAN_LABEL,
        "matriks_skala": {
            f"{k}-{d}": an.MATRIKS_SKALA.get((k, d))
            for k in range(1, 6)
            for d in range(1, 6)
        },
        "cells": cells,
    }


# ------------------------------ Form 5: Prioritas ----------------------------
@router.get("/form5")
def form_5(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Daftar risiko prioritas (is_prioritas=True), diurutkan skala menurun."""
    rows = list_risiko(opd_id, tahun, None, session)
    prioritas = [r for r in rows if r["analisis"]["is_prioritas"]]
    governance.urutkan_prioritas(session, prioritas, opd_id, tahun)
    grouped: dict[str, list] = {j: [] for j in JENIS_RISIKO}
    for r in prioritas:
        grouped.setdefault(r["jenis_risiko"], []).append(r)
    return [
        {"jenis": j, "label": JENIS_LABEL[j], "items": grouped.get(j, [])}
        for j in JENIS_RISIKO
    ]


# ------------------------------ Form 7: RTP Risiko ---------------------------
@router.get("/rtp")
def list_rtp(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Risiko prioritas + RTP-nya (Form 7)."""
    rows = list_risiko(opd_id, tahun, None, session)
    saved_rtp_records = session.exec(
        select(RtpRisiko).join(Risiko, RtpRisiko.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    rtp_map = {rt.risiko_id: rt for rt in saved_rtp_records}
    prioritas = [r for r in rows if r["analisis"]["is_prioritas"] or r["id"] in rtp_map]
    # Jika ada id prioritas yang belum ada di rtp_map, fetch
    missing_ids = [r["id"] for r in prioritas if r["id"] not in rtp_map]
    if missing_ids:
        for rt in session.exec(select(RtpRisiko).where(RtpRisiko.risiko_id.in_(missing_ids))).all():
            rtp_map[rt.risiko_id] = rt
    p_ids = [r["id"] for r in prioritas]
    infokom_map: dict[int, Infokom] = {}
    pi_map: dict[int, MonitoringPi] = {}
    if p_ids:
        for inf in session.exec(select(Infokom).where(Infokom.risiko_id.in_(p_ids))).all():
            infokom_map[inf.risiko_id] = inf
        for pi in session.exec(select(MonitoringPi).where(MonitoringPi.risiko_id.in_(p_ids))).all():
            pi_map[pi.risiko_id] = pi

    out = []
    for r in prioritas:
        rt = rtp_map.get(r["id"])
        rtp = rt.model_dump() if rt else None
        if rtp is not None:
            # Pemilik/penanggung jawab selalu mengikuti Form 3.b (satu sumber
            # data) — tampilkan nilai terkini meski RTP disimpan lebih dulu.
            rtp["pemilik_penanggung_jawab"] = r.get("pemilik_risiko")
        inf = infokom_map.get(r["id"])
        pi = pi_map.get(r["id"])
        out.append({
            **r,
            "rtp": rtp,
            "infokom": inf.model_dump() if inf else None,
            "monitoring_pi": pi.model_dump() if pi else None,
        })
    return out


@router.get("/rtp/options")
def rtp_options(
    opd_id: int,
    tahun: int,
    session: Session = Depends(get_session),
):
    """Opsi Rencana Tindak Pengendalian (RTP) dari Form 7 untuk combobox Form 8 & 9."""
    rows = list_rtp(opd_id, tahun, session)
    out = []
    seen: set[str] = set()
    for r in rows:
        rtp = r.get("rtp")
        if not rtp:
            continue
        rencana = (rtp.get("rencana_tindak") or "").strip()
        if not rencana:
            continue
        kode = r.get("kode_risiko") or ""
        uraian = r.get("uraian_risiko") or ""
        sublabel = f"[{kode}] {uraian}" if kode else uraian

        if rencana not in seen:
            seen.add(rencana)
            out.append(
                {
                    "label": rencana,
                    "value": rencana,
                    "sublabel": sublabel,
                    "kode_risiko": kode,
                    "uraian_risiko": uraian,
                    "jenis_risiko": r.get("jenis_risiko"),
                    "penanggung_jawab": rtp.get("pemilik_penanggung_jawab") or r.get("pemilik_risiko"),
                    "rencana_waktu": rtp.get("target_waktu"),
                    "realisasi_waktu": rtp.get("realisasi_waktu"),
                }
            )
    return out


@router.post("/rtp")
def save_rtp(body: RtpInput, session: Session = Depends(get_session), user: dict = UserDep):
    risiko = governance.risiko_akses(session, user, body.risiko_id, tulis=True)
    obj = session.exec(select(RtpRisiko).where(RtpRisiko.risiko_id == risiko.id)).first()
    if not obj:
        obj = RtpRisiko(risiko_id=risiko.id)
    data = body.model_dump(exclude={"risiko_id", "bukti_upload"})
    data["target_mulai"] = body.target_mulai or body.target_waktu
    data["target_selesai"] = body.target_selesai or body.target_waktu
    # Ringkasan kompatibel untuk tabel, dashboard, serta ekspor lama.
    data["target_waktu"] = (
        f"{body.target_mulai.isoformat()} s.d. {body.target_selesai.isoformat()}"
        if body.target_mulai else body.target_waktu.isoformat() if body.target_waktu else None
    )
    evidence = None
    if body.bukti_berkas_id:
        evidence = session.get(RtpBukti, body.bukti_berkas_id)
        if not evidence or evidence.risiko_id != risiko.id:
            raise HTTPException(422, "Berkas bukti tidak berasal dari risiko ini")
    if body.bukti_upload:
        try:
            content = base64.b64decode(body.bukti_upload.base64, validate=True)
        except (ValueError, binascii.Error):
            raise HTTPException(422, "Berkas tidak valid")
        if not content or len(content) > MAX_BUKTI:
            raise HTTPException(422, "Berkas harus berisi data dan maksimal 5 MB")
        name = body.bukti_upload.nama.replace("\\", "/").rsplit("/", 1)[-1]
        name = "".join(c for c in name if c.isprintable()).strip()
        if not name or name in {".", ".."}:
            raise HTTPException(422, "Nama berkas tidak valid")
        evidence = RtpBukti(risiko_id=risiko.id, nama=name, konten=content,
            ukuran=len(content), pembuat=governance.identitas(user))
        session.add(evidence)
        session.flush()
    data["bukti_berkas_id"] = evidence.id if evidence else None
    data["bukti_nama"] = evidence.nama if evidence else None
    for key, value in data.items():
        setattr(obj, key, value)
    # Realisasi lama tetap utuh; tidak diedit melalui Form 7.
    obj.pemilik_penanggung_jawab = risiko.pemilik_risiko
    obj.updated_at = now_wib()
    session.add(obj)

    tindak = (body.rencana_tindak or "").strip()
    if tindak:
        inf = session.exec(select(Infokom).where(Infokom.risiko_id == risiko.id)).first()
        if inf:
            inf.kegiatan_pengendalian = tindak
        else:
            inf = Infokom(
                opd_id=risiko.opd_id,
                tahun=risiko.tahun,
                risiko_id=risiko.id,
                kegiatan_pengendalian=tindak,
                rencana_mulai=data.get("target_mulai"),
                rencana_selesai=data.get("target_selesai"),
                rencana_waktu=data.get("target_waktu"),
            )
            session.add(inf)

        pi = session.exec(select(MonitoringPi).where(MonitoringPi.risiko_id == risiko.id)).first()
        if pi:
            pi.kegiatan_pengendalian = tindak
            if not pi.penanggung_jawab:
                pi.penanggung_jawab = risiko.pemilik_risiko
        else:
            pi = MonitoringPi(
                opd_id=risiko.opd_id,
                tahun=risiko.tahun,
                risiko_id=risiko.id,
                jenis_risiko=risiko.jenis_risiko,
                kegiatan_pengendalian=tindak,
                penanggung_jawab=risiko.pemilik_risiko,
                rencana_mulai=data.get("target_mulai"),
                rencana_selesai=data.get("target_selesai"),
                rencana_waktu=data.get("target_waktu"),
            )
            session.add(pi)

    governance.audit(session, user, obj, "rtp_diperbarui", risiko.opd_id, risiko.tahun, risiko.id)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/rtp/{rid}/berkas/{bid}")
def unduh_bukti(rid: int, bid: int, session: Session = Depends(get_session), user: dict = UserDep):
    governance.risiko_akses(session, user, rid)
    evidence = session.get(RtpBukti, bid)
    if not evidence or evidence.risiko_id != rid:
        raise HTTPException(404, "Berkas bukti tidak ditemukan")
    return Response(content=evidence.konten, media_type="application/octet-stream", headers={
        "Content-Disposition": "attachment; filename*=UTF-8''" + quote(evidence.nama, safe=""),
        "X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store",
    })
