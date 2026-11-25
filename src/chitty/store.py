"""Contexts on disk: find, list, read, write, move, archive."""

import json
import re
import secrets
import shutil
import subprocess
import sys
import time
import tomllib
from collections.abc import Generator, Iterable, Mapping, Sequence
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from importlib.resources import files
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

from chitty import commands, formatter, git, ids, locks
from chitty.actor import actor
from chitty.config import (
    BACKLOG_DIR,
    CHITTY_VERSION,
    CONFIG_NAME,
    INITIAL_CONFIG,
    RepoConfig,
    check_setup_version,
    load_repo_config,
    resolve_workflow,
    runner_required_message,
    search_root,
    validate_repo_config,
)
from chitty.errors import ChittyError, ManagedGuideError, NoNextTicket, ProvisionalOffMain
from chitty.ids import TaskId
from chitty.markdown import escape_literal_asterisks
from chitty.model import (
    DESCRIPTION,
    STATUSES as TASK_STATUSES,
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
from chitty.renumbering import blocking_link, plan_renumbering, rewrite_task
from chitty.selection import (
    STATUSES,
    DependencyFact,
    TicketFacts,
    blocker_marker,
    blocking_ids,
    choose,
    dependency_marker,
    mode_statuses,
)
from chitty.selection import skip_reason as pure_skip_reason
from chitty.ticket_source import WORKING_TREE, ticket_source

ARCHIVE_DIR = "archive"
AGENTS_FILE = "AGENTS.md"
CLAUDE_FILE = "CLAUDE.md"
GUIDE_HEADING = "## Chitty"
GUIDE_BEGIN = "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->"
GUIDE_END = "<!-- chitty:end -->"
BACKLOG_DESCRIPTION = "This ticket needs refining."
# Failed reviews (review → doing) before a task is escalated to a human.
REVIEW_FAILURE_LIMIT = 3
PLANNING_RETURN_LIMIT = 3
PRIORITY_ORDER = {"high": 0, "medium": 1, None: 1, "low": 2}
ROLE_NAMES = ("work", "review", "repair", "plan", "cold-read", "setup", "rebase")
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
class SummaryLine:
    id: TaskId
    title: str
    when: datetime
    actor: str
    new: bool


def summary_sections(
    tasks: Sequence["StoredTask"], now: datetime, hours: int
) -> list[tuple[str, list[SummaryLine]]]:
    """Group tasks changed in the `hours` before `now` by their latest status.

    Pure: reads only each task's timed History transitions.
    """
    start = now - timedelta(hours=hours)
    sections: dict[str, list[SummaryLine]] = {}
    for stored in tasks:
        transitions = stored.task.attributed_transitions()
        eligible = [t for t in transitions if start <= t[0] <= now]
        if not eligible:
            continue
        # max/min keep the first of equal keys, so index breaks ties by line order.
        _, (when, actor, _, new) = max(enumerate(eligible), key=lambda pair: (pair[1][0], pair[0]))
        first_when, _, first_old, _ = min(transitions, key=lambda t: t[0])
        created = first_old is None and start <= first_when <= now
        title = stored.task.frontmatter.title
        sections.setdefault(new, []).append(SummaryLine(stored.id, title, when, actor, created))
    rank = {status: index for index, status in enumerate(reversed(TASK_STATUSES))}
    order = sorted(sections, key=lambda status: (rank.get(status, len(rank)), status))
    return [
        (status, sorted(sections[status], key=lambda line: (-line.when.timestamp(), line.id)))
        for status in order
    ]


@dataclass(frozen=True)
class SourceCopy:
    ref: str | None
    path: Path
    task: Task


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
    previous_status: str | None = None


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
    replace_in_description: Sequence[tuple[str, str]] = ()
    add_criteria: Sequence[str] = ()
    rm_criteria: Sequence[int] = ()
    set_criteria: Sequence[tuple[int, str]] = ()
    check: Sequence[int] = ()
    uncheck: Sequence[int] = ()
    plan: str | None = None  # "" removes
    note: str | None = None
    notes: Sequence[str] = ()
    set_notes: str | None = None  # "" removes
    summary: str | None = None  # "" removes
    override_review_independence: bool = False
    human: bool = False
    # Internal, not exposed in the CLI or MCP: `chitty run` fails a review
    # before any criterion is reviewed, so there is nothing to give a verdict on.
    skip_verdicts: bool = False
    # Internal runner handoff: synchronize a status in the main checkout after
    # an error repair, even though the repair branch has a newer task revision.
    skip_current_version: bool = False

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
            task = task.with_section(DESCRIPTION, escape_literal_asterisks(self.description))
        if self.replace_in_description:
            task = task.with_section(
                DESCRIPTION,
                escape_literal_asterisks(
                    replace_pairs(task.section(DESCRIPTION) or "", self.replace_in_description)
                ),
            )
        task = task.with_criteria(
            add=[escape_literal_asterisks(text) for text in self.add_criteria],
            remove=self.rm_criteria,
            set_criteria=[(i, escape_literal_asterisks(text)) for i, text in self.set_criteria],
            check=self.check,
            uncheck=self.uncheck,
        )
        if self.plan is not None:
            task = task.with_section(PLAN, escape_literal_asterisks(self.plan))
        if self.note is not None:
            task = task.with_note(escape_literal_asterisks(self.note))
        for note in self.notes:
            task = task.with_note(escape_literal_asterisks(note))
        if self.set_notes is not None:
            task = task.with_section("Notes", escape_literal_asterisks(self.set_notes))
        if self.summary is not None:
            task = task.with_section(SUMMARY, escape_literal_asterisks(self.summary))
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
        self._discovered_contexts: list[Context] | None = None
        self._ticket_ids: set[TaskId] | None = None
        self._ticket_ref_files: dict[str, list[tuple[Path, str]]] | None = None
        self._working_index: dict[TaskId, list[Path]] | None = None
        self._ref_index: dict[str, dict[TaskId, list[tuple[Path, str]]]] = {}
        self._source_refs: dict[TaskId, str] = {}
        self._task_locations: dict[tuple[str, bool], list[StoredTask]] = {}
        self._current_branch_cached = False
        self._current_branch_value: str | None = None
        self._repository_value: bool | None = None
        self._main_tip_cached = False
        self._main_tip_value: str | None = None
        self._branch_tips_value: dict[str, str] | None = None
        self._main_branch_value: str | None = None
        self._main_files: dict[tuple[str, tuple[Path, ...]], list[tuple[Path, str]] | None] = {}

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
        """Resolve a context from the first selected path, without parsing the ticket.

        Use the same discovery and selection as `source_copy`, but do not reject
        duplicate copies. Fall back to a configured prefix match if the path
        gives no context, even for an absent ticket. Discovery and selection
        errors propagate; no matching context raises `<id>: no context`.
        """
        _, copies = self._source_files(task_id)
        if copies:
            name = copies[0][0].parts[1]
            for context in self.discovered_contexts():
                if context.name == name:
                    return context
        for context in self.contexts():
            if context.prefix == task_id.prefix:
                return context
        raise ChittyError(f"{task_id}: no context in {self.root} has prefix {task_id.prefix!r}")

    def discovered_contexts(self) -> list[Context]:
        """Configured contexts plus on-disk directories containing ticket files."""
        if self._discovered_contexts is not None:
            return list(self._discovered_contexts)
        root = self.root / BACKLOG_DIR
        contexts = {context.name: context for context in self.contexts()}
        if root.is_dir():
            for directory in sorted(path for path in root.iterdir() if path.is_dir()):
                contexts.setdefault(directory.name, Context(directory.name, "", directory))
        names: set[str] = set()
        files_by_ref = self._ref_files()
        main_ref = f"refs/heads/{self._main_branch()}" if files_by_ref else ""
        for ref, ref_files in files_by_ref.items():
            for path, _ in ref_files:
                parts = path.parts
                if not (len(parts) == 3 or (len(parts) == 4 and parts[2] == ARCHIVE_DIR)):
                    continue
                if parts[0] != BACKLOG_DIR:
                    continue
                if ref != main_ref:
                    try:
                        task_id, _ = ids.parse_filename(path.name)
                    except ids.IdError:
                        continue
                    if str(task_id).lower() != ref.rsplit("/", 1)[-1]:
                        continue
                names.add(parts[1])
        for name in sorted(names):
            contexts.setdefault(name, Context(name, "", root / name))
        self._discovered_contexts = list(contexts.values())
        return list(self._discovered_contexts)

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
        """List authoritative tickets in one active or archive directory."""
        key = (context.name, archived)
        cached = self._task_locations.get(key)
        if cached is not None:
            return list(cached)
        directory = (context.archive_directory if archived else context.directory).relative_to(
            self.root
        )
        result: list[StoredTask] = []
        for task_id in self.ticket_ids():
            ref, copies = self._source_files(task_id)
            if not any(path.parent == directory for path, _ in copies):
                continue
            source = self._parse_source_copy(task_id, ref, copies)
            if source is not None:
                result.append(
                    StoredTask(
                        task_id,
                        context.name,
                        self.root / source.path,
                        archived,
                        source.task,
                        source.ref,
                    )
                )
        self._task_locations[key] = result
        return list(result)

    def _current_branch(self) -> str | None:
        if not self._current_branch_cached:
            self._current_branch_value = git.current_branch(self.root)
            self._current_branch_cached = True
        return self._current_branch_value

    def _is_repository(self) -> bool:
        if self._repository_value is None:
            self._repository_value = git.is_repository(self.root)
        return self._repository_value

    def _main_tip(self) -> str | None:
        if not self._main_tip_cached:
            self._main_tip_value = git.ref_commit(self.root, f"refs/heads/{self._main_branch()}")
            self._main_tip_cached = True
        return self._main_tip_value

    def _branch_tips(self) -> dict[str, str]:
        if self._branch_tips_value is None:
            self._branch_tips_value = git.branch_tips(self.root)
        return self._branch_tips_value

    def _main_branch(self) -> str:
        if self._main_branch_value is None:
            if git.is_linked_worktree(self.root):
                self._main_branch_value = load_repo_config(git.main_checkout(self.root)).main_branch
            else:
                self._main_branch_value = self.config.main_branch
        return self._main_branch_value

    def _main_files_for(
        self, branch: str, directories: tuple[Path, ...]
    ) -> list[tuple[Path, str]] | None:
        key = (branch, directories)
        if key not in self._main_files:
            self._main_files[key] = git.main_files(self.root, branch, directories)
        return self._main_files[key]

    def _invalidate(self) -> None:
        self._discovered_contexts = None
        self._ticket_ids = None
        self._ticket_ref_files = None
        self._working_index = None
        self._ref_index.clear()
        self._source_refs.clear()
        self._task_locations.clear()
        self._current_branch_cached = False
        self._current_branch_value = None
        self._repository_value = None
        self._main_tip_cached = False
        self._main_tip_value = None
        self._branch_tips_value = None
        self._main_branch_value = None
        self._main_files.clear()

    def source_of(self, task_id: TaskId) -> str | None:
        """Return the short ref selected for a ticket, or None for the working tree."""
        if task_id not in self._source_refs:
            if not self._is_repository():
                self._source_refs[task_id] = WORKING_TREE
            else:
                self.ticket_ids()
                self._source_refs[task_id] = self._choose_source(task_id)
        ref = self._source_refs[task_id]
        return ref.removeprefix("refs/heads/").removeprefix("refs/remotes/") if ref else None

    def source_copy(self, task_id: TaskId) -> SourceCopy | None:
        """Parse the unique file at the selected source, or return `None` if absent.

        Use the working tree outside Git and `_choose_source` otherwise.
        Discovery can fail on an invalid entry even for another ticket, with
        `<path>: <error>` locally or `<main>:<path>: <error>` on the main ref.
        Selection errors propagate. Multiple matches raise `<id> is used by
        more than one file`; parse failures use `<path>: <error>` for the working
        tree or `<ref>:<path>: <error>` for a ref (using its short name).
        """
        ref, copies = self._source_files(task_id)
        return self._parse_source_copy(task_id, ref, copies)

    def _source_files(self, task_id: TaskId) -> tuple[str, list[tuple[Path, str]]]:
        """The ticket's source ref and its files there, unparsed."""
        if task_id not in self._source_refs:
            if not self._is_repository():
                self._source_refs[task_id] = WORKING_TREE
            else:
                self.ticket_ids()
                self._source_refs[task_id] = self._choose_source(task_id)
        ref = self._source_refs[task_id]
        copies = (
            self._working_ticket_files(task_id)
            if ref == WORKING_TREE
            else self._ref_ticket_files(ref, task_id)
        )
        return ref, copies

    def _working_ticket_files(self, task_id: TaskId) -> list[tuple[Path, str]]:
        paths = self._working_ticket_index().get(task_id, [])
        return [(path.relative_to(self.root), path.read_text()) for path in paths]

    def _working_ticket_index(self) -> dict[TaskId, list[Path]]:
        """Every working-tree ticket path by id, from one walk of `chitty/`.

        Paths keep the walk order: context directories by name, each active
        then archive, and by name within a directory. An invalid entry anywhere
        raises `_files`'s error, whichever ticket is later asked for.
        """
        if self._working_index is None:
            index: dict[TaskId, list[Path]] = {}
            root = self.root / BACKLOG_DIR
            if root.is_dir():
                for directory in sorted(path for path in root.iterdir() if path.is_dir()):
                    context = Context(directory.name, "", directory)
                    for archived in (False, True):
                        for path in self._files(context, archived):
                            index.setdefault(ids.parse_filename(path.name)[0], []).append(path)
            self._working_index = index
        return self._working_index

    def _parse_source_copy(
        self, task_id: TaskId, ref: str, copies: list[tuple[Path, str]]
    ) -> SourceCopy | None:
        if len(copies) > 1:
            paths_text = ", ".join(str(self.root / path) for path, _ in copies)
            raise ChittyError(f"{task_id} is used by more than one file: {paths_text}")
        if not copies:
            return None
        path, content = copies[0]
        short = ref.removeprefix("refs/heads/").removeprefix("refs/remotes/") if ref else None
        try:
            task = parse(content)
        except TaskError as error:
            location = f"{short}:{path}" if short is not None else str(self.root / path)
            raise ChittyError(f"{location}: {error}") from None
        return SourceCopy(short, path, task)

    def _ref_ticket_files(self, ref: str, task_id: TaskId) -> list[tuple[Path, str]]:
        return list(self._ref_ticket_index(ref).get(task_id, []))

    def _ref_ticket_index(self, ref: str) -> dict[TaskId, list[tuple[Path, str]]]:
        """`ref`'s ticket files (from `_ref_files`) by id; unparseable names are skipped."""
        if ref not in self._ref_index:
            index: dict[TaskId, list[tuple[Path, str]]] = {}
            for path, content in self._ref_files().get(ref, []):
                parts = path.parts
                if not (len(parts) == 3 or (len(parts) == 4 and parts[2] == ARCHIVE_DIR)):
                    continue
                if parts[0] != BACKLOG_DIR:
                    continue
                try:
                    found, _ = ids.parse_filename(path.name)
                except ids.IdError:
                    continue
                index.setdefault(found, []).append((path, content))
            self._ref_index[ref] = index
        return self._ref_index[ref]

    def _choose_source(self, task_id: TaskId) -> str:
        """Return a full Git ref or `WORKING_TREE` as chosen by `ticket_source`.

        Candidates are configured main, the ticket branch, and its remote-tracking
        refs. Selection does not parse ticket bodies or guarantee a file exists.
        Policy failures report a missing tip (`configured main branch`),
        divergence (`ticket <id> has diverged refs`), or conflicting changes
        (`ticket <id> changed on both`), with the ID quoted in backticks.
        Git and configuration errors propagate.
        """
        main = self._main_branch()
        main_ref = f"refs/heads/{main}"
        main_tip = self._main_tip()
        tips = self._branch_tips()
        ticket_tips = {
            ref: tip for ref, tip in tips.items() if ref in self._ref_files() and ref != main_ref
        }
        local = {
            ref.removeprefix("refs/heads/"): tip
            for ref, tip in ticket_tips.items()
            if ref.startswith("refs/heads/")
        }
        remote = {
            ref.removeprefix("refs/remotes/"): tip
            for ref, tip in ticket_tips.items()
            if ref.startswith("refs/remotes/")
        }

        def full_ref(name: str) -> str:
            if name == main or name == str(task_id).lower():
                return f"refs/heads/{name}"
            return f"refs/remotes/{name}"

        def changed_on_both(name: str) -> bool:
            if main_tip is None:
                return False
            ref = full_ref(name)
            paths = sorted(
                {
                    path
                    for source in (main_ref, ref)
                    for path, _ in self._ref_ticket_files(source, task_id)
                }
            )
            return git.changed_since_split(
                self.root, tips[ref], main_tip, paths
            ) and git.changed_since_split(self.root, main_tip, tips[ref], paths)

        def contains(a: str | None, b: str) -> bool:
            return a is not None and git.is_ancestor(self.root, b, a)

        provisional = isinstance(task_id.number, str) and bool(
            self._working_ticket_files(task_id) or self._ref_ticket_files(main_ref, task_id)
        )
        source = ticket_source(
            task_id,
            provisional,
            self._current_branch(),
            main,
            main_tip,
            local,
            remote,
            contains,
            changed_on_both,
        )
        return full_ref(source) if source != WORKING_TREE else WORKING_TREE

    def ticket_ids(self) -> set[TaskId]:
        if self._ticket_ids is None:
            self._ticket_ids = self._collect_ticket_ids()
        return set(self._ticket_ids)

    def exists(self, task_id: TaskId) -> bool:
        return task_id in self.ticket_ids()

    def _collect_ticket_ids(self) -> set[TaskId]:
        result = set(self._working_ticket_index())
        files_by_ref = self._ref_files()
        if not files_by_ref:
            return result
        main = self._main_branch()
        main_ref = f"refs/heads/{main}"
        for ref, ref_files in files_by_ref.items():
            own_id = None if ref == main_ref else TaskId.parse(ref.rsplit("/", 1)[-1].upper())
            for path, _content in ref_files:
                parts = path.parts
                if not (len(parts) == 3 or (len(parts) == 4 and parts[2] == ARCHIVE_DIR)):
                    continue
                if parts[0] != BACKLOG_DIR or ids.is_hidden_entry(path.name):
                    continue
                try:
                    task_id, _ = ids.parse_filename(path.name)
                except ids.IdError as error:
                    if own_id is None:
                        raise ChittyError(f"{main}:{path}: {error}") from None
                    continue
                if own_id is None or task_id == own_id:
                    result.add(task_id)
        return result

    def _ref_files(self) -> dict[str, list[tuple[Path, str]]]:
        if self._ticket_ref_files is not None:
            return self._ticket_ref_files
        if not self._is_repository():
            self._ticket_ref_files = {}
            return self._ticket_ref_files
        main_ref = f"refs/heads/{self._main_branch()}"
        refs: dict[str, str] = {}
        main_tip = self._main_tip()
        if main_tip is not None:
            refs[main_ref] = main_tip
        prefixes = {context.prefix for context in self.contexts()}
        for ref, tip in self._branch_tips().items():
            if ref.startswith("refs/heads/"):
                name = ref.removeprefix("refs/heads/")
            elif ref.startswith("refs/remotes/"):
                name = ref.removeprefix("refs/remotes/").partition("/")[2]
            else:
                continue
            try:
                task_id = TaskId.parse(name.upper())
            except ids.IdError:
                continue
            if name == str(task_id).lower() and task_id.prefix in prefixes and ref != main_ref:
                refs[ref] = tip

        self._ticket_ref_files = {
            ref: git.files_at(self.root, tip, (Path(BACKLOG_DIR),)) for ref, tip in refs.items()
        }
        return self._ticket_ref_files

    def all_tasks(self) -> list[StoredTask]:
        """List active and archived tickets in configured contexts, or `[]` if none.

        `_tasks_in_location` supplies the cached or parsed working-tree and
        history results; its listing errors propagate.
        """
        return [t for context in self.contexts() for t in self.tasks(context, "all")]

    def lookup(self, task_id: TaskId) -> StoredTask | None:
        """Wrap the parsed `source_copy` as a stored task, or return `None` if absent.

        `source_copy` handles source selection and parsing; its errors propagate.
        """
        return self._stored_task(task_id, self.source_copy(task_id))

    def _working_task(self, task_id: TaskId) -> StoredTask | None:
        copy = self._parse_source_copy(task_id, WORKING_TREE, self._working_ticket_files(task_id))
        return self._stored_task(task_id, copy)

    def _stored_task(self, task_id: TaskId, copy: SourceCopy | None) -> StoredTask | None:
        if copy is None:
            return None
        return StoredTask(
            task_id,
            copy.path.parts[1],
            self.root / copy.path,
            copy.path.parts[2] == ARCHIVE_DIR,
            copy.task,
            copy.ref,
        )

    def children_of(self, parent: TaskId) -> tuple[list[TaskId], list[tuple[TaskId, ChittyError]]]:
        """Return readable children in configured contexts and per-candidate errors."""
        by_context: dict[str, list[TaskId]] = {context.name: [] for context in self.contexts()}
        errors: list[tuple[TaskId, ChittyError]] = []
        for task_id in sorted(self.ticket_ids() - {parent}):
            try:
                ref, files = self._source_files(task_id)
                if not any(path.parts[1] in by_context for path, _ in files):
                    continue
                copy = self._parse_source_copy(task_id, ref, files)
            except ChittyError as error:
                errors.append((task_id, error))
                continue
            assert copy is not None  # The source has at least one configured file.
            reference = copy.task.frontmatter.parent
            if reference is not None and TaskId.parse(reference) == parent:
                by_context[copy.path.parts[1]].append(task_id)
        return [task_id for children in by_context.values() for task_id in children], errors

    def referenced_tasks(
        self, stored: StoredTask
    ) -> list[tuple[TaskId, StoredTask | ChittyError | None]]:
        prefixes = [context.prefix for context in self.contexts()]
        text = "\n".join(
            [
                stored.task.section(DESCRIPTION) or "",
                *(criterion.text for criterion in stored.task.criteria),
            ]
        )
        references: list[tuple[TaskId, StoredTask | ChittyError | None]] = []
        for task_id in ids.ticket_references(text, prefixes):
            if task_id != stored.id:
                try:
                    result = self.lookup(task_id)
                except ChittyError as error:
                    references.append((task_id, error))
                else:
                    references.append((task_id, result))
        return references

    def find(self, task_id: TaskId) -> StoredTask:
        """Return the parsed ticket from `lookup`, or raise if absent.

        On a miss, use `context_of` to report `no task <id> in <directory>`.
        Errors from either helper propagate, including a missing context.
        """
        task = self.lookup(task_id)
        if task is None:
            context = self.context_of(task_id)
            raise ChittyError(f"no task {task_id} in {context.directory}")
        return task

    def for_human_edit(self, task_id: TaskId) -> "Repo":
        """Select the worktree containing the latest task version, if any."""
        branch = self.find(task_id).branch
        if branch is None or branch == self._current_branch():
            return self
        worktree = git.worktree_for_branch(self.root, branch)
        return Repo.open(worktree) if worktree is not None else self

    def check_dependencies(self, references: Sequence[str]) -> None:
        for reference in references:
            task_id = TaskId.parse(reference)
            if not self.exists(task_id):
                raise ChittyError(f"no task {task_id} in {self.context_of(task_id).directory}")

    # -- writing ---------------------------------------------------------
    #
    # Each public write commits its own paths when autocommit is on.

    def prepare_write(self) -> None:
        """Enforce the repository setup policy before any mutation."""
        self._prepare_write()

    def _prepare_write(self) -> None:
        self._check_setup_version()
        if self.config.autocommit:
            if shutil.which("git") is None:
                raise ChittyError(
                    "autocommit requires Git, but `git` was not found on PATH; "
                    "install Git or set `autocommit = false`"
                )
            if not git.is_repository(self.root):
                raise ChittyError(
                    f"autocommit requires {self.root} to be in a Git work tree; "
                    "run `git init` or set `autocommit = false`"
                )
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
            with locks.main_checkout_lock(self.root):
                init_repo(self.root, False, "chitty: upgrade repository setup")
        except ManagedGuideError as error:
            print(
                f"warning: {error}; skipping repository setup upgrade until the marker lines "
                "are repaired",
                file=sys.stderr,
            )
            return
        self.config = load_repo_config(self.root)

    def refresh_setup(self) -> None:
        """Refresh setup before running Pi, without changing ticket branches."""
        # `run` may be invoked from a ticket worktree; setup belongs on main.
        if git.is_linked_worktree(self.root):
            return
        self._check_setup_version()
        with locks.main_checkout_lock(self.root):
            protected = (CONFIG_NAME, "pyproject.toml", AGENTS_FILE, ".gitignore")
            dirty = [name for name in protected if git.dirty_paths(self.root, Path(name))]
            if dirty:
                raise ChittyError(
                    "repository setup files have uncommitted changes; commit or stash these first: "
                    + ", ".join(dirty)
                )
            paths = init_repo(
                self.root,
                False,
                "chitty: upgrade repository setup" if git.is_repository(self.root) else None,
            )
            for path in paths:
                print(path, file=sys.stderr)
        self.config = load_repo_config(self.root)

    def _check_setup_version(self) -> None:
        check_setup_version(self.config)

    @contextmanager
    def _all_or_nothing(self) -> Generator[None, None, None]:
        main_checkout = git.is_repository(self.root) and not git.is_linked_worktree(self.root)
        lock = locks.main_checkout_lock(self.root) if main_checkout else nullcontext()
        with lock:
            before = _task_file_bytes(self.contexts())
            index = _git_index_path(self.root) if git.is_repository(self.root) else None
            index_before = index.read_bytes() if index and index.exists() else None
            try:
                yield
            except BaseException:
                _restore_task_files(self.contexts(), before)
                if index is not None:
                    if index_before is None:
                        index.unlink(missing_ok=True)
                    else:
                        index.write_bytes(index_before)
                self._invalidate()
                raise

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
        if self.config.contexts[context.name].random_ids:
            fields["status"] = "backlog"
        depends_on = fields.get("depends_on")
        if isinstance(depends_on, list):
            fields["depends_on"] = self._references(depends_on)
            self.check_dependencies(fields["depends_on"])
        parent = fields.get("parent")
        if isinstance(parent, str):
            fields["parent"] = str(self.resolve(parent))
            self.check_dependencies([fields["parent"]])
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
            task = task.with_note(escape_literal_asterisks(note))
        task_id, provisional = self.new_id(context)
        task = task.with_field("provisional", True if provisional else None)
        path = context.directory / ids.filename(task_id, ids.slugify(title))
        with self._all_or_nothing():
            self._write(path, task.render())
            stored = StoredTask(task_id, context.name, path, False, task)
            return self._commit(Change(stored, (path,), (stored,)), "add")

    def planning_branch(self) -> str | None:
        if shutil.which("git") is None:
            return None  # Preserve the usual command-specific Git prerequisite errors.
        branch = self._current_branch()
        if branch is None or branch == self._main_branch():
            return None
        try:
            task_id = TaskId.parse(branch)
        except ids.IdError:
            return branch
        return None if branch == str(task_id).lower() else branch

    def find_for_show(self, task_id: TaskId) -> StoredTask:
        if self.planning_branch() and (draft := self._working_task(task_id)) is not None:
            return draft
        return self.find(task_id)

    def _reject_planning_conflicts(self, task_id: TaskId, branch: str) -> None:
        tips = git.branch_tips(self.root)
        local_ref = f"refs/heads/{branch}"
        current = tips.get(local_ref)
        if current is None:
            raise ChittyError(f"planning branch {branch} has no committed tip")
        for ref, tip in sorted(tips.items()):
            remote_branch = ref.removeprefix("refs/remotes/").partition("/")[2]
            if ref == local_ref or (ref.startswith("refs/remotes/") and remote_branch == branch):
                continue
            base = git.common_ancestor(self.root, current, tip)
            if base is None or base == tip:
                continue
            for path in git.changed_paths(self.root, base, tip):
                parts = path.parts
                if not parts or parts[0] != BACKLOG_DIR:
                    continue
                if not (len(parts) == 3 or (len(parts) == 4 and parts[2] == ARCHIVE_DIR)):
                    continue
                try:
                    changed_id, _ = ids.parse_filename(path.name)
                except ids.IdError:
                    continue
                if changed_id == task_id:
                    raise ChittyError(f"planning edit for {task_id} conflicts with {ref}")

    def _branch_task(self, task_id: TaskId, branch: str) -> StoredTask:
        draft = self._working_task(task_id)
        if draft is None:
            raise ChittyError(f"no local draft for {task_id} in {self.root / BACKLOG_DIR}")
        self._reject_planning_conflicts(task_id, branch)
        return draft

    def edit_current(self, task_id: TaskId, edit: Edit) -> tuple[Change, bool]:
        if branch := self.planning_branch():
            return self.edit_planning(task_id, edit, branch)
        return self.edit(task_id, edit), False

    def edit_planning(self, task_id: TaskId, edit: Edit, branch: str) -> tuple[Change, bool]:
        draft = self._branch_task(task_id, branch)
        active = locks.holder(self.root, str(task_id)) is not None
        self._prepare_write()
        if edit.is_empty():
            raise ChittyError("nothing to change")
        return self._edit_stored(draft, edit), active

    def edit(self, task_id: TaskId, edit: Edit) -> Change:
        """Apply an edit. References in depends_on may be shorthand."""
        self._prepare_write()
        if edit.is_empty():
            raise ChittyError("nothing to change")
        return self._edit_stored(self.find(task_id), edit)

    def _edit_stored(self, stored: StoredTask, edit: Edit) -> Change:
        task_id = stored.id
        if stored.context not in self.config.contexts:
            raise ChittyError(f"cannot write ticket in unconfigured context {stored.context!r}")
        previous_status = stored.task.frontmatter.status
        if (
            edit.status is not None
            and edit.status != "backlog"
            and self.config.contexts[stored.context].random_ids
        ):
            raise ChittyError(
                f"{task_id} is in a random-ID context; "
                f"run `chitty move {task_id} tasks` to promote it"
            )
        if (
            edit.status == "done"
            and edit.status != previous_status
            and self.review_required(self.context(stored.context))
            and previous_status != "review"
        ):
            if previous_status != "error" or not edit.human:
                raise ChittyError("setting status done requires -s review first")
            if not any(note and note.strip() for note in (edit.note, *edit.notes)):
                raise ChittyError("moving error → done requires --note with the reason")
        def require_clean() -> None:
            if uncommitted := git.uncommitted_paths(self.root):
                listed = ", ".join(f"`{path}`" for path in uncommitted)
                raise ChittyError(
                    f"cannot move {task_id} to {edit.status}; the worktree has "
                    f"uncommitted changes: {listed}. Commit or resolve them "
                    "before changing status"
                )

        leaving_doing = (
            previous_status == "doing"
            and edit.status is not None
            and edit.status not in ("doing", "review")
            and not edit.skip_current_version
            and self._current_branch() == str(task_id).lower()
        )
        if leaving_doing:
            require_clean()
        entering_review = edit.status == "review" and previous_status != "review"
        passing_review = previous_status == "review" and edit.status == "done"
        if (
            (entering_review or passing_review)
            and (self.root / ".git").exists()
            and not edit.skip_current_version
        ):
            self._require_current_version(stored)

            require_clean()
            skip_check = (
                entering_review
                and self.config.check
                and self.config.workflow == "runner"
                and git.is_ancestor(self.root, "HEAD", self._main_branch())
            )
            if skip_check:
                print(f"skipped check: HEAD is already on {self._main_branch()}", file=sys.stderr)
            if entering_review and self.config.check and not skip_check:
                command = self.config.check
                print(f"running check {command} before review (output in .chitty/check.log)", file=sys.stderr)
                start = time.monotonic()
                try:
                    status = commands.run_logged(
                        "check", command, self.root, self.config.command_timeout
                    )
                except commands.CommandTimedOut as error:
                    raise ChittyError(f"cannot move {task_id} to review; {error}") from error
                except FileNotFoundError as error:
                    raise ChittyError(
                        f"cannot move {task_id} to review; check command not found: {command}"
                    ) from error
                print(f"check finished in {int(time.monotonic() - start)}s", file=sys.stderr)
                if status:
                    raise ChittyError(
                        f"cannot move {task_id} to review; check failed with status {status}; "
                        "output in `.chitty/check.log`"
                    )
                require_clean()
                self._require_current_version(stored)
        if edit.replace_in_description:
            if edit.description is not None:
                raise ChittyError("--replace-in-description cannot be combined with --description")
            if any(not old for old, _ in edit.replace_in_description):
                raise ChittyError("--replace-in-description OLD cannot be empty")
            replace_pairs(stored.task.section(DESCRIPTION) or "", edit.replace_in_description)
        edit = check_edit(stored.task, edit, actor())
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
        with self._all_or_nothing():
            change = replace(
                self._save(stored, task, allow_stale=edit.skip_current_version),
                actor=actor_name,
                previous_status=previous_status,
            )
            return self._commit(change, "edit")

    def _save(self, stored: StoredTask, task: Task, *, allow_stale: bool = False) -> Change:
        """Write an edited task; touches nothing if the content is unchanged."""
        # Guard every shared-store write so CLI and MCP cannot fork a task differently.
        if not allow_stale:
            self._require_current_version(stored)
        if task.frontmatter.depends_on != stored.task.frontmatter.depends_on:
            self.check_dependencies(task.frontmatter.depends_on)
        if task.frontmatter.parent and task.frontmatter.parent != stored.task.frontmatter.parent:
            self.check_dependencies([task.frontmatter.parent])
        path = stored.path
        if task.frontmatter.title != stored.task.frontmatter.title:
            target = path.with_name(ids.filename(stored.id, ids.slugify(task.frontmatter.title)))
            if target != path:
                if target.exists():
                    raise ChittyError(f"cannot rename {path} to {target}: destination exists")
                git.move(self.root, path, target)
                self._invalidate()
                path = target
        updated = StoredTask(stored.id, stored.context, path, stored.archived, task)
        if task.render() == stored.task.render():
            return Change(updated, (), ())
        self._write(path, task.render())
        paths = (stored.path, path) if path != stored.path else (path,)
        return Change(updated, paths, (updated,))

    def new_id(self, context: Context) -> tuple[TaskId, bool]:
        """Choose an ID appropriate to the context and current Git checkout."""
        if self.config.contexts[context.name].random_ids:
            return TaskId(context.prefix, self.next_number(context)), False
        if git.is_repository(self.root):
            main_branch = self._main_branch()
            if self._current_branch() != main_branch:
                if not git.has_branch_ref(self.root, main_branch):
                    raise ChittyError(
                        f"main branch {main_branch!r} has no ref; "
                        "configure main_branch in chitty.toml"
                    )
                used = {
                    task_id.number
                    for task_id in self.ticket_ids()
                    if task_id.prefix == context.prefix and isinstance(task_id.number, str)
                }
                for _ in range(RANDOM_ID_ATTEMPTS):
                    task_id = TaskId(context.prefix, ids.provisional_suffix(_provisional_draw))
                    if task_id.number not in used:
                        return task_id, True
                raise ChittyError(
                    f"no unused provisional ID in context {context.name} "
                    f"after {RANDOM_ID_ATTEMPTS} attempts"
                )
        return TaskId(context.prefix, self.next_number(context)), False

    def _prepare_renumbering(
        self, mapping: dict[TaskId, TaskId], writable: tuple[StoredTask, ...]
    ) -> list[tuple[StoredTask, Task, Path]]:
        result: list[tuple[StoredTask, Task, Path]] = []
        for stored in writable:
            final = rewrite_task(stored.task, mapping)
            if stored.id in mapping:
                final = final.with_field("provisional", None).with_field(
                    "moved_from", str(stored.id)
                )
                final = final.with_history_event(
                    datetime.now(UTC), actor(), f"renumbered from {stored.id}"
                )
            final_id = mapping.get(stored.id, stored.id)
            path = stored.path
            if final_id != stored.id or final.frontmatter.title != stored.task.frontmatter.title:
                path = path.with_name(ids.filename(final_id, ids.slugify(final.frontmatter.title)))
            if final.render() != stored.task.render() or path != stored.path:
                result.append((stored, final, path))
        return result

    def _plan_provisional_renumbering(self) -> tuple[dict[TaskId, TaskId], tuple[StoredTask, ...]]:
        """Select writable disk tickets and allocate fresh sequential IDs without writing."""
        if git.is_repository(self.root):
            branch = git.current_branch(self.root)
            main = self._main_branch()
            if branch != main:
                raise ProvisionalOffMain(
                    f"provisional tickets are renumbered on {main}; "
                    f"current branch is {branch or 'detached HEAD'}"
                )
        sequential = {
            context.name: context
            for context in self.contexts()
            if not self.config.contexts[context.name].random_ids
        }
        disk_paths: list[Path] = []
        disk_entries: list[tuple[Context, Path, bool]] = []
        writable: list[StoredTask] = []
        candidates: list[TaskId] = []
        for context in self.discovered_contexts():
            for archived in (False, True):
                for path in self._files(context, archived):
                    disk_paths.append(path)
                    disk_entries.append((context, path, archived))
                    if context.name not in self.config.contexts:
                        continue
                    task_id, _ = ids.parse_filename(path.name)
                    if self.source_of(task_id) is not None:
                        continue
                    stored = self._load(context, path, archived)
                    writable.append(stored)
                    if context.name in sequential and stored.task.frontmatter.provisional:
                        candidates.append(task_id)
        if not candidates:
            return {}, ()

        seen: dict[TaskId, Path] = {}
        candidate_ids = set(candidates)
        for path in disk_paths:
            task_id, _ = ids.parse_filename(path.name)
            if task_id in candidate_ids:
                if task_id in seen:
                    raise ChittyError(
                        f"{task_id} is used by more than one file: {seen[task_id]}, {path}"
                    )
                seen[task_id] = path

        used = {context.prefix: self._used_numbers(context) for context in sequential.values()}
        self._reserve_numbers(used, self.ticket_ids())
        for path in disk_paths:
            self._reserve_numbers(used, ids.ticket_references(path.read_text(), used.keys()))
        mapping = plan_renumbering(used, candidates)
        self._guard_untouched_disk_links(disk_entries, {item.path for item in writable}, mapping)
        self._guard_ref_links(mapping)
        return mapping, tuple(writable)

    def _guard_untouched_disk_links(
        self,
        entries: list[tuple[Context, Path, bool]],
        writable: set[Path],
        mapping: dict[TaskId, TaskId],
    ) -> None:
        for context, path, archived in entries:
            if path in writable:
                continue
            stored = self._load(context, path, archived)
            link = blocking_link(stored.task.frontmatter, mapping)
            if link is not None:
                old, field = link
                raise ChittyError(f"cannot renumber {old}: {stored.id} links to it in {field}")

    def _guard_ref_links(self, mapping: dict[TaskId, TaskId]) -> None:
        for task_id in sorted(self.ticket_ids()):
            if self.source_of(task_id) is None:
                continue
            stored = self.lookup(task_id)
            if stored is None:
                continue
            link = blocking_link(stored.task.frontmatter, mapping)
            if link is not None:
                old, field = link
                raise ChittyError(f"cannot renumber {old}: {stored.id} links to it in {field}")

    @staticmethod
    def _reserve_numbers(used: dict[str, set[int]], references: Iterable[TaskId]) -> None:
        for task_id in references:
            if task_id.prefix in used and isinstance(task_id.number, int):
                used[task_id.prefix].add(task_id.number)

    def _used_numbers(self, context: Context) -> set[int]:
        numbers = {
            number
            for archived in (False, True)
            for p in self._files(context, archived)
            if isinstance(number := ids.parse_filename(p.name)[0].number, int)
        }
        if self.config.archive == "delete":
            numbers.update(self._deleted_numbers(context))
        return numbers

    def next_number(self, context: Context) -> int:
        used = self._used_numbers(context)
        if self.config.contexts[context.name].random_ids:
            for _ in range(RANDOM_ID_ATTEMPTS):
                if (number := _random_number()) not in used:
                    return number
            raise ChittyError(
                f"no unused random number in context {context.name!r} "
                f"after {RANDOM_ID_ATTEMPTS} attempts"
            )
        if git.is_repository(self.root) and self._current_branch() != self._main_branch():
            raise ChittyError("sequential ticket numbers can only be allocated on main")
        return ids.next_number(used)

    def archive_current(self, task_id: TaskId) -> Change:
        branch = self.planning_branch()
        if branch is None:
            return self.archive(task_id)
        if self.config.archive == "delete":
            raise ChittyError('archiving on a branch needs archive = "move"')
        stored = self._branch_task(task_id, branch)
        self._prepare_write()
        with self._all_or_nothing():
            return self._commit(self._set_archived(stored, True), "archive")

    def archive(self, task_id: TaskId) -> Change:
        self._prepare_write()
        with self._all_or_nothing():
            change = self._archive(task_id)
            return self._commit(change, "delete" if self.config.archive == "delete" else "archive")

    def renumber_provisional(self) -> tuple[Change, ...]:
        mapping, writable = self._plan_provisional_renumbering()
        if not mapping:
            return ()
        self._prepare_write()
        prepared = self._prepare_renumbering(mapping, writable)
        with self._all_or_nothing():
            for _, task, path in prepared:
                self._write(path, task.render())
            for old, _, path in prepared:
                if old.path != path:
                    old.path.unlink()
            self._invalidate()
            final = tuple(
                StoredTask(mapping.get(old.id, old.id), old.context, path, old.archived, task)
                for old, task, path in prepared
            )
            changes = tuple(
                Change(task, (old.path, path) if old.path != path else (path,), (task,))
                for (old, _, path), task in zip(prepared, final, strict=True)
                if old.id in mapping
            )
            paths = tuple(
                p
                for old, _, path in prepared
                for p in ((old.path, path) if old.path != path else (path,))
            )
            self._commit(Change(changes[0].task, paths, final), "renumber provisional tickets")
            return changes

    def archive_done(self) -> tuple[Change, ...]:
        """Archive every non-archived done task in one finalization."""
        self._prepare_write()
        with self._all_or_nothing():
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
            stored = self.find(task_id)
            self._require_current_version(stored)
            return self._set_archived(stored, True)
        return self._delete_done(task_id)

    def _deleted_numbers(self, context: Context) -> list[int]:
        numbers: list[int] = []
        directory = Path(BACKLOG_DIR) / context.name
        for path in git.deleted_paths(self.root):
            try:
                task_id, _ = ids.parse_filename(path.name)
            except ids.IdError:
                continue
            if (
                task_id.prefix == context.prefix
                and directory in path.parents
                and isinstance(task_id.number, int)
            ):
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
        with self._all_or_nothing():
            stored = self.find(task_id)
            self._require_current_version(stored)
            return self._commit(self._set_archived(stored, False), "restore")

    def move(self, task_id: TaskId, target: Context) -> Change:
        """Give a task the next ID in another context and rewrite references to it."""
        self._prepare_write()
        stored = self.find(task_id)
        self._require_current_version(stored)
        if target.name == stored.context:
            raise ChittyError(f"{task_id} is already in context {target.name!r}")
        new_id, provisional = self.new_id(target)
        directory = target.archive_directory if stored.archived else target.directory
        old, new = str(task_id), str(new_id)
        moved_task = stored.task.with_field(
            "depends_on", _replace(stored.task.frontmatter.depends_on, old, new)
        )
        if moved_task.frontmatter.parent == old:
            moved_task = moved_task.with_field("parent", new)
        if (
            self.config.contexts[target.name].random_ids
            and moved_task.frontmatter.status != "backlog"
        ):
            moved_task = moved_task.with_history(
                datetime.now(UTC), actor(), moved_task.frontmatter.status, "backlog"
            )
            moved_task = moved_task.with_field("status", "backlog")
        moved_task = moved_task.with_field("provisional", True if provisional else None)
        with self._all_or_nothing():
            moved = self._relocate(stored, new_id, target, directory, moved_task)
            touched = [stored.path, moved.path]
            changes: list[Change] = []
            for other in self.all_tasks():
                task = other.task
                if old not in task.frontmatter.depends_on and task.frontmatter.parent != old:
                    continue
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
        new_id, provisional = self.new_id(context)
        task = stored.task.with_field("provisional", True if provisional else None)
        with self._all_or_nothing():
            renumbered = self._relocate(stored, new_id, context, directory, task)
            change = self._commit(
                Change(renumbered, (stored.path, renumbered.path), (renumbered,)), "renumber"
            )
            old = str(task_id)
            references = tuple(
                other
                for other in self.all_tasks()
                if other.id != new_id
                and (
                    old in other.task.frontmatter.depends_on or other.task.frontmatter.parent == old
                )
            )
            return change, references

    def _locate_task_file(self, path: Path) -> tuple[Context, bool, Path]:
        """The context, archive flag and scanned path of a task file, without collapsing IDs."""
        for context in self.discovered_contexts():
            for archived in (False, True):
                for candidate, problem in scan(context, archived, allow_any_prefix=True):
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
        self._invalidate()
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
            # The task file is temporarily dirty until its autocommit below;
            # validate content here, but leave worktree cleanliness to `chitty check`.
            if task_paths:
                _, problems = fix(self, self.contexts(), task_paths, include_worktree_state=False)
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
        self._invalidate()
        return change

    def _references(self, references: Sequence[str]) -> list[str]:
        return [str(self.resolve(reference)) for reference in dict.fromkeys(references)]

    def _set_archived(self, stored: StoredTask, archived: bool) -> Change:
        task_id = stored.id
        if stored.archived == archived:
            state = "archived" if archived else "not archived"
            raise ChittyError(f"{task_id} is already {state}")
        if stored.context not in self.config.contexts:
            raise ChittyError(f"cannot write ticket in unconfigured context {stored.context!r}")
        context = self.context(stored.context)
        directory = context.archive_directory if archived else context.directory
        new_path = directory / stored.path.name
        directory.mkdir(parents=True, exist_ok=True)
        state = "archived" if archived else stored.task.frontmatter.status
        previous = stored.task.frontmatter.status if archived else "archived"
        actor_name = actor()
        task = stored.task.with_history(datetime.now(UTC), actor_name, previous, state)
        stored.path.rename(new_path)
        self._invalidate()
        self._write(new_path, task.render())
        moved = StoredTask(stored.id, stored.context, new_path, archived, task)
        return Change(moved, (stored.path, new_path), (moved,), actor_name)

    def _require_current_version(self, stored: StoredTask) -> None:
        branch = stored.branch
        if branch is None or branch == self._current_branch():
            return
        own = str(stored.id).lower()
        if self._current_branch() == own and branch == self._main_branch():
            main_ref = f"refs/heads/{branch}"
            own_ref = f"refs/heads/{own}"
            paths = sorted(
                {
                    path
                    for ref in (main_ref, own_ref)
                    for path, _ in self._ref_ticket_files(ref, stored.id)
                }
            )
            if not git.changed_since_split(self.root, main_ref, own_ref, paths):
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
        for path, problem in scan(context, archived, allow_any_prefix=True):
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
        self._invalidate()


VERDICT_LINE_RE = re.compile(r"^(\d+): (pass|fail) - (\S.*)$")


def check_edit(task: Task, edit: Edit, reviewer: str) -> Edit:
    """Validate an edit that depends only on the current task and its actor."""
    previous_status = task.frontmatter.status
    if edit.set_notes is not None and (edit.note is not None or edit.notes):
        raise ChittyError("--set-notes cannot be combined with --note or --note-file")
    if previous_status == "review" and edit.set_notes is not None:
        raise ChittyError("--set-notes is not allowed while a task is in review")
    if previous_status == "review":
        for criteria, option in (
            (edit.add_criteria, "--ac"),
            (edit.rm_criteria, "--rm-ac"),
            (edit.set_criteria, "--set-ac"),
        ):
            if criteria:
                raise ChittyError(f"{option} is not allowed while a task is in review")
    if edit.status == "blocked" and not (edit.note or edit.notes):
        raise ChittyError("setting status blocked requires --note with the reason")
    returning_to_planning = previous_status in {"doing", "review"} and edit.status == "planning"
    if returning_to_planning and not any(
        note and note.strip() for note in (edit.note, *edit.notes)
    ):
        raise ChittyError(f"moving {previous_status} → planning requires --note with the reason")
    is_review_transition = previous_status == "review" and edit.status in {
        "doing",
        "done",
        "planning",
    }
    if edit.status == "doing" and is_review_transition and not (edit.note or edit.notes):
        raise ChittyError("moving review → doing requires --note with the reason")
    if (
        edit.status == "done"
        and previous_status == "review"
        and not any(note.startswith("Reviewed:") for note in (edit.note, *edit.notes) if note)
    ):
        raise ChittyError("moving review → done requires --note starting 'Reviewed:'")
    if is_review_transition and not edit.skip_verdicts:
        _validate_review_verdict(task, edit)
    if edit.override_review_independence and not is_review_transition:
        raise ChittyError("--override-review-independence only applies to review transitions")
    if is_review_transition:
        work = task.review_work(reviewer)
        if work and not edit.override_review_independence:
            raise ChittyError(
                f"{reviewer} cannot review this task: {', '.join(work)}; "
                "leave the review to another agent"
            )
    if edit.status == "doing" and previous_status in {"review", "done"}:
        return _escalate_repeated_failure(task, edit)
    if returning_to_planning:
        returns = _count_since_block(task, {("doing", "planning"), ("review", "planning")})
        if returns >= PLANNING_RETURN_LIMIT:
            reason = (
                f"Escalated to human review: returned to planning {returns} times. "
                "A human should decide how to proceed, then unblock it."
            )
            return _escalate(edit, reason, f"Returned to planning {returns} times")
        return replace(edit, owner="")
    return edit


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
            + ". Give each criterion one such line in the note"
        )

    verdict_by_number = {number: verdict for number, verdict in verdicts}
    if edit.status == "done" and any(verdict == "fail" for verdict in verdict_by_number.values()):
        raise ChittyError("moving review → done requires every verdict to be pass")
    if edit.status in {"doing", "planning"} and not any(
        verdict == "fail" for verdict in verdict_by_number.values()
    ):
        raise ChittyError(f"moving review → {edit.status} requires at least one fail verdict")


