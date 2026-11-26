"""Report a failed `make release`: print its log path and capture it in Sump.

Usage: python3 scripts/report_release_failure.py LOG

`scripts/release.sh` runs this when any step fails, so every failure, local or
in the publish workflow, is captured once and `chitty fetch-errors` (TASK-256)
can pick it up.
"""

import json
import subprocess
import sys
from pathlib import Path

SUMP_PROJECT = "chitty"
TAIL_LINES = 60


def last_release_line(lines: list[str]) -> str:
    """Return the script's own last `release:` message, or the last line."""
    for line in reversed(lines):
        if line.startswith("release:"):
            return line
    return lines[-1] if lines else "no output"


def main(log: Path) -> None:
    lines = log.read_text().splitlines()
    print(f"release: failed; full log: {log}", file=sys.stderr)
    subprocess.run(
        ["sump", "capture", SUMP_PROJECT]
        + ["--message", f"make release failed: {last_release_line(lines)}"]
        + ["--context-json", json.dumps({"log": str(log), "tail": lines[-TAIL_LINES:]})],
        check=True,
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
