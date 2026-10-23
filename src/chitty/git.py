"""Optional autocommit: commit exactly the paths a write touched."""

import subprocess
from collections.abc import Sequence
from pathlib import Path

from chitty.errors import ChittyError


def commit(root: Path, paths: Sequence[Path], message: str) -> None:
    """Commit only `paths`, so nothing the user had staged is swept in.

    Deleted paths are included only if git tracks them.
    """
    relative = [str(path.relative_to(root)) for path in paths]
    present = [p for p in relative if (root / p).exists()]
    tracked = set(_git(root, "ls-files", "--", *relative).splitlines())
    included = [p for p in relative if p in present or p in tracked]
    _git(root, "add", "--", *present)
    _git(root, "commit", "--quiet", "--only", "-m", message, "--", *included)


def _git(root: Path, *args: str) -> str:
    command = ["git", *args]
    result = subprocess.run(command, check=False, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        shown = " ".join(command)
        raise ChittyError(f"autocommit failed: `{shown}` in {root}:\n{result.stderr.strip()}")
    return result.stdout
