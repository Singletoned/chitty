"""Optional autocommit: commit exactly the paths a write touched."""

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from chitty.errors import ChittyError


@dataclass(frozen=True)
class HistoricalFile:
    """A file from the newest committed version visible on a Git ref."""

    path: Path
    content: str
    ref: str
    committed_at: int


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


def move(root: Path, old: Path, new: Path) -> None:
    """Rename a tracked path through Git, preserving its staged rename."""
    relative = str(old.relative_to(root))
    try:
        _git(root, "ls-files", "--error-unmatch", "--", relative)
    except ChittyError:
        old.rename(new)
    else:
        _git(root, "mv", "--", relative, str(new.relative_to(root)))


def require_clean(root: Path) -> None:
    """Refuse to continue unless the worktree has no changes or untracked files."""
    try:
        status = _git(root, "status", "--porcelain", "--no-renames")
    except ChittyError as error:
        raise ChittyError(f"cannot confirm a clean Git working tree: {error}") from error
    if status:
        raise ChittyError(
            f"working tree is dirty in {root}; commit or stash these first:\n{status.rstrip()}"
        )


def remove_sources(root: Path, paths: Sequence[Path]) -> dict[Path, tuple[bytes, str]]:
    """Remove sources, retaining enough state to restore them after a failed import."""
    originals = {path: (path.read_bytes(), "") for path in paths}
    relative = [str(path.relative_to(root)) for path in paths]
    patches = _git(root, "diff", "--cached", "--binary", "--", *relative)
    for path in paths:
        originals[path] = (originals[path][0], patches)
    _git(root, "rm", "--quiet", "--", *relative)
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


def historical_files(root: Path, directory: Path) -> list[HistoricalFile]:
    """Read the latest committed version of every file below ``directory``.

    Refs are enumerated once, tree entries are read once per ref, and every
    selected blob is fetched through one ``git cat-file --batch`` process.
    The caller overlays uncommitted worktree files separately.
    """
    try:
        refs = [
            line.partition("\t")[0]
            for line in _git(
                root,
                "for-each-ref",
                "--format=%(refname)%09%(symref)",
                "refs/heads",
                "refs/remotes",
            ).splitlines()
            if not line.partition("\t")[2]
        ]
        if not refs:
            return []
        changed = _latest_changes(root, refs, directory)
        blobs = _tree_blobs(root, refs, directory)
    except ChittyError:
        return []

    selected = [(path, commit, committed_at) for path, (commit, committed_at) in changed.items()]
    contents = _read_blobs(root, [(f"{commit}:{path}", path) for path, commit, _ in selected])
    files: list[HistoricalFile] = []
    for path, commit, committed_at in selected:
        result = contents.get((f"{commit}:{path}", path))
        if result is None:
            continue
        blob, content = result
        candidates = blobs.get(path, ())
        matching = [ref for ref, object_id in candidates if object_id == blob]
        if matching:
            files.append(HistoricalFile(path, content, _display_ref(matching[0]), committed_at))
    return files


def current_branch(root: Path) -> str | None:
    """Return the checked-out branch, or ``None`` outside Git or when detached."""
    try:
        branch = _git(root, "branch", "--show-current").strip()
    except ChittyError:
        return None
    return branch or None


def worktree_for_branch(root: Path, branch: str) -> Path | None:
    """Return the worktree that has a local branch checked out, if any."""
    try:
        lines = _git(root, "worktree", "list", "--porcelain").splitlines()
    except ChittyError:
        return None
    worktree: Path | None = None
    for line in lines:
        if line.startswith("worktree "):
            worktree = Path(line.removeprefix("worktree "))
        elif line == f"branch refs/heads/{branch}":
            return worktree
    return None


def has_local_branch(root: Path, branch: str) -> bool:
    """Report whether ``branch`` names a local branch."""
    try:
        branches = _git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    except ChittyError:
        return False
    return branch in branches.splitlines()


def dirty_paths(root: Path, directory: Path) -> set[Path]:
    """Return changed or untracked paths below ``directory`` in this worktree."""
    try:
        lines = _git(
            root, "status", "--porcelain", "--untracked-files=all", "--", str(directory)
        ).splitlines()
    except ChittyError:
        return set()
    return {Path(line[3:]) for line in lines if len(line) > 3}


def _latest_changes(
    root: Path, refs: Sequence[str], directory: Path
) -> dict[Path, tuple[str, int]]:
    output = _git(
        root,
        "log",
        "--no-renames",
        "--format=%H%x09%ct",
        "--name-only",
        *refs,
        "--",
        str(directory),
    )
    result: dict[Path, tuple[str, int]] = {}
    commit = ""
    timestamp = 0
    for line in output.splitlines():
        if "\t" in line:
            commit, _, value = line.partition("\t")
            timestamp = int(value)
        elif line:
            path = Path(line)
            previous = result.get(path)
            if previous is None or timestamp > previous[1]:
                result[path] = (commit, timestamp)
    return result


def _tree_blobs(
    root: Path, refs: Sequence[str], directory: Path
) -> dict[Path, list[tuple[str, str]]]:
    result: dict[Path, list[tuple[str, str]]] = {}
    for ref in refs:
        output = _git(root, "ls-tree", "-r", "--full-tree", ref, "--", str(directory))
        for line in output.splitlines():
            metadata, _, filename = line.partition("\t")
            _, kind, object_id = metadata.split()
            if kind == "blob":
                result.setdefault(Path(filename), []).append((ref, object_id))
    return result


def _read_blobs(
    root: Path, objects: Sequence[tuple[str, Path]]
) -> dict[tuple[str, Path], tuple[str, str]]:
    if not objects:
        return {}
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    process.stdin.write("".join(f"{object_id}\n" for object_id, _ in objects).encode())
    process.stdin.close()
    result: dict[tuple[str, Path], tuple[str, str]] = {}
    for object_id, path in objects:
        header = process.stdout.readline().decode().rstrip("\n")
        parts = header.split()
        if len(parts) == 2 and parts[1] == "missing":
            continue
        if len(parts) != 3:
            raise ChittyError(f"cannot read Git object {object_id}: {header}")
        returned, kind, size = parts
        if kind != "blob":
            raise ChittyError(f"Git object {object_id} is not a blob")
        content = process.stdout.read(int(size))
        process.stdout.read(1)
        result[(object_id, path)] = (returned, content.decode())
    stderr = process.stderr.read().decode() if process.stderr is not None else ""
    returncode = process.wait()
    process.stdout.close()
    if process.stderr is not None:
        process.stderr.close()
    if returncode != 0:
        raise ChittyError(f"cannot read historical task files: {stderr.strip()}")
    return result


def _display_ref(ref: str) -> str:
    for prefix in ("refs/heads/", "refs/remotes/"):
        if ref.startswith(prefix):
            return ref.removeprefix(prefix)
    return ref


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
