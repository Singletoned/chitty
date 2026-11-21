import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.git import Commit, commits_missing_trailer, with_task_trailer
from chitty.ids import TaskId

TASK_ID = TaskId.parse("TASK-1")


line = st.one_of(
    st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126) | st.just("\t"),
        max_size=30,
    ),
    st.sampled_from(("\t", "Key: value", "Signed-off-by: A <a@example.com>")),
    st.sampled_from(("chitty: generated", "Task: TASK-1", "Task: TASK-10", "")),
)
message = (
    st.lists(line, min_size=1, max_size=15)
    .filter(lambda lines: bool(lines[0].strip()))
    .map(lambda lines: "\n".join(lines))
)


class TestTaskTrailer(unittest.TestCase):
    @given(message)
    def test_trailer_is_added_once_and_is_detected(self, source):
        result = with_task_trailer(source, TASK_ID)
        missing = commits_missing_trailer([Commit("", source)], TASK_ID)
        self.assertEqual(commits_missing_trailer([Commit("", result)], TASK_ID), [])
        self.assertEqual(with_task_trailer(result, TASK_ID), result)
        if not missing:
            self.assertEqual(result, source)
        else:
            self.assertTrue(result.startswith(source.rstrip()))
            self.assertEqual(
                sum(line.rstrip() == "Task: TASK-1" for line in result.splitlines()),
                sum(line.rstrip() == "Task: TASK-1" for line in source.splitlines()) + 1,
            )

    def test_fixed_examples(self):
        examples = (
            (
                "Fix\n\nSigned-off-by: A <a@example.com>",
                "Fix\n\nSigned-off-by: A <a@example.com>\nTask: TASK-1\n",
            ),
            ("Fix", "Fix\n\nTask: TASK-1\n"),
            ("Key: value", "Key: value\n\nTask: TASK-1\n"),
        )
        for source in ("", "  \n"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                with_task_trailer(source, TASK_ID)
        for source, expected in examples:
            with self.subTest(source=source):
                self.assertEqual(with_task_trailer(source, TASK_ID), expected)
