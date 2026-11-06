"""Contexts on disk: find, list, read, write, move, archive."""

import json
import re
import secrets
import sys
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

from chitty import formatter, git, ids, locks
from chitty.actor import actor, remove_pi_session_environment
from chitty.config import (
    BACKLOG_DIR,
    CHITTY_VERSION,
    CONFIG_NAME,
    INITIAL_CONFIG,
    RepoConfig,
    check_setup_version,
    load_repo_config,
    validate_repo_config,
)
from chitty.errors import ChittyError, ManagedGuideError, NoNextTicket
from chitty.ids import TaskId
from chitty.model import (
    DESCRIPTION,
    HISTORY,
    HISTORY_ACTION_SEPARATOR,
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
CLAUDE_FILE = "CLAUDE.md"
GUIDE_HEADING = "## Chitty"
GUIDE_BEGIN = "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->"
GUIDE_END = "<!-- chitty:end -->"
BACKLOG_DESCRIPTION = "This ticket needs refining."
# Failed reviews (review → doing) before a task is escalated to a human.
REVIEW_FAILURE_LIMIT = 3
PRIORITY_ORDER = {"high": 0, "medium": 1, None: 1, "low": 2}
ROLE_NAMES = ("work", "review", "plan")
# Random IDs have eight digits with no leading zero, which `ID_RE` requires.
RANDOM_ID_MIN = 10_000_000
RANDOM_ID_MAX = 99_999_999
# Collisions are vanishingly rare, so many failed draws mean something is wrong.
RANDOM_ID_ATTEMPTS = 100

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
    branch: str | None = None

    @property
    def slug(self) -> str:
        return ids.parse_filename(self.path.name)[1]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "context": self.context,
            "archived": self.archived,
            "path": str(self.path),
            **({"branch": self.branch} if self.branch else {}),
            **self.task.as_dict(),
        }


@dataclass(frozen=True)
class Change:
    """The result of a write: its representative task, affected tasks, and paths."""

    task: StoredTask
    paths: tuple[Path, ...]
    tasks: tuple[StoredTask, ...]
    actor: str | None = None


