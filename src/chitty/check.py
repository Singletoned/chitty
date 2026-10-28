"""Cross-file validation: every file parses, IDs are unique, references resolve."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from chitty import git, ids
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.model import Task, parse
from chitty.store import Context, Repo, scan


@dataclass(frozen=True)
class Problem:
    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def fix(
    repo: Repo, contexts: Sequence[Context], paths: Sequence[Path]
) -> tuple[list[Problem], list[Problem]]:
    """Repair safe problems, then return repairs and remaining problems."""
    wanted = {path.resolve() for path in paths}
    fixed: list[Problem] = []
    for context in contexts:
        for archived in (False, True):
            for path, problem in scan(context, archived):
                if problem or (wanted and path.resolve() not in wanted):
                    continue
                try:
                    task = parse(path.read_text())
                    task_id, _slug = ids.parse_filename(path.name)
                    target = path.with_name(
                        ids.filename(task_id, ids.slugify(task.frontmatter.title))
                    )
                    if target != path:
                        if target.exists():
                            raise ChittyError(f"cannot rename to existing task file {target}")
                        git.move(repo.root, path, target)
                        fixed.append(Problem(path, f"renamed to {target.name}"))
                        path = target
                    canonical = [str(TaskId.parse(item)) for item in task.frontmatter.depends_on]
                    parent = task.frontmatter.parent
                    canonical_parent = str(TaskId.parse(parent)) if parent else None
                    had_dependencies = canonical != task.frontmatter.depends_on
                    if not had_dependencies and canonical_parent == parent:
                        continue
                    task = task.with_field("depends_on", canonical)
                    task = task.with_field("parent", canonical_parent)
                    path.write_text(task.render())
                    field = "depends_on IDs" if had_dependencies else "parent ID"
                    fixed.append(Problem(path, f"rewrote {field} as upper-case"))
                except ChittyError:
                    continue
    return fixed, check(repo, contexts, paths)


def check(repo: Repo, contexts: Sequence[Context], paths: Sequence[Path]) -> list[Problem]:
    """Problems in the given contexts, or only in the given paths if any are given.

    References are always resolved against the whole repo.
    """
    problems: list[Problem] = []
    by_id: dict[TaskId, list[Path]] = defaultdict(list)
    tasks: dict[Path, Task] = {}
    in_context: dict[Path, Context] = {}
    for context in repo.contexts():
        for archived in (False, True):
            for path, problem in scan(context, archived):
                in_context[path] = context
                if problem:
                    problems.append(Problem(path, problem))
                    continue
                by_id[ids.parse_filename(path.name)[0]].append(path)
                try:
                    tasks[path] = parse(path.read_text())
                except ChittyError as error:
                    problems.append(Problem(path, str(error)))
    for task_id, task_paths in by_id.items():
        if len(task_paths) > 1:
            others = ", ".join(str(p) for p in task_paths)
            problems += [
                Problem(p, f"{task_id} is used by more than one file: {others}") for p in task_paths
            ]
    graph: dict[TaskId, set[TaskId]] = {
        task_id: set()
        for task_id, task_paths in by_id.items()
        if len(task_paths) == 1 and task_paths[0] in tasks
    }
    for path, task in tasks.items():
        own_id = ids.parse_filename(path.name)[0]
        for reference in task.frontmatter.depends_on:
            dependency = TaskId.parse(reference)
            if reference != str(dependency):
                problems.append(Problem(path, f"depends_on {reference!r} must be upper-case"))
            if dependency == own_id:
                problems.append(Problem(path, "depends_on lists the task itself"))
            elif dependency not in by_id:
                problems.append(Problem(path, f"depends_on {reference}: no such task"))
            elif own_id in graph and dependency in graph:
                graph[own_id].add(dependency)
    parent_graph: dict[TaskId, set[TaskId]] = {task_id: set() for task_id in graph}
    for path, task in tasks.items():
        own_id = ids.parse_filename(path.name)[0]
        reference = task.frontmatter.parent
        if reference is None:
            continue
        parent = TaskId.parse(reference)
        if reference != str(parent):
            problems.append(Problem(path, f"parent {reference!r} must be upper-case"))
        if parent == own_id:
            problems.append(Problem(path, "parent lists the task itself"))
        elif parent not in by_id:
            problems.append(Problem(path, f"parent {reference}: no such task"))
        elif own_id in parent_graph and parent in parent_graph:
            parent_graph[own_id].add(parent)
    for cycle in _cycles(graph):
        names = ", ".join(str(task_id) for task_id in cycle)
        for task_id in cycle:
            problems.append(Problem(by_id[task_id][0], f"depends_on cycle: {names}"))
    for cycle in _cycles(parent_graph):
        names = ", ".join(str(task_id) for task_id in cycle)
        for task_id in cycle:
            problems.append(Problem(by_id[task_id][0], f"parent cycle: {names}"))

    if paths:
        wanted = {p.resolve() for p in paths}
        problems += [
            Problem(p, "not a task file in any chitty context")
            for p in sorted(wanted - set(in_context))
        ]
        return [p for p in problems if p.path in wanted]
    names = {c.name for c in contexts}
    return [p for p in problems if p.path not in in_context or in_context[p.path].name in names]


def _cycles(graph: dict[TaskId, set[TaskId]]) -> list[tuple[TaskId, ...]]:
    """Return each cyclic strongly connected component, in stable order."""
    index = 0
    indices: dict[TaskId, int] = {}
    lowlinks: dict[TaskId, int] = {}
    stack: list[TaskId] = []
    on_stack: set[TaskId] = set()
    cycles: list[tuple[TaskId, ...]] = []

    def visit(task_id: TaskId) -> None:
        nonlocal index
        indices[task_id] = index
        lowlinks[task_id] = index
        index += 1
        stack.append(task_id)
        on_stack.add(task_id)
        for dependency in sorted(graph[task_id], key=str):
            if dependency not in indices:
                visit(dependency)
                lowlinks[task_id] = min(lowlinks[task_id], lowlinks[dependency])
            elif dependency in on_stack:
                lowlinks[task_id] = min(lowlinks[task_id], indices[dependency])
        if lowlinks[task_id] != indices[task_id]:
            return
        component: list[TaskId] = []
        while True:
            dependency = stack.pop()
            on_stack.remove(dependency)
            component.append(dependency)
            if dependency == task_id:
                break
        if len(component) > 1:
            cycles.append(tuple(sorted(component, key=str)))

    for task_id in sorted(graph, key=str):
        if task_id not in indices:
            visit(task_id)
    return sorted(cycles, key=lambda cycle: tuple(map(str, cycle)))
