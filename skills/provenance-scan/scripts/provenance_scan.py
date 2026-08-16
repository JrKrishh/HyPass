#!/usr/bin/env python3
"""Read-only auditor: report which files carry Claude/C2PA provenance markers.

Walks the given files and/or directories, scans each supported file, and prints
a report. Never modifies anything.

Exit codes:
    0  no provenance markers found
    1  provenance markers found in at least one file
    2  usage error (no paths given)

Usage:
    provenance_scan.py <path> [path ...]
"""
import sys
import zipfile
from pathlib import Path

MARKERS = [
    b"C2PA", b"c2pa", b"JUMBF", b"jumbf",
    b"Anthropic", b"anthropic", b"Made with Claude", b"made with claude",
    b"Claude", b"claude",
]

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif", ".svg"}
OFFICE_EXT = {
    ".docx", ".docm", ".dotx", ".dotm",
    ".xlsx", ".xlsm", ".xltx", ".xltm",
    ".pptx", ".pptm", ".potx", ".potm",
}
OOXML_META_PARTS = ("docProps/core.xml", "docProps/app.xml", "docProps/custom.xml")


def scan_bytes(data):
    return sorted({m.decode("latin-1") for m in MARKERS if m in data})


def scan_office(path):
    """Scan only the metadata parts so body text mentioning Claude isn't a hit."""
    found = set()
    try:
        with zipfile.ZipFile(path) as zin:
            names = set(zin.namelist())
            for part in OOXML_META_PARTS:
                if part in names:
                    found.update(scan_bytes(zin.read(part)))
    except zipfile.BadZipFile:
        return None
    return sorted(found)


def scan_file(path):
    ext = path.suffix.lower()
    if ext in OFFICE_EXT:
        return scan_office(path)
    if ext in IMAGE_EXT or ext == ".pdf":
        return scan_bytes(path.read_bytes())
    return None  # unsupported type -> skipped


def iter_paths(args):
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
    as_json = False
    args = []
    for a in argv:
        if a == "--json":
            as_json = True
        else:
            args.append(a)
    if not args:
        print("usage: provenance_scan.py [--json] <path> [path ...]")
        return 2
    results = []
    flagged = 0
    for path in iter_paths(args):
        markers = scan_file(path)
        if markers is None:
            continue  # unsupported type
        is_flagged = bool(markers)
        flagged += is_flagged
        results.append({"file": str(path), "markers": markers, "flagged": is_flagged})
        if not as_json:
            print(f"{'FLAGGED' if is_flagged else 'clean   '} {path}: {markers}" if is_flagged
                  else f"clean    {path}")
    if as_json:
        import json
        print(json.dumps({"scanned": len(results), "flagged": flagged, "files": results}, indent=2))
    else:
        print(f"\nScanned {len(results)} file(s); {flagged} carry provenance markers.")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
