---
name: dream
description: Review the conversation (or recent session history when run standalone) and persist the user's preferences, corrections, and standing directions as project-level memories so future sessions align to them.
disable-model-invocation: true
---

# /dream — distill this session into project memory

Max (bilingual Italian/English, solo dev/ops) runs `/dream [history]` to make you extract his preferences, corrections, and standing directions and persist them as project-level memories. Follow this procedure exactly.

## 1. Determine mode

- **In-conversation (default):** if the current conversation has substantive exchanges, analyze it directly. No file reads needed.
- **Standalone/history mode:** use when the conversation is fresh OR `$ARGUMENTS` contains `history`. Mine recent transcripts:
  - Project transcript dir: `~/.claude/projects/<project-slug>/` where `<project-slug>` is the cwd with `/` replaced by `-` (e.g. `/home/max/Developer/openclaw` → `-home-max-Developer-openclaw`).
  - Pick the 3-5 most recent `*.jsonl` by mtime (`ls -t`), skipping tiny already-summarized files.
  - Extract ONLY user messages, token-efficiently — transcripts can be megabytes, never full-read. Per file:

```bash
jq -r 'select(.type=="user") | .message.content | if type=="array" then .[] | select(.type=="text") | .text else . end' file.jsonl 2>/dev/null | head -c 8000
```

  - Transcript line schemas vary; keep the `2>/dev/null` and tolerate files that yield nothing.

## 2. Distill

Scan for, in order of value:

1. **Explicit corrections and feedback** — "no, do it this way", "non fare X", repeated re-asks after an unsatisfying answer.
2. **Standing constraints and approval rules** — e.g. "never publish/post/push without my approval".
3. **Stable preferences** — reply language, verbosity, formatting, preferred tools/commands, workflow habits.
4. **Project facts not derivable from the repo** — goals, deadlines, external accounts.

Ignore: one-off task details, anything already in the repo's CLAUDE.md or git history, and secrets/credentials — NEVER store credentials in memory.

## 3. Persist to project-level memory

Write to `~/.claude/projects/<project-slug>/memory/` (create the dir if missing). One file per fact, named `<type>_<slug>.md`. Match the existing convention exactly (see real examples in `~/.claude/projects/-home-max-Developer-hermes-agent/memory/` — read one to match style). Template:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary used for recall relevance>
metadata:
  node_type: memory
  type: user | feedback | project | reference
---

<the fact. For feedback/project memories add:>
**Why:** <what prompted this — quote or paraphrase the user's words>
**How to apply:** <concrete behavioral instruction for future sessions>
```

Then maintain the index `MEMORY.md` in the same dir: one line per memory, format:

```markdown
- [Title](file.md) — hook
```

Create MEMORY.md if missing; append or update the line for each memory written. NEVER put memory bodies in MEMORY.md — index lines only.

## 4. Dedup discipline

BEFORE writing anything, read the existing memory dir (`MEMORY.md` first, then any candidate files):

- If a file already covers the fact → UPDATE that file, don't create a duplicate.
- If the conversation shows a previous memory is now wrong → correct or delete it, and fix its MEMORY.md line.
- Convert relative dates ("yesterday", "next week") to absolute dates before storing.

## 5. Report

End with a short bullet list for Max — memories **created / updated / deleted**, each with its one-line description — in the language he has been using in the conversation (Italian or English).
