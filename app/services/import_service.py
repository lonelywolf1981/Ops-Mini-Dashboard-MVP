from __future__ import annotations

import csv
import io
import json
import logging
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, ImportRun
from app.services.events_service import ALLOWED_LEVELS, parse_ts

logger = logging.getLogger(__name__)

CSV_HEADER = ["timestamp", "source", "level", "message", "metric_value", "tag"]

# 10 MB — достаточно для CSV/JSON с десятками тысяч строк
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


# ---------------------------------------------------------------------------
# Внутренние парсеры — возвращают итерируемое dict-строк или бросают HTTPException
# ---------------------------------------------------------------------------

def _parse_csv(text: str) -> csv.DictReader:
    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    actual_header = list(reader.fieldnames or [])
    if actual_header != CSV_HEADER:
        raise HTTPException(
            status_code=400,
            detail="CSV header must be exactly: " + ",".join(CSV_HEADER),
        )
    return reader


def _parse_json(text: str) -> list[Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise HTTPException(
            status_code=400,
            detail="JSON must be a list of event objects",
        )
    return data


# ---------------------------------------------------------------------------
# Общая обработка строк (работает и для CSV-dict, и для JSON-dict)
# ---------------------------------------------------------------------------

def _process_event_rows(
    rows: Iterable[Any],
    safe_filename: str,
    run_id: int,
    db: Session,
) -> tuple[int, int, int]:
    inserted = skipped = errors = 0

    for line_num, row in enumerate(rows, start=2):
        try:
            if not isinstance(row, dict):
                logger.warning("Import %s, row %d: expected object, got %s", safe_filename, line_num, type(row).__name__)
                errors += 1
                continue

            timestamp = parse_ts(str(row.get("timestamp") or ""))
            source = str(row.get("source") or "").strip()
            level = str(row.get("level") or "").strip().upper()
            message = str(row.get("message") or "").strip()

            if not (source and level and message):
                skipped += 1
                continue

            if level not in ALLOWED_LEVELS:
                skipped += 1
                continue

            # metric_value: строка в CSV, число/null в JSON
            raw_metric = row.get("metric_value")
            if raw_metric is None or raw_metric == "":
                metric_value = None
            elif isinstance(raw_metric, (int, float)):
                metric_value = float(raw_metric)
            else:
                metric_value = float(str(raw_metric).strip())

            raw_tag = row.get("tag")
            tag = str(raw_tag).strip() if raw_tag not in (None, "") else None

            db.add(
                Event(
                    timestamp=timestamp,
                    source=source,
                    level=level,
                    message=message,
                    metric_value=metric_value,
                    tag=tag,
                    import_run_id=run_id,
                )
            )
            inserted += 1

        except KeyError as exc:
            logger.warning("Import %s, row %d: missing field %s", safe_filename, line_num, exc)
            errors += 1
        except ValueError as exc:
            logger.warning("Import %s, row %d: parse error: %s", safe_filename, line_num, exc)
            errors += 1

    return inserted, skipped, errors


# ---------------------------------------------------------------------------
# Публичный интерфейс
# ---------------------------------------------------------------------------

async def import_file(file: UploadFile, db: Session) -> dict[str, object]:
    """Принимает .csv или .json, валидирует и записывает события в БД."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    safe_filename = Path(file.filename).name
    lower = safe_filename.lower()

    if not (lower.endswith(".csv") or lower.endswith(".json")):
        raise HTTPException(status_code=400, detail="Only .csv and .json supported")

    content = await file.read()

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )

    text = content.decode("utf-8", errors="replace")

    rows: Iterable[Any] = _parse_csv(text) if lower.endswith(".csv") else _parse_json(text)

    run = ImportRun(
        started_at=datetime.now().astimezone(),
        filename=safe_filename,
        inserted=0,
        skipped=0,
        errors=0,
    )
    db.add(run)
    db.flush()

    inserted, skipped, errors = _process_event_rows(rows, safe_filename, run.id, db)

    run.inserted = inserted
    run.skipped = skipped
    run.errors = errors

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Database error during import of '%s'", safe_filename)
        raise HTTPException(status_code=500, detail="Database error during import")

    logger.info(
        "Import '%s' completed: inserted=%d skipped=%d errors=%d",
        safe_filename, inserted, skipped, errors,
    )

    return {
        "import_run_id": run.id,
        "filename": run.filename,
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors,
    }


def list_import_runs(
    db: Session,
    *,
    limit: int,
    offset: int,
) -> list[dict[str, object]]:
    stmt = (
        select(ImportRun)
        .order_by(ImportRun.started_at.desc(), ImportRun.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(stmt).all()

    return [
        {
            "id": run.id,
            "started_at": run.started_at.isoformat(),
            "filename": run.filename,
            "inserted": run.inserted,
            "skipped": run.skipped,
            "errors": run.errors,
        }
        for run in rows
    ]
