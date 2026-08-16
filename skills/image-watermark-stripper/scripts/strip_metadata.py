#!/usr/bin/env python3
"""Strip provenance metadata (C2PA, EXIF, XMP, IPTC, PNG text chunks) from images."""
import re
import sys
from pathlib import Path

MARKERS = [
    b"C2PA", b"c2pa", b"JUMBF", b"jumbf",
    b"Anthropic", b"anthropic", b"Made with Claude", b"made with claude",
    b"XMP", b"xmp",
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
    from PIL import Image  # imported lazily: SVG and --check work without Pillow
    with Image.open(src) as im:
        im.load()
        fmt = im.format
        icc = im.info.get("icc_profile")
        dst = im.copy()
        dst.info.clear()
        kwargs = {}
        if fmt == "JPEG":
            kwargs["quality"] = 95
        if icc and fmt in ("JPEG", "PNG", "WEBP"):
            kwargs["icc_profile"] = icc
        dst.save(out, format=fmt, **kwargs)


def main(argv):
    check_only = False
    args = []
    for a in argv:
        if a in ("--check", "-c"):
            check_only = True
        else:
            args.append(a)
    if not args:
        print("usage: strip_metadata.py [--check] <image> [image ...]")
        return 1
    for arg in args:
        src = Path(arg)
        if not src.is_file():
            print(f"SKIP {arg}: not found")
            continue
        before = scan(src)
        if check_only:
            print(f"{src.name}: markers={before or 'none'} (check only)")
            continue
        out = src.with_name(f"{src.stem}_clean{src.suffix}")
        if src.suffix.lower() == ".svg":
            strip_svg(src, out)
        else:
            strip_raster(src, out)
        after = scan(out)
        print(f"{src.name}: markers before={before or 'none'} after={after or 'none'} -> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
