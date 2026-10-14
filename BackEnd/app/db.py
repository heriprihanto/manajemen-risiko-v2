from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine, text

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)

# Kolom yang ditambahkan setelah tabel pertama kali dibuat. create_all tidak
# mengubah tabel yang sudah ada, jadi terapkan lewat ALTER idempotent.
_COLUMN_MIGRATIONS = (
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS target_mulai date",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS target_selesai date",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS status_pengendalian varchar",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS respon_risiko varchar",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS bukti_judul varchar",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS bukti_link varchar",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS bukti_berkas_id integer REFERENCES tr_rtp_bukti(id)",
    "ALTER TABLE tr_rtp_risiko ADD COLUMN IF NOT EXISTS bukti_nama varchar",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS kategori_jabatan varchar",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS whatsapp_invited_at timestamp",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS nip varchar",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS no_hp varchar",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS token_id varchar",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS invited_at timestamp",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS submitted_at timestamp",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_tr_cee_responden_token_id ON tr_cee_responden (token_id)",
    "ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS konteks_id integer",
    "ALTER TABLE tr_risiko ADD COLUMN IF NOT EXISTS konteks_sumber varchar",
    "ALTER TABLE tr_konteks_operasional_opd ADD COLUMN IF NOT EXISTS indikator_program varchar",
    "ALTER TABLE tr_konteks_operasional_opd ADD COLUMN IF NOT EXISTS ref_subkegiatan varchar",
    "ALTER TABLE tr_konteks_operasional_opd ADD COLUMN IF NOT EXISTS ref_indikator varchar",
    "ALTER TABLE tr_konteks_strategis_pemda ADD COLUMN IF NOT EXISTS prioritas_pembangunan varchar",
    "ALTER TABLE tr_cee_simpulan ADD COLUMN IF NOT EXISTS penjelasan text",
    "ALTER TABLE tr_cee_responden ADD COLUMN IF NOT EXISTS narasi text",
    "ALTER TABLE tr_pengaturan ADD COLUMN IF NOT EXISTS template_email_subject varchar",
    "ALTER TABLE tr_pengaturan ADD COLUMN IF NOT EXISTS template_email text",
    "ALTER TABLE tr_pengaturan ADD COLUMN IF NOT EXISTS template_wa text",
    "ALTER TABLE tr_infokom ADD COLUMN IF NOT EXISTS risiko_id integer REFERENCES tr_risiko(id)",
    "ALTER TABLE tr_infokom ADD COLUMN IF NOT EXISTS rencana_mulai date",
    "ALTER TABLE tr_infokom ADD COLUMN IF NOT EXISTS rencana_selesai date",
    "ALTER TABLE tr_monitoring_pi ADD COLUMN IF NOT EXISTS risiko_id integer REFERENCES tr_risiko(id)",
    "ALTER TABLE tr_monitoring_pi ADD COLUMN IF NOT EXISTS rencana_mulai date",
    "ALTER TABLE tr_monitoring_pi ADD COLUMN IF NOT EXISTS rencana_selesai date",
)


def init_db() -> None:
    # Import models so SQLModel metadata is populated before create_all.
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    with engine.begin() as conn:
        for stmt in _COLUMN_MIGRATIONS:
            conn.execute(text(stmt))


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