def _escalate_repeated_failure(task: Task, edit: Edit) -> Edit:
    """Turn the limit-th failed review since the last block into a block for a human."""
    failures = _count_since_block(task, {("review", "doing"), ("done", "doing")})
    if failures < REVIEW_FAILURE_LIMIT:
        return edit
    reason = (
        f"Escalated to human review: failed review {failures} times. "
        "A human should decide how to proceed, then unblock it."
    )
    return _escalate(edit, reason, f"Failed review {failures} times")


def _count_since_block(task: Task, transitions: set[tuple[str, str]]) -> int:
    count = 1
    for old, new in reversed(task.transitions()):
        if new == "blocked":
            break
        count += (old, new) in transitions
    return count


def _escalate(edit: Edit, reason: str, summary: str) -> Edit:
    first_line = next(
        (line.strip() for note in (edit.note, *edit.notes) if note
         for line in note.splitlines() if line.strip()),
        "",
    )
    if first_line:
        summary += f": {first_line}"
    return replace(
        edit, status="blocked", owner="human", notes=(*edit.notes, reason),
        summary=edit.summary or summary,
    )


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
    if name:
        return Target(local, local.context(name))
    return Target(local, local.default_context)


def managed_guide(workflow: str) -> str:
    """Return the general guide for a workflow: tickets-only, or the runner too."""
    tickets = files("chitty").joinpath("guide.md").read_text()
    if workflow == "tickets":
        return tickets
    if workflow == "runner":
        return f"{tickets}\n{files('chitty').joinpath('guide-runner.md').read_text()}"
    raise ChittyError(f"unknown workflow {workflow!r}; choose from tickets, runner")


