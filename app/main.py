from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import engine
from app.models import Base
from app.routers.dashboard import router as dashboard_router
from app.routers.events import router as events_router
from app.routers.import_data import router as import_router
from app.routers.web import router as web_router

app = FastAPI(title="Ops Mini Dashboard")

Base.metadata.create_all(bind=engine)

app_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(app_dir / "static")), name="static")

app.include_router(dashboard_router)
app.include_router(events_router)
app.include_router(import_router)
app.include_router(web_router)
