"""Layanan agregasi Laporan Rekapitulasi Manajemen Risiko:
1. Rekapitulasi Kuesioner (nilai jawaban dan persentase per OPD)
   Format: No | Nama OPD | Jumlah Responden | Modus | Simpulan
2. Rekapitulasi Konteks Risiko
   Format: No | Nama OPD | Jumlah Konteks Risiko Strategis OPD | Jumlah Konteks Risiko Operasional OPD
3. Rekapitulasi Identifikasi Risiko
   Format: No | Nama OPD | Kategori Risiko | Strategis OPD | Operasional OPD
4. Rekapitulasi Identifikasi Risiko (Level Risiko)
   Format: No | Nama OPD | Level Risiko
"""
from app.services import selera
from typing import Any
from sqlmodel import Session, func, select

from app.models import (
    AnalisisRisiko,
    CeeJawaban,
    CeeResponden,
    Infokom,
    KonteksOperasionalOpd,
    KonteksStrategisOpd,
    MonitoringPi,
    MonitoringRiskEvent,
    Opd,
    Risiko,
    RtpRisiko,
)
from app.services import cee as cee_svc
from app.services.analisis import (
    LEVEL_RENDAH,
    LEVEL_SANGAT_RENDAH,
    LEVEL_SANGAT_TINGGI,
    LEVEL_SEDANG,
    LEVEL_TINGGI,
    level_risiko,
)


def _clean_opd_id(val: Any) -> int | None:
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    return None


def get_all_opds(session: Session, opd_id: int | None = None) -> list[Opd]:
    opd_id = _clean_opd_id(opd_id)
    stmt = select(Opd).where(Opd.aktif == 1)
    if opd_id:
        stmt = stmt.where(Opd.id_sub_pd == opd_id)
    return session.exec(stmt.order_by(Opd.kode)).all()


