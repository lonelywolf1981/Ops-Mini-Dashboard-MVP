from __future__ import annotations

import csv
import io
import logging
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, ImportRun
from app.services.events_service import ALLOWED_LEVELS, parse_ts

logger = logging.getLogger(__name__)

CSV_HEADER = ["timestamp", "source", "level", "message", "metric_value", "tag"]

# 10 MB — достаточно для CSV с десятками тысяч строк
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


async def import_csv_file(file: UploadFile, db: Session) -> dict[str, object]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv supported")

    # Защита от path traversal в имени файла
    safe_filename = Path(file.filename).name

    content = await file.read()

    # Защита от DoS через большой файл
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )

    text = content.decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    actual_header = list(reader.fieldnames or [])
    if actual_header != CSV_HEADER:
        raise HTTPException(
            status_code=400,
            detail=(
                "CSV header must be exactly: "
                + ",".join(CSV_HEADER)
            ),
        )

    run = ImportRun(
        started_at=datetime.now().astimezone(),
        filename=safe_filename,
        inserted=0,
        skipped=0,
        errors=0,
    )
    db.add(run)
    # flush даёт run.id без коммита — транзакция остаётся открытой
    db.flush()

    inserted = 0
    skipped = 0
    errors = 0

    # enumerate с start=2: строка 1 — заголовок, данные с 2
    for line_num, row in enumerate(reader, start=2):
        try:
            timestamp = parse_ts(row["timestamp"])
            source = (row["source"] or "").strip()
            level = (row["level"] or "").strip().upper()
            message = (row["message"] or "").strip()

            if not (source and level and message):
                skipped += 1
                continue

            if level not in ALLOWED_LEVELS:
                skipped += 1
                continue

            metric_raw = (row["metric_value"] or "").strip()
            metric_value = float(metric_raw) if metric_raw else None
            tag = (row["tag"] or "").strip() or None

            db.add(
                Event(
                    timestamp=timestamp,
                    source=source,
                    level=level,
                    message=message,
                    metric_value=metric_value,
                    tag=tag,
                    import_run_id=run.id,
                )
            )
            inserted += 1
        except KeyError as exc:
            logger.warning("Import %s, row %d: missing field %s", safe_filename, line_num, exc)
            errors += 1
        except ValueError as exc:
            logger.warning("Import %s, row %d: parse error: %s", safe_filename, line_num, exc)
            errors += 1

    run.inserted = inserted
    run.skipped = skipped
    run.errors = errors

    # Единственный коммит — ImportRun и все Event атомарно
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
