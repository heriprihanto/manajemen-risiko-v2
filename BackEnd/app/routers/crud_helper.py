"""Factory CRUD generik untuk tabel transaksi sederhana yang difilter per OPD & tahun."""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlmodel import Session, SQLModel, select

from app.core.datetime_utils import now_wib
from app.core.security import UserDep, guard_record
from app.db import get_session


def _apply(obj: SQLModel, data: dict[str, Any]) -> None:
    fields = type(obj).model_fields
    for key, value in data.items():
        if key in fields and key not in ("id", "created_at"):
            setattr(obj, key, value)
    if "updated_at" in fields:
        obj.updated_at = now_wib()


def make_opd_tahun_router(
    *,
    model: type[SQLModel],
    prefix: str,
    tag: str,
    order_by: str | None = "id",
) -> APIRouter:
    """Buat router list/create/update/delete untuk model dengan kolom opd_id & tahun."""
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("")
    def list_items(
        opd_id: int, tahun: int, session: Session = Depends(get_session)
    ):
        stmt = select(model).where(model.opd_id == opd_id, model.tahun == tahun)
        if order_by:
            stmt = stmt.order_by(getattr(model, order_by))
        return session.exec(stmt).all()

    @router.post("")
    def create_item(
        payload: dict[str, Any] = Body(...),
        session: Session = Depends(get_session),
    ):
        obj = model()
        _apply(obj, payload)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @router.put("/{item_id}")
    def update_item(
        item_id: int,
        payload: dict[str, Any] = Body(...),
        session: Session = Depends(get_session),
        user: dict = UserDep,
    ):
        obj = guard_record(user, session.get(model, item_id))
        _apply(obj, payload)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @router.delete("/{item_id}")
    def delete_item(
        item_id: int,
        session: Session = Depends(get_session),
        user: dict = UserDep,
    ):
        obj = guard_record(user, session.get(model, item_id))
        session.delete(obj)
        session.commit()
        return {"ok": True}

    return router