@dataclass(frozen=True)
class NextAction:
    """The next ticket and whether it needs work or an independent review."""

    mode: Literal["work", "review"]
    id: TaskId

    def as_dict(self) -> dict[str, str]:
        return {"mode": self.mode, "id": str(self.id)}


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
    override_review_independence: bool = False
    # Internal, not exposed in the CLI or MCP: `chitty run` fails a review
    # before any criterion is reviewed, so there is nothing to give a verdict on.
    skip_verdicts: bool = False

    def is_empty(self) -> bool:
        return not any(
            value is not None and (isinstance(value, str) or bool(value))
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
        self._historical_files: list[git.HistoricalFile] | None = None

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

    def review_required(self, context: Context) -> bool:
        """Whether tasks in a context must pass through review before completion."""
        override = self.config.contexts[context.name].review
        return self.config.review if override is None else override

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
            found += self._tasks_in_location(context, False)
        if which in ("archived", "all"):
            found += self._tasks_in_location(context, True)
        return sorted(found, key=lambda t: t.id)

    def _tasks_in_location(self, context: Context, archived: bool) -> list[StoredTask]:
        local = [self._load(context, path, archived) for path in self._files(context, archived)]
        directory = context.archive_directory if archived else context.directory
        relative_directory = directory.relative_to(self.root)
        historical: dict[TaskId, tuple[StoredTask, int]] = {}
        for file in self._history():
            if file.path.parent != relative_directory:
                continue
            try:
                task_id, _ = ids.parse_filename(file.path.name)
                task = parse(file.content)
            except (ids.IdError, TaskError) as error:
                raise ChittyError(f"{file.ref}:{file.path}: {error}") from None
            if task_id.prefix != context.prefix:
                continue
            previous = historical.get(task_id)
            if previous is None or file.committed_at > previous[1]:
                historical[task_id] = (
                    StoredTask(
                        task_id, context.name, self.root / file.path, archived, task, file.ref
                    ),
                    file.committed_at,
                )
        tasks = {task_id: stored for task_id, (stored, _) in historical.items()}
        dirty = git.dirty_paths(self.root, relative_directory)
        current_branch = git.current_branch(self.root)
        for stored in local:
            relative_path = stored.path.relative_to(self.root)
            previous = tasks.get(stored.id)
            if relative_path in dirty or previous is None or previous.branch == current_branch:
                tasks[stored.id] = stored
        return list(tasks.values())

    def _history(self) -> list[git.HistoricalFile]:
        if self._historical_files is None:
            self._historical_files = git.historical_files(self.root, Path(BACKLOG_DIR))
        return self._historical_files

    def all_tasks(self) -> list[StoredTask]:
        return [t for context in self.contexts() for t in self.tasks(context, "all")]

    def find(self, task_id: TaskId) -> StoredTask:
        context = self.context_of(task_id)
        matches = [
            task
            for archived in (False, True)
            for task in self._tasks_in_location(context, archived)
            if task.id == task_id
        ]
        if not matches:
            raise ChittyError(f"no task {task_id} in {context.directory}")
        if len(matches) > 1:
            paths = ", ".join(str(task.path) for task in matches)
            raise ChittyError(f"{task_id} is used by more than one file: {paths}")
        return matches[0]

    def check_dependencies(self, references: Sequence[str]) -> None:
        for reference in references:
            self.find(TaskId.parse(reference))

    # -- writing ---------------------------------------------------------
    #
    # Each public write commits its own paths when autocommit is on.

    def prepare_write(self) -> None:
        """Enforce the repository setup policy before any mutation."""
        self._prepare_write()

    def _prepare_write(self) -> None:
        self._check_setup_version()
        recorded = self.config.chitty_version
        if recorded == CHITTY_VERSION:
            return
        # Setup belongs on main: a ticket branch's own code may be older than
        # the upgraded setup and could not read it. It picks the setup up when
        # rebased onto main.
        if git.is_linked_worktree(self.root):
            return
        if not self.config.autocommit:
            raise ChittyError("repository setup is stale; run `chitty init` before writing")
        try:
            paths = init_repo(self.root, False)
        except ManagedGuideError as error:
            print(
                f"warning: {error}; skipping repository setup upgrade until the marker lines "
                "are repaired",
                file=sys.stderr,
            )
            return
        files = [path for path in paths if path.is_file() and path.is_relative_to(self.root)]
        if files:
            git.commit(self.root, files, "chitty: upgrade repository setup")
        self.config = load_repo_config(self.root)

    def refresh_setup(self) -> None:
        """Refresh setup before running Pi, without changing ticket branches."""
        # `run` may be invoked from a ticket worktree; setup belongs on main.
        if git.is_linked_worktree(self.root):
            return
        self._check_setup_version()
        protected = (CONFIG_NAME, "pyproject.toml", AGENTS_FILE, ".gitignore")
        dirty = [name for name in protected if git.dirty_paths(self.root, Path(name))]
        if dirty:
            raise ChittyError(
                "repository setup files have uncommitted changes; commit or stash these first: "
                + ", ".join(dirty)
            )
        paths = init_repo(self.root, False)
        for path in paths:
            print(path, file=sys.stderr)
        files = [path for path in paths if path.is_file() and path.is_relative_to(self.root)]
        if files and git.is_repository(self.root):
            git.commit(self.root, files, "chitty: upgrade repository setup")
        self.config = load_repo_config(self.root)

    def _check_setup_version(self) -> None:
        check_setup_version(self.config)

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
        self._prepare_write()
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
        if status == "done" and self.review_required(context):
            raise ChittyError("setting status done requires -s review first")
        if description is None:
            if status != "backlog":
                raise ChittyError("description is required unless status is backlog")
            description = BACKLOG_DESCRIPTION
        task = new_task(title, today, description, criteria, fields)
        actor_name = actor()
        task = task.with_section(HISTORY, "").with_history(
            datetime.now(UTC), actor_name, None, task.frontmatter.status
        )
        for note in notes:
            task = task.with_note(note)
        task_id = TaskId(context.prefix, self.next_number(context))
        path = context.directory / ids.filename(task_id, ids.slugify(title))
        self._write(path, task.render())
        stored = StoredTask(task_id, context.name, path, False, task)
        return self._commit(Change(stored, (path,), (stored,)), "add")

    def edit(self, task_id: TaskId, edit: Edit) -> Change:
        """Apply an edit. References in depends_on may be shorthand."""
        self._prepare_write()
        if edit.is_empty():
            raise ChittyError("nothing to change")
        stored = self.find(task_id)
        previous_status = stored.task.frontmatter.status
        if edit.status == "blocked" and not (edit.note or edit.notes):
            raise ChittyError("setting status blocked requires --note with the reason")
        if (
            edit.status == "done"
            and edit.status != previous_status
            and self.review_required(self.context(stored.context))
            and previous_status != "review"
        ):
            raise ChittyError("setting status done requires -s review first")
        is_review_transition = previous_status == "review" and edit.status in {"doing", "done"}
        if edit.status == "doing" and previous_status == "review" and not (edit.note or edit.notes):
            raise ChittyError("moving review → doing requires --note with the reason")
        if (
            edit.status == "done"
            and previous_status == "review"
            and not any(note.startswith("Reviewed:") for note in (edit.note, *edit.notes) if note)
        ):
            raise ChittyError("moving review → done requires --note starting 'Reviewed:'")
        if is_review_transition and not edit.skip_verdicts:
            _validate_review_verdict(stored.task, edit)
        if edit.override_review_independence and not is_review_transition:
            raise ChittyError("--override-review-independence only applies to review transitions")
        if is_review_transition:
            reviewer = actor()
            work = stored.task.review_work(reviewer)
            if work and not edit.override_review_independence:
                raise ChittyError(f"{reviewer} cannot review this task: {', '.join(work)}")
        if edit.status == "doing" and previous_status == "review":
            edit = _escalate_repeated_failure(stored.task, edit)
        edit = replace(
            edit,
            depends_on=self._references(edit.depends_on),
            rm_depends_on=self._references(edit.rm_depends_on),
            parent=str(self.resolve(edit.parent)) if edit.parent else edit.parent,
        )
        task = edit.apply(stored.task)
        # An edit that changes nothing writes nothing, so it records no History either.
        action = _history_action(edit) if task.render() != stored.task.render() else None
        actor_name = None
        if edit.status is not None and edit.status != stored.task.frontmatter.status or action:
            actor_name = actor()
            now = datetime.now(UTC)
            if action:
                task = task.with_history_event(now, actor_name, action)
            if edit.status is not None and edit.status != stored.task.frontmatter.status:
                task = task.with_history(now, actor_name, previous_status, edit.status)
        return self._commit(replace(self._save(stored, task), actor=actor_name), "edit")

    def _save(self, stored: StoredTask, task: Task) -> Change:
        """Write an edited task; touches nothing if the content is unchanged."""
        # Guard every shared-store write so CLI and MCP cannot fork a task differently.
        self._require_current_version(stored)
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
        active_directory = context.directory.relative_to(self.root)
        archive_directory = context.archive_directory.relative_to(self.root)
        for file in self._history():
            if file.path.parent not in (active_directory, archive_directory):
                continue
            try:
                task_id, _ = ids.parse_filename(file.path.name)
            except ids.IdError:
                continue
            if task_id.prefix == context.prefix:
                numbers.append(task_id.number)
        if self.config.archive == "delete":
            numbers += self._deleted_numbers(context)
        if self.config.contexts[context.name].random_ids:
            used = set(numbers)
            for _ in range(RANDOM_ID_ATTEMPTS):
                if (number := _random_number()) not in used:
                    return number
            raise ChittyError(
                f"no unused random number in context {context.name!r} "
                f"after {RANDOM_ID_ATTEMPTS} attempts"
            )
        return ids.next_number(numbers)

    def archive(self, task_id: TaskId) -> Change:
        self._prepare_write()
        change = self._archive(task_id)
        return self._commit(change, "delete" if self.config.archive == "delete" else "archive")

    def archive_done(self) -> tuple[Change, ...]:
        """Archive every non-archived done task in one finalization."""
        self._prepare_write()
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
        self._require_current_version(stored)
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
        stored.path.unlink()
        tasks = _unique_tasks((stored, *(task for change in changes for task in change.tasks)))
        return Change(stored, (*paths, stored.path), tasks)

    def restore(self, task_id: TaskId) -> Change:
        self._prepare_write()
        return self._commit(self._set_archived(task_id, False), "restore")

    def move(self, task_id: TaskId, target: Context) -> Change:
        """Give a task the next ID in another context and rewrite references to it."""
        self._prepare_write()
        stored = self.find(task_id)
        self._require_current_version(stored)
        if target.name == stored.context:
            raise ChittyError(f"{task_id} is already in context {target.name!r}")
        new_id = TaskId(target.prefix, self.next_number(target))
        directory = target.archive_directory if stored.archived else target.directory
        old, new = str(task_id), str(new_id)
        moved_task = stored.task.with_field(
            "depends_on", _replace(stored.task.frontmatter.depends_on, old, new)
        )
        if moved_task.frontmatter.parent == old:
            moved_task = moved_task.with_field("parent", new)
        moved = self._relocate(stored, new_id, target, directory, moved_task)
        touched = [stored.path, moved.path]
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
        tasks = _unique_tasks((moved, *(task for change in changes for task in change.tasks)))
        return self._commit(Change(moved, tuple(touched), tasks), "move")

    def renumber(self, path: Path) -> tuple[Change, tuple[StoredTask, ...]]:
        """Give one of several files sharing an ID the next number in its context.

        The file is found through `scan`, because `find` and `all_tasks` collapse
        files sharing an ID into one. References are not rewritten: a reference
        to a shared ID cannot say which file it meant, so the tickets naming the
        old ID are returned for a person to check.
        """
        context, archived, found = self._locate_task_file(path.resolve())
        directory = context.archive_directory if archived else context.directory
        stored = self._load(context, found, archived)
        task_id = stored.id
        others = [
            other
            for other_archived in (False, True)
            for other in self._files(context, other_archived)
            if other != found and ids.parse_filename(other.name)[0] == task_id
        ]
        if not others:
            raise ChittyError(
                f"{task_id} is used by no other file; use `chitty move` to give it a new ID"
            )
        # Refuse before preparing the write, so a refused renumber changes nothing.
        self._prepare_write()
        new_id = TaskId(context.prefix, self.next_number(context))
        renumbered = self._relocate(stored, new_id, context, directory, stored.task)
        change = self._commit(
            Change(renumbered, (stored.path, renumbered.path), (renumbered,)), "renumber"
        )
        old = str(task_id)
        references = tuple(
            other
            for other in self.all_tasks()
            if other.id != new_id
            and (old in other.task.frontmatter.depends_on or other.task.frontmatter.parent == old)
        )
        return change, references

    def _locate_task_file(self, path: Path) -> tuple[Context, bool, Path]:
        """The context, archive flag and scanned path of a task file, without collapsing IDs."""
        for context in self.contexts():
            for archived in (False, True):
                for candidate, problem in scan(context, archived):
                    if candidate.resolve() != path:
                        continue
                    if problem:
                        raise ChittyError(f"{path}: {problem}")
                    return context, archived, candidate
        raise ChittyError(f"{path} is not a task file in a context of this repository")

    def _relocate(
        self, stored: StoredTask, new_id: TaskId, context: Context, directory: Path, task: Task
    ) -> StoredTask:
        """Write a task under a new ID, recording its old one, and remove the old file."""
        new_path = directory / ids.filename(new_id, stored.slug)
        task = task.with_field("moved_from", str(stored.id))
        self._write(new_path, task.render())
        stored.path.unlink()
        return StoredTask(new_id, context.name, new_path, stored.archived, task)

    # -- helpers ---------------------------------------------------------

    def finalize(self, change: Change, verb: str) -> Change:
        """Run fix, formatting and at most one autocommit for batched writes."""
        self._prepare_write()
        return self._commit(change, verb)

    def _commit(self, change: Change, verb: str) -> Change:
        if not change.paths:
            return change
        existing = [path for path in change.paths if path.exists()]
        if self.config.autoformat or self.config.autocommit:
            # check imports store for scan and domain types, so this intentional
            # local import keeps the dependency one-directional at module load.
            from chitty.check import errors, fix

            directories = tuple(context.directory.resolve() for context in self.contexts())
            task_paths = [
                path
                for path in existing
                if any(path.resolve().is_relative_to(directory) for directory in directories)
            ]
            _, problems = fix(self, self.contexts(), task_paths)
            if blocking := errors(problems):
                details = "\n".join(str(problem) for problem in blocking)
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
        self._require_current_version(stored)
        if stored.archived == archived:
            state = "archived" if archived else "not archived"
            raise ChittyError(f"{task_id} is already {state}")
        context = self.context(stored.context)
        directory = context.archive_directory if archived else context.directory
        new_path = directory / stored.path.name
        directory.mkdir(parents=True, exist_ok=True)
        state = "archived" if archived else stored.task.frontmatter.status
        previous = stored.task.frontmatter.status if archived else "archived"
        actor_name = actor()
        task = stored.task.with_history(datetime.now(UTC), actor_name, previous, state)
        stored.path.rename(new_path)
        self._write(new_path, task.render())
        moved = StoredTask(stored.id, stored.context, new_path, archived, task)
        return Change(moved, (stored.path, new_path), (moved,), actor_name)

    def _require_current_version(self, stored: StoredTask) -> None:
        branch = stored.branch
        if branch is None or branch == git.current_branch(self.root):
            return
        worktree = git.worktree_for_branch(self.root, branch)
        if worktree is not None:
            instruction = f"run Chitty in worktree {worktree}"
        elif git.has_local_branch(self.root, branch):
            instruction = f"run `git switch {branch}` first"
        else:
            instruction = f"run `git switch --track {branch}` first"
        raise ChittyError(
            f"{stored.id}'s latest committed version is on branch {branch}; {instruction}"
        )

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


VERDICT_LINE_RE = re.compile(r"^(\d+): (pass|fail) - (\S.*)$")


def _validate_review_verdict(task: Task, edit: Edit) -> None:
    """Require one pass/fail verdict line for every acceptance criterion."""
    criterion_count = len(task.criteria)
    if not criterion_count:
        return

    lines = [line for note in (edit.note, *edit.notes) if note for line in note.splitlines()]
    verdicts = [
        (int(match.group(1)), match.group(2))
        for line in lines
        if (match := VERDICT_LINE_RE.fullmatch(line))
    ]
    numbers = [number for number, _ in verdicts]
    expected = set(range(1, criterion_count + 1))
    counts = {number: numbers.count(number) for number in set(numbers)}
    missing = sorted(expected - set(numbers))
    duplicated = sorted(number for number, count in counts.items() if count > 1)
    out_of_range = sorted(number for number in set(numbers) if number not in expected)
    problems: list[str] = []
    if missing:
        problems.append(f"missing {', '.join(map(str, missing))}")
    if duplicated:
        problems.append(f"duplicated {', '.join(map(str, duplicated))}")
    if out_of_range:
        problems.append(f"out-of-range {', '.join(map(str, out_of_range))}")
    if problems:
        raise ChittyError(
            "review verdict lines must match ^(\\d+): (pass|fail) - (\\S.*)$; "
            + "; ".join(problems)
        )

    verdict_by_number = {number: verdict for number, verdict in verdicts}
    if edit.status == "done" and any(verdict == "fail" for verdict in verdict_by_number.values()):
        raise ChittyError("moving review → done requires every verdict to be pass")
    if edit.status == "doing" and not any(
        verdict == "fail" for verdict in verdict_by_number.values()
    ):
        raise ChittyError("moving review → doing requires at least one fail verdict")


def _escalate_repeated_failure(task: Task, edit: Edit) -> Edit:
    """Turn the limit-th failed review since the last block into a block for a human."""
    failures = 1
    for old, new in reversed(task.transitions()):
        if new == "blocked":
            break
        failures += (old, new) == ("review", "doing")
    if failures < REVIEW_FAILURE_LIMIT:
        return edit
    reason = (
        f"Escalated to human review: failed review {failures} times. "
        "A human should decide how to proceed, then unblock it."
    )
    return replace(edit, status="blocked", owner="human", notes=(*edit.notes, reason))


def renumbered_dict(change: Change, references: Sequence[StoredTask]) -> dict[str, Any]:
    """The JSON both front ends return for `renumber`."""
    return {
        "task": change.task.as_dict(),
        "references": [{"id": str(task.id), "path": str(task.path)} for task in references],
    }


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


def guide(role: str | None = None, ticket_id: str | None = None) -> str:
    """Return prefix-independent general or role-specific agent guidance."""
    if role is None:
        return files("chitty").joinpath("guide.md").read_text()
    if role not in ROLE_NAMES:
        raise ChittyError(f"unknown role {role!r}; choose from {', '.join(ROLE_NAMES)}")
    if ticket_id is not None and role == "plan":
        raise ChittyError("the plan role does not take a ticket ID")

    text = files("chitty").joinpath("roles", f"{role}.md").read_text()
    return f"Work only on Chitty ticket {ticket_id}.\n\n{text}" if ticket_id is not None else text


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
            (
                "setup",
                '# setup = "make install" # run before the agent starts in a ticket worktree',
            ),
            (
                "agent_command",
                (
                    '# agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts '
                    '--chitty-{mode} {id}"'
                ),
            ),
        )
        if key not in settings and not (key in {"setup", "agent_command"} and f"{key} =" in text)
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


