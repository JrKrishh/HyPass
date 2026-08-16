---
name: media-metadata-stripper
description: Strip metadata from audio and video files (.mp3/.mp4/.mov/.wav/.m4a/.flac/.avi/.mkv/.webm) using ffmpeg, with no re-encode. Use when the user asks to remove tags, author, encoder, or Claude/Anthropic/C2PA provenance from a media file, or to check what tags a media file carries.
license: MIT
---

# Media Metadata Stripper

Removes container and stream metadata from audio/video by remuxing with ffmpeg. Streams are copied (`-c copy`), so there is no quality loss - only the tags are dropped.

Covers the audio/video formats the image and document strippers don't reach. As C2PA provenance extends to audio and video, this is where those tags would live.

## When to use

- "remove metadata/tags from this video or audio file"
- "strip author/encoder/Claude tags from this mp4/mp3"
- "check what tags this media file has"

## How to run

Requires ffmpeg and ffprobe on PATH (`https://ffmpeg.org`, or `brew install ffmpeg` / `apt install ffmpeg` / `choco install ffmpeg`). Without them, files are reported and skipped.

Strip (writes `<name>_clean.<ext>` next to the original):

```powershell
python "$env:USERPROFILE\.claude\skills\media-metadata-stripper\scripts\strip_media_metadata.py" "path\to\clip.mp4"
```

Check only (reads tags with ffprobe, writes nothing):

```powershell
python "$env:USERPROFILE\.claude\skills\media-metadata-stripper\scripts\strip_media_metadata.py" --check "path\to\clip.mp4"
```

macOS/Linux: `python ~/.claude/skills/media-metadata-stripper/scripts/strip_media_metadata.py <file>`.

## What it does

1. Reads container/stream tags with `ffprobe` and scans them for provenance markers (C2PA, Claude, Anthropic)
2. Remuxes with `ffmpeg -map_metadata -1 -map_chapters -1 -c copy`, dropping global metadata and chapters without re-encoding
3. Re-scans the output to confirm tags are gone

## Limitations

- Needs ffmpeg/ffprobe installed; without them it skips (does not silently pass)
- Removes tag/metadata only - it does not touch the audio or video content, so any signal embedded in the media itself is unaffected
- Handled: `.mp3/.mp4/.m4a/.mov/.wav/.flac/.avi/.mkv/.webm`. Other containers are skipped
