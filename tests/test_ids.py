import unittest

from chitty.ids import IdError, TaskId, filename, next_number, parse_filename, resolve, slugify


class TestTaskId(unittest.TestCase):
    def test_parse_and_str(self):
        task_id = TaskId.parse("TASK-13")
        self.assertEqual(task_id, TaskId("TASK", 13))
        self.assertEqual(str(task_id), "TASK-13")

    def test_rejects_padding_zero_but_canonicalizes_case(self):
        self.assertEqual(TaskId.parse("task-1"), TaskId("TASK", 1))
        self.assertEqual(TaskId.parse("Human-2"), TaskId("HUMAN", 2))
        for text in ("TASK-013", "TASK-0", "TASK1", "TASK-", "-1"):
            with self.subTest(text=text), self.assertRaises(IdError):
                TaskId.parse(text)

    def test_resolve_shorthand(self):
        self.assertEqual(resolve("13", "TASK"), TaskId("TASK", 13))
        self.assertEqual(resolve("HUMAN-2", "TASK"), TaskId("HUMAN", 2))
        with self.assertRaises(IdError):
            resolve("013", "TASK")


class TestSlugs(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("Add search to the task list"), "add-search-to-the-task-list")
        self.assertEqual(slugify("  Fix -- login!! "), "fix-login")
        self.assertEqual(slugify("日本語"), "")

    def test_slug_is_truncated_without_trailing_hyphen(self):
        slug = slugify("a" * 59 + " bcd")
        self.assertEqual(slug, "a" * 59)

    def test_filename_round_trip(self):
        task_id = TaskId("TASK", 13)
        self.assertEqual(filename(task_id, "add-search"), "TASK-13--add-search.md")
        self.assertEqual(filename(task_id, ""), "TASK-13.md")
        self.assertEqual(parse_filename("TASK-13--add-search.md"), (task_id, "add-search"))
        self.assertEqual(parse_filename("TASK-13.md"), (task_id, ""))

    def test_parse_filename_rejects_bad_names(self):
        for name in ("TASK-13--add--search.md", "TASK-13--.md", "TASK-13-add.md", "TASK-13.txt"):
            with self.subTest(name=name), self.assertRaises(IdError):
                parse_filename(name)


class TestAlphanumericTaskId(unittest.TestCase):
    def test_parses_suffix_and_preserves_numeric_type(self):
        self.assertEqual(str(TaskId.parse("backlog-k3f9x2ab")), "BACKLOG-K3F9X2AB")
        self.assertEqual(TaskId.parse("BACKLOG-0A"), TaskId("BACKLOG", "0A"))
        self.assertEqual(TaskId.parse("BACKLOG-48213907"), TaskId("BACKLOG", 48213907))

    def test_rejects_padded_numeric_id_with_updated_error(self):
        with self.assertRaisesRegex(IdError, "expected PREFIX-N or PREFIX-SUFFIX"):
            TaskId.parse("BACKLOG-013")

    def test_sorts_numeric_before_alphanumeric(self):
        values = [TaskId.parse(value) for value in ("BACKLOG-K3F9X2AB", "BACKLOG-12", "BACKLOG-0A")]
        self.assertEqual(
            [str(value) for value in sorted(values)],
            ["BACKLOG-12", "BACKLOG-0A", "BACKLOG-K3F9X2AB"],
        )

    def test_alphanumeric_filename_round_trip(self):
        task_id = TaskId.parse("BACKLOG-K3F9X2AB")
        self.assertEqual(parse_filename("BACKLOG-K3F9X2AB--x.md"), (task_id, "x"))


class TestNextNumber(unittest.TestCase):
    def test_next_number(self):
        self.assertEqual(next_number([]), 1)
        self.assertEqual(next_number([3, 1, 7]), 8)