def repository_guide(start_dir: Path) -> str:
    """Return the general guide for the repository found from `start_dir`."""
    root = search_root(start_dir)
    # Outside any repository there is no workflow setting, so keep the full guide.
    workflow = "runner" if root is None else load_repo_config(root).workflow
    return managed_guide(workflow)


def guide(role: str, ticket_id: str | None = None, *, directory: Path, workflow: str) -> str:
    """Return prefix-independent role-specific agent guidance."""
    if role not in ROLE_NAMES:
        raise ChittyError(f"unknown role {role!r}; choose from {', '.join(ROLE_NAMES)}")
    if workflow != "runner":
        raise ChittyError(runner_required_message(f"guide {role}"))
    if ticket_id is not None and role in {"plan", "setup"}:
        raise ChittyError(f"the {role} role does not take a ticket ID")

    roles = files("chitty").joinpath("roles")
    text = roles.joinpath(f"{role}.md").read_text()
    signals = roles.joinpath("property-signals.md").read_text().rstrip()
    text = text.replace("<!-- property-signals -->", signals)
    if (
        ticket_id is not None
        and role in {"work", "repair"}
        and git.is_repository(directory)
        and git.rebase_in_progress(directory)
    ):
        rebase = roles.joinpath("rebase.md").read_text().rstrip()
        return f"Work only on Chitty ticket {ticket_id}.\n\n{rebase}\n\n{text}"
    return f"Work only on Chitty ticket {ticket_id}.\n\n{text}" if ticket_id is not None else text


