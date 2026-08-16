#!/usr/bin/env python3
"""Dispatcher: strip provenance/metadata from any supported file by routing it to
the right sibling skill (image, document, or media stripper).

Resolves sibling scripts relative to the skills root, which is the same shape in
the repo and once installed (skills-root/<skill>/scripts/<script>.py), so it works
either way. Walks directories recursively.

Usage:
    strip_all.py <path> [path ...]            # strip -> <name>_clean.<ext>
    strip_all.py --check <path> [path ...]    # scan only, write nothing
"""
import subprocess
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]

IMAGE_STRIPPER = SKILLS_ROOT / "image-watermark-stripper/scripts/strip_metadata.py"
DOC_STRIPPER = SKILLS_ROOT / "document-metadata-stripper/scripts/strip_document_metadata.py"
MEDIA_STRIPPER = SKILLS_ROOT / "media-metadata-stripper/scripts/strip_media_metadata.py"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif", ".svg"}
DOC_EXT = {
    ".docx", ".docm", ".dotx", ".dotm",
    ".xlsx", ".xlsm", ".xltx", ".xltm",
    ".pptx", ".pptm", ".potx", ".potm",
    ".pdf",
}
MEDIA_EXT = {".mp3", ".mp4", ".m4a", ".mov", ".wav", ".flac", ".avi", ".mkv", ".webm"}


def stripper_for(ext):
    if ext in IMAGE_EXT:
        return IMAGE_STRIPPER
    if ext in DOC_EXT:
        return DOC_STRIPPER
    if ext in MEDIA_EXT:
        return MEDIA_STRIPPER
    return None


def iter_files(args):
    for arg in args:
        p = Path(arg)
        if p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file():
                    yield child
        elif p.is_file():
            yield p
        else:
            print(f"SKIP {arg}: not found")


def main(argv):
    check_only = "--check" in argv or "-c" in argv
    deep = "--deep" in argv
    args = [a for a in argv if a not in ("--check", "-c", "--deep")]
    if not args:
        print("usage: strip_all.py [--check] [--deep] <path> [path ...]")
        return 1
    routed = 0
    for path in iter_files(args):
        script = stripper_for(path.suffix.lower())
        if script is None:
            continue  # unsupported type -> skipped silently
        if not script.is_file():
            print(f"SKIP {path.name}: stripper not found ({script.name}) - is the skill installed?")
            continue
        cmd = [sys.executable, str(script)]
        if check_only:
            cmd.append("--check")
        if deep and script == DOC_STRIPPER:  # only the document stripper supports --deep
            cmd.append("--deep")
        cmd.append(str(path))
        routed += 1
        subprocess.run(cmd)
    if routed == 0:
        print("No supported files found.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
