from backend.app.models.entities import ScanMode
from backend.app.services.library_service import normalize_scan_config


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
