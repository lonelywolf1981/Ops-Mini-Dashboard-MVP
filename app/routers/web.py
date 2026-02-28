from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.dashboard_service import get_dashboard_payload, get_top_sources_payload
from app.services.events_service import get_distinct_sources, list_events_payload
from app.services.import_service import import_file, list_import_runs

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

router = APIRouter(tags=["web"])


def _normalize_datetime_input(value: str | None) -> str | None:
    if value is None:
        return None

    raw_value = value.strip()
    if not raw_value:
        return None

    try:
        parsed = datetime.fromisoformat(raw_value)
    except ValueError:
        return raw_value

    if parsed.tzinfo is None:
        return parsed.astimezone().isoformat(timespec="seconds")
    return parsed.isoformat(timespec="seconds")


def _to_datetime_local(value: str | None) -> str:
    if not value:
        return ""

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed.strftime("%Y-%m-%dT%H:%M")


def _build_query_string(params: dict[str, str | int | None]) -> str:
    filtered = {k: v for k, v in params.items() if v not in (None, "")}
    return urlencode(filtered)


def _build_events_context(
    db: Session,
    *,
    level: str | None,
    source: str | None,
    q: str | None,
    start: str | None,
    end: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    normalized_start = _normalize_datetime_input(start)
    normalized_end = _normalize_datetime_input(end)
    error_message: str | None = None

    try:
        # Запрашиваем limit+1, чтобы проверить наличие следующей страницы
        events = list_events_payload(
            db,
            level=level,
            source=source,
            q=q,
            start=normalized_start,
            end=normalized_end,
            limit=limit + 1,
            offset=offset,
        )
    except HTTPException as exc:
        events = []
        error_message = str(exc.detail)

    has_next = len(events) > limit
    events = events[:limit]

    sources = get_distinct_sources(db)

    base_params: dict[str, str | int | None] = {
        "level": level,
        "source": source,
        "q": q,
        "start": start,
        "end": end,
        "limit": limit,
    }
    export_params: dict[str, str | int | None] = {
        "level": level,
        "source": source,
        "q": q,
        "start": normalized_start,
        "end": normalized_end,
    }

    prev_url = None
    prev_table_url = None
    if offset > 0:
        prev_offset = max(0, offset - limit)
        prev_query = _build_query_string({**base_params, "offset": prev_offset})
        prev_url = "/ui/events?" + prev_query
        prev_table_url = "/ui/events/table?" + prev_query

    next_url = None
    next_table_url = None
    if has_next:
        next_query = _build_query_string({**base_params, "offset": offset + limit})
        next_url = "/ui/events?" + next_query
        next_table_url = "/ui/events/table?" + next_query

    export_query = _build_query_string(export_params)
    export_url = "/events/export.csv"
    if export_query:
        export_url += f"?{export_query}"

    return {
        "events": events,
        "sources": sources,
        "level": level or "",
        "source": source or "",
        "q": q or "",
        "start": _to_datetime_local(start),
        "end": _to_datetime_local(end),
        "limit": limit,
        "offset": offset,
        "prev_url": prev_url,
        "next_url": next_url,
        "prev_table_url": prev_table_url,
        "next_table_url": next_table_url,
        "export_url": export_url,
        "error_message": error_message,
    }


def _build_import_context(db: Session, *, limit: int, offset: int) -> dict[str, object]:
    # Запрашиваем limit+1, чтобы проверить наличие следующей страницы
    imports = list_import_runs(db, limit=limit + 1, offset=offset)

    has_next = len(imports) > limit
    imports = imports[:limit]

    prev_url = None
    if offset > 0:
        prev_offset = max(0, offset - limit)
        prev_url = "/ui/import?" + _build_query_string({"limit": limit, "offset": prev_offset})

    next_url = None
    if has_next:
        next_url = "/ui/import?" + _build_query_string({"limit": limit, "offset": offset + limit})

    return {
        "imports": imports,
        "limit": limit,
        "offset": offset,
        "prev_url": prev_url,
        "next_url": next_url,
    }


@router.get("/", include_in_schema=False)
def web_home() -> RedirectResponse:
    return RedirectResponse(url="/ui/dashboard", status_code=307)


@router.get("/ui/dashboard", response_class=HTMLResponse, include_in_schema=False)
def web_dashboard(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    dashboard = get_dashboard_payload(db)
    top_sources = get_top_sources_payload(db, limit=5)
    by_day_raw = dashboard.get("by_day")
    by_day: list[dict[str, object]] = []
    if isinstance(by_day_raw, list):
        by_day = [item for item in by_day_raw if isinstance(item, dict)]
    day_counts: list[int] = []
    for item in by_day:
        count_value = item.get("count")
        if isinstance(count_value, int):
            day_counts.append(count_value)
    day_max = max(day_counts, default=1)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "dashboard": dashboard,
            "top_sources": top_sources,
            "day_max": day_max,
        },
    )


@router.get("/ui/events", response_class=HTMLResponse, include_in_schema=False)
def web_events(
    request: Request,
    level: str | None = Query(default=None),
    source: str | None = Query(default=None),
    q: str | None = Query(default=None),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    context = _build_events_context(
        db,
        level=level,
        source=source,
        q=q,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )

    return templates.TemplateResponse(
        request,
        "events.html",
        context,
    )


@router.get("/ui/events/table", response_class=HTMLResponse, include_in_schema=False)
def web_events_table(
    request: Request,
    level: str | None = Query(default=None),
    source: str | None = Query(default=None),
    q: str | None = Query(default=None),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    context = _build_events_context(
        db,
        level=level,
        source=source,
        q=q,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )

    return templates.TemplateResponse(
        request,
        "events_table.html",
        context,
    )


@router.get("/ui/import", response_class=HTMLResponse, include_in_schema=False)
def web_import_page(
    request: Request,
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    context = _build_import_context(db, limit=limit, offset=offset)
    context.update({"result": None, "error_message": None})

    return templates.TemplateResponse(
        request,
        "import.html",
        context,
    )


@router.post("/ui/import", response_class=HTMLResponse, include_in_schema=False)
async def web_import_submit(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    result: dict[str, object] | None = None
    error_message: str | None = None

    try:
        result = await import_file(file, db)
    except HTTPException as exc:
        error_message = str(exc.detail)

    context = _build_import_context(db, limit=20, offset=0)
    context.update({"result": result, "error_message": error_message})

    return templates.TemplateResponse(
        request,
        "import.html",
        context,
    )
