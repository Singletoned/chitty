import re
import unittest

from hypothesis import find, given, settings

from chitty.ids import TaskId
from chitty.model import parse
from tests.ticket_strategies import ticket_texts

IDS = [TaskId.parse("TASK-1"), TaskId.parse("TASK-22")]


class TestTicketStrategies(unittest.TestCase):
    @given(ticket_texts(IDS))
    def test_round_trip(self, text):
        rendered = parse(text).render()
        self.assertEqual(parse(rendered).render(), rendered)

    def test_empty_ids(self):
        with self.assertRaises(ValueError):
            ticket_texts([])

    def check_find(self, predicate):
        find(ticket_texts(IDS), predicate, settings=settings(max_examples=2000, deadline=None))

    def test_uppercase_checked(self):
        self.check_find(lambda text: "\n- [X] " in text)

    def test_continuation(self):
        self.check_find(lambda text: re.search(r"(?m)^- \[[ xX]\] .+\n  Text ", text) is not None)

    def test_plan_present(self):
        self.check_find(lambda text: "\n## Plan\n" in text)

    def test_plan_absent(self):
        self.check_find(lambda text: "\n## Plan\n" not in text)

    def test_title_id(self):
        self.check_find(lambda text: has_id(parse(text).frontmatter.title))

    def test_labels_id(self):
        self.check_find(lambda text: any(has_id(x) for x in parse(text).frontmatter.labels))

    def test_owner_id(self):
        self.check_find(lambda text: has_id(parse(text).frontmatter.owner or ""))

    def test_parent_id(self):
        self.check_find(lambda text: id_field_matches(parse(text).frontmatter.parent))

    def test_depends_on_id(self):
        self.check_find(
            lambda text: any(TaskId.parse(x) in IDS for x in parse(text).frontmatter.depends_on)
        )

    def test_moved_from_id(self):
        self.check_find(lambda text: id_field_matches(parse(text).frontmatter.moved_from))

    def test_suffix_dash(self):
        self.check_find(lambda text: "TASK-1-x" in text and "TASK-12" not in text)

    def test_suffix_letter(self):
        self.check_find(lambda text: "TASK-1A" in text and "TASK-12" not in text)

    def test_prefix_letter(self):
        self.check_find(lambda text: "XTASK-1" in text and "TASK-12" not in text)

    def test_prefix_dash(self):
        self.check_find(lambda text: "X-TASK-1" in text and "TASK-12" not in text)


def id_field_matches(value):
    return value is not None and TaskId.parse(value) in IDS


def has_id(value):
    return any(
        re.search(r"(?<![A-Za-z0-9-])" + re.escape(str(x)) + r"(?![A-Za-z0-9])", value) for x in IDS
    )
