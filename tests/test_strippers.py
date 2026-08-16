"""Tests for the skill scripts. Office/scan tests use the stdlib only; the image
test is skipped when Pillow is unavailable."""
import importlib.util
import io
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def load(rel):
    path = SKILLS / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_docx(path):
    core = (
        b'<?xml version="1.0"?><cp:coreProperties xmlns:cp="c" xmlns:dc="d">'
        b"<dc:creator>Claude (Anthropic)</dc:creator>"
        b"<cp:lastModifiedBy>Claude</cp:lastModifiedBy></cp:coreProperties>"
    )
    app = (
        b'<?xml version="1.0"?><Properties xmlns="e">'
        b"<Application>Claude Code</Application><Company>Anthropic</Company></Properties>"
    )
    body = b'<?xml version="1.0"?><w:document xmlns:w="x"><w:body><w:t>About Claude usage</w:t></w:body></w:document>'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"<Types/>")
        z.writestr("word/document.xml", body)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)


class DocumentStripperTests(unittest.TestCase):
    def setUp(self):
        self.doc = load("document-metadata-stripper/scripts/strip_document_metadata.py")

    def test_office_strip_removes_markers_and_keeps_body(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "s.docx"
            make_docx(src)
            self.assertTrue(self.doc.scan_office(src))  # markers present before
            out = Path(d) / "s_clean.docx"
            self.doc.strip_office(src, out)
            self.assertEqual(self.doc.scan_office(out), [])  # none after
            with zipfile.ZipFile(out) as z:
                self.assertIn(b"About Claude usage", z.read("word/document.xml"))
                self.assertEqual(set(z.namelist()) & set(self.doc.OOXML_META_PARTS),
                                 {"docProps/core.xml", "docProps/app.xml"})


def make_docx_with_revisions(path):
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    document = (
        '<?xml version="1.0"?>'
        f'<w:document xmlns:w="{W}"><w:body>'
        '<w:p w:rsidR="00AB12CD">'
        '<w:r><w:t>Kept. </w:t></w:r>'
        '<w:ins w:id="1" w:author="R"><w:r><w:t>INS_KEEP</w:t></w:r></w:ins>'
        '<w:del w:id="2"><w:r><w:delText>DEL_SECRET</w:delText></w:r></w:del>'
        '<w:commentRangeStart w:id="0"/><w:commentRangeEnd w:id="0"/>'
        '<w:r><w:commentReference w:id="0"/></w:r>'
        '</w:p></w:body></w:document>'
    ).encode()
    comments = (f'<?xml version="1.0"?><w:comments xmlns:w="{W}">'
                '<w:comment w:id="0"><w:p><w:r><w:t>SECRET_NOTE</w:t></w:r></w:p></w:comment></w:comments>').encode()
    settings = (f'<?xml version="1.0"?><w:settings xmlns:w="{W}">'
                '<w:rsids><w:rsid w:val="00AB12CD"/></w:rsids></w:settings>').encode()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"<Types/>")
        z.writestr("word/document.xml", document)
        z.writestr("word/comments.xml", comments)
        z.writestr("word/settings.xml", settings)


