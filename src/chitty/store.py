"""Contexts on disk: find, list, read, write, move, archive."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from chitty import git, ids
from chitty.config import (
    BACKLOG_DIR,
    CONFIG_NAME,
    INITIAL_CONFIG,
    RepoConfig,
    load_repo_config,
    load_user_contexts,
    user_contexts_path,
    validate_repo_config,
)
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.model import (
    DESCRIPTION,
    PLAN,
    FieldValue,
    Task,
    TaskError,
    new_task,
    parse,
)

ARCHIVE_DIR = "archive"
AGENTS_FILE = "AGENTS.md"
GUIDE_HEADING = "## Chitty"

Which = Literal["active", "archived", "all"]


@dataclass(frozen=True)
class Context:
    name: str
    prefix: str
    directory: Path

    @property
    def archive_directory(self) -> Path:
        return self.directory / ARCHIVE_DIR


@dataclass(frozen=True)
class StoredTask:
    id: TaskId
    context: str
    path: Path
    archived: bool
    task: Task

    @property
    def slug(self) -> str:
        return ids.parse_filename(self.path.name)[1]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "context": self.context,
            "archived": self.archived,
            "path": str(self.path),
            **self.task.as_dict(),
        }


@dataclass(frozen=True)
class Change:
    """The result of a write: the task as it now is, and every path touched."""

    task: StoredTask
    paths: tuple[Path, ...]


@dataclass(frozen=True)
class Edit:
    """A set of changes to one task. None and () mean "leave alone"."""

    title: str | None = None
    status: str | None = None
    add_labels: Sequence[str] = ()
    rm_labels: Sequence[str] = ()
    priority: str | None = None  # "" removes
    owner: str | None = None  # "" removes
    depends_on: Sequence[str] = ()
    rm_depends_on: Sequence[str] = ()
    description: str | None = None
    add_criteria: Sequence[str] = ()
    rm_criteria: Sequence[int] = ()
    check: Sequence[int] = ()
    uncheck: Sequence[int] = ()
    plan: str | None = None  # "" removes
    note: str | None = None

    def is_empty(self) -> bool:
        return all(
            value is None or (not isinstance(value, str) and len(value) == 0)
            for value in vars(self).values()
        )

    def apply(self, task: Task) -> Task:
        fm = task.frontmatter
        if self.title is not None:
            task = task.with_field("title", self.title)
        if self.status is not None:
            task = task.with_field("status", self.status)
        if self.add_labels or self.rm_labels:
            labels = _update_list(fm.labels, self.add_labels, self.rm_labels, "label")
            task = task.with_field("labels", labels)
        if self.priority is not None:
            task = task.with_field("priority", self.priority or None)
        if self.owner is not None:
            task = task.with_field("owner", self.owner or None)
        if self.depends_on or self.rm_depends_on:
            references = _update_list(
                fm.depends_on, self.depends_on, self.rm_depends_on, "dependency"
            )
            task = task.with_field("depends_on", references)
        if self.description is not None:
            task = task.with_section(DESCRIPTION, self.description)
        task = task.with_criteria(
            add=self.add_criteria, remove=self.rm_criteria, check=self.check, uncheck=self.uncheck
        )
        if self.plan is not None:
            task = task.with_section(PLAN, self.plan)
        if self.note is not None:
            task = task.with_note(self.note)
        return task


@dataclass(frozen=True)
class Target:
    """Where `add` writes. A foreign target is a user-level context in another repo."""

    repo: "Repo"
    context: Context
    foreign: bool


class Repo:
    def __init__(self, root: Path, config: RepoConfig) -> None:
        self.root = root
        self.config = config

    @classmethod
    def open(cls, root: Path) -> "Repo":
        return cls(root, load_repo_config(root))

    def commit(self, change: Change, verb: str) -> None:
        """Commit the change if autocommit is on and anything was written."""
        if self.config.autocommit and change.paths:
            title = change.task.task.frontmatter.title
            git.commit(self.root, change.paths, f"chitty: {verb} {change.task.id} {title}")

    # -- contexts --------------------------------------------------------

    def contexts(self) -> list[Context]:
        return [self.context(name) for name in self.config.contexts]

    def context(self, name: str) -> Context:
        config = self.config.contexts.get(name)
        if config is None:
            known = ", ".join(self.config.contexts)
            raise ChittyError(f"no context {name!r} in {self.root} (known: {known})")
        return Context(name, config.prefix, self.root / BACKLOG_DIR / name)

    @property
    def default_context(self) -> Context:
        return self.context(self.config.default_context)

    def context_of(self, task_id: TaskId) -> Context:
        for context in self.contexts():
            if context.prefix == task_id.prefix:
                return context
        raise ChittyError(f"{task_id}: no context in {self.root} has prefix {task_id.prefix!r}")

    def resolve(self, text: str) -> TaskId:
        """`TASK-13`, or bare `13` for the default context."""
        return ids.resolve(text, self.default_context.prefix)

    # -- reading ---------------------------------------------------------

    def tasks(self, context: Context, which: Which) -> list[StoredTask]:
        found: list[StoredTask] = []
        if which in ("active", "all"):
            found += [self._load(context, p, False) for p in self._files(context, False)]
        if which in ("archived", "all"):
            found += [self._load(context, p, True) for p in self._files(context, True)]
        return sorted(found, key=lambda t: t.id)

    def all_tasks(self) -> list[StoredTask]:
        return [t for context in self.contexts() for t in self.tasks(context, "all")]

    def find(self, task_id: TaskId) -> StoredTask:
        context = self.context_of(task_id)
        matches = [
            (path, archived)
            for archived in (False, True)
            for path in self._files(context, archived)
            if ids.parse_filename(path.name)[0] == task_id
        ]
        if not matches:
            raise ChittyError(f"no task {task_id} in {context.directory}")
        if len(matches) > 1:
            paths = ", ".join(str(p) for p, _ in matches)
            raise ChittyError(f"{task_id} is used by more than one file: {paths}")
        path, archived = matches[0]
        return self._load(context, path, archived)

    def check_dependencies(self, references: Sequence[str]) -> None:
        for reference in references:
            self.find(TaskId.parse(reference))

    # -- writing ---------------------------------------------------------

    def add(
        self,
        context: Context,
        title: str,
        description: str,
        criteria: Sequence[str],
        fields: Mapping[str, FieldValue],
        today: date,
    ) -> Change:
        depends_on = fields.get("depends_on")
        if isinstance(depends_on, list):
            self.check_dependencies(depends_on)
        task = new_task(title, today, description, criteria, fields)
        task_id = TaskId(context.prefix, self.next_number(context))
        path = context.directory / ids.filename(task_id, ids.slugify(title))
        self._write(path, task.render())
        return Change(StoredTask(task_id, context.name, path, False, task), (path,))

    def save(self, stored: StoredTask, task: Task) -> Change:
        """Write an edited task; touches nothing if the content is unchanged."""
        if task.frontmatter.depends_on != stored.task.frontmatter.depends_on:
            self.check_dependencies(task.frontmatter.depends_on)
        updated = StoredTask(stored.id, stored.context, stored.path, stored.archived, task)
        if task.render() == stored.task.render():
            return Change(updated, ())
        self._write(stored.path, task.render())
        return Change(updated, (stored.path,))

    def next_number(self, context: Context) -> int:
        numbers = [
            ids.parse_filename(p.name)[0].number
            for archived in (False, True)
            for p in self._files(context, archived)
        ]
        return ids.next_number(numbers)

    def archive(self, task_id: TaskId) -> Change:
        return self._set_archived(task_id, True)

    def restore(self, task_id: TaskId) -> Change:
        return self._set_archived(task_id, False)

    def move(self, task_id: TaskId, target: Context) -> Change:
        """Give a task the next ID in another context and rewrite references to it."""
        stored = self.find(task_id)
        if target.name == stored.context:
            raise ChittyError(f"{task_id} is already in context {target.name!r}")
        new_id = TaskId(target.prefix, self.next_number(target))
        directory = target.archive_directory if stored.archived else target.directory
        new_path = directory / ids.filename(new_id, stored.slug)
        task = stored.task.with_field("moved_from", str(task_id))
        old, new = str(task_id), str(new_id)
        task = task.with_field("depends_on", _replace(task.frontmatter.depends_on, old, new))
        self._write(new_path, task.render())
        stored.path.unlink()
        touched = [stored.path, new_path]
        for other in self.all_tasks():
            if old in other.task.frontmatter.depends_on:
                references = _replace(other.task.frontmatter.depends_on, old, new)
                touched += self.save(other, other.task.with_field("depends_on", references)).paths
        moved = StoredTask(new_id, target.name, new_path, stored.archived, task)
        return Change(moved, tuple(touched))

    # -- helpers ---------------------------------------------------------

    def _set_archived(self, task_id: TaskId, archived: bool) -> Change:
        stored = self.find(task_id)
        if stored.archived == archived:
            state = "archived" if archived else "not archived"
            raise ChittyError(f"{task_id} is already {state}")
        context = self.context(stored.context)
        directory = context.archive_directory if archived else context.directory
        new_path = directory / stored.path.name
        directory.mkdir(parents=True, exist_ok=True)
        stored.path.rename(new_path)
        moved = StoredTask(stored.id, stored.context, new_path, archived, stored.task)
        return Change(moved, (stored.path, new_path))

    def _files(self, context: Context, archived: bool) -> list[Path]:
        files: list[Path] = []
        for path, problem in scan(context, archived):
            if problem:
                raise ChittyError(f"{path}: {problem}")
            files.append(path)
        return files

    def _load(self, context: Context, path: Path, archived: bool) -> StoredTask:
        task_id, _ = ids.parse_filename(path.name)
        try:
            task = parse(path.read_text())
        except TaskError as error:
            raise ChittyError(f"{path}: {error}") from None
        return StoredTask(task_id, context.name, path, archived, task)

    def _write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def resolve_add_target(local: Repo | None, name: str | None) -> Target:
    """A context in this repo, or (for `add` only) one from the user's contexts.toml."""
    if name is None:
        if local is None:
            raise ChittyError("no chitty.toml here or in any parent (run `chitty init`)")
        return Target(local, local.default_context, False)
    user = load_user_contexts().contexts
    if local is not None and name in local.config.contexts:
        if name in user:
            raise ChittyError(
                f"context {name!r} is defined in both {local.root / CONFIG_NAME} "
                f"and {user_contexts_path()}; rename one"
            )
        return Target(local, local.context(name), False)
    if name not in user:
        here = local.root / CONFIG_NAME if local else "this directory (no chitty.toml)"
        raise ChittyError(f"no context {name!r} in {here} or {user_contexts_path()}")
    entry = user[name]
    repo = Repo.open(Path(entry.repo).expanduser().resolve())
    context = repo.context(entry.context) if entry.context else repo.default_context
    return Target(repo, context, True)


