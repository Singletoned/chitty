#!/usr/bin/env python3
"""How `read` is used: how much of each file, and whether it seemed to matter.

Lines read and file lengths are exact, taken from Pi's arguments and its "N more
lines" marker. Relevance is a heuristic: an identifier first seen in a read is
"reused" if the agent later writes it, in text, thinking or tool arguments. The
"needed" share is the lines near such identifiers. A read with no trace may still
have told the agent that something was absent, so treat it as an upper bound.
"""

import collections
import json
import pathlib
import re
import statistics
import sys

CHARS_PER_TOKEN = 4
INPUT_DOLLARS_PER_TOKEN = 2e-6
CACHED_DOLLARS_PER_TOKEN = 0.2e-6
NEEDED_CONTEXT_LINES = 20
MIN_IDENTIFIER_LENGTH = 6
WHOLE_FILE_COVERAGE = 0.9
BUCKETS = ((100, "<100"), (300, "100-299"), (700, "300-699"), (10**9, "700+"))
IDENTIFIER = re.compile(rf"[A-Za-z_][A-Za-z0-9_]{{{MIN_IDENTIFIER_LENGTH - 1},}}")
MORE_LINES = re.compile(r"\[(\d+) more lines in file\. Use offset=\d+ to continue\.\]\s*$")
WRITE_TOOLS = {"edit", "write"}


def norm(path):
    path = re.sub(r"^(.*/)?\.worktrees/[^/]+/", "", path or "?")
    path = re.sub(r"^.*/singletoned/chitty/", "", path)
    return path.replace(str(pathlib.Path.home()), "~")


def result_text(message):
    return "".join(
        b.get("text", "") for b in message.get("content") or [] if b.get("type") == "text"
    )


def assistant_output(message):
    parts = []
    for block in message.get("content") or []:
        kind = block.get("type")
        if kind == "text":
            parts.append(block.get("text", ""))
        elif kind == "thinking":
            parts.append(block.get("thinking", ""))
        elif kind == "toolCall":
            parts.append(json.dumps(block.get("arguments") or {}))
    return "\n".join(parts)


def load_session(path):
    """Return the session's reads plus when each identifier first and last appeared."""
    session = {"reads": [], "errors": [], "edited": {}, "compactions": [], "calls": 0}
    first_seen, last_written, args = {}, {}, {}
    step = 0
    for line in path.read_text(errors="replace").splitlines():
        entry = json.loads(line)
        if entry.get("type") == "compaction":
            session["compactions"].append(session["calls"])
        if entry.get("type") != "message":
            continue
        message = entry["message"]
        step += 1
        if message.get("role") == "assistant":
            session["calls"] += 1
            for block in message.get("content") or []:
                if block.get("type") == "toolCall" and isinstance(block.get("arguments"), dict):
                    args[block.get("id")] = block["arguments"]
                    if block.get("name") in WRITE_TOOLS:
                        session["edited"][norm(block["arguments"].get("path"))] = step
            for word in IDENTIFIER.findall(assistant_output(message)):
                first_seen.setdefault(word, step)
                last_written[word] = step
        elif message.get("role") == "user":
            for word in IDENTIFIER.findall(result_text(message)):
                first_seen.setdefault(word, step)
        elif message.get("role") == "toolResult":
            text = result_text(message)
            if message.get("toolName") == "read":
                call = args.get(message.get("toolCallId"), {})
                if message.get("isError"):
                    session["errors"].append(text[:40])
                else:
                    session["reads"].append(
                        {
                            "path": norm(call.get("path")),
                            "offset": call.get("offset") or 1,
                            "limit": call.get("limit"),
                            "text": text,
                            "step": step,
                            "call": session["calls"],
                        }
                    )
            for word in IDENTIFIER.findall(text):
                first_seen.setdefault(word, step)
    return session, first_seen, last_written


