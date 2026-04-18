from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from downloader import append_archive_entries, read_archive, read_titles, write_errors


class DownloaderHelpersTest(unittest.TestCase):
    def test_read_titles_discards_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            titles_file = Path(tmpdir) / "titles.txt"
            titles_file.write_text("Song A\n\n Song B \n \nSong C\n", encoding="utf-8")

            self.assertEqual(read_titles(titles_file), ["Song A", "Song B", "Song C"])

    def test_read_archive_ignores_invalid_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_file = Path(tmpdir) / "archive.txt"
            archive_file.write_text(
                "youtube abc123\n"
                "nonsense line\n"
                "youtube def456\n",
                encoding="utf-8",
            )

            self.assertEqual(read_archive(archive_file), {"abc123", "def456"})

    def test_append_archive_entries_deduplicates_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_file = Path(tmpdir) / "archive.txt"
            append_archive_entries(archive_file, ["abc123", "abc123", "def456"])

            self.assertEqual(
                archive_file.read_text(encoding="utf-8"),
                "youtube abc123\nyoutube def456\n",
            )

    def test_write_errors_overwrites_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            errors_file = Path(tmpdir) / "errors.txt"
            errors_file.write_text("old\n", encoding="utf-8")

            write_errors(errors_file, ["Song A", "Song B"])

            self.assertEqual(errors_file.read_text(encoding="utf-8"), "Song A\nSong B\n")


if __name__ == "__main__":
    unittest.main()
