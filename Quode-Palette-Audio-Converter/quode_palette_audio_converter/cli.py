"""Command-line interface for Quode Palette Audio Converter."""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

AUDIO_EXTENSIONS = {".aac", ".aif", ".aiff", ".alac", ".flac", ".m4a", ".m4b", ".mka", ".mp3", ".oga", ".ogg", ".opus", ".wav", ".wma", ".weba", ".webm"}
CODEC_BY_FORMAT = {
    "mp3": ["-c:a", "libmp3lame"], "wav": ["-c:a", "pcm_s16le"],
    "flac": ["-c:a", "flac"], "ogg": ["-c:a", "libvorbis"],
    "opus": ["-c:a", "libopus"], "m4a": ["-c:a", "aac"],
    "aac": ["-c:a", "aac"], "wma": ["-c:a", "wmav2"],
}

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quode-audio", description="Convert audio files with FFmpeg, including whole folders.", epilog="Examples:\n  quode-audio song.m4a --to mp3\n  quode-audio ./recordings --to flac --recursive\n  quode-audio ./audio --to mp3 --output-dir ./converted --quality 2", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="An audio file or a folder of audio files.")
    parser.add_argument("--to", dest="output_format", required=True, choices=sorted(CODEC_BY_FORMAT), help="Target audio format.")
    parser.add_argument("--output-dir", type=Path, help="Write converted files here instead of beside each source file.")
    parser.add_argument("--recursive", action="store_true", help="Include audio files in subfolders when input is a folder.")
    parser.add_argument("--quality", type=int, choices=range(10), default=2, help="MP3 VBR quality from 0 (best) to 9 (smallest). Default: 2.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing output files. By default, they are skipped.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable or path to it. Default: ffmpeg on PATH.")
    parser.add_argument("--version", action="version", version="Quode Palette Audio Converter 1.0.0")
    return parser

def find_inputs(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() not in AUDIO_EXTENSIONS:
            raise ValueError(f"Unsupported input extension: {source.suffix or '(none)'}")
        return [source]
    if not source.is_dir():
        raise FileNotFoundError(f"Input path does not exist: {source}")
    iterator = source.rglob("*") if recursive else source.iterdir()
    return sorted(p for p in iterator if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS)

def output_path(source: Path, target_format: str, output_dir: Path | None) -> Path:
    destination = output_dir / f"{source.stem}.{target_format}" if output_dir else source.with_suffix(f".{target_format}")
    if destination.resolve() == source.resolve():
        destination = source.with_name(f"{source.stem}_converted.{target_format}")
    return destination

def convert_one(source: Path, destination: Path, target_format: str, ffmpeg: str, quality: int, overwrite: bool) -> tuple[bool, str]:
    if destination.exists() and not overwrite:
        return False, f"Skipped, output already exists: {destination}"
    destination_existed = destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [ffmpeg, "-hide_banner", "-nostdin", "-v", "error", "-i", str(source), "-map", "0:a:0", "-vn", *CODEC_BY_FORMAT[target_format]]
    if target_format == "mp3":
        command.extend(["-q:a", str(quality)])
    command.extend(["-y" if overwrite else "-n", str(destination)])
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        return False, f"Could not run FFmpeg: {exc}"
    if result.returncode != 0:
        if not destination_existed:
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                pass
        return False, result.stderr.strip() or f"FFmpeg exited with status {result.returncode}."
    return True, f"Converted: {source} -> {destination}"

def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if shutil.which(args.ffmpeg) is None and not Path(args.ffmpeg).is_file():
        print(f"Error: FFmpeg was not found: {args.ffmpeg}\nInstall FFmpeg and ensure it is on PATH, or pass --ffmpeg.", file=sys.stderr)
        return 2
    try:
        sources = find_inputs(args.input, args.recursive)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print("No supported audio files found.", file=sys.stderr)
        return 1
    successes = failures = skipped = 0
    for source in sources:
        destination = output_path(source, args.output_format, args.output_dir)
        ok, message = convert_one(source, destination, args.output_format, args.ffmpeg, args.quality, args.overwrite)
        if ok:
            successes += 1
            print(f"[OK] {message}")
        elif message.startswith("Skipped,"):
            skipped += 1
            print(f"[SKIP] {message}")
        else:
            failures += 1
            print(f"[ERROR] {source}: {message}", file=sys.stderr)
    print(f"\nFinished. Converted: {successes}, skipped: {skipped}, failed: {failures}.")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
