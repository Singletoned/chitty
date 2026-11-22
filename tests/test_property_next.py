"""Properties of pure next-ticket selection."""

import random
import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.selection import STATUSES as PICK_ORDER
from chitty.selection import (
    DependencyFact,
    TicketFacts,
    choose,
    dependency_marker,
    skip_reason,
)
from tests import examples

STATUSES = (
    "review",
    "doing",
    "todo",
    "done",
    "backlog",
    "blocked",
    "planning",
    "cold-read",
    "error",
)
PRIORITIES = ("high", "medium", None, "low")
TEST_STATUS_RANK = {status: i for i, status in enumerate(("review", "doing", "todo"))}
TEST_PRIORITY_RANK = {"high": 0, "medium": 1, None: 1, "low": 2}


@st.composite
def facts_strategy(draw):
    dependency = st.lists(st.sampled_from(("done", "unfinished", "broken")), max_size=2).map(
        lambda states: tuple(DependencyFact("TASK-900", state, "failure") for state in states)
    )
    fact = st.builds(
        TicketFacts,
        id=st.integers(min_value=1, max_value=999).map(lambda n: f"TASK-{n}"),
        context=st.sampled_from(("work", "human", "other")),
        status=st.sampled_from(STATUSES),
        priority=st.sampled_from(PRIORITIES),
        owner=st.sampled_from((None, "agent", "human", "untestable")),
        archived=st.booleans(),
        locked=st.booleans(),
        dependencies=dependency,
    )
    # Most samples contain several eligible tickets, making ordering meaningful.
    preferred = st.builds(
        TicketFacts,
        id=st.integers(min_value=1, max_value=999).map(lambda n: f"TASK-{n}"),
        context=st.just("work"),
        status=st.sampled_from(("review", "doing", "todo")),
        priority=st.sampled_from(PRIORITIES),
        owner=st.none(),
        archived=st.just(False),
        locked=st.just(False),
        dependencies=st.just(()),
    )
    count = draw(st.integers(min_value=2, max_value=5))
    return draw(st.lists(preferred, min_size=count, max_size=count) | st.lists(fact, max_size=20))


def independently_choosable(fact, mode=None, owner=None):
    allowed = {"review", "doing", "todo"}
    if mode == "work":
        allowed = {"doing", "todo"}
    elif mode == "review":
        allowed = {"review"}
    return (
        not fact.archived
        and not fact.locked
        and fact.context != "human"
        and fact.owner != "human"
        and fact.status in allowed
        and (fact.owner == owner if owner is not None else fact.owner is None)
        and not (fact.status == "todo" and any(d.state != "done" for d in fact.dependencies))
    )


class TestPropertyNext(unittest.TestCase):
    def test_unfinished_and_broken_todo_dependencies_are_excluded(self):
        blocked = TicketFacts(
            "TASK-1",
            "work",
            "todo",
            "high",
            None,
            False,
            False,
            (DependencyFact("TASK-900", "unfinished"),),
        )
        broken = TicketFacts(
            "TASK-2",
            "work",
            "todo",
            "high",
            None,
            False,
            False,
            (DependencyFact("TASK-901", "broken", "missing"),),
        )
        ready = TicketFacts("TASK-3", "work", "todo", "low", None, False, False)
        self.assertEqual(choose((ready, blocked, broken), order=PICK_ORDER), ready)

    @settings(max_examples=examples(300))
    @given(
        facts_strategy(),
        st.sampled_from((None, "work", "review")),
        st.sampled_from((None, "agent")),
        st.permutations(PICK_ORDER),
    )
    def test_choice_obeys_filters_and_independent_order(self, facts, mode, owner, order):
        # Shuffle so source ordering cannot accidentally satisfy ranking.
        random.Random(len(facts) * 173 + sum(map(len, (f.id for f in facts)))).shuffle(facts)
        selected = choose(tuple(facts), modes=(mode,) if mode else (), owner=owner, order=order)
        expected = sorted(
            (fact for fact in facts if independently_choosable(fact, mode, owner)),
            key=lambda f: (
                order.index(f.status),
                TEST_PRIORITY_RANK[f.priority],
                (f.id.rsplit("-", 1)[0], int(f.id.rsplit("-", 1)[1])),
            ),
        )
        self.assertEqual(selected, expected[0] if expected else None)
        if selected is not None:
            self.assertTrue(independently_choosable(selected, mode, owner))

    @settings(max_examples=examples(300))
    @given(facts_strategy())
    def test_dependency_marker_matches_independent_expectation(self, facts):
        for fact in facts:
            expected = None
            if not fact.archived and fact.status != "done":
                broken = next((d for d in fact.dependencies if d.state == "broken"), None)
                unfinished = [d.reference for d in fact.dependencies if d.state == "unfinished"]
                if broken:
                    expected = f"💔 {fact.id} depends on {broken.reference}: {broken.error}"
                elif unfinished:
                    expected = f"🔗 waits on {', '.join(unfinished)}"
            self.assertEqual(dependency_marker(fact), expected)

    @settings(max_examples=examples(300))
    @given(facts_strategy(), st.booleans())
    def test_untestable_marker_only_replaces_owned_skip_reason(self, facts, include_owner):
        for fact in facts:
            expected = None
            if not fact.archived and fact.status in TEST_STATUS_RANK:
                if fact.locked:
                    expected = "🏃 running"
                elif fact.context == "human" or fact.owner == "human":
                    expected = "👤 human"
                elif include_owner and fact.owner is not None:
                    expected = f"👤 {fact.owner}"
                elif fact.status == "todo":
                    unfinished = [d.reference for d in fact.dependencies if d.state == "unfinished"]
                    broken = next((d for d in fact.dependencies if d.state == "broken"), None)
                    if broken:
                        expected = f"💔 {fact.id} depends on {broken.reference}: {broken.error}"
                    elif unfinished:
                        expected = f"🔗 waits on {', '.join(unfinished)}"
            actual = skip_reason(fact, include_owner=include_owner)
            if expected == "👤 untestable":
                self.assertEqual(actual, "🙋 untestable")
            else:
                self.assertEqual(actual, expected)

    @settings(max_examples=examples(200))
    @given(facts_strategy())
    def test_skip_reason_agrees_with_single_ticket_choice(self, facts):
        for fact in facts:
            if fact.status in {"review", "doing", "todo"} and not fact.archived:
                self.assertEqual(
                    skip_reason(fact) is None, choose((fact,), order=PICK_ORDER) == fact
                )
            if fact.status in {"done", "backlog", "blocked"}:
                self.assertIsNone(skip_reason(fact))
