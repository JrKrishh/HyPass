# Skills Index

Catalog of skills in this repository. Each skill lives under `skills/<name>/` with a `SKILL.md` (name, description, and license frontmatter) that Claude Code loads on demand. The repo is packaged as a Claude Code plugin (`hypass`) so all skills install together — see [README.md](README.md).

| Skill | Purpose | Trigger when | Files |
|-------|---------|--------------|-------|
| [document-metadata-stripper](skills/document-metadata-stripper/SKILL.md) | Strip authoring/provenance metadata from Office documents (.docx/.pptx/.xlsx + variants) and PDFs. | Removing author/company/Claude tags from a document, or checking whether one carries provenance metadata. | `SKILL.md`, `scripts/strip_document_metadata.py` |
| [git-human-commits](skills/git-human-commits/SKILL.md) | Keep commits and PRs attributed only to the account holder (JrKrishh), with human-style messages and no Claude/AI attribution trailers or footers. | Making a commit, opening a PR, or auditing git history for AI attribution. | `SKILL.md` |
| [image-watermark-stripper](skills/image-watermark-stripper/SKILL.md) | Strip AI provenance metadata (C2PA, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files. | Removing watermarks/AI tags/metadata from images, or checking whether an image carries provenance tags. | `SKILL.md`, `scripts/strip_metadata.py` |
| [media-metadata-stripper](skills/media-metadata-stripper/SKILL.md) | Strip metadata from audio/video files (mp3/mp4/mov/wav/...) with ffmpeg, no re-encode. | Removing tags/author/Claude markers from a media file, or checking what tags it carries. | `SKILL.md`, `scripts/strip_media_metadata.py` |
| [provenance-scan](skills/provenance-scan/SKILL.md) | Read-only audit of files/folders for Claude/C2PA provenance markers across images, documents, and PDFs. Supports `--json` and a pre-commit hook. | Checking which files in a project carry provenance before publishing; no modification. | `SKILL.md`, `scripts/provenance_scan.py`, `hooks/pre-commit` |
| [strip-all](skills/strip-all/SKILL.md) | One command that auto-detects file type and routes each file to the right stripper (image/document/media). | Cleaning a whole folder or a mixed set of files at once. | `SKILL.md`, `scripts/strip_all.py` |
| [text-watermark](skills/text-watermark/SKILL.md) | Explain and handle the invisible text watermark no stripper can remove, with a human-rewrite checklist. | Asked to remove the SynthID/text watermark, or why the file strippers don't touch text. | `SKILL.md` |

## Details

### document-metadata-stripper
- **Directory:** `skills/document-metadata-stripper/`
- **License:** MIT
- **Description:** Strip authoring/provenance metadata from Office documents and PDFs, or check whether a document carries it.
- **Entry point:** `scripts/strip_document_metadata.py [--check] [--deep] <file>` — writes `<name>_clean.<ext>` (or scans only with `--check`).
- **Formats:** `.docx/.docm/.dotx/.dotm`, `.xlsx/.xlsm/.xltx/.xltm`, `.pptx/.pptm/.potx/.potm` via stdlib; `.pdf` via pikepdf or pypdf.
- **Deep clean:** `--deep` also removes tracked changes, comments, RSIDs, hidden text, and embedded OLE objects (Word), or annotations, attachments, JavaScript, and revision history (PDF).

### git-human-commits
- **Directory:** `skills/git-human-commits/`
- **License:** MIT
- **Description:** Ensure commits and PRs are authored only by the GitHub account holder (JrKrishh), with no Claude attribution trailers or "Generated with Claude Code" footers, and human-style commit/PR text.
- **Covers:** authorship checks (`user.name`/`user.email`), commit message style, PR description style, and flag-and-verify commands for auditing history.

### image-watermark-stripper
- **Directory:** `skills/image-watermark-stripper/`
- **License:** MIT
- **Description:** Strip AI provenance metadata (C2PA content credentials, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files.
- **Entry point:** `scripts/strip_metadata.py <image>` — writes `<name>_clean.<ext>` and reports provenance markers found before/after.
- **Formats:** PNG/JPEG/WebP/GIF/BMP/TIFF via Pillow; SVG via metadata/comment removal. HEIC/AVIF need extra Pillow plugins.
- **Modes:** `--check` scans and reports without writing.

### media-metadata-stripper
- **Directory:** `skills/media-metadata-stripper/`
- **License:** MIT
- **Description:** Strip container/stream metadata from audio and video by remuxing with ffmpeg (no re-encode).
- **Entry point:** `scripts/strip_media_metadata.py [--check] <file>` — writes `<name>_clean.<ext>`.
- **Formats:** `.mp3/.mp4/.m4a/.mov/.wav/.flac/.avi/.mkv/.webm`. Needs ffmpeg/ffprobe on PATH.

### provenance-scan
- **Directory:** `skills/provenance-scan/`
- **License:** MIT
- **Description:** Read-only auditor that reports which files carry Claude/C2PA provenance markers. The detect side to the strippers' remove side.
- **Entry point:** `scripts/provenance_scan.py [--json] <path> [path ...]` — walks files/dirs, prints `FLAGGED`/`clean` per file; exit `1` if any flagged (CI/pre-publish gate). Stdlib only.
- **Extras:** `--json` for machine-readable output; `hooks/pre-commit` blocks committing files with provenance markers.

### strip-all
- **Directory:** `skills/strip-all/`
- **License:** MIT
- **Description:** Dispatcher that auto-detects each file's type and runs the matching stripper. Write-side companion to provenance-scan.
- **Entry point:** `scripts/strip_all.py [--check] <path> [path ...]` — routes images/SVG, Office/PDF, and audio/video to the right skill via subprocess. Relies on the sibling strippers being installed.

### text-watermark
- **Directory:** `skills/text-watermark/`
- **License:** MIT
- **Description:** Guidance (no script) on the SynthID-style text watermark that no metadata stripper removes, plus a human-rewrite checklist for degrading it.

## Install

One step in Claude Code — `/plugin marketplace add JrKrishh/HyPass` then `/plugin install hypass@hypass` — installs all skills at once. Manual `install.ps1`/`install.sh` and full details are in [README.md](README.md). Python deps for the stripper scripts: `pip install -r requirements.txt`.
