import tempfile
import unittest
from pathlib import Path
from quode_palette_audio_converter.cli import find_inputs, output_path, build_parser

class CliTests(unittest.TestCase):
    def test_finds_supported_audio_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "track.m4a").touch()
            (root / "notes.txt").touch()
            self.assertEqual([root / "track.m4a"], find_inputs(root, False))

    def test_recursive_scan_finds_nested_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()
            (nested / "track.wav").touch()
            self.assertEqual([nested / "track.wav"], find_inputs(root, True))

    def test_same_format_uses_converted_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "track.mp3"
            source.touch()
            self.assertEqual("track_converted.mp3", output_path(source, "mp3", None).name)

    def test_quality_default(self):
        args = build_parser().parse_args(["track.m4a", "--to", "mp3"])
        self.assertEqual(2, args.quality)

if __name__ == "__main__":
    unittest.main()
