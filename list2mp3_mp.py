from __future__ import annotations

from downloader import DEFAULT_MAX_WORKERS, build_parser, run_from_args


def main() -> int:
    parser = build_parser(
        "Download title-based YouTube audio in parallel using a worker pool.",
        default_workers=DEFAULT_MAX_WORKERS,
    )
    args = parser.parse_args()
    return run_from_args(args)


if __name__ == "__main__":
    raise SystemExit(main())
