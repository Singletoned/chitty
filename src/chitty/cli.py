"""Command-line interface. Thin: parse flags, call store/model, print."""

import json
import os
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, TextIO, cast

import click
from click.shell_completion import CompletionItem

from chitty import locks
from chitty.actor import actor, pi_session_environment_missing
from chitty.check import check as check_repo
from chitty.check import errors
from chitty.check import fix as fix_repo
from chitty.config import (
    CHITTY_VERSION,
    find_root,
    registered_projects,
    search_root,
    user_contexts_path,
    version_key,
)
from chitty.errors import NO_NEXT_TICKET_EXIT, ChittyError, NoNextTicket
from chitty.import_backlog import import_directory
from chitty.inbox import list_waiting, waiting
from chitty.inbox import pull as pull_suggestions
from chitty.inbox import suggest as send_suggestion
from chitty.integrations.claude.usage import run_hook
from chitty.model import (
    ACCEPTANCE_CRITERIA,
    FIELD_ORDER,
    PRIORITIES,
    PRIORITY_GLYPHS,
    SECTION_ORDER,
    STATUS_GLYPHS,
    STATUS_LABELS,
    STATUSES,
)
from chitty.run import RunInterrupted, run_loop
from chitty.run import run as run_next
from chitty.store import (
    BROKEN_DEPENDENCY_GLYPH,
    Change,
    Edit,
    Repo,
    StoredTask,
    guide,
    init_repo,
    matches,
    next_action,
    ordered,
    renumbered_dict,
    resolve_add_target,
    skip_reason,
)
from chitty.upgrade import check_for_upgrade


class _Group(click.Group):
    def invoke(self, ctx: click.Context) -> Any:
        if user_contexts_path().exists():
            click.echo("warning: contexts.toml is ignored; use chitty suggest", err=True)
        try:
            return super().invoke(ctx)
        except NoNextTicket as error:
            # An idle queue is a normal outcome for a loop, not a failure, so
            # it gets a plain line on stderr rather than click's `Error:`.
            click.echo(str(error), err=True)
            ctx.exit(NO_NEXT_TICKET_EXIT)
        except ChittyError as error:
            raise click.ClickException(str(error)) from error


@click.group(cls=_Group)
@click.version_option(version=CHITTY_VERSION, prog_name="chitty")
def cli() -> None:
    """Markdown-native task tracker for humans and coding agents.

    Tasks are markdown files under chitty/<context>/. IDs are PREFIX-N
    (e.g. TASK-13); a bare number means the default context.

    Coding agents: run `chitty guide` for how to work with chitty.
    """


def main() -> None:
    try:
        cli()
    finally:
        if "_CHITTY_COMPLETE" not in os.environ:
            check_for_upgrade()


json_option = click.option("--json", "as_json", is_flag=True, help="Print JSON.")
mode_option = click.option(
    "--mode",
    type=click.Choice(["work", "review"]),
    help="Choose only tickets to work (doing, todo) or only tickets to review.",
)


def _complete_context(
    _ctx: click.Context | None, _param: click.Parameter | None, incomplete: str
) -> list[CompletionItem]:
    try:
        contexts = _repo().contexts()
    except ChittyError:
        return []
    return [
        CompletionItem(context.name) for context in contexts if context.name.startswith(incomplete)
    ]


