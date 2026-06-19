---
name: cost
description: Estimate what Claude Cowork / Claude Code conversations would cost if run on the pay-per-token Claude API instead of the subscription. Reports token counts and cache-aware API cost in USD and EUR, for the current conversation or for the whole history (cost per conversation). Trigger when the user asks things like "how much would this conversation cost on the API", "API cost of my Cowork conversations", "token usage / token count", "cost per conversation", "/cost", or wants to compare subscription vs API pricing.
---

# cost — Cowork → Claude API cost estimator

## Overview

Claude Cowork (and Claude Code) already run on the Claude API and write one JSONL
transcript per conversation under `~/.claude/projects/`. Every assistant turn records
the **actual** API call it made, including the prompt-cache breakdown. This skill reads
those transcripts, sums the real token usage, and prices it at Anthropic list rates
(cache-aware) so a business user can judge what their conversations would cost on the
API instead of the subscription.

It answers three things:
1. **Token count** (current conversation and/or per conversation across history).
2. **Exact tokens** needed to replay the same multi-turn, tool-using conversation on the API.
3. **Cost** of those tokens in **USD and EUR**, accounting for prompt-cache hits.

## When to Use This Skill

Use it when the user wants the token count or the API-equivalent cost of their Cowork /
Claude Code usage — for one conversation or all of them — or asks to compare subscription
vs API pricing.

## How to Run

The worker is `cost.py`, located in this skill's folder. Run it with the system Python.

1. **Pick the mode** from the request:
   - **current** (default) — the active conversation. Use for "this conversation", "current chat".
   - **history** — every conversation with per-conversation + total cost. Use when the user
     says "all", "history", "per conversation", "each conversation", "everything".

2. **Run the script with `--json`** so you can render the result yourself:

   ```
   python "C:\Users\massimo.olivieri\.claude\skills\cost\cost.py" --mode current --json
   ```
   ```
   python "C:\Users\massimo.olivieri\.claude\skills\cost\cost.py" --mode history --json
   ```

   Options:
   - `--rate-eur 0.92` — EUR per 1 USD (approximate, editable). Pass a current rate if the
     user gives one.
   - `--include-subagents` — also count subagent API calls (more complete cost). Use it when
     the user wants the full picture or asks about agents/subagents.

3. **Render the JSON as a short English report.** Show the token breakdown
   (uncached input / cache read / cache write / output / **total**) and the cost in **USD
   and EUR**. In history mode, present a ranked table (most expensive first) with a TOTAL row.

   **Money formatting — always use exactly two decimals.** Each cost object carries
   ready-to-render strings: use `usd_display` (e.g. `$1.23`) and `eur_display` (e.g.
   `€1,13`) verbatim. The euro figure uses a **comma** as the decimal separator. Do not
   re-derive the amounts from the numeric `usd`/`eur` fields.

## Graceful Fallback (run outside Cowork / Claude Code)

If the script returns `{"status": "unavailable", ...}`, it found no transcripts — this
happens when it's run outside Cowork or Claude Code. **Do not invent numbers.** Relay the
`message` field kindly and verbatim in tone: explain that transcripts only exist inside a
Cowork / Claude Code session, and invite the user to run it from there. Keep it friendly,
not an error.

## Reporting Notes (always include briefly)

- The figures are the **actual API calls** the conversation made, priced at **Anthropic list
  rates** including prompt-cache discounts (cache read ≈ 0.1×, 5-min write 1.25×, 1-hour write
  2× of base input) — not an estimate.
- This is the **API pay-per-token** cost; the **Cowork/Claude subscription bills differently**,
  so treat it as a comparison, not your actual invoice.
- If the output lists `unknown_models`, mention those calls were counted as tokens but priced
  at $0 because their rate isn't in the table yet (add them to `PRICES` in `cost.py`).
