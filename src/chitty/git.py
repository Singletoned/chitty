"""Optional autocommit: commit exactly the paths a write touched."""

import os
import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from chitty.errors import ChittyError
from chitty.ids import TaskId


@dataclass(frozen=True)
class BranchCommit:
    sha: str
    subject: str
    paths: tuple[PurePosixPath, ...]


@dataclass(frozen=True)
class SquashPlan:
    keep: tuple[str, ...]
    squashed: tuple[str, ...]


def squash_plan(
    commits: Sequence[BranchCommit], ticket_directories: Sequence[PurePosixPath]
) -> SquashPlan | None:
    """Plan a safe separation of bookkeeping from implementation commits."""
    keep: list[str] = []
    squashed: list[str] = []
    for commit in commits:
        if not commit.paths:
            return None
        inside = [any(path.is_relative_to(d) for d in ticket_directories) for path in commit.paths]
        if commit.subject.startswith("chitty: ") and all(inside):
            squashed.append(commit.sha)
        else:
            if any(inside):
                return None
            keep.append(commit.sha)
    return SquashPlan(tuple(keep), tuple(squashed)) if len(squashed) >= 2 else None


@dataclass(frozen=True)
class Commit:
    """A Git commit's object ID and full message."""

    sha: str
    message: str


def commits_missing_trailer(commits: Sequence[Commit], task_id: TaskId) -> list[Commit]:
    """Return non-Chitty commits without this task's trailer in their last paragraph."""
    missing: list[Commit] = []
    for commit in commits:
        lines = commit.message.splitlines()
        if lines and lines[0].startswith("chitty: "):
            continue
        text = commit.message.rstrip()
        paragraphs = text.splitlines()
        if not any(not line.strip() for line in paragraphs):
            missing.append(commit)
            continue
        last: list[str] = []
        for line in reversed(paragraphs):
            if not line.strip():
                break
            last.append(line)
        if not any(line.strip() == f"Task: {task_id}" for line in last):
            missing.append(commit)
    return missing


def with_task_trailer(message: str, task_id: TaskId) -> str:
    """Add this task's trailer, joining a final paragraph of trailers when possible."""
    if not message.strip():
        raise ValueError("commit message must not be empty")
    if not commits_missing_trailer([Commit("", message)], task_id):
        return message
    body = message.rstrip()
    lines = body.splitlines()
    last_paragraph = lines
    for index in range(len(lines) - 1, -1, -1):
        if not lines[index].strip():
            last_paragraph = lines[index + 1 :]
            break
    if last_paragraph is not lines and all(
        re.fullmatch(r"[A-Za-z0-9-]+: .+", line) for line in last_paragraph
    ):
        return f"{body}\nTask: {task_id}\n"
    return f"{body}\n\nTask: {task_id}\n"


def add_task_trailers(root: Path, main_branch: str, branch: str, task_id: TaskId) -> int:
    """Rewrite ticket commits with task trailers, preserving trees and authors."""
    if _git(root, "rev-list", "--merges", f"{main_branch}..HEAD").strip():
        raise ChittyError(f"cannot add task trailers to merge commits on {branch}")
    commits = branch_commits(root, main_branch)
    missing = {commit.sha for commit in commits if commits_missing_trailer([commit], task_id)}
    if not missing:
        return 0
    old_tip = _git(root, "rev-parse", "HEAD").strip()
    parent = _git(root, "rev-parse", main_branch).strip()
    for commit in commits:
        metadata = (
            _git(root, "show", "-s", "--format=%an%x00%ae%x00%ad", "--date=raw", commit.sha)
            .rstrip("\n")
            .split("\0")
        )
        environment = os.environ.copy()
        environment.update(
            GIT_AUTHOR_NAME=metadata[0],
            GIT_AUTHOR_EMAIL=metadata[1],
            GIT_AUTHOR_DATE=metadata[2],
        )
        message = with_task_trailer(commit.message, task_id)
        result = subprocess.run(
            [
                "git",
                "commit-tree",
                _git(root, "show", "-s", "--format=%T", commit.sha).strip(),
                "-p",
                parent,
                "-F",
                "-",
            ],
            input=message,
            text=True,
            capture_output=True,
            cwd=root,
            env=environment,
            check=False,
        )
        if result.returncode:
            raise ChittyError(f"`git commit-tree` failed in {root}:\n{result.stderr.strip()}")
        parent = result.stdout.strip()
    _git(root, "update-ref", f"refs/heads/{branch}", parent, old_tip)
    return len(missing)


