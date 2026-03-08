from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.entities import JobStatus, ScanJob
from backend.app.schemas.scan import ScanJobRead


def serialize_scan_job(scan_job: ScanJob) -> ScanJobRead:
    files_total = scan_job.files_total or 0
    files_scanned = scan_job.files_scanned or 0
    progress_percent = 0.0
    if files_total > 0:
        progress_percent = min(100.0, round((files_scanned / files_total) * 100, 1))

    if scan_job.status == JobStatus.queued:
        phase_label = "Queued"
    elif files_total == 0 and scan_job.status == JobStatus.running:
        phase_label = "Discovering files"
    elif scan_job.status == JobStatus.running:
        phase_label = "Analyzing media"
    elif scan_job.status == JobStatus.completed:
        phase_label = "Completed"
    else:
        phase_label = "Failed"

    return ScanJobRead(
        id=scan_job.id,
        library_id=scan_job.library_id,
        library_name=scan_job.library.name if scan_job.library else None,
        status=scan_job.status,
        job_type=scan_job.job_type,
        files_total=files_total,
        files_scanned=files_scanned,
        errors=scan_job.errors,
        started_at=scan_job.started_at,
        finished_at=scan_job.finished_at,
        progress_percent=progress_percent,
        phase_label=phase_label,
    )


def list_active_scan_jobs(db: Session) -> list[ScanJobRead]:
    jobs = db.scalars(
        select(ScanJob)
        .where(ScanJob.status.in_([JobStatus.queued, JobStatus.running]))
        .options(selectinload(ScanJob.library))
        .order_by(ScanJob.started_at.desc(), ScanJob.id.desc())
    ).all()
    seen_libraries: set[int] = set()
    deduplicated: list[ScanJobRead] = []
    for job in jobs:
        if job.library_id in seen_libraries:
            continue
        seen_libraries.add(job.library_id)
        deduplicated.append(serialize_scan_job(job))
    return deduplicated


def list_library_scan_jobs(db: Session, library_id: int, limit: int = 10) -> list[ScanJobRead]:
    jobs = db.scalars(
        select(ScanJob)
        .where(ScanJob.library_id == library_id)
        .options(selectinload(ScanJob.library))
        .order_by(ScanJob.id.desc())
        .limit(limit)
    ).all()
    return [serialize_scan_job(job) for job in jobs]
