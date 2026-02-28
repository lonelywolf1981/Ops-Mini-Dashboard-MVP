from __future__ import annotations

from fastapi import FastAPI

from app.db import engine
from app.models import Base
from app.routers.dashboard import router as dashboard_router
from app.routers.events import router as events_router
from app.routers.import_data import router as import_router

app = FastAPI(title="Ops Mini Dashboard")

Base.metadata.create_all(bind=engine)

app.include_router(dashboard_router)
app.include_router(events_router)
app.include_router(import_router)
