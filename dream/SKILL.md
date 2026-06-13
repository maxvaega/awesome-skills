---
name: dream
description: Self-improving memory loop — capture the user's preferences, corrections, and standing rules as project memories; periodically consolidate them (REM pass) and propose improvements to skills and CLAUDE.md. Modes - default, history, queued, rem, proposals, setup.
disable-model-invocation: true
---

# /dream — distill sessions into memory, consolidate, self-improve

The user runs `/dream [mode]` to make learnings from sessions persist: preferences, corrections, and standing directions become project-level memories; recurring gaps become improvement proposals for skills and CLAUDE.md; a periodic consolidation pass ("REM sleep") keeps the memory store lean and true. Follow this procedure exactly. Reply in the language the user has been using.

## 0. Mode dispatch

Parse `$ARGUMENTS`:

| `$ARGUMENTS` | Mode |
|---|---|
| *(empty)* | **Capture** from the current conversation (§1–§5, then §6) |
| `history` | **Capture** from recent transcripts (§1–§5, then §6) |
| `queued` | **Capture** from transcripts queued by the SessionEnd hook (§1–§5, then §6) |
| `rem` or `rem --dry-run` | **REM consolidation** pass (§7) |
| `proposals` | **Review pending proposals** interactively (§8) |
| `setup` | **Install opt-in automation** on this machine (§9) |

Paths used throughout:

- Project slug: cwd with `/` replaced by `-` (e.g. `/home/me/proj` → `-home-me-proj`).
- Project memory: `~/.claude/projects/<project-slug>/memory/`
- Dream state: `~/.claude/dream/` containing `queue.tsv`, `digested.log`, `reports/`, `proposals/` (create dirs as needed).
- Global user profile: `~/.claude/CLAUDE.md` (loaded by Claude Code in every session, all projects).

## 1. Gather source material (capture modes)

- **Default (in-conversation):** if the current conversation has substantive exchanges, analyze it directly. No file reads needed. If it's fresh/empty, fall back to `history`.
- **`history`:** mine recent transcripts from `~/.claude/projects/<project-slug>/`. Pick the 3-5 most recent `*.jsonl` by mtime (`ls -t`), skipping tiny files.
- **`queued`:** read `~/.claude/dream/queue.tsv` (TSV: `timestamp<TAB>cwd<TAB>transcript_path`), take only lines whose `cwd` matches the current project. Process those transcripts, then move the processed lines to `~/.claude/dream/digested.log`. If none match, say so and stop.

Extract ONLY user messages, token-efficiently — transcripts can be megabytes, never full-read. Per file:

```bash
jq -r 'select(.type=="user") | .message.content | if type=="array" then .[] | select(.type=="text") | .text else . end' file.jsonl 2>/dev/null | head -c 8000
```

Transcript line schemas vary; keep the `2>/dev/null` and tolerate files that yield nothing.

## 2. Distill

Scan for, in order of value:

1. **Explicit corrections and feedback** — "no, do it this way", "stop doing X", "this is too verbose", repeated re-asks after an unsatisfying answer. Frustration signals are FIRST-CLASS, not noise.
2. **Standing constraints and approval rules** — e.g. "never publish/post/push without my approval".
3. **Stable preferences** — reply language, verbosity, formatting, preferred tools/commands, workflow habits.
4. **Project facts not derivable from the repo** — goals, deadlines, external accounts.
5. **Skill/runbook gaps** — a fix or technique applied this session that an existing skill or the project's CLAUDE.md should already know (→ becomes a proposal, §6, never a direct edit).

**Do NOT capture** (these harden into self-imposed constraints that bite later when the environment changes):

- Environment-dependent failures: missing binaries, "command not found", unconfigured credentials, uninstalled packages. The user can fix these — they are not durable rules.
- Negative claims about tools ("X tool is broken", "Y doesn't work"). These harden into refusals cited for months after the actual problem was fixed. If a tool failed because of setup state, capture the FIX (install command, config step) — never "this tool doesn't work" as a standalone fact.
- Transient errors that resolved before the session ended. If retrying worked, the lesson is the retry pattern, not the failure.
- One-off task narratives, anything already in the repo's CLAUDE.md or git history, and secrets/credentials — NEVER store credentials in memory.

