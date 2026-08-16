---
name: document-metadata-stripper
description: Strip authoring/provenance metadata from Office documents (.docx/.pptx/.xlsx and their macro/template variants) and PDFs. Use when the user asks to remove author, company, "Made with Claude"/Anthropic tags, or tracking metadata from a document, to clean a generated document, or to check whether a document carries provenance metadata.
license: MIT
---

# Document Metadata Stripper

Removes authoring and provenance metadata from documents. Office files (Open XML) store creator, last-modified-by, company, application, and custom properties in `docProps/core.xml`, `docProps/app.xml`, and `docProps/custom.xml`; PDFs store it in the `/Info` dictionary and an XMP stream. This skill clears those without touching the document body.

Companion to `image-watermark-stripper` (images) - it covers the document formats Claude Code generates, which the image tool doesn't reach.

## When to use

- "remove my name / the author from this document"
- "clean this docx/pptx/xlsx/pdf of Claude or Anthropic tags"
- "check if this document has provenance metadata"

## How to run

Requires Python 3. Office formats work with the standard library alone. PDF needs `pikepdf` (preferred) or `pypdf`: `pip install pikepdf`.

Strip (writes `<name>_clean.<ext>` next to the original):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/document-metadata-stripper/scripts/strip_document_metadata.py" "path/to/file.docx"
```

Check only (scans and reports, writes nothing):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/document-metadata-stripper/scripts/strip_document_metadata.py" --check "path/to/file.docx"
```

`${CLAUDE_PLUGIN_ROOT}` is set automatically for plugin installs; for a manual `~/.claude/skills` install, use that path instead.

### Deep clean (`--deep`)

Add `--deep` to also remove hidden content the default pass leaves behind:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/document-metadata-stripper/scripts/strip_document_metadata.py" --deep "path/to/file.docx"
```

- **Word:** accepts tracked insertions (keeps the text), drops tracked deletions (removes the text), strips revision records and comments, and removes revision-save IDs (RSIDs).
- **PDF:** removes annotations, embedded file attachments, JavaScript/auto-run actions, and rewrites the file so prior incremental-revision history is discarded.

`--deep` changes document content (it finalizes tracked changes), so it is opt-in; the default pass touches metadata only.

## What it does

1. Scans the metadata parts (not the body) for provenance tokens (Claude, Anthropic, "Made with Claude", C2PA)
2. Office: blanks `dc:creator`, `cp:lastModifiedBy`, title/subject/description/keywords, `Company`, `Manager`, `Application`, `AppVersion` in core/app props, and drops all custom `<property>` entries - then rewrites the package with the rest of its parts byte-for-byte
3. PDF: clears the `/Info` dictionary and removes the XMP `/Metadata` stream
4. Re-scans the output to confirm the markers are gone
5. With `--deep`: additionally removes tracked changes, comments, and RSIDs (Word) or annotations, attachments, JavaScript, and revision history (PDF)

## Limitations

- Office handled with stdlib; PDF needs pikepdf or pypdf installed (without one, PDFs are reported and skipped, not silently passed). `--deep` PDF cleaning needs pikepdf for the full set (annotations/attachments/JS); pypdf handles annotations only
- The scan is a token heuristic over the metadata parts (C2PA/Claude/Anthropic), not a full metadata dump - use a viewer for an exhaustive audit
- Only metadata is removed by default; text watermarks woven into the document's prose are unaffected and only degrade with a genuine human rewrite
- `--deep` Word cleaning targets tracked changes/comments/RSIDs; it does not remove hidden text (`w:vanish`) or embedded OLE objects
- Handled: `.docx/.docm/.dotx/.dotm`, `.xlsx/.xlsm/.xltx/.xltm`, `.pptx/.pptm/.potx/.potm`, `.pdf`. Legacy `.doc/.xls/.ppt` are not supported
