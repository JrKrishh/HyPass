---
name: strip-all
description: One command to strip provenance/metadata from any supported file - images, Office documents, PDFs, and audio/video - by auto-detecting the type and routing to the right stripper. Use when the user wants to clean a whole folder or a mixed set of files at once, rather than picking a specific stripper.
license: MIT
---

# Strip All

Dispatcher over the other stripper skills. Point it at files or folders; it detects each file's type and runs the matching stripper (image, document, or media). The write-side companion to `provenance-scan`'s read-side audit.

## When to use

- "clean this whole folder of AI provenance"
- "strip metadata from all these files" (mixed images/docs/media)
- one command instead of choosing a stripper per file

## How to run

Requires Python 3. Depends on the other stripper skills being installed alongside it (they are, if you ran the installer). Each underlying stripper has its own dependencies: Pillow for images, pikepdf for PDFs, ffmpeg for audio/video.

```powershell
python "$env:USERPROFILE\.claude\skills\strip-all\scripts\strip_all.py" "path\to\folder"
```

Check only (report via each stripper's `--check`, write nothing):

```powershell
python "$env:USERPROFILE\.claude\skills\strip-all\scripts\strip_all.py" --check "path\to\folder"
```

macOS/Linux: `python ~/.claude/skills/strip-all/scripts/strip_all.py <path>`.

## What it does

1. Walks the given files/folders (directories recursively)
2. Routes each file by extension: images/SVG -> `image-watermark-stripper`; Office/PDF -> `document-metadata-stripper`; audio/video -> `media-metadata-stripper`
3. Runs that stripper as a subprocess, so each skill keeps its own dependencies and logic (single source of truth, no duplicated code)
4. Unsupported file types are skipped silently

## Limitations

- Relies on the sibling skills being installed under the same skills root; if one is missing it reports and skips those files
- Inherits each underlying stripper's limits (e.g. PDF needs pikepdf, media needs ffmpeg)
- Writes `<name>_clean.<ext>` copies via the underlying strippers; it does not delete or overwrite originals
