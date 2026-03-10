from __future__ import annotations

from copy import deepcopy
from threading import Lock

from backend.app.schemas.library import LibraryDetail, LibrarySummary
from backend.app.schemas.media import DashboardResponse


class StatsCache:
    def __init__(self) -> None:
        self._lock = Lock()
        self._dashboard: dict[str, DashboardResponse] = {}
        self._libraries: dict[str, list[LibrarySummary]] = {}
        self._library_details: dict[str, dict[int, LibraryDetail]] = {}

    def get_dashboard(self, cache_key: str) -> DashboardResponse | None:
        with self._lock:
            return deepcopy(self._dashboard.get(cache_key))

    def set_dashboard(self, cache_key: str, payload: DashboardResponse) -> None:
        with self._lock:
            self._dashboard[cache_key] = deepcopy(payload)

    def get_libraries(self, cache_key: str) -> list[LibrarySummary] | None:
        with self._lock:
            return deepcopy(self._libraries.get(cache_key))

    def set_libraries(self, cache_key: str, payload: list[LibrarySummary]) -> None:
        with self._lock:
            self._libraries[cache_key] = deepcopy(payload)

    def get_library_detail(self, cache_key: str, library_id: int) -> LibraryDetail | None:
        with self._lock:
            return deepcopy(self._library_details.get(cache_key, {}).get(library_id))

    def set_library_detail(self, cache_key: str, library_id: int, payload: LibraryDetail) -> None:
        with self._lock:
            self._library_details.setdefault(cache_key, {})[library_id] = deepcopy(payload)

    def invalidate(self, cache_key: str, library_id: int | None = None) -> None:
        with self._lock:
            self._dashboard.pop(cache_key, None)
            self._libraries.pop(cache_key, None)
            if library_id is None:
                self._library_details.pop(cache_key, None)
            else:
                self._library_details.setdefault(cache_key, {}).pop(library_id, None)


stats_cache = StatsCache()
