# claude-skills

Personal Claude Code skills for clean, human-owned output.

## Skills

See [INDEX.md](INDEX.md) for the full catalog with per-skill details.

### image-watermark-stripper

Strips AI provenance metadata (C2PA content credentials, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files. Claude marks `.png`/`.jpg`/`.svg` with signed C2PA credentials (Anthropic, Aug 2026 - EU AI Act). Runs `strip_metadata.py`, writes `<name>_clean.<ext>`, and reports provenance markers found before/after.

### document-metadata-stripper

Strips authoring/provenance metadata (creator, company, application, custom properties, "Made with Claude"/Anthropic tags) from Office documents (`.docx`/`.pptx`/`.xlsx` and their macro/template variants) and PDFs, without touching the document body. Office formats run on the Python standard library; PDF support needs `pikepdf` or `pypdf`. Supports a `--check` scan-only mode.

### media-metadata-stripper

Strips container and stream metadata from audio/video (`.mp3`/`.mp4`/`.mov`/`.wav` and more) by remuxing with ffmpeg - streams are copied, so there's no re-encode or quality loss, only tags dropped. Needs ffmpeg on PATH. Supports a `--check` scan-only mode.

### strip-all

Dispatcher: point it at a folder or a mixed set of files and it auto-detects each file's type and runs the matching stripper (image, document, or media). The write-side companion to `provenance-scan`. Reuses the other skills as subprocesses, so there's a single source of truth per format.

### provenance-scan

Read-only auditor. Walks files and folders and reports which images, documents, and PDFs carry Claude/C2PA provenance markers, without modifying anything. Exit code `1` if any file is flagged, so it works as a pre-publish or CI gate; `--json` gives machine-readable output, and `hooks/pre-commit` blocks committing flagged files. Standard library only. This is the detect side to the strippers' remove side.

### text-watermark

Guidance (no script) for the invisible SynthID-style watermark Claude weaves into generated **text** - which no metadata stripper can remove. Explains why the file tools don't touch it and gives a human-rewrite checklist for degrading it.

### git-human-commits

Keeps commits and PRs attributed only to the GitHub account holder: no `Co-Authored-By: Claude` trailers, no "🤖 Generated with Claude Code" footer, no Claude-Session link, and human-style commit/PR text. Includes flag-and-verify commands for auditing history.

## Install

Windows (PowerShell):

```powershell
git clone https://github.com/JrKrishh/claude-skills.git "$env:TEMP\claude-skills"
powershell -ExecutionPolicy Bypass -File "$env:TEMP\claude-skills\install.ps1"
```

macOS/Linux:

```bash
git clone https://github.com/JrKrishh/claude-skills.git /tmp/claude-skills
bash /tmp/claude-skills/install.sh
```

The installer copies every skill directory into `~/.claude/skills/`. Restart Claude Code to load them. The stripper scripts need Python 3; install their dependencies with `pip install -r requirements.txt` (Pillow for images, pikepdf for PDFs).

## Remove Claude git/PR attribution (one-time)

Add to `~/.claude/settings.json`:

```json
{
  "attribution": { "commit": "", "pr": "", "sessionUrl": false }
}
```

This removes the `Co-Authored-By: Claude` commit trailer, the "Generated with Claude Code" PR footer, and the Claude-Session link.

## Notes

- C2PA metadata stripping is permanent - the credential cannot be recovered once stripped
- Attribution removal is cosmetic: Claude text still carries Anthropic's invisible SynthID text watermark, which only a human rewrite degrades
- Skills are personal-use tools for your own generated content
