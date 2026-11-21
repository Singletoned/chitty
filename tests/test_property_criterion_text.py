import string
import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.ids import TaskId
from chitty.model import SECTION_ORDER, TaskError, parse
from tests.test_property_renumbering import criterion_bytes, section_bytes
from tests.ticket_strategies import ticket_texts


@st.composite
def criterion_cases(draw):
    source = draw(ticket_texts([TaskId("TASK", 1)]).filter(lambda text: bool(parse(text).criteria)))
    task = parse(source)
    index = draw(st.integers(min_value=1, max_value=len(task.criteria)))
    text = draw(st.text(alphabet=string.printable[:95], min_size=1).filter(str.strip))
    return task, index, text


class TestCriterionText(unittest.TestCase):
    @given(criterion_cases())
    def test_text_and_checked(self, case):
        task, index, text = case
        result = parse(task.with_criterion_text(index, text).render())
        self.assertEqual(result.criteria[index - 1].text, text.strip())
        self.assertEqual(result.criteria[index - 1].checked, task.criteria[index - 1].checked)

    @given(criterion_cases())
    def test_marker(self, case):
        task, index, text = case
        result = task.with_criterion_text(index, text)
        self.assertEqual(criterion_bytes(result, index - 1)[3], criterion_bytes(task, index - 1)[3])

    @given(criterion_cases())
    def test_other_items_and_sections(self, case):
        task, index, text = case
        result = task.with_criterion_text(index, text)
        for i in range(len(task.criteria)):
            if i != index - 1:
                self.assertEqual(criterion_bytes(result, i), criterion_bytes(task, i))
        for name in SECTION_ORDER:
            if name != "Acceptance Criteria":
                self.assertEqual(section_bytes(result, name), section_bytes(task, name))

    @given(criterion_cases())
    def test_count(self, case):
        task, index, text = case
        self.assertEqual(len(task.with_criterion_text(index, text).criteria), len(task.criteria))

    @given(criterion_cases())
    def test_idempotent(self, case):
        task, index, text = case
        once = task.with_criterion_text(index, text)
        self.assertEqual(once.with_criterion_text(index, text).render(), once.render())

    def test_invalid_arguments(self):
        task = parse(
            "---\ntitle: Example\nstatus: todo\ncreated: 2024-01-01\n---\n\n"
            "## Description\n\nExample\n\n## Acceptance Criteria\n\n- [x] Example\n"
        )
        for index, text in [(0, "text"), (2, "text"), (1, ""), (1, "a\nb")]:
            with self.subTest(index=index, text=text), self.assertRaises(TaskError):
                task.with_criterion_text(index, text)
