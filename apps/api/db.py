from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .settings import settings


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    external_id: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def record_to_dict(row: Record) -> dict[str, object]:
    return {
        "id": row.id,
        "kind": row.kind,
        "external_id": row.external_id,
        "title": row.title,
        "body": row.body,
        "data": row.data,
        "created_at": row.created_at.isoformat(),
    }


def save_record(
    kind: str,
    external_id: str,
    *,
    title: str = "",
    body: str = "",
    data: dict[str, object] | None = None,
) -> dict[str, object]:
    with SessionLocal() as db:
        row = Record(
            kind=kind,
            external_id=external_id,
            title=title,
            body=body,
            data=data or {},
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return record_to_dict(row)


def get_record(kind: str, external_id: str) -> dict[str, object] | None:
    with SessionLocal() as db:
        row = db.scalar(
            select(Record)
            .where(Record.kind == kind, Record.external_id == external_id)
            .order_by(Record.id.desc())
        )
        return record_to_dict(row) if row else None


def list_record_dicts(kind: str) -> list[dict[str, object]]:
    with SessionLocal() as db:
        rows = db.scalars(
            select(Record).where(Record.kind == kind).order_by(Record.id.desc())
        ).all()
        return [record_to_dict(row) for row in rows]


def list_all_record_dicts() -> list[dict[str, object]]:
    with SessionLocal() as db:
        rows = db.scalars(select(Record).order_by(Record.id.asc())).all()
        return [record_to_dict(row) for row in rows]


def count_by_kind() -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in list_all_record_dicts():
        kind = str(row["kind"])
        counts[kind] = counts.get(kind, 0) + 1
    return counts