def changed_files(root: Path, base: str, paths: Sequence[str]) -> list[str]:
    """Return exactly listed paths changed on the branch from ``base``."""
    if not paths:
        return []
    output = _git(
        root,
        "--literal-pathspecs",
        "diff",
        "-z",
        "--no-renames",
        "--name-only",
        f"{base}...HEAD",
        "--",
        *paths,
    )
    return [path for path in output.split("\0") if path and path in paths]


def short_sha(root: Path, sha: str) -> str:
    """Return Git's abbreviated object ID for ``sha``."""
    return _git(root, "rev-parse", "--short", sha).strip()


def changed_paths(root: Path, base: str, branch: str) -> list[PurePosixPath]:
    """Return committed paths changed from the merge base to ``branch``."""
    result = subprocess.run(
        ["git", "diff", "-z", "--no-renames", "--name-only", f"{base}...{branch}"],
        check=False,
        cwd=root,
        capture_output=True,
    )
    if result.returncode:
        command = f"git diff -z --no-renames --name-only {base}...{branch}"
        raise ChittyError(f"`{command}` failed in {root}:\n{result.stderr.decode().strip()}")
    return [PurePosixPath(path.decode()) for path in result.stdout.split(b"\0") if path]


def branch_commits(root: Path, main_branch: str) -> list[Commit]:
    """Return non-merge commits unique to HEAD, oldest first."""
    shas = _git(root, "rev-list", "--no-merges", "--reverse", f"{main_branch}..HEAD").splitlines()
    commits: list[Commit] = []
    for sha in shas:
        message = _git(root, "show", "-s", "--format=%B", sha)
        commits.append(Commit(sha, message))
    return commits


def commit(root: Path, paths: Sequence[Path], message: str) -> None:
    """Commit only `paths`, so nothing the user had staged is swept in.

    Deleted paths are included only if git tracks them.
    """
    relative = [str(path.relative_to(root)) for path in paths]
    present = [p for p in relative if (root / p).exists()]
    tracked = set(_git(root, "ls-files", "--", *relative).splitlines())
    staged = _git(root, "diff", "--cached", "--binary", "--", *relative)
    # A path-limited commit needs both sides of a staged rename. Disable rename
    # detection so Git reports its deletion and addition separately.
    staged_paths = set(
        _git(root, "diff", "--cached", "--no-renames", "--name-only", "--", *relative).splitlines()
    )
    included = [p for p in relative if p in present or p in tracked or p in staged_paths]
    # Init can intentionally manage an ignored CLAUDE.md; limit force-add to
    # these explicit paths so other ignored files remain untouched.
    _git(root, "add", "--force", "--", *present)
    try:
        _git(root, "commit", "--quiet", "--only", "-m", message, "--", *included)
    except ChittyError as error:
        _git(root, "reset", "--", *relative)
        if staged:
            _apply_cached(root, staged)
        raise ChittyError(f"autocommit failed: {error}") from error


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


def branch_tips(root: Path) -> dict[str, str]:
    """Return commit IDs for local and remote-tracking refs, excluding symrefs."""
    output = _git(
        root,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)%09%(symref)",
        "refs/heads",
        "refs/remotes",
    )
    return {
        ref: commit
        for line in output.splitlines()
        for ref, commit, symref in [line.split("\t")]
        if not symref
    }


def merge_base(root: Path, first: str, second: str) -> str:
    """Return the merge base of two commits."""
    return _git(root, "merge-base", first, second).strip()


def common_ancestor(root: Path, first: str, second: str) -> str | None:
    """Return the merge base, or None for unrelated histories."""
    args = ("merge-base", first, second)
    result = subprocess.run(["git", *args], check=False, cwd=root, capture_output=True, text=True)
    if result.returncode == 1:
        return None
    if result.returncode:
        raise ChittyError(f"`git {' '.join(args)}` failed in {root}:\n{result.stderr.strip()}")
    return result.stdout.strip()


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    """Whether ancestor is reachable from descendant."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        cwd=root,
        capture_output=True,
    )
    if result.returncode in (0, 1):
        return result.returncode == 0
    command = f"git merge-base --is-ancestor {ancestor} {descendant}"
    raise ChittyError(f"`{command}` failed in {root}:\n{result.stderr.decode().strip()}")


def ref_commit(root: Path, ref: str) -> str | None:
    """Resolve a ref or commit-ish to a commit ID; return None if absent/unborn."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    if result.returncode == 1:
        return None
    raise ChittyError(
        f"`git rev-parse --verify --quiet {ref}^{{commit}}` failed in {root}:\n"
        f"{result.stderr.strip()}"
    )


