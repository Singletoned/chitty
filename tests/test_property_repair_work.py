import unittest
from pathlib import PurePosixPath

from hypothesis import given
from hypothesis import strategies as st

from chitty.git import has_work_beyond_tickets

segments = st.text(alphabet="abcXYZ012_-é", min_size=1, max_size=8)
paths = st.lists(segments, min_size=1, max_size=4).map(lambda parts: PurePosixPath(*parts))


class TestRepairWorkProperties(unittest.TestCase):
    @given(st.lists(paths), st.lists(paths))
    def test_matches_containment_and_is_order_duplicate_invariant(self, changed, directories):
        expected = any(
            not any(path.is_relative_to(directory) for directory in directories) for path in changed
        )
        self.assertEqual(has_work_beyond_tickets(changed, directories), expected)
        self.assertEqual(has_work_beyond_tickets(changed[::-1], directories * 2), expected)
        self.assertEqual(has_work_beyond_tickets(changed * 2, directories[::-1]), expected)

    @given(st.lists(paths), st.lists(paths), paths)
    def test_adding_path_never_turns_work_into_no_work(self, changed, directories, path):
        if has_work_beyond_tickets(changed, directories):
            self.assertTrue(has_work_beyond_tickets([*changed, path], directories))

    def test_path_edge_cases(self):
        directory = PurePosixPath("chitty/tasks")
        self.assertFalse(has_work_beyond_tickets([], [directory]))
        self.assertFalse(has_work_beyond_tickets([directory], [directory]))
        self.assertFalse(has_work_beyond_tickets([directory / "a.md"], [directory]))
        self.assertTrue(has_work_beyond_tickets([PurePosixPath("src/a.py")], [directory]))
        self.assertTrue(has_work_beyond_tickets([PurePosixPath("chitty/tasksX/a.md")], [directory]))
        self.assertTrue(has_work_beyond_tickets([directory], []))