def get_rekap_kuesioner(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """Rekapitulasi Kuesioner CEE per OPD."""
    opds = get_all_opds(session, opd_id)
    opd_ids = [o.id_sub_pd for o in opds]

    # Hitung jumlah responden per OPD
    resp_stmt = (
        select(CeeResponden.opd_id, func.count(CeeResponden.id))
        .where(CeeResponden.tahun == tahun)
    )
    if opd_id:
        resp_stmt = resp_stmt.where(CeeResponden.opd_id == opd_id)
    resp_counts = dict(session.exec(resp_stmt.group_by(CeeResponden.opd_id)).all())

    # Agregasi jawaban (nilai 1..4) per OPD via JOIN CeeResponden
    ans_stmt = (
        select(CeeResponden.opd_id, CeeJawaban.nilai, func.count(CeeJawaban.id))
        .join(CeeResponden, CeeResponden.id == CeeJawaban.responden_id)
        .where(CeeResponden.tahun == tahun)
    )
    if opd_id:
        ans_stmt = ans_stmt.where(CeeResponden.opd_id == opd_id)
    ans_rows = session.exec(
        ans_stmt.group_by(CeeResponden.opd_id, CeeJawaban.nilai)
    ).all()

    # Susun per-OPD jawaban map: { opd_id: { 1: c1, 2: c2, 3: c3, 4: c4 } }
    ans_map: dict[int, dict[int, int]] = {}
    for oid, val, cnt in ans_rows:
        if val in (1, 2, 3, 4):
            ans_map.setdefault(oid, {})[val] = cnt

    items = []
    tot_resp = 0
    tot_jawaban = 0
    tot_vals = {1: 0, 2: 0, 3: 0, 4: 0}

    for idx, o in enumerate(opds, start=1):
        c_resp = resp_counts.get(o.id_sub_pd, 0)
        c_vals = ans_map.get(o.id_sub_pd, {})
        v1 = c_vals.get(1, 0)
        v2 = c_vals.get(2, 0)
        v3 = c_vals.get(3, 0)
        v4 = c_vals.get(4, 0)
        t_jawab = v1 + v2 + v3 + v4

        # Hitung modus jawaban: nilai paling banyak muncul (bila seri, ambil nilai tertinggi)
        all_vals_list = []
        for val in (1, 2, 3, 4):
            all_vals_list.extend([val] * c_vals.get(val, 0))
        md = cee_svc.modus(all_vals_list)
        simp = cee_svc.predikat_dari_nilai(md) if md is not None else "-"

        p1 = round(v1 / t_jawab * 100, 1) if t_jawab else 0.0
        p2 = round(v2 / t_jawab * 100, 1) if t_jawab else 0.0
        p3 = round(v3 / t_jawab * 100, 1) if t_jawab else 0.0
        p4 = round(v4 / t_jawab * 100, 1) if t_jawab else 0.0

        tot_resp += c_resp
        tot_jawaban += t_jawab
        tot_vals[1] += v1
        tot_vals[2] += v2
        tot_vals[3] += v3
        tot_vals[4] += v4

        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": o.nama_pd or o.nama_pd_singkat or "-",
                "jumlah_responden": c_resp,
                "total_jawaban": t_jawab,
                "nilai_1": v1,
                "persen_1": p1,
                "nilai_2": v2,
                "persen_2": p2,
                "nilai_3": v3,
                "persen_3": p3,
                "nilai_4": v4,
                "persen_4": p4,
                "modus": md,
                "simpulan": simp or "-",
            }
        )

    # Modus gabungan seluruh daerah
    all_daerah_vals = []
    for val in (1, 2, 3, 4):
        all_daerah_vals.extend([val] * tot_vals[val])
    md_total = cee_svc.modus(all_daerah_vals)
    simp_total = cee_svc.predikat_dari_nilai(md_total) if md_total is not None else "-"

    tot_p1 = round(tot_vals[1] / tot_jawaban * 100, 1) if tot_jawaban else 0.0
    tot_p2 = round(tot_vals[2] / tot_jawaban * 100, 1) if tot_jawaban else 0.0
    tot_p3 = round(tot_vals[3] / tot_jawaban * 100, 1) if tot_jawaban else 0.0
    tot_p4 = round(tot_vals[4] / tot_jawaban * 100, 1) if tot_jawaban else 0.0

    return {
        "tahun": tahun,
        "items": items,
        "summary": {
            "total_opd": len(opds),
            "opd_mengisi": sum(1 for it in items if it["jumlah_responden"] > 0),
            "total_responden": tot_resp,
            "total_jawaban": tot_jawaban,
            "nilai_1": tot_vals[1],
            "persen_1": tot_p1,
            "nilai_2": tot_vals[2],
            "persen_2": tot_p2,
            "nilai_3": tot_vals[3],
            "persen_3": tot_p3,
            "nilai_4": tot_vals[4],
            "persen_4": tot_p4,
            "modus": md_total,
            "simpulan": simp_total or "-",
        },
    }


def get_rekap_konteks(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """Rekapitulasi Konteks Risiko: Strategis OPD & Operasional OPD per OPD."""
    opds = get_all_opds(session, opd_id)

    # Hitung Konteks Strategis OPD (Form 2.b)
    ks_stmt = (
        select(KonteksStrategisOpd.opd_id, func.count(KonteksStrategisOpd.id))
        .where(KonteksStrategisOpd.tahun == tahun)
    )
    if opd_id:
        ks_stmt = ks_stmt.where(KonteksStrategisOpd.opd_id == opd_id)
    ks_map = dict(session.exec(ks_stmt.group_by(KonteksStrategisOpd.opd_id)).all())

    # Hitung Konteks Operasional OPD (Form 2.c)
    ko_stmt = (
        select(KonteksOperasionalOpd.opd_id, func.count(KonteksOperasionalOpd.id))
        .where(KonteksOperasionalOpd.tahun == tahun)
    )
    if opd_id:
        ko_stmt = ko_stmt.where(KonteksOperasionalOpd.opd_id == opd_id)
    ko_map = dict(session.exec(ko_stmt.group_by(KonteksOperasionalOpd.opd_id)).all())

    items = []
    tot_strat = 0
    tot_oper = 0

    for idx, o in enumerate(opds, start=1):
        c_strat = ks_map.get(o.id_sub_pd, 0)
        c_oper = ko_map.get(o.id_sub_pd, 0)
        tot = c_strat + c_oper
        tot_strat += c_strat
        tot_oper += c_oper

        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": o.nama_pd or o.nama_pd_singkat or "-",
                "jumlah_strategis_opd": c_strat,
                "jumlah_operasional_opd": c_oper,
                "total_konteks": tot,
            }
        )

    return {
        "tahun": tahun,
        "items": items,
        "summary": {
            "total_opd": len(opds),
            "opd_mengisi": sum(1 for it in items if it["total_konteks"] > 0),
            "total_strategis_opd": tot_strat,
            "total_operasional_opd": tot_oper,
            "grand_total": tot_strat + tot_oper,
        },
    }


