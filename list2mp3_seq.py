from __future__ import annotations

from downloader import build_parser, run_from_args


def main() -> int:
    parser = build_parser("Download title-based YouTube audio sequentially.", default_workers=1)
    args = parser.parse_args()
    args.jobs = 1
    return run_from_args(args)


if __name__ == "__main__":
    raise SystemExit(main())
