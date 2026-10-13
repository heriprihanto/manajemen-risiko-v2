from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH), env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "Manajemen Risiko"
    ENVIRONMENT: str = "local"

    # JWT auth (login sso_users)
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 jam

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "db_manajemen_risiko"

    TAHUN_ANGGARAN: int = 2026

    # Firebase (untuk verifikasi ID token survei publik via login Google)
    FIREBASE_PROJECT_ID: str = "manajemen-risiko-98127"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = Field(default="", validation_alias=AliasChoices("SMTP_USERNAME", "SMTP_USER"))
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = Field(default="", validation_alias=AliasChoices("SMTP_FROM", "EMAILS_FROM_EMAIL"))
    SMTP_STARTTLS: bool = Field(default=True, validation_alias=AliasChoices("SMTP_STARTTLS", "SMTP_TLS"))
    SMTP_SSL: bool = False
    # Diisi melalui BackEnd/.env atau environment deployment.
    WHATSAPP_GATEWAY_URL: str = ""
    WHATSAPP_DEVICE_ID: str = ""

    SURVEI_PUBLIC_URL: str = "http://localhost:5173/survei"

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