def _complete_project(
    ctx: click.Context, parameter: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    return [CompletionItem(name) for name in registered_projects() if name.startswith(incomplete)]


def _complete_task_id(
    _ctx: click.Context | None, _param: click.Parameter | None, incomplete: str
) -> list[CompletionItem]:
    try:
        tasks = _repo().all_tasks()
    except ChittyError:
        return []
    return [
        CompletionItem(str(task.id))
        for task in sorted(tasks, key=lambda task: (task.archived, str(task.id)))
        if str(task.id).lower().startswith(incomplete.lower())
    ]


context_option = click.option(
    "-c",
    "--context",
    help="Context name (default: default_context from chitty.toml).",
    shell_complete=_complete_context,
)


def _repo(*, warn_setup_version: bool = True) -> Repo:
    repo = Repo.open(find_root(Path.cwd()))
    if warn_setup_version:
        _warn_setup_version(repo.config.chitty_version)
    return repo


def _warn_setup_version(recorded: str | None) -> None:
    if recorded is None:
        click.echo("warning: re-run `chitty init` to refresh repository setup", err=True)
        return
    try:
        recorded_key = version_key(recorded)
        current_key = version_key(CHITTY_VERSION)
    except ChittyError:
        click.echo("warning: recorded version cannot be read; run `chitty init`", err=True)
        return
    if recorded_key == current_key:
        return
    if recorded_key < current_key:
        click.echo("warning: re-run `chitty init` to refresh repository setup", err=True)
    else:
        click.echo("warning: upgrade chitty to match this repository's setup", err=True)


def _print_json(data: Any) -> None:
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def _report(change: Change, as_json: bool, verb: str) -> None:
    """Print the result of a write."""
    if as_json:
        _print_json(change.task.as_dict())
    elif change.paths:
        actor_name = f" actor {change.actor}" if change.actor else ""
        click.echo(f"{verb} {change.task.id} {change.task.path}{actor_name}")
    else:
        click.echo(f"unchanged {change.task.id}")


def _priority(_ctx: click.Context, _param: click.Parameter, value: str | None) -> str | None:
    if value is not None and value not in (*PRIORITIES, ""):
        raise click.BadParameter(f"must be one of {', '.join(PRIORITIES)}, or '' to unset")
    return value


def _text(value: str | None, file: TextIO | None, name: str) -> str | None:
    if value is not None and file is not None:
        raise click.UsageError(f"give --{name} or --{name}-file, not both")
    return file.read() if file is not None else value


@cli.command()
@click.option(
    "--autocommit",
    "enable_autocommit",
    is_flag=True,
    help="Enable autocommit and commit this clean setup change.",
)
def init(enable_autocommit: bool) -> None:
    """Create or upgrade Chitty configuration and agent instructions."""
    paths = init_repo(Path.cwd(), enable_autocommit)
    if not paths:
        click.echo("already up to date")
    for path in paths:
        click.echo(f"updated {path}")


@cli.command()
def pull() -> None:
    """Explain the replacement for the former inbox-import command."""
    raise click.UsageError(
        "run `chitty inbox --pull`, then re-run `chitty init` to refresh the guide"
    )


@cli.command()
@click.option("--pull", "import_suggestions", is_flag=True, help="Import all waiting suggestions.")
@json_option
def inbox(import_suggestions: bool, as_json: bool) -> None:
    """List waiting suggestions, or import all of them with --pull."""
    repo = _repo()
    if import_suggestions:
        click.echo(f"actor {actor()}")
        task_ids = pull_suggestions(repo)
        if task_ids:
            for task_id in task_ids:
                click.echo(f"pulled {task_id}")
        else:
            click.echo("no suggestions waiting", err=True)
        return
    suggestions = list_waiting(repo)
    if as_json:
        _print_json(suggestions)
    elif suggestions:
        for suggestion in suggestions:
            click.echo(f"{suggestion['origin']}  {suggestion['created']}  {suggestion['title']}")
        click.echo("run `chitty inbox --pull` to import them", err=True)
    else:
        click.echo("no suggestions waiting", err=True)


@cli.command()
@click.argument("project", shell_complete=_complete_project)
@click.argument("title")
@click.option("-d", "--description")
@click.option("--task", help="Task ID being worked on.")
@click.option("--create", is_flag=True, help="Create an inbox for a non-Chitty project.")
def suggest(
    project: str, title: str, description: str | None, task: str | None, create: bool
) -> None:
    """Send a suggestion to a registered project or an explicit local path.

    PROJECT is a registered name unless it contains `/`, is `.`, or starts with
    `~` or `.`; paths resolve their Chitty configuration before sending.
    """
    click.echo(send_suggestion(project, title, description, create, Path.cwd(), task))


@cli.group("import")
def import_() -> None:
    """Import tasks from another tracker."""


@import_.command("backlog-md")
@click.option("--context", default=None, help="Destination context (default: repository default).")
@click.option("--keep-source", is_flag=True, help="Leave all imported source files in place.")
def import_backlog_md(context: str | None, keep_source: bool) -> None:
    """Convert the local backlog/ directory and remove its imported sources.

    Refuses to run unless the Git working tree is clean, untracked files
    included, so Git history can restore anything the import removes.
    """
    repo = _repo()
    selected = repo.context(context or repo.config.default_context)
    if repo.tasks(selected, "all"):
        raise ChittyError(f"{selected.name} already contains tasks; refusing to import")
    source = repo.root / "backlog"
    if not source.is_dir():
        raise ChittyError(f"{source} does not exist")
    for report in import_directory(source, repo, selected, repo.root / "AGENTS.md", keep_source):
        click.echo(report)


@cli.command()
@click.argument("title")
@context_option
@click.option("-d", "--description", help="The Description section (required except for backlog).")
@click.option("-s", "--status", type=click.Choice(STATUSES), default="todo", show_default=True)
@click.option("--ac", "criteria", multiple=True, help="Acceptance criterion (repeatable).")
@click.option("-l", "--label", "labels", multiple=True, help="Label (repeatable).")
@click.option("-p", "--priority", type=click.Choice(PRIORITIES))
@click.option("--owner", help="Free text: human, a name, an agent.")
@click.option("--depends-on", multiple=True, help="Task ID this is blocked on (repeatable).")
@click.option("--parent", help="Parent task ID in this repository.")
@click.option("--note", "notes", multiple=True, help="Append a paragraph to Notes (repeatable).")
@click.option("--note-file", type=click.File(), help="Read a note from a file ('-' for stdin).")
@json_option
def add(
    title: str,
    context: str | None,
    description: str | None,
    status: str,
    criteria: tuple[str, ...],
    labels: tuple[str, ...],
    priority: str | None,
    owner: str | None,
    depends_on: tuple[str, ...],
    parent: str | None,
    notes: tuple[str, ...],
    note_file: TextIO | None,
    as_json: bool,
) -> None:
    """Create a task with status todo.

    -c names a context in this repository. Use `chitty suggest` to send work
    to another repository.
    """
    root = search_root(Path.cwd())
    target = resolve_add_target(Repo.open(root) if root else None, context)
    random_ids = target.repo.config.contexts[target.context.name].random_ids
    if description is None and status != "backlog" and not random_ids:
        raise click.UsageError("--description is required unless --status backlog")
    fields = {
        "status": status,
        "labels": list(dict.fromkeys(labels)),
        "priority": priority,
        "owner": owner,
        "depends_on": list(depends_on),
        "parent": parent,
    }
    if note_file is not None:
        notes = (*notes, note_file.read())
    change = target.repo.add(
        target.context, title, description, criteria, fields, date.today(), notes
    )
    _report(change, as_json, "added")


@cli.command("list")
@click.option(
    "-c", "--context", "contexts", multiple=True, help="Context name (repeatable; defaults to all)."
)
@click.option(
    "-s",
    "--status",
    "statuses",
    multiple=True,
    type=click.Choice(STATUSES),
    help="Status to include (repeatable; defaults to todo, doing, blocked, and review).",
)
@click.option("-l", "--label", "labels", multiple=True, help="Only tasks with every label.")
@click.option("--owner")
@click.option("--parent", help="Only children of this task ID.")
@click.option("--search", help="Case-insensitive match on title and body.")
@click.option("--all", "all_", is_flag=True, help="Every status (never archived tasks).")
@json_option
def list_(
    contexts: tuple[str, ...],
    statuses: tuple[str, ...],
    labels: tuple[str, ...],
    owner: str | None,
    parent: str | None,
    search: str | None,
    all_: bool,
    as_json: bool,
) -> None:
    """List tasks, one per line."""
    repo = _repo()
    selected = [repo.context(context) for context in contexts] if contexts else repo.contexts()
    selected_statuses = STATUSES if all_ else statuses or ("todo", "doing", "blocked", "review")
    parent = str(repo.resolve(parent)) if parent else None
    tasks = [
        task
        for context in selected
        for task in repo.tasks(context, "active")
        if matches(task, selected_statuses, labels, owner, search, parent)
    ]
    tasks = ordered(tasks, selected_statuses)
    if not tasks:
        click.echo(
            f"no tasks: contexts={','.join(context.name for context in selected)}; "
            f"statuses={','.join(selected_statuses)}",
            err=True,
        )
    if repo.config.project and waiting(repo.config.project):
        click.echo("suggestions waiting: run chitty inbox --pull", err=True)
    if as_json:
        _print_json([{**task.as_dict(), "skipped": skip_reason(repo, task)} for task in tasks])
        return
    width = max((len(str(t.id)) for t in tasks), default=0)
    show_priority = any(t.task.frontmatter.priority is not None for t in tasks)
    reasons = [skip_reason(repo, stored) for stored in tasks]
    show_markers = any(reasons)
    for stored, reason in zip(tasks, reasons, strict=True):
        fm = stored.task.frontmatter
        line = f"{stored.id!s:<{width}}  {STATUS_GLYPHS[fm.status]} {STATUS_LABELS[fm.status]:<5}"
        if show_priority:
            line += f"  {_two_columns(PRIORITY_GLYPHS[fm.priority])}"
        if show_markers:
            line += f"  {_two_columns(reason.split()[0] if reason else '')}"
        label_text = f"  [{','.join(sorted(fm.labels))}]" if fm.labels else ""
        room = repo.config.list_width - _columns(line) - 2 - _columns(label_text)
        click.echo(f"{line}  {_shorten(fm.title, room)}{label_text}")
        if reason and reason.startswith(BROKEN_DEPENDENCY_GLYPH):
            click.echo(f"warning: {reason.removeprefix(BROKEN_DEPENDENCY_GLYPH).strip()}", err=True)


def _columns(text: str) -> int:
    """Return how many terminal columns text takes, counting emoji as two."""
    total = 0
    for char in text:
        if char == "\ufe0f":
            total += 1  # turns the preceding narrow symbol into a wide emoji
        elif unicodedata.east_asian_width(char) in {"W", "F"}:
            total += 2
        elif not unicodedata.combining(char):
            total += 1
    return total


def _two_columns(glyph: str) -> str:
    """Pad a glyph, or nothing, to two terminal columns."""
    return glyph + " " * (2 - _columns(glyph))


def _shorten(title: str, room: int) -> str:
    """Cut a title to fit in room columns, ending it with an ellipsis when cut."""
    if _columns(title) <= room:
        return title
    shortened = ""
    for char in title:
        if _columns(shortened + char) > room - 1:
            break
        shortened += char
    return shortened.rstrip() + "…"


@cli.command("next")
@click.option("--owner", help="Choose tickets owned by this agent.")
@mode_option
@json_option
def next_(mode: Literal["work", "review"] | None, as_json: bool, owner: str | None) -> None:
    """Print the next ticket to work or review."""
    action = next_action(_repo(), mode=mode, owner=owner)
    if as_json:
        _print_json(action.as_dict())
    else:
        click.echo(f"{action.mode} {action.id}")


@cli.command("claude-usage-hook", hidden=True)
def claude_usage_hook() -> None:
    """Record usage from a Claude Code SessionEnd hook."""
    run_hook(cast(TextIO, sys.stdin))


@cli.command("run", context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option("--ticket", metavar="ID", help="Run the next ticket, or the one named by --ticket.")
@click.option("--owner", help="Choose tickets owned by this agent.")
@click.option("--agent", metavar="NAME", help="Use the named command from [agent_commands].")
@click.option(
    "--loop",
    is_flag=True,
    help="Keep running; wait 60 seconds between attempts, including when idle. Stop on errors.",
)
@mode_option
@click.pass_context
def run(
    ctx: click.Context,
    ticket: str | None,
    owner: str | None,
    agent: str | None,
    loop: bool,
    mode: Literal["work", "review"] | None,
) -> None:
    """Run the next ticket, or the one named by --ticket; other arguments go to the agent."""
    if loop and ticket is not None:
        raise click.UsageError("--loop cannot be used with --ticket")
    try:
        if loop:
            options: list[str] = []
            if owner is not None:
                options.extend(("--owner", owner))
            if agent is not None:
                options.extend(("--agent", agent))
            if mode is not None:
                options.extend(("--mode", mode))
            if ctx.args:
                options.extend(("--", *ctx.args))
            raise click.exceptions.Exit(run_loop(tuple(options)))
        result = run_next(
            _repo(warn_setup_version=False),
            ticket,
            tuple(ctx.args),
            agent=agent,
            mode=mode,
            owner=owner,
        )
    except RunInterrupted as interrupted:
        click.echo(f"interrupted during {interrupted.phase}", err=True)
        raise click.exceptions.Exit(130) from None
    except KeyboardInterrupt:
        click.echo("interrupted while waiting for work", err=True)
        raise click.exceptions.Exit(130) from None
    click.echo(f"{result.action.id}: {result.old_status} → {result.new_status}")


@cli.command()
@click.argument("task_id", metavar="ID", shell_complete=_complete_task_id)
@json_option
def show(task_id: str, as_json: bool) -> None:
    """Show a task, with acceptance criteria numbered."""
    repo = _repo()
    stored = repo.find(repo.resolve(task_id))
    children = [
        task.id for task in repo.all_tasks() if task.task.frontmatter.parent == str(stored.id)
    ]
    try:
        worked_on = stored.task.review_work(actor())
    except ChittyError:
        worked_on = []
    running = locks.holder(repo.root, str(stored.id))
    if as_json:
        _print_json({**stored.as_dict(), "running": running})
    else:
        output = _format(stored)
        if worked_on:
            output += "\nworked on: " + ", ".join(worked_on)
        if children:
            output += "\nchildren: " + ", ".join(map(str, children))
        if running is not None:
            output += "\nrunning: " + _running_line(running)
        click.echo(output)


def _running_line(record: dict[str, Any]) -> str:
    pid = record.get("pid", "unknown")
    if "actor" not in record:
        return f"process {pid}"
    started = datetime.fromisoformat(str(record["started"]))
    local_time = started.astimezone().strftime("%H:%M")
    return (
        f"{record.get('mode', 'unknown')} by {record['actor']}, process {pid}, since {local_time}"
    )


def _format(stored: StoredTask) -> str:
    fm = stored.task.frontmatter.model_dump(mode="json", exclude_defaults=True)
    lines = [f"{stored.id}{'  (archived)' if stored.archived else ''}"]
    for key in FIELD_ORDER:
        value = fm.get(key)
        if isinstance(value, list):
            lines.append(f"{key}: {', '.join(cast(list[str], value))}")
        elif value is not None:
            lines.append(f"{key}: {value}")
    lines.append(f"path: {stored.path}")
    if stored.branch:
        lines.append(f"branch: {stored.branch}")
    for name in SECTION_ORDER:
        if name == ACCEPTANCE_CRITERIA:
            criteria = stored.task.criteria
            content = "\n".join(
                f"{n}. [{'x' if c.checked else ' '}] {c.text}"
                for n, c in enumerate(criteria, start=1)
            )
        else:
            content = stored.task.section(name)
        if content:
            lines += ["", f"## {name}", "", content]
    return "\n".join(lines)


@cli.command()
@click.argument("task_id", metavar="ID", shell_complete=_complete_task_id)
@click.option("--title")
@click.option("-s", "--status", type=click.Choice(STATUSES))
@click.option("--add-label", multiple=True)
@click.option("--rm-label", multiple=True)
@click.option("-p", "--priority", callback=_priority, help="low, medium, high; '' unsets.")
@click.option("--owner", help="'' unsets.")
@click.option("--depends-on", multiple=True, help="Add a dependency (repeatable).")
@click.option("--rm-depends-on", multiple=True, help="Remove a dependency (repeatable).")
@click.option("--parent", help="Parent task ID; '' unsets.")
@click.option("-d", "--description", help="Replace the Description section.")
@click.option("--description-file", type=click.File(), help="Read --description from a file.")
@click.option("--ac", multiple=True, help="Append an acceptance criterion (repeatable).")
@click.option("--rm-ac", type=int, multiple=True, help="Remove criterion N (repeatable).")
@click.option(
    "--set-ac", type=(int, str), nargs=2, multiple=True, help="Replace criterion N (repeatable)."
)
@click.option("--check", type=int, multiple=True, help="Tick criterion N (repeatable).")
@click.option("--uncheck", type=int, multiple=True, help="Untick criterion N (repeatable).")
@click.option("--plan", help="Replace the Plan section; '' removes it.")
@click.option("--plan-file", type=click.File(), help="Read --plan from a file.")
@click.option("--note", "notes", multiple=True, help="Append a paragraph to Notes (repeatable).")
@click.option("--note-file", type=click.File(), help="Read a note from a file ('-' for stdin).")
@click.option("--set-notes", help="Replace the Notes section; '' removes it.")
@click.option("--set-notes-file", type=click.File(), help="Read replacement Notes from a file.")
@click.option("--summary", help="Replace the Summary section; '' removes it.")
@click.option(
    "--override-review-independence",
    is_flag=True,
    help="Allow an actor who worked on a task to review it; records the override in History.",
)
@json_option
def edit(
    task_id: str,
    title: str | None,
    status: str | None,
    add_label: tuple[str, ...],
    rm_label: tuple[str, ...],
    priority: str | None,
    owner: str | None,
    depends_on: tuple[str, ...],
    rm_depends_on: tuple[str, ...],
    parent: str | None,
    description: str | None,
    description_file: TextIO | None,
    ac: tuple[str, ...],
    rm_ac: tuple[int, ...],
    set_ac: tuple[tuple[int, str], ...],
    check: tuple[int, ...],
    uncheck: tuple[int, ...],
    plan: str | None,
    plan_file: TextIO | None,
    notes: tuple[str, ...],
    note_file: TextIO | None,
    set_notes: str | None,
    set_notes_file: TextIO | None,
    summary: str | None,
    override_review_independence: bool,
    as_json: bool,
) -> None:
    """Change a task. Criterion numbers refer to the list before this edit."""
    repo = _repo()
    changes = Edit(
        title=title,
        status=status,
        add_labels=add_label,
        rm_labels=rm_label,
        priority=priority,
        owner=owner,
        depends_on=depends_on,
        rm_depends_on=rm_depends_on,
        parent=parent,
        description=_text(description, description_file, "description"),
        add_criteria=ac,
        rm_criteria=rm_ac,
        set_criteria=set_ac,
        check=check,
        uncheck=uncheck,
        plan=_text(plan, plan_file, "plan"),
        notes=(*notes, note_file.read()) if note_file is not None else notes,
        set_notes=_text(set_notes, set_notes_file, "set-notes"),
        summary=summary,
        override_review_independence=override_review_independence,
    )
    change = repo.edit(repo.resolve(task_id), changes)
    escalated = status == "doing" and change.task.task.frontmatter.status == "blocked"
    _report(change, as_json, "escalated to human review" if escalated else "updated")


@cli.command()
@click.argument("task_id", metavar="ID", shell_complete=_complete_task_id)
@click.argument("text")
@json_option
def note(task_id: str, text: str, as_json: bool) -> None:
    """Append TEXT as a paragraph to a task's Notes section."""
    repo = _repo()
    _report(repo.edit(repo.resolve(task_id), Edit(note=text)), as_json, "updated")


@cli.command("check")
@context_option
@click.argument("paths", nargs=-1, type=click.Path(path_type=Path))
@json_option
def check_(context: str | None, paths: tuple[Path, ...], as_json: bool) -> None:
    """Validate task files. Exits non-zero if there are any problems.

    With PATHs, only those files are checked; otherwise every context, or
    just -c CONTEXT.
    """
    repo = _repo()
    contexts = [repo.context(context)] if context else repo.contexts()
    problems = check_repo(repo, contexts, paths)
    if as_json:
        _print_json(
            [{"path": str(p.path), "message": p.message, "severity": p.severity} for p in problems]
        )
    else:
        for problem in problems:
            click.echo(str(problem))
    if blocking := errors(problems):
        raise click.ClickException(f"{len(blocking)} problem(s)")


@cli.command("fix")
@context_option
@click.argument("paths", nargs=-1, type=click.Path(path_type=Path))
@json_option
def fix_(context: str | None, paths: tuple[Path, ...], as_json: bool) -> None:
    """Repair safe task-file problems; exits non-zero for unresolved problems."""
    repo = _repo()
    contexts = [repo.context(context)] if context else repo.contexts()
    fixed, problems = fix_repo(repo, contexts, paths)
    if as_json:
        _print_json(
            {
                "fixed": [
                    {"path": str(problem.path), "message": problem.message} for problem in fixed
                ],
                "problems": [
                    {
                        "path": str(problem.path),
                        "message": problem.message,
                        "severity": problem.severity,
                    }
                    for problem in problems
                ],
            }
        )
    else:
        for problem in fixed:
            click.echo(f"fixed: {problem}")
        for problem in problems:
            click.echo(str(problem))
    if blocking := errors(problems):
        raise click.ClickException(f"{len(blocking)} unresolved problem(s)")


@cli.command()
@click.argument("task_id", metavar="ID", shell_complete=_complete_task_id)
@json_option
def path(task_id: str, as_json: bool) -> None:
    """Print the task's file path."""
    repo = _repo()
    stored = repo.find(repo.resolve(task_id))
    if as_json:
        _print_json({"id": str(stored.id), "path": str(stored.path)})
    else:
        click.echo(str(stored.path))


@cli.command()
@click.argument("task_id", metavar="ID", shell_complete=_complete_task_id)
@click.argument("context", shell_complete=_complete_context)
@json_option
def move(task_id: str, context: str, as_json: bool) -> None:
    """Move a task to another context in this repo.

    It gets the next ID there (keeping its slug), records moved_from, and
    every depends_on reference to the old ID is rewritten.
    """
    repo = _repo()
    change = repo.move(repo.resolve(task_id), repo.context(context))
    _report(change, as_json, "moved")
    if not as_json:
        for touched in change.paths[2:]:
            click.echo(f"rewrote reference in {touched}")


@cli.command()
@click.argument("path", type=click.Path(path_type=Path))
@json_option
def renumber(path: Path, as_json: bool) -> None:
    """Give one of several files sharing an ID the next number in its context.

    PATH is the task file to change. It keeps its slug and records moved_from.
    References are not rewritten, because a reference to a shared ID cannot say
    which file it meant: each ticket naming the old ID is listed to check.
    """
    change, references = _repo().renumber(path)
    if as_json:
        _print_json(renumbered_dict(change, references))
        return
    _report(change, as_json, "renumbered")
    old = change.task.task.frontmatter.moved_from
    for reference in references:
        click.echo(f"check reference to {old} in {reference.id} {reference.path}")


@cli.command()
@click.argument("task_id", metavar="ID", required=False, shell_complete=_complete_task_id)
@json_option
def archive(task_id: str | None, as_json: bool) -> None:
    """Archive one task, or every done task when ID is omitted."""
    repo = _repo()
    verb = "deleted" if repo.config.archive == "delete" else "archived"
    if task_id is not None:
        change = repo.archive(repo.resolve(task_id))
        _report(change, as_json, verb)
        if not as_json and verb == "deleted":
            for path in change.paths[:-1]:
                click.echo(f"removed dependency reference in {path}")
        return
    changes = repo.archive_done()
    if as_json:
        _print_json([change.task.as_dict() for change in changes])
    elif changes:
        for change in changes:
            actor_name = f" actor {change.actor}" if change.actor else ""
            click.echo(f"{verb} {change.task.id}{actor_name}")
            if verb == "deleted":
                for path in change.paths[:-1]:
                    click.echo(f"removed dependency reference in {path}")
    else:
        click.echo(f"no done tasks to {verb[:-1]}")


@cli.command("guide")
@click.argument("role", required=False)
@click.argument("task_id", metavar="[ID]", required=False)
def guide_(role: str | None, task_id: str | None) -> None:
    """Print general or role-specific instructions for coding agents.

    \b
    Examples:
      chitty guide                    General agent instructions
      chitty guide setup              Configure chitty run in a repository
      chitty guide work TASK-12       Work on a ticket
      chitty guide review TASK-12     Review a ticket
      chitty guide plan               Write or refine tickets
      chitty guide cold-read TASK-12  Cold-read a proposed ticket

    Work, review and cold-read accept an optional ticket ID. Setup and plan do not.
    """
    click.echo(guide(role, task_id), nl=False)
    if role is None and pi_session_environment_missing():
        click.echo(
            "\nPi needs Chitty's extension to set its session identity. Reload the extension or "
            "set `CHITTY_ACTOR` when starting Pi; servers started before the extension use "
            "that workaround."
        )


@cli.command()
@json_option
def whoami(as_json: bool) -> None:
    """Print the stable name Chitty uses for this actor."""
    name = actor()
    _print_json({"actor": name}) if as_json else click.echo(name)


@cli.command()
def mcp() -> None:
    """Run the stdio MCP server (needs the mcp extra)."""
    # Imported here because the mcp package is an optional extra.
    try:
        from chitty.mcp import run
    except ModuleNotFoundError as error:
        if error.name is None or not error.name.startswith("mcp"):
            raise
        raise ChittyError(
            "chitty mcp needs the mcp extra: uv tool install 'chitty[mcp]'"
        ) from error
    run()
