"""Contexts on disk: find, list, read, write, move, archive."""

import json
import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from chitty import formatter, git, ids
from chitty.config import (
    BACKLOG_DIR,
    CHITTY_VERSION,
    CONFIG_NAME,
    INITIAL_CONFIG,
    RepoConfig,
    load_repo_config,
    validate_repo_config,
)
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.model import (
    DESCRIPTION,
    PLAN,
    SUMMARY,
    FieldValue,
    Task,
    TaskError,
    new_task,
    parse,
)

ARCHIVE_DIR = "archive"
AGENTS_FILE = "AGENTS.md"
GUIDE_HEADING = "## Chitty"
BACKLOG_DESCRIPTION = "This ticket needs refining."

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
    """The result of a write: its representative task, affected tasks, and paths."""

    task: StoredTask
    paths: tuple[Path, ...]
    tasks: tuple[StoredTask, ...]


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
    parent: str | None = None  # "" removes
    description: str | None = None
    add_criteria: Sequence[str] = ()
    rm_criteria: Sequence[int] = ()
    check: Sequence[int] = ()
    uncheck: Sequence[int] = ()
    plan: str | None = None  # "" removes
    note: str | None = None
    notes: Sequence[str] = ()
    summary: str | None = None  # "" removes

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
        if self.parent is not None:
            task = task.with_field("parent", self.parent or None)
        if self.description is not None:
            task = task.with_section(DESCRIPTION, self.description)
        task = task.with_criteria(
            add=self.add_criteria, remove=self.rm_criteria, check=self.check, uncheck=self.uncheck
        )
        if self.plan is not None:
            task = task.with_section(PLAN, self.plan)
        if self.note is not None:
            task = task.with_note(self.note)
        for note in self.notes:
            task = task.with_note(note)
        if self.summary is not None:
            task = task.with_section(SUMMARY, self.summary)
        return task


