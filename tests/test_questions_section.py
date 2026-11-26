import unittest

from chitty import model
from chitty.ids import TaskId
from chitty.renumbering import rewrite_task

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

    def test_answer_and_round_trip(self):
        text = (
            BASE + "## Questions\n\n- [x] Which database?\n\n"
            "  Postgres, because we already run it.\n\n- [ ] Who owns the migration?\n"
        )
        task = model.parse(text)
        self.assertEqual(
            task.questions,
            (
                model.Question(True, "Which database?", "Postgres, because we already run it."),
                model.Question(False, "Who owns the migration?", None),
            ),
        )
        self.assertEqual(task.render(), text)

    def test_answer_lines(self):
        for blank in ("", "   "):
            with self.subTest(blank=blank):
                text = BASE + f"## Questions\n- [ ] Q\n{blank}\n  Part one\n\tpart two\n"
                self.assertEqual(
                    model.parse(text).questions,
                    (model.Question(False, "Q", "Part one part two"),),
                )

    def test_second_answer_paragraph_is_rejected(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questions\n- [ ] Q\n\n  First\n\n  Second\n")
        self.assertEqual(str(error.exception), "question 1: an answer must be one paragraph")

    def test_renumber_question_and_answer(self):
        text = (
            "---\ntitle: T\nstatus: todo\ncreated: 2026-11-23\n---\n\n"
            "## Description\n\nD.\n\n## Acceptance Criteria\n\n- [ ] A\n\n"
            "## Questions\n\n- [ ] Does TASK-7 block TASK-70?\n\n  Yes, see TASK-7.\n"
        )
        task = rewrite_task(model.parse(text), {TaskId("TASK", 7): TaskId("TASK", 12)})
        self.assertEqual(
            task.questions,
            (model.Question(False, "Does TASK-12 block TASK-70?", "Yes, see TASK-12."),),
        )

    def test_unindented_line_after_blank_is_rejected(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questions\n- [ ] Q\n\nanswer\n")
        self.assertEqual(
            str(error.exception),
            "'## Questions' may only contain '- [ ] ...' items; found 'answer'",
        )

    def test_unknown_section(self):
        with self.assertRaises(model.TaskError) as error:
            model.parse(BASE + "## Questionz\n")
        self.assertIn("unknown section 'Questionz'", str(error.exception))
        self.assertIn("Questions", str(error.exception))