def files_at(root: Path, ref: str, directories: Sequence[Path]) -> list[tuple[Path, str]]:
    """Read all blobs below directories at a ref tip."""
    objects: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for directory in directories:
        output = _git(root, "ls-tree", "-r", "-z", "--full-tree", ref, "--", str(directory))
        for entry in output.split("\0"):
            if not entry:
                continue
            metadata, filename = entry.split("\t", 1)
            _mode, kind, object_id = metadata.split()
            if kind != "blob":
                continue
            path = Path(filename)
            if path not in seen:
                seen.add(path)
                objects.append((object_id, path))
    contents = _read_blobs(root, objects)
    files: list[tuple[Path, str]] = []
    for object_id, path in objects:
        result = contents.get((object_id, path))
        if result is None:
            raise ChittyError(f"selected Git blob is missing: {path}")
        files.append((path, result[1]))
    return files


def changed_since_split(root: Path, ref: str, against: str, paths: Sequence[Path]) -> bool:
    """Whether ref changed any selected path since diverging from against."""
    result = subprocess.run(
        ["git", "merge-base", ref, against], check=False, cwd=root, capture_output=True, text=True
    )
    if result.returncode == 1:
        raise ChittyError(f"refs {ref} and {against} have unrelated histories")
    if result.returncode != 0:
        raise ChittyError(
            f"`git merge-base {ref} {against}` failed in {root}:\n{result.stderr.strip()}"
        )
    if not paths:
        return False
    diff = subprocess.run(
        [
            "git",
            "--literal-pathspecs",
            "diff",
            "--quiet",
            result.stdout.strip(),
            ref,
            "--",
            *map(str, paths),
        ],
        check=False,
        cwd=root,
        capture_output=True,
    )
    if diff.returncode in (0, 1):
        return diff.returncode == 1
    raise ChittyError(
        f"`git diff --quiet --literal-pathspecs {result.stdout.strip()} {ref} -- ...` "
        f"failed in {root}:\n{diff.stderr.decode().strip()}"
    )


def main_files(
    root: Path, branch: str, directories: Sequence[Path]
) -> list[tuple[Path, str]] | None:
    """Read files below ``directories`` from the local integration branch.

    ``None`` means that the repository is outside Git or has no local branch,
    allowing callers to retain their non-Git behavior.
    """
    if not is_repository(root) or not has_local_branch(root, branch):
        return None
    entries: list[tuple[Path, str]] = []
    objects: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for directory in directories:
        output = _git(
            root, "ls-tree", "-r", "--full-tree", f"refs/heads/{branch}", "--", str(directory)
        )
        for line in output.splitlines():
            metadata, _, filename = line.partition("\t")
            parts = metadata.split()
            if len(parts) != 3 or parts[1] != "blob":
                continue
            path = Path(filename)
            if path in seen:
                continue
            seen.add(path)
            objects.append((f"refs/heads/{branch}:{path}", path))
    contents = _read_blobs(root, objects)
    for object_id, path in objects:
        result = contents.get((object_id, path))
        if result is not None:
            entries.append((path, result[1]))
    return entries


def repository_answer(
    command: Sequence[str], directory: Path, returncode: int, stdout: str, stderr: str
) -> bool:
    if returncode == 0:
        return stdout.strip() == "true"
    if returncode == 128 and "not a git repository" in stderr:
        return False
    shown = " ".join(command)
    raise ChittyError(f"`{shown}` failed in {directory}:\n{stderr.strip()}")


def is_repository(directory: Path) -> bool:
    """Whether ``directory`` is inside a Git worktree."""
    directory = directory.resolve()
    if not directory.is_dir():
        raise ChittyError(f"Not a directory: {directory}")
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=False,
            cwd=directory,
            env={**os.environ, "LC_ALL": "C"},
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        for parent in (directory, *directory.parents):
            marker = parent / ".git"
            if os.path.lexists(marker):
                raise ChittyError(
                    f"`git` is unavailable on PATH, but repository marker exists: {marker}"
                ) from error
        return False
    return repository_answer(
        ["git", "rev-parse", "--is-inside-work-tree"],
        directory,
        result.returncode,
        result.stdout,
        result.stderr,
    )


