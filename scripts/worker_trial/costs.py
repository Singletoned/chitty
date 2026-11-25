"""Token use and API-equivalent cost of each worker trial run.

Usage: python3 scripts/worker_trial/costs.py TRIAL_DIR

Reads TRIAL_DIR/results.tsv (written by run_trial.sh) and each harness's own
session logs, matched to a run by its clone path: Pi (~/.pi/agent/sessions),
Claude Code (~/.claude/projects), Codex (~/.codex/sessions) and agy
(~/.gemini/antigravity-cli/brain). Only sessions written after the run's clone
was created count, so a rerun does not add an earlier attempt's tokens.

Costs use API list prices per million tokens. Sessions on a subscription are not
billed this way: compare runs with these numbers, do not read them as a bill.
"""

import csv
import glob
import json
import os
import sys
from collections import Counter
from pathlib import Path

HOME = Path.home()

# $ per million tokens: input, output, cache write, cache read.
PRICES = {
    "gpt-6-luna": (0.10, 0.50, 0.125, 0.01),  # Pi's models-store.json
    "gpt-6.1-terra": (1.00, 5.00, 1.25, 0.05),  # Pi's models-store.json
    "claude-haiku-5-5": (0.10, 0.50, 0.125, 0.01),  # 5-minute cache writes
    "claude-sonnet-5-5": (2.00, 10.00, 2.50, 0.10),
    # Gemini Developer API standard tier, introductory rates to 2026-12-31
    # (ai.google.dev/gemini-api/docs/pricing); implicit caching has no storage fee.
    "gemini-3.8-flash-medium": (0.75, 3.75, 0.0, 0.075),
    # Standard tier as reported by secondary sources; not yet seen on ai.google.dev.
    "gemini-4-hydrogen-medium": (1.50, 7.50, 0.0, 0.075),
}
CLAUDE_1H_WRITE = {"claude-haiku-5-5": 0.20, "claude-sonnet-5-5": 4.00}
# A transcript that names the run's clone path fewer times than this only
# mentions it in passing (for example in `ps` output from another run).
AGY_MIN_MENTIONS = 10


class Run:
    def __init__(self, trial_dir: Path, variant: str, ticket: str) -> None:
        self.variant = variant
        self.name = f"{variant}--{ticket.lower()}"
        self.clone = trial_dir / "runs" / self.name
        self.path_marker = f"{self.clone}/"
        # Pi and Claude Code name session folders after the path, with `/` and
        # `.` replaced by `-`.
        self.folder_marker = f"{trial_dir.name}-runs-{self.name}-"

    def current(self, path: str) -> bool:
        clone = self.clone
        return clone.exists() and os.stat(path).st_mtime >= clone.stat().st_birthtime


def json_lines(path: str) -> list[dict]:
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def cost(model: str | None, tokens: Counter, write_1h: int) -> float | None:
    if model not in PRICES:
        return None
    inp, out, write, read = PRICES[model]
    write_5m = tokens["cache_write"] - write_1h
    total = (
        tokens["input"] * inp
        + tokens["output"] * out
        + write_5m * write
        + write_1h * CLAUDE_1H_WRITE.get(model, write)
        + tokens["cache_read"] * read
    )
    return total / 1_000_000


def pi_usage(run: Run) -> tuple[str | None, Counter]:
    tokens: Counter = Counter()
    model = None
    for path in glob.glob(str(HOME / f".pi/agent/sessions/*{run.folder_marker}*/*.jsonl")):
        if not run.current(path):
            continue
        for event in json_lines(path):
            if event.get("type") == "model_change":
                model = event.get("modelId")
            message = event.get("message") or {}
            usage = message.get("usage") if message.get("role") == "assistant" else None
            if usage:
                tokens["input"] += usage.get("input", 0)
                tokens["output"] += usage.get("output", 0)
                tokens["cache_read"] += usage.get("cacheRead", 0)
                tokens["cache_write"] += usage.get("cacheWrite", 0)
    return model, tokens


