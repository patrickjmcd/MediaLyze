from pathlib import Path


def ensure_relative_to_root(candidate: Path, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved_candidate = candidate.resolve()
    resolved_candidate.relative_to(resolved_root)
    return resolved_candidate


def relative_display_path(candidate: Path, root: Path) -> str:
    resolved_root = root.resolve()
    resolved_candidate = candidate.resolve()
    relative = resolved_candidate.relative_to(resolved_root)
    return "." if str(relative) == "." else relative.as_posix()