class DeepCleanTests(unittest.TestCase):
    def setUp(self):
        self.doc = load("document-metadata-stripper/scripts/strip_document_metadata.py")

    def test_default_keeps_revisions_deep_removes_them(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "r.docx"
            make_docx_with_revisions(src)

            # Default strip: deep content remains.
            shallow = Path(d) / "shallow.docx"
            self.doc.strip_office(src, shallow, deep=False)
            with zipfile.ZipFile(shallow) as z:
                self.assertIn(b"DEL_SECRET", z.read("word/document.xml"))
                self.assertIn(b"SECRET_NOTE", z.read("word/comments.xml"))

            # Deep strip: revisions/comments/rsids gone, insertion accepted, body kept.
            deep = Path(d) / "deep.docx"
            self.doc.strip_office(src, deep, deep=True)
            with zipfile.ZipFile(deep) as z:
                doc = z.read("word/document.xml")
                self.assertIn(b"Kept.", doc)
                self.assertIn(b"INS_KEEP", doc)      # insertion accepted
                self.assertNotIn(b"<w:ins", doc)
                self.assertNotIn(b"DEL_SECRET", doc)  # deletion dropped
                self.assertNotIn(b"commentReference", doc)
                self.assertNotIn(b"w:rsid", doc)
                self.assertNotIn(b"SECRET_NOTE", z.read("word/comments.xml"))


def make_docx_with_hidden_and_ole(path):
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    document = (
        '<?xml version="1.0"?>'
        f'<w:document xmlns:w="{W}"><w:body><w:p>'
        '<w:r><w:t>Visible.</w:t></w:r>'
        '<w:r><w:rPr><w:vanish/></w:rPr><w:t>HIDDEN_SECRET</w:t></w:r>'
        '<w:r><w:rPr><w:vanish w:val="false"/></w:rPr><w:t>NOT_HIDDEN</w:t></w:r>'
        '<w:r><w:object><o:OLEObject r:id="rId5" xmlns:o="urn:o" xmlns:r="urn:r"/></w:object></w:r>'
        '</w:p></w:body></w:document>'
    ).encode()
    rels = (
        b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Id="rId5" Type="urn:oleObject" Target="embeddings/oleObject1.bin"/>'
        b'<Relationship Id="rId1" Type="urn:settings" Target="settings.xml"/></Relationships>'
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"<Types/>")
        z.writestr("word/document.xml", document)
        z.writestr("word/_rels/document.xml.rels", rels)
        z.writestr("word/embeddings/oleObject1.bin", b"OLE_PAYLOAD_SECRET")


class DeepHiddenOleTests(unittest.TestCase):
    def setUp(self):
        self.doc = load("document-metadata-stripper/scripts/strip_document_metadata.py")

    def test_deep_removes_hidden_text_and_ole(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "o.docx"
            make_docx_with_hidden_and_ole(src)
            out = Path(d) / "o_clean.docx"
            self.doc.strip_office(src, out, deep=True)
            with zipfile.ZipFile(out) as z:
                doc = z.read("word/document.xml")
                rels = z.read("word/_rels/document.xml.rels")
                self.assertIn(b"Visible.", doc)
                self.assertNotIn(b"HIDDEN_SECRET", doc)     # hidden run dropped
                self.assertIn(b"NOT_HIDDEN", doc)           # w:val="false" kept
                self.assertNotIn(b"<w:object", doc)          # OLE reference removed
                self.assertNotIn("word/embeddings/oleObject1.bin", z.namelist())
                self.assertNotIn(b"embeddings/oleObject1.bin", rels)
                self.assertIn(b"settings.xml", rels)         # other rels intact


class ProvenanceScanTests(unittest.TestCase):
    def setUp(self):
        self.scan = load("provenance-scan/scripts/provenance_scan.py")

    def test_flags_docx_and_returns_nonzero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            make_docx(Path(d) / "s.docx")
            rc = self.scan.main([d])
            self.assertEqual(rc, 1)  # provenance found -> exit 1

    def test_clean_dir_returns_zero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "notes.txt").write_text("plain text, no markers")
            rc = self.scan.main([d])
            self.assertEqual(rc, 0)


class ProvenanceScanJsonTests(unittest.TestCase):
    def test_json_output_shape(self):
        import io
        import json
        import tempfile
        from contextlib import redirect_stdout
        scan = load("provenance-scan/scripts/provenance_scan.py")
        with tempfile.TemporaryDirectory() as d:
            make_docx(Path(d) / "s.docx")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = scan.main(["--json", d])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["flagged"], 1)
            self.assertTrue(payload["files"][0]["flagged"])
            self.assertIn("Claude", payload["files"][0]["markers"])


class StripAllTests(unittest.TestCase):
    def test_dispatches_office_to_document_stripper(self):
        import tempfile
        strip_all = load("strip-all/scripts/strip_all.py")
        with tempfile.TemporaryDirectory() as d:
            make_docx(Path(d) / "s.docx")
            rc = strip_all.main([d])
            self.assertEqual(rc, 0)
            self.assertTrue((Path(d) / "s_clean.docx").is_file())  # routed + cleaned


class ImageStripperTests(unittest.TestCase):
    def test_png_text_chunk_removed(self):
        try:
            from PIL import Image, PngImagePlugin
        except ImportError:
            self.skipTest("Pillow not installed")
        import tempfile
        mod = load("image-watermark-stripper/scripts/strip_metadata.py")
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "img.png"
            out = Path(d) / "img_clean.png"
            info = PngImagePlugin.PngInfo()
            info.add_text("provenance", "Made with Claude / Anthropic")
            Image.new("RGB", (8, 8), (200, 10, 10)).save(src, pnginfo=info)
            self.assertTrue(mod.scan(src))  # marker present
            mod.strip_raster(src, out)
            self.assertEqual(mod.scan(out), [])  # gone after


if __name__ == "__main__":
    unittest.main()
