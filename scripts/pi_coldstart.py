#!/usr/bin/env python3
"""Per-session cold-start report: what a session pays before useful work starts.

"Orientation" is everything up to the first `edit`/`write` call. Sessions that
never edit count entirely as orientation and are reported separately.
"""

import collections
import json
import pathlib
import statistics
import sys

CHARS_PER_TOKEN = 4
WRITE_TOOLS = {"edit", "write"}


def blocks_len(content):
    if isinstance(content, str):
        return len(content)
    return sum(len(b.get("text", "")) for b in content or [] if b.get("type") == "text")


def session(path):
    s = {
        "path": path,
        "calls": 0,
        "cost": 0.0,
        "first_total": None,
        "first_user": 0,
        "first_input": 0,
        "first_cached": 0,
        "orient_calls": None,
        "orient_cost": None,
        "orient_tools": collections.Counter(),
        "start": None,
        "first_tool": None,
        "injected": 0,
    }
    for line in path.read_text(errors="replace").splitlines():
        e = json.loads(line)
        if e.get("type") == "session":
            s["start"] = e["timestamp"][:10]
        if e.get("type") == "custom_message" and s["first_total"] is None:
            s["injected"] += blocks_len(e.get("content"))
        if e.get("type") != "message":
            continue
        m = e["message"]
        if m.get("role") == "user" and s["first_total"] is None:
            s["first_user"] += blocks_len(m.get("content"))
        if m.get("role") == "toolResult" and s["orient_calls"] is None:
            s["orient_tools"][m.get("toolName")] += blocks_len(m.get("content"))
        if m.get("role") != "assistant":
            continue
        u = m.get("usage") or {}
        total = u.get("input", 0) + u.get("cacheRead", 0) + u.get("cacheWrite", 0)
        if s["first_total"] is None:
            s["first_total"], s["first_input"], s["first_cached"] = (
                total,
                u.get("input", 0),
                u.get("cacheRead", 0),
            )
        s["calls"] += 1
        s["cost"] += (u.get("cost") or {}).get("total", 0)
        s["last_total"] = total
        names = {b.get("name") for b in m.get("content") or [] if b.get("type") == "toolCall"}
        if names & WRITE_TOOLS and s["orient_calls"] is None:
            s["orient_calls"], s["orient_cost"], s["orient_ctx"] = s["calls"], s["cost"], total
    return s


def q(xs):
    xs = sorted(xs)
    n = len(xs)
    return (
        f"min {xs[0]:,.0f}  p25 {xs[n // 4]:,.0f}  p50 {xs[n // 2]:,.0f}"
        f"  p75 {xs[3 * n // 4]:,.0f}  max {xs[-1]:,.0f}"
    )


def main():
    files = [f for root in sys.argv[1:] for f in pathlib.Path(root).rglob("*.jsonl")]
    ss = [session(f) for f in files]
    ss = [s for s in ss if s["calls"]]
    cost = sum(s["cost"] for s in ss)
    print(
        f"sessions with calls: {len(ss)}, cost ${cost:.2f}, "
        f"median calls {statistics.median(s['calls'] for s in ss)}"
    )
    print("calls/session:", q([s["calls"] for s in ss]))
    print(
        "cost/session $:",
        " ".join(f"{x:.2f}" for x in statistics.quantiles([s["cost"] for s in ss], n=4)),
    )
    prompt = [s["first_total"] - (s["first_user"] + s["injected"]) / CHARS_PER_TOKEN for s in ss]
    print("first-call context (tok):", q([s["first_total"] for s in ss]))
    print("baseline = first call minus user text (tok):", q(prompt))
    print(
        "first-call cached share: %.0f%%"
        % (100 * sum(s["first_cached"] for s in ss) / sum(s["first_total"] for s in ss))
    )
    print("\nbaseline by start date")
    by = collections.defaultdict(list)
    for s, p in zip(ss, prompt):
        by[s["start"]].append(p)
    for d in sorted(by):
        print(f"  {d}  n={len(by[d]):3}  median {statistics.median(by[d]):8,.0f}")
    edit = [s for s in ss if s["orient_calls"]]
    none = [s for s in ss if not s["orient_calls"]]
    print(
        f"\nsessions that edit: {len(edit)} (${sum(s['cost'] for s in edit):.2f}); "
        f"never edit: {len(none)} (${sum(s['cost'] for s in none):.2f})"
    )
    print("calls before first edit:", q([s["orient_calls"] for s in edit]))
    print("context at first edit (tok):", q([s["orient_ctx"] for s in edit]))
    oc = sum(s["orient_cost"] for s in edit)
    print(
        f"cost before first edit ${oc:.2f}, "
        f"{100 * oc / sum(s['cost'] for s in edit):.0f}% of editing sessions' cost"
    )
    print("\nchars/4 of tool output before first edit, across editing sessions")
    t = collections.Counter()
    for s in edit:
        t.update(s["orient_tools"])
    for k, v in t.most_common(10):
        print(f"  {v // CHARS_PER_TOKEN:>9,} tok  {k}")
    print("\nsmallest sessions (calls, cost, first ctx)")
    for s in sorted(ss, key=lambda s: s["calls"])[:8]:
        print(f"  {s['calls']:4} ${s['cost']:.3f} {s['first_total']:,}")
    short = [s for s in ss if s["calls"] <= 10]
    print(f"\nsessions <=10 calls: {len(short)}, ${sum(s['cost'] for s in short):.2f}")


main()
