from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dir2list import extract_titles, is_video_file


class Dir2ListTest(unittest.TestCase):
    def test_is_video_file_by_extension(self) -> None:
        self.assertTrue(is_video_file(Path("clip.mp4")))
        self.assertFalse(is_video_file(Path("notes.txt")))

    def test_extract_titles_uses_stem_and_skips_non_videos(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            (directory / "Track One.mp4").write_text("", encoding="utf-8")
            (directory / "Track Two.mkv").write_text("", encoding="utf-8")
            (directory / "ignore.txt").write_text("", encoding="utf-8")
            (directory / "nested").mkdir()

            self.assertEqual(extract_titles([directory]), ["Track One", "Track Two"])


if __name__ == "__main__":
    unittest.main()
