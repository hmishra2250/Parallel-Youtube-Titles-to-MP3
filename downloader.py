from __future__ import annotations

import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from yt_dlp import YoutubeDL


DEFAULT_TITLES_FILE = Path("titles.txt")
DEFAULT_ERRORS_FILE = Path("errors.txt")
DEFAULT_ARCHIVE_FILE = Path("archive.txt")
DEFAULT_DOWNLOAD_DIR = Path("downloads")
DEFAULT_MAX_WORKERS = 8


@dataclass(frozen=True)
class VideoMatch:
    title_query: str
    video_id: str
    video_title: str
    webpage_url: str


@dataclass(frozen=True)
class DownloadResult:
    title_query: str
    success: bool
    video_id: str | None = None
    video_title: str | None = None
    skipped: bool = False
    error: str | None = None


def read_titles(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_archive(path: Path) -> set[str]:
    if not path.exists():
        return set()

    known_ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[0] == "youtube":
            known_ids.add(parts[1])
    return known_ids


def write_errors(path: Path, failed_titles: Iterable[str]) -> None:
    titles = list(failed_titles)
    contents = "".join(f"{title}\n" for title in titles)
    path.write_text(contents, encoding="utf-8")


def append_archive_entries(path: Path, video_ids: Iterable[str]) -> None:
    entries = sorted(set(video_ids))
    if not entries:
        return

    with path.open("a", encoding="utf-8") as archive_file:
        for video_id in entries:
            archive_file.write(f"youtube {video_id}\n")


def build_search_ydl() -> YoutubeDL:
    return YoutubeDL(
        {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": True,
        }
    )


def search_video(title: str) -> VideoMatch:
    with build_search_ydl() as ydl:
        search_response = ydl.extract_info(f"ytsearch1:{title}", download=False)

    entries = (search_response or {}).get("entries") or []
    if not entries:
        raise ValueError(f"No YouTube result found for {title!r}")

    entry = entries[0]
    video_id = entry.get("id")
    if not video_id:
        raise ValueError(f"Search result for {title!r} did not include a video ID")

    video_title = entry.get("title") or title
    webpage_url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}"
    if webpage_url.startswith("/watch?"):
        webpage_url = f"https://www.youtube.com{webpage_url}"
    elif webpage_url == video_id:
        webpage_url = f"https://www.youtube.com/watch?v={video_id}"

    return VideoMatch(title_query=title, video_id=video_id, video_title=video_title, webpage_url=webpage_url)


def build_download_options(download_dir: Path) -> dict:
    download_dir.mkdir(parents=True, exist_ok=True)
    return {
        "writethumbnail": True,
        "format": "bestaudio/best",
        "outtmpl": str(download_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            },
            {
                "key": "FFmpegMetadata",
            },
            {
                "key": "EmbedThumbnail",
            },
        ],
    }


def download_match(match: VideoMatch, download_dir: Path, dry_run: bool = False) -> None:
    if dry_run:
        return

    with YoutubeDL(build_download_options(download_dir)) as ydl:
        ydl.download([match.webpage_url])


def process_one(
    title: str,
    *,
    download_dir: Path,
    archived_ids: set[str],
    in_flight_ids: set[str],
    state_lock: threading.Lock,
    dry_run: bool = False,
) -> DownloadResult:
    match: VideoMatch | None = None
    claimed = False
    try:
        print(f"Searching: {title}")
        match = search_video(title)
        print(f"Found: {match.video_title} ({match.video_id})")

        with state_lock:
            if match.video_id in archived_ids:
                return DownloadResult(
                    title_query=title,
                    success=True,
                    video_id=match.video_id,
                    video_title=match.video_title,
                    skipped=True,
                )
            if match.video_id in in_flight_ids:
                return DownloadResult(
                    title_query=title,
                    success=True,
                    video_id=match.video_id,
                    video_title=match.video_title,
                    skipped=True,
                )
            in_flight_ids.add(match.video_id)
            claimed = True

        if dry_run:
            print(f"Dry run: would download {match.webpage_url}")
        else:
            print(f"Downloading: {match.webpage_url}")
        download_match(match, download_dir=download_dir, dry_run=dry_run)
        return DownloadResult(
            title_query=title,
            success=True,
            video_id=match.video_id,
            video_title=match.video_title,
        )
    except Exception as exc:
        return DownloadResult(
            title_query=title,
            success=False,
            video_id=match.video_id if match else None,
            video_title=match.video_title if match else None,
            error=str(exc),
        )
    finally:
        if claimed and match is not None:
            with state_lock:
                in_flight_ids.discard(match.video_id)


def run_downloads(
    *,
    titles_file: Path,
    errors_file: Path,
    archive_file: Path,
    download_dir: Path,
    max_workers: int,
    dry_run: bool = False,
) -> int:
    titles = read_titles(titles_file)
    if not titles:
        raise ValueError(f"No titles found in {titles_file}")

    archived_ids = read_archive(archive_file)
    in_flight_ids: set[str] = set()
    state_lock = threading.Lock()

    print(f"Loaded {len(titles)} titles from {titles_file}")
    print(f"Archive contains {len(archived_ids)} video IDs")
    print(f"Using {max_workers} worker(s)")

    results: list[DownloadResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(
                process_one,
                title,
                download_dir=download_dir,
                archived_ids=archived_ids,
                in_flight_ids=in_flight_ids,
                state_lock=state_lock,
                dry_run=dry_run,
            ): title
            for title in titles
        }

        for future in as_completed(future_map):
            result = future.result()
            results.append(result)
            if result.success:
                status = "skipped" if result.skipped else "done"
                print(f"{status.upper()}: {result.title_query}")
            else:
                print(f"FAILED: {result.title_query}: {result.error}")

    failures = [result.title_query for result in results if not result.success]
    successful_ids = [
        result.video_id
        for result in results
        if result.success and not result.skipped and result.video_id is not None
    ]

    write_errors(errors_file, failures)
    append_archive_entries(archive_file, successful_ids)

    print(
        "Finished. "
        f"successful={len(successful_ids)} "
        f"skipped={sum(1 for result in results if result.skipped)} "
        f"failed={len(failures)}"
    )
    return 0 if not failures else 1


def build_parser(description: str, default_workers: int) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--titles-file", type=Path, default=DEFAULT_TITLES_FILE)
    parser.add_argument("--errors-file", type=Path, default=DEFAULT_ERRORS_FILE)
    parser.add_argument("--archive-file", type=Path, default=DEFAULT_ARCHIVE_FILE)
    parser.add_argument("--download-dir", type=Path, default=DEFAULT_DOWNLOAD_DIR)
    parser.add_argument("--jobs", type=int, default=default_workers)
    parser.add_argument("--dry-run", action="store_true", help="Resolve YouTube matches without downloading.")
    return parser


def run_from_args(args: argparse.Namespace) -> int:
    if args.jobs < 1:
        raise ValueError("--jobs must be at least 1")

    return run_downloads(
        titles_file=args.titles_file,
        errors_file=args.errors_file,
        archive_file=args.archive_file,
        download_dir=args.download_dir,
        max_workers=args.jobs,
        dry_run=args.dry_run,
    )
