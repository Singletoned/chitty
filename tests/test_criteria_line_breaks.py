import string
import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.ids import TaskId
from chitty.model import parse
from tests import examples
from tests.test_cli import CliTestCase
from tests.ticket_strategies import ticket_texts

OTHER_LINE_BREAKS = "\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"


@st.composite
def criterion_cases(draw):
    source = draw(ticket_texts([TaskId("TASK", 1)]).filter(lambda text: bool(parse(text).criteria)))
    task = parse(source)
    index = draw(st.integers(min_value=1, max_value=len(task.criteria)))
    alphabet = string.printable[:95] + OTHER_LINE_BREAKS
    text = draw(
        st.text(alphabet=alphabet, min_size=1).filter(
            lambda value: bool(value.strip()) and any(c in value for c in OTHER_LINE_BREAKS)
        )
    )
    return task, index, text


class TestCriteriaLineBreaks(unittest.TestCase):
    @settings(max_examples=examples(100))
    @given(criterion_cases())
    def test_replacement_round_trip(self, case):
        task, index, text = case
        result = parse(task.with_criteria([], [], [(index, text)], [], []).render())
        self.assertEqual(len(result.criteria), len(task.criteria))
        for number, (before, after) in enumerate(zip(task.criteria, result.criteria), start=1):
            if number == index:
                self.assertEqual((after.text, after.checked), (text.strip(), False))
            else:
                self.assertEqual((after.text, after.checked), (before.text, before.checked))

    def test_replacement_strips_trailing_separators(self):
        source = (
            "---\ntitle: Example\nstatus: todo\ncreated: 2024-01-01\n---\n\n"
            "## Description\n\nExample\n\n## Acceptance Criteria\n\n- [ ] old\n"
        )
        for text in ("a\u2028", "a\n", "a\r"):
            with self.subTest(text=text):
                task = parse(source).with_criteria([], [], [(1, text)], [], [])
                self.assertEqual(parse(task.render()).criteria[0].text, "a")

    def test_parse_and_render_unicode_separator(self):
        source = (
            "---\ntitle: Example\nstatus: todo\ncreated: 2024-01-01\n---\n\n"
            "## Description\n\nExample\n\n## Acceptance Criteria\n\n- [ ] a\u2028b\n"
        )
        task = parse(source)
        self.assertEqual([item.text for item in task.criteria], ["a\u2028b"])
        self.assertEqual(task.render(), source)


class TestCliCriteriaLineBreaks(CliTestCase):
    def test_edit_unicode_separator(self):
        self.run_cli("add", "T", "-d", "x", "--ac", "one")
        self.run_cli("edit", "TASK-1", "--set-ac", "1", "a\u2028b")
        self.assertEqual(self.json("show", "TASK-1")["acceptance_criteria"][0]["text"], "a\u2028b")