@dataclass(frozen=True)
class Target:
    """Where `add` writes: this repo, or a user-level context in another repo."""

    repo: "Repo"
    context: Context


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
    #
    # Each public write commits its own paths when autocommit is on.

    def add(
        self,
        context: Context,
        title: str,
        description: str | None,
        criteria: Sequence[str],
        fields: Mapping[str, FieldValue],
        today: date,
        notes: Sequence[str] = (),
    ) -> Change:
        """Create a task. References in depends_on may be shorthand."""
        fields = dict(fields)
        depends_on = fields.get("depends_on")
        if isinstance(depends_on, list):
            fields["depends_on"] = self._references(depends_on)
            self.check_dependencies(fields["depends_on"])
        parent = fields.get("parent")
        if isinstance(parent, str):
            fields["parent"] = str(self.resolve(parent))
            self.find(TaskId.parse(fields["parent"]))
        status = fields.get("status", "todo")
        if status == "done" and self.config.review:
            raise ChittyError("setting status done requires -s review first")
        if description is None:
            if status != "backlog":
                raise ChittyError("description is required unless status is backlog")
            description = BACKLOG_DESCRIPTION
        task = new_task(title, today, description, criteria, fields)
        for note in notes:
            task = task.with_note(note)
        task_id = TaskId(context.prefix, self.next_number(context))
        path = context.directory / ids.filename(task_id, ids.slugify(title))
        self._write(path, task.render())
        stored = StoredTask(task_id, context.name, path, False, task)
        return self._commit(Change(stored, (path,), (stored,)), "add")

    def edit(self, task_id: TaskId, edit: Edit) -> Change:
        """Apply an edit. References in depends_on may be shorthand."""
        if edit.is_empty():
            raise ChittyError("nothing to change")
        stored = self.find(task_id)
        previous_status = stored.task.frontmatter.status
        if edit.status == "blocked" and not (edit.note or edit.notes):
            raise ChittyError("setting status blocked requires --note with the reason")
        if (
            edit.status == "done"
            and edit.status != previous_status
            and self.config.review
            and previous_status != "review"
        ):
            raise ChittyError("setting status done requires -s review first")
        if edit.status == "doing" and previous_status == "review" and not (edit.note or edit.notes):
            raise ChittyError("moving review → doing requires --note with the reason")
        edit = replace(
            edit,
            depends_on=self._references(edit.depends_on),
            rm_depends_on=self._references(edit.rm_depends_on),
            parent=str(self.resolve(edit.parent)) if edit.parent else edit.parent,
        )
        task = edit.apply(stored.task)
        if edit.status is not None and edit.status != stored.task.frontmatter.status:
            task = task.with_history(date.today(), previous_status, edit.status)
        return self._commit(self._save(stored, task), "edit")

    def _save(self, stored: StoredTask, task: Task) -> Change:
        """Write an edited task; touches nothing if the content is unchanged."""
        if task.frontmatter.depends_on != stored.task.frontmatter.depends_on:
            self.check_dependencies(task.frontmatter.depends_on)
        if task.frontmatter.parent and task.frontmatter.parent != stored.task.frontmatter.parent:
            self.find(TaskId.parse(task.frontmatter.parent))
        path = stored.path
        if task.frontmatter.title != stored.task.frontmatter.title:
            target = path.with_name(ids.filename(stored.id, ids.slugify(task.frontmatter.title)))
            if target != path:
                if target.exists():
                    raise ChittyError(f"cannot rename {path} to {target}: destination exists")
                git.move(self.root, path, target)
                path = target
        updated = StoredTask(stored.id, stored.context, path, stored.archived, task)
        if task.render() == stored.task.render():
            return Change(updated, (), ())
        self._write(path, task.render())
        paths = (stored.path, path) if path != stored.path else (path,)
        return Change(updated, paths, (updated,))

    def next_number(self, context: Context) -> int:
        numbers = [
            ids.parse_filename(p.name)[0].number
            for archived in (False, True)
            for p in self._files(context, archived)
        ]
        if self.config.archive == "delete":
            numbers += self._deleted_numbers(context)
        return ids.next_number(numbers)

    def archive(self, task_id: TaskId) -> Change:
        change = self._archive(task_id)
        return self._commit(change, "delete" if self.config.archive == "delete" else "archive")

    def archive_done(self) -> tuple[Change, ...]:
        """Archive every non-archived done task in one finalization."""
        changes = tuple(
            self._archive(task.id)
            for context in self.contexts()
            for task in self.tasks(context, "active")
            if task.task.frontmatter.status == "done"
        )
        if changes:
            paths = tuple(path for change in changes for path in change.paths)
            verb = "delete" if self.config.archive == "delete" else "archive"
            tasks = _unique_tasks(tuple(task for change in changes for task in change.tasks))
            self._commit(Change(changes[-1].task, paths, tasks), f"{verb} done tasks")
        return changes

    def _archive(self, task_id: TaskId) -> Change:
        if self.config.archive == "move":
            return self._set_archived(task_id, True)
        return self._delete_done(task_id)

    def _deleted_numbers(self, context: Context) -> list[int]:
        numbers: list[int] = []
        directory = Path(BACKLOG_DIR) / context.name
        for path in git.deleted_paths(self.root):
            try:
                task_id, _ = ids.parse_filename(path.name)
            except ids.IdError:
                continue
            if task_id.prefix == context.prefix and directory in path.parents:
                numbers.append(task_id.number)
        return numbers

    def _delete_done(self, task_id: TaskId) -> Change:
        stored = self.find(task_id)
        if stored.task.frontmatter.status != "done":
            raise ChittyError(f"{task_id} is not done and cannot be deleted")
        paths: list[Path] = []
        changes: list[Change] = []
        for other in self.all_tasks():
            if other.id == task_id:
                continue
            task = other.task
            if str(task_id) in task.frontmatter.depends_on:
                references = [item for item in task.frontmatter.depends_on if item != str(task_id)]
                task = task.with_field("depends_on", references)
            if task.frontmatter.parent == str(task_id):
                task = task.with_field("parent", None)
            change = self._save(other, task)
            paths += change.paths
            changes.append(change)
        deleted = replace(
            stored,
            task=stored.task.with_history(date.today(), stored.task.frontmatter.status, "deleted"),
        )
        stored.path.unlink()
        tasks = _unique_tasks((deleted, *(task for change in changes for task in change.tasks)))
        return Change(deleted, (*paths, stored.path), tasks)

    def restore(self, task_id: TaskId) -> Change:
        return self._commit(self._set_archived(task_id, False), "restore")

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
        if task.frontmatter.parent == old:
            task = task.with_field("parent", new)
        self._write(new_path, task.render())
        stored.path.unlink()
        touched = [stored.path, new_path]
        changes: list[Change] = []
        for other in self.all_tasks():
            task = other.task
            if old in task.frontmatter.depends_on:
                task = task.with_field(
                    "depends_on", _replace(task.frontmatter.depends_on, old, new)
                )
            if task.frontmatter.parent == old:
                task = task.with_field("parent", new)
            change = self._save(other, task)
            touched += change.paths
            changes.append(change)
        moved = StoredTask(new_id, target.name, new_path, stored.archived, task)
        tasks = _unique_tasks((moved, *(task for change in changes for task in change.tasks)))
        return self._commit(Change(moved, tuple(touched), tasks), "move")

    # -- helpers ---------------------------------------------------------

    def finalize(self, change: Change, verb: str) -> Change:
        """Run fix, formatting and at most one autocommit for batched writes."""
        return self._commit(change, verb)

    def _commit(self, change: Change, verb: str) -> Change:
        if not change.paths:
            return change
        existing = [path for path in change.paths if path.exists()]
        if self.config.autoformat or self.config.autocommit:
            # check imports store for scan and domain types, so this intentional
            # local import keeps the dependency one-directional at module load.
            from chitty.check import fix

            directories = tuple(context.directory.resolve() for context in self.contexts())
            task_paths = [
                path
                for path in existing
                if any(path.resolve().is_relative_to(directory) for directory in directories)
            ]
            _, problems = fix(self, self.contexts(), task_paths)
            if problems:
                details = "\n".join(str(problem) for problem in problems)
                raise ChittyError(
                    f"cannot finalize task write with unresolved problems:\n{details}"
                )
        if self.config.autoformat:
            formatter.run(self.root, self.config.autoformat, existing)
        if self.config.autocommit:
            title = change.task.task.frontmatter.title
            message = f"chitty: {verb} {change.task.id} {title}"
            trailers = "\n".join(f"Task: {task.id}" for task in change.tasks)
            git.commit(self.root, change.paths, f"{message}\n\n{trailers}")
        return change

    def _references(self, references: Sequence[str]) -> list[str]:
        return [str(self.resolve(reference)) for reference in dict.fromkeys(references)]

    def _set_archived(self, task_id: TaskId, archived: bool) -> Change:
        stored = self.find(task_id)
        if stored.archived == archived:
            state = "archived" if archived else "not archived"
            raise ChittyError(f"{task_id} is already {state}")
        context = self.context(stored.context)
        directory = context.archive_directory if archived else context.directory
        new_path = directory / stored.path.name
        directory.mkdir(parents=True, exist_ok=True)
        state = "archived" if archived else stored.task.frontmatter.status
        previous = stored.task.frontmatter.status if archived else "archived"
        task = stored.task.with_history(date.today(), previous, state)
        stored.path.rename(new_path)
        self._write(new_path, task.render())
        moved = StoredTask(stored.id, stored.context, new_path, archived, task)
        return Change(moved, (stored.path, new_path), (moved,))

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


