import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.config import PROJECT_NAME_RE
from chitty.ids import TaskId, ticket_references
from tests import examples

PREFIXES = ("TASK", "TASKS", "HUMAN")
SEPARATORS = (" ", "\n", ",", ".", "`", "(", ")")


class TestTicketReferences(unittest.TestCase):
    @settings(max_examples=examples(150))
    @given(
        st.lists(st.tuples(st.sampled_from(PREFIXES), st.integers(1, 9999)), max_size=30), st.data()
    )
    def test_ids_are_returned_once_in_first_appearance_order(self, parts, data):
        separators = data.draw(
            st.lists(
                st.sampled_from(SEPARATORS),
                min_size=max(0, len(parts) - 1),
                max_size=max(0, len(parts) - 1),
            )
        )
        text = "".join(
            ("" if index == 0 else separators[index - 1]) + f"{prefix}-{number}"
            for index, (prefix, number) in enumerate(parts)
        )
        expected = list(dict.fromkeys(TaskId(prefix, number) for prefix, number in parts))
        self.assertEqual(ticket_references(text, PREFIXES, foreign=()), expected)

    @settings(max_examples=examples(100))
    @given(
        st.lists(
            st.tuples(st.sampled_from(PREFIXES), st.integers(1, 9999)),
            min_size=1,
            max_size=15,
            unique=True,
        ),
        st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-"),
        st.data(),
    )
    def test_preceding_ascii_word_or_hyphen_character_blocks_one_reference(self, parts, char, data):
        selected = data.draw(st.integers(min_value=0, max_value=len(parts) - 1))
        fragments = [f"{prefix}-{number}" for prefix, number in parts]
        fragments[selected] = char + fragments[selected]
        text = " ".join(fragments)
        expected = [
            TaskId(prefix, number)
            for index, (prefix, number) in enumerate(parts)
            if index != selected
        ]
        self.assertEqual(ticket_references(text, PREFIXES, foreign=()), expected)

    @settings(max_examples=examples(200))
    @given(st.text(), st.sets(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1)))
    def test_arbitrary_text_never_raises_and_matches_requested_prefix(self, text, prefixes):
        result = ticket_references(text, prefixes, foreign=())
        self.assertTrue(all(task_id.prefix in prefixes for task_id in result))
        self.assertTrue(all(str(task_id) in text.upper() for task_id in result))

    @settings(max_examples=examples(150))
    @given(
        st.lists(st.tuples(st.sampled_from(PREFIXES), st.integers(1, 9999)), max_size=30),
        st.from_regex(PROJECT_NAME_RE, fullmatch=True),
        st.data(),
    )
    def test_foreign_qualified_references_are_excluded(self, parts, name, data):
        separators = data.draw(
            st.lists(st.sampled_from(SEPARATORS), min_size=len(parts), max_size=len(parts))
        )
        qualified = data.draw(st.lists(st.booleans(), min_size=len(parts), max_size=len(parts)))
        quotes = data.draw(st.lists(st.booleans(), min_size=len(parts), max_size=len(parts)))
        fragments = [
            (name.title() + " " + ("`" if quote else "") if foreign else "") + f"{prefix}-{number}"
            for (prefix, number), foreign, quote in zip(parts, qualified, quotes, strict=True)
        ]
        text = "".join(
            ("," if foreign and sep == "." else sep) + fragment
            for sep, fragment, foreign in zip(separators, fragments, qualified, strict=True)
        )
        expected = list(
            dict.fromkeys(
                TaskId(*part) for part, foreign in zip(parts, qualified, strict=True) if not foreign
            )
        )
        all_ids = list(dict.fromkeys(TaskId(*part) for part in parts))
        self.assertEqual(ticket_references(text, PREFIXES, foreign=(name,)), expected)
        self.assertEqual(ticket_references(text, PREFIXES, foreign=()), all_ids)

    def test_foreign_name_boundary(self):
        for text in (
            "x_other TASK-9",
            ".other TASK-9",
            "other\nTASK-9",
            "other \nTASK-9",
            "other\tTASK-9",
            "other  TASK-9",
        ):
            with self.subTest(text=text):
                self.assertEqual(
                    ticket_references(text, PREFIXES, foreign=("other",)), [TaskId("TASK", 9)]
                )
        self.assertEqual(ticket_references("OTHER `TASK-9`", PREFIXES, foreign=("other",)), [])

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
                    ticket_references(text, PREFIXES, foreign=()),
                    [TaskId.parse(item) for item in expected],
                )
