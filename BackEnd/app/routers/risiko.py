"""Form 3a/3b/3c (identifikasi risiko), Form 4 (analisis), Form 5 (prioritas),
Matriks Risiko, Form 7 (RTP risiko)."""
import base64
import binascii
import re
from urllib.parse import quote
from datetime import date, datetime
from typing import Any

from app.core.datetime_utils import now_wib

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import Response
from app.models.risiko import RtpBukti
from app.schemas.rtp import RtpInput, MAX_BUKTI
from sqlmodel import Session, func, select

from app.core.security import UserDep, ensure_opd_access, guard_record
from app.db import get_session
from app.models import (
    AnalisisRisiko,
    Opd,
    RealisasiRtp,
    RefBidangUrusan,
    Risiko,
    RtpRisiko,
    TreatedRisk,
    MonitoringRiskEvent,
    Infokom,
    MonitoringPi,
    RtpCee,
)
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
    evidence = session.get(RtpBukti, bid)
    if not evidence:
        raise HTTPException(404, "Berkas bukti tidak ditemukan")
    if evidence.risiko_id:
        governance.risiko_akses(session, user, evidence.risiko_id)
    elif evidence.rtp_cee_id:
        cee = session.get(RtpCee, evidence.rtp_cee_id)
        if cee:
            governance.opd_akses(user, cee.opd_id)
    return Response(content=evidence.konten, media_type="application/octet-stream", headers={
        "Content-Disposition": "attachment; filename*=UTF-8''" + quote(evidence.nama, safe=""),
        "X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store",
    })


@router.get("/bukti/{bid}")
def unduh_bukti_langsung(bid: int, session: Session = Depends(get_session), user: dict = UserDep):
    return unduh_bukti(0, bid, session, user)


