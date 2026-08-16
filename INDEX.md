# Skills Index

Catalog of skills in this repository. Each skill lives in its own directory with a `SKILL.md` (name + description frontmatter) that Claude Code loads on demand.

| Skill | Purpose | Trigger when | Files |
|-------|---------|--------------|-------|
| [document-metadata-stripper](document-metadata-stripper/SKILL.md) | Strip authoring/provenance metadata from Office documents (.docx/.pptx/.xlsx + variants) and PDFs. | Removing author/company/Claude tags from a document, or checking whether one carries provenance metadata. | `SKILL.md`, `scripts/strip_document_metadata.py` |
| [git-human-commits](git-human-commits/SKILL.md) | Keep commits and PRs attributed only to the account holder (JrKrishh), with human-style messages and no Claude/AI attribution trailers or footers. | Making a commit, opening a PR, or auditing git history for AI attribution. | `SKILL.md` |
| [image-watermark-stripper](image-watermark-stripper/SKILL.md) | Strip AI provenance metadata (C2PA, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files. | Removing watermarks/AI tags/metadata from images, or checking whether an image carries provenance tags. | `SKILL.md`, `scripts/strip_metadata.py` |

## Details

### document-metadata-stripper
- **Directory:** `document-metadata-stripper/`
- **License:** MIT
- **Description:** Strip authoring/provenance metadata from Office documents and PDFs, or check whether a document carries it.
- **Entry point:** `scripts/strip_document_metadata.py [--check] <file>` — writes `<name>_clean.<ext>` (or scans only with `--check`).
- **Formats:** `.docx/.docm/.dotx/.dotm`, `.xlsx/.xlsm/.xltx/.xltm`, `.pptx/.pptm/.potx/.potm` via stdlib; `.pdf` via pikepdf or pypdf.

### git-human-commits
- **Directory:** `git-human-commits/`
- **License:** MIT
- **Description:** Ensure commits and PRs are authored only by the GitHub account holder (JrKrishh), with no Claude attribution trailers or "Generated with Claude Code" footers, and human-style commit/PR text.
- **Covers:** authorship checks (`user.name`/`user.email`), commit message style, PR description style, and flag-and-verify commands for auditing history.

### image-watermark-stripper
- **Directory:** `image-watermark-stripper/`
- **License:** MIT
- **Description:** Strip AI provenance metadata (C2PA content credentials, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files.
- **Entry point:** `scripts/strip_metadata.py <image>` — writes `<name>_clean.<ext>` and reports provenance markers found before/after.
- **Formats:** PNG/JPEG/WebP/GIF/BMP/TIFF via Pillow; SVG via metadata/comment removal. HEIC/AVIF need extra Pillow plugins.

## Install

See [README.md](README.md). `install.ps1` copies every skill directory into `%USERPROFILE%\.claude\skills\`; restart Claude Code to load them.
