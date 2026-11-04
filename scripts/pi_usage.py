#!/usr/bin/env python3
"""Which tools and skills sessions actually use, and which files they carry.

Carry is tokens multiplied by the calls remaining before the session ends or
compacts: the number of times that result was re-sent.
"""

import collections
import json
import pathlib
import re
import sys

CHARS_PER_TOKEN = 4


def norm(path):
    path = re.sub(r"^.*/\.worktrees/[^/]+/", "", path or "?")
    path = re.sub(r"^.*/singletoned/chitty/", "", path)
    return path.replace(str(pathlib.Path.home()), "~")


def flush(pending, carry, calls):
    for path, tok, at in pending:
        carry[path] += tok * (calls - at)
    pending.clear()


def main():
    tools, tool_sessions = collections.Counter(), collections.Counter()
    skills, reads, carry = (collections.Counter() for _ in range(3))
    read_sessions = collections.Counter()
    files = [f for root in sys.argv[1:] for f in pathlib.Path(root).rglob("*.jsonl")]
    sessions = dup_tok = all_tok = 0
    for f in files:
        sessions += 1
        args, seen_tools, pending, seen_paths = {}, set(), [], collections.Counter()
        calls = 0

        for line in f.read_text(errors="replace").splitlines():
            e = json.loads(line)
            if e.get("type") == "compaction":
                flush(pending, carry, calls)
            if e.get("type") != "message":
                continue
            m = e["message"]
            if m.get("role") == "assistant":
                calls += 1
                for b in m.get("content") or []:
                    if b.get("type") == "toolCall":
                        a = b.get("arguments") or {}
                        a = a if isinstance(a, dict) else {}
                        args[b.get("id")] = a
                        tools[b.get("name")] += 1
                        seen_tools.add(b.get("name"))
            elif m.get("role") == "toolResult" and m.get("toolName") == "read":
                a = args.get(m.get("toolCallId"), {})
                p = norm(a.get("path"))
                tok = (
                    sum(
                        len(b.get("text", ""))
                        for b in m.get("content") or []
                        if b.get("type") == "text"
                    )
                    // CHARS_PER_TOKEN
                )
                reads[p] += tok
                all_tok += tok
                if p in seen_paths:
                    dup_tok += tok
                seen_paths[p] += 1
                pending.append((p, tok, calls))
                hit = re.search(r"skills/([^/]+)/SKILL\.md", a.get("path") or "")
                if hit:
                    skills[hit.group(1)] += 1
        flush(pending, carry, calls)
        tool_sessions.update(seen_tools)
        read_sessions.update(seen_paths.keys())
    print(f"sessions {sessions}\n\nTOOL USE (calls, sessions)")
    for k, v in tools.most_common():
        print(f"  {v:6} {tool_sessions[k]:4}  {k}")
    print("\nSKILL.md reads", skills.most_common())
    print(
        f"\nREADS: {all_tok:,} tok total, {dup_tok:,} ({100 * dup_tok / all_tok:.0f}%) "
        "are repeat reads in the same session"
    )
    print("top by carry (token-calls), read tok, sessions")
    for k, v in carry.most_common(15):
        print(f"  {v:>12,}  {reads[k]:>9,}  {read_sessions[k]:3}  {k}")


main()
