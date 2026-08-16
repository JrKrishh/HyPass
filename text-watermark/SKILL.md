---
name: text-watermark
description: Explain and handle the invisible text watermark Claude weaves into generated prose and code, which no metadata stripper can remove. Use when the user asks to remove the text/SynthID watermark from Claude's writing, why the image or document strippers don't touch text, or how to make AI-written text no longer detectable as Claude output.
license: MIT
---

# Text Watermark

Since Aug 2, 2026, Anthropic embeds a SynthID-style invisible watermark into the **text** Claude generates - a statistical bias in word choice, woven into the words themselves. It is not metadata. This is the honest limit of the stripper skills.

## The key fact

No file tool can remove it. `image-watermark-stripper`, `document-metadata-stripper`, and `provenance-scan` all operate on **metadata** - C2PA credentials, EXIF, author fields. The text watermark lives in the **word choices of the prose itself**, so:

- Copying, pasting, and reformatting keep it intact.
- Stripping a document's metadata does nothing to the watermark in its body text.
- It travels with the text into emails, commit messages, PR descriptions, code comments, chat - anywhere Claude's words go.

## What actually degrades it

The watermark is statistical, so it weakens as the wording diverges from what Claude produced:

- **Light edits** (fixing a word here and there): mostly intact.
- **Heavy rewriting / paraphrasing**: detection weakens.
- **Full human rewrite or translation**: the mark degrades to the point of not being reliably detectable, because the signal lives in the specific words and you have replaced them.

This is why `git-human-commits` treats a genuine human rewrite of commit and PR text as watermark hygiene, not just style.

## Human-rewrite checklist

When the goal is text that no longer reads as Claude output, rewrite rather than reformat:

1. Read Claude's draft, then write the passage again in your own words without copying phrasing.
2. Change sentence structure and order, not just individual words.
3. Cut AI-tell phrasing ("It's important to note", "leverage", "delve", "in today's fast-paced").
4. For code: rename variables, reorder logic, rewrite comments in your own voice.
5. Shorter still helps - the watermark needs a length of text to be detectable, so terse edited output carries a weaker signal.

## Honesty note

This skill does not defeat provenance for deception. Detection only shows Claude *may have processed* text, not authorship, and heavy editing legitimately reflects real human authorship of the final wording. Use it to own your edited work, not to misrepresent unedited AI output as your own.
