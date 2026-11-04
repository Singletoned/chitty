#!/usr/bin/env python3
"""Attribute Pi session spend to what was sitting in context. No LLM involved.

Billing per API call is exact (from `usage`). The split of each call's input
across context items is estimated from character counts, scaled to the exact
total for that call. The first N cached tokens are priced at that call's
cache-read rate; the remainder at its write/uncached rate.
"""

import collections
import json
import pathlib
import re
import statistics
import sys

CHARS_PER_TOKEN = 4
IMAGE_TOKENS = 1500


def text_len(content):
    if isinstance(content, str):
        return len(content)
    n = 0
    for b in content or []:
        t = b.get("type")
        if t == "text":
            n += len(b.get("text", ""))
        elif t == "image":
            n += IMAGE_TOKENS * CHARS_PER_TOKEN
    return n


def bash_key(cmd):
    cmd = re.sub(r"^\s*(cd\s+\S+\s*(&&|;)\s*)+", "", cmd or "").strip()
    words = cmd.split()
    if not words:
        return "bash: (empty)"
    head = words[0].rsplit("/", 1)[-1]
    if head in {"git", "uv", "make", "mate", "chitty", "npm", "docker"} and len(words) > 1:
        return f"bash: {head} {words[1]}"
    return f"bash: {head}"


def walk(path, agg):
    items, index, last_id = [], {}, None
    calls = {}
    prev_total, new_since_call = None, 0
    baseline = None
    for line in path.read_text(errors="replace").splitlines():
        e = json.loads(line)
        typ = e.get("type")
        eid, parent = e.get("id"), e.get("parentId")
        if typ == "session" or eid is None:
            continue
        # Branch: rewind context to this entry's parent.
        if parent is not None and parent != last_id and parent in index:
            del items[index[parent] + 1 :]
            index = {k: v for k, v in index.items() if v <= index[parent]}
        added = []
        if typ == "compaction":
            agg["compactions"] += 1
            keep = index.get(e.get("firstKeptEntryId"), len(items))
            items[:] = [["compaction summary", len(e.get("summary", "")), None]] + items[keep:]
            index = {k: v - keep + 1 for k, v in index.items() if v >= keep}
            prev_total, new_since_call = None, 0
        elif typ == "custom_message":
            added.append(("injected: " + e.get("customType", "?"), text_len(e.get("content"))))
        elif typ == "branch_summary":
            added.append(("branch summary", len(e.get("summary", ""))))
        elif typ == "message":
            m = e["message"]
            role = m.get("role")
            if role == "user":
                added.append(("user message", text_len(m.get("content"))))
            elif role == "toolResult":
                name = m.get("toolName", "?")
                key = "tool: " + name
                args = calls.get(m.get("toolCallId"), {})
                if name == "bash":
                    key = bash_key(args.get("command"))
                n = text_len(m.get("content"))
                added.append((key, n))
                agg["results"][key] += 1
                agg["result_chars"][key] += n
                if name == "read" and args.get("path"):
                    agg["read_paths"][pathlib.Path(args["path"]).suffix or "(none)"] += n
            elif role == "assistant":
                u = m.get("usage") or {}
                c = u.get("cost") or {}
                total = u.get("input", 0) + u.get("cacheRead", 0) + u.get("cacheWrite", 0)
                model = f"{m.get('provider')}/{m.get('model')}"
                agg["models"][model] += c.get("total", 0)
                agg["model_calls"][model] += 1
                for k in ("input", "output", "cacheRead", "cacheWrite"):
                    agg["kind_cost"][k] += c.get(k, 0)
                    agg["kind_tokens"][k] += u.get(k, 0)
                agg["sum_context"] += total
                agg["calls"] += 1
                agg["output_cost"] += c.get("output", 0)

                est = [[k, n / CHARS_PER_TOKEN] for k, n, _ in items]
                s = sum(n for _, n in est)
                if baseline is None:
                    baseline = max(total - s, 0)
                base = min(baseline, total)
                factor = (total - base) / s if s else 0
                agg["scale"].append(factor)
                # Calibration: measured context growth vs estimated growth.
                if prev_total is not None and new_since_call and total >= prev_total:
                    agg["calib"].append((total - prev_total) / (new_since_call / CHARS_PER_TOKEN))
                read_left = u.get("cacheRead", 0)
                read_rate = c.get("cacheRead", 0) / u["cacheRead"] if u.get("cacheRead") else 0
                fresh = u.get("input", 0) + u.get("cacheWrite", 0)
                fresh_rate = (c.get("input", 0) + c.get("cacheWrite", 0)) / fresh if fresh else 0
                for k, tok in [["system prompt + tool defs", base]] + [
                    [k, n * factor] for k, n in est
                ]:
                    r = min(tok, read_left)
                    read_left -= r
                    agg["attr_cost"][k] += r * read_rate + (tok - r) * fresh_rate
                    agg["attr_tokens"][k] += tok
                agg["attr_ok"] += c.get("input", 0) + c.get("cacheRead", 0) + c.get("cacheWrite", 0)
                prev_total, new_since_call = total, 0

                thinking = text = 0
                for b in m.get("content") or []:
                    t = b.get("type")
                    if t == "thinking":
                        thinking += len(b.get("thinking", ""))
                    elif t == "text":
                        text += len(b.get("text", ""))
                    elif t == "toolCall":
                        raw = b.get("arguments") or {}
                        n = len(raw) if isinstance(raw, str) else len(json.dumps(raw))
                        if isinstance(raw, str):  # some providers store args as a JSON string
                            try:
                                raw = json.loads(raw)
                            except json.JSONDecodeError:
                                agg["bad_args"]["string"] += 1
                                raw = {}
                        calls[b.get("id")] = raw if isinstance(raw, dict) else {}
                        added.append(("assistant: tool call args", n))
                if thinking:
                    added.append(("assistant: thinking", thinking))
                if text:
                    added.append(("assistant: text", text))
        for k, n in added:
            items.append([k, n, eid])
            new_since_call += n
        index[eid] = len(items) - 1
        if eid:
            last_id = eid