"Nothing to save" is a real outcome but should NOT be the default. If the session ran smoothly with no corrections and no new durable facts, say so and stop. Otherwise, act.

## 3. Route and persist

**Routing rule:** stable cross-project facts about the user (`type: user` — language, tone, approval rules, formatting preferences) go to the **global profile** `~/.claude/CLAUDE.md`, NOT per-project memory. Everything else (`feedback` / `project` / `reference`) goes to per-project memory.

**Global profile** (`~/.claude/CLAUDE.md`): create if missing with header `# User profile (maintained by /dream)`, then short bullet lines. Hard cap **~1,500 characters** — when over, merge/trim the least valuable lines instead of appending.

**Project memory:** one file per fact in `~/.claude/projects/<project-slug>/memory/`, named `<type>_<slug>.md`:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary used for recall relevance>
metadata:
  node_type: memory
  type: user | feedback | project | reference
  originSessionId: <session id if known>
  created: <YYYY-MM-DD>
  lastConfirmed: <YYYY-MM-DD>
  status: active        # active | stale | archived
  pinned: false         # pinned memories bypass all REM transitions
---

<the fact. For feedback/project memories add:>
**Why:** <what prompted this — quote or paraphrase the user's words>
**How to apply:** <concrete behavioral instruction for future sessions>
```

Link related memories with `[[their-name]]`. Then maintain the index `MEMORY.md` in the same dir — one line per memory: `- [Title](file.md) — hook`. Create it if missing; append or update the line for each memory written. NEVER put memory bodies in MEMORY.md — index lines only.

## 4. Dedup discipline

BEFORE writing anything, read the existing memory dir (`MEMORY.md` first, then candidate files):

- If a file already covers the fact → UPDATE that file, don't create a duplicate.
- If a session **re-confirms** an existing memory → bump its `lastConfirmed` date (this is what keeps it from going stale in REM passes).
- If the conversation shows a previous memory is now wrong → correct it (or set `status: stale` with a dated note) and fix its MEMORY.md line.
- Convert relative dates ("yesterday", "next week") to absolute dates before storing.

## 5. Report (capture modes)

End with a short bullet list — memories **created / updated / confirmed**, proposals written (§6) — each with its one-line description, in the user's language. If proposals are pending, add: "N proposals pending — run `/dream proposals` to review."

## 6. Self-improvement pass (runs at the end of every capture mode)

If the session revealed a gap, error, or missing step in one of the user's skills (`~/.claude/skills/*/SKILL.md`) or in the project's CLAUDE.md — e.g. a workaround applied that the runbook doesn't document, a skill that was loaded and turned out wrong or missing a step — write a **proposal file**. NEVER edit the target directly in this pass.

Proposal file: `~/.claude/dream/proposals/<YYYY-MM-DD>-<target-slug>.md`:

```markdown
---
target: </absolute/path/to/SKILL.md or CLAUDE.md>
type: skill | claude-md
status: pending        # pending | applied | rejected
created: <YYYY-MM-DD>
---

## Evidence
<quote the triggering exchange from the session>

## Suggested edit

### Before
```<fenced block of the current text, or "(new section)">```

### After
```<fenced block of the proposed text>```
```

Rules:

- Preference order: patch an existing skill section > add a new section to an existing skill > propose a new skill (rarely — only when no existing skill covers the class of task).
- Check existing proposals (including `status: rejected`) first — never re-propose a rejected idea, never duplicate a pending one.
- NEVER propose edits to hooks, `settings.json`, permission configs, or anything credential-bearing.
- One proposal per distinct gap; keep the suggested edit minimal and surgical.

## 7. REM consolidation (`/dream rem [--dry-run]`)

> **Dry-run:** when `--dry-run` is present, your report IS the deliverable — describe every action you WOULD take, write the report file, and make ZERO other mutations.

For the current project's memory dir (skip silently if it has no memory files):

1. **Backfill** lifecycle fields on legacy memories missing them: `created` ← file mtime, `lastConfirmed` ← created, `status: active`, `pinned: false`.
2. **Merge** overlapping memories. Judge overlap on CONTENT, not age or filename. The bar: "would a maintainer write these as N separate memories, or one with N subsections?" If the latter, merge into the strongest file — union the Why sections, keep earliest `created` and latest `lastConfirmed`, fix `[[links]]`, archive the absorbed files.
3. **Verify against reality**: for memories referencing concrete paths, containers, flags, or commands, run read-only checks (`test -e`, `docker ps`, `command -v`). Broken reference → `status: stale` + a dated note explaining what no longer matches. NEVER delete — archiving is the maximum destructive action.
4. **Time transitions** (skip `pinned: true`; `type: user` entries are exempt — they belong in the global profile): `active` → `stale` when `lastConfirmed` is >60 days old; `stale` → `archived` when >120 days. A stale memory re-confirmed by recent sessions goes back to `active`.
5. **Archive** = move the file to `memory/.archive/` and remove its MEMORY.md line. Recoverable by `mv` back.
6. **Promote**: if a near-identical preference appears in ≥2 projects' memory dirs (check other `~/.claude/projects/*/memory/MEMORY.md` indexes), merge it upward into `~/.claude/CLAUDE.md` (respecting the ~1,500-char cap) and archive the per-project copies.
7. **Index cap**: keep MEMORY.md ≤ 20 lines — the index loads into context every session, bloat has a permanent token cost. If over, archive lowest-value first: oldest `lastConfirmed`, `type: reference` before `feedback`.
8. **Report** to `~/.claude/dream/reports/<YYYY-MM-DD>-rem.md`: lists of merged / stale / archived / promoted memories and pending proposals. Then run the self-improvement pass (§6) over what you observed.

## 8. Proposals review (`/dream proposals`)

Interactive only — if running non-interactively (headless/cron), refuse: "proposals review requires an interactive session."

1. List `~/.claude/dream/proposals/*.md` with `status: pending`. If none: say so, stop.
2. For each: show target, evidence, and the before/after diff. Ask the user: approve / reject / edit.
3. On **approve**: apply the edit to the target. If the skill has a canonical source in a repo (check for a repo copy that `~/.claude/skills/<name>` mirrors), edit the repo copy first, then sync the installed copy. Set `status: applied`.
4. On **reject**: set `status: rejected` and keep the file (it prevents re-proposing).
5. Summarize what was applied/rejected.

## 9. Setup — opt-in automation (`/dream setup`)

Installs the closed loop on this machine. Confirm each step with the user before doing it; all steps are optional and independent.

0. **Preflight**: verify `claude -p --help` works and note whether `--max-turns` is supported; verify `jq` is installed; locate this skill's `scripts/` dir (next to this SKILL.md — check both the installed `~/.claude/skills/dream/scripts/` and the repo source).
1. **SessionEnd hook** (queues finished sessions for nightly dreaming): copy `scripts/dream-queue-hook.sh` to `~/.claude/hooks/dream-queue.sh` (`chmod +x`), then add to `~/.claude/settings.json` hooks (merge, don't overwrite existing hooks):
   ```json
   "SessionEnd": [{"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/dream-queue.sh"}]}]
   ```
   Verify the hook payload shape once: the hook writes a debug line on first run; alternatively `echo '{"cwd":"/tmp","transcript_path":"/tmp/t.jsonl","session_id":"test"}' | bash ~/.claude/hooks/dream-queue.sh` then check `~/.claude/dream/queue.tsv`.
2. **Nightly capture cron** ("light sleep"): install `scripts/dream-nightly.sh` to `~/.local/bin/` (`chmod +x`) and offer the crontab line:
   ```
   0 4 * * * $HOME/.local/bin/dream-nightly.sh >> $HOME/.local/state/dream-nightly.log 2>&1
   ```
   Cost note for the user: ≤3 headless sessions per night, zero when no sessions are queued.
3. **Weekly REM cron**: install `scripts/dream-rem.sh` to `~/.local/bin/` and offer:
   ```
   30 4 * * 0 $HOME/.local/bin/dream-rem.sh >> $HOME/.local/state/dream-rem.log 2>&1
   ```
4. Report what was installed and how to disable (remove crontab lines, remove the SessionEnd hook entry).