def guide() -> str:
    return files("chitty").joinpath("guide.md").read_text()


def init_repo(directory: Path, prefix: str) -> list[Path]:
    """Write chitty.toml and the default context, and add the guide to AGENTS.md."""
    config_path = directory / CONFIG_NAME
    if config_path.exists():
        raise ChittyError(f"{config_path} already exists")
    text = INITIAL_CONFIG.format(prefix=prefix)
    config = validate_repo_config(text, config_path)
    config_path.write_text(text)
    written = [config_path]
    (directory / BACKLOG_DIR / config.default_context).mkdir(parents=True, exist_ok=True)
    agents = directory / AGENTS_FILE
    existing = agents.read_text() if agents.exists() else ""
    if GUIDE_HEADING not in existing.splitlines():
        head = existing.rstrip("\n") + "\n\n" if existing.strip() else ""
        agents.write_text(head + guide())
        written.append(agents)
    return written


def matches(
    stored: StoredTask,
    statuses: Sequence[str],
    labels: Sequence[str],
    owner: str | None,
    search: str | None,
) -> bool:
    """Filter for `list`: any of the statuses, all of the labels."""
    fm = stored.task.frontmatter
    if statuses and fm.status not in statuses:
        return False
    if not set(labels) <= set(fm.labels):
        return False
    if owner is not None and fm.owner != owner:
        return False
    if search is None:
        return True
    data = stored.task.as_dict()
    criteria = [c["text"] for c in data["acceptance_criteria"]]
    texts = [fm.title, data["description"], data["plan"], data["notes"], *criteria]
    return any(search.casefold() in text.casefold() for text in texts if text)