def analyse_read(read, session, first_seen, last_written):
    match = MORE_LINES.search(read["text"])
    lines = read["text"][: match.start()].splitlines() if match else read["text"].splitlines()
    read["lines"] = len(lines)
    read["total"] = read["offset"] - 1 + len(lines) + (int(match.group(1)) if match else 0)
    read["tokens"] = len(read["text"]) // CHARS_PER_TOKEN
    end = next((c for c in session["compactions"] if c >= read["call"]), session["calls"])
    read["carry"] = read["tokens"] * (end - read["call"])
    read["cost"] = (
        read["tokens"] * INPUT_DOLLARS_PER_TOKEN + read["carry"] * CACHED_DOLLARS_PER_TOKEN
    )
    new = {
        word for word in IDENTIFIER.findall(read["text"]) if first_seen.get(word) == read["step"]
    }
    used = {word for word in new if last_written.get(word, 0) > read["step"]}
    read["new_ids"], read["used_ids"] = len(new), len(used)
    needed = set()
    for number, line in enumerate(lines):
        if used & set(IDENTIFIER.findall(line)):
            needed.update(range(number - NEEDED_CONTEXT_LINES, number + NEEDED_CONTEXT_LINES + 1))
    read["needed"] = len(needed & set(range(len(lines))))
    read["edited_later"] = session["edited"].get(read["path"], 0) > read["step"]
    read["range"] = (read["offset"], read["offset"] + len(lines))


def bucket(total):
    return next(label for limit, label in BUCKETS if total < limit)


def group_report(groups, title):
    """Print, by file size, how much of a file one session reads."""
    table = collections.defaultdict(lambda: collections.Counter())
    for reads in groups.values():
        total = reads[-1]["total"]
        seen = set()
        for read in reads:
            seen.update(range(*read["range"]))
        row = table[bucket(total)]
        row["groups"] += 1
        row["reads"] += len(reads)
        row["tokens"] += sum(r["tokens"] for r in reads)
        row["cost"] += sum(r["cost"] for r in reads)
        row["coverage"] += min(len(seen) / total, 1) if total else 0
        row["whole"] += total > 0 and len(seen) / total >= WHOLE_FILE_COVERAGE
        row["read_lines"] += sum(r["lines"] for r in reads)
        row["unique_lines"] += len(seen)
        row["needed"] += sum(r["needed"] for r in reads)
    print(f"\nBY FILE LENGTH, {title} (one row counts one file in one session)")
    print("  lines    files reads/file tok/file  cost  mean-cover  90%+read  repeat  needed")
    for _, label in BUCKETS:
        row = table[label]
        if not row["groups"]:
            continue
        n = row["groups"]
        print(
            f"  {label:8} {n:4} {row['reads'] / n:9.1f} {row['tokens'] / n:8,.0f}"
            f" ${row['cost']:5.2f} {100 * row['coverage'] / n:9.0f}%"
            f" {100 * row['whole'] / n:8.0f}%"
            f" {100 * (1 - row['unique_lines'] / max(row['read_lines'], 1)):6.0f}%"
            f" {100 * row['needed'] / max(row['read_lines'], 1):6.0f}%"
        )


def relevance_report(reads):
    edited = [r for r in reads if r["edited_later"]]
    other = [r for r in reads if not r["edited_later"]]
    print("\nRELEVANCE: tokens read, cost, share of new identifiers the agent later wrote")
    for label, rows in (("file edited later", edited), ("file not edited later", other)):
        tokens = sum(r["tokens"] for r in rows)
        cost = sum(r["cost"] for r in rows)
        rates = [r["used_ids"] / r["new_ids"] for r in rows if r["new_ids"]]
        needed = sum(r["needed"] for r in rows) / max(sum(r["lines"] for r in rows), 1)
        print(
            f"  {label:22} {len(rows):5} reads {tokens:>9,} tok ${cost:6.2f}"
            f"  median reuse {100 * statistics.median(rates):3.0f}%  needed {100 * needed:3.0f}%"
        )
    print("\nNOT EDITED LATER, by how much left a trace")
    bands = collections.Counter()
    for read in other:
        new = read["new_ids"]
        if not new:
            band = "nothing new in it"
        elif not read["used_ids"]:
            band = "no trace at all"
        elif read["used_ids"] / new < 0.05:
            band = "under 5% reused"
        else:
            band = "5% or more reused"
        bands[band, "n"] += 1
        bands[band, "cost"] += read["cost"]
        bands[band, "tokens"] += read["tokens"]
    for band in ("nothing new in it", "no trace at all", "under 5% reused", "5% or more reused"):
        print(
            f"  {band:20} {bands[band, 'n']:5} reads {bands[band, 'tokens']:>9,} tok"
            f" ${bands[band, 'cost']:6.2f}"
        )


