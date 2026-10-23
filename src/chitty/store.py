"""Contexts on disk: find, list, read, write, move, archive."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from chitty import ids
from chitty.config import BACKLOG_DIR, RepoConfig, load_repo_config
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.model import FieldValue, Task, TaskError, new_task, parse

ARCHIVE_DIR = "archive"

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

    def as_dict(self, root: Path) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "context": self.context,
            "archived": self.archived,
            "path": str(self.path.relative_to(root)),
            **self.task.as_dict(),
        }


@dataclass(frozen=True)
class Change:
    """The result of a write: the task as it now is, and every path touched."""

    task: StoredTask
    paths: tuple[Path, ...]


class Repo:
    def __init__(self, root: Path, config: RepoConfig) -> None:
        self.root = root
        self.config = config

    @classmethod
    def open(cls, root: Path) -> "Repo":
        return cls(root, load_repo_config(root))

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
        fields: dict[str, FieldValue],
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
        directory = context.archive_directory if archived else context.directory
        if not directory.is_dir():
            return []
        files: list[Path] = []
        for path in sorted(directory.iterdir()):
            if path.is_dir() and not archived and path.name == ARCHIVE_DIR:
                continue
            if path.is_dir():
                raise ChittyError(f"{path}: unexpected directory in a chitty context")
            try:
                task_id, _ = ids.parse_filename(path.name)
            except ids.IdError as error:
                raise ChittyError(f"{path}: {error}") from None
            if task_id.prefix != context.prefix:
                raise ChittyError(
                    f"{path}: prefix {task_id.prefix!r} does not belong in context "
                    f"{context.name!r} (prefix {context.prefix!r})"
                )
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


def _replace(references: list[str], old: str, new: str) -> list[str]:
    return [new if reference == old else reference for reference in references]
