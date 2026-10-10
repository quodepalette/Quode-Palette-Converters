import tempfile
import unittest
from pathlib import Path
from quode_palette_video_converter.cli import collect, format_time, parse_progress_line, parser, render_progress

class VideoCliTests(unittest.TestCase):
    def test_finds_video_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "clip.mp4").touch()
            (root / "readme.txt").touch()
            self.assertEqual([root / "clip.mp4"], collect(root, False))
    def test_recursive_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); sub = root / "sub"; sub.mkdir(); (sub / "clip.mov").touch()
            self.assertEqual([sub / "clip.mov"], collect(root, True))
    def test_target_format_required(self):
        with self.assertRaises(SystemExit): parser().parse_args(["clip.mp4"])

class ProgressTests(unittest.TestCase):
    def test_parse_progress_line(self):
        self.assertEqual(2.5, parse_progress_line("out_time_us=2500000\n"))
        self.assertIsNone(parse_progress_line("speed=1.2x\n"))
        self.assertIsNone(parse_progress_line("out_time_us=N/A\n"))
    def test_format_time(self):
        self.assertEqual("01:05", format_time(65))
        self.assertEqual("1:01:01", format_time(3661))
    def test_render_progress_with_total(self):
        line = render_progress("[1/2]", 50, 100, 10)
        self.assertIn("50.0%", line)
        self.assertIn("ETA 00:10", line)
    def test_render_progress_without_total(self):
        self.assertIn("working", render_progress("[1/1]", 5, None, 3))

if __name__ == "__main__": unittest.main()