def no_trace_report(reads):
    rows = [r for r in reads if not r["edited_later"] and r["new_ids"] and not r["used_ids"]]
    spend, count = collections.Counter(), collections.Counter()
    for read in rows:
        spend[read["path"]] += read["cost"]
        count[read["path"]] += 1
    print("\nNO TRACE: top files")
    for path, cost in spend.most_common(14):
        print(f"  ${cost:5.2f} {count[path]:3}  {path}")


def files_report(reads):
    by_file = collections.defaultdict(list)
    sessions = collections.defaultdict(set)
    for read in reads:
        by_file[read["path"]].append(read)
        sessions[read["path"]].add(read["session"])
    print("\nTOP FILES: cost, sessions, reads, lines, tok/read, % reads edited later, needed")
    ranked = sorted(by_file.items(), key=lambda item: -sum(r["cost"] for r in item[1]))
    for path, rows in ranked[:18]:
        lines = sum(r["lines"] for r in rows)
        edited = sum(r["edited_later"] for r in rows)
        print(
            f"  ${sum(r['cost'] for r in rows):5.2f} {len(sessions[path]):3} {len(rows):4}"
            f" {rows[-1]['total']:5} {sum(r['tokens'] for r in rows) // len(rows):6,}"
            f" {100 * edited // len(rows):4}%"
            f" {100 * sum(r['needed'] for r in rows) // max(lines, 1):4}%"
            f"  {path}"
        )


def main():
    reads, errors, groups = [], collections.Counter(), {}
    files = [f for root in sys.argv[1:] for f in pathlib.Path(root).rglob("*.jsonl")]
    for path in files:
        session, first_seen, last_written = load_session(path)
        errors.update(error.split(":")[0] for error in session["errors"])
        for read in session["reads"]:
            analyse_read(read, session, first_seen, last_written)
            read["session"] = str(path)
            groups.setdefault((str(path), read["path"]), []).append(read)
            reads.append(read)
    print(f"sessions {len(files)}, reads {len(reads)}, read errors {sum(errors.values())}")
    print(
        f"tokens {sum(r['tokens'] for r in reads):,}, "
        f"est. cost ${sum(r['cost'] for r in reads):.2f}"
    )
    print(f"median limit {statistics.median(r['limit'] for r in reads if r['limit'])}")
    print("\nPER READ")
    kinds = collections.Counter()
    for read in reads:
        whole = read["offset"] <= 1 and read["lines"] >= read["total"]
        head = read["offset"] <= 1
        kind = "whole file" if whole else "from the top, partial" if head else "from an offset"
        kinds[kind] += 1
        kinds[kind, "tokens"] += read["tokens"]
    total_tokens = sum(r["tokens"] for r in reads)
    for kind in ("whole file", "from the top, partial", "from an offset"):
        print(
            f"  {kinds[kind]:5} reads  "
            f"{100 * kinds[kind, 'tokens'] / total_tokens:3.0f}% of tokens  {kind}"
        )
    group_report(groups, "all files")
    spend = collections.Counter()
    for read in reads:
        spend[read["path"]] += read["cost"]
    top = spend.most_common(1)[0][0]
    group_report({k: v for k, v in groups.items() if k[1] != top}, f"excluding {top}")
    relevance_report(reads)
    no_trace_report(reads)
    files_report(reads)
    print("\nread errors", errors.most_common(5))


main()