def scan(context: Context, archived: bool) -> list[tuple[Path, str | None]]:
    """Every entry in a context directory, with the reason it is invalid (if it is)."""
    directory = context.archive_directory if archived else context.directory
    if not directory.is_dir():
        return []
    entries: list[tuple[Path, str | None]] = []
    for path in sorted(directory.iterdir()):
        if path.is_dir():
            if not archived and path.name == ARCHIVE_DIR:
                continue
            entries.append((path, "unexpected directory in a chitty context"))
            continue
        try:
            task_id, _ = ids.parse_filename(path.name)
        except ids.IdError as error:
            entries.append((path, str(error)))
            continue
        if task_id.prefix != context.prefix:
            message = f"prefix {task_id.prefix!r} does not belong in context {context.name!r}"
            entries.append((path, f"{message} (prefix {context.prefix!r})"))
            continue
        entries.append((path, None))
    return entries


def _update_list(
    current: list[str], add: Sequence[str], remove: Sequence[str], noun: str
) -> list[str]:
    missing = [item for item in remove if item not in current]
    if missing:
        raise ChittyError(f"no {noun} {missing[0]!r} to remove")
    kept = [item for item in current if item not in remove]
    return kept + [item for item in dict.fromkeys(add) if item not in kept]


def _replace(references: list[str], old: str, new: str) -> list[str]:
    return [new if reference == old else reference for reference in references]
