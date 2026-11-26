import unittest

from chitty import model

BASE = "---\ntitle: Test\nstatus: todo\ncreated: 2026-01-01\n---\n\n## Description\n\nTest.\n\n"


class TestQuestionsSection(unittest.TestCase):
    def test_items_and_round_trip(self):
        text = BASE + "## Questions\n\n- [x] Which database?\n\n- [ ] Who owns the migration?\n"
        task = model.parse(text)
        self.assertEqual(
            task.questions,
            (
                model.Question(True, "Which database?", None),
                model.Question(False, "Who owns the migration?", None),
            ),
        )
        self.assertEqual(task.render(), text)

    def test_uppercase_checked(self):
        self.assertEqual(
            model.parse(BASE + "## Questions\n- [X] Q\n").questions,
            (model.Question(True, "Q", None),),
        )

    def test_continuation(self):
        self.assertEqual(
            model.parse(BASE + "## Questions\n- [ ] Q\n  more\n").questions,
            (model.Question(False, "Q more", None),),
        )

    def test_empty_item(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questions\n- [ ]\n")
        self.assertEqual(str(error.exception), "question 1 has no text")

    def test_nested_list(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questions\n- [ ] Q\n  - nested\n")
        self.assertEqual(str(error.exception), "question 1: nested lists are not allowed")

    def test_other_line_after_blank(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questions\n- [ ] Q\n\n  answer\n")
        self.assertEqual(
            str(error.exception),
            "'## Questions' may only contain '- [ ] ...' items; found 'answer'",
        )

    def test_unknown_section(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questionz\n")
        self.assertIn("unknown section 'Questionz'", str(error.exception))
        self.assertIn("Questions", str(error.exception))
