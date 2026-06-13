# 🧠 dream — a self-improving memory loop for Claude Code

`/dream` turns session learnings into durable behavior. It captures your preferences, corrections, and standing rules as project-level memories; a periodic consolidation pass ("REM sleep") keeps the memory store lean and true; and when sessions reveal gaps in your skills or CLAUDE.md, it writes improvement **proposals** you approve before anything changes.

Inspired by the background-reflection + curator architecture of [NousResearch's Hermes Agent](https://github.com/NousResearch/hermes-agent), rebuilt on plain Claude Code primitives: markdown files, hooks, and cron. No database, no daemon.

## The loop

```
 session ends ──► SessionEnd hook queues it          (optional, zero tokens)
                       │
 nightly 04:00 ──► claude -p "/dream queued"         "light sleep": capture
                       │                              memories + proposals
 weekly Sun 04:30 ──► claude -p "/dream rem"         "REM sleep": merge, verify,
                       │                              decay, archive, promote
 you, anytime ──► /dream proposals                    review & apply skill/
                                                      CLAUDE.md improvements
```

Every automated piece is **opt-in** — out of the box, `/dream` is a manual command.

## Modes

| Command | What it does |
|---|---|
| `/dream` | Capture from the current conversation |
| `/dream history` | Capture from the project's recent session transcripts |
| `/dream queued` | Capture from sessions queued by the SessionEnd hook (used by the nightly cron) |
| `/dream rem` | Consolidation pass: merge overlapping memories, verify they still match reality, stale/archive by age, promote cross-project preferences to the global profile, cap the index. `--dry-run` reports without touching anything |
| `/dream proposals` | Review pending self-improvement proposals; approve/reject each |
| `/dream setup` | Guided, step-by-step install of the optional automation (hook + cron) |

## What gets stored, and where

- **Per-project memories** — `~/.claude/projects/<slug>/memory/`, one markdown file per fact with lifecycle metadata (`created`, `lastConfirmed`, `status: active|stale|archived`, `pinned`), indexed by a `MEMORY.md` that Claude Code loads each session (capped at 20 lines — index bloat costs context tokens forever).
- **Global user profile** — `~/.claude/CLAUDE.md`, loaded in *every* session: stable cross-project preferences (language, approval rules, formatting), hard-capped at ~1,500 characters.
- **Dream state** — `~/.claude/dream/`: `queue.tsv` (sessions awaiting digestion), `digested.log`, `reports/` (REM run reports), `proposals/` (pending skill/CLAUDE.md edits).

## Safety properties

- **Never deletes** — archiving (move to `memory/.archive/`) is the maximum destructive action; everything is recoverable with `mv`.
- **Pinned memories** (`pinned: true`) bypass all automatic transitions.
- **Self-editing is proposal-only**: dream never edits a skill or CLAUDE.md directly. It writes a before/after proposal; you apply it via the interactive `/dream proposals`. Proposals never target hooks, settings.json, or anything credential-bearing. Rejected proposals are remembered and never re-proposed.
- **Anti-capture rules** (borrowed from Hermes): no environment-dependent failures, no "tool X is broken" claims (they harden into refusals long after the problem is fixed — the *fix* gets captured instead), no transient errors that resolved, no credentials, ever.
- **Bounded cost**: nightly run handles ≤3 projects, skips trivial transcripts, reads user-messages-only via `jq`, and exits at zero cost when nothing is queued.

## Install

```bash
# skill only (manual /dream):
cp -r dream ~/.claude/skills/

# then, optionally, inside any Claude Code session:
/dream setup     # walks you through hook + cron, confirming each step
```

`scripts/` contains the three automation pieces `setup` installs:

- `dream-queue-hook.sh` — SessionEnd hook; appends finished, non-trivial sessions to the queue. Exits 0 always.
- `dream-nightly.sh` — cron, e.g. `0 4 * * *`; dreams over queued sessions.
- `dream-rem.sh` — cron, e.g. `30 4 * * 0`; weekly consolidation across all projects with memories.

To disable: remove the two crontab lines and the `SessionEnd` entry from `~/.claude/settings.json`.

## Known caveats

- The exact SessionEnd hook JSON payload may vary across Claude Code versions; the hook saves the first payload it sees to `~/.claude/dream/hook-debug.json` so you can verify the field names (`cwd`, `transcript_path`).
- Whether SessionEnd fires for headless `claude -p` runs doesn't matter: the `DREAM_HEADLESS` env guard prevents cron-spawned sessions from re-queueing themselves either way.
- Check `claude -p --help` for `--max-turns` support; older CLI versions may need the flag removed from the scripts.
