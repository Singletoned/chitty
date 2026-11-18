import json
import unittest
from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from chitty.ids import (
    PROVISIONAL_DIGITS,
    PROVISIONAL_LENGTH,
    PROVISIONAL_LETTERS,
    TaskId,
    provisional_suffix,
)
from chitty.model import TaskError, new_task, parse

PREFIX = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1)


def base_task():
    return new_task("Property", date(2026, 1, 1), "Description.", [], {})


class TestProvisionalProperties(unittest.TestCase):
    @given(prefix=PREFIX, seed=st.randoms())
    def test_suffix_round_trips(self, prefix, seed):
        suffix = provisional_suffix(lambda n: seed.randrange(n))
        self.assertEqual(len(suffix), PROVISIONAL_LENGTH)
        self.assertIn(suffix[0], PROVISIONAL_LETTERS)
        self.assertTrue(set(suffix) <= set(PROVISIONAL_LETTERS + PROVISIONAL_DIGITS))
        self.assertEqual(TaskId.parse(f"{prefix}-{suffix}").number, suffix)

    def test_suffix_uses_boundary_draws(self):
        self.assertEqual(provisional_suffix(lambda _n: 0), "AAAAAA")
        self.assertEqual(provisional_suffix(lambda n: n - 1), "Z99999")

    @given(provisional=st.booleans())
    def test_field_round_trips(self, provisional):
        task = base_task()
        if provisional:
            task = task.with_field("provisional", True)
        reparsed = parse(task.render())
        self.assertEqual(reparsed.frontmatter.provisional, True if provisional else None)
        self.assertEqual(reparsed.as_dict()["provisional"], True if provisional else None)
        self.assertIsNone(reparsed.with_field("provisional", None).frontmatter.provisional)
        with self.assertRaises(TaskError):
            reparsed.with_field("provisional", False)

    @given(text=st.text().filter(lambda value: value != "true"))
    def test_only_true_is_accepted(self, text):
        task = base_task()
        malformed = task.render().replace(
            "created: 2026-01-01\n", f"created: 2026-01-01\nprovisional: {json.dumps(text)}\n"
        )
        with self.assertRaises(TaskError) as caught:
            parse(malformed)
        self.assertIn("provisional", str(caught.exception))

    def test_true_parses(self):
        self.assertIs(
            parse(base_task().with_field("provisional", True).render()).frontmatter.provisional,
            True,
        )


if __name__ == "__main__":
    unittest.main()
