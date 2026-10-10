"""Video conversion command-line interface backed by FFmpeg."""
from __future__ import annotations
import argparse
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Sequence

VIDEO_EXTENSIONS = {".3gp", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".mts", ".m2ts", ".ogv", ".ts", ".webm", ".wmv"}
VIDEO_CODECS = {
    "mp4": ["-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"],
    "mkv": ["-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac", "-b:a", "192k"],
    "webm": ["-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-c:a", "libopus", "-b:a", "128k"],
    "mov": ["-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac", "-b:a", "192k"],
    "avi": ["-c:v", "mpeg4", "-q:v", "5", "-c:a", "libmp3lame", "-q:a", "2"],
    "gif": ["-vf", "fps=15,scale=640:-1:flags=lanczos"],
}

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="quode-video", description="Convert video files with FFmpeg.")
    p.add_argument("input", type=Path, help="A video file or folder.")
    p.add_argument("--to", dest="fmt", required=True, choices=sorted(VIDEO_CODECS), help="Output format.")
    p.add_argument("--output-dir", type=Path, help="Optional destination folder.")
    p.add_argument("--recursive", action="store_true", help="Include subfolders.")
    p.add_argument("--overwrite", action="store_true", help="Replace existing output files.")
    p.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable or path.")
    return p

