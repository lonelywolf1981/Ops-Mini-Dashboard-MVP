from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.import_service import import_csv_file, list_import_runs

router = APIRouter(tags=["import"])


@router.post("/import")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return await import_csv_file(file, db)


@router.get("/imports")
def imports_history(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    return list_import_runs(db, limit=limit, offset=offset)
