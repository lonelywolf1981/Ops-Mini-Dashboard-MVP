from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Event


def get_dashboard_payload(db: Session) -> dict[str, object]:
    total = db.scalar(select(func.count(Event.id))) or 0
    by_level_rows = db.execute(
        select(Event.level, func.count(Event.id)).group_by(Event.level)
    ).all()
    by_level = {level: count for level, count in by_level_rows}

    unique_sources = db.scalar(select(func.count(func.distinct(Event.source)))) or 0

    by_day_rows = db.execute(
        select(func.strftime("%Y-%m-%d", Event.timestamp).label("day"), func.count(Event.id))
        .group_by("day")
        .order_by("day")
    ).all()
    by_day = [{"day": day, "count": count} for day, count in by_day_rows]

    latest_rows = db.execute(
        select(
            Event.timestamp,
            Event.source,
            Event.level,
            Event.message,
            Event.metric_value,
            Event.tag,
        )
        .order_by(Event.timestamp.desc())
        .limit(20)
    ).all()

    latest = [
        {
            "timestamp": timestamp.isoformat(),
            "source": source,
            "level": level,
            "message": message,
            "metric_value": metric_value,
            "tag": tag,
        }
        for timestamp, source, level, message, metric_value, tag in latest_rows
    ]

    return {
        "total": total,
        "by_level": by_level,
        "unique_sources": unique_sources,
        "by_day": by_day,
        "latest": latest,
    }


def get_top_sources_payload(
    db: Session,
    *,
    limit: int,
) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}

    for level in ("ERROR", "WARN"):
        rows = db.execute(
            select(Event.source, func.count(Event.id).label("count"))
            .where(Event.level == level)
            .group_by(Event.source)
            .order_by(func.count(Event.id).desc(), Event.source.asc())
            .limit(limit)
        ).all()

        result[level] = [{"source": source, "count": count} for source, count in rows]

    return result
