"""Script pembaruan skala_risiko dan is_prioritas pada tr_analisis_risiko
berdasarkan Matriks Analisis Risiko 5x5 standar baru.
"""
from sqlmodel import select
from app.db import get_session
from app.models.risiko import AnalisisRisiko
from app.services import analisis as an


def recalculate():
    with next(get_session()) as session:
        rows = session.exec(select(AnalisisRisiko)).all()
        updated_count = 0
        for r in rows:
            if r.skala_dampak is not None and r.skala_kemungkinan is not None:
                new_skala = an.hitung_skala(r.skala_dampak, r.skala_kemungkinan)
                old_skala = r.skala_risiko
                if new_skala != old_skala:
                    print(f"Update ID {r.id}: D={r.skala_dampak}, K={r.skala_kemungkinan}, old={old_skala} -> new={new_skala}")
                    r.skala_risiko = new_skala
                    # jika is_prioritas belum diubah manual, update default
                    r.is_prioritas = an.is_prioritas_default(new_skala)
                    session.add(r)
                    updated_count += 1
                else:
                    print(f"ID {r.id}: D={r.skala_dampak}, K={r.skala_kemungkinan}, skala={new_skala} (tetap)")
        if updated_count > 0:
            session.commit()
            print(f"Berhasil memperbarui {updated_count} baris AnalisisRisiko.")
        else:
            print("Semua baris AnalisisRisiko sudah sesuai dengan matriks baru.")


if __name__ == "__main__":
    recalculate()
