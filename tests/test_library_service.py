import os
import tempfile

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("CONFIG_PATH", tempfile.mkdtemp(prefix="medialyze-config-"))
os.environ.setdefault("MEDIA_ROOT", tempfile.mkdtemp(prefix="medialyze-media-"))

from backend.app.db.base import Base
from backend.app.models.entities import (
    Library,
    LibraryType,
    MediaFile,
    MediaFormat,
    ScanMode,
    ScanStatus,
    VideoStream,
)
from backend.app.schemas.library import LibraryUpdate
from backend.app.services.library_service import delete_library, normalize_scan_config
from backend.app.services.library_service import update_library_settings


def test_normalize_scan_config_for_manual_mode() -> None:
    assert normalize_scan_config(ScanMode.manual, {"interval_minutes": 1}) == {}


def test_normalize_scan_config_for_scheduled_mode_enforces_minimum() -> None:
    assert normalize_scan_config(ScanMode.scheduled, {"interval_minutes": 1}) == {
        "interval_minutes": 5
    }


def test_normalize_scan_config_for_watch_mode_enforces_minimum() -> None:
    assert normalize_scan_config(ScanMode.watch, {"debounce_seconds": 1}) == {
        "debounce_seconds": 3
    }


def test_delete_library_removes_related_media_rows() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys = ON;")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with session_factory() as db:
        library = Library(
            name="Movies",
            path="/tmp/movies",
            type=LibraryType.mixed,
            scan_mode=ScanMode.manual,
            scan_config={},
        )
        db.add(library)
        db.flush()

        media_file = MediaFile(
            library_id=library.id,
            relative_path="movie.mkv",
            filename="movie.mkv",
            extension="mkv",
            size_bytes=123,
            mtime=1.0,
            scan_status=ScanStatus.ready,
            quality_score=5,
        )
        db.add(media_file)
        db.flush()
        db.add(MediaFormat(media_file_id=media_file.id, container_format="matroska", duration=1.0, bit_rate=1, probe_score=1))
        db.add(VideoStream(media_file_id=media_file.id, stream_index=0, codec="h264", width=1920, height=1080))
        db.commit()

        deleted = delete_library(db, library.id)

        remaining_libraries = db.scalars(select(Library)).all()
        remaining_files = db.scalars(select(MediaFile)).all()

    assert deleted is True
    assert remaining_libraries == []
    assert remaining_files == []


def test_update_library_settings_can_rename_library() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys = ON;")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with session_factory() as db:
        library = Library(
            name="Movies",
            path="/tmp/movies",
            type=LibraryType.mixed,
            scan_mode=ScanMode.manual,
            scan_config={},
        )
        db.add(library)
        db.commit()

        updated = update_library_settings(db, library.id, LibraryUpdate(name="Films"))

        assert updated is not None
        assert updated.name == "Films"