def get_rekap_identifikasi(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """Rekapitulasi Identifikasi Risiko: Kategori Risiko, Strategis OPD, Operasional OPD."""
    opds = get_all_opds(session, opd_id)

    # Ambil seluruh risiko untuk tahun yang dipilih
    risk_stmt = select(Risiko).where(
        Risiko.tahun == tahun,
        Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
    )
    if opd_id:
        risk_stmt = risk_stmt.where(Risiko.opd_id == opd_id)
    risiko_list = session.exec(risk_stmt).all()

    # Strukturkan per opd_id -> kategori_risiko -> { strategis: 0, operasional: 0 }
    opd_risk_map: dict[int, dict[str, dict[str, int]]] = {}
    global_cat_map: dict[str, dict[str, int]] = {}

    for r in risiko_list:
        cat = (r.kategori_risiko or "").strip() or "Lainnya / Belum Ditentukan"
        omap = opd_risk_map.setdefault(r.opd_id, {})
        cdata = omap.setdefault(cat, {"strategis_opd": 0, "operasional_opd": 0})
        gdata = global_cat_map.setdefault(
            cat, {"strategis_opd": 0, "operasional_opd": 0}
        )

        if r.jenis_risiko == "strategis_opd":
            cdata["strategis_opd"] += 1
            gdata["strategis_opd"] += 1
        elif r.jenis_risiko == "operasional_opd":
            cdata["operasional_opd"] += 1
            gdata["operasional_opd"] += 1

    items = []
    flattened_rows = []
    tot_strat = 0
    tot_oper = 0

    for idx, o in enumerate(opds, start=1):
        cats = opd_risk_map.get(o.id_sub_pd, {})
        nama_opd = o.nama_pd or o.nama_pd_singkat or "-"

        cat_items = []
        opd_strat = 0
        opd_oper = 0

        # Jika ada kategori pada OPD ini
        sorted_cat_keys = sorted(cats.keys())
        if sorted_cat_keys:
            for ckey in sorted_cat_keys:
                s_val = cats[ckey]["strategis_opd"]
                o_val = cats[ckey]["operasional_opd"]
                t_val = s_val + o_val
                opd_strat += s_val
                opd_oper += o_val
                cat_items.append(
                    {
                        "kategori_risiko": ckey,
                        "strategis_opd": s_val,
                        "operasional_opd": o_val,
                        "total": t_val,
                    }
                )
        else:
            cat_items.append(
                {
                    "kategori_risiko": "-",
                    "strategis_opd": 0,
                    "operasional_opd": 0,
                    "total": 0,
                }
            )

        opd_total = opd_strat + opd_oper
        tot_strat += opd_strat
        tot_oper += opd_oper

        # Buat flattened rows untuk tabel HTML / Excel yang menggunakan rowspan
        row_count = len(cat_items)
        for r_idx, c_it in enumerate(cat_items):
            flattened_rows.append(
                {
                    "no": idx if r_idx == 0 else None,
                    "rowspan": row_count if r_idx == 0 else 0,
                    "opd_id": o.id_sub_pd,
                    "nama_opd": nama_opd,
                    "kategori_risiko": c_it["kategori_risiko"],
                    "strategis_opd": c_it["strategis_opd"],
                    "operasional_opd": c_it["operasional_opd"],
                    "total": c_it["total"],
                    "is_first": r_idx == 0,
                    "is_last": r_idx == row_count - 1,
                    "subtotal_strategis": opd_strat,
                    "subtotal_operasional": opd_oper,
                    "subtotal_total": opd_total,
                }
            )

        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": nama_opd,
                "kategori_list": cat_items,
                "subtotal_strategis": opd_strat,
                "subtotal_operasional": opd_oper,
                "total_risiko": opd_total,
            }
        )

    # Ringkasan per kategori di seluruh daerah
    summary_categories = [
        {
            "kategori_risiko": c,
            "strategis_opd": data["strategis_opd"],
            "operasional_opd": data["operasional_opd"],
            "total": data["strategis_opd"] + data["operasional_opd"],
        }
        for c, data in sorted(
            global_cat_map.items(),
            key=lambda x: x[1]["strategis_opd"] + x[1]["operasional_opd"],
            reverse=True,
        )
    ]

    return {
        "tahun": tahun,
        "items": items,
        "rows": flattened_rows,
        "summary": {
            "total_opd": len(opds),
            "opd_mengisi": sum(1 for it in items if it["total_risiko"] > 0),
            "total_strategis_opd": tot_strat,
            "total_operasional_opd": tot_oper,
            "grand_total": tot_strat + tot_oper,
            "by_kategori": summary_categories,
        },
    }


