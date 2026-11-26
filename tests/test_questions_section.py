import json
import os
import string
import unittest

from click.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st

from chitty import model
from chitty.cli import cli
from chitty.ids import TaskId
from chitty.renumbering import rewrite_task
from tests import examples
from tests.support import RepoTestCase

BASE = "---\ntitle: Test\nstatus: todo\ncreated: 2026-01-01\n---\n\n## Description\n\nTest.\n\n"


words = st.lists(
    st.text(alphabet=string.ascii_letters, min_size=1, max_size=12), min_size=1, max_size=3
).map(" ".join)
indent = st.sampled_from(("  ", "    ", "\t"))


@st.composite
def question_bodies(draw):
    count = draw(st.integers(min_value=1, max_value=5))
    items = []
    expected = []
    for index in range(1, count + 1):
        tick = draw(st.sampled_from((" ", "x", "X")))
        text = draw(words)
        lines = [f"- [{tick}] {text}\n"]
        if draw(st.booleans()):
            continuation = draw(words)
            lines.append(f"{draw(indent)}{continuation}\n")
            text += " " + continuation
        answer = None
        if draw(st.booleans()):
            lines.append("\n" * draw(st.integers(min_value=1, max_value=2)))
            answer_lines = draw(st.lists(words, min_size=1, max_size=2))
            for line in answer_lines:
                lines.append(f"{draw(indent)}{line}\n")
            answer = " ".join(answer_lines)
        items.append("".join(lines))
        expected.append({"index": index, "checked": tick != " ", "text": text, "answer": answer})
    body = items[0]
    for item in items[1:]:
        body += "\n" * draw(st.integers(min_value=1, max_value=2)) + item
    if draw(st.booleans()):
        body += "\n"
    return body, expected


class TestShowQuestions(RepoTestCase):
    def setUp(self):
        super().setUp()
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        self.path = self.root / "chitty/tasks/TASK-1--test.md"
        self.path.parent.mkdir(parents=True)

    def show(self, *args):
        result = CliRunner().invoke(cli, ["show", "TASK-1", *args], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return result.output

    def test_show_questions(self):
        self.path.write_text(
            BASE + "## Acceptance Criteria\n\n- [ ] Done\n\n"
            "## Questions\n\n- [x] Which database?\n\n"
            "  Postgres, because we already run it.\n\n- [ ] Who owns the migration?\n\n"
            "## Plan\n\nNext.\n"
        )
        lines = self.show().splitlines()
        start = lines.index("## Questions")
        self.assertEqual(
            lines[start : start + 5],
            [
                "## Questions",
                "",
                "1. [x] Which database?",
                "   Postgres, because we already run it.",
                "2. [ ] Who owns the migration?",
            ],
        )
        self.assertFalse(lines[start + 5].startswith(" "))
        self.assertLess(lines.index("## Acceptance Criteria"), start)
        self.assertLess(start, lines.index("## Plan"))
        self.assertEqual(
            json.loads(self.show("--json"))["questions"],
            [
                {
                    "index": 1,
                    "checked": True,
                    "text": "Which database?",
                    "answer": "Postgres, because we already run it.",
                },
                {"index": 2, "checked": False, "text": "Who owns the migration?", "answer": None},
            ],
        )

    def test_show_without_questions(self):
        self.path.write_text(BASE)
        self.assertNotIn("## Questions", self.show().splitlines())


class TestQuestionsSection(unittest.TestCase):
    def test_as_dict(self):
        text = (
            BASE + "## Questions\n\n- [x] Which database?\n\n"
            "  Postgres, because we already run it.\n\n- [ ] Who owns the migration?\n"
        )
        self.assertEqual(
            model.parse(text).as_dict()["questions"],
            [
                {
                    "index": 1,
                    "checked": True,
                    "text": "Which database?",
                    "answer": "Postgres, because we already run it.",
                },
                {"index": 2, "checked": False, "text": "Who owns the migration?", "answer": None},
            ],
        )
        self.assertEqual(model.parse(BASE).as_dict()["questions"], [])

    @settings(max_examples=examples(50))
    @given(question_bodies())
    def test_generated_questions(self, generated):
        body, expected = generated
        text = BASE + "## Questions\n\n" + body
        task = model.parse(text)
        self.assertEqual(task.render(), text)
        self.assertEqual(task.as_dict()["questions"], expected)

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
