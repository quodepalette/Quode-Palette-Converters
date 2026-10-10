import tempfile
import unittest
from pathlib import Path

from quode_palette_image_converter.cli import build_parser, find_inputs, make_output_path


class ImageCliTests(unittest.TestCase):
    def test_finds_supported_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "photo.webp").touch()
            (root / "notes.txt").touch()
            self.assertEqual([root / "photo.webp"], find_inputs(root, recursive=False))

    def test_recursive_scan_finds_nested_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()
            (nested / "photo.png").touch()
            self.assertEqual([nested / "photo.png"], find_inputs(root, recursive=True))

    def test_same_format_uses_converted_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "photo.jpg"
            source.touch()
            self.assertEqual("photo_converted.jpg", make_output_path(source, "jpg", None).name)

    def test_quality_default(self):
        args = build_parser().parse_args(["photo.png", "--to", "jpg"])
        self.assertEqual(90, args.quality)


if __name__ == "__main__":
    unittest.main()