def get_rekap_level_risiko(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """Rekapitulasi Level Risiko per OPD."""
    opds = get_all_opds(session, opd_id)

    # Ambil seluruh risiko untuk tahun yang dipilih
    risk_stmt = select(Risiko).where(
        Risiko.tahun == tahun,
        Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
    )
    if opd_id:
        risk_stmt = risk_stmt.where(Risiko.opd_id == opd_id)
    risiko_list = session.exec(risk_stmt).all()
    risk_ids = [r.id for r in risiko_list]

    amap: dict[int, AnalisisRisiko] = {}
    if risk_ids:
        for a in session.exec(
            select(AnalisisRisiko).where(AnalisisRisiko.risiko_id.in_(risk_ids))
        ).all():
            amap[a.risiko_id] = a

    # Kelompokkan level risiko per OPD
    LEVEL_KEYS = [
        "sangat_tinggi",
        "tinggi",
        "sedang",
        "rendah",
        "sangat_rendah",
        "belum_analisis",
    ]

    opd_level_map: dict[int, dict[str, int]] = {}
    for r in risiko_list:
        a = amap.get(r.id)
        omap = opd_level_map.setdefault(
            r.opd_id,
            {k: 0 for k in LEVEL_KEYS},
        )
        if a and a.skala_risiko is not None:
            lvl = level_risiko(a.skala_risiko)
            if lvl == LEVEL_SANGAT_TINGGI:
                omap["sangat_tinggi"] += 1
            elif lvl == LEVEL_TINGGI:
                omap["tinggi"] += 1
            elif lvl == LEVEL_SEDANG:
                omap["sedang"] += 1
            elif lvl == LEVEL_RENDAH:
                omap["rendah"] += 1
            elif lvl == LEVEL_SANGAT_RENDAH:
                omap["sangat_rendah"] += 1
            else:
                omap["belum_analisis"] += 1
        else:
            omap["belum_analisis"] += 1

    items = []
    flattened_rows = []
    tot_st = tot_t = tot_sd = tot_r = tot_sr = tot_ba = 0

    LEVEL_LABELS = [
        ("sangat_tinggi", "Sangat Tinggi (5)", "#ef4444"),
        ("tinggi", "Tinggi (4)", "#f97316"),
        ("sedang", "Sedang (3)", "#eab308"),
        ("rendah", "Rendah (2)", "#22c55e"),
        ("sangat_rendah", "Sangat Rendah (1)", "#15803d"),
        ("belum_analisis", "Belum Dianalisis", "#94a3b8"),
    ]

    for idx, o in enumerate(opds, start=1):
        omap = opd_level_map.get(o.id_sub_pd, {k: 0 for k in LEVEL_KEYS})
        st = omap["sangat_tinggi"]
        t = omap["tinggi"]
        sd = omap["sedang"]
        r = omap["rendah"]
        sr = omap["sangat_rendah"]
        ba = omap["belum_analisis"]
        tot_opd = st + t + sd + r + sr + ba

        tot_st += st
        tot_t += t
        tot_sd += sd
        tot_r += r
        tot_sr += sr
        tot_ba += ba

        nama_opd = o.nama_pd or o.nama_pd_singkat or "-"

        # Tambahkan item per OPD (tampilan matriks kolom)
        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": nama_opd,
                "sangat_tinggi": st,
                "tinggi": t,
                "sedang": sd,
                "rendah": r,
                "sangat_rendah": sr,
                "belum_analisis": ba,
                "total_risiko": tot_opd,
            }
        )

        # Tambahkan ke flattened_rows untuk opsi Tampilan Rincian Baris per Level
        level_items = []
        for key, lbl, color in LEVEL_LABELS:
            cnt = omap[key]
            if tot_opd > 0 and cnt > 0:
                persen = round(cnt / tot_opd * 100, 1)
                level_items.append(
                    {
                        "level_key": key,
                        "level_label": lbl,
                        "color": color,
                        "jumlah": cnt,
                        "persen": persen,
                    }
                )
        if not level_items:
            level_items.append(
                {
                    "level_key": "nihil",
                    "level_label": "Belum ada risiko",
                    "color": "#94a3b8",
                    "jumlah": 0,
                    "persen": 0.0,
                }
            )

        row_count = len(level_items)
        for r_idx, l_it in enumerate(level_items):
            flattened_rows.append(
                {
                    "no": idx if r_idx == 0 else None,
                    "rowspan": row_count if r_idx == 0 else 0,
                    "opd_id": o.id_sub_pd,
                    "nama_opd": nama_opd,
                    "level_key": l_it["level_key"],
                    "level_label": l_it["level_label"],
                    "color": l_it["color"],
                    "jumlah": l_it["jumlah"],
                    "persen": l_it["persen"],
                    "is_first": r_idx == 0,
                    "is_last": r_idx == row_count - 1,
                    "subtotal": tot_opd,
                }
            )

    grand_total = tot_st + tot_t + tot_sd + tot_r + tot_sr + tot_ba

    return {
        "tahun": tahun,
        "items": items,
        "rows": flattened_rows,
        "summary": {
            "total_opd": len(opds),
            "opd_mengisi": sum(1 for it in items if it["total_risiko"] > 0),
            "sangat_tinggi": tot_st,
            "tinggi": tot_t,
            "sedang": tot_sd,
            "rendah": tot_r,
            "sangat_rendah": tot_sr,
            "belum_analisis": tot_ba,
            "grand_total": grand_total,
        },
    }