def is_linked_worktree(directory: Path) -> bool:
    """Whether ``directory`` is in a linked worktree rather than its main checkout.

    Non-Git directories, including machines without Git, are deliberately not
    linked worktrees.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir", "--git-common-dir"],
            check=False,
            cwd=directory,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    paths = result.stdout.splitlines()
    if result.returncode != 0 or len(paths) != 2:
        return False
    git_directory, common_directory = paths
    return (directory / git_directory).resolve() != (directory / common_directory).resolve()


def main_checkout(root: Path) -> Path:
    """Find the primary checkout by comparing each worktree's Git directory."""
    common_dir = _git_path(root, "--git-common-dir")
    output = _git(root, "worktree", "list", "--porcelain")
    worktrees = [
        Path(line.removeprefix("worktree "))
        for line in output.splitlines()
        if line.startswith("worktree ")
    ]
    for worktree in worktrees:
        if _git_path(worktree, "--git-dir") == common_dir:
            return worktree.resolve()
    raise ChittyError(f"cannot find the main checkout for {root}")


def current_branch(root: Path) -> str | None:
    """Return the checked-out branch, or ``None`` outside Git or when detached."""
    if not is_repository(root):
        return None
    branch = _git(root, "branch", "--show-current").strip()
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


def prune_worktrees(root: Path) -> None:
    """Forget linked worktrees whose directories were removed outside Git."""
    _git(root, "worktree", "prune")


def local_branches(root: Path) -> list[str]:
    """Return local branch names, excluding remote refs."""
    output = _git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return output.splitlines()


def has_local_branch(root: Path, branch: str) -> bool:
    """Report whether ``branch`` names a local branch."""
    try:
        branches = _git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    except ChittyError:
        return False
    return branch in branches.splitlines()


def has_branch_ref(root: Path, branch: str) -> bool:
    """Whether a local or remote branch ref exists; Git errors are surfaced."""
    refs = _git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes")
    for ref in refs.splitlines():
        if ref == f"refs/heads/{branch}":
            return True
        if ref.startswith("refs/remotes/"):
            _, _, remote_branch = ref.removeprefix("refs/remotes/").partition("/")
            if remote_branch == branch:
                return True
    return False


def dirty_paths(root: Path, directory: Path) -> set[Path]:
    """Return changed or untracked paths below ``directory`` in this worktree."""
    if not is_repository(root):
        return set()
    lines = _git(
        root, "status", "--porcelain", "--untracked-files=all", "--", str(directory)
    ).splitlines()
    return {Path(line[3:]) for line in lines if len(line) > 3}


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
    input_data = "".join(f"{object_id}\n" for object_id, _ in objects).encode()
    stdout, stderr = process.communicate(input_data)
    result: dict[tuple[str, Path], tuple[str, str]] = {}
    position = 0
    for object_id, path in objects:
        end = stdout.find(b"\n", position)
        header = stdout[position:end].decode() if end >= 0 else stdout[position:].decode()
        position = end + 1 if end >= 0 else len(stdout)
        parts = header.split()
        if len(parts) == 2 and parts[1] == "missing":
            continue
        if len(parts) != 3:
            raise ChittyError(f"cannot read Git object {object_id}: {header}")
        returned, kind, size = parts
        if kind != "blob":
            raise ChittyError(f"Git object {object_id} is not a blob")
        content_end = position + int(size)
        content = stdout[position:content_end]
        position = content_end + 1
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ChittyError(f"Git file is not UTF-8: {path}") from error
        result[(object_id, path)] = (returned, decoded)
    if process.returncode != 0:
        raise ChittyError(f"cannot read historical task files: {stderr.decode().strip()}")
    return result


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


