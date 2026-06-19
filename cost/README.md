# `cost` — Cowork → Claude API cost estimator

A Claude **Cowork / Claude Code** skill that estimates what your conversations
would cost if run on the **pay-per-token Claude API** instead of the
subscription. It reports token counts and cache-aware cost in **USD and EUR**,
for the current conversation or for your whole history.

## What it does

Cowork and Claude Code already run on the Claude API and write one JSONL
transcript per conversation under `~/.claude/projects/`. Every assistant turn
records the **actual** API call it made, including the prompt-cache breakdown.
This skill reads those transcripts, sums the real token usage, and prices it at
Anthropic list rates — so the result is a faithful replay cost, not a guess.

It answers three things:

1. **Token count** — for the current conversation and/or per conversation across history.
2. **Exact tokens** needed to replay the same multi-turn, tool-using conversation on the API.
3. **Cost** of those tokens in USD and EUR, accounting for prompt-cache hits.

> This is the **API pay-per-token** cost. The Cowork/Claude **subscription bills
> differently**, so treat the figure as a comparison, not your actual invoice.

## How accuracy works

Each API call can appear several times in a transcript (streaming partials +
the final row). The skill dedupes by `requestId` and keeps the row with the
largest token total — the finalized one — so nothing is double-counted or
undercounted.

A common claim online is that `usage.input_tokens` is unreliable. That's only
because, with caching, almost all input lands in the *cache-read* / *cache-write*
fields and `input_tokens` is just the small uncached remainder. The **total is
accurate when you sum all four token categories**, which is exactly what this
skill does.

## Usage

### Inside Cowork / Claude Code (normal use)

Just ask in natural language, or type `/cost`:

- "How much would this conversation cost on the API?"
- "What's the API cost of all my Cowork conversations?"
- "Token usage / cost per conversation"

Claude runs the script and renders a short English report.

### Running the script directly

```bash
# Current conversation (default)
python cost.py --mode current

# Every conversation, ranked, with a TOTAL row
python cost.py --mode history

# Machine-readable output (used by the skill to render the report)
python cost.py --mode current --json
```

**Options**

| Flag | Default | Meaning |
|---|---|---|
| `--mode current\|history` | `current` | One conversation, or all of them with per-conversation + total cost. |
| `--rate-eur <n>` | `0.92` | EUR per 1 USD (approximate, editable). |
| `--include-subagents` | off | Also count subagent API calls (more complete cost). |
| `--json` | off | Emit structured JSON instead of the human table. |

### Example (human output)

```
Claude Cowork → API cost estimate (current conversation)
Conversation : my-conversation-title
Transcript   : 3b042aa5-....jsonl
API calls    : 22

Tokens to replay this conversation on the API:
  Uncached input : 6,424
  Cache read     : 3,724,966
  Cache write    : 244,372  (5-min 0 / 1-hour 244,372)
  Output         : 35,062
  TOTAL          : 4,010,824

Estimated API cost (list price, cache-aware):
  USD : $5.2149
  EUR : €4.7977   (at 0.92 EUR per USD)
```

## Pricing

Per million tokens — base input / output (source: Anthropic, cached 2026-06-04):

| Model | input $/M | output $/M |
|---|---|---|
| `claude-opus-4-8` | 5.00 | 25.00 |
| `claude-opus-4-7` | 5.00 | 25.00 |
| `claude-opus-4-6` | 5.00 | 25.00 |
| `claude-opus-4-5` | 5.00 | 25.00 |
| `claude-sonnet-4-6` | 3.00 | 15.00 |
| `claude-haiku-4-5` | 1.00 | 5.00 |
| `claude-fable-5` | 10.00 | 50.00 |

Cache multipliers on the base input price: **cache read 0.1×**, **5-minute write
1.25×**, **1-hour write 2×**. Per call:

```
cost = input·base
     + cache_read·0.1·base
     + write_5m·1.25·base
     + write_1h·2·base
     + output·out_rate
```

To add or update a model, edit the `PRICES` dict at the top of `cost.py`.
Unknown model IDs are counted as tokens but priced at $0 and flagged in the
output, so totals stay honest.

## Behaviour outside Cowork / Claude Code

If the script finds no transcripts (e.g. it's run outside a Cowork / Claude Code
session), it exits cleanly with a friendly message instead of an error,
explaining that transcripts only exist inside such a session.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Skill manifest — trigger phrases and instructions for Claude. |
| `cost.py` | The worker — parses transcripts, computes tokens and cost. |
| `README.md` | This document. |

## Requirements

- Python 3 (uses only the standard library).
- Installed at `~/.claude/skills/cost/`. Restart Cowork / Claude Code after
  installing so the skill is picked up.

## Notes & limitations

- Server-side tool usage (`web_search` / `web_fetch`) is counted and reported but
  not separately priced — those carry their own per-request fees.
- The EUR rate is a static, editable approximation (`--rate-eur`); it is not
  fetched live.
- Transcripts are read-only; the skill never modifies them.
