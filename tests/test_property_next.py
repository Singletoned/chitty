"""Properties of pure next-ticket selection."""

import random
import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.selection import STATUSES as PICK_ORDER
from chitty.selection import DependencyFact, TicketFacts, choose, skip_reason

STATUSES = ("review", "doing", "todo", "done", "backlog", "blocked")
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
        owner=st.sampled_from((None, "agent", "human")),
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

    @settings(max_examples=300)
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

    @settings(max_examples=200)
    @given(facts_strategy())
    def test_skip_reason_agrees_with_single_ticket_choice(self, facts):
        for fact in facts:
            if fact.status in {"review", "doing", "todo"} and not fact.archived:
                self.assertEqual(
                    skip_reason(fact) is None, choose((fact,), order=PICK_ORDER) == fact
                )
            if fact.status in {"done", "backlog", "blocked"}:
                self.assertIsNone(skip_reason(fact))
