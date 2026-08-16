#!/usr/bin/env bash
# Install the skills into ~/.claude/skills/ (macOS/Linux counterpart to install.ps1).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$HOME/.claude/skills"
mkdir -p "$dest"

for dir in "$root"/skills/*/; do
    name="$(basename "$dir")"
    # Only install skill directories (those with a SKILL.md).
    [ -f "$dir/SKILL.md" ] || continue
    rm -rf "${dest:?}/$name"
    cp -R "$dir" "$dest/$name"
    echo "installed: $dest/$name"
done

echo "Done. Restart Claude Code to load the skills."
