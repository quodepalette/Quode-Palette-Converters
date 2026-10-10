"""Command-line image conversion using Pillow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
    from PIL.Image import DecompressionBombError
except ImportError:  # Give users a useful message if dependencies are not installed.
    Image = None  # type: ignore[assignment]
    ImageOps = None  # type: ignore[assignment]
    UnidentifiedImageError = Exception  # type: ignore[assignment,misc]
    DecompressionBombError = Exception  # type: ignore[assignment,misc]

# Pillow format names differ from the extensions used on disk.
FORMAT_BY_TARGET = {
    "png": ("PNG", ".png"),
    "jpg": ("JPEG", ".jpg"),
    "webp": ("WEBP", ".webp"),
    "bmp": ("BMP", ".bmp"),
    "tiff": ("TIFF", ".tiff"),
    "gif": ("GIF", ".gif"),
    "ico": ("ICO", ".ico"),
}
INPUT_EXTENSIONS = {
    ".avif", ".bmp", ".dib", ".gif", ".heic", ".heif", ".ico", ".jfif",
    ".jpeg", ".jpg", ".jpe", ".png", ".tif", ".tiff", ".webp",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quode-image",
        description="Convert image files or folders to a chosen format.",
        epilog=(
            "Examples:\n"
            "  quode-image photo.webp --to jpg\n"
            "  quode-image ./photos --to webp --recursive\n"
            "  quode-image ./photos --to png --output-dir ./converted"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="An image file or a folder of images.")
    parser.add_argument("--to", dest="output_format", required=True,
                        choices=sorted(FORMAT_BY_TARGET), help="Target image format.")
    parser.add_argument("--output-dir", type=Path,
                        help="Write converted files here instead of beside each source file.")
    parser.add_argument("--recursive", action="store_true",
                        help="Include images in subfolders when input is a folder.")
    parser.add_argument("--quality", type=int, choices=range(1, 101), default=90,
                        help="Quality for JPEG and WebP, from 1 to 100. Default: 90.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace existing output files. By default, they are skipped.")
    parser.add_argument("--version", action="version", version="Quode Palette Image Converter 1.0.0")
    return parser


def find_inputs(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() not in INPUT_EXTENSIONS:
            raise ValueError(f"Unsupported input extension: {source.suffix or '(none)'}")
        return [source]
    if not source.is_dir():
        raise FileNotFoundError(f"Input path does not exist: {source}")
    iterator = source.rglob("*") if recursive else source.iterdir()
    return sorted(p for p in iterator if p.is_file() and p.suffix.lower() in INPUT_EXTENSIONS)


def make_output_path(source: Path, target: str, output_dir: Path | None) -> Path:
    extension = FORMAT_BY_TARGET[target][1]
    destination = output_dir / f"{source.stem}{extension}" if output_dir else source.with_suffix(extension)
    if destination.resolve() == source.resolve():
        destination = source.with_name(f"{source.stem}_converted{extension}")
    return destination


def convert_one(source: Path, destination: Path, target: str, quality: int,
                overwrite: bool) -> tuple[str, str]:
    if destination.exists() and not overwrite:
        return "skipped", f"Output already exists: {destination}"
    if Image is None:
        return "failed", "Pillow is not installed. Run: python -m pip install -r requirements.txt"

    destination.parent.mkdir(parents=True, exist_ok=True)
    image_format = FORMAT_BY_TARGET[target][0]
    temporary = destination.with_name(f".{destination.stem}.quode-tmp{destination.suffix}")
    try:
        with Image.open(source) as opened:
            # Apply EXIF orientation so exported images match how they are normally viewed.
            frame = ImageOps.exif_transpose(opened)
            frame.seek(0)  # Animated inputs are intentionally converted from their first frame.
            frame.load()
            output = frame.copy()

            if image_format == "JPEG":
                # JPEG cannot store transparency, so use a clean white background.
                if output.mode in ("RGBA", "LA") or (output.mode == "P" and "transparency" in output.info):
                    rgba = output.convert("RGBA")
                    background = Image.new("RGB", rgba.size, "white")
                    background.paste(rgba, mask=rgba.getchannel("A"))
                    output = background
                elif output.mode not in ("RGB", "L"):
                    output = output.convert("RGB")
                elif output.mode == "L":
                    output = output.convert("RGB")
            elif image_format == "ICO":
                output = output.convert("RGBA")
            elif image_format in ("BMP", "GIF") and output.mode not in ("RGB", "L", "P"):
                output = output.convert("RGB")

            save_options: dict[str, object] = {}
            if image_format in ("JPEG", "WEBP"):
                save_options["quality"] = quality
            if image_format == "PNG":
                save_options["optimize"] = True
            if image_format == "WEBP":
                save_options["method"] = 6
            output.save(temporary, format=image_format, **save_options)
        # Replace only after a complete save, avoiding a half-written final file.
        if overwrite and destination.exists():
            destination.unlink()
        temporary.replace(destination)
        return "converted", f"{source} -> {destination}"
    except (OSError, ValueError, UnidentifiedImageError, DecompressionBombError) as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return "failed", str(exc) or exc.__class__.__name__
    except Exception as exc:  # Keep a bad image from stopping a whole batch.
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return "failed", f"Unexpected conversion error: {exc}"


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sources = find_inputs(args.input, args.recursive)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print("No supported image files found.", file=sys.stderr)
        return 1

    converted = skipped = failed = 0
    for source in sources:
        destination = make_output_path(source, args.output_format, args.output_dir)
        status, message = convert_one(source, destination, args.output_format, args.quality, args.overwrite)
        if status == "converted":
            converted += 1
            print(f"[OK] Converted: {message}")
        elif status == "skipped":
            skipped += 1
            print(f"[SKIP] {message}")
        else:
            failed += 1
            print(f"[ERROR] {source}: {message}", file=sys.stderr)

    print(f"\nFinished. Converted: {converted}, skipped: {skipped}, failed: {failed}.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
