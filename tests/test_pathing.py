from pathlib import Path

import pytest

from backend.app.utils.pathing import ensure_relative_to_root, relative_display_path


def test_relative_display_path_uses_dot_for_root(tmp_path: Path) -> None:
    assert relative_display_path(tmp_path, tmp_path) == "."


def test_ensure_relative_to_root_rejects_parent_escape(tmp_path: Path) -> None:
    outsider = tmp_path.parent
    with pytest.raises(ValueError):
        ensure_relative_to_root(outsider, tmp_path)
