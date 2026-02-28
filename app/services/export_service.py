from __future__ import annotations

import csv
import io
from collections.abc import Iterator

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Event
from app.services.events_service import build_event_filters

EXPORT_HEADER = ["timestamp", "source", "level", "message", "metric_value", "tag"]


def export_events_csv_rows(
    db: Session,
    *,
    level: str | None,
    source: str | None,
    q: str | None,
    start: str | None,
    end: str | None,
) -> Iterator[str]:
    filters = build_event_filters(level=level, source=source, q=q, start=start, end=end)
    stmt = (
        select(Event.timestamp, Event.source, Event.level, Event.message, Event.metric_value, Event.tag)
        .order_by(Event.timestamp.desc())
        .limit(5000)
    )
    if filters:
        stmt = stmt.where(and_(*filters))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(EXPORT_HEADER)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    for row in db.execute(stmt):
        writer.writerow(
            [
                row[0].isoformat(),
                row[1],
                row[2],
                row[3],
                "" if row[4] is None else row[4],
                "" if row[5] is None else row[5],
            ]
        )
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)
