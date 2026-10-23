"""Cross-file validation: every file parses, IDs are unique, references resolve."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from chitty import ids
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
    for path, task in tasks.items():
        own_id = ids.parse_filename(path.name)[0]
        for reference in task.frontmatter.depends_on:
            if reference == str(own_id):
                problems.append(Problem(path, "depends_on lists the task itself"))
            elif TaskId.parse(reference) not in by_id:
                problems.append(Problem(path, f"depends_on {reference}: no such task"))

    if paths:
        wanted = {p.resolve() for p in paths}
        problems += [
            Problem(p, "not a task file in any chitty context")
            for p in sorted(wanted - set(in_context))
        ]
        return [p for p in problems if p.path in wanted]
    names = {c.name for c in contexts}
    return [p for p in problems if p.path not in in_context or in_context[p.path].name in names]
