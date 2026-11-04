#!/usr/bin/env python3
"""Explain two large cost buckets: uncached input and tool call arguments.

Calls with at least `LARGE_INPUT` uncached tokens are grouped by what preceded
them. A large input after a long gap suggests cache expiry; with no gap it may
be either a miss or a large new tool result, which the logs cannot distinguish.
"""

import collections
import datetime
import json
import pathlib
import sys

CHARS_PER_TOKEN = 4
LARGE_INPUT = 5000
SHORT_GAP_SECONDS = 60
LONG_GAP_SECONDS = 300


def large_input_cause(previous, now, after_compaction):
    if previous is None:
        return "first call of session"
    if after_compaction:
        return "after compaction"
    gap = (now - previous).total_seconds()
    if gap > LONG_GAP_SECONDS:
        return "gap >5min"
    if gap > SHORT_GAP_SECONDS:
        return "gap 1-5min"
    return "no gap (<60s)"


def main():
    input_cost = 0.0
    causes, cause_counts = collections.Counter(), collections.Counter()
    arg_tokens, arg_calls = collections.Counter(), collections.Counter()
    other_usage = collections.Counter()
    for root in sys.argv[1:]:
        for path in pathlib.Path(root).rglob("*.jsonl"):
            previous, after_compaction = None, False
            for line in path.read_text(errors="replace").splitlines():
                entry = json.loads(line)
                if entry.get("type") == "compaction":
                    after_compaction = True
                if entry.get("type") != "message":
                    if '"usage"' in line or '"cost"' in line:
                        other_usage[f"{entry.get('type')}/{entry.get('customType')}"] += 1
                    continue
                message = entry["message"]
                if message.get("role") != "assistant":
                    continue
                for block in message.get("content") or []:
                    if block.get("type") == "toolCall":
                        raw = block.get("arguments") or {}
                        text = raw if isinstance(raw, str) else json.dumps(raw)
                        arg_tokens[block.get("name")] += len(text) // CHARS_PER_TOKEN
                        arg_calls[block.get("name")] += 1
                usage = message.get("usage") or {}
                cost = (usage.get("cost") or {}).get("input", 0)
                now = datetime.datetime.fromisoformat(entry["timestamp"])
                input_cost += cost
                if usage.get("input", 0) >= LARGE_INPUT:
                    cause = large_input_cause(previous, now, after_compaction)
                    causes[cause] += cost
                    cause_counts[cause] += 1
                previous, after_compaction = now, False
    print(f"uncached input cost ${input_cost:,.2f}")
    print(f"calls with >={LARGE_INPUT:,} uncached tokens, by what preceded them")
    for cause, cost in causes.most_common():
        print(f"  ${cost:9,.2f}  {cause_counts[cause]:6} calls  {cause}")
    print("usage recorded outside assistant messages:", other_usage.most_common(8))
    print("\ntool call arguments")
    total = sum(arg_tokens.values())
    for name, tokens in arg_tokens.most_common(8):
        share = 100 * tokens / total
        print(f"  {tokens:>12,} tok {share:5.1f}% {arg_calls[name]:6} calls  {name}")


main()