def main():
    agg = collections.defaultdict(collections.Counter)
    for k in ("compactions", "calls", "sum_context", "output_cost", "attr_ok"):
        agg[k] = 0
    agg["scale"], agg["calib"] = [], []
    files = sorted(f for root in sys.argv[1:] for f in pathlib.Path(root).rglob("*.jsonl"))
    bad = 0
    for f in files:
        try:
            walk(f, agg)
        except json.JSONDecodeError:
            bad += 1
    total = sum(agg["models"].values())
    print(
        f"sessions {len(files)} (unparseable {bad}), calls {agg['calls']}, "
        f"compactions {agg['compactions']}, cost ${total:,.2f}"
    )
    print("\nBY MODEL")
    for k, v in agg["models"].most_common(10):
        print(f"  {v:10,.2f}  {agg['model_calls'][k]:7}  {k}")
    print("\nBY BILLING KIND (exact)")
    for k, v in agg["kind_cost"].most_common():
        print(f"  {v:10,.2f}  {100 * v / total:5.1f}%  {agg['kind_tokens'][k]:>16,} tok  {k}")
    print(f"  mean context per call: {agg['sum_context'] / agg['calls']:,.0f} tok")
    print("\nATTRIBUTED INPUT COST, what was in context (estimated split)")
    attr = sum(agg["attr_cost"].values())
    print(
        f"  allocated ${attr:,.2f} of ${agg['attr_ok']:,.2f} exact input-side; "
        f"output ${agg['output_cost']:,.2f}"
    )
    for k, v in agg["attr_cost"].most_common(30):
        c = agg["results"][k]
        extra = (
            f"  {c:6} results, {agg['result_chars'][k] // c // CHARS_PER_TOKEN:6,} tok/result"
            if c
            else ""
        )
        print(f"  {v:10,.2f}  {100 * v / total:5.1f}%  {k}{extra}")
    print("\nread chars by file type")
    tot = sum(agg["read_paths"].values()) or 1
    for k, v in agg["read_paths"].most_common(8):
        print(f"  {100 * v / tot:5.1f}%  {k}")
    q = statistics.quantiles(agg["calib"], n=10)
    print(
        f"\nCALIBRATION measured/estimated growth: n={len(agg['calib'])} "
        f"p10={q[0]:.2f} p50={q[4]:.2f} p90={q[8]:.2f}"
    )
    q = statistics.quantiles([x for x in agg["scale"] if x], n=10)
    print(f"per-call scale factor: p10={q[0]:.2f} p50={q[4]:.2f} p90={q[8]:.2f}")


main()
