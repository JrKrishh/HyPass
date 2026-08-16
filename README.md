# claude-skills

Personal Claude Code skills for clean, human-owned output.

## Skills

### image-watermark-stripper

Strips AI provenance metadata (C2PA content credentials, EXIF, XMP, IPTC, PNG text chunks, SVG metadata) from image files. Claude marks `.png`/`.jpg`/`.svg` with signed C2PA credentials (Anthropic, Aug 2026 - EU AI Act). Runs `strip_metadata.py`, writes `<name>_clean.<ext>`, and reports provenance markers found before/after.

### git-human-commits

Keeps commits and PRs attributed only to the GitHub account holder: no `Co-Authored-By: Claude` trailers, no "🤖 Generated with Claude Code" footer, no Claude-Session link, and human-style commit/PR text. Includes flag-and-verify commands for auditing history.

## Install

```powershell
git clone https://github.com/JrKrishh/claude-skills.git "$env:TEMP\claude-skills"
powershell -ExecutionPolicy Bypass -File "$env:TEMP\claude-skills\install.ps1"
```

`install.ps1` copies both skills into `%USERPROFILE%\.claude\skills\`. Restart Claude Code to load them.

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
