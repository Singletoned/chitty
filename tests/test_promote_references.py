import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.ids import TaskId, ticket_references

PREFIXES = ("TASK", "TASKS", "HUMAN")
SEPARATORS = (" ", "\n", ",", ".", "`", "(", ")")


class TestTicketReferences(unittest.TestCase):
    @settings(max_examples=150)
    @given(st.lists(st.tuples(st.sampled_from(PREFIXES), st.integers(1, 9999)), max_size=30))
    def test_ids_are_returned_once_in_first_appearance_order(self, parts):
        text = "".join(
            ("" if index == 0 else SEPARATORS[(index - 1) % len(SEPARATORS)]) + f"{prefix}-{number}"
            for index, (prefix, number) in enumerate(parts)
        )
        expected = list(dict.fromkeys(TaskId(prefix, number) for prefix, number in parts))
        self.assertEqual(ticket_references(text, PREFIXES), expected)

    @settings(max_examples=100)
    @given(
        st.tuples(st.sampled_from(PREFIXES), st.integers(1, 9999)),
        st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-"),
    )
    def test_preceding_ascii_word_or_hyphen_character_blocks_reference(self, part, char):
        prefix, number = part
        self.assertEqual(ticket_references(f"{char}{prefix}-{number}", PREFIXES), [])

    @settings(max_examples=200)
    @given(st.text(), st.sets(st.text(min_size=1)))
    def test_arbitrary_text_never_raises_and_matches_requested_prefix(self, text, prefixes):
        result = ticket_references(text, prefixes)
        self.assertTrue(all(task_id.prefix in prefixes for task_id in result))
        self.assertTrue(all(str(task_id) in text for task_id in result))

    def test_documented_examples(self):
        cases = {
            "see TASK-12.": ["TASK-12"],
            "`TASK-12`": ["TASK-12"],
            "TASK-1-2": ["TASK-1"],
            "TASK-12a": ["TASK-12A"],
            "TASKS-3": ["TASKS-3"],
            "XTASK-12": [],
            "task-12": [],
            "a-TASK-1": [],
            "TASK-012": [],
            "UTF-8": [],
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    ticket_references(text, PREFIXES),
                    [TaskId.parse(item) for item in expected],
                )
