import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.ids import TaskId
from chitty.model import parse
from chitty.store import Edit
from tests import examples
from tests.test_cli import CliTestCase
from tests.ticket_strategies import ticket_texts


class TestDifficultyCli(CliTestCase):
    def test_add_edit_and_unset(self):
        self.run_cli("add", "T", "-d", "x", "-p", "low", "--difficulty", "high")
        path = next((self.root / "chitty" / "tasks").glob("TASK-1--*.md"))
        self.assertIn("priority: low\ndifficulty: high\n", path.read_text())
        self.assertIn("difficulty: high", self.run_cli("show", "TASK-1").output)
        self.assertEqual(self.json("show", "TASK-1")["difficulty"], "high")
        self.run_cli("edit", "TASK-1", "--difficulty", "low")
        self.assertIn("difficulty: low\n", path.read_text())
        self.assertIn("changed difficulty", path.read_text())
        self.run_cli("edit", "TASK-1", "--difficulty", "")
        self.assertNotIn("difficulty:", path.read_text())
        self.assertIsNone(self.json("show", "TASK-1")["difficulty"])

    def test_invalid_options_do_not_write(self):
        result = self.run_cli("add", "T", "-d", "x", "--difficulty", "hard", exit_code=2)
        self.assertIn("'hard' is not one of", result.output)
        self.assertFalse(list((self.root / "chitty" / "tasks").glob("TASK-*.md")))
        self.run_cli("add", "T", "-d", "x")
        path = next((self.root / "chitty" / "tasks").glob("TASK-1--*.md"))
        before = path.read_bytes()
        result = self.run_cli("edit", "TASK-1", "--difficulty", "hard", exit_code=2)
        self.assertIn("'hard' is not one of", result.output)
        self.assertEqual(path.read_bytes(), before)

    def test_check_rejects_invalid_frontmatter(self):
        self.run_cli("add", "T", "-d", "x")
        path = next((self.root / "chitty" / "tasks").glob("TASK-1--*.md"))
        path.write_text(
            path.read_text().replace("status: todo\n", "status: todo\ndifficulty: hard\n")
        )
        result = self.run_cli("check", exit_code=1)
        self.assertIn("difficulty: Input should be 'low', 'medium' or 'high'", result.output)


class TestDifficultyProperty(unittest.TestCase):
    @settings(max_examples=examples(50))
    @given(ticket_texts([TaskId("TASK", 1)]), st.sampled_from(("low", "medium", "high", "")))
    def test_apply_preserves_other_fields_and_sections(self, text, difficulty):
        original = parse(text)
        changed = Edit(difficulty=difficulty).apply(original)
        before = original.as_dict()
        after = changed.as_dict()
        self.assertEqual(after.pop("difficulty"), difficulty or None)
        before.pop("difficulty")
        self.assertEqual(after, before)