def _add_missing_agent_commands_table(
    text: str, settings: Mapping[str, object], pyproject: bool
) -> str:
    if "agent_commands" in settings:
        return text
    prefix = "tool.chitty." if pyproject else ""
    return text.rstrip() + f"\n\n[{prefix}agent_commands]\n"


def _random_number() -> int:
    """A random ticket number for a `random_ids` context; tests patch it."""
    return RANDOM_ID_MIN + secrets.randbelow(RANDOM_ID_MAX - RANDOM_ID_MIN + 1)


def _add_missing_backlog_context(text: str, config: RepoConfig, pyproject: bool) -> str:
    """Add the generated `backlog` context after the last context table."""
    if "backlog" in config.contexts or any(
        context.prefix == "BACKLOG" for context in config.contexts.values()
    ):
        return text
    prefix = "tool.chitty." if pyproject else ""
    headers = list(re.finditer(rf"(?m)^\[{re.escape(prefix)}contexts\.[^\]]+\]\s*$", text))
    if not headers:
        # Contexts written as dotted keys or inline tables have no header to follow.
        return text
    last = headers[-1]
    following = re.search(r"(?m)^\[", text[last.end() :])
    position = last.end() + following.start() if following else len(text)
    table = f'[{prefix}contexts.backlog]\nprefix = "BACKLOG"\nrandom_ids = true\n'
    rest = text[position:]
    updated = text[:position].rstrip("\n") + "\n\n" + table + ("\n" + rest if rest else "")
    data = tomllib.loads(updated)
    settings = data["tool"]["chitty"] if pyproject else data
    try:
        RepoConfig.model_validate(settings)
    except ValidationError:
        return text
    return updated


