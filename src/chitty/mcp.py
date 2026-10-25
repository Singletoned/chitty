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
from chitty.config import find_root, search_root
from chitty.errors import ChittyError
from chitty.store import Edit, Repo, Which, guide, matches, resolve_add_target

Status = Literal["backlog", "todo", "doing", "done"]
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


@_tool("add", "Create a task with status todo. `context` may also name a user-level context.")
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
) -> dict[str, Any]:
    root = search_root(Path.cwd())
    target = resolve_add_target(Repo.open(root) if root else None, context)
    fields = {
        "status": status,
        "labels": list(dict.fromkeys(label or [])),
        "priority": priority,
        "owner": owner,
        "depends_on": depends_on or [],
    }
    change = target.repo.add(target.context, title, description, ac or [], fields, date.today())
    return change.task.as_dict()


@_tool("list", "List tasks. `status`: any of; `label`: all of; `search`: title and body.")
def list_(
    context: str | None = None,
    status: list[Status] | None = None,
    label: list[str] | None = None,
    owner: str | None = None,
    search: str | None = None,
    archived: bool = False,
    all: bool = False,
) -> list[dict[str, Any]]:
    if archived and all:
        raise ChittyError("give archived or all, not both")
    which: Which = "all" if all else "archived" if archived else "active"
    repo = _repo()
    target = repo.context(context) if context else repo.default_context
    tasks = repo.tasks(target, which)
    found = [t for t in tasks if matches(t, status or [], label or [], owner, search)]
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
    description: str | None = None,
    ac: list[str] | None = None,
    rm_ac: list[int] | None = None,
    check: list[int] | None = None,
    uncheck: list[int] | None = None,
    plan: str | None = None,
    note: str | None = None,
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
        description=description,
        add_criteria=ac or (),
        rm_criteria=rm_ac or (),
        check=check or (),
        uncheck=uncheck or (),
        plan=plan,
        note=note,
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


@_tool("archive", "Move a task into its context's archive/.")
def archive(id: str) -> dict[str, Any]:
    repo = _repo()
    return repo.archive(repo.resolve(id)).task.as_dict()


@_tool("restore", "Move an archived task back out of archive/.")
def restore(id: str) -> dict[str, Any]:
    repo = _repo()
    return repo.restore(repo.resolve(id)).task.as_dict()


@_tool("check", "Validate task files: every context, one `context`, or only `paths`.")
def check(context: str | None = None, paths: list[str] | None = None) -> list[dict[str, str]]:
    repo = _repo()
    contexts = [repo.context(context)] if context else repo.contexts()
    problems = check_repo(repo, contexts, [Path(p) for p in paths or []])
    return [{"path": str(p.path), "message": p.message} for p in problems]


@_tool("path", "The task's file path.")
def path(id: str) -> dict[str, Any]:
    repo = _repo()
    stored = repo.find(repo.resolve(id))
    return {"id": str(stored.id), "path": str(stored.path)}


def run() -> None:
    server.run("stdio")