def _default_project(directory_name: str) -> str:
    project = re.sub(r"[^a-z0-9]+", "-", directory_name.lower()).strip("-")
    if not project:
        raise ChittyError(
            'cannot derive a project name; choose a valid directory name or set project = "name" '
            "in configuration before running init"
        )
    return project


def add_runner_workflow(text: str, recorded_version: str | None, pyproject: bool) -> str:
    if pyproject:
        header = re.search(r"(?m)^\[tool\.chitty\][ \t]*$", text)
        if header is None:
            return text
        following = re.search(r"(?m)^\[", text[header.end() :])
        end = header.end() + following.start() if following else len(text)
        start = header.end()
    else:
        following = re.search(r"(?m)^\[", text)
        start, end = 0, following.start() if following else len(text)
    section = text[start:end]
    if re.search(r"(?m)^[ \t]*workflow[ \t]*=", section):
        return text
    if resolve_workflow(None, recorded_version) != "runner":
        return text
    version = re.search(r"(?m)^[ \t]*chitty_version[ \t]*=", section)
    if version is None:
        raise ChittyError("cannot add workflow: Chitty section has no chitty_version line")
    line_end = text.find("\n", start + version.start())
    if line_end < 0 or line_end >= end:
        return text + '\nworkflow = "runner"\n'
    insertion = line_end + 1
    return text[:insertion] + 'workflow = "runner"\n' + text[insertion:]


