import unittest
from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from chitty.model import (
    ACCEPTANCE_CRITERIA,
    DESCRIPTION,
    NOTES,
    PLAN,
    SUMMARY,
    Task,
    TaskError,
    _text_lines,
    new_task,
    parse,
)

SECTIONS = (DESCRIPTION, ACCEPTANCE_CRITERIA, PLAN, NOTES, SUMMARY)
TEXT_CHARS = st.sampled_from("abc :-*`~|")
SPLIT_CHARS = st.sampled_from(["\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028"])
LINE = st.one_of(
    st.text(alphabet=TEXT_CHARS, max_size=8),
    st.builds(lambda pre, text: pre + text, SPLIT_CHARS, st.just("## Plan")),
    st.sampled_from(
        [
            "## Plan",
            "## Notes",
            "## Summary",
            "## Description",
            "##\tPlan",
            "## Notes\t",
            "### Plan",
            "### Notes",
            "```",
            "~~~",
            "````",
            "  ```",
            "```python",
        ]
    ),
)
BODY = st.lists(LINE, max_size=8).map("\n".join)


def base_task() -> Task:
    task = new_task("Property", date(2026, 1, 1), "Base description.", ["criterion"], {})
    task = task.with_section(PLAN, "Base plan.")
    task = task.with_note("Base notes.")
    return task.with_section(SUMMARY, "Base summary.")


def snapshot(task: Task, skip: str) -> dict[str, object]:
    sections: dict[str, object] = {name: task.section(name) for name in SECTIONS if name != skip}
    if skip != ACCEPTANCE_CRITERIA:
        sections[ACCEPTANCE_CRITERIA] = tuple(
            (criterion.checked, criterion.text) for criterion in task.criteria
        )
    return sections


class TestSectionProperty(unittest.TestCase):
    @given(section=st.sampled_from((DESCRIPTION, PLAN, NOTES, SUMMARY)), text=BODY)
    def test_with_section_keeps_text_in_its_section(self, section: str, text: str):
        task = base_task()
        try:
            edited = task.with_section(section, text)
        except TaskError:
            return
        reparsed = parse(edited.render())
        expected = "".join(_text_lines(text)).strip("\n")
        self.assertEqual(reparsed.section(section), expected or None)
        self.assertEqual(snapshot(reparsed, section), snapshot(task, section))

    @given(text=BODY)
    def test_with_note_appends_to_notes_only(self, text: str):
        task = base_task()
        try:
            edited = task.with_note(text)
        except TaskError:
            return
        reparsed = parse(edited.render())
        expected = "".join(_text_lines(text)).strip("\n")
        self.assertTrue((reparsed.section(NOTES) or "").endswith(expected))
        self.assertEqual(snapshot(reparsed, NOTES), snapshot(task, NOTES))


if __name__ == "__main__":
    unittest.main()
