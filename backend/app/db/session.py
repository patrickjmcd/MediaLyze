from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import Settings, get_settings


def _sqlite_url(database_path: Path) -> str:
    return f"sqlite:///{database_path}"


def create_engine_for_settings(settings: Settings) -> Engine:
    engine = create_engine(
        _sqlite_url(settings.database_path),
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _configure_sqlite(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.close()

    return engine


SETTINGS = get_settings()
ENGINE = create_engine_for_settings(SETTINGS)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db(engine: Engine | None = None) -> None:
    from backend.app.db.base import Base
    from backend.app.models import entities  # noqa: F401

    active_engine = engine or ENGINE
    Base.metadata.create_all(active_engine)
    with active_engine.begin() as connection:
        connection.execute(text("PRAGMA optimize;"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

