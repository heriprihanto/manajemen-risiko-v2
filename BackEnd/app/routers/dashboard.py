"""Ringkasan eksekutif dashboard per OPD & tahun."""
import re
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.core.datetime_utils import today_wib
from app.db import get_session
from app.models import (
    AnalisisRisiko,
    CeeResponden,
    Infokom,
    KonteksOperasionalOpd,
    KonteksStrategisOpd,
    MonitoringPi,
    RealisasiRtp,
    RefBidangUrusan,
    Risiko,
    RtpCee,
    RtpRisiko,
)
from app.services import analisis as an
from app.services import selera

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

JENIS_LABEL = {
    "strategis_pemda": "Strategis Pemda (Form 3.a)",
    "strategis_opd": "Strategis OPD (Form 3.b)",
    "operasional_opd": "Operasional OPD (Form 3.c)",
    "cee": "RTP atas CEE",
}


def parse_deadline(target_selesai: Any, target_mulai: Any, target_waktu: Any, tahun_default: int) -> date | None:
    """Menguraikan batas akhir tanggal jatuh tempo RTP dari kolom tanggal atau teks target waktu."""
    if target_selesai:
        return target_selesai if isinstance(target_selesai, date) else date.fromisoformat(str(target_selesai)[:10])
    if target_mulai:
        return target_mulai if isinstance(target_mulai, date) else date.fromisoformat(str(target_mulai)[:10])
    if not target_waktu:
        return None

    tw = str(target_waktu).strip()

    # 1. Cek format ISO YYYY-MM-DD
    m_iso = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", tw)
    if m_iso:
        return date(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))

    # 2. Cek tahun dalam teks, jika tidak ada gunakan tahun_default
    y_match = re.search(r"\b(202\d)\b", tw)
    y = int(y_match.group(1)) if y_match else int(tahun_default)

    tw_lower = tw.lower()

    # Cek format tanggal Indonesia DD Bulan YYYY
    m_id = re.search(r"(\d{1,2})\s+([a-zA-Z]+)(?:\s+\d{4})?", tw_lower)
    month_names = {
        "januari": (1, 31), "jan": (1, 31),
        "februari": (2, 28), "feb": (2, 28),
        "maret": (3, 31), "mar": (3, 31),
        "april": (4, 30), "apr": (4, 30),
        "mei": (5, 31),
        "juni": (6, 30), "jun": (6, 30),
        "juli": (7, 31), "jul": (7, 31),
        "agustus": (8, 31), "agu": (8, 31), "agt": (8, 31),
        "september": (9, 30), "sep": (9, 30),
        "oktober": (10, 31), "okt": (10, 31),
        "november": (11, 30), "nov": (11, 30),
        "desember": (12, 31), "des": (12, 31),
    }
    if m_id:
        d_val = int(m_id.group(1))
        m_name = m_id.group(2)
        if m_name in month_names:
            m_val, max_d = month_names[m_name]
            return date(y, m_val, min(d_val, max_d))

    # Cek Semester
    if re.search(r"\bsemester\s*(?:ii|2|kedua)\b", tw_lower):
        return date(y, 12, 31)
    if re.search(r"\bsemester\s*(?:i|1|pertama)\b", tw_lower):
        return date(y, 6, 30)

    # Cek Triwulan (jika ada rentang 'triwulan i - iv', ambil batas akhir tertinggi)
    if re.search(r"(?:triwulan|tw)?\s*(?:-\s*|\bs\.d\.\s*|\bsampai\s*)?(?:triwulan|tw)?\s*(?:iv|4|keempat)\b", tw_lower):
        return date(y, 12, 31)
    if re.search(r"(?:triwulan|tw)?\s*(?:-\s*|\bs\.d\.\s*|\bsampai\s*)?(?:triwulan|tw)?\s*(?:iii|3|ketiga)\b", tw_lower):
        return date(y, 9, 30)
    if re.search(r"(?:triwulan|tw)?\s*(?:-\s*|\bs\.d\.\s*|\bsampai\s*)?(?:triwulan|tw)?\s*(?:ii|2|kedua)\b", tw_lower):
        return date(y, 6, 30)
    if re.search(r"(?:triwulan|tw)?\s*(?:i|1|pertama)\b", tw_lower):
        return date(y, 3, 31)

    # Cek nama bulan standalone (e.g. 'November 2026')
    for m_k, (m_val, max_d) in month_names.items():
        if re.search(rf"\b{m_k}\b", tw_lower):
            return date(y, m_val, max_d)

    return date(y, 12, 31)


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

    # 8. Peringatan Jatuh Tempo RTP (Akan Jatuh Tempo <= 30 hari & Lewat Jatuh Tempo)
    today = today_wib()
    items_akan_jatuh_tempo = []
    items_lewat_jatuh_tempo = []

    # Ambil status realisasi Form 7
    saved_realisasi = session.exec(
        select(RealisasiRtp).where(RealisasiRtp.risiko_id.in_(ids))
    ).all() if ids else []
    rel_map = {rel.risiko_id: rel for rel in saved_realisasi}

    for r in risiko:
        rt = rtp_map.get(r.id)
        if not rt or not (rt.rencana_tindak or "").strip():
            continue

        rel = rel_map.get(r.id)
        if rel and rel.status_realisasi == "selesai":
            # RTP sudah selesai dilaksanakan
            continue

        deadline = parse_deadline(rt.target_selesai, rt.target_mulai, rt.target_waktu, tahun)
        if not deadline:
            continue

        days_diff = (deadline - today).days

        item = {
            "id": r.id,
            "source_type": "risiko",
            "kode_risiko": r.kode_risiko or f"R-{r.id}",
            "uraian_risiko": r.uraian_risiko,
            "rencana_tindak": rt.rencana_tindak,
            "penanggung_jawab": rt.pemilik_penanggung_jawab or r.pemilik_risiko or "OPD",
            "target_waktu": rt.target_waktu or deadline.strftime("%d-%m-%Y"),
            "jatuh_tempo": deadline.isoformat(),
            "sisa_hari": days_diff,
            "status_realisasi": rel.status_realisasi if rel else "belum",
            "jenis_risiko": r.jenis_risiko,
            "jenis_label": JENIS_LABEL.get(r.jenis_risiko, r.jenis_risiko),
            "link": "/realisasi-rtp",
        }

        if days_diff < 0:
            items_lewat_jatuh_tempo.append(item)
        elif 0 <= days_diff <= 30:
            items_akan_jatuh_tempo.append(item)

    # Ambil status realisasi Form 6 (CEE)
    cee_rows = session.exec(
        select(RtpCee).where(RtpCee.opd_id == opd_id, RtpCee.tahun == tahun)
    ).all()
    cee_ids = [c.id for c in cee_rows]
    cee_real_records = session.exec(
        select(RealisasiRtp).where(RealisasiRtp.rtp_cee_id.in_(cee_ids))
    ).all() if cee_ids else []
    cee_rel_map = {rel.rtp_cee_id: rel for rel in cee_real_records}

    for c in cee_rows:
        if not (c.rencana_tindak or "").strip():
            continue

        rel = cee_rel_map.get(c.id)
        if rel and rel.status_realisasi == "selesai":
            continue

        deadline = parse_deadline(c.target_selesai, c.target_mulai, c.target_waktu, tahun)
        if not deadline:
            continue

        days_diff = (deadline - today).days

        item = {
            "id": f"cee-{c.id}",
            "source_type": "cee",
            "kode_risiko": f"CEE-{c.no_urut or c.id}",
            "uraian_risiko": c.kondisi_kerentanan or "Kelemahan Lingkungan Pengendalian",
            "rencana_tindak": c.rencana_tindak,
            "penanggung_jawab": c.pemilik_penanggung_jawab or "Pimpinan OPD",
            "target_waktu": c.target_waktu or deadline.strftime("%d-%m-%Y"),
            "jatuh_tempo": deadline.isoformat(),
            "sisa_hari": days_diff,
            "status_realisasi": rel.status_realisasi if rel else "belum",
            "jenis_risiko": "cee",
            "jenis_label": "RTP atas CEE",
            "link": "/realisasi-rtp",
        }

        if days_diff < 0:
            items_lewat_jatuh_tempo.append(item)
        elif 0 <= days_diff <= 30:
            items_akan_jatuh_tempo.append(item)

    items_lewat_jatuh_tempo.sort(key=lambda x: x["sisa_hari"])
    items_akan_jatuh_tempo.sort(key=lambda x: x["sisa_hari"])

    # 9. Rekomendasi Eksekutif (Smart Engine)
    rekomendasi = []

    # Peringatan Jatuh Tempo Prioritas Utama di Rekomendasi
    if items_lewat_jatuh_tempo:
        rekomendasi.append(
            {
                "severity": "kritis",
                "judul": f"{len(items_lewat_jatuh_tempo)} RTP Sudah Lewat Jatuh Tempo",
                "pesan": (
                    f"Terdapat {len(items_lewat_jatuh_tempo)} rencana tindak pengendalian yang telah melewati "
                    f"tenggat waktu target penyelesaian dan belum selesai terealisasi. Segera tindak lanjuti."
                ),
                "action_label": "Realisasi RTP",
                "action_link": "/realisasi-rtp",
            }
        )
    if items_akan_jatuh_tempo:
        rekomendasi.append(
            {
                "severity": "perhatian",
                "judul": f"{len(items_akan_jatuh_tempo)} RTP Akan Jatuh Tempo dalam 30 Hari",
                "pesan": (
                    f"Terdapat {len(items_akan_jatuh_tempo)} rencana tindak pengendalian yang mendekati "
                    f"batas waktu pelaksanaan dalam 30 hari ke depan. Pastikan aksi mitigasi segera dirampungkan."
                ),
                "action_label": "Realisasi RTP",
                "action_link": "/realisasi-rtp",
            }
        )

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
        "peringatan_rtp": {
            "akan_jatuh_tempo": items_akan_jatuh_tempo,
            "lewat_jatuh_tempo": items_lewat_jatuh_tempo,
            "total_akan_jatuh_tempo": len(items_akan_jatuh_tempo),
            "total_lewat_jatuh_tempo": len(items_lewat_jatuh_tempo),
        },
    }
