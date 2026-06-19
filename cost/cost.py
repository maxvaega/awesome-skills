#!/usr/bin/env python3
"""
cost.py — Estimate what a Claude Cowork / Claude Code conversation would cost
on the Claude API (pay-per-token), using the local JSONL transcripts.

Cowork already runs on the Claude API and writes one JSONL transcript per
session under ~/.claude/projects/<cwd-slug>/<sessionId>.jsonl. Every assistant
turn records the *actual* API call it made, including the prompt-cache
breakdown. Summing those usages and applying Anthropic list prices gives the
real replay cost — no estimation.

Modes:
  --mode current   the active conversation (most recently written transcript)
  --mode history   every conversation, with per-conversation + total cost

If no transcripts are found (e.g. run outside Cowork/Claude Code) the script
exits cleanly with a friendly message instead of an error.
"""

import argparse
import json
import sys
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 28

# --- Pricing -----------------------------------------------------------------
# USD per 1,000,000 tokens: (base input, output). Source: claude-api skill
# (cached 2026-06-04). Easy to extend — just add a model row.
PRICES = {
    "claude-opus-4-8":   (Decimal("5"),  Decimal("25")),
    "claude-opus-4-7":   (Decimal("5"),  Decimal("25")),
    "claude-opus-4-6":   (Decimal("5"),  Decimal("25")),
    "claude-opus-4-5":   (Decimal("5"),  Decimal("25")),
    "claude-sonnet-4-6": (Decimal("3"),  Decimal("15")),
    "claude-haiku-4-5":  (Decimal("1"),  Decimal("5")),
    "claude-fable-5":    (Decimal("10"), Decimal("50")),
}

# Cache multipliers applied to the base input price (shared/prompt-caching.md).
CACHE_READ_MULT = Decimal("0.1")    # cache read
WRITE_5M_MULT = Decimal("1.25")     # 5-minute cache write
WRITE_1H_MULT = Decimal("2")        # 1-hour cache write
MILLION = Decimal("1000000")

TOKEN_KEYS = ("input", "cache_read", "write_5m", "write_1h", "output")


def projects_dir() -> Path:
    return Path.home() / ".claude" / "projects"


def iter_json_lines(path: Path):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def empty_acc() -> dict:
    acc = {k: 0 for k in TOKEN_KEYS}
    acc.update(calls=0, web_search=0, web_fetch=0)
    return acc


def _usage_total(usage: dict) -> int:
    return (int(usage.get("input_tokens") or 0)
            + int(usage.get("cache_read_input_tokens") or 0)
            + int(usage.get("cache_creation_input_tokens") or 0)
            + int(usage.get("output_tokens") or 0))


def aggregate_file(path: Path, by_model: dict | None = None) -> dict:
    """Accumulate token usage per model from one transcript.

    Each API call can appear several times (streaming partials + final row). We
    dedupe by requestId and keep the row with the largest token total — the
    finalized one — so partial rows never undercount.
    """
    if by_model is None:
        by_model = {}
    best: dict = {}     # key -> [model, usage, total]
    order: list = []
    for obj in iter_json_lines(path):
        if obj.get("type") != "assistant":
            continue
        msg = obj.get("message") or {}
        usage = msg.get("usage")
        if not usage:
            continue
        key = obj.get("requestId") or obj.get("uuid") or id(obj)
        total = _usage_total(usage)
        if key not in best:
            best[key] = [msg.get("model") or "unknown", usage, total]
            order.append(key)
        elif total > best[key][2]:
            best[key] = [msg.get("model") or "unknown", usage, total]

    for key in order:
        model, usage, _ = best[key]
        acc = by_model.setdefault(model, empty_acc())
        acc["calls"] += 1
        acc["input"] += int(usage.get("input_tokens") or 0)
        acc["cache_read"] += int(usage.get("cache_read_input_tokens") or 0)
        acc["output"] += int(usage.get("output_tokens") or 0)
        cw = int(usage.get("cache_creation_input_tokens") or 0)
        cc = usage.get("cache_creation") or {}
        w1h = int(cc.get("ephemeral_1h_input_tokens") or 0)
        w5m = int(cc.get("ephemeral_5m_input_tokens") or 0)
        if w1h or w5m:
            acc["write_1h"] += w1h
            acc["write_5m"] += w5m
            leftover = cw - w1h - w5m
            if leftover > 0:  # any unsplit remainder: price as the cheaper 5-min write
                acc["write_5m"] += leftover
        else:
            acc["write_5m"] += cw  # no split available: assume default 5-min TTL
        stu = usage.get("server_tool_use") or {}
        acc["web_search"] += int(stu.get("web_search_requests") or 0)
        acc["web_fetch"] += int(stu.get("web_fetch_requests") or 0)
    return by_model