def _add_missing_settings(
    text: str, settings: Mapping[str, object], pyproject: bool, project: str
) -> str:
    if pyproject:
        match = re.search(r"(?m)^\[tool\.chitty\]\s*$", text)
        assert match is not None
        following = re.search(r"(?m)^\[", text[match.end() :])
        position = match.end() + following.start() if following else len(text)
        section = text[match.end() : position]
    else:
        following = re.search(r"(?m)^\[", text)
        position = following.start() if following else len(text)
        section = text[:position]
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
                "check",
                '# check = "make check" # validate the ticket worktree before the agent starts',
            ),
            (
                "agent_command",
                ('# agent_command = "pi -p {prompt}"'),
            ),
            ("work_model", '# work_model = "provider/model" # default for work sessions'),
            ("review_model", '# review_model = "provider/model" # default for review sessions'),
            ("rebase_model", '# rebase_model = "provider/model" # default for rebase sessions'),
        )
        if key not in settings
        and not (key in {"setup", "check", "agent_command"} and f"{key} =" in text)
        and not (key in {"work_model", "review_model", "rebase_model"} and f"{key} =" in section)
    ]
    if not additions:
        return text
    return text[:position] + "\n".join(additions) + "\n\n" + text[position:]


def _add_missing_agent_commands_table(
    text: str, settings: Mapping[str, object], pyproject: bool
) -> str:
    if "agent_commands" in settings:
        return text
    prefix = "tool.chitty." if pyproject else ""
    return text.rstrip() + f"\n\n[{prefix}agent_commands]\n"


