#!/usr/bin/env python3
"""Strip authoring/provenance metadata from Office (.docx/.pptx/.xlsx) and PDF files.

Office formats (Open XML) are handled with the standard library only. PDF needs
pikepdf or pypdf installed; without one, PDFs are reported and skipped.

Usage:
    strip_document_metadata.py <file> [file ...]      # strip -> <name>_clean.<ext>
    strip_document_metadata.py --check <file> [...]   # scan only, write nothing
"""
import re
import sys
import zipfile
from pathlib import Path

# Provenance / authoring tokens the scan reports on.
MARKERS = [
    b"Claude", b"claude", b"Anthropic", b"anthropic",
    b"Made with Claude", b"made with claude", b"C2PA", b"c2pa",
]

# Open XML metadata parts (Word/Excel/PowerPoint share these).
OOXML_META_PARTS = ("docProps/core.xml", "docProps/app.xml", "docProps/custom.xml")

# Tags in core.xml / app.xml whose text content carries authorship/provenance.
SENSITIVE_TAGS = [
    "dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject",
    "dc:description", "cp:keywords", "cp:category", "cp:contentStatus",
    "Company", "Manager", "Application", "AppVersion",
]

OFFICE_SUFFIXES = {
    ".docx", ".docm", ".dotx", ".dotm",
    ".xlsx", ".xlsm", ".xltx", ".xltm",
    ".pptx", ".pptm", ".potx", ".potm",
}

# <property ...>...</property> blocks in custom.xml (custom props / tracking tags).
CUSTOM_PROP_RE = re.compile(rb"<property\b.*?</property>", re.S)


def scan_bytes(data):
    return sorted({m.decode("latin-1") for m in MARKERS if m in data})


def _blank_tag_text(xml_bytes):
    for tag in SENSITIVE_TAGS:
        pat = re.compile(
            rb"(<" + tag.encode() + rb"[^>]*>).*?(</" + tag.encode() + rb">)", re.S
        )
        xml_bytes = pat.sub(rb"\1\2", xml_bytes)
    return xml_bytes


def _transform_meta_part(name, data):
    if name == "docProps/custom.xml":
        return CUSTOM_PROP_RE.sub(b"", data)
    return _blank_tag_text(data)


def scan_office(path):
    """Scan only the metadata parts, so body text mentioning Claude isn't a hit."""
    found = set()
    with zipfile.ZipFile(path) as zin:
        names = set(zin.namelist())
        for part in OOXML_META_PARTS:
            if part in names:
                found.update(scan_bytes(zin.read(part)))
    return sorted(found)


def strip_office(src, out):
    with zipfile.ZipFile(src) as zin:
        infos = zin.infolist()
        with zipfile.ZipFile(out, "w") as zout:
            for info in infos:
                data = zin.read(info.filename)
                if info.filename in OOXML_META_PARTS:
                    data = _transform_meta_part(info.filename, data)
                # Preserve per-entry compression type.
                zout.writestr(info, data, compress_type=info.compress_type)


def _pdf_backend():
    try:
        import pikepdf  # noqa: F401
        return "pikepdf"
    except ImportError:
        pass
    try:
        import pypdf  # noqa: F401
        return "pypdf"
    except ImportError:
        return None


def scan_pdf(path):
    return scan_bytes(path.read_bytes())


def strip_pdf(src, out, backend):
    if backend == "pikepdf":
        import pikepdf
        with pikepdf.open(src) as pdf:
            pdf.docinfo = pikepdf.Dictionary()  # clear /Info (Author, Producer, ...)
            if "/Metadata" in pdf.Root:
                del pdf.Root.Metadata  # drop XMP stream
            pdf.save(out)
    else:  # pypdf
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(str(src))
        writer = PdfWriter()
        writer.append(reader)
        writer.add_metadata({})
        try:
            writer.xmp_metadata = None  # drop XMP where supported
        except Exception:
            pass
        with open(out, "wb") as fh:
            writer.write(fh)


def process(arg, check_only):
    src = Path(arg)
    if not src.is_file():
        print(f"SKIP {arg}: not found")
        return
    suffix = src.suffix.lower()

    if suffix in OFFICE_SUFFIXES:
        before = scan_office(src)
        if check_only:
            print(f"{src.name}: markers={before or 'none'} (check only)")
            return
        out = src.with_name(f"{src.stem}_clean{src.suffix}")
        strip_office(src, out)
        print(f"{src.name}: markers before={before or 'none'} after={scan_office(out) or 'none'} -> {out.name}")
        return

    if suffix == ".pdf":
        before = scan_pdf(src)
        if check_only:
            print(f"{src.name}: markers={before or 'none'} (check only)")
            return
        backend = _pdf_backend()
        if not backend:
            print(f"SKIP {src.name}: PDF support needs pikepdf or pypdf (pip install pikepdf). markers={before or 'none'}")
            return
        out = src.with_name(f"{src.stem}_clean{src.suffix}")
        strip_pdf(src, out, backend)
        print(f"{src.name}: markers before={before or 'none'} after={scan_pdf(out) or 'none'} -> {out.name} [{backend}]")
        return

    print(f"SKIP {src.name}: unsupported type {suffix} (handled: {', '.join(sorted(OFFICE_SUFFIXES))}, .pdf)")


def main(argv):
    check_only = False
    args = []
    for a in argv:
        if a in ("--check", "-c"):
            check_only = True
        else:
            args.append(a)
    if not args:
        print("usage: strip_document_metadata.py [--check] <file> [file ...]")
        return 1
    for arg in args:
        process(arg, check_only)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