def file_meta(path: Path) -> tuple[str, str | None]:
    """Best-effort (title, started_at) for a transcript."""
    title = None
    started = None
    first_user = None
    for obj in iter_json_lines(path):
        if started is None and obj.get("timestamp"):
            started = obj["timestamp"]
        if title is None and obj.get("slug"):
            title = obj["slug"]
        if first_user is None and obj.get("type") == "user":
            content = (obj.get("message") or {}).get("content")
            txt = None
            if isinstance(content, str):
                txt = content
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        txt = block.get("text")
                        break
            if txt:
                first_user = " ".join(txt.split())
        if title and started and first_user:
            break
    if not title:
        if first_user:
            title = first_user[:57] + "..." if len(first_user) > 60 else first_user
        else:
            title = path.stem
    return title, started


def cost_for_model(model: str, acc: dict) -> Decimal | None:
    price = PRICES.get(model)
    if price is None:
        return None
    base_in, out_rate = price
    base = base_in / MILLION
    return (
        Decimal(acc["input"]) * base
        + Decimal(acc["cache_read"]) * base * CACHE_READ_MULT
        + Decimal(acc["write_5m"]) * base * WRITE_5M_MULT
        + Decimal(acc["write_1h"]) * base * WRITE_1H_MULT
        + Decimal(acc["output"]) * (out_rate / MILLION)
    )


def summarize(by_model: dict) -> tuple[dict, Decimal, set]:
    tok = {k: 0 for k in TOKEN_KEYS}
    tok.update(calls=0, web_search=0, web_fetch=0)
    usd = Decimal(0)
    unknown = set()
    for model, acc in by_model.items():
        for k in tok:
            tok[k] += acc.get(k, 0)
        c = cost_for_model(model, acc)
        if c is None:
            unknown.add(model)
        else:
            usd += c
    tok["total"] = sum(tok[k] for k in TOKEN_KEYS)
    return tok, usd, unknown


def subagent_files(conv_path: Path) -> list[Path]:
    d = conv_path.parent / conv_path.stem / "subagents"
    return sorted(d.glob("*.jsonl")) if d.is_dir() else []


def find_conversations() -> list[Path] | None:
    """Return conversation transcripts, or None if there is no projects dir."""
    pd = projects_dir()
    if not pd.is_dir():
        return None
    return sorted(pd.glob("*/*.jsonl"))


# --- Formatting --------------------------------------------------------------
def usd_str(d: Decimal) -> str:
    return f"${d.quantize(Decimal('0.0001'))}"


def eur_str(d: Decimal, rate: Decimal) -> str:
    return f"€{(d * rate).quantize(Decimal('0.0001'))}"


UNAVAILABLE_MESSAGE = (
    "This skill reads Claude Cowork / Claude Code conversation transcripts, which "
    "are stored locally only when you work inside Cowork or Claude Code. I couldn't "
    "find any transcripts on this machine (~/.claude/projects), so there's nothing "
    "to measure here.\n\nIf you're running this outside of Cowork or Claude Code, "
    "that's expected — please open the skill from within a Cowork or Claude Code "
    "session and try again."
)


def unavailable(reason: str, as_json: bool):
    payload = {"status": "unavailable", "reason": reason, "message": UNAVAILABLE_MESSAGE}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(UNAVAILABLE_MESSAGE)
    return 0


def model_block_json(by_model: dict, rate: Decimal) -> list:
    out = []
    for model, acc in sorted(by_model.items()):
        c = cost_for_model(model, acc)
        out.append({
            "model": model,
            "priced": c is not None,
            "calls": acc["calls"],
            "tokens": {k: acc[k] for k in TOKEN_KEYS},
            "total_tokens": sum(acc[k] for k in TOKEN_KEYS),
            "usd": float((c or Decimal(0)).quantize(Decimal("0.000001"))),
            "eur": float(((c or Decimal(0)) * rate).quantize(Decimal("0.000001"))),
        })
    return out


def run_current(args, files, rate):
    conv = max(files, key=lambda p: p.stat().st_mtime)
    by_model = aggregate_file(conv)
    sub_calls = 0
    if args.include_subagents:
        for sf in subagent_files(conv):
            before = sum(a["calls"] for a in by_model.values())
            aggregate_file(sf, by_model)
            sub_calls += sum(a["calls"] for a in by_model.values()) - before
    tok, usd, unknown = summarize(by_model)
    title, started = file_meta(conv)

    if args.json:
        print(json.dumps({
            "status": "ok",
            "mode": "current",
            "rate_eur_per_usd": float(rate),
            "conversation": {
                "title": title,
                "transcript": conv.name,
                "started_at": started,
                "calls": tok["calls"],
                "subagent_calls_included": sub_calls if args.include_subagents else None,
                "tokens": {**{k: tok[k] for k in TOKEN_KEYS}, "total": tok["total"]},
                "server_tool_use": {"web_search": tok["web_search"], "web_fetch": tok["web_fetch"]},
                "by_model": model_block_json(by_model, rate),
                "usd": float(usd.quantize(Decimal("0.000001"))),
                "eur": float((usd * rate).quantize(Decimal("0.000001"))),
            },
            "unknown_models": sorted(unknown),
        }, indent=2))
        return 0

    print("Claude Cowork → API cost estimate (current conversation)")
    print(f"Conversation : {title}")
    print(f"Transcript   : {conv.name}")
    print(f"API calls    : {tok['calls']}"
          + (f" (+{sub_calls} subagent)" if args.include_subagents else ""))
    print()
    print("Tokens to replay this conversation on the API:")
    print(f"  Uncached input : {tok['input']:,}")
    print(f"  Cache read     : {tok['cache_read']:,}")
    print(f"  Cache write    : {tok['write_5m'] + tok['write_1h']:,}"
          f"  (5-min {tok['write_5m']:,} / 1-hour {tok['write_1h']:,})")
    print(f"  Output         : {tok['output']:,}")
    print(f"  TOTAL          : {tok['total']:,}")
    print()
    print(f"Estimated API cost (list price, cache-aware):")
    print(f"  USD : {usd_str(usd)}")
    print(f"  EUR : {eur_str(usd, rate)}   (at {rate} EUR per USD)")
    if unknown:
        print()
        print(f"  ! Unknown model(s) priced at $0: {', '.join(sorted(unknown))}."
              " Add them to PRICES in cost.py.")
    return 0


