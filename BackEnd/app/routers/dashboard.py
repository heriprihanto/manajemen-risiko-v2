"""Ringkasan eksekutif dashboard per OPD & tahun."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.db import get_session
from app.models import (
    AnalisisRisiko,
    CeeResponden,
    Infokom,
    KonteksOperasionalOpd,
    KonteksStrategisOpd,
    MonitoringPi,
    RefBidangUrusan,
    Risiko,
    RtpRisiko,
)
from app.services import analisis as an
from app.services import selera

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

JENIS_LABEL = {
    "strategis_pemda": "Strategis Pemda (Form 3.a)",
    "strategis_opd": "Strategis OPD (Form 3.b)",
    "operasional_opd": "Operasional OPD (Form 3.c)",
}


@router.get("/summary")
def summary(opd_id: int, tahun: int, session: Session = Depends(get_session)):
    # 1. Responden CEE
    jumlah_responden = session.exec(
        select(func.count(CeeResponden.id)).where(
            CeeResponden.opd_id == opd_id, CeeResponden.tahun == tahun
        )
    ).one()

    # 2. Risiko
    risiko = session.exec(
        select(Risiko).where(Risiko.opd_id == opd_id, Risiko.tahun == tahun)
    ).all()
    ids = [r.id for r in risiko]

    # 3. Analisis & RTP
    amap: dict[int, AnalisisRisiko] = {}
    rtp_map: dict[int, RtpRisiko] = {}
    if ids:
        amap = {
            a.risiko_id: a
            for a in session.exec(
                select(AnalisisRisiko).where(AnalisisRisiko.risiko_id.in_(ids))
            ).all()
        }
        rtp_map = {
            rt.risiko_id: rt
            for rt in session.exec(
                select(RtpRisiko).where(RtpRisiko.risiko_id.in_(ids))
            ).all()
        }

    # 4. Ref Bidang Urusan
    bu_ids = [r.id_bidang_urusan for r in risiko if r.id_bidang_urusan]
    bu_map: dict[int, RefBidangUrusan] = {}
    if bu_ids:
        bu_map = {
            b.id: b
            for b in session.exec(
                select(RefBidangUrusan).where(RefBidangUrusan.id.in_(bu_ids))
            ).all()
        }

    # 5. Agregasi
    per_jenis: dict[str, int] = {
        "strategis_pemda": 0,
        "strategis_opd": 0,
        "operasional_opd": 0,
    }
    per_level: dict[str, int] = {
        an.LEVEL_SANGAT_TINGGI: 0,
        an.LEVEL_TINGGI: 0,
        an.LEVEL_SEDANG: 0,
        an.LEVEL_RENDAH: 0,
        an.LEVEL_SANGAT_RENDAH: 0,
    }
    per_kategori: dict[str, int] = {}
    per_cuc: dict[str, int] = {"C": 0, "UC": 0, "Belum Ditentukan": 0}

    jumlah_dianalisis = 0
    jumlah_prioritas = 0
    jumlah_rtp = 0
    prioritas_dengan_rtp = 0
    prioritas_tanpa_rtp = 0

    heatmap_cells: dict[str, list[dict[str, Any]]] = {}
    detailed_risks: list[dict[str, Any]] = []

    aktif = selera.daftar_aktif(session, opd_id, tahun)
    for r in risiko:
        # Jenis
        if r.jenis_risiko in per_jenis:
            per_jenis[r.jenis_risiko] += 1
        else:
            per_jenis[r.jenis_risiko] = 1

        # C / UC
        cuc_val = (r.cuc or "").strip().upper()
        if cuc_val in ("C", "UC"):
            per_cuc[cuc_val] += 1
        else:
            per_cuc["Belum Ditentukan"] += 1

        # Kategori
        kat = (r.kategori_risiko or "Lainnya").strip()
        per_kategori[kat] = per_kategori.get(kat, 0) + 1

        # Analisis & RTP
        a = amap.get(r.id)
        rtp = rtp_map.get(r.id)
        has_rtp = bool(rtp and (rtp.rencana_tindak or "").strip())
        if has_rtp:
            jumlah_rtp += 1

        d, k, s = (
            (a.skala_dampak, a.skala_kemungkinan, a.skala_risiko)
            if a
            else (None, None, None)
        )
        lvl = an.level_risiko(s) if s is not None else None
        setting = selera.resolve(aktif, r.pemilik_risiko)
        is_prio = selera.status(s, setting)

        if s is not None:
            jumlah_dianalisis += 1
            if lvl in per_level:
                per_level[lvl] += 1
            if is_prio:
                jumlah_prioritas += 1
                if has_rtp:
                    prioritas_dengan_rtp += 1
                else:
                    prioritas_tanpa_rtp += 1

        bu = bu_map.get(r.id_bidang_urusan) if r.id_bidang_urusan else None
        bu_alias = (
            (bu.bidang_urusan_alias or bu.nama_bidang_urusan) if bu else None
        )

        item_dict = {
            "id": r.id,
            "kode_risiko": r.kode_risiko or f"R-{r.id}",
            "uraian_risiko": r.uraian_risiko,
            "keterangan_risiko": r.keterangan_risiko,
            "jenis_risiko": r.jenis_risiko,
            "jenis_label": JENIS_LABEL.get(r.jenis_risiko, r.jenis_risiko),
            "kategori_risiko": r.kategori_risiko or "Lainnya",
            "pemilik_risiko": r.pemilik_risiko,
            "cuc": r.cuc,
            "bidang_urusan": bu_alias,
            "skala_dampak": d,
            "skala_kemungkinan": k,
            "skala_risiko": s,
            "level": lvl,
            "is_prioritas": is_prio,
            "ambang_selera": setting.ambang if setting else None,
            "has_rtp": has_rtp,
            "rencana_tindak": rtp.rencana_tindak if rtp else None,
            "target_waktu": rtp.target_waktu if rtp else None,
            "pemilik_penanggung_jawab": (
                rtp.pemilik_penanggung_jawab if rtp else None
            ),
        }
        detailed_risks.append(item_dict)

        if d and k:
            cell_key = f"{k}-{d}"
            heatmap_cells.setdefault(cell_key, []).append(item_dict)

    # 6. Top prioritas mengikuti ambang yang berlaku.
    top_prioritas = [
        r
        for r in detailed_risks
        if r["skala_risiko"] is not None
        and r["is_prioritas"]
    ]
    top_prioritas.sort(
        key=lambda x: (x["skala_risiko"] or 0, 1 if not x["has_rtp"] else 0),
        reverse=True,
    )
    top_prioritas = top_prioritas[:10]

    # 7. Monitoring & Konteks counts
    infokom_count = session.exec(
        select(func.count(Infokom.id)).where(
            Infokom.opd_id == opd_id, Infokom.tahun == tahun
        )
    ).one()
    monitoring_pi_count = session.exec(
        select(func.count(MonitoringPi.id)).where(
            MonitoringPi.opd_id == opd_id, MonitoringPi.tahun == tahun
        )
    ).one()
    konteks_count = session.exec(
        select(func.count(KonteksStrategisOpd.id)).where(
            KonteksStrategisOpd.opd_id == opd_id, KonteksStrategisOpd.tahun == tahun
        )
    ).one() + session.exec(
        select(func.count(KonteksOperasionalOpd.id)).where(
            KonteksOperasionalOpd.opd_id == opd_id,
            KonteksOperasionalOpd.tahun == tahun,
        )
    ).one()

    # 8. Rekomendasi Eksekutif (Smart Engine)
    rekomendasi = []

    # Rekomendasi 1: RTP Prioritas
    if prioritas_tanpa_rtp > 0:
        rekomendasi.append(
            {
                "severity": "kritis",
                "judul": f"{prioritas_tanpa_rtp} Risiko Prioritas Belum Memiliki RTP",
                "pesan": (
                    f"Terdapat {prioritas_tanpa_rtp} risiko dengan level prioritas tinggi/sangat tinggi "
                    f"yang belum dilengkapi Rencana Tindak Pengendalian (Form 7). "
                    f"Segera tetapkan tindakan mitigasi, penanggung jawab, dan target waktu penyelesaian."
                ),
                "action_label": "Susun RTP (Form 7)",
                "action_link": "/rtp",
            }
        )
    elif jumlah_prioritas > 0:
        rekomendasi.append(
            {
                "severity": "sukses",
                "judul": "Seluruh Risiko Prioritas Telah Memiliki RTP",
                "pesan": (
                    f"Semua {jumlah_prioritas} risiko prioritas telah memiliki Rencana Tindak Pengendalian (Form 7). "
                    f"Langkah berikutnya adalah pemantauan pelaksanaan pengendalian secara berkala."
                ),
                "action_label": "Lihat Pemantauan (Form 9)",
                "action_link": "/monitoring",
            }
        )

    # Rekomendasi 2: Risiko Uncontrollable (UC)
    uc_high = [
        r
        for r in detailed_risks
        if r["cuc"] == "UC"
        and r["level"] in (an.LEVEL_SANGAT_TINGGI, an.LEVEL_TINGGI)
    ]
    if uc_high:
        rekomendasi.append(
            {
                "severity": "perhatian",
                "judul": f"{len(uc_high)} Risiko Uncontrollable (UC) Level Tinggi",
                "pesan": (
                    f"Terdapat {len(uc_high)} risiko di luar kendali langsung OPD yang bernilai dampak signifikan. "
                    f"Diperlukan koordinasi lintas sektoral, eskalasi ke tingkat Pemerintah Daerah/Sekda, "
                    f"atau contingency plan (rencana kedaruratan)."
                ),
                "action_label": "Tinjau Risiko UC",
                "action_link": "/identifikasi-risiko",
            }
        )

    # Rekomendasi 3: Kategori Risiko Dominan
    if per_kategori:
        sorted_kat = sorted(
            per_kategori.items(), key=lambda x: x[1], reverse=True
        )
        top_kat, top_kat_count = sorted_kat[0]
        if top_kat != "Lainnya" and top_kat_count > 0:
            rekomendasi.append(
                {
                    "severity": "informasi",
                    "judul": f"Fokus Utama: Kategori {top_kat} ({top_kat_count} Risiko)",
                    "pesan": (
                        f"Sebagian besar risiko yang dihadapi berada pada kategori {top_kat}. "
                        f"Direkomendasikan untuk memperkuat SOP, audit kepatuhan internal, "
                        f"dan sosialisasi pencegahan pada area ini."
                    ),
                    "action_label": "Kamus Risiko",
                    "action_link": "/kamus-risiko",
                }
            )

    # Rekomendasi 4: Analisis belum lengkap
    belum_dianalisis = len(risiko) - jumlah_dianalisis
    if belum_dianalisis > 0:
        rekomendasi.append(
            {
                "severity": "perhatian",
                "judul": f"{belum_dianalisis} Risiko Belum Dianalisis",
                "pesan": (
                    f"Terdapat {belum_dianalisis} risiko teridentifikasi yang belum dinilai skala kemungkinan "
                    f"dan dampaknya. Selesaikan penilaian pada Form 4 agar profil risiko akurat."
                ),
                "action_label": "Analisis Risiko (Form 4)",
                "action_link": "/analisis",
            }
        )

    # Rekomendasi 5: Responden CEE
    if jumlah_responden == 0:
        rekomendasi.append(
            {
                "severity": "informasi",
                "judul": "Survei CEE Belum Memiliki Responden",
                "pesan": (
                    "Belum ada pengisian kuesioner Control Environment Evaluation (CEE) untuk OPD ini "
                    "pada tahun penilaian aktif. Bagikan tautan survei kepada pegawai terkait."
                ),
                "action_label": "Kelola Kuesioner",
                "action_link": "/cee/kuesioner",
            }
        )

    # 9. Tahapan Progress
    tahapan_progress = [
        {
            "no": 1,
            "nama": "Lingkungan Pengendalian (CEE)",
            "form": "Form 1.a / 1.b / 1.c",
            "link": "/cee/form1a",
            "status": "selesai" if jumlah_responden > 0 else "belum",
            "keterangan": (
                f"{jumlah_responden} responden terdata"
                if jumlah_responden > 0
                else "Belum ada responden"
            ),
        },
        {
            "no": 2,
            "nama": "Penetapan Konteks",
            "form": "Form 2.a / 2.b / 2.c",
            "link": "/konteks/opd",
            "status": "selesai" if konteks_count > 0 else "belum",
            "keterangan": (
                f"{konteks_count} konteks ditetapkan"
                if konteks_count > 0
                else "Belum ada konteks"
            ),
        },
        {
            "no": 3,
            "nama": "Identifikasi Risiko",
            "form": "Form 3.a / 3.b / 3.c",
            "link": "/identifikasi-risiko",
            "status": "selesai" if len(risiko) > 0 else "belum",
            "keterangan": f"{len(risiko)} risiko teridentifikasi",
        },
        {
            "no": 4,
            "nama": "Analisis & Evaluasi",
            "form": "Form 4 & Form 5",
            "link": "/analisis",
            "status": (
                "selesai"
                if (len(risiko) > 0 and jumlah_dianalisis == len(risiko))
                else ("proses" if jumlah_dianalisis > 0 else "belum")
            ),
            "keterangan": f"{jumlah_dianalisis} dari {len(risiko)} risiko dinilai",
        },
        {
            "no": 5,
            "nama": "Rencana Tindak Pengendalian (RTP)",
            "form": "Form 7",
            "link": "/rtp",
            "status": (
                "selesai"
                if (jumlah_prioritas > 0 and prioritas_tanpa_rtp == 0)
                else ("proses" if jumlah_rtp > 0 else "belum")
            ),
            "keterangan": (
                f"{prioritas_dengan_rtp} dari {jumlah_prioritas} prioritas ber-RTP"
                if jumlah_prioritas > 0
                else "Tidak ada risiko prioritas"
            ),
        },
        {
            "no": 6,
            "nama": "Pemantauan & Evaluasi",
            "form": "Form 8 & Form 9",
            "link": "/monitoring",
            "status": (
                "selesai"
                if (infokom_count > 0 and monitoring_pi_count > 0)
                else (
                    "proses"
                    if (infokom_count > 0 or monitoring_pi_count > 0)
                    else "belum"
                )
            ),
            "keterangan": f"{infokom_count} Infokom, {monitoring_pi_count} Pemantauan PI",
        },
    ]

    return {
        "opd_id": opd_id,
        "tahun": tahun,
        "jumlah_responden": jumlah_responden,
        "jumlah_risiko": len(risiko),
        "jumlah_dianalisis": jumlah_dianalisis,
        "jumlah_prioritas": jumlah_prioritas,
        "jumlah_rtp": jumlah_rtp,
        "prioritas_dengan_rtp": prioritas_dengan_rtp,
        "prioritas_tanpa_rtp": prioritas_tanpa_rtp,
        "persentase_rtp": (
            round((prioritas_dengan_rtp / jumlah_prioritas) * 100)
            if jumlah_prioritas > 0
            else 100
        ),
        "persentase_analisis": (
            round((jumlah_dianalisis / len(risiko)) * 100)
            if len(risiko) > 0
            else 0
        ),
        "risiko_per_jenis": per_jenis,
        "risiko_per_level": per_level,
        "risiko_per_kategori": per_kategori,
        "risiko_per_cuc": per_cuc,
        "heatmap": {
            "dampak_label": an.DAMPAK_LABEL,
            "kemungkinan_label": an.KEMUNGKINAN_LABEL,
            "cells": heatmap_cells,
        },
        "top_prioritas": top_prioritas,
        "rekomendasi": rekomendasi,
        "tahapan_progress": tahapan_progress,
    }
