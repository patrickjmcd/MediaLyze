from pathlib import Path

from backend.app.services.subtitles import detect_external_subtitles


def test_detect_external_subtitles_matches_sibling_files(tmp_path: Path) -> None:
    video = tmp_path / "movie.mkv"
    video.write_text("video")
    (tmp_path / "movie.en.srt").write_text("sub")
    (tmp_path / "movie.de.ass").write_text("sub")
    (tmp_path / "other.en.srt").write_text("sub")

    subtitles = detect_external_subtitles(video, (".srt", ".ass"))

    assert subtitles == [
        {"path": "movie.de.ass", "language": "de", "format": "ass"},
        {"path": "movie.en.srt", "language": "en", "format": "srt"},
    ]

