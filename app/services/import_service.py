from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import Event, ImportRun
from app.services.events_service import ALLOWED_LEVELS, parse_ts

CSV_HEADER = ["timestamp", "source", "level", "message", "metric_value", "tag"]


async def import_csv_file(file: UploadFile, db: Session) -> dict[str, object]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv supported")

    run = ImportRun(
        started_at=datetime.now().astimezone(),
        filename=file.filename,
        inserted=0,
        skipped=0,
        errors=0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    content = await file.read()
    text = content.decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    actual_header = reader.fieldnames or []
    if actual_header != CSV_HEADER:
        raise HTTPException(
            status_code=400,
            detail=(
                "CSV header must be exactly: "
                + ",".join(CSV_HEADER)
            ),
        )

    inserted = 0
    skipped = 0
    errors = 0

    for row in reader:
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
        except (ValueError, KeyError):
            errors += 1

    run.inserted = inserted
    run.skipped = skipped
    run.errors = errors
    db.add(run)
    db.commit()

    return {
        "import_run_id": run.id,
        "filename": run.filename,
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors,
    }
