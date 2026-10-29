"""stdio MCP server. Tools mirror the CLI one-to-one (same names, same argument
names) and return what the CLI prints with --json. Needs the `mcp` extra."""

import functools
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from chitty.check import check as check_repo
from chitty.check import fix as fix_repo
from chitty.config import find_root, search_root
from chitty.errors import ChittyError
from chitty.inbox import list_waiting
from chitty.inbox import pull as pull_suggestions
from chitty.inbox import suggest as send_suggestion
from chitty.model import STATUSES
from chitty.store import Edit, Repo, guide, matches, resolve_add_target

Status = Literal["backlog", "todo", "doing", "blocked", "review", "done"]
Priority = Literal["low", "medium", "high"]

server = MCPServer(name="chitty", instructions=guide())


def _tool[F: Callable[..., Any]](name: str, description: str) -> Callable[[F], F]:
    """Register a tool whose ChittyErrors reach the client as tool errors."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ChittyError as error:
                raise ToolError(str(error)) from error

        server.tool(name=name, description=description)(wrapper)
        return func

    return decorator


def _repo() -> Repo:
    return Repo.open(find_root(Path.cwd()))


@server.resource("chitty://guide", name="guide", mime_type="text/markdown")
def guide_resource() -> str:
    return guide()


@_tool("inbox", "List waiting suggestions, or import all of them with pull=true.")
def inbox(pull: bool = False) -> list[dict[str, object]] | list[str]:
    repo = _repo()
    if pull:
        return pull_suggestions(repo)
    return list_waiting(repo)


@_tool("suggest", "Send a suggestion to a project's machine-local inbox.")
def suggest(
    project: str,
    title: str,
    description: str | None = None,
    task: str | None = None,
    create: bool = False,
) -> str:
    return str(send_suggestion(project, title, description, create, Path.cwd(), task))


@_tool("add", "Create a task with status todo in this repository.")
def add(
    title: str,
    description: str | None = None,
    context: str | None = None,
    status: Status = "todo",
    ac: list[str] | None = None,
    label: list[str] | None = None,
    priority: Priority | None = None,
    owner: str | None = None,
    depends_on: list[str] | None = None,
    parent: str | None = None,
    note: list[str] | None = None,
) -> dict[str, Any]:
    root = search_root(Path.cwd())
    target = resolve_add_target(Repo.open(root) if root else None, context)
    fields = {
        "status": status,
        "labels": list(dict.fromkeys(label or [])),
        "priority": priority,
        "owner": owner,
        "depends_on": depends_on or [],
        "parent": parent,
    }
    change = target.repo.add(
        target.context, title, description, ac or [], fields, date.today(), note or []
    )
    return change.task.as_dict()


@_tool(
    "list",
    "List tasks. `context` and `status` are repeatable; status defaults to "
    "todo, doing, blocked, and review. `label`: all of; `search`: title and body.",
)
def list_(
    context: list[str] | None = None,
    status: list[Status] | None = None,
    label: list[str] | None = None,
    owner: str | None = None,
    parent: str | None = None,
    search: str | None = None,
    all: bool = False,
) -> list[dict[str, Any]]:
    repo = _repo()
    contexts = [repo.context(name) for name in context] if context else repo.contexts()
    statuses = list(STATUSES) if all else status or ["todo", "doing", "blocked", "review"]
    tasks = [task for selected in contexts for task in repo.tasks(selected, "active")]
    parent = str(repo.resolve(parent)) if parent else None
    found = [t for t in tasks if matches(t, statuses, label or [], owner, search, parent)]
    return [t.as_dict() for t in found]


@_tool("show", "Show a task. Work on one task per session: start here.")
def show(id: str) -> dict[str, Any]:
    repo = _repo()
    return repo.find(repo.resolve(id)).as_dict()


@_tool(
    "edit",
    "Change a task. Write `plan` and set status doing before coding; tick criteria with "
    "`check` (numbers from show) as you meet them; record surprises with `note`. "
    "Criterion numbers refer to the list before this edit. '' unsets priority/owner/plan.",
)
def edit(
    id: str,
    title: str | None = None,
    status: Status | None = None,
    add_label: list[str] | None = None,
    rm_label: list[str] | None = None,
    priority: Priority | Literal[""] | None = None,
    owner: str | None = None,
    depends_on: list[str] | None = None,
    rm_depends_on: list[str] | None = None,
    parent: str | None = None,
    description: str | None = None,
    ac: list[str] | None = None,
    rm_ac: list[int] | None = None,
    check: list[int] | None = None,
    uncheck: list[int] | None = None,
    plan: str | None = None,
    note: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    repo = _repo()
    changes = Edit(
        title=title,
        status=status,
        add_labels=add_label or (),
        rm_labels=rm_label or (),
        priority=priority,
        owner=owner,
        depends_on=depends_on or (),
        rm_depends_on=rm_depends_on or (),
        parent=parent,
        description=description,
        add_criteria=ac or (),
        rm_criteria=rm_ac or (),
        check=check or (),
        uncheck=uncheck or (),
        plan=plan,
        note=note,
        summary=summary,
    )
    return repo.edit(repo.resolve(id), changes).task.as_dict()


@_tool("note", "Append text as a paragraph to a task's Notes section.")
def note(id: str, text: str) -> dict[str, Any]:
    repo = _repo()
    return repo.edit(repo.resolve(id), Edit(note=text)).task.as_dict()


@_tool("move", "Move a task to another context in this repo; it gets a new ID there.")
def move(id: str, context: str) -> dict[str, Any]:
    repo = _repo()
    return repo.move(repo.resolve(id), repo.context(context)).task.as_dict()


@_tool("archive", "Archive one task, or every non-archived done task when `id` is omitted.")
def archive(id: str | None = None) -> dict[str, Any] | list[dict[str, Any]]:
    repo = _repo()
    if id is not None:
        return repo.archive(repo.resolve(id)).task.as_dict()
    return [change.task.as_dict() for change in repo.archive_done()]


@_tool("check", "Validate task files: every context, one `context`, or only `paths`.")
def check(context: str | None = None, paths: list[str] | None = None) -> list[dict[str, str]]:
    repo = _repo()
    contexts = [repo.context(context)] if context else repo.contexts()
    problems = check_repo(repo, contexts, [Path(p) for p in paths or []])
    return [
        {"path": str(problem.path), "message": problem.message, "severity": problem.severity}
        for problem in problems
    ]


@_tool("fix", "Repair safe task-file problems; reports unresolved problems.")
def fix(
    context: str | None = None, paths: list[str] | None = None
) -> dict[str, list[dict[str, str]]]:
    repo = _repo()
    contexts = [repo.context(context)] if context else repo.contexts()
    fixed, problems = fix_repo(repo, contexts, [Path(path) for path in paths or []])
    return {
        "fixed": [{"path": str(problem.path), "message": problem.message} for problem in fixed],
        "problems": [
            {
                "path": str(problem.path),
                "message": problem.message,
                "severity": problem.severity,
            }
            for problem in problems
        ],
    }


@_tool("path", "The task's file path.")
def path(id: str) -> dict[str, Any]:
    repo = _repo()
    stored = repo.find(repo.resolve(id))
    return {"id": str(stored.id), "path": str(stored.path)}


def run() -> None:
    server.run("stdio")
