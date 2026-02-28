from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Event

ALLOWED_LEVELS = {"INFO", "WARN", "ERROR"}


def parse_ts(value: str) -> datetime:
    raw_value = value.strip()
    try:
        parsed = datetime.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(f"bad timestamp: {value}") from exc

    if parsed.tzinfo is None:
        raise ValueError(f"bad timestamp: {value}")
    return parsed


def normalize_level(level: str | None) -> str | None:
    if level is None:
        return None

    normalized = level.strip().upper()
    if normalized not in ALLOWED_LEVELS:
        raise HTTPException(status_code=400, detail="level must be one of INFO,WARN,ERROR")
    return normalized


def build_event_filters(
    *,
    level: str | None,
    source: str | None,
    q: str | None,
    start: str | None,
    end: str | None,
) -> list:
    filters = []

    normalized_level = normalize_level(level)
    if normalized_level:
        filters.append(Event.level == normalized_level)

    if source:
        filters.append(Event.source == source)

    if q:
        filters.append(Event.message.contains(q))

    if start:
        try:
            filters.append(Event.timestamp >= parse_ts(start))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if end:
        try:
            filters.append(Event.timestamp <= parse_ts(end))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return filters


def get_distinct_sources(db: Session) -> list[str]:
    """Возвращает отсортированный список уникальных источников событий."""
    rows = db.execute(select(Event.source).distinct().order_by(Event.source.asc())).all()
    return [row[0] for row in rows]


def list_events_payload(
    db: Session,
    *,
    level: str | None,
    source: str | None,
    q: str | None,
    start: str | None,
    end: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, object]]:
    filters = build_event_filters(level=level, source=source, q=q, start=start, end=end)

    stmt = select(Event).order_by(Event.timestamp.desc()).limit(limit).offset(offset)
    if filters:
        stmt = stmt.where(and_(*filters))
    rows = db.scalars(stmt).all()

    return [
        {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "level": event.level,
            "message": event.message,
            "metric_value": event.metric_value,
            "tag": event.tag,
            "import_run_id": event.import_run_id,
        }
        for event in rows
    ]