def _provisional_draw(n: int) -> int:
    return secrets.randbelow(n)


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


def _git_index_path(root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "index"],
        check=True,
        cwd=root,
        capture_output=True,
        text=True,
    )
    path = Path(result.stdout.strip())
    return (root / path).resolve() if not path.is_absolute() else path


def _task_file_bytes(contexts: Sequence[Context]) -> dict[Path, bytes]:
    return {
        path: path.read_bytes()
        for context in contexts
        for directory in (context.directory, context.archive_directory)
        if directory.exists()
        for path in directory.rglob("*.md")
        if path.is_file()
    }


def _restore_task_files(contexts: Sequence[Context], before: Mapping[Path, bytes]) -> None:
    current = _task_file_bytes(contexts)
    for path in current.keys() - before.keys():
        path.unlink()
    for path, content in before.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != content:
            path.write_bytes(content)


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


def managed_block(existing: str) -> str | None:
    """Return the managed guide block, including its delimiters."""
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
    if markers:
        begins = [item for item in markers if item[3] == GUIDE_BEGIN]
        ends = [item for item in markers if item[3] == GUIDE_END]
        if len(begins) != 1 or len(ends) != 1 or begins[0][0] >= ends[0][0]:
            raise ManagedGuideError("invalid Chitty guide markers")
        return existing[begins[0][1] : ends[0][2]]

    match = re.search(r"(?ms)^## Chitty\n.*?(?=^## |\Z)", existing)
    return match.group() if match else None


