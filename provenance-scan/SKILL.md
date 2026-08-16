---
name: provenance-scan
description: Audit a file or folder for Claude/C2PA provenance markers without modifying anything. Use when the user wants to check which images, documents, or PDFs in a project carry AI provenance metadata before publishing or sharing, or wants a read-only report of what would need stripping.
license: MIT
---

# Provenance Scan

Read-only auditor. Walks the files and folders you point it at, scans each supported file for Claude/C2PA provenance markers, and prints a report. It never writes or modifies anything - use the stripper skills to actually clean flagged files.

Companion to `image-watermark-stripper` and `document-metadata-stripper`: this is the detect side, they are the remove side.

## When to use

- "which files in this folder have Claude/AI provenance?"
- "check my project for content credentials before I publish"
- "audit this directory for C2PA metadata"

## How to run

Requires Python 3 (standard library only - no dependencies).

```powershell
python "$env:USERPROFILE\.claude\skills\provenance-scan\scripts\provenance_scan.py" "path\to\folder"
```

macOS/Linux: `python ~/.claude/skills/provenance-scan/scripts/provenance_scan.py <path>`.

Pass any mix of files and directories; directories are walked recursively. Add `--json` for machine-readable output (a `{scanned, flagged, files:[{file, markers, flagged}]}` object) suitable for CI artifacts or gating.

### As a git pre-commit hook

`hooks/pre-commit` scans staged files and blocks the commit if any carry provenance markers (bypass with `git commit --no-verify`). Install it with:

```bash
cp provenance-scan/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

## What it does

1. For each supported file, scans for provenance tokens (C2PA, JUMBF, Claude, Anthropic, "Made with Claude")
2. Images (`.png/.jpg/.webp/.gif/.bmp/.tiff/.svg`) and PDFs are byte-scanned; Office files are scanned in their metadata parts only (so body text mentioning Claude isn't a false hit)
3. Prints one line per file (`FLAGGED` or `clean`) and a summary count
4. Exit code is `1` if any file is flagged, `0` if all clean - usable in a pre-publish check or CI gate

## Limitations

- Detection only; it does not remove anything
- Token heuristic, not a full metadata dump or a signed-C2PA validator - a flagged file definitely has markers, but a clean result means "no known tokens found," not a cryptographic guarantee
- Does not detect the SynthID-style text watermark woven into document/text prose (no metadata scan can - see the text-watermark skill)
