"""Pure ticket eligibility and ordering rules for next-ticket selection."""

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


STATUSES = ("review", "doing", "todo")
STATUS_RANK = {status: rank for rank, status in enumerate(STATUSES)}
MODE_STATUSES: dict[str, tuple[str, ...]] = {"work": ("doing", "todo"), "review": ("review",)}


def mode_statuses(modes: tuple[str, ...]) -> set[str] | None:
    """Return allowed statuses, or None when no mode limits the choice."""
    if not modes:
        return None
    return {status for mode in modes for status in MODE_STATUSES[mode]}


PRIORITY_RANK = {"high": 0, "medium": 1, None: 1, "low": 2}


def _id_key(value: str) -> TaskId:
    return TaskId.parse(value)


def skip_reason(fact: TicketFacts, *, include_owner: bool = True) -> str | None:
    """Explain why an active ticket cannot be selected, if applicable."""
    if fact.archived or fact.status not in STATUS_RANK:
        return None
    if fact.locked:
        return "▶ running"
    if fact.context == "human" or fact.owner == "human":
        return "👤 human"
    if include_owner and fact.owner is not None:
        return f"👤 {fact.owner}"
    if fact.status != "todo":
        return None
    unfinished: list[str] = []
    for dependency in fact.dependencies:
        if dependency.state == "broken":
            return f"⚠️ {fact.id} depends on {dependency.reference}: {dependency.error}"
        if dependency.state == "unfinished":
            unfinished.append(dependency.reference)
    if unfinished:
        return f"🔒 waits on {', '.join(unfinished)}"
    return None


def choose(
    facts: tuple[TicketFacts, ...],
    *,
    modes: tuple[Literal["work", "review"], ...] = (),
    owner: str | None = None,
) -> TicketFacts | None:
    """Return the first selectable ticket in status, priority, ID order."""
    statuses = mode_statuses(modes)
    candidates: list[TicketFacts] = []
    for fact in facts:
        if fact.archived or fact.status not in STATUS_RANK:
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
        key=lambda fact: (STATUS_RANK[fact.status], PRIORITY_RANK[fact.priority], _id_key(fact.id)),
        default=None,
    )
