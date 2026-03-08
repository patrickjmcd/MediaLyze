from pathlib import Path

from backend.app.core.config import Settings
from backend.app.schemas.browse import BrowseEntry, BrowseResponse
from backend.app.utils.pathing import ensure_relative_to_root, relative_display_path


def browse_media_root(settings: Settings, relative_path: str = ".") -> BrowseResponse:
    candidate = settings.media_root / relative_path
    safe_path = ensure_relative_to_root(candidate, settings.media_root)

    entries = [
        BrowseEntry(
            name=entry.name,
            path=relative_display_path(entry, settings.media_root),
            is_dir=entry.is_dir(),
        )
        for entry in sorted(safe_path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    ]

    parent_path = None
    if safe_path != settings.media_root.resolve():
        parent_path = relative_display_path(safe_path.parent, settings.media_root)

    return BrowseResponse(
        current_path=relative_display_path(safe_path, settings.media_root),
        parent_path=parent_path,
        entries=entries,
    )

