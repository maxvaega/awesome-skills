#!/usr/bin/env bash
# Weekly "REM sleep": run the /dream rem consolidation pass in every project
# that has accumulated memories. Maps each ~/.claude/projects/<slug>/memory/
# dir back to its working directory and runs a headless `claude -p "/dream rem"`.
set -u

PROJECTS_DIR="${HOME}/.claude/projects"
MAX_PROJECTS=5

command -v claude >/dev/null 2>&1 || { echo "claude CLI not found"; exit 1; }

# --max-turns exists only on some CLI versions; use it when available.
TURNS_FLAG=()
claude --help 2>&1 | grep -q -- '--max-turns' && TURNS_FLAG=(--max-turns 40)

count=0
for memdir in "$PROJECTS_DIR"/*/memory; do
    [ -d "$memdir" ] || continue
    # Only dirs with actual memory files (beyond a bare MEMORY.md).
    files=$(find "$memdir" -maxdepth 1 -name '*.md' ! -name 'MEMORY.md' | head -1)
    [ -n "$files" ] || continue
    [ "$count" -lt "$MAX_PROJECTS" ] || { echo "project cap ($MAX_PROJECTS) reached, rest next week"; break; }

    # Slug -> cwd: "-home-me-Developer-proj" -> "/home/me/Developer/proj".
    # Dashes are ambiguous (dir names may contain them), so prefer the cwd
    # recorded in the project's most recent transcript when available.
    slug=$(basename "$(dirname "$memdir")")
    cwd=""
    latest=$(ls -t "$(dirname "$memdir")"/*.jsonl 2>/dev/null | head -1)
    if [ -n "$latest" ] && command -v jq >/dev/null 2>&1; then
        cwd=$(head -50 "$latest" | jq -r 'select(.cwd) | .cwd' 2>/dev/null | head -1)
    fi
    [ -n "$cwd" ] || cwd=$(printf '%s' "$slug" | tr '-' '/')
    if [ ! -d "$cwd" ]; then
        echo "[$(date -Iseconds)] skip: cannot resolve cwd for $slug (tried: $cwd)"
        continue
    fi

    echo "[$(date -Iseconds)] REM pass: $cwd"
    if (cd "$cwd" && DREAM_HEADLESS=1 claude -p "/dream rem" "${TURNS_FLAG[@]}"); then
        echo "[$(date -Iseconds)] done: $cwd"
    else
        echo "[$(date -Iseconds)] FAILED: $cwd"
    fi
    count=$((count + 1))
done
exit 0
