import unittest

from hypothesis import example, given
from hypothesis import strategies as st

from chitty.model import STATUSES
from chitty.selection import DependencyFact, TicketFacts, blocker_marker, blocking_ids


@st.composite
def ticket_facts(draw):
    ids = draw(st.lists(st.integers(1, 6), unique=True, min_size=1, max_size=6))
    facts = []
    for number in ids:
        others = [f"TASK-{value}" for value in range(1, 7) if value != number] + ["TASK-99"]
        deps = draw(
            st.lists(
                st.tuples(
                    st.sampled_from(others), st.sampled_from(("done", "unfinished", "broken"))
                ),
                max_size=3,
            )
        )
        if any(state == "broken" for _, state in deps):
            first_broken = next(i for i, (_, state) in enumerate(deps) if state == "broken")
            deps = [item for item in deps[:first_broken] if item[1] != "broken"] + [
                deps[first_broken]
            ]
        dependencies = tuple(
            DependencyFact(reference.lower() if draw(st.booleans()) else reference, state)
            for reference, state in deps
        )
        facts.append(
            TicketFacts(
                f"TASK-{number}",
                draw(st.sampled_from(("work", "human"))),
                draw(st.sampled_from(STATUSES)),
                None,
                draw(st.sampled_from((None, "agent", "human", "untestable"))),
                draw(st.booleans()),
                draw(st.booleans()),
                dependencies,
            )
        )
    return facts


def check_blocker_rule(facts, get_blocking_ids, get_blocker_marker):
    expected_blocking = {
        dependency.reference.upper()
        for dependent in facts
        if not dependent.archived and dependent.status != "done"
        for dependency in dependent.dependencies
        if dependency.state == "unfinished"
    }
    blocking = get_blocking_ids(facts)
    shuffled = list(reversed(facts))
    assert blocking == expected_blocking
    assert get_blocking_ids(shuffled) == expected_blocking
    for fact in facts:
        expected = None
        if (
            not fact.archived
            and fact.status != "done"
            and not any(
                dependency.state in {"unfinished", "broken"} for dependency in fact.dependencies
            )
            and fact.id in blocking
        ):
            expected = "🚧"
        assert get_blocker_marker(fact, blocking) == expected


@given(ticket_facts())
def test_blocker_markers_follow_rule(facts):
    check_blocker_rule(facts, blocking_ids, blocker_marker)


def unfinished_marker_mutant(fact, blocking):
    if fact.archived or fact.status == "done":
        return None
    if any(dependency.state == "broken" for dependency in fact.dependencies):
        return None
    return "🚧" if fact.id in blocking else None


def inactive_dependents_mutant(facts):
    return {
        dependency.reference.upper()
        for fact in facts
        for dependency in fact.dependencies
        if dependency.state == "unfinished"
    }


def done_dependency_mutant(facts):
    return {
        dependency.reference.upper()
        for fact in facts
        if not fact.archived and fact.status != "done"
        for dependency in fact.dependencies
        if dependency.state == "done"
    }


def owner_lock_mutant(facts):
    return {
        dependency.reference.upper()
        for fact in facts
        if not fact.archived and fact.status != "done" and fact.owner is None and not fact.locked
        for dependency in fact.dependencies
        if dependency.state == "unfinished"
    }


def raw_reference_mutant(facts):
    return {
        dependency.reference
        for fact in facts
        if not fact.archived and fact.status != "done"
        for dependency in fact.dependencies
        if dependency.state == "unfinished"
    }


# A chain TASK-1 -> TASK-2 -> TASK-3: TASK-2 blocks TASK-1 but waits on TASK-3,
# so it gets no marker. Random draws reach this only sometimes, which let the
# unfinished-dependency mutant survive about one run in ten.
CHAIN = [
    TicketFacts(
        "TASK-1",
        "work",
        "todo",
        None,
        None,
        False,
        False,
        (DependencyFact("TASK-2", "unfinished"),),
    ),
    TicketFacts(
        "TASK-2",
        "work",
        "todo",
        None,
        None,
        False,
        False,
        (DependencyFact("TASK-3", "unfinished"),),
    ),
]


def run_property(get_blocking_ids, get_blocker_marker):
    @given(ticket_facts())
    @example(CHAIN)
    def property_test(facts):
        check_blocker_rule(facts, get_blocking_ids, get_blocker_marker)

    property_test()


class TestBlockerPropertyMutants(unittest.TestCase):
    def test_rule_rejects_each_wrong_implementation(self):
        mutants = (
            (blocking_ids, unfinished_marker_mutant),
            (inactive_dependents_mutant, blocker_marker),
            (done_dependency_mutant, blocker_marker),
            (owner_lock_mutant, blocker_marker),
            (raw_reference_mutant, blocker_marker),
        )
        for index, mutant in enumerate(mutants, start=1):
            with self.subTest(mutant=index), self.assertRaises(AssertionError):
                run_property(*mutant)
