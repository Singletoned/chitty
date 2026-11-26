import string
import unittest

from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from chitty.config import RepoConfig
from tests import examples


class PrioritiesConfigTests(unittest.TestCase):
    def config(self, **extra: object) -> RepoConfig:
        return RepoConfig.model_validate(
            {
                "format": 1,
                "default_context": "tasks",
                "autocommit": False,
                "contexts": {"tasks": {"prefix": "TASK"}},
                **extra,
            }
        )

    def assert_refused(self, priorities: list[str], message: str) -> None:
        with self.assertRaises(ValidationError) as caught:
            self.config(priorities=priorities)
        self.assertIn(message, str(caught.exception))

    def test_default(self) -> None:
        self.assertEqual(self.config().priorities, ["high", "medium", "", "low"])

    def test_missing_empty(self) -> None:
        self.assert_refused(
            ["high"], 'priorities must contain "" exactly once, to place tickets with no priority'
        )

    def test_repeated_empty(self) -> None:
        self.assert_refused(
            ["", ""], 'priorities must contain "" exactly once, to place tickets with no priority'
        )

    def test_duplicate_name(self) -> None:
        self.assert_refused(["a", "a", ""], "priorities lists 'a' twice")

    def test_surrounding_whitespace(self) -> None:
        self.assert_refused(
            [" a", ""],
            "priority ' a' must be one word or phrase on one line, without surrounding spaces",
        )

    @settings(max_examples=examples(50))
    @given(
        name=st.text(alphabet=string.ascii_letters, min_size=1, max_size=5),
        boundary=st.sampled_from("\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"),
        data=st.data(),
    )
    def test_line_break(self, name: str, boundary: str, data: st.DataObject) -> None:
        position = data.draw(st.integers(min_value=0, max_value=len(name)))
        name = name[:position] + boundary + name[position:]
        self.assert_refused(
            [name, ""],
            f"priority {name!r} must be one word or phrase on one line, without surrounding spaces",
        )