def _add_missing_human_review(text: str, config: RepoConfig, pyproject: bool) -> str:
    """Set the generated human context's review policy without changing explicit settings."""
    human = config.contexts.get("human")
    if human is None or human.review is not None:
        return text
    header = r"\[tool\.chitty\.contexts\.human\]" if pyproject else r"\[contexts\.human\]"
    match = re.search(rf"(?m)^{header}\s*$", text)
    if match is None:
        return text
    following = re.search(r"(?m)^\[", text[match.end() :])
    position = match.end() + following.start() if following else len(text)
    return text[:position] + "\nreview = false\n" + text[position:]


def _set_autocommit(text: str, pyproject: bool) -> str:
    """Enable autocommit without changing unrelated TOML tables."""
    pattern = r"(?m)^(autocommit\s*=\s*)false(?=\s*(?:#.*)?$)"
    if not pyproject:
        return re.sub(pattern, r"\g<1>true", text)
    match = re.search(r"(?m)^\[tool\.chitty\]\s*$", text)
    assert match is not None
    following = re.search(r"(?m)^\[", text[match.end() :])
    end = match.end() + following.start() if following else len(text)
    section = text[match.end() : end]
    return text[: match.end()] + re.sub(pattern, r"\g<1>true", section) + text[end:]


def _add_worktrees_to_gitignore(path: Path) -> bool:
    """Add the default agent worktree directory to Git's ignored paths."""
    text = path.read_text() if path.exists() else ""
    if ".worktrees/" in text.splitlines():
        return False
    path.write_text(
        f"{text if not text or text.endswith(chr(10)) else text + chr(10)}.worktrees/\n"
    )
    return True


