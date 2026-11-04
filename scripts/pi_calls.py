#!/usr/bin/env python3
"""What the model calls were for, priced at each call's exact billed cost.

Each call re-sends the context, so a call's cost is what it costs to decide on
its tool calls. A call with several tools splits its cost evenly between them.
Classifying shell by its text is a heuristic; the costs themselves are exact.
"""

import collections
import itertools
import json
import pathlib
import re
import statistics
import sys

VERIFY = re.compile(r"\b(make (check|test|format)|npm test|ruff|pyright|unittest|mate check)\b")
CHITTY = re.compile(r"\bchitty\s")
GIT = re.compile(r"\bgit\s")
QUOTED = re.compile(r"\"(?:[^\"\\\\]|\\\\.)*\"|'[^']*'")
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n\s*\1\s*(?:\n|$)", re.DOTALL)
SHELL_TOOLS = {"bash", "ctx_execute", "ctx_batch_execute", "ctx_execute_file"}
EXPLORE_TOOLS = {"read", "ctx_search", "brave_search"}
EDIT_TOOLS = {"edit", "write"}
READ_ONLY = {"explore: read or search", "explore: shell", "git"}
CONTEXT_BANDS = ((30_000, "<30k"), (60_000, "30-60k"), (100_000, "60-100k"), (10**9, "100k+"))
LENGTH_BANDS = ((20, "<20"), (50, "20-49"), (100, "50-99"), (10**9, "100+"))


def classify(block):
    name = block.get("name")
    args = block.get("arguments")
    args = args if isinstance(args, dict) else {}
    if name in EDIT_TOOLS:
        return "edit"
    if name in EXPLORE_TOOLS:
        return "explore: read or search"
    if name == "subagent":
        return "subagent"
    if name in SHELL_TOOLS:
        script = args.get("command") or args.get("code") or ""
        for item in args.get("commands") or []:
            script += "\n" + (item.get("command", "") if isinstance(item, dict) else "")
        # Quoted text such as `--note "make check passes"` is not a command.
        text = QUOTED.sub("", HEREDOC.sub("", script))
        if VERIFY.search(text):
            return "verify"
        if CHITTY.search(text):
            return "chitty"
        if GIT.search(text):
            return "git"
        return "explore: shell"
    return "other tool"


def load_calls(path):
    calls = []
    for line in path.read_text(errors="replace").splitlines():
        entry = json.loads(line)
        if entry.get("type") != "message" or entry["message"].get("role") != "assistant":
            continue
        message = entry["message"]
        usage = message.get("usage") or {}
        cost = usage.get("cost") or {}
        tools = [b for b in message.get("content") or [] if b.get("type") == "toolCall"]
        calls.append(
            {
                "cost": cost.get("total", 0),
                "output_cost": cost.get("output", 0),
                "reasoning": usage.get("reasoning", 0),
                "output": usage.get("output", 0),
                "context": usage.get("input", 0)
                + usage.get("cacheRead", 0)
                + usage.get("cacheWrite", 0),
                "kinds": [classify(b) for b in tools] or ["no tool (reply)"],
            }
        )
    return calls


def band(value, bands):
    return next(label for limit, label in bands if value < limit)


def table(title, spend, count, total, order=None):
    print(f"\n{title}")
    for key in order or [k for k, _ in spend.most_common()]:
        cost = spend[key]
        print(f"  ${cost:7.2f} {100 * cost / total:5.1f}% {count[key]:6} calls  {key}")


def main():
    sessions = [
        calls
        for root in sys.argv[1:]
        for path in pathlib.Path(root).rglob("*.jsonl")
        if (calls := load_calls(path))
    ]
    every = [call for calls in sessions for call in calls]
    total = sum(c["cost"] for c in every)
    print(f"sessions {len(sessions)}, calls {len(every)}, cost ${total:.2f}")
    print(f"mean cost per call ${total / len(every):.4f}")
    output_cost = sum(c["output_cost"] for c in every)
    reasoning = sum(c["reasoning"] for c in every)
    output = sum(c["output"] for c in every)
    print(f"output ${output_cost:.2f}; reasoning {100 * reasoning / output:.0f}% of output tokens")

    spend, count = collections.Counter(), collections.Counter()
    for call in every:
        for kind in call["kinds"]:
            spend[kind] += call["cost"] / len(call["kinds"])
            count[kind] += 1 / len(call["kinds"])
    table("BY PURPOSE OF THE CALL", spend, count, total)

    spend, count = collections.Counter(), collections.Counter()
    for call in every:
        key = band(call["context"], CONTEXT_BANDS)
        spend[key] += call["cost"]
        count[key] += 1
    table("BY CONTEXT SIZE", spend, count, total, [label for _, label in CONTEXT_BANDS])

    spend, count = collections.Counter(), collections.Counter()
    for calls in sessions:
        key = band(len(calls), LENGTH_BANDS)
        spend[key] += sum(c["cost"] for c in calls)
        count[key] += 1
    print("\nBY SESSION LENGTH (count is sessions)")
    for _, key in LENGTH_BANDS:
        share = 100 * spend[key] / total
        print(f"  ${spend[key]:7.2f} {share:5.1f}% {count[key]:4} sessions  {key}")
    ranked = sorted((sum(c["cost"] for c in calls) for calls in sessions), reverse=True)
    print(f"top 5 sessions ${sum(ranked[:5]):.2f}; median session ${statistics.median(ranked):.2f}")

    phases = collections.Counter()
    phase_calls = collections.Counter()
    streak_calls = single = 0
    for calls in sessions:
        edits = [i for i, c in enumerate(calls) if "edit" in c["kinds"]]
        for i, call in enumerate(calls):
            if not edits:
                phase = "session never edits"
            elif i < edits[0]:
                phase = "before first edit"
            elif i <= edits[-1]:
                phase = "first edit to last edit"
            else:
                phase = "after last edit"
            phases[phase] += call["cost"]
            phase_calls[phase] += 1
        for current, following in itertools.pairwise(calls):
            one_read_only = len(current["kinds"]) == 1 and current["kinds"][0] in READ_ONLY
            if one_read_only:
                single += 1
                if len(following["kinds"]) == 1 and following["kinds"][0] in READ_ONLY:
                    streak_calls += 1
    table("BY PHASE", phases, phase_calls, total)
    mean = total / len(every)
    print(
        f"\nsingle read-only calls {single}; immediately followed by another: {streak_calls}"
        f" (about ${streak_calls * mean:.2f} at mean call cost)"
    )
    tools_per_call = [len(c["kinds"]) for c in every if c["kinds"] != ["no tool (reply)"]]
    print(f"mean tools per tool-using call {statistics.mean(tools_per_call):.2f}")


main()