def _unique_tasks(tasks: Sequence[StoredTask]) -> tuple[StoredTask, ...]:
    """Keep one trailer per task ID, in the order the tasks were written."""
    result: list[StoredTask] = []
    seen: set[str] = set()
    for task in tasks:
        if str(task.id) not in seen:
            seen.add(str(task.id))
            result.append(task)
    return tuple(result)


def resolve_add_target(local: Repo | None, name: str | None) -> Target:
    """Resolve an add target only within the current repository."""
    if local is None:
        raise ChittyError("no chitty.toml here or in any parent (run `chitty init`)")
    return Target(local, local.context(name) if name else local.default_context)


def guide(prefix: str = "TASK") -> str:
    """Render agent guidance using a repository's default task prefix."""
    template = files("chitty").joinpath("guide.md").read_text()
    return template.replace("TASK-N", f"{prefix}-N")


def _default_project(directory_name: str) -> str:
    project = re.sub(r"[^a-z0-9]+", "-", directory_name.lower()).strip("-")
    if not project:
        raise ChittyError(
            'cannot derive a project name; choose a valid directory name or set project = "name" '
            "in configuration before running init"
        )
    return project


def _add_missing_settings(
    text: str, settings: Mapping[str, object], pyproject: bool, project: str
) -> str:
    additions = [
        value
        for key, value in (
            ("project", f"project = {json.dumps(project)}"),
            ("chitty_version", f'chitty_version = "{CHITTY_VERSION}"'),
            ("archive", 'archive = "move"'),
            ("review", "review = true"),
        )
        if key not in settings
    ]
    if not additions:
        return text
    if pyproject:
        match = re.search(r"(?m)^\[tool\.chitty\]\s*$", text)
        assert match is not None
        following = re.search(r"(?m)^\[", text[match.end() :])
        position = match.end() + following.start() if following else len(text)
    else:
        following = re.search(r"(?m)^\[", text)
        position = following.start() if following else len(text)
    return text[:position] + "\n".join(additions) + "\n\n" + text[position:]