def _file_state(path: Path) -> tuple[str, bytes | Path] | None:
    if path.is_symlink():
        return "symlink", path.readlink()
    if path.exists():
        return "file", path.read_bytes()
    return None


def _restore_file(path: Path, state: tuple[str, bytes | Path] | None) -> None:
    if path.exists() or path.is_symlink():
        path.unlink()
    if state is None:
        return
    kind, content = state
    if kind == "symlink":
        assert isinstance(content, Path)
        path.symlink_to(content)
    else:
        assert isinstance(content, bytes)
        path.write_bytes(content)


def _managed_agents(existing: str, agents: Path) -> str:
    """Return `AGENTS.md` with the exact managed guide block installed."""
    lines = existing.splitlines(keepends=True)
    offsets: list[tuple[int, int, str]] = []
    offset = 0
    for line in lines:
        offsets.append((offset, offset + len(line), line.rstrip("\n")))
        offset += len(line)
    markers = [
        (index, start, end, value)
        for index, (start, end, value) in enumerate(offsets)
        if value in (GUIDE_BEGIN, GUIDE_END)
    ]
    rendered = f"{GUIDE_BEGIN}\n\n{guide().rstrip('\\n')}\n\n{GUIDE_END}\n"
    if markers:
        begins = [item for item in markers if item[3] == GUIDE_BEGIN]
        ends = [item for item in markers if item[3] == GUIDE_END]
        if len(begins) != 1 or len(ends) != 1 or begins[0][0] >= ends[0][0]:
            raise ManagedGuideError(
                f"{agents} has invalid Chitty guide markers; remove the marker lines so the "
                "next `chitty init` can migrate the block"
            )
        return existing[: begins[0][1]] + rendered + existing[ends[0][2] :]

    pattern = r"(?ms)^## Chitty\n.*?(?=^## |\Z)"
    match = re.search(pattern, existing)
    if match:
        # The legacy match includes the separator before a following heading.
        suffix = existing[match.end() :]
        separator = "\n" if suffix.startswith("## ") else ""
        print(f"migrated Chitty guide markers in {agents}", file=sys.stderr)
        return existing[: match.start()] + rendered + separator + suffix
    return (existing.rstrip("\n") + "\n\n" if existing.strip() else "") + rendered


