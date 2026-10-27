import os
from collections.abc import Generator

os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models import approval as _approval_models  # noqa: F401
from app.models import run as _run_models  # noqa: F401
from app.models import workflow as _workflow_models  # noqa: F401
from app.models import workspace as _workspace_models  # noqa: F401


@pytest.fixture
def db_sessionmaker() -> Generator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    try:
        yield testing_session_local
    finally:
        Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_sessionmaker: sessionmaker[Session]) -> Generator[Session]:
    session = db_sessionmaker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(
    db_session: Session, db_sessionmaker: sessionmaker[Session], monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # The Celery task opens its own session (mirroring the real worker process);
    # eager mode makes it run in-process, so point it at the same test database.
    monkeypatch.setattr("app.workers.tasks.SessionLocal", db_sessionmaker)

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
