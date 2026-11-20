from hypothesis import given
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


@given(ticket_facts())
def test_blocker_markers_follow_rule(facts):
    blocking = blocking_ids(facts)
    shuffled = list(reversed(facts))
    assert blocking_ids(shuffled) == blocking
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
        assert blocker_marker(fact, blocking) == expected