def init_repo(directory: Path, enable_autocommit: bool) -> list[Path]:
    """Create or non-destructively upgrade the repository's Chitty setup."""
    if enable_autocommit:
        git.require_clean(directory)
    claude = directory / CLAUDE_FILE
    if claude.exists() and not claude.is_symlink():
        raise ChittyError(f"{claude} exists and must be replaced with a symlink to {AGENTS_FILE}")
    from chitty.actor import install_pi_extension, validate_pi_extension
    from chitty.config import inbox_path, load_repo_config, register_project

    config_path = directory / CONFIG_NAME
    pyproject_path = directory / "pyproject.toml"
    agents = directory / AGENTS_FILE
    gitignore = directory / ".gitignore"
    existing_agents = agents.read_text() if agents.exists() else ""
    updated_agents = _managed_agents(existing_agents, agents)
    linked_worktree = git.is_linked_worktree(directory)
    if not linked_worktree:
        validate_pi_extension()
    else:
        print("skipping machine-wide Pi setup from linked Git worktree", file=sys.stderr)
    originals = {
        path: _file_state(path) for path in (config_path, pyproject_path, agents, claude, gitignore)
    }
    has_pyproject_config = False
    if not config_path.exists() and pyproject_path.exists():
        pyproject_data = tomllib.loads(pyproject_path.read_text())
        tool = pyproject_data.get("tool")
        has_pyproject_config = isinstance(tool, Mapping) and "chitty" in tool
    written: list[Path] = []
    if not config_path.exists() and not has_pyproject_config:
        project = _default_project(directory.name)
        text = INITIAL_CONFIG.format(project=json.dumps(project), version=CHITTY_VERSION)
        if enable_autocommit:
            text = _set_autocommit(text, False)
        config = validate_repo_config(text, config_path)
        config_path.write_text(text)
        written.append(config_path)
    else:
        config = load_repo_config(directory)
        check_setup_version(config)
        source = config_path if config_path.exists() else pyproject_path
        text = source.read_text()
        data = tomllib.loads(text)
        settings = data if source == config_path else data["tool"]["chitty"]
        updated = _add_missing_settings(
            text, settings, source == pyproject_path, _default_project(directory.name)
        )
        updated = _add_missing_agent_commands_table(updated, settings, source == pyproject_path)
        updated = _add_missing_human_review(updated, config, source == pyproject_path)
        updated = _add_missing_backlog_context(updated, config, source == pyproject_path)
        updated = re.sub(
            r'(?m)^(chitty_version\s*=\s*)["\'][^"\']*["\']\s*$',
            rf'\g<1>"{CHITTY_VERSION}"',
            updated,
        )
        if enable_autocommit:
            updated = _set_autocommit(updated, source == pyproject_path)
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
    if _add_worktrees_to_gitignore(gitignore):
        written.append(gitignore)
    if not linked_worktree:
        pi_settings = remove_pi_session_environment()
        if pi_settings is not None:
            written.append(pi_settings)
        pi_extension = install_pi_extension()
        if pi_extension is not None:
            written.append(pi_extension)
    if updated_agents != existing_agents:
        agents.write_text(updated_agents)
        written.append(agents)
    if claude.is_symlink() and claude.readlink() != Path(AGENTS_FILE):
        claude.unlink()
    if not claude.exists():
        claude.symlink_to(AGENTS_FILE)
        written.append(claude)
    committed = [path for path in written if path.is_relative_to(directory) and not path.is_dir()]
    if enable_autocommit and committed:
        try:
            git.commit(directory, committed, "chitty: initialize and enable autocommit")
        except ChittyError:
            for path, state in originals.items():
                _restore_file(path, state)
            raise
    return written


