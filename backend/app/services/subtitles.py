from pathlib import Path


LANGUAGE_HINTS = {
    "de",
    "deu",
    "ger",
    "en",
    "eng",
    "fr",
    "fre",
    "spa",
    "es",
    "it",
    "ita",
    "jpn",
    "ja",
    "und",
}


def detect_external_subtitles(video_path: Path, allowed_extensions: tuple[str, ...]) -> list[dict[str, str | None]]:
    parent = video_path.parent
    suffixes = {extension.lower() for extension in allowed_extensions}
    stem = video_path.stem
    detected: list[dict[str, str | None]] = []

    for entry in sorted(parent.iterdir()):
        if not entry.is_file():
            continue
        extension = entry.suffix.lower()
        if extension not in suffixes:
            continue
        if entry == video_path:
            continue
        if not (entry.stem == stem or entry.name.startswith(f"{stem}.")):
            continue

        middle = entry.name[len(stem) : -len(entry.suffix)]
        tokens = [token.lower() for token in middle.split(".") if token]
        language = next((token for token in tokens if token in LANGUAGE_HINTS), None)

        detected.append(
            {
                "path": entry.name,
                "language": language,
                "format": extension.lstrip("."),
            }
        )

    return detected

