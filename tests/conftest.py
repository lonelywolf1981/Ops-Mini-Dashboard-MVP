from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.dependencies import get_db
from app.main import app
from app.models import Base


@pytest.fixture()
def sample_csv() -> str:
    """Базовый CSV с тремя событиями (INFO, ERROR, WARN) для повторного использования в тестах."""
    return (
        "timestamp,source,level,message,metric_value,tag\n"
        "2026-02-28T21:06:00+05:00,sensor-temp-01,INFO,Temperature reading,3.125,temp\n"
        "2026-02-28T21:09:10+05:00,logger,ERROR,Write timeout while flushing chunk,,io\n"
        "2026-02-28T21:10:00+05:00,sensor-temp-01,WARN,Temperature drift above expected,3.450,temp\n"
    )


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    Base.metadata.create_all(bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