def ordered(tasks: Sequence[StoredTask], statuses: Sequence[str]) -> list[StoredTask]:
    """Order tasks by selected status and priority, preserving source order for ties."""
    status_order = {status: index for index, status in enumerate(statuses)}
    return sorted(
        tasks,
        key=lambda stored: (
            status_order[stored.task.frontmatter.status],
            PRIORITY_ORDER[stored.task.frontmatter.priority],
        ),
    )


def _ticket_action(
    repo: Repo,
    stored: StoredTask,
    *,
    refuse: bool,
    owner: str | None = None,
) -> NextAction | None:
    """Validate a ticket for running, or return None when selecting the next ticket."""
    frontmatter = stored.task.frontmatter
    status_order = {"review": 0, "doing": 1, "todo": 2}
    if stored.archived:
        if refuse:
            raise ChittyError(f"cannot run archived ticket {stored.id}")
        return None
    if frontmatter.status not in status_order:
        if refuse:
            raise ChittyError(f"cannot run {stored.id}: status is {frontmatter.status}")
        return None
    if stored.context == "human":
        if refuse:
            raise ChittyError(f"cannot run human ticket {stored.id}")
        return None
    if frontmatter.owner == "human":
        if refuse:
            raise ChittyError(f"cannot run {stored.id}: owner is human")
        return None
    if not refuse:
        if owner is None:
            if frontmatter.status != "review" and frontmatter.owner is not None:
                return None
        elif frontmatter.owner != owner:
            return None
    dependencies: list[tuple[TaskId, StoredTask | None]] = []
    for reference in frontmatter.depends_on:
        dependency_id = TaskId.parse(reference)
        try:
            dependency = repo.find(dependency_id)
        except ChittyError as error:
            if git.main_files(repo.root, ()) is None or "used by more than one file" not in str(
                error
            ):
                raise ChittyError(f"{stored.id} depends on {reference}: {error}") from None
            dependency = None
        dependencies.append((dependency_id, dependency))
    if frontmatter.status == "todo" and any(
        not _dependency_is_done(repo, dependency_id, dependency)
        for dependency_id, dependency in dependencies
    ):
        if refuse:
            raise ChittyError(f"cannot run {stored.id}: it has unfinished dependencies")
        return None
    action_mode: Literal["work", "review"] = "review" if frontmatter.status == "review" else "work"
    return NextAction(action_mode, stored.id)


