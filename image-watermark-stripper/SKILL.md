---
name: image-watermark-stripper
description: Strip AI provenance metadata (C2PA content credentials, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files. Use when the user asks to remove watermarks, Claude tags, AI labels, or metadata from images, to clean generated images, or to check whether an image carries provenance tags.
license: MIT
---

# Image Watermark Stripper

Removes machine-readable provenance metadata from images. Claude marks files (.png/.jpg/.svg) with signed C2PA content credentials stored in file metadata (Anthropic, Aug 2026 - EU AI Act compliance). This skill strips those tags.

## When to use

- "remove the watermark from this image"
- "clean this image of Claude/AI tags"
- "check if this image has provenance metadata"

## How to run

Requires Python 3 with Pillow: `pip install Pillow` (or `pip install -r requirements.txt` from the repo root).

Strip (writes `<name>_clean.<ext>` next to the original):

```powershell
python "$env:USERPROFILE\.claude\skills\image-watermark-stripper\scripts\strip_metadata.py" "path\to\image.png"
```

Check only (scans and reports, writes nothing):

```powershell
python "$env:USERPROFILE\.claude\skills\image-watermark-stripper\scripts\strip_metadata.py" --check "path\to\image.png"
```

macOS/Linux: `python ~/.claude/skills/image-watermark-stripper/scripts/strip_metadata.py <image>`.

The script prints the provenance markers found before and after. The scan is a token heuristic covering C2PA/JUMBF/XMP and Claude/Anthropic markers; EXIF and IPTC are stripped but not individually reported by the scan.

## What it does

1. Byte-scans the file for provenance markers
2. Re-encodes the image with Pillow, clearing the metadata dictionary (drops EXIF, XMP, IPTC, C2PA/JUMBF, PNG tEXt/iTXt/zTXt chunks)
3. Keeps the ICC color profile for JPEG/PNG/WebP (color correctness; carries no provenance)
4. SVG: removes `<metadata>` blocks and XML comments
5. Re-scans the output to verify markers are gone

## Verification

- Marker scan before/after in the script output
- Optional, if exiftool is installed: `exiftool -all= -o out.png in.png`
- Anthropic ships a drop-in C2PA checker ("coming soon") - use it to confirm

## Limitations

- Only metadata-level tags. Current Claude file marking is C2PA metadata only; nothing is embedded in pixels. (Invisible pixel watermarks from other tools may survive re-encoding.)
- JPEG is re-encoded (quality 95) - minor generation loss, invisible in practice
- PNG/JPEG/WebP/GIF/BMP/TIFF handled via Pillow; HEIC/AVIF need extra Pillow plugins
- C2PA removal is permanent - it cannot be recovered once stripped
