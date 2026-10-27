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
    staged = _git(root, "diff", "--cached", "--binary", "--", *relative)
    _git(root, "add", "--", *present)
    try:
        _git(root, "commit", "--quiet", "--only", "-m", message, "--", *included)
    except ChittyError:
        _git(root, "reset", "--", *relative)
        if staged:
            _apply_cached(root, staged)
        raise


def deleted_paths(root: Path) -> list[Path]:
    """Return task paths deleted in reachable history or the worktree.

    Delete-mode ID allocation must not guess from an incomplete history.
    """
    try:
        shallow = _git(root, "rev-parse", "--is-shallow-repository").strip()
        if shallow != "false":
            raise ChittyError(f"git history is shallow in {root}; cannot allocate delete-mode IDs")
        historical = _git(
            root, "log", "--all", "--no-renames", "--diff-filter=D", "--name-only", "--format="
        ).splitlines()
        status = _git(root, "status", "--porcelain", "--no-renames").splitlines()
    except ChittyError as error:
        raise ChittyError(
            f"git history is unavailable for delete-mode ID allocation: {error}"
        ) from error
    pending = [line[3:] for line in status if len(line) > 3 and "D" in line[:2]]
    return [Path(path) for path in [*historical, *pending] if path]


def _apply_cached(root: Path, patch: str) -> None:
    result = subprocess.run(
        ["git", "apply", "--cached", "--whitespace=nowarn"],
        check=False,
        cwd=root,
        input=patch,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ChittyError(f"autocommit failed restoring the Git index:\n{result.stderr.strip()}")


def _git(root: Path, *args: str) -> str:
    command = ["git", *args]
    result = subprocess.run(command, check=False, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        shown = " ".join(command)
        raise ChittyError(f"autocommit failed: `{shown}` in {root}:\n{result.stderr.strip()}")
    return result.stdout