def claude_usage(run: Run) -> tuple[str | None, Counter, int]:
    tokens: Counter = Counter()
    model = None
    write_1h = 0
    seen: set[str] = set()
    pattern = str(HOME / f".claude/projects/*{run.folder_marker}*/**/*.jsonl")
    for path in glob.glob(pattern, recursive=True):
        if not run.current(path):
            continue
        for event in json_lines(path):
            message = event.get("message")
            if not isinstance(message, dict) or not message.get("usage"):
                continue
            key = message.get("id") or event.get("requestId") or event.get("uuid")
            if key in seen:  # one API response is logged once per content block
                continue
            seen.add(key)
            usage = message["usage"]
            model = message.get("model") or model
            tokens["input"] += usage.get("input_tokens", 0)
            tokens["output"] += usage.get("output_tokens", 0)
            tokens["cache_read"] += usage.get("cache_read_input_tokens", 0)
            tokens["cache_write"] += usage.get("cache_creation_input_tokens", 0)
            write_1h += (usage.get("cache_creation") or {}).get("ephemeral_1h_input_tokens", 0)
    return model, tokens, write_1h


def codex_usage(run: Run) -> tuple[str | None, Counter]:
    """Codex logs running totals; take each session file's last total."""
    tokens: Counter = Counter()
    model = None
    for path in glob.glob(str(HOME / ".codex/sessions/*/*/*/rollout-*.jsonl")):
        if not run.current(path):
            continue
        with open(path) as handle:
            if run.path_marker not in handle.read(4000):
                continue
        last = None
        for event in json_lines(path):
            payload = event.get("payload") or {}
            if payload.get("type") == "token_count" and payload.get("info"):
                last = payload["info"]["total_token_usage"]
            if event.get("type") == "turn_context":
                model = payload.get("model") or model
        if last:
            cached = last.get("cached_input_tokens", 0)
            tokens["input"] += last.get("input_tokens", 0) - cached
            tokens["cache_read"] += cached
            tokens["output"] += last.get("output_tokens", 0)
    return model, tokens


def agy_usage(run: Run) -> tuple[str | None, Counter]:
    """agy logs each model step in its conversation's transcript."""
    tokens: Counter = Counter()
    model = None
    pattern = str(HOME / ".gemini/antigravity-cli/brain/*/.system_generated/logs/transcript.jsonl")
    for path in glob.glob(pattern):
        if not run.current(path):
            continue
        with open(path) as handle:
            lines = handle.readlines()
        if sum(run.path_marker in line for line in lines) < AGY_MIN_MENTIONS:
            continue
        for line in lines:
            step = json.loads(line)
            if step.get("type") != "PLANNER_RESPONSE":
                continue
            model = step.get("model") or model
            tokens["input"] += step.get("input_tokens") or 0
            tokens["cache_read"] += step.get("cache_read_tokens") or 0
            tokens["output"] += step.get("output_tokens") or 0
    return model, tokens


def usage(run: Run) -> tuple[str | None, Counter, int]:
    if run.variant.startswith("pi"):
        return (*pi_usage(run), 0)
    if run.variant.startswith("claude-"):
        return claude_usage(run)
    if run.variant.startswith("codex-"):
        return (*codex_usage(run), 0)
    if run.variant.startswith("agy"):
        return (*agy_usage(run), 0)
    raise SystemExit(f"no usage reader for variant {run.variant!r}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    trial_dir = Path(sys.argv[1]).resolve()
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with open(trial_dir / "results.tsv") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            rows[(row["variant"], row["ticket"])] = row  # a rerun's later line wins
    print(
        "variant\tticket\tstatus\tminutes\tmodel\tinput\tcache_read\tcache_write\toutput\tcost_usd"
    )
    for (variant, ticket), row in sorted(rows.items()):
        model, tokens, write_1h = usage(Run(trial_dir, variant, ticket))
        value = cost(model, tokens, write_1h)
        price = "n/a" if value is None else f"{value:.3f}"
        print(
            f"{variant}\t{ticket}\t{row['status']}\t{int(row['seconds']) / 60:.0f}\t{model}\t"
            f"{tokens['input']}\t{tokens['cache_read']}\t{tokens['cache_write']}\t"
            f"{tokens['output']}\t{price}"
        )


if __name__ == "__main__":
    main()
