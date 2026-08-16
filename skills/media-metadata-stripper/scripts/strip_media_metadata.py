#!/usr/bin/env python3
"""Strip metadata from audio/video files using ffmpeg.

Removes container/stream tags (title, artist, comment, encoder, and any
Claude/Anthropic/C2PA provenance tags) by remuxing with metadata dropped. Stream
data is copied, so there is no re-encode and no quality loss.

Requires ffmpeg/ffprobe on PATH. Without them, files are reported and skipped.

Usage:
    strip_media_metadata.py <file> [file ...]        # strip -> <name>_clean.<ext>
    strip_media_metadata.py --check <file> [...]     # scan tags only, write nothing
"""
import shutil
import subprocess
import sys
from pathlib import Path

MARKERS = ["C2PA", "c2pa", "Claude", "claude", "Anthropic", "anthropic", "Made with Claude"]

MEDIA_SUFFIXES = {".mp3", ".mp4", ".m4a", ".mov", ".wav", ".flac", ".avi", ".mkv", ".webm"}


def have_ffmpeg():
    return shutil.which("ffmpeg") and shutil.which("ffprobe")


def read_tags(path):
    """Return the ffprobe tag dump (format + stream tags) as text, or '' on error."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_format", "-show_streams", str(path)],
            capture_output=True, text=True,
        )
        return out.stdout or ""
    except Exception:
        return ""


def scan(path):
    tags = read_tags(path)
    return sorted({m for m in MARKERS if m in tags})


def strip(src, out):
    # -map_metadata -1 drops global metadata; -c copy avoids re-encoding.
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-map_metadata", "-1",
         "-map_chapters", "-1", "-c", "copy", str(out)],
        capture_output=True,
    )


def process(arg, check_only):
    src = Path(arg)
    if not src.is_file():
        print(f"SKIP {arg}: not found")
        return
    if src.suffix.lower() not in MEDIA_SUFFIXES:
        print(f"SKIP {src.name}: unsupported type {src.suffix} (handled: {', '.join(sorted(MEDIA_SUFFIXES))})")
        return
    if not have_ffmpeg():
        print(f"SKIP {src.name}: needs ffmpeg/ffprobe on PATH (install ffmpeg)")
        return
    before = scan(src)
    if check_only:
        print(f"{src.name}: markers={before or 'none'} (check only)")
        return
    out = src.with_name(f"{src.stem}_clean{src.suffix}")
    strip(src, out)
    after = scan(out) if out.is_file() else ["<strip failed>"]
    print(f"{src.name}: markers before={before or 'none'} after={after or 'none'} -> {out.name}")


def main(argv):
    check_only = False
    args = []
    for a in argv:
        if a in ("--check", "-c"):
            check_only = True
        else:
            args.append(a)
    if not args:
        print("usage: strip_media_metadata.py [--check] <file> [file ...]")
        return 1
    for arg in args:
        process(arg, check_only)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
