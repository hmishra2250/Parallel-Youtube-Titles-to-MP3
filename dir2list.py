from __future__ import annotations

import argparse
import mimetypes
from pathlib import Path


COMMON_VIDEO_SUFFIXES = {
    ".3gp",
    ".avi",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
    ".wmv",
}


def is_video_file(path: Path) -> bool:
    if path.suffix.lower() in COMMON_VIDEO_SUFFIXES:
        return True

    mime_type, _ = mimetypes.guess_type(path.name)
    return bool(mime_type and mime_type.startswith("video/"))


def extract_titles(directories: list[Path]) -> list[str]:
    titles: list[str] = []
    for directory in directories:
        for child in sorted(directory.expanduser().iterdir()):
            if child.is_file() and is_video_file(child):
                titles.append(child.stem)
    return titles


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a list of local video filenames into a titles file.")
    parser.add_argument("directories", nargs="+", type=Path, help="Directories to scan non-recursively.")
    parser.add_argument("--output", type=Path, default=Path("titles.txt"))
    args = parser.parse_args()

    titles = extract_titles(args.directories)
    args.output.write_text("".join(f"{title}\n" for title in titles), encoding="utf-8")
    print(f"Wrote {len(titles)} titles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