def get_rekap_kepatuhan(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """5. Rekapitulasi Kepatuhan & Progres Pengisian OPD (6 Tahapan)."""
    opds = get_all_opds(session, opd_id)

    # 1. CEE (Form 1)
    cee_q = select(CeeResponden.opd_id, func.count(CeeResponden.id)).where(
        CeeResponden.tahun == tahun
    )
    if opd_id:
        cee_q = cee_q.where(CeeResponden.opd_id == opd_id)
    cee_map = dict(session.exec(cee_q.group_by(CeeResponden.opd_id)).all())

    # 2. Konteks (Form 2.b + Form 2.c)
    ks_q = select(KonteksStrategisOpd.opd_id, func.count(KonteksStrategisOpd.id)).where(
        KonteksStrategisOpd.tahun == tahun
    )
    ko_q = select(KonteksOperasionalOpd.opd_id, func.count(KonteksOperasionalOpd.id)).where(
        KonteksOperasionalOpd.tahun == tahun
    )
    if opd_id:
        ks_q = ks_q.where(KonteksStrategisOpd.opd_id == opd_id)
        ko_q = ko_q.where(KonteksOperasionalOpd.opd_id == opd_id)
    ks_map = dict(session.exec(ks_q.group_by(KonteksStrategisOpd.opd_id)).all())
    ko_map = dict(session.exec(ko_q.group_by(KonteksOperasionalOpd.opd_id)).all())

    # 3. Identifikasi Risiko (Form 3.b + Form 3.c)
    risk_q = select(Risiko.opd_id, func.count(Risiko.id)).where(
        Risiko.tahun == tahun,
        Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
    )
    if opd_id:
        risk_q = risk_q.where(Risiko.opd_id == opd_id)
    risk_map = dict(session.exec(risk_q.group_by(Risiko.opd_id)).all())

    # 4. Analisis Risiko (Form 4)
    an_q = (
        select(Risiko.opd_id, func.count(AnalisisRisiko.id))
        .join(AnalisisRisiko, AnalisisRisiko.risiko_id == Risiko.id)
        .where(
            Risiko.tahun == tahun,
            Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
        )
    )
    if opd_id:
        an_q = an_q.where(Risiko.opd_id == opd_id)
    an_map = dict(session.exec(an_q.group_by(Risiko.opd_id)).all())

    # 5. RTP atas Risiko (Form 7)
    rtp_q = (
        select(Risiko.opd_id, func.count(RtpRisiko.id))
        .join(RtpRisiko, RtpRisiko.risiko_id == Risiko.id)
        .where(
            Risiko.tahun == tahun,
            Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
        )
    )
    if opd_id:
        rtp_q = rtp_q.where(Risiko.opd_id == opd_id)
    rtp_map = dict(session.exec(rtp_q.group_by(Risiko.opd_id)).all())

    # 6. Pemantauan & Infokom (Form 8 & Form 9)
    info_q = select(Infokom.opd_id, func.count(Infokom.id)).where(
        Infokom.tahun == tahun
    )
    mon_q = select(MonitoringPi.opd_id, func.count(MonitoringPi.id)).where(
        MonitoringPi.tahun == tahun
    )
    if opd_id:
        info_q = info_q.where(Infokom.opd_id == opd_id)
        mon_q = mon_q.where(MonitoringPi.opd_id == opd_id)
    info_map = dict(session.exec(info_q.group_by(Infokom.opd_id)).all())
    mon_map = dict(session.exec(mon_q.group_by(MonitoringPi.opd_id)).all())

    items = []
    tot_lengkap = 0
    tot_sebagian = 0
    tot_belum = 0

    for idx, o in enumerate(opds, start=1):
        c_cee = cee_map.get(o.id_sub_pd, 0)
        c_konteks = ks_map.get(o.id_sub_pd, 0) + ko_map.get(o.id_sub_pd, 0)
        c_risk = risk_map.get(o.id_sub_pd, 0)
        c_an = an_map.get(o.id_sub_pd, 0)
        c_rtp = rtp_map.get(o.id_sub_pd, 0)
        c_pantau = info_map.get(o.id_sub_pd, 0) + mon_map.get(o.id_sub_pd, 0)

        # Hitung tahapan selesai dari total 6 tahapan
        stages = [
            c_cee > 0,
            c_konteks > 0,
            c_risk > 0,
            c_an > 0,
            c_rtp > 0,
            c_pantau > 0,
        ]
        selesai_count = sum(1 for s in stages if s)
        persen = round((selesai_count / 6) * 100, 1)

        if persen >= 100.0:
            status = "Lengkap"
            tot_lengkap += 1
        elif persen > 0.0:
            status = "Sebagian"
            tot_sebagian += 1
        else:
            status = "Belum Mengisi"
            tot_belum += 1

        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": o.nama_pd or o.nama_pd_singkat or "-",
                "cee_count": c_cee,
                "konteks_count": c_konteks,
                "identifikasi_count": c_risk,
                "analisis_count": c_an,
                "rtp_count": c_rtp,
                "pemantauan_count": c_pantau,
                "tahap_selesai": selesai_count,
                "total_tahap": 6,
                "persen_progres": persen,
                "status_kepatuhan": status,
            }
        )

    rata_progres = round(
        sum(it["persen_progres"] for it in items) / len(items), 1
    ) if items else 0.0

    return {
        "tahun": tahun,
        "items": items,
        "summary": {
            "total_opd": len(opds),
            "lengkap": tot_lengkap,
            "sebagian": tot_sebagian,
            "belum_mengisi": tot_belum,
            "rata_progres": rata_progres,
        },
    }


