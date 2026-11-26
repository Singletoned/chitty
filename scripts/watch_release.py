"""Wait for a release tag's publish workflow, then upgrade or report the failure.

Usage: python3 scripts/watch_release.py VERSION

`make release` runs this after pushing the tag. On success the global `chitty`
is upgraded to the release; on failure the script exits non-zero and
`scripts/release.sh` reports it (`scripts/report_release_failure.py`).
"""

import json
import subprocess
import sys
import time

WORKFLOW = "release.yml"
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
    """Install VERSION as the global chitty until it reports it; PyPI can lag.

    `uv tool upgrade` does nothing for a tool installed with an exact pin, so
    install the released version directly. Until PyPI serves it, the install
    fails (uv prints why) and is retried.
    """
    for attempt in range(UPGRADE_ATTEMPTS):
        subprocess.run(["uv", "tool", "install", f"chitty=={version}"], check=False)
        installed = subprocess.run(
            ["uv", "tool", "list"], check=True, capture_output=True, text=True
        ).stdout
        if f"chitty v{version}\n" in installed:
            return
        if attempt + 1 < UPGRADE_ATTEMPTS:
            time.sleep(UPGRADE_DELAY_SECONDS)
    raise SystemExit(f"release: global chitty is not {version} after installing it")


def report_failure(tag: str, url: object) -> None:
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