def _managed_agents(existing: str, agents: Path, workflow: str) -> str:
    """Return `AGENTS.md` with the exact managed guide block installed."""
    rendered = f"{GUIDE_BEGIN}\n\n{managed_guide(workflow).rstrip('\n')}\n\n{GUIDE_END}\n"
    try:
        block = managed_block(existing)
    except ManagedGuideError:
        raise ManagedGuideError(
            f"{agents} has invalid Chitty guide markers; remove the marker lines so the "
            "next `chitty init` can migrate the block"
        ) from None
    if block is not None:
        start = existing.index(block)
        if block.startswith(GUIDE_BEGIN):
            return existing[:start] + rendered + existing[start + len(block) :]
        # The legacy match includes the separator before a following heading.
        suffix = existing[start + len(block) :]
        separator = "\n" if suffix.startswith("## ") else ""
        print(f"migrated Chitty guide markers in {agents}", file=sys.stderr)
        return existing[:start] + rendered + separator + suffix
    return (existing.rstrip("\n") + "\n\n" if existing.strip() else "") + rendered


def init_repo(
    directory: Path, enable_autocommit: bool, commit_message: str | None
) -> list[Path]:
    """Create or non-destructively upgrade the repository's Chitty setup."""
    if git.is_linked_worktree(directory):
        main = git.main_checkout(directory)
        raise ChittyError(
            f"`chitty init` cannot run in linked worktree {directory}; "
            f"run it from the main checkout {main}"
        )
    if enable_autocommit:
        git.require_clean(directory)
    claude = directory / CLAUDE_FILE
    if claude.exists() and not claude.is_symlink():
        raise ChittyError(f"{claude} exists and must be replaced with a symlink to {AGENTS_FILE}")
    from chitty.config import inbox_path, load_repo_config, register_project

    config_path = directory / CONFIG_NAME
    pyproject_path = directory / "pyproject.toml"
    agents = directory / AGENTS_FILE
    gitignore = directory / ".gitignore"
    existing_agents = agents.read_text() if agents.exists() else ""
    has_pyproject_config = False
    if not config_path.exists() and pyproject_path.exists():
        pyproject_data = tomllib.loads(pyproject_path.read_text())
        tool = pyproject_data.get("tool")
        has_pyproject_config = isinstance(tool, Mapping) and "chitty" in tool
    # The block must match the workflow the config will have, so load it before
    # rendering. Damaged markers still raise here, before any file is written.
    if config_path.exists() or has_pyproject_config:
        workflow = load_repo_config(directory).workflow
    else:
        # A new config omits `workflow`, so it gets the default for this version.
        workflow = resolve_workflow(None, CHITTY_VERSION)
    updated_agents = _managed_agents(existing_agents, agents, workflow)
    originals = {
        path: _file_state(path) for path in (config_path, pyproject_path, agents, claude, gitignore)
    }
    created_directories: set[Path] = set()
    try:
        written: list[Path] = []
        if not config_path.exists() and not has_pyproject_config:
            project = _default_project(directory.name)
            text = INITIAL_CONFIG.format(project=json.dumps(project), version=CHITTY_VERSION)
            branch = git.current_branch(directory)
            if branch is not None and branch != "main":
                # New repositories preserve a non-main integration branch; existing
                # configs are upgrades and deliberately remain unchanged.
                project_line = f"project = {json.dumps(project)}\n"
                text = text.replace(
                    project_line,
                    f"{project_line}main_branch = {json.dumps(branch)}\n",
                    1,
                )
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
            recorded_version = settings.get("chitty_version")
            if recorded_version != CHITTY_VERSION:
                updated = add_runner_workflow(
                    updated,
                    recorded_version if isinstance(recorded_version, str) else None,
                    source == pyproject_path,
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
                missing: list[Path] = []
                parent = path
                while not parent.exists():
                    missing.append(parent)
                    parent = parent.parent
                created_directories.update(missing)
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
        if updated_agents != existing_agents:
            agents.write_text(updated_agents)
            written.append(agents)
        if claude.is_symlink() and claude.readlink() != Path(AGENTS_FILE):
            claude.unlink()
        if not claude.exists():
            claude.symlink_to(AGENTS_FILE)
            written.append(claude)
        committed = [
            path for path in written if path.is_relative_to(directory) and not path.is_dir()
        ]
        if commit_message is not None and committed:
            git.commit(directory, committed, commit_message)
        return written
    except BaseException:
        for path, state in originals.items():
            _restore_file(path, state)
        for path in sorted(created_directories, key=lambda item: len(item.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        raise


def ordered(tasks: Sequence[StoredTask], statuses: Sequence[str]) -> list[StoredTask]:
    """Order tasks by status, bug label, and priority, preserving source order for ties."""
    status_order = {status: index for index, status in enumerate(statuses)}
    return sorted(
        tasks,
        key=lambda stored: (
            status_order[stored.task.frontmatter.status],
            "bug" not in stored.task.frontmatter.labels,
            PRIORITY_ORDER[stored.task.frontmatter.priority],
        ),
    )


def _selection_facts(
    repo: Repo, stored: StoredTask, *, locked: bool, dependencies: bool
) -> TicketFacts:
    fm = stored.task.frontmatter
    dependency_facts: list[DependencyFact] = []
    if dependencies and not stored.archived:
        for reference in fm.depends_on:
            dependency_id = TaskId.parse(reference)
            try:
                dependency = repo.find(dependency_id)
                complete = _dependency_is_done(repo, dependency_id, dependency)
            except ChittyError as error:
                dependency_facts.append(DependencyFact(reference, "broken", str(error)))
                break
            dependency_facts.append(DependencyFact(reference, "done" if complete else "unfinished"))
    return TicketFacts(
        str(stored.id),
        stored.context,
        fm.status,
        fm.priority,
        fm.owner,
        stored.archived,
        locked,
        tuple(dependency_facts),
        tuple(fm.labels),
    )


def blocking_ids_for(repo: Repo) -> set[str]:
    """Find active tickets named by a waiting dependent in any context."""
    facts = (
        _selection_facts(repo, stored, locked=False, dependencies=True)
        for context in repo.discovered_contexts()
        for stored in repo.tasks(context, "active")
    )
    return blocking_ids(facts)


def list_marker(repo: Repo, stored: StoredTask, blocking: set[str]) -> str | None:
    """Return the list marker, retaining selection reasons before blockers."""
    reason = skip_reason(repo, stored)
    if reason is not None:
        return reason
    fact = _selection_facts(
        repo, stored, locked=locks.is_locked(repo.root, str(stored.id)), dependencies=True
    )
    return dependency_marker(fact) or blocker_marker(fact, blocking)


def skip_reason(repo: Repo, stored: StoredTask) -> str | None:
    """Return the reason `next` would skip a ticket, or None when selectable."""
    return _skip_reason(repo, stored, include_owner=True)


def _skip_reason(
    repo: Repo, stored: StoredTask, *, include_owner: bool, owner: str | None = None
) -> str | None:
    is_locked = locks.is_locked(repo.root, str(stored.id))
    fm = stored.task.frontmatter
    may_read_dependencies = (
        fm.status == "todo"
        and not stored.archived
        and not is_locked
        and stored.context != "human"
        and fm.owner != "human"
        and (
            (include_owner and fm.owner is None)
            or (not include_owner and owner is not None and fm.owner == owner)
        )
    )
    fact = _selection_facts(repo, stored, locked=is_locked, dependencies=may_read_dependencies)
    return pure_skip_reason(fact, include_owner=include_owner)


def _ticket_action(
    repo: Repo,
    stored: StoredTask,
    *,
    refuse: bool,
    owner: str | None = None,
) -> NextAction | None:
    """Validate a ticket for running, or return None when selecting the next ticket."""
    frontmatter = stored.task.frontmatter
    status_order = {"review": 0, "doing": 1, "todo": 2, "error": 3}
    if stored.archived:
        if refuse:
            raise ChittyError(f"cannot run archived ticket {stored.id}")
        return None
    if frontmatter.status not in status_order:
        if refuse:
            raise ChittyError(f"cannot run {stored.id}: status is {frontmatter.status}")
        return None
    if refuse and frontmatter.status == "error":
        raise ChittyError(f"cannot run {stored.id}: use `chitty run --errors` to repair it")
    if stored.context == "human":
        if refuse:
            raise ChittyError(f"cannot run human ticket {stored.id}")
        return None
    if frontmatter.owner == "human":
        if refuse:
            raise ChittyError(f"cannot run {stored.id}: owner is human")
        return None
    if not refuse:
        if _skip_reason(repo, stored, include_owner=owner is None, owner=owner) is not None:
            return None
        if owner is not None and frontmatter.owner != owner:
            return None
    else:
        dependencies: list[tuple[TaskId, StoredTask | None]] = []
        for reference in frontmatter.depends_on:
            dependency_id = TaskId.parse(reference)
            try:
                dependency = repo.find(dependency_id)
            except ChittyError as error:
                main_branch = repo._main_branch()  # pyright: ignore[reportPrivateUsage]
                if repo._main_files_for(  # pyright: ignore[reportPrivateUsage]
                    main_branch, ()
                ) is None or ("used by more than one file" not in str(error)):
                    raise ChittyError(f"{stored.id} depends on {reference}: {error}") from None
                dependency = None
            dependencies.append((dependency_id, dependency))
        if frontmatter.status == "todo" and any(
            not _dependency_is_done(repo, dependency_id, dependency)
            for dependency_id, dependency in dependencies
        ):
            raise ChittyError(f"cannot run {stored.id}: it has unfinished dependencies")
    action_mode: Literal["work", "review"] = "review" if frontmatter.status == "review" else "work"
    return NextAction(action_mode, stored.id)


def _dependency_is_done(repo: Repo, dependency_id: TaskId, dependency: StoredTask | None) -> bool:
    """Whether a dependency is complete on the ref used to create worktrees."""
    context = repo.context_of(dependency_id)
    main_branch = repo._main_branch()  # pyright: ignore[reportPrivateUsage]
    directories = (
        context.directory.relative_to(repo.root),
        context.archive_directory.relative_to(repo.root),
    )
    main_files = repo._main_files_for(  # pyright: ignore[reportPrivateUsage]
        main_branch, directories
    )
    if main_files is None:
        assert dependency is not None
        return dependency.archived or dependency.task.frontmatter.status == "done"

    matches: list[tuple[bool, Path, Task]] = []
    for path, content in main_files:
        try:
            task_id, _ = ids.parse_filename(path.name)
            # Parse only the dependency's file: other tickets cannot change the answer.
            if task_id != dependency_id:
                continue
            task = parse(content)
        except (ids.IdError, TaskError) as error:
            raise ChittyError(f"refs/heads/{main_branch}:{path}: {error}") from None
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


def next_action(
    repo: Repo,
    *,
    modes: tuple[Literal["work", "review", "errors"], ...] = (),
    owner: str | None = None,
) -> NextAction:
    """Select the one ticket to review or work next across every context.

    Each mode adds its statuses to the choice; no mode means every mode. It
    filters before `_ticket_action` checks dependencies, so a bad reference on a
    ticket outside the modes does not stop this one. A ticket another
    `chitty run` holds the run lock for is skipped.
    """
    if owner in ("", "human"):
        raise ChittyError("--owner must name an agent, not human or empty")
    locked = locks.locked_ids(repo.root)
    statuses = mode_statuses(modes)
    facts: list[TicketFacts] = []
    stored_by_id: dict[str, StoredTask] = {}
    for stored in repo.all_tasks():
        fm = stored.task.frontmatter
        if statuses is not None and fm.status not in statuses:
            continue
        is_locked = str(stored.id) in locked
        # Keep dependency reads lazy: only otherwise-eligible todo tickets need them.
        eligible = (
            not stored.archived
            and fm.status == "todo"
            and not is_locked
            and stored.context != "human"
            and fm.owner != "human"
            and (fm.owner is None if owner is None else fm.owner == owner)
        )
        fact = _selection_facts(repo, stored, locked=is_locked, dependencies=eligible)
        facts.append(fact)
        stored_by_id[str(stored.id)] = stored
    # Keep omitted statuses out of selection; error tickets are opt-in.
    configured_order = STATUSES if repo.config.job_order is None else tuple(repo.config.job_order)
    if "errors" in modes:
        order = ("error",)
    else:
        order = tuple(status for status in configured_order if status != "error")
    selected = choose(tuple(facts), modes=modes, owner=owner, order=order)
    if selected is None:
        raise NoNextTicket(
            "no error ticket"
            if modes == ("errors",)
            else "no next ticket"
            if not modes
            else f"no next ticket for --mode {' or '.join(modes)}"
        )
    stored = stored_by_id[selected.id]
    return NextAction("review" if stored.task.frontmatter.status == "review" else "work", stored.id)


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


def scan(
    context: Context, archived: bool, *, allow_any_prefix: bool = False
) -> list[tuple[Path, str | None]]:
    """Every entry in a context directory, with the reason it is invalid (if it is)."""
    directory = context.archive_directory if archived else context.directory
    if not directory.is_dir():
        return []
    entries: list[tuple[Path, str | None]] = []
    for path in sorted(directory.iterdir()):
        if ids.is_hidden_entry(path.name):
            continue
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
        if not allow_any_prefix and task_id.prefix != context.prefix:
            message = f"prefix {task_id.prefix!r} does not belong in context {context.name!r}"
            entries.append((path, f"{message} (prefix {context.prefix!r})"))
            continue
        entries.append((path, None))
    return entries


def replace_pairs(text: str, pairs: Sequence[tuple[str, str]]) -> str:
    """Apply replacements in order, requiring each OLD exactly once as we go."""
    for old, new in pairs:
        count = text.count(old)
        if count != 1:
            raise ChittyError(
                f"--replace-in-description OLD must occur exactly once; found {count} of {old!r}"
            )
        text = text.replace(old, new)
    return text


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
    if edit.description is not None or edit.replace_in_description:
        changes.append("description")
    if edit.add_criteria or edit.rm_criteria or edit.set_criteria or edit.uncheck:
        changes.append("acceptance criteria")
    if edit.set_notes is not None:
        actions.append("replaced notes")
    elif edit.note is not None or edit.notes:
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
