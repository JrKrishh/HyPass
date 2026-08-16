#!/usr/bin/env python3
"""Strip authoring/provenance metadata from Office (.docx/.pptx/.xlsx) and PDF files.

Office formats (Open XML) are handled with the standard library only. PDF needs
pikepdf or pypdf installed; without one, PDFs are reported and skipped.

Usage:
    strip_document_metadata.py <file> [file ...]      # strip -> <name>_clean.<ext>
    strip_document_metadata.py --check <file> [...]   # scan only, write nothing
    strip_document_metadata.py --deep <file> [...]    # also remove deep/hidden data

--deep additionally removes hidden content that the default pass leaves behind:
  Word:  tracked changes (accepts insertions, drops deletions), revision records,
         comments, and revision-save IDs (RSIDs).
  PDF:   annotations, embedded file attachments, JavaScript/open actions, and the
         document's prior incremental-revision history (rewritten clean).
Default (non-deep) behavior is unchanged.
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

# --- Deep-clean patterns (Word) ---
# RSIDs (revision-save IDs) correlate edits/sessions; safe to remove.
RSID_ATTR_RE = re.compile(rb'\s+w:rsid[A-Za-z]*="[^"]*"')
RSIDS_BLOCK_RE = re.compile(rb"<w:rsids>.*?</w:rsids>", re.S)
# Tracked changes: unwrap insertions (keep text), drop deletions (remove text).
INS_RE = re.compile(rb"<w:ins\b[^>]*>(.*?)</w:ins>", re.S)
DEL_RE = re.compile(rb"<w:del\b[^>]*>.*?</w:del>", re.S)
# Revision records inside pPr/rPr/tblPr/etc.
_CHANGE_TAGS = "pPrChange|rPrChange|tblPrChange|trPrChange|tcPrChange|sectPrChange|numberingChange"
CHANGE_RE = re.compile(rb"<w:(" + _CHANGE_TAGS.encode() + rb")\b.*?</w:\1>", re.S)
CHANGE_EMPTY_RE = re.compile(rb"<w:(?:" + _CHANGE_TAGS.encode() + rb")\b[^>]*/>")
# Comment anchors/markers left in document.xml.
COMMENT_REF_RE = re.compile(
    rb"<w:commentRangeStart\b[^>]*/>|<w:commentRangeEnd\b[^>]*/>|<w:commentReference\b[^>]*/>"
)
# Hidden text: a run whose properties carry an active <w:vanish/> (not w:val="false").
RUN_RE = re.compile(rb"<w:r\b[^>]*>.*?</w:r>", re.S)
ACTIVE_VANISH_RE = re.compile(rb'<w:vanish(?:\s+w:val="(?:true|1|on)")?\s*/>')
# Embedded OLE objects: the <w:object> reference in document.xml, the embedding
# parts, and their relationship entries.
OBJECT_RE = re.compile(rb"<w:object\b.*?</w:object>", re.S)
EMBED_REL_RE = re.compile(rb'<Relationship\b[^>]*Target="[^"]*embeddings/[^"]*"[^>]*/>')
EMBED_PART_PREFIX = "word/embeddings/"


def _drop_hidden_runs(data):
    def repl(m):
        run = m.group(0)
        return b"" if ACTIVE_VANISH_RE.search(run) else run
    return RUN_RE.sub(repl, data)
# Comment/author side-parts to empty out (keeps the part valid; drops the content).
COMMENT_PARTS = (
    "word/comments.xml", "word/commentsExtended.xml",
    "word/commentsIds.xml", "word/commentsExtensible.xml", "word/people.xml",
)
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
EMPTY_COMMENTS = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<w:comments xmlns:w="' + _W_NS.encode() + b'"/>'
)
EMPTY_PEOPLE = (
    b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    b'<w15:people xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"/>'
)


def deep_clean_document_xml(data):
    prev = None
    while prev != data:  # unwrap possibly-nested insertions
        prev = data
        data = INS_RE.sub(rb"\1", data)
    data = DEL_RE.sub(b"", data)
    data = CHANGE_RE.sub(b"", data)
    data = CHANGE_EMPTY_RE.sub(b"", data)
    data = COMMENT_REF_RE.sub(b"", data)
    data = OBJECT_RE.sub(b"", data)      # embedded OLE object references
    data = _drop_hidden_runs(data)       # hidden text runs
    data = RSID_ATTR_RE.sub(b"", data)
    return data


def deep_clean_settings_xml(data):
    data = RSIDS_BLOCK_RE.sub(b"", data)
    data = RSID_ATTR_RE.sub(b"", data)
    return data


def _deep_transform(name, data):
    if name == "word/document.xml":
        return deep_clean_document_xml(data)
    if name == "word/settings.xml":
        return deep_clean_settings_xml(data)
    if name == "word/_rels/document.xml.rels":
        return EMBED_REL_RE.sub(b"", data)  # drop rels to removed OLE parts
    if name == "word/people.xml":
        return EMPTY_PEOPLE
    if name in COMMENT_PARTS:
        return EMPTY_COMMENTS
    return data


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


def strip_office(src, out, deep=False):
    with zipfile.ZipFile(src) as zin:
        infos = zin.infolist()
        with zipfile.ZipFile(out, "w") as zout:
            for info in infos:
                name = info.filename
                if deep and name.startswith(EMBED_PART_PREFIX):
                    continue  # drop embedded OLE object parts entirely
                data = zin.read(name)
                if name in OOXML_META_PARTS:
                    data = _transform_meta_part(name, data)
                elif deep:
                    data = _deep_transform(name, data)
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


def strip_pdf(src, out, backend, deep=False):
    if backend == "pikepdf":
        import pikepdf
        with pikepdf.open(src) as pdf:
            pdf.docinfo = pikepdf.Dictionary()  # clear /Info (Author, Producer, ...)
            if "/Metadata" in pdf.Root:
                del pdf.Root.Metadata  # drop XMP stream
            if deep:
                for page in pdf.pages:
                    if "/Annots" in page:
                        del page.Annots  # annotations, comments, form widgets
                root = pdf.Root
                names = root.get("/Names")
                if names is not None:
                    for key in ("/EmbeddedFiles", "/JavaScript"):
                        if key in names:
                            del names[key]
                for key in ("/OpenAction", "/AA"):  # auto-run actions
                    if key in root:
                        del root[key]
                acro = root.get("/AcroForm")
                if acro is not None and "/XFA" in acro:
                    del acro.XFA  # XFA can carry a full data payload
            # pikepdf writes a fresh file (non-incremental), so any prior
            # incremental-revision history is dropped automatically.
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
        if deep:
            for page in writer.pages:
                if "/Annots" in page:
                    del page["/Annots"]
        with open(out, "wb") as fh:
            writer.write(fh)


def process(arg, check_only, deep=False):
    src = Path(arg)
    if not src.is_file():
        print(f"SKIP {arg}: not found")
        return
    suffix = src.suffix.lower()
    tag = " [deep]" if deep else ""

    if suffix in OFFICE_SUFFIXES:
        before = scan_office(src)
        if check_only:
            print(f"{src.name}: markers={before or 'none'} (check only)")
            return
        out = src.with_name(f"{src.stem}_clean{src.suffix}")
        strip_office(src, out, deep=deep)
        print(f"{src.name}: markers before={before or 'none'} after={scan_office(out) or 'none'} -> {out.name}{tag}")
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
        strip_pdf(src, out, backend, deep=deep)
        print(f"{src.name}: markers before={before or 'none'} after={scan_pdf(out) or 'none'} -> {out.name} [{backend}]{tag}")
        return

    print(f"SKIP {src.name}: unsupported type {suffix} (handled: {', '.join(sorted(OFFICE_SUFFIXES))}, .pdf)")


def main(argv):
    check_only = False
    deep = False
    args = []
    for a in argv:
        if a in ("--check", "-c"):
            check_only = True
        elif a == "--deep":
            deep = True
        else:
            args.append(a)
    if not args:
        print("usage: strip_document_metadata.py [--check] [--deep] <file> [file ...]")
        return 1
    for arg in args:
        process(arg, check_only, deep=deep)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
