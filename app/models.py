# app/models.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ImportRun(Base):
    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)

    inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    events: Mapped[list["Event"]] = relationship(back_populates="import_run")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    source: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(8), nullable=False, index=True)  # INFO/WARN/ERROR
    message: Mapped[str] = mapped_column(Text, nullable=False)

    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    tag: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    import_run_id: Mapped[int] = mapped_column(ForeignKey("import_runs.id"), nullable=False, index=True)
    import_run: Mapped["ImportRun"] = relationship(back_populates="events")