import unittest

from chitty.ids import IdError, TaskId, filename, next_number, parse_filename, resolve, slugify


class TestTaskId(unittest.TestCase):
    def test_parse_and_str(self):
        task_id = TaskId.parse("TASK-13")
        self.assertEqual(task_id, TaskId("TASK", 13))
        self.assertEqual(str(task_id), "TASK-13")

    def test_rejects_padding_zero_and_lowercase(self):
        for text in ("TASK-013", "TASK-0", "task-1", "TASK1", "TASK-", "-1"):
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


class TestNextNumber(unittest.TestCase):
    def test_next_number(self):
        self.assertEqual(next_number([]), 1)
        self.assertEqual(next_number([3, 1, 7]), 8)
