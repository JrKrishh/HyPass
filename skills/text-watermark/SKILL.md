---
name: text-watermark
description: Explain and handle the invisible text watermark Claude weaves into generated prose and code, which no metadata stripper can remove. Use when the user asks to remove the text/SynthID watermark from Claude's writing, why the image or document strippers don't touch text, or how to make AI-written text no longer detectable as Claude output.
license: MIT
---

# Text Watermark

Since Aug 2, 2026, Anthropic embeds a SynthID-style invisible watermark into the **text** Claude generates - a statistical bias in word choice, woven into the words themselves. It is not metadata. This is the honest limit of the stripper skills.

## How it's embedded

It is not a payload hidden in the file - there is nothing to locate and delete. It is a statistical bias in *which words the model chose*, added during generation (this is SynthID-Text, published by Google DeepMind in Nature, 2024; the successor to the earlier green-list/red-list schemes):

1. Text is generated one token at a time; at each step the model has many near-equivalent candidate words.
2. A secret keyed pseudo-random function - seeded by the provider's key plus a window of the preceding tokens - assigns each candidate a hidden score.
3. "Tournament sampling" favors the higher-scoring candidate among tokens the model already found probable, so quality and meaning do not visibly change.
4. Across a passage, the chosen words are subtly, consistently skewed. A detector with the secret key recomputes those scores and runs a statistical test; longer text = stronger signal, short snippets barely register.

Because the signal lives in the token choices themselves (and each token's score depends on the tokens before it), there is no field, header, or marker to strip.

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

## What the research shows

Published academic work (not this repo) has measured these watermarks' robustness, and the finding is consistent: meaning-preserving edits degrade detection. One robustness study reports SynthID-Text's true-positive rate falling from ~0.998 on clean text to ~0.498 under moderate paraphrasing; survey work notes rewriting/translation attacks reaching high evasion rates across watermarking schemes generally. The takeaway for this skill is factual, not a recipe: a watermark is a probabilistic signal over wording, and rewriting the wording weakens the signal. It is not an unbreakable seal, and it is not proof of authorship - only that the text *may* have been model-generated.

## Human-rewrite checklist

When the goal is text that no longer reads as Claude output, rewrite rather than reformat:

1. Read Claude's draft, then write the passage again in your own words without copying phrasing.
2. Change sentence structure and order, not just individual words.
3. Cut AI-tell phrasing ("It's important to note", "leverage", "delve", "in today's fast-paced").
4. For code: rename variables, reorder logic, rewrite comments in your own voice.
5. Shorter still helps - the watermark needs a length of text to be detectable, so terse edited output carries a weaker signal.

## Honesty note

This skill does not defeat provenance for deception. Detection only shows Claude *may have processed* text, not authorship, and heavy editing legitimately reflects real human authorship of the final wording. Use it to own your edited work, not to misrepresent unedited AI output as your own.
