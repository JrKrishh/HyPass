#!/usr/bin/env python3
"""Strip provenance metadata (C2PA, EXIF, XMP, IPTC, PNG text chunks) from images."""
import re
import sys
from pathlib import Path

from PIL import Image

MARKERS = [
    b"C2PA", b"c2pa", b"JUMBF", b"jumbf",
    b"Anthropic", b"anthropic", b"Made with Claude", b"made with claude",
    b"XMP", b"xmp", b"Adobe", b"adobe",
]

SVG_METADATA_RE = re.compile(r"<metadata\b[^>]*>.*?</metadata>", re.S | re.I)
SVG_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def scan(path):
    data = path.read_bytes()
    return sorted({m.decode("latin-1") for m in MARKERS if m in data})


def strip_svg(src, out):
    text = src.read_text(encoding="utf-8", errors="replace")
    text = SVG_METADATA_RE.sub("", text)
    text = SVG_COMMENT_RE.sub("", text)
    out.write_text(text, encoding="utf-8")


def strip_raster(src, out):
    with Image.open(src) as im:
        im.load()
        fmt = im.format
        icc = im.info.get("icc_profile")
        dst = im.copy()
        dst.info.clear()
        kwargs = {}
        if fmt == "JPEG":
            kwargs["quality"] = 95
        if icc and fmt in ("JPEG", "PNG"):
            kwargs["icc_profile"] = icc
        dst.save(out, format=fmt, **kwargs)


def main(argv):
    if not argv:
        print("usage: strip_metadata.py <image> [image ...]")
        return 1
    for arg in argv:
        src = Path(arg)
        if not src.is_file():
            print(f"SKIP {arg}: not found")
            continue
        out = src.with_name(f"{src.stem}_clean{src.suffix}")
        before = scan(src)
        if src.suffix.lower() == ".svg":
            strip_svg(src, out)
        else:
            strip_raster(src, out)
        after = scan(out)
        print(f"{src.name}: markers before={before or 'none'} after={after or 'none'} -> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
