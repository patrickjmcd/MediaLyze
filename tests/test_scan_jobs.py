from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.models.entities import JobStatus, Library, LibraryType, ScanJob, ScanMode
from backend.app.services.scan_jobs import list_active_scan_jobs, serialize_scan_job


def test_serialize_scan_job_for_discovery_phase() -> None:
    job = ScanJob(
        id=1,
        library_id=2,
        status=JobStatus.running,
        job_type="incremental",
        files_total=0,
        files_scanned=0,
        errors=0,
        started_at=datetime.now(UTC),
        finished_at=None,
    )

    payload = serialize_scan_job(job)

    assert payload.phase_label == "Discovering files"
    assert payload.progress_percent == 0.0


def test_serialize_scan_job_for_analysis_phase() -> None:
    job = ScanJob(
        id=1,
        library_id=2,
        status=JobStatus.running,
        job_type="incremental",
        files_total=20,
        files_scanned=5,
        errors=0,
        started_at=datetime.now(UTC),
        finished_at=None,
    )

    payload = serialize_scan_job(job)

    assert payload.phase_label == "Analyzing media"
    assert payload.progress_percent == 25.0


def test_list_active_scan_jobs_deduplicates_per_library() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with session_factory() as db:
        library = Library(
            name="Movies",
            path="/tmp/movies",
            type=LibraryType.movies,
            scan_mode=ScanMode.manual,
            scan_config={},
        )
        db.add(library)
        db.flush()
        db.add_all(
            [
                ScanJob(
                    library_id=library.id,
                    status=JobStatus.running,
                    job_type="incremental",
                    files_total=100,
                    files_scanned=10,
                    errors=0,
                    started_at=datetime.now(UTC),
                ),
                ScanJob(
                    library_id=library.id,
                    status=JobStatus.queued,
                    job_type="full",
                    files_total=0,
                    files_scanned=0,
                    errors=0,
                ),
            ]
        )
        db.commit()

        jobs = list_active_scan_jobs(db)

    assert len(jobs) == 1
    assert jobs[0].library_name == "Movies"
