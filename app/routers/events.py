from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.events_service import list_events_payload
from app.services.export_service import export_events_csv_rows

router = APIRouter(tags=["events"])


@router.get("/events")
def list_events(
    level: str | None = Query(default=None, description="INFO/WARN/ERROR"),
    source: str | None = Query(default=None),
    q: str | None = Query(default=None, description="substring in message"),
    start: str | None = Query(default=None, description="ISO timestamp from"),
    end: str | None = Query(default=None, description="ISO timestamp to"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    return list_events_payload(
        db,
        level=level,
        source=source,
        q=q,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )


@router.get("/events/export.csv")
def export_events_csv(
    level: str | None = None,
    source: str | None = None,
    q: str | None = None,
    start: str | None = None,
    end: str | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    rows = export_events_csv_rows(
        db,
        level=level,
        source=source,
        q=q,
        start=start,
        end=end,
    )
    return StreamingResponse(rows, media_type="text/csv")
