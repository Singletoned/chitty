"""Command-line interface. Thin: parse flags, call store/model, print."""

import json
from datetime import date
from pathlib import Path
from typing import Any, TextIO, cast

import click

from chitty.check import check as check_repo
from chitty.config import find_root
from chitty.errors import ChittyError
from chitty.model import ACCEPTANCE_CRITERIA, FIELD_ORDER, PRIORITIES, SECTION_ORDER, STATUSES
from chitty.store import Change, Edit, Repo, StoredTask, Which, init_repo, matches


class _Group(click.Group):
    def invoke(self, ctx: click.Context) -> Any:
        try:
            return super().invoke(ctx)
        except ChittyError as error:
            raise click.ClickException(str(error)) from error


@click.group(cls=_Group)
@click.version_option(package_name="chitty")
def cli() -> None:
    """Markdown-native task tracker for humans and coding agents.

    Tasks are markdown files under chitty/<context>/. IDs are PREFIX-N
    (e.g. TASK-13); a bare number means the default context.
    """


def main() -> None:
    cli()


json_option = click.option("--json", "as_json", is_flag=True, help="Print JSON.")
context_option = click.option(
    "-c", "--context", help="Context name (default: default_context from chitty.toml)."
)


def _repo() -> Repo:
    return Repo.open(find_root(Path.cwd()))


def _print_json(data: Any) -> None:
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def _report(change: Change, as_json: bool, verb: str) -> None:
    if as_json:
        _print_json(change.task.as_dict())
    elif change.paths:
        click.echo(f"{verb} {change.task.id} {change.task.path}")
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
@click.option("--prefix", default="TASK", show_default=True, help="ID prefix for tasks/.")
def init(prefix: str) -> None:
    """Write chitty.toml and chitty/tasks/, and add the agent guide to AGENTS.md."""
    for path in init_repo(Path.cwd(), prefix):
        click.echo(f"wrote {path}")


@cli.command()
@click.argument("title")
@context_option
@click.option("-d", "--description", required=True, help="The Description section.")
@click.option("--ac", "criteria", multiple=True, help="Acceptance criterion (repeatable).")
@click.option("-l", "--label", "labels", multiple=True, help="Label (repeatable).")
@click.option("-p", "--priority", type=click.Choice(PRIORITIES))
@click.option("--owner", help="Free text: human, a name, an agent.")
@click.option("--depends-on", multiple=True, help="Task ID this is blocked on (repeatable).")
@json_option
def add(
    title: str,
    context: str | None,
    description: str,
    criteria: tuple[str, ...],
    labels: tuple[str, ...],
    priority: str | None,
    owner: str | None,
    depends_on: tuple[str, ...],
    as_json: bool,
) -> None:
    """Create a task with status todo."""
    repo = _repo()
    target = repo.context(context) if context else repo.default_context
    fields = {
        "labels": list(dict.fromkeys(labels)),
        "priority": priority,
        "owner": owner,
        "depends_on": [str(repo.resolve(d)) for d in dict.fromkeys(depends_on)],
    }
    change = repo.add(target, title, description, criteria, fields, date.today())
    _report(change, as_json, "added")


@cli.command("list")
@context_option
@click.option("-s", "--status", "statuses", multiple=True, type=click.Choice(STATUSES))
@click.option("-l", "--label", "labels", multiple=True, help="Only tasks with every label.")
@click.option("--owner")
@click.option("--search", help="Case-insensitive match on title and body.")
@click.option("--archived", is_flag=True, help="Only archived tasks.")
@click.option("--all", "all_", is_flag=True, help="Archived and non-archived tasks.")
@json_option
def list_(
    context: str | None,
    statuses: tuple[str, ...],
    labels: tuple[str, ...],
    owner: str | None,
    search: str | None,
    archived: bool,
    all_: bool,
    as_json: bool,
) -> None:
    """List tasks, one per line."""
    if archived and all_:
        raise click.UsageError("give --archived or --all, not both")
    which: Which = "all" if all_ else "archived" if archived else "active"
    repo = _repo()
    target = repo.context(context) if context else repo.default_context
    tasks = [t for t in repo.tasks(target, which) if matches(t, statuses, labels, owner, search)]
    if as_json:
        _print_json([t.as_dict() for t in tasks])
        return
    width = max((len(str(t.id)) for t in tasks), default=0)
    for stored in tasks:
        fm = stored.task.frontmatter
        line = f"{stored.id!s:<{width}}  {fm.status:<6}  {fm.title}"
        if fm.labels:
            line += f"  [{','.join(sorted(fm.labels))}]"
        if stored.archived:
            line += "  (archived)"
        click.echo(line)


