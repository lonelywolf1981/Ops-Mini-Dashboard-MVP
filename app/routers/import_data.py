from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.import_service import import_csv_file

router = APIRouter(tags=["import"])


@router.post("/import")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return await import_csv_file(file, db)
