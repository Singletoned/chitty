"""Strategies for valid, non-canonical ticket Markdown."""

import json
import string

from hypothesis import strategies as st

from chitty.ids import TaskId
from chitty.model import PRIORITIES, STATUSES


def ticket_texts(ids: list[TaskId]):
    if not ids:
        raise ValueError("ids must not be empty")
    return _ticket_texts(ids)


@st.composite
def _ticket_texts(draw, ids: list[TaskId]):
    identifier = st.sampled_from([str(task_id) for task_id in ids])
    free = st.text(alphabet=string.printable[:95], max_size=20)
    mention = identifier.flatmap(
        lambda value: st.sampled_from(
            [
                value,
                f"`{value}`",
                f"https://example.com/{value}",
                f"{value}-x",
                f"{value}A",
                f"X{value}",
                f"X-{value}",
            ]
        )
    )
    # Prefix text makes all generated prose safe from Markdown structural markers.
    prose = st.tuples(free, mention, free).map(lambda parts: "Text " + " ".join(parts))

    def scalar(value):
        return json.dumps(value, ensure_ascii=True)

    fields = [
        f"title: {scalar(draw(prose))}",
        f"status: {draw(st.sampled_from(STATUSES))}",
        f"created: {draw(st.dates()).isoformat()}",
    ]
    if draw(st.booleans()):
        fields.append(f"priority: {draw(st.sampled_from(PRIORITIES))}")
    if draw(st.booleans()):
        labels = draw(st.lists(prose, min_size=1, max_size=2, unique=True))
        fields.append(f"labels: {json.dumps(labels)}")
    if draw(st.booleans()):
        fields.append(f"owner: {scalar(draw(prose))}")
    if draw(st.booleans()):
        dependencies = draw(st.lists(identifier, min_size=1, max_size=len(ids), unique=True))
        fields.append(f"depends_on: {json.dumps(dependencies)}")
    for field in ("parent", "moved_from"):
        if draw(st.booleans()):
            fields.append(f"{field}: {draw(identifier)}")
    if draw(st.booleans()):
        fields.append("provisional: true")
    sections = ["## Description\n\n" + draw(prose) + "\n"]
    if draw(st.booleans()):
        lines = []
        for _ in range(draw(st.integers(min_value=1, max_value=2))):
            lines.append(f"- [{draw(st.sampled_from([' ', 'x', 'X']))}] {draw(prose)}\n")
            if draw(st.booleans()):
                lines.append("  " + draw(prose) + "\n")
        sections.append("## Acceptance Criteria\n\n" + "".join(lines))
    for name in ("Plan", "Notes", "Summary"):
        if draw(st.booleans()):
            sections.append(f"## {name}\n\n{draw(prose)}\n")
    sections.append("## History\n\n- 2024-01-01T00:00:00Z actor: " + draw(prose) + "\n")
    return "---\n" + "\n".join(fields) + "\n---\n\n" + "\n".join(sections)
