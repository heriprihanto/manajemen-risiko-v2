"""Teks RTP yang konsisten pada ekspor cetak."""
from app.schemas.rtp import STATUS_LABEL, RESPON_LABEL


def pengendalian_text(rtp):
    parts = [STATUS_LABEL.get(rtp.get("status_pengendalian"), ""), rtp.get("pengendalian_ada")]
    if rtp.get("bukti_judul"):
        parts.extend(["Bukti: " + rtp["bukti_judul"], rtp.get("bukti_link") or rtp.get("bukti_nama")])
    return "\n".join(p for p in parts if p)


def rencana_text(rtp):
    return "\n".join(p for p in [RESPON_LABEL.get(rtp.get("respon_risiko"), ""), rtp.get("rencana_tindak")] if p)
