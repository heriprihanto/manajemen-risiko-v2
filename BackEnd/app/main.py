from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import OpdScopeDep, UserDep
from app.db import init_db
from app.routers import (
    auth,
    cee,
    dashboard,
    kamus,
    konteks,
    lapor_kejadian,
    laporan,
    master,
    monitoring,
    pengaturan,
    rekapitulasi,
    risiko,
    survei,
)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API = "/api"
# Auth: publik. Survei: publik (token undangan responden).
app.include_router(auth.router, prefix=API)
app.include_router(survei.router, prefix=API)
app.include_router(lapor_kejadian.router, prefix=API)
# Master/referensi/kamus: cukup terautentikasi.
app.include_router(master.router, prefix=API, dependencies=[UserDep])
app.include_router(kamus.router, prefix=API, dependencies=[UserDep])
# Pengaturan: baca cukup terautentikasi, tulis dijaga AdminDep di endpoint-nya.
app.include_router(pengaturan.router, prefix=API, dependencies=[UserDep])
# Data transaksi: terautentikasi + dibatasi per OPD (Admin bebas, OPD hanya miliknya).
scoped = [OpdScopeDep]
app.include_router(cee.router, prefix=API, dependencies=scoped)
app.include_router(konteks.router, prefix=API, dependencies=scoped)
app.include_router(risiko.router, prefix=API, dependencies=scoped)
app.include_router(monitoring.router, prefix=API, dependencies=scoped)
app.include_router(dashboard.router, prefix=API, dependencies=scoped)
app.include_router(laporan.router, prefix=API, dependencies=scoped)
app.include_router(rekapitulasi.router, prefix=API, dependencies=scoped)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "project": settings.PROJECT_NAME, "tahun": settings.TAHUN_ANGGARAN}


@app.get("/api/config")
def config() -> dict:
    return {
        "project_name": settings.PROJECT_NAME,
        "tahun_default": settings.TAHUN_ANGGARAN,
    }
