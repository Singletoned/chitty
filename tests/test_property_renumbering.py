import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.ids import TaskId, provisional_suffix
from chitty.renumbering import plan_renumbering, replace_ids

PREFIX = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=4)


def provisional_ids(prefix, seed, count):
    values = set()
    while len(values) < count:
        suffix = provisional_suffix(lambda bound: seed.randrange(bound))
        values.add(TaskId(prefix, suffix))
    return sorted(values)


class TestRenumberingProperties(unittest.TestCase):
    @given(
        prefix=PREFIX,
        used_numbers=st.sets(st.integers(1, 100), min_size=2).filter(
            lambda values: max(values) - min(values) + 1 > len(values)
        ),
        seed=st.randoms(),
    )
    def test_plan_allocates_sorted_ids_after_highest_used(self, prefix, used_numbers, seed):
        ids = provisional_ids(prefix, seed, 1 + seed.randrange(5))
        mapping = plan_renumbering({prefix: used_numbers}, ids)
        start = max(used_numbers) + 1
        self.assertEqual(
            mapping,
            {task_id: TaskId(prefix, start + index) for index, task_id in enumerate(ids)},
        )
        self.assertEqual(len(mapping), len(ids))
        self.assertTrue(all(new_id.number not in used_numbers for new_id in mapping.values()))

    @given(prefix=PREFIX, seed=st.randoms())
    def test_missing_prefix_starts_at_one(self, prefix, seed):
        ids = provisional_ids(prefix, seed, 1 + seed.randrange(4))
        self.assertEqual(
            list(plan_renumbering({}, ids).values()),
            [TaskId(prefix, number) for number in range(1, len(ids) + 1)],
        )

    @given(prefix=PREFIX, seed=st.randoms())
    def test_duplicate_and_numeric_ids_are_errors(self, prefix, seed):
        task_id = provisional_ids(prefix, seed, 1)[0]
        with self.assertRaisesRegex(ChittyError, str(task_id)):
            plan_renumbering({}, [task_id, task_id])
        with self.assertRaises(ChittyError):
            plan_renumbering({}, [TaskId(prefix, 1)])

    @given(
        prefix=PREFIX,
        seed=st.randoms(),
        filler=st.text(alphabet=" .,/()[]_\n", min_size=1, max_size=40),
    )
    def test_replace_mentions_only_at_specified_boundaries(self, prefix, seed, filler):
        old = provisional_ids(prefix, seed, 1)[0]
        new = TaskId(prefix, 123)
        mapping = {old: new}
        old_text = str(old)
        text = filler.join(
            [
                old_text,
                f"`{old_text}`",
                f"({old_text})",
                f"[{old_text}]",
                f'"{old_text}"',
                f"/{old_text}/",
                f"_{old_text}_",
                f"{old_text}--slug.md",
                f"{old_text}-foo",
                f"X{old_text}",
                f"-{old_text}",
                f"{old_text}Y",
                old_text.lower(),
                f"{prefix}-{old.number}".lower(),
            ]
        )
        # Build the oracle from explicitly selected occurrences, independent of regex.
        pieces = [
            (old_text, str(new)),
            (f"`{old_text}`", f"`{new}`"),
            (f"({old_text})", f"({new})"),
            (f"[{old_text}]", f"[{new}]"),
            (f'"{old_text}"', f'"{new}"'),
            (f"/{old_text}/", f"/{new}/"),
            (f"_{old_text}_", f"_{new}_"),
            (f"{old_text}--slug.md", f"{new}--slug.md"),
            (f"{old_text}-foo", f"{new}-foo"),
            (f"X{old_text}", f"X{old_text}"),
            (f"-{old_text}", f"-{old_text}"),
            (f"{old_text}Y", f"{old_text}Y"),
            (old_text.lower(), old_text.lower()),
            (f"{prefix}-{old.number}".lower(), f"{prefix}-{old.number}".lower()),
        ]
        self.assertEqual(text, filler.join(source for source, _ in pieces))
        expected = filler.join(result for _, result in pieces)
        rewritten = replace_ids(text, mapping)
        self.assertEqual(rewritten, expected)
        self.assertEqual(replace_ids(rewritten, mapping), rewritten)

    @given(text=st.text(alphabet=" .,/()[]_\n", max_size=100))
    def test_text_without_id_is_unchanged(self, text):
        self.assertEqual(replace_ids(text, {TaskId("TASK", "K7Q2MX"): TaskId("TASK", 1)}), text)


if __name__ == "__main__":
    unittest.main()