def run_history(args, files, rate):
    rows = []
    grand = {k: 0 for k in TOKEN_KEYS}
    grand["total"] = 0
    grand_usd = Decimal(0)
    unknown_all = set()
    for conv in files:
        by_model = aggregate_file(conv)
        if args.include_subagents:
            for sf in subagent_files(conv):
                aggregate_file(sf, by_model)
        tok, usd, unknown = summarize(by_model)
        if tok["total"] == 0:
            continue
        title, started = file_meta(conv)
        rows.append({"title": title, "transcript": conv.name, "started_at": started,
                     "calls": tok["calls"], "tokens": tok, "usd": usd,
                     "by_model": by_model})
        for k in grand:
            grand[k] += tok[k]
        grand_usd += usd
        unknown_all |= unknown
    rows.sort(key=lambda r: r["usd"], reverse=True)

    if args.json:
        print(json.dumps({
            "status": "ok",
            "mode": "history",
            "rate_eur_per_usd": float(rate),
            "conversation_count": len(rows),
            "conversations": [{
                "title": r["title"],
                "transcript": r["transcript"],
                "started_at": r["started_at"],
                "calls": r["calls"],
                "total_tokens": r["tokens"]["total"],
                "tokens": {k: r["tokens"][k] for k in TOKEN_KEYS},
                "usd": float(r["usd"].quantize(Decimal("0.000001"))),
                "eur": float((r["usd"] * rate).quantize(Decimal("0.000001"))),
            } for r in rows],
            "total": {
                "total_tokens": grand["total"],
                "tokens": {k: grand[k] for k in TOKEN_KEYS},
                "usd": float(grand_usd.quantize(Decimal("0.000001"))),
                "eur": float((grand_usd * rate).quantize(Decimal("0.000001"))),
            },
            "unknown_models": sorted(unknown_all),
        }, indent=2))
        return 0

    print("Claude Cowork → API cost estimate (all conversations)")
    print(f"{len(rows)} conversation(s) under ~/.claude/projects, "
          f"priced at list price (cache-aware). Rate: {rate} EUR per USD.")
    print()
    print(f"{'#':>2}  {'Conversation':<44} {'Tokens':>14} {'USD':>12} {'EUR':>12}")
    print("-" * 88)
    for i, r in enumerate(rows, 1):
        title = r["title"]
        if len(title) > 43:
            title = title[:40] + "..."
        print(f"{i:>2}  {title:<44} {r['tokens']['total']:>14,} "
              f"{usd_str(r['usd']):>12} {eur_str(r['usd'], rate):>12}")
    print("-" * 88)
    print(f"{'':>2}  {'TOTAL':<44} {grand['total']:>14,} "
          f"{usd_str(grand_usd):>12} {eur_str(grand_usd, rate):>12}")
    if unknown_all:
        print()
        print(f"! Unknown model(s) priced at $0: {', '.join(sorted(unknown_all))}."
              " Add them to PRICES in cost.py.")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Estimate Claude API cost of Cowork conversations.")
    p.add_argument("--mode", choices=["current", "history"], default="current")
    p.add_argument("--rate-eur", type=Decimal, default=Decimal("0.92"),
                   help="EUR per 1 USD (approximate, editable). Default 0.92.")
    p.add_argument("--include-subagents", action="store_true",
                   help="Also count subagent API calls.")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = p.parse_args(argv)

    # Windows consoles default to cp1252 and can't encode → / € — force UTF-8.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    files = find_conversations()
    if files is None:
        return unavailable("no_projects_dir", args.json)
    if not files:
        return unavailable("no_conversations", args.json)

    rate = args.rate_eur
    if args.mode == "current":
        return run_current(args, files, rate)
    return run_history(args, files, rate)


if __name__ == "__main__":
    sys.exit(main())