def get_rekap_realisasi_rtp(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """6. Rekapitulasi Realisasi RTP (Tingkat Tindak Lanjut Mitigasi Risiko)."""
    opds = get_all_opds(session, opd_id)

    # Ambil seluruh risiko OPD tahun terpilih
    risk_stmt = select(Risiko).where(
        Risiko.tahun == tahun,
        Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
    )
    if opd_id:
        risk_stmt = risk_stmt.where(Risiko.opd_id == opd_id)
    risiko_list = session.exec(risk_stmt).all()
    risk_ids = [r.id for r in risiko_list]

    # Map analisis untuk prioritas
    an_map: dict[int, AnalisisRisiko] = {}
    if risk_ids:
        for a in session.exec(
            select(AnalisisRisiko).where(AnalisisRisiko.risiko_id.in_(risk_ids))
        ).all():
            an_map[a.risiko_id] = a

    # Map RTP risiko
    rtp_map: dict[int, RtpRisiko] = {}
    if risk_ids:
        for r in session.exec(
            select(RtpRisiko).where(RtpRisiko.risiko_id.in_(risk_ids))
        ).all():
            rtp_map[r.risiko_id] = r

    # Kelompokkan per OPD
    opd_risks: dict[int, list[Risiko]] = {}
    for r in risiko_list:
        opd_risks.setdefault(r.opd_id, []).append(r)

    items = []
    tot_risiko = 0
    tot_prioritas = 0
    tot_target_rtp = 0
    tot_selesai = 0
    tot_proses = 0

    tot_opd_selesai = 0
    tot_opd_proses = 0
    tot_opd_belum = 0

    for idx, o in enumerate(opds, start=1):
        r_list = opd_risks.get(o.id_sub_pd, [])
        jml_risiko = len(r_list)
        jml_prio = 0
        jml_rtp = 0
        jml_selesai = 0

        aktif = selera.daftar_aktif(session, o.id_sub_pd, tahun)
        for r in r_list:
            a = an_map.get(r.id)
            is_prio = selera.status(a.skala_risiko if a else None, selera.resolve(aktif, r.pemilik_risiko))
            if is_prio:
                jml_prio += 1

            rt = rtp_map.get(r.id)
            if rt and (rt.rencana_tindak or "").strip():
                jml_rtp += 1
                # Realisasi dianggap selesai jika realisasi_waktu terisi dan bukan '-'
                rw = (rt.realisasi_waktu or "").strip()
                if rw and rw != "-":
                    jml_selesai += 1

        jml_proses = jml_rtp - jml_selesai
        persen = round((jml_selesai / jml_rtp * 100), 1) if jml_rtp > 0 else 0.0

        if jml_rtp == 0:
            status = "Nihil Target RTP" if jml_prio == 0 else "Belum Dibuat RTP"
        elif jml_selesai == jml_rtp:
            status = "Selesai 100%"
            tot_opd_selesai += 1
        elif jml_selesai > 0:
            status = "Dalam Proses"
            tot_opd_proses += 1
        else:
            status = "Belum Terealisasi"
            tot_opd_belum += 1

        tot_risiko += jml_risiko
        tot_prioritas += jml_prio
        tot_target_rtp += jml_rtp
        tot_selesai += jml_selesai
        tot_proses += jml_proses

        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": o.nama_pd or o.nama_pd_singkat or "-",
                "total_risiko": jml_risiko,
                "risiko_prioritas": jml_prio,
                "target_rtp": jml_rtp,
                "realisasi_selesai": jml_selesai,
                "dalam_proses": jml_proses,
                "tingkat_realisasi": persen,
                "status_tindak_lanjut": status,
            }
        )

    rata_realisasi = round(
        (tot_selesai / tot_target_rtp * 100), 1
    ) if tot_target_rtp > 0 else 0.0

    return {
        "tahun": tahun,
        "items": items,
        "summary": {
            "total_opd": len(opds),
            "total_risiko": tot_risiko,
            "total_prioritas": tot_prioritas,
            "total_target_rtp": tot_target_rtp,
            "total_realisasi_selesai": tot_selesai,
            "total_dalam_proses": tot_proses,
            "tingkat_realisasi_daerah": rata_realisasi,
            "opd_selesai": tot_opd_selesai,
            "opd_proses": tot_opd_proses,
            "opd_belum": tot_opd_belum,
        },
    }