def _git_path(root: Path, argument: str) -> Path:
    value = _git(root, "rev-parse", argument).strip()
    path = Path(value)
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def file_at_merge_base(root: Path, first_ref: str, second_ref: str, path: Path | str) -> str | None:
    """Read a file at the merge-base of two refs, or report when none exists."""
    result = subprocess.run(
        ["git", "merge-base", first_ref, second_ref],
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        raise ChittyError(f"refs `{first_ref}` and `{second_ref}` have no merge-base")
    if result.returncode:
        raise ChittyError(
            f"cannot find merge-base of `{first_ref}` and `{second_ref}` in {root}: "
            f"{result.stderr.strip()}"
        )
    return file_at(root, result.stdout.strip(), path)


def file_at(root: Path, ref: str, path: Path | str) -> str | None:
    """Read a file at a Git ref, returning ``None`` when it is absent."""
    relative = str(path)
    _git(root, "rev-parse", "--verify", ref)
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{ref}:{relative}"],
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if exists.returncode:
        return None
    return _git(root, "show", f"{ref}:{relative}")


def _git(root: Path, *args: str) -> str:
    command = ["git", *args]
    result = subprocess.run(command, check=False, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        shown = " ".join(command)
        raise ChittyError(f"`{shown}` failed in {root}:\n{result.stderr.strip()}")
    return result.stdout


def rebase_in_progress(root: Path) -> bool:
    """Whether this worktree has a rebase stopped part-way."""
    return any(
        (root / _git(root, "rev-parse", "--git-path", name).strip()).exists()
        for name in ("rebase-merge", "rebase-apply")
    )


def merge_in_progress(root: Path) -> bool:
    """Whether this worktree has an unfinished merge."""
    path = root / _git(root, "rev-parse", "--git-path", "MERGE_HEAD").strip()
    return path.exists()


def uncommitted_paths(root: Path) -> list[str]:
    """Changed, staged or untracked (but not ignored) paths in this worktree."""
    lines = _git(root, "status", "--porcelain", "--untracked-files=all", "--no-renames")
    return sorted(line[3:] for line in lines.splitlines() if len(line) > 3)


def rebase_onto(root: Path, main_branch: str) -> list[str]:
    """Rebase this worktree onto ``main_branch``; return unresolved paths."""
    completed = subprocess.run(
        ["git", "-c", "rerere.enabled=false", "rebase", main_branch],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return []
    output = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    if rebase_in_progress(root):
        conflict_output = _git(root, "diff", "--name-only", "--diff-filter=U", "-z")
        conflicts = conflict_output.rstrip("\0").split("\0") if conflict_output else []
        if conflicts:
            return conflicts
        abort_rebase(root)
        raise ChittyError(f"`git rebase {main_branch}` stopped in {root}:\n{output}")
    raise ChittyError(f"`git rebase {main_branch}` failed in {root}:\n{output}")


def abort_rebase(root: Path) -> None:
    _git(root, "rebase", "--abort")


def fast_forward(root: Path, branch: str) -> None:
    """Fast-forward the current branch to ``branch``."""
    _git(root, "merge", "--ff-only", branch)


def remove_worktree(root: Path, worktree: Path) -> None:
    """Remove a clean linked worktree without forcing Git to discard files."""
    _git(root, "worktree", "remove", str(worktree))


def delete_branch(root: Path, branch: str) -> None:
    """Delete a fully merged local branch without forcing deletion."""
    _git(root, "branch", "-d", branch)


def _check_saved_work_ref(ref: str) -> None:
    prefix = "refs/chitty/stash/"
    if not ref.startswith(prefix) or not ref[len(prefix) :]:
        raise ChittyError(f"saved work must use a ref under refs/chitty/stash/: {ref}")


def save_work(root: Path, ref: str, message: str) -> bool:
    _check_saved_work_ref(ref)
    if not _git(root, "status", "--porcelain", "--untracked-files=all").strip():
        return False
    exists = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if exists.returncode == 0:
        raise ChittyError(
            f"{ref} already exists; apply it with git stash apply {ref} "
            f"and delete it with git update-ref -d {ref}"
        )
    if exists.returncode != 1:
        exists.check_returncode()
    _git(root, "add", "-A")
    commit = _git(root, "stash", "create", message).strip()
    if not commit:
        raise ChittyError(f"git stash create produced no commit in {root}")
    _git(root, "update-ref", ref, commit)
    _git(root, "reset", "--hard")
    _git(root, "clean", "-fd")
    return True


def restore_work(root: Path, ref: str) -> bool:
    """Restore saved work into a clean worktree, retaining the ref on failure."""
    _check_saved_work_ref(ref)
    exists = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if exists.returncode:
        raise ChittyError(f"{ref} does not exist")
    if _git(root, "status", "--porcelain", "--untracked-files=all").strip():
        raise ChittyError(f"cannot restore {ref}: the worktree has uncommitted changes")
    result = subprocess.run(
        ["git", "-c", "rerere.enabled=false", "stash", "apply", ref],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        _git(root, "reset", "--hard")
        _git(root, "clean", "-fd")
        return False
    _git(root, "update-ref", "-d", ref)
    return True
