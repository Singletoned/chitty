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
    staged = _git(root, "diff", "--cached", "--binary", "--", *relative)
    staged_paths = set(_git(root, "diff", "--cached", "--name-only", "--", *relative).splitlines())
    included = [p for p in relative if p in present or p in tracked or p in staged_paths]
    _git(root, "add", "--", *present)
    try:
        _git(root, "commit", "--quiet", "--only", "-m", message, "--", *included)
    except ChittyError:
        _git(root, "reset", "--", *relative)
        if staged:
            _apply_cached(root, staged)
        raise


def source_problems(root: Path, paths: Sequence[Path]) -> list[Path]:
    """Return source paths that are untracked or differ from HEAD/index."""
    relative = [str(path.relative_to(root)) for path in paths]
    try:
        tracked = set(_git(root, "ls-files", "--", *relative).splitlines())
        status = _git(root, "status", "--porcelain", "--no-renames", "--", *relative)
    except ChittyError:
        return list(paths)
    changed = {line[3:] for line in status.splitlines() if len(line) > 3}
    return [
        path
        for path, name in zip(paths, relative, strict=True)
        if name not in tracked or name in changed
    ]


def remove_sources(root: Path, paths: Sequence[Path], force: bool) -> dict[Path, tuple[bytes, str]]:
    """Remove sources, retaining enough state to restore them after a failed import."""
    originals = {path: (path.read_bytes(), "") for path in paths}
    relative = [str(path.relative_to(root)) for path in paths]
    try:
        patches = _git(root, "diff", "--cached", "--binary", "--", *relative)
        for path in paths:
            originals[path] = (originals[path][0], patches)
        arguments = ("rm", "-f", "--", *relative) if force else ("rm", "--", *relative)
        _git(root, *arguments)
    except ChittyError:
        for path in paths:
            path.unlink(missing_ok=True)
        if force:
            for path in originals:
                path.unlink(missing_ok=True)
        else:
            raise
    return originals


def restore_sources(root: Path, originals: dict[Path, tuple[bytes, str]]) -> None:
    """Restore files and their pre-import index state after a failed import."""
    paths = list(originals)
    for path, (content, _) in originals.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    relative = [str(path.relative_to(root)) for path in paths]
    try:
        _git(root, "reset", "--", *relative)
        patch = next((patch for _, patch in originals.values() if patch), "")
        if patch:
            _apply_cached(root, patch)
    except ChittyError:
        pass


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