def get_rekap_risk_event(
    session: Session, tahun: int, opd_id: int | None = None
) -> dict[str, Any]:
    """7. Rekapitulasi Keterjadian Risiko (Risk Event Log)."""
    opds = get_all_opds(session, opd_id)

    # Ambil risiko tahun terpilih
    risk_stmt = select(Risiko).where(
        Risiko.tahun == tahun,
        Risiko.jenis_risiko.in_(["strategis_opd", "operasional_opd"]),
    )
    if opd_id:
        risk_stmt = risk_stmt.where(Risiko.opd_id == opd_id)
    risiko_list = session.exec(risk_stmt).all()
    risk_ids = [r.id for r in risiko_list]

    # Ambil seluruh event untuk risiko-risiko tersebut
    events_by_risk: dict[int, list[MonitoringRiskEvent]] = {}
    if risk_ids:
        ev_stmt = select(MonitoringRiskEvent).where(
            MonitoringRiskEvent.risiko_id.in_(risk_ids)
        ).order_by(MonitoringRiskEvent.tanggal_terjadi)
        all_events = session.exec(ev_stmt).all()
        for e in all_events:
            events_by_risk.setdefault(e.risiko_id, []).append(e)

    # Kelompokkan per OPD
    opd_risks: dict[int, list[Risiko]] = {}
    for r in risiko_list:
        opd_risks.setdefault(r.opd_id, []).append(r)

    items = []
    log_rows = []
    tot_risiko_daerah = 0
    tot_risiko_terjadi = 0
    tot_events_daerah = 0
    opd_ada_kejadian = 0
    opd_nihil_kejadian = 0

    log_counter = 1

    for idx, o in enumerate(opds, start=1):
        r_list = opd_risks.get(o.id_sub_pd, [])
        jml_risiko = len(r_list)

        risiko_terkena = 0
        total_events = 0

        nama_opd = o.nama_pd or o.nama_pd_singkat or "-"

        for r in r_list:
            evs = events_by_risk.get(r.id, [])
            if evs:
                risiko_terkena += 1
                total_events += len(evs)
                for e in evs:
                    tgl_str = (
                        e.tanggal_terjadi.strftime("%d/%m/%Y")
                        if e.tanggal_terjadi
                        else "-"
                    )
                    log_rows.append(
                        {
                            "no": log_counter,
                            "opd_id": o.id_sub_pd,
                            "kode_opd": o.kode or "",
                            "nama_opd": nama_opd,
                            "kode_risiko": r.kode_risiko or "-",
                            "uraian_risiko": r.uraian_risiko or "-",
                            "tanggal_terjadi": tgl_str,
                            "sebab_kejadian": e.sebab_kejadian or "-",
                            "dampak_kejadian": e.dampak_kejadian or "-",
                            "rtp": e.rtp or "-",
                            "realisasi_rtp": e.realisasi_pelaksanaan_rtp or "-",
                            "keterangan": e.keterangan_rtp
                            or e.keterangan_kejadian
                            or "-",
                        }
                    )
                    log_counter += 1

        if total_events > 0:
            status = "Ada Kejadian"
            opd_ada_kejadian += 1
        else:
            status = "Nihil Kejadian"
            opd_nihil_kejadian += 1

        tot_risiko_daerah += jml_risiko
        tot_risiko_terjadi += risiko_terkena
        tot_events_daerah += total_events

        items.append(
            {
                "no": idx,
                "opd_id": o.id_sub_pd,
                "kode_opd": o.kode or "",
                "nama_opd": nama_opd,
                "total_risiko": jml_risiko,
                "risiko_terkena": risiko_terkena,
                "total_events": total_events,
                "status": status,
            }
        )

    return {
        "tahun": tahun,
        "items": items,
        "log_rows": log_rows,
        "summary": {
            "total_opd": len(opds),
            "total_risiko": tot_risiko_daerah,
            "total_risiko_terjadi": tot_risiko_terjadi,
            "total_events": tot_events_daerah,
            "opd_ada_kejadian": opd_ada_kejadian,
            "opd_nihil_kejadian": opd_nihil_kejadian,
        },
    }