def init_repo(directory: Path, prefix: str | None) -> list[Path]:
    """Create or non-destructively upgrade the repository's Chitty setup."""
    from chitty.config import inbox_path, load_repo_config, register_project

    config_path = directory / CONFIG_NAME
    pyproject_path = directory / "pyproject.toml"
    has_pyproject_config = False
    if not config_path.exists() and pyproject_path.exists():
        pyproject_data = tomllib.loads(pyproject_path.read_text())
        tool = pyproject_data.get("tool")
        has_pyproject_config = isinstance(tool, Mapping) and "chitty" in tool
    written: list[Path] = []
    if not config_path.exists() and not has_pyproject_config:
        project = _default_project(directory.name)
        text = INITIAL_CONFIG.format(
            prefix=prefix or "TASK", project=json.dumps(project), version=CHITTY_VERSION
        )
        config = validate_repo_config(text, config_path)
        config_path.write_text(text)
        written.append(config_path)
    else:
        config = load_repo_config(directory)
        default = config.contexts[config.default_context]
        if prefix is not None and prefix != default.prefix:
            raise ChittyError(
                f"--prefix {prefix} disagrees with existing default context prefix {default.prefix}"
            )
        source = config_path if config_path.exists() else pyproject_path
        text = source.read_text()
        data = tomllib.loads(text)
        settings = data if source == config_path else data["tool"]["chitty"]
        updated = _add_missing_settings(
            text, settings, source == pyproject_path, _default_project(directory.name)
        )
        updated = re.sub(
            r'(?m)^(chitty_version\s*=\s*)["\'][^"\']*["\']\s*$',
            rf'\g<1>"{CHITTY_VERSION}"',
            updated,
        )
        if updated != text:
            tomllib.loads(updated)
            source.write_text(updated)
            written.append(source)
            config = load_repo_config(directory)
    for name in config.contexts:
        path = directory / BACKLOG_DIR / name
        if not path.exists():
            path.mkdir(parents=True)
            written.append(path)
    if config.project:
        inbox = inbox_path(config.project)
        owner = inbox / "repo"
        changed = not owner.exists() or owner.read_text().strip() != str(directory.resolve())
        register_project(config.project, directory)
        if changed:
            written.append(inbox)
    agents = directory / AGENTS_FILE
    existing = agents.read_text() if agents.exists() else ""
    pattern = r"(?ms)^## Chitty\n.*?(?=^## |\Z)"
    rendered_guide = guide(config.contexts[config.default_context].prefix)
    updated, count = re.subn(pattern, rendered_guide.rstrip() + "\n", existing)
    if not count:
        updated = (existing.rstrip("\n") + "\n\n" if existing.strip() else "") + rendered_guide
    if updated != existing:
        agents.write_text(updated)
        written.append(agents)
    return written


def matches(
    stored: StoredTask,
    statuses: Sequence[str],
    labels: Sequence[str],
    owner: str | None,
    search: str | None,
    parent: str | None = None,
) -> bool:
    """Filter for `list`: any of the statuses, all of the labels."""
    fm = stored.task.frontmatter
    if statuses and fm.status not in statuses:
        return False
    if not set(labels) <= set(fm.labels):
        return False
    if owner is not None and fm.owner != owner:
        return False
    if parent is not None and fm.parent != parent:
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
