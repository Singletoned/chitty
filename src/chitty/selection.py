"""Pure ticket eligibility and ordering rules for next-ticket selection."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from chitty.ids import TaskId


@dataclass(frozen=True)
class DependencyFact:
    reference: str
    state: Literal["done", "unfinished", "broken"]
    error: str | None = None


@dataclass(frozen=True)
class TicketFacts:
    id: str
    context: str
    status: str
    priority: str | None
    owner: str | None
    archived: bool
    locked: bool
    dependencies: tuple[DependencyFact, ...] = ()
    labels: tuple[str, ...] = ()


STATUSES = ("review", "doing", "todo")
STATUS_RANK = {status: rank for rank, status in enumerate(STATUSES)}
MODE_STATUSES: dict[str, tuple[str, ...]] = {
    "work": ("doing", "todo"),
    "review": ("review",),
    "errors": ("error",),
}


def mode_statuses(modes: tuple[str, ...]) -> set[str] | None:
    """Return allowed statuses, or None when no mode limits the choice."""
    if not modes:
        return None
    return {status for mode in modes for status in MODE_STATUSES[mode]}


PRIORITY_RANK = {"high": 0, "medium": 1, None: 1, "low": 2}
UNTESTABLE_OWNER = "untestable"
DEPENDENCY_GLYPH = "🔗"
BLOCKER_GLYPH = "🚧"
BROKEN_DEPENDENCY_GLYPH = "💔"
HUMAN_GLYPH = "👤"
UNTESTABLE_GLYPH = "🙋"
RUNNING_GLYPH = "🏃"


def blocking_ids(facts: Iterable[TicketFacts]) -> set[str]:
    """Return IDs named by active tickets waiting on unfinished dependencies."""
    result: set[str] = set()
    for fact in facts:
        if fact.archived or fact.status == "done":
            continue
        result.update(
            str(TaskId.parse(dependency.reference))
            for dependency in fact.dependencies
            if dependency.state == "unfinished"
        )
    return result


def blocker_marker(fact: TicketFacts, blocking: set[str]) -> str | None:
    """Mark active chain endpoints that have waiting dependents."""
    if fact.archived or fact.status == "done":
        return None
    if any(dependency.state in {"unfinished", "broken"} for dependency in fact.dependencies):
        return None
    return BLOCKER_GLYPH if str(TaskId.parse(fact.id)) in blocking else None


def _id_key(value: str) -> TaskId:
    return TaskId.parse(value)


def skip_reason(fact: TicketFacts, *, include_owner: bool = True) -> str | None:
    """Explain why an active ticket cannot be selected, if applicable."""
    if fact.archived or fact.status not in STATUS_RANK:
        return None
    if fact.locked:
        return f"{RUNNING_GLYPH} running"
    if fact.context == "human" or fact.owner == "human":
        return f"{HUMAN_GLYPH} human"
    if include_owner and fact.owner is not None:
        # Give planners' untestable tickets a distinct list marker.
        glyph = UNTESTABLE_GLYPH if fact.owner == UNTESTABLE_OWNER else HUMAN_GLYPH
        return f"{glyph} {fact.owner}"
    if fact.status != "todo":
        return None
    return dependency_marker(fact)


def dependency_marker(fact: TicketFacts) -> str | None:
    """Describe unfinished dependencies, independently of selection status."""
    if fact.archived or fact.status == "done":
        return None
    unfinished: list[str] = []
    for dependency in fact.dependencies:
        if dependency.state == "broken":
            return (
                f"{BROKEN_DEPENDENCY_GLYPH} {fact.id} depends on "
                f"{dependency.reference}: {dependency.error}"
            )
        if dependency.state == "unfinished":
            unfinished.append(dependency.reference)
    if unfinished:
        return f"{DEPENDENCY_GLYPH} waits on {', '.join(unfinished)}"
    return None


def choose(
    facts: tuple[TicketFacts, ...],
    *,
    modes: tuple[Literal["work", "review", "errors"], ...] = (),
    owner: str | None = None,
    order: tuple[str, ...] = STATUSES,
) -> TicketFacts | None:
    """Return the first ticket in configured status, bug label, priority, ID order."""
    statuses = mode_statuses(modes)
    candidates: list[TicketFacts] = []
    for fact in facts:
        if fact.archived or fact.status not in order:
            continue
        if statuses is not None and fact.status not in statuses:
            continue
        if skip_reason(fact, include_owner=owner is None) is not None:
            continue
        if owner is not None and fact.owner != owner:
            continue
        candidates.append(fact)
    return min(
        candidates,
        key=lambda fact: (
            order.index(fact.status),
            "bug" not in fact.labels,
            PRIORITY_RANK[fact.priority],
            _id_key(fact.id),
        ),
        default=None,
    )
