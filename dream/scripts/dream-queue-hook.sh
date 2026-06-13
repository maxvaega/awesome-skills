#!/usr/bin/env bash
# Claude Code SessionEnd hook: queue finished sessions for nightly dreaming.
# Reads the hook JSON payload from stdin, appends "timestamp<TAB>cwd<TAB>transcript_path"
# to ~/.claude/dream/queue.tsv. Always exits 0 — a hook must never block session end.
set -u

DREAM_DIR="${HOME}/.claude/dream"
QUEUE="${DREAM_DIR}/queue.tsv"
DIGESTED="${DREAM_DIR}/digested.log"
MIN_BYTES=10240   # skip trivial sessions (<10 KB transcript)

# Recursion guard: headless dream runs spawned by cron must not re-queue themselves.
[ -n "${DREAM_HEADLESS:-}" ] && exit 0

command -v jq >/dev/null 2>&1 || exit 0

payload=$(cat 2>/dev/null) || exit 0
[ -n "$payload" ] || exit 0

cwd=$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)
transcript=$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null)

# Keep one sample payload around so the JSON shape can be inspected after install.
mkdir -p "$DREAM_DIR"
[ -f "${DREAM_DIR}/hook-debug.json" ] || printf '%s\n' "$payload" > "${DREAM_DIR}/hook-debug.json"

[ -n "$cwd" ] && [ -n "$transcript" ] || exit 0
[ -f "$transcript" ] || exit 0

size=$(wc -c < "$transcript" 2>/dev/null || echo 0)
[ "$size" -ge "$MIN_BYTES" ] || exit 0

# Dedup: skip if this transcript is already queued or already digested.
if [ -f "$QUEUE" ] && grep -qF "$transcript" "$QUEUE" 2>/dev/null; then exit 0; fi
if [ -f "$DIGESTED" ] && grep -qF "$transcript" "$DIGESTED" 2>/dev/null; then exit 0; fi

printf '%s\t%s\t%s\n' "$(date -Iseconds)" "$cwd" "$transcript" >> "$QUEUE"
exit 0
