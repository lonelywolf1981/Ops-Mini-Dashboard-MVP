from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.dashboard_service import get_dashboard_payload, get_top_sources_payload

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)) -> dict[str, object]:
    return get_dashboard_payload(db)


@router.get("/dashboard/top-sources")
def top_sources(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, object]]]:
    return get_top_sources_payload(db, limit=limit)