@cli.command()
@click.argument("task_id", metavar="ID")
@json_option
def show(task_id: str, as_json: bool) -> None:
    """Show a task, with acceptance criteria numbered."""
    repo = _repo()
    stored = repo.find(repo.resolve(task_id))
    if as_json:
        _print_json(stored.as_dict())
    else:
        click.echo(_format(stored))


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
@click.argument("task_id", metavar="ID")
@click.option("--title")
@click.option("-s", "--status", type=click.Choice(STATUSES))
@click.option("--add-label", multiple=True)
@click.option("--rm-label", multiple=True)
@click.option("-p", "--priority", callback=_priority, help="low, medium, high; '' unsets.")
@click.option("--owner", help="'' unsets.")
@click.option("--depends-on", multiple=True, help="Add a dependency (repeatable).")
@click.option("--rm-depends-on", multiple=True, help="Remove a dependency (repeatable).")
@click.option("-d", "--description", help="Replace the Description section.")
@click.option("--description-file", type=click.File(), help="Read --description from a file.")
@click.option("--ac", multiple=True, help="Append an acceptance criterion (repeatable).")
@click.option("--rm-ac", type=int, multiple=True, help="Remove criterion N (repeatable).")
@click.option("--check", type=int, multiple=True, help="Tick criterion N (repeatable).")
@click.option("--uncheck", type=int, multiple=True, help="Untick criterion N (repeatable).")
@click.option("--plan", help="Replace the Plan section; '' removes it.")
@click.option("--plan-file", type=click.File(), help="Read --plan from a file.")
@click.option("--note", help="Append a paragraph to Notes.")
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
    description: str | None,
    description_file: TextIO | None,
    ac: tuple[str, ...],
    rm_ac: tuple[int, ...],
    check: tuple[int, ...],
    uncheck: tuple[int, ...],
    plan: str | None,
    plan_file: TextIO | None,
    note: str | None,
    as_json: bool,
) -> None:
    """Change a task. Criterion numbers refer to the list before this edit."""
    repo = _repo()
    stored = repo.find(repo.resolve(task_id))
    changes = Edit(
        title=title,
        status=status,
        add_labels=add_label,
        rm_labels=rm_label,
        priority=priority,
        owner=owner,
        depends_on=[str(repo.resolve(d)) for d in depends_on],
        rm_depends_on=[str(repo.resolve(d)) for d in rm_depends_on],
        description=_text(description, description_file, "description"),
        add_criteria=ac,
        rm_criteria=rm_ac,
        check=check,
        uncheck=uncheck,
        plan=_text(plan, plan_file, "plan"),
        note=note,
    )
    if changes.is_empty():
        raise click.UsageError("nothing to change")
    _report(repo.save(stored, changes.apply(stored.task)), as_json, "updated")


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
        _print_json([{"path": str(p.path), "message": p.message} for p in problems])
    else:
        for problem in problems:
            click.echo(str(problem))
    if problems:
        raise click.ClickException(f"{len(problems)} problem(s)")


@cli.command()
@click.argument("task_id", metavar="ID")
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
@click.argument("task_id", metavar="ID")
@click.argument("context")
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
@click.argument("task_id", metavar="ID")
@json_option
def archive(task_id: str, as_json: bool) -> None:
    """Move a task into its context's archive/."""
    repo = _repo()
    _report(repo.archive(repo.resolve(task_id)), as_json, "archived")


@cli.command()
@click.argument("task_id", metavar="ID")
@json_option
def restore(task_id: str, as_json: bool) -> None:
    """Move an archived task back out of archive/."""
    repo = _repo()
    _report(repo.restore(repo.resolve(task_id)), as_json, "restored")