def collect(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in VIDEO_EXTENSIONS:
            raise ValueError(f"Unsupported video extension: {path.suffix or '(none)'}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"Input path does not exist: {path}")
    it = path.rglob("*") if recursive else path.iterdir()
    return sorted(x for x in it if x.is_file() and x.suffix.lower() in VIDEO_EXTENSIONS)

DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
BAR_WIDTH = 28

def probe_duration(ffmpeg: str, src: Path) -> float | None:
    """Return the media duration in seconds, or None if FFmpeg can't tell."""
    try:
        result = subprocess.run([ffmpeg, "-hide_banner", "-nostdin", "-i", str(src)], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    except OSError:
        return None
    match = DURATION_RE.search(result.stderr or "")
    if not match:
        return None
    h, m, sec = match.groups()
    total = int(h) * 3600 + int(m) * 60 + float(sec)
    return total if total > 0 else None

def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"

def render_progress(label: str, done: float, total: float | None, elapsed: float) -> str:
    """Build one progress line (plain ASCII so it works in any Windows console)."""
    if total:
        frac = min(max(done / total, 0.0), 1.0)
        filled = int(round(frac * BAR_WIDTH))
        bar = "#" * filled + "-" * (BAR_WIDTH - filled)
        eta = ""
        if frac > 0.01 and elapsed > 0:
            eta = f"  ETA {format_time(elapsed * (1 - frac) / frac)}"
        return f"{label} [{bar}] {frac * 100:5.1f}%  {format_time(done)}/{format_time(total)}{eta}"
    spinner = "|/-\\"[int(elapsed * 4) % 4]
    return f"{label} {spinner} working...  {format_time(done)} processed  ({format_time(elapsed)} elapsed)"

class ProgressPrinter:
    """Draws a single-line progress bar when attached to a terminal; otherwise prints occasional updates."""
    def __init__(self, label: str, total: float | None, stream=None) -> None:
        self.label, self.total = label, total
        self.stream = stream or sys.stdout
        self.tty = bool(getattr(self.stream, "isatty", lambda: False)())
        self.start = time.monotonic()
        self.last_draw = 0.0
        self.last_len = 0
        self.next_step = 25.0

    def update(self, done: float, force: bool = False) -> None:
        now = time.monotonic()
        elapsed = now - self.start
        if self.tty:
            if not force and now - self.last_draw < 0.1:
                return
            line = render_progress(self.label, done, self.total, elapsed)
            self.stream.write("\r" + line + " " * max(0, self.last_len - len(line)))
            self.stream.flush()
            self.last_len, self.last_draw = len(line), now
        elif self.total and (done / self.total * 100 >= self.next_step or force):
            print(render_progress(self.label, done, self.total, elapsed), file=self.stream, flush=True)
            while self.next_step <= done / self.total * 100:
                self.next_step += 25.0

    def clear(self) -> None:
        if self.tty and self.last_len:
            self.stream.write("\r" + " " * self.last_len + "\r")
            self.stream.flush()

def parse_progress_line(line: str) -> float | None:
    """Return processed seconds from an FFmpeg '-progress' line, if it carries one."""
    key, _, value = line.strip().partition("=")
    if key in ("out_time_us", "out_time_ms"):
        try:
            return max(0.0, int(value) / 1_000_000)
        except ValueError:
            return None
    return None

def convert(src: Path, dst: Path, fmt: str, ffmpeg: str, overwrite: bool, label: str = "") -> tuple[str, str]:
    if dst.exists() and not overwrite:
        return "skip", f"Output already exists: {dst}"
    existed = dst.exists()
    dst.parent.mkdir(parents=True, exist_ok=True)
    duration = probe_duration(ffmpeg, src)
    cmd = [ffmpeg, "-hide_banner", "-nostdin", "-v", "error", "-progress", "pipe:1", "-nostats", "-i", str(src), "-map", "0:v:0", "-map", "0:a?", "-sn", "-dn", *VIDEO_CODECS[fmt], "-y" if overwrite else "-n", str(dst)]
    printer = ProgressPrinter(label or "Converting", duration)
    errors: list[str] = []
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    except OSError as exc:
        return "error", f"Could not start FFmpeg: {exc}"
    drain = threading.Thread(target=lambda: errors.extend(proc.stderr), daemon=True)
    drain.start()
    done = 0.0
    try:
        printer.update(0.0, force=True)
        for line in proc.stdout:
            seconds = parse_progress_line(line)
            if seconds is not None:
                done = seconds
                printer.update(done)
            elif line.startswith("progress=") and not printer.tty:
                continue
        proc.wait()
        drain.join(timeout=5)
    except KeyboardInterrupt:
        proc.kill()
        proc.wait()
        printer.clear()
        if not existed:
            try: dst.unlink(missing_ok=True)
            except OSError: pass
        raise
    if proc.returncode == 0:
        printer.update(duration or done, force=True)
    printer.clear()
    if proc.returncode:
        if not existed:
            try: dst.unlink(missing_ok=True)
            except OSError: pass
        return "error", "".join(errors).strip() or f"FFmpeg exited with status {proc.returncode}."
    return "ok", f"Converted {src} -> {dst}"

def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if shutil.which(args.ffmpeg) is None and not Path(args.ffmpeg).is_file():
        print(f"Error: FFmpeg was not found: {args.ffmpeg}. Install FFmpeg or use --ffmpeg.", file=sys.stderr)
        return 2
    try: sources = collect(args.input, args.recursive)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr); return 2
    if not sources:
        print("No supported video files found.", file=sys.stderr); return 1
    counts = {"ok": 0, "skip": 0, "error": 0}
    total_files = len(sources)
    for index, src in enumerate(sources, start=1):
        dst = (args.output_dir / f"{src.stem}.{args.fmt}") if args.output_dir else src.with_suffix(f".{args.fmt}")
        if dst.resolve() == src.resolve(): dst = src.with_name(f"{src.stem}_converted.{args.fmt}")
        print(f"\nFile {index} of {total_files}: {src.name}")
        try:
            status, msg = convert(src, dst, args.fmt, args.ffmpeg, args.overwrite, label=f"[{index}/{total_files}]")
        except KeyboardInterrupt:
            print("\nCancelled.", file=sys.stderr)
            return 130
        counts[status] += 1
        print(f"[{status.upper()}] {msg}", file=sys.stderr if status == "error" else sys.stdout)
    print(f"\nFinished. Converted: {counts['ok']}, skipped: {counts['skip']}, failed: {counts['error']}.")
    return 1 if counts["error"] else 0

if __name__ == "__main__": raise SystemExit(main())