def _dependency_is_done(repo: Repo, dependency_id: TaskId, dependency: StoredTask | None) -> bool:
    """Whether a dependency is complete on the ref used to create worktrees."""
    context = repo.context_of(dependency_id)
    main_files = git.main_files(
        repo.root,
        (
            context.directory.relative_to(repo.root),
            context.archive_directory.relative_to(repo.root),
        ),
    )
    if main_files is None:
        assert dependency is not None
        return dependency.archived or dependency.task.frontmatter.status == "done"

    matches: list[tuple[bool, Path, Task]] = []
    for path, content in main_files:
        try:
            task_id, _ = ids.parse_filename(path.name)
            task = parse(content)
        except (ids.IdError, TaskError) as error:
            raise ChittyError(f"refs/heads/main:{path}: {error}") from None
        if task_id == dependency_id:
            matches.append((path.parent.name == ARCHIVE_DIR, path, task))
    if not matches:
        return False
    if len(matches) > 1:
        paths = ", ".join(str(path) for _, path, _ in matches)
        raise ChittyError(f"{dependency_id} is used by more than one file: {paths}")
    archived, _, task = matches[0]
    return archived or task.frontmatter.status == "done"


def ticket_action(repo: Repo, task_id: TaskId) -> NextAction:
    """Return the work or review action for an explicitly chosen ticket."""
    try:
        stored = repo.find(task_id)
    except ChittyError:
        raise ChittyError(f"cannot run {task_id}: unknown ticket") from None
    action = _ticket_action(repo, stored, refuse=True)
    assert action is not None
    return action


MODE_STATUSES: dict[str, tuple[str, ...]] = {"work": ("doing", "todo"), "review": ("review",)}


def next_action(
    repo: Repo,
    *,
    mode: Literal["work", "review"] | None = None,
    owner: str | None = None,
) -> NextAction:
    """Select the one ticket to review or work next across every context.

    A `mode` limits the choice to that mode's statuses. It filters before
    `_ticket_action` checks dependencies, so a bad reference on a ticket in the
    other mode does not stop this one. A ticket another `chitty run` holds the
    run lock for is skipped.
    """
    if owner in ("", "human"):
        raise ChittyError("--owner must name an agent, not human or empty")
    status_order = {"review": 0, "doing": 1, "todo": 2}
    locked = locks.locked_ids(repo.root)
    candidates = [
        (stored, action)
        for stored in repo.all_tasks()
        if mode is None or stored.task.frontmatter.status in MODE_STATUSES[mode]
        if str(stored.id) not in locked
        if (action := _ticket_action(repo, stored, refuse=False, owner=owner)) is not None
    ]
    if not candidates:
        raise NoNextTicket(
            "no next ticket" if mode is None else f"no next ticket for --mode {mode}"
        )
    return min(
        candidates,
        key=lambda pair: (
            status_order[pair[0].task.frontmatter.status],
            PRIORITY_ORDER[pair[0].task.frontmatter.priority],
            pair[0].id,
        ),
    )[1]


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


def _history_action(edit: Edit) -> str | None:
    """Describe an edit's deliberate non-status changes as one History event."""
    actions: list[str] = []
    changes: list[str] = []
    if edit.title is not None:
        changes.append("title")
    if edit.add_labels or edit.rm_labels:
        changes.append("labels")
    if edit.priority is not None:
        changes.append("priority")
    if edit.owner is not None:
        changes.append("owner")
    if edit.depends_on or edit.rm_depends_on:
        changes.append("dependencies")
    if edit.parent is not None:
        changes.append("parent")
    if edit.description is not None:
        changes.append("description")
    if edit.add_criteria or edit.rm_criteria or edit.uncheck:
        changes.append("acceptance criteria")
    if edit.note is not None or edit.notes:
        changes.append("notes")
    if edit.summary is not None:
        changes.append("summary")
    if changes:
        actions.append(f"changed {', '.join(changes)}")
    if edit.plan is not None:
        actions.append("wrote the plan")
    if edit.check:
        actions.append("ticked acceptance criteria")
    if edit.override_review_independence:
        actions.append("overrode review independence")
    return HISTORY_ACTION_SEPARATOR.join(actions) or None


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
