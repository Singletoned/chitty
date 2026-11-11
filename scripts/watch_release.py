"""Wait for a release tag's publish workflow, then upgrade or report the failure.

Usage: python3 scripts/watch_release.py VERSION

`make release` runs this after pushing the tag. On success the global `chitty`
is upgraded to the release; on failure the failure is captured in Sump, so
`chitty fetch-errors` (TASK-256) can pick it up, and the script exits non-zero.
"""

import json
import subprocess
import sys
import time

WORKFLOW = "release.yml"
SUMP_PROJECT = "chitty"
FIND_ATTEMPTS = 30
FIND_DELAY_SECONDS = 2
UPGRADE_ATTEMPTS = 10
UPGRADE_DELAY_SECONDS = 15


def find_run(tag: str) -> dict[str, object]:
    """Return the workflow run for TAG, waiting for GitHub to create it."""
    for _ in range(FIND_ATTEMPTS):
        output = subprocess.run(
            ["gh", "run", "list", "--workflow", WORKFLOW, "--branch", tag]
            + ["--json", "databaseId,url", "--limit", "1"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        runs = json.loads(output)
        if runs:
            return runs[0]
        time.sleep(FIND_DELAY_SECONDS)
    raise SystemExit(f"release: no {WORKFLOW} run found for {tag}")


def upgrade(version: str) -> None:
    """Upgrade the global chitty until it reports VERSION; PyPI can lag."""
    for attempt in range(UPGRADE_ATTEMPTS):
        subprocess.run(["uv", "tool", "upgrade", "chitty"], check=True)
        installed = subprocess.run(
            ["uv", "tool", "list"], check=True, capture_output=True, text=True
        ).stdout
        if f"chitty v{version}\n" in installed:
            return
        if attempt + 1 < UPGRADE_ATTEMPTS:
            time.sleep(UPGRADE_DELAY_SECONDS)
    raise SystemExit(f"release: global chitty did not upgrade to {version}")


def report_failure(tag: str, url: object) -> None:
    subprocess.run(
        ["sump", "capture", SUMP_PROJECT]
        + ["--message", f"release {tag}: publish workflow failed"]
        + ["--context-json", json.dumps({"tag": tag, "run_url": url})],
        check=True,
    )
    raise SystemExit(f"release: publish workflow failed for {tag}: {url}")


def main(version: str) -> None:
    tag = f"v{version}"
    run = find_run(tag)
    watched = subprocess.run(
        ["gh", "run", "watch", str(run["databaseId"]), "--exit-status"], check=False
    )
    if watched.returncode != 0:
        report_failure(tag, run["url"])
    upgrade(version)


if __name__ == "__main__":
    main(sys.argv[1])
