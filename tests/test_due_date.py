import os
import string
import unittest
from datetime import date

from click.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.cli import cli
from chitty.model import TaskError, parse, render_scalar
from tests import examples
from tests.support import RepoTestCase

TEXT = (
    "---\ntitle: Test\nstatus: todo\ncreated: 2026-11-23\n"
    "moved_from: HUMAN-3\n---\n\n## Description\n\nTest.\n"
)
DUE = "due: 2026-12-01\n"
WITH_DUE = TEXT.replace("moved_from:", DUE + "moved_from:")


class TestDueDate(unittest.TestCase):
    def test_parse_render_json(self):
        task = parse(WITH_DUE)
        self.assertEqual(task.frontmatter.due, date(2026, 12, 1))
        self.assertEqual(task.render(), WITH_DUE)
        self.assertEqual(task.as_dict()["due"], "2026-12-01")

    def test_missing(self):
        task = parse(TEXT)
        self.assertIsNone(task.frontmatter.due)
        self.assertIsNone(task.as_dict()["due"])

    def test_with_field(self):
        task = parse(TEXT)
        for value in (date(2026, 12, 1), "2026-12-01"):
            updated = task.with_field("due", value)
            self.assertEqual(updated.render(), WITH_DUE)
            self.assertEqual(updated.with_field("due", None).render(), TEXT)

    def test_malformed(self):
        for value, message in (
            ("01-12-2026", "'01-12-2026' is not an ISO 8601 date (YYYY-MM-DD)"),
            (
                "2026-13-01",
                (
                    "Input should be a valid date or datetime, "
                    "month value is outside expected range of 1-12"
                ),
            ),
        ):
            with self.subTest(value=value), self.assertRaises(TaskError) as error:
                parse(TEXT.replace("moved_from:", f"due: {value}\nmoved_from:"))
            self.assertEqual(str(error.exception), f"due: {message}")

    @settings(max_examples=examples(50))
    @given(st.dates())
    def test_dates(self, value):
        text = parse(TEXT).with_field("due", value).render()
        task = parse(text)
        self.assertEqual(task.frontmatter.due, value)
        self.assertEqual(task.render(), text)

    @settings(max_examples=examples(50))
    @given(st.text(alphabet=string.printable[:95]))
    def test_strings(self, value):
        text = TEXT.replace("moved_from:", f"due: {render_scalar(value)}\nmoved_from:")
        try:
            parse(text)
        except TaskError as error:
            self.assertTrue(str(error).startswith("due: "), str(error))


class TestDueCheck(RepoTestCase):
    def test_check(self):
        directory = self.root / "chitty" / "tasks"
        directory.mkdir(parents=True)
        path = directory / "TASK-1--t.md"
        path.write_text(TEXT.replace("moved_from:", "due: 01-12-2026\nmoved_from:"))
        old = os.getcwd()
        try:
            os.chdir(self.root)
            result = CliRunner().invoke(cli, ["check"])
        finally:
            os.chdir(old)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn(
            f"{path}: due: '01-12-2026' is not an ISO 8601 date (YYYY-MM-DD)", result.output
        )
