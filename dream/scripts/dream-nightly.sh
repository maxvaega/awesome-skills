#!/usr/bin/env bash
# Nightly "light sleep": dream over sessions queued by the SessionEnd hook.
# Groups ~/.claude/dream/queue.tsv by project cwd, runs a headless
# `claude -p "/dream queued"` in each (max MAX_PROJECTS per night), and moves
# processed lines to digested.log. Safe to run any time; exits immediately
# when the queue is empty.
set -u

DREAM_DIR="${HOME}/.claude/dream"
QUEUE="${DREAM_DIR}/queue.tsv"
DIGESTED="${DREAM_DIR}/digested.log"
MAX_PROJECTS=3      # token bound: at most this many headless sessions per run
MAX_AGE_DAYS=14     # queue entries older than this are dropped, not dreamed

[ -s "$QUEUE" ] || exit 0
command -v claude >/dev/null 2>&1 || { echo "claude CLI not found"; exit 1; }

# --max-turns exists only on some CLI versions; use it when available.
TURNS_FLAG=()
claude --help 2>&1 | grep -q -- '--max-turns' && TURNS_FLAG=(--max-turns 30)

mkdir -p "$DREAM_DIR"

# Drop stale queue entries (older than MAX_AGE_DAYS) to digested.log with a marker.
cutoff=$(date -d "-${MAX_AGE_DAYS} days" -Iseconds 2>/dev/null || date -v-"${MAX_AGE_DAYS}"d -Iseconds)
tmp=$(mktemp)
while IFS=$'\t' read -r ts cwd transcript; do
    [ -n "${ts:-}" ] || continue
    if [[ "$ts" < "$cutoff" ]]; then
        printf '%s\t%s\t%s\tskipped-too-old\n' "$ts" "$cwd" "$transcript" >> "$DIGESTED"
    else
        printf '%s\t%s\t%s\n' "$ts" "$cwd" "$transcript" >> "$tmp"
    fi
done < "$QUEUE"
mv "$tmp" "$QUEUE"
[ -s "$QUEUE" ] || exit 0

# Distinct cwds, most recently active first, capped at MAX_PROJECTS.
mapfile -t cwds < <(sort -t$'\t' -k1,1r "$QUEUE" | cut -f2 | awk '!seen[$0]++' | head -n "$MAX_PROJECTS")

for cwd in "${cwds[@]}"; do
    if [ ! -d "$cwd" ]; then
        echo "[$(date -Iseconds)] skip missing dir: $cwd"
        awk -F'\t' -v c="$cwd" '$2==c {print $0 "\tskipped-dir-gone"}' "$QUEUE" >> "$DIGESTED"
        awk -F'\t' -v c="$cwd" '$2!=c' "$QUEUE" > "${QUEUE}.tmp" && mv "${QUEUE}.tmp" "$QUEUE"
        continue
    fi
    echo "[$(date -Iseconds)] dreaming: $cwd"
    if (cd "$cwd" && DREAM_HEADLESS=1 claude -p "/dream queued" "${TURNS_FLAG[@]}"); then
        # Success: move this cwd's lines from queue to digested.
        awk -F'\t' -v c="$cwd" '$2==c' "$QUEUE" >> "$DIGESTED"
        awk -F'\t' -v c="$cwd" '$2!=c' "$QUEUE" > "${QUEUE}.tmp" && mv "${QUEUE}.tmp" "$QUEUE"
        echo "[$(date -Iseconds)] done: $cwd"
    else
        echo "[$(date -Iseconds)] FAILED (will retry tomorrow): $cwd"
    fi
done
exit 0
