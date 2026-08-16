---
name: git-human-commits
description: Ensure commits and PRs are authored only by the GitHub account holder (JrKrishh), with no Claude attribution trailers or "Generated with Claude Code" footers, and human-style commit/PR text. Use for any commit, PR creation, or when asked to check/clean git history for AI attribution.
license: MIT
---

# Git Human Commits

Commits and PRs must be authored by the GitHub account holder only. No Claude attribution, no AI footers, no AI-sounding descriptions.

## Before committing

1. Confirm authorship: `git config user.name` must be `JrKrishh`, `git config user.email` must be `manir1179@gmail.com`. If missing, set both before committing.
2. Attribution is already disabled in `~/.claude/settings.json` (`attribution.commit/pr` = empty, `sessionUrl` = false). If a commit still carries trailers, something overrode it - check `.claude/settings.json` and `.claude/settings.local.json` in the repo.
3. Never add `Co-Authored-By`, `Generated with`, `Claude-Session`, or similar trailers manually.

## Commit message style

Match the repo's existing style (Tether uses short imperative subjects). Write the subject as if a developer wrote it:

- Short imperative subject: `Fix X`, `Add Y`, no emojis, no period at end
- Body only when needed: 1-3 plain sentences on what changed and why
- No "This commit introduces/implements/enhances", no "leverage", no bullet-heavy bodies
- Reference the concrete thing: file, endpoint, flag, bug symptom

## PR description style

- 1-2 short paragraphs or 3-4 terse bullets, first person where natural
- No "## What changed / Why / How" boilerplate, no emojis, no "This PR..." opener
- Name the actual behavior change and the risk, like a developer explaining to a teammate
- Strip any "🤖 Generated with [Claude Code]" footer or Claude-Session link before opening the PR
- The heavy human edit doubles as watermark hygiene: Claude's SynthID text mark weakens with rewriting and dies on a full human rewrite

## Flag & verify

After committing, verify and report:

```powershell
git log -1 --format="%an <%ae>%n%B"
```

Check the author is the account holder and no `Co-Authored-By`/`Generated with` lines exist.

Audit history for Claude attribution:

```powershell
git log --all --format="%h %an <%ae> %s" | Select-String "anthropic|Claude"
git log --all --grep="Co-Authored-By"
```

Before opening a PR, check the body with `gh pr view <n> --json body -q .body` after `gh pr create` and remove any AI footer with `gh pr edit <n> --body-file <file>`.
