from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.db.session import get_db
from backend.app.services.runtime import ScanRuntimeManager


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db


def get_app_settings() -> Settings:
    return get_settings()


def get_scan_runtime(request: Request) -> ScanRuntimeManager:
    return request.app.state.scan_runtime