# ------------------------------ Treated Risk ----------------------------------
@router.get("/treated")
def list_treated(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Daftar risiko beserta nilai inheren, RTP, dan Treated Risk."""
    rows = list_risiko(opd_id, tahun, None, session)

    saved_rtp_records = session.exec(
        select(RtpRisiko).join(Risiko, RtpRisiko.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    rtp_map = {rt.risiko_id: rt for rt in saved_rtp_records}

    saved_treated = session.exec(
        select(TreatedRisk).join(Risiko, TreatedRisk.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    treated_map = {tr.risiko_id: tr for tr in saved_treated}

    saved_realisasi = session.exec(
        select(RealisasiRtp).join(Risiko, RealisasiRtp.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    realisasi_map = {rel.risiko_id: rel for rel in saved_realisasi}

    # Ambil selera risiko aktif OPD
    policy_id, policy = governance.snapshot_kebijakan(session, opd_id, tahun)
    ambang_selera = 10
    if policy and policy.get("selera"):
        ambang_selera = max(policy["selera"]) if isinstance(policy["selera"], list) and policy["selera"] else 10

    out = []
    for r in rows:
        rt = rtp_map.get(r["id"])
        tr = treated_map.get(r["id"])
        rel = realisasi_map.get(r["id"])

        an_data = r.get("analisis") or {}
        inh_dampak = an_data.get("skala_dampak")
        inh_kemungkinan = an_data.get("skala_kemungkinan")
        inh_skala = an_data.get("skala_risiko")

        tr_dampak = tr.dampak_treated if tr else None
        tr_kemungkinan = tr.kemungkinan_treated if tr else None
        tr_skala = tr.skala_treated if tr else None
        tr_level = an.level_risiko(tr_skala) if tr_skala else None
        tr_justifikasi = tr.justifikasi if tr else None

        delta_skor = None
        if inh_skala is not None and tr_skala is not None:
            delta_skor = round(tr_skala - inh_skala, 1)

        memenuhi_selera = None
        if tr_skala is not None:
            memenuhi_selera = tr_skala <= ambang_selera

        out.append({
            **r,
            "rtp": rt.model_dump() if rt else None,
            "realisasi": {
                "id": rel.id if rel else None,
                "status_realisasi": rel.status_realisasi if rel else "belum",
                "tanggal_realisasi": rel.tanggal_realisasi.isoformat() if rel and rel.tanggal_realisasi else None,
                "uraian_hasil": rel.uraian_hasil if rel else None,
                "hambatan": rel.hambatan if rel else None,
                "bukti_berkas_id": rel.bukti_berkas_id if rel else None,
                "bukti_nama": rel.bukti_nama if rel else None,
                "bukti_link": rel.bukti_link if rel else None,
            } if rel else None,
            "treated": {
                "id": tr.id if tr else None,
                "dampak_treated": tr_dampak,
                "kemungkinan_treated": tr_kemungkinan,
                "skala_treated": tr_skala,
                "level_treated": tr_level,
                "justifikasi": tr_justifikasi,
                "delta_skor": delta_skor,
                "memenuhi_selera": memenuhi_selera,
                "updated_at": tr.updated_at.isoformat() if tr and tr.updated_at else None,
                "updated_by": tr.updated_by if tr else None,
            } if tr else None,
        })

    return {
        "items": out,
        "ambang_selera": ambang_selera,
        "kriteria_dampak": an.DAMPAK_LABEL,
        "kriteria_kemungkinan": an.KEMUNGKINAN_LABEL,
        "matriks_skala": {
            f"{k}-{d}": an.MATRIKS_SKALA.get((k, d))
            for k in range(1, 6)
            for d in range(1, 6)
        },
    }


@router.post("/treated")
def save_treated(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Simpan atau perbarui penilaian Treated Risk atas risiko."""
    risiko_id = payload.get("risiko_id")
    if not risiko_id:
        raise HTTPException(400, "risiko_id wajib diisi")

    risiko = governance.risiko_akses(session, user, risiko_id, tulis=True)
    dampak = payload.get("dampak_treated")
    kemungkinan = payload.get("kemungkinan_treated")
    justifikasi = (payload.get("justifikasi") or "").strip() or None

    if dampak is not None and not (1 <= int(dampak) <= 5):
        raise HTTPException(400, "Dampak treated harus bernilai antara 1 dan 5")
    if kemungkinan is not None and not (1 <= int(kemungkinan) <= 5):
        raise HTTPException(400, "Kemungkinan treated harus bernilai antara 1 dan 5")

    dampak = int(dampak) if dampak is not None else None
    kemungkinan = int(kemungkinan) if kemungkinan is not None else None
    skala = an.hitung_skala(dampak, kemungkinan)

    obj = session.exec(select(TreatedRisk).where(TreatedRisk.risiko_id == risiko.id)).first()
    if not obj:
        obj = TreatedRisk(risiko_id=risiko.id)

    obj.dampak_treated = dampak
    obj.kemungkinan_treated = kemungkinan
    obj.skala_treated = skala
    obj.justifikasi = justifikasi
    obj.updated_at = now_wib()
    obj.updated_by = user.get("username")
    session.add(obj)

    # Catat audit dan riwayat tata kelola jika penilaian lengkap
    if dampak and kemungkinan and skala:
        try:
            evaluated = governance.nilai(session, risiko, dampak, kemungkinan)
            history = PenilaianRiwayat(
                risiko_id=risiko.id,
                tahap="target",
                dampak=dampak,
                kemungkinan=kemungkinan,
                skor=int(skala),
                prioritas=evaluated.get("prioritas", False),
                di_luar_toleransi=evaluated.get("di_luar_toleransi", False),
                kebijakan_id=evaluated.get("kebijakan_id"),
                kebijakan_snapshot=evaluated.get("kebijakan_snapshot", {}),
                alasan=justifikasi or "Penilaian Treated Risk pasca-RTP",
                pembuat=governance.identitas(user),
            )
            session.add(history)
            governance.audit(session, user, obj, "treated_risk_dinilai", risiko.opd_id, risiko.tahun, risiko.id)
        except Exception:
            pass

    session.commit()
    session.refresh(obj)
    return {
        "id": obj.id,
        "risiko_id": obj.risiko_id,
        "dampak_treated": obj.dampak_treated,
        "kemungkinan_treated": obj.kemungkinan_treated,
        "skala_treated": obj.skala_treated,
        "level_treated": an.level_risiko(obj.skala_treated),
        "justifikasi": obj.justifikasi,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        "updated_by": obj.updated_by,
    }


# ------------------------------ Realisasi RTP ---------------------------------
@router.get("/realisasi")
def list_realisasi(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    """Daftar rencana tindak pengendalian beserta status, tanggal, dan bukti dukung realisasinya."""
    rows = list_risiko(opd_id, tahun, None, session)

    saved_rtp_records = session.exec(
        select(RtpRisiko).join(Risiko, RtpRisiko.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    rtp_map = {rt.risiko_id: rt for rt in saved_rtp_records}

    saved_realisasi = session.exec(
        select(RealisasiRtp).join(Risiko, RealisasiRtp.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    realisasi_map = {rel.risiko_id: rel for rel in saved_realisasi}

    saved_treated = session.exec(
        select(TreatedRisk).join(Risiko, TreatedRisk.risiko_id == Risiko.id)
        .where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    treated_map = {tr.risiko_id: tr for tr in saved_treated}

    items = []
    total_rtp = 0
    selesai_cnt = 0
    proses_cnt = 0
    belum_cnt = 0

    # 1. RTP Pengelolaan Risiko (Form 7)
    for r in rows:
        is_prioritas = r.get("analisis", {}).get("is_prioritas", False)
        rt = rtp_map.get(r["id"])
        # Fokuskan pada risiko prioritas atau yang memiliki rencana tindak pengendalian
        if not is_prioritas and not rt:
            continue

        total_rtp += 1
        rel = realisasi_map.get(r["id"])
        tr = treated_map.get(r["id"])

        status_realisasi = rel.status_realisasi if rel and rel.status_realisasi else "belum"
        if status_realisasi == "selesai":
            selesai_cnt += 1
        elif status_realisasi == "proses":
            proses_cnt += 1
        else:
            belum_cnt += 1

        items.append({
            **r,
            "source_type": "risiko",
            "risiko_id": r["id"],
            "rtp_cee_id": None,
            "rtp": rt.model_dump() if rt else None,
            "realisasi": {
                "id": rel.id if rel else None,
                "status_realisasi": status_realisasi,
                "tanggal_realisasi": rel.tanggal_realisasi.isoformat() if rel and rel.tanggal_realisasi else None,
                "uraian_hasil": rel.uraian_hasil if rel else None,
                "hambatan": rel.hambatan if rel else None,
                "bukti_berkas_id": rel.bukti_berkas_id if rel else None,
                "bukti_nama": rel.bukti_nama if rel else None,
                "bukti_link": rel.bukti_link if rel else None,
                "updated_at": rel.updated_at.isoformat() if rel and rel.updated_at else None,
                "updated_by": rel.updated_by if rel else None,
            } if rel else {
                "id": None,
                "status_realisasi": "belum",
                "tanggal_realisasi": None,
                "uraian_hasil": None,
                "hambatan": None,
                "bukti_berkas_id": None,
                "bukti_nama": None,
                "bukti_link": None,
                "updated_at": None,
                "updated_by": None,
            },
            "treated": {
                "id": tr.id if tr else None,
                "dampak_treated": tr.dampak_treated if tr else None,
                "kemungkinan_treated": tr.kemungkinan_treated if tr else None,
                "skala_treated": tr.skala_treated if tr else None,
                "level_treated": an.level_risiko(tr.skala_treated) if tr and tr.skala_treated else None,
            } if tr else None,
        })

    # 2. RTP atas CEE (Form 6)
    cee_rows = session.exec(
        select(RtpCee).where(RtpCee.opd_id == opd_id, RtpCee.tahun == tahun)
        .order_by(RtpCee.no_urut, RtpCee.id)
    ).all()

    cee_realisasi = session.exec(
        select(RealisasiRtp).join(RtpCee, RealisasiRtp.rtp_cee_id == RtpCee.id)
        .where(RtpCee.opd_id == opd_id, RtpCee.tahun == tahun)
    ).all()
    cee_rel_map = {rel.rtp_cee_id: rel for rel in cee_realisasi}

    for c in cee_rows:
        total_rtp += 1
        rel = cee_rel_map.get(c.id)

        tgl_rel = rel.tanggal_realisasi.isoformat() if rel and rel.tanggal_realisasi else None
        if not tgl_rel and c.realisasi_waktu and re.match(r"^\d{4}-\d{2}-\d{2}$", str(c.realisasi_waktu).strip()):
            tgl_rel = str(c.realisasi_waktu).strip()

        status_realisasi = rel.status_realisasi if rel and rel.status_realisasi else ("selesai" if tgl_rel else "belum")
        if status_realisasi == "selesai":
            selesai_cnt += 1
        elif status_realisasi == "proses":
            proses_cnt += 1
        else:
            belum_cnt += 1

        items.append({
            "id": f"cee-{c.id}",
            "source_type": "cee",
            "risiko_id": None,
            "rtp_cee_id": c.id,
            "opd_id": c.opd_id,
            "tahun": c.tahun,
            "jenis_risiko": "cee",
            "kode_risiko": f"CEE-{c.no_urut or c.id}",
            "uraian_risiko": c.kondisi_kerentanan or c.rencana_tindak or "Kelemahan Lingkungan Pengendalian",
            "sasaran": c.aspek_cee or "Lingkungan Pengendalian Intern",
            "pemilik_risiko": c.pemilik_penanggung_jawab or "Pimpinan OPD",
            "analisis": {
                "level": "CEE",
                "is_prioritas": True,
            },
            "rtp": {
                "id": c.id,
                "rencana_tindak": c.rencana_tindak,
                "target_waktu": c.target_waktu,
                "target_mulai": c.target_mulai.isoformat() if c.target_mulai else None,
                "target_selesai": c.target_selesai.isoformat() if c.target_selesai else None,
                "pemilik_penanggung_jawab": c.pemilik_penanggung_jawab,
                "aspek_cee": c.aspek_cee,
                "kondisi_kerentanan": c.kondisi_kerentanan,
            },
            "realisasi": {
                "id": rel.id if rel else None,
                "status_realisasi": status_realisasi,
                "tanggal_realisasi": tgl_rel,
                "uraian_hasil": rel.uraian_hasil if rel else None,
                "hambatan": rel.hambatan if rel else None,
                "bukti_berkas_id": rel.bukti_berkas_id if rel else None,
                "bukti_nama": rel.bukti_nama if rel else None,
                "bukti_link": rel.bukti_link if rel else (c.realisasi_waktu if c.realisasi_waktu and str(c.realisasi_waktu).startswith("http") else None),
                "updated_at": rel.updated_at.isoformat() if rel and rel.updated_at else None,
                "updated_by": rel.updated_by if rel else None,
            },
            "treated": None,
        })

    persen_selesai = round((selesai_cnt / total_rtp * 100), 1) if total_rtp > 0 else 0

    return {
        "items": items,
        "summary": {
            "total": total_rtp,
            "selesai": selesai_cnt,
            "proses": proses_cnt,
            "belum": belum_cnt,
            "persen_selesai": persen_selesai,
        },
    }


@router.post("/realisasi")
def save_realisasi(
    payload: dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    user: dict = UserDep,
):
    """Simpan status realisasi RTP, tanggal realisasi, dan unggah berkas bukti dukung."""
    risiko_id = payload.get("risiko_id")
    rtp_cee_id = payload.get("rtp_cee_id")

    if not risiko_id and not rtp_cee_id:
        raise HTTPException(400, "risiko_id atau rtp_cee_id wajib diisi")

    risiko = None
    rtp_cee = None
    if risiko_id:
        risiko = governance.risiko_akses(session, user, risiko_id, tulis=True)
    elif rtp_cee_id:
        rtp_cee = session.get(RtpCee, rtp_cee_id)
        if not rtp_cee:
            raise HTTPException(404, "Data RTP atas CEE tidak ditemukan")
        ensure_opd_access(user, rtp_cee.opd_id)
        governance.boleh_tulis(session, user, rtp_cee.opd_id)

    status_realisasi = payload.get("status_realisasi") or "belum"
    if status_realisasi not in {"belum", "proses", "selesai"}:
        raise HTTPException(400, "status_realisasi harus 'belum', 'proses', atau 'selesai'")

    tgl_str = payload.get("tanggal_realisasi")
    tanggal_realisasi = None
    if tgl_str:
        try:
            tanggal_realisasi = date.fromisoformat(str(tgl_str).split("T")[0])
        except ValueError:
            raise HTTPException(422, "Format tanggal realisasi tidak valid (gunakan YYYY-MM-DD)")

    uraian_hasil = (payload.get("uraian_hasil") or "").strip() or None
    hambatan = (payload.get("hambatan") or "").strip() or None
    bukti_link = (payload.get("bukti_link") or "").strip() or None

    bukti_upload = payload.get("bukti_upload")
    bukti_berkas_id = payload.get("bukti_berkas_id")

    evidence = None
    if bukti_berkas_id:
        evidence = session.get(RtpBukti, bukti_berkas_id)
        if not evidence:
            raise HTTPException(422, "Berkas bukti tidak ditemukan")
        if risiko and evidence.risiko_id != risiko.id:
            raise HTTPException(422, "Berkas bukti tidak berasal dari risiko ini")
        if rtp_cee and evidence.rtp_cee_id != rtp_cee.id:
            raise HTTPException(422, "Berkas bukti tidak berasal dari RTP CEE ini")

    if bukti_upload and isinstance(bukti_upload, dict) and bukti_upload.get("base64"):
        try:
            content = base64.b64decode(bukti_upload["base64"], validate=True)
        except (ValueError, binascii.Error):
            raise HTTPException(422, "Berkas tidak valid")
        if not content or len(content) > MAX_BUKTI:
            raise HTTPException(422, "Berkas harus berisi data dan maksimal 5 MB")
        name = (bukti_upload.get("nama") or "bukti_realisasi.pdf").replace("\\", "/").rsplit("/", 1)[-1]
        name = "".join(c for c in name if c.isprintable()).strip()
        if not name or name in {".", ".."}:
            raise HTTPException(422, "Nama berkas tidak valid")
        evidence = RtpBukti(
            risiko_id=risiko.id if risiko else None,
            rtp_cee_id=rtp_cee.id if rtp_cee else None,
            nama=name,
            konten=content,
            ukuran=len(content),
            pembuat=governance.identitas(user),
        )
        session.add(evidence)
        session.flush()

    if risiko:
        obj = session.exec(select(RealisasiRtp).where(RealisasiRtp.risiko_id == risiko.id)).first()
        if not obj:
            obj = RealisasiRtp(risiko_id=risiko.id)
    else:
        obj = session.exec(select(RealisasiRtp).where(RealisasiRtp.rtp_cee_id == rtp_cee.id)).first()
        if not obj:
            obj = RealisasiRtp(rtp_cee_id=rtp_cee.id)

    obj.status_realisasi = status_realisasi
    obj.tanggal_realisasi = tanggal_realisasi
    obj.uraian_hasil = uraian_hasil
    obj.hambatan = hambatan
    obj.bukti_link = bukti_link
    if evidence:
        obj.bukti_berkas_id = evidence.id
        obj.bukti_nama = evidence.nama
    elif payload.get("hapus_bukti"):
        obj.bukti_berkas_id = None
        obj.bukti_nama = None

    obj.updated_at = now_wib()
    obj.updated_by = user.get("username")
    session.add(obj)

    if risiko:
        # Sinkronisasi ke RtpRisiko.realisasi_waktu
        rtp_obj = session.exec(select(RtpRisiko).where(RtpRisiko.risiko_id == risiko.id)).first()
        if rtp_obj and tanggal_realisasi:
            rtp_obj.realisasi_waktu = tanggal_realisasi.isoformat()
            session.add(rtp_obj)

        # Sinkronisasi ke MonitoringPi jika ada
        pi = session.exec(select(MonitoringPi).where(MonitoringPi.risiko_id == risiko.id)).first()
        if pi and tanggal_realisasi:
            pi.realisasi_waktu = tanggal_realisasi.isoformat()
            session.add(pi)

        governance.audit(session, user, obj, "realisasi_rtp_diperbarui", risiko.opd_id, risiko.tahun, risiko.id)
    elif rtp_cee:
        # Sinkronisasi ke RtpCee.realisasi_waktu
        if tanggal_realisasi:
            rtp_cee.realisasi_waktu = tanggal_realisasi.isoformat()
            session.add(rtp_cee)
        governance.audit(session, user, obj, "realisasi_rtp_cee_diperbarui", rtp_cee.opd_id, rtp_cee.tahun)

    session.commit()
    session.refresh(obj)

    return {
        "id": obj.id,
        "risiko_id": obj.risiko_id,
        "rtp_cee_id": obj.rtp_cee_id,
        "status_realisasi": obj.status_realisasi,
        "tanggal_realisasi": obj.tanggal_realisasi.isoformat() if obj.tanggal_realisasi else None,
        "uraian_hasil": obj.uraian_hasil,
        "hambatan": obj.hambatan,
        "bukti_berkas_id": obj.bukti_berkas_id,
        "bukti_nama": obj.bukti_nama,
        "bukti_link": obj.bukti_link,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        "updated_by": obj.updated_by,
    }

