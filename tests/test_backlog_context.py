import os
import subprocess
import tomllib
from unittest import mock

from chitty.config import CHITTY_VERSION
from tests.test_cli import CliTestCase

BACKLOG = '\n[contexts.backlog]\nprefix = "BACKLOG"\nrandom_ids = true\n'


class TestRandomIds(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text() + BACKLOG)

    def add_backlog(self, *numbers: int, exit_code: int = 0):
        with mock.patch("chitty.store._random_number", side_effect=numbers) as patched:
            args = ["add", "Idea", "-c", "backlog", "-s", "backlog"]
            result = self.run_cli(*args, exit_code=exit_code)
        return result, patched

    def test_add_gives_a_random_number(self):
        result, _ = self.add_backlog(48213907)
        self.assertIn("BACKLOG-48213907", result.stdout)
        self.assertTrue((self.root / "chitty/backlog/BACKLOG-48213907--idea.md").exists())
        self.assertEqual(self.json("add", "Sequential", "-d", "x")["id"], "TASK-1")
        self.run_cli("check")

    def test_retries_a_number_already_used(self):
        self.add_backlog(48213907)
        result, patched = self.add_backlog(48213907, 12345678)
        self.assertIn("BACKLOG-12345678", result.stdout)
        self.assertEqual(patched.call_count, 2)

    def test_retries_a_number_used_only_on_another_branch(self):
        git = ["git", "-C", str(self.root)]
        subprocess.run([*git, "init", "--quiet", "-b", "main"], check=True)
        subprocess.run([*git, "config", "user.email", "test@example.com"], check=True)
        subprocess.run([*git, "config", "user.name", "Test"], check=True)
        subprocess.run([*git, "add", "--all"], check=True)
        subprocess.run([*git, "commit", "--quiet", "-m", "setup"], check=True)
        subprocess.run([*git, "switch", "--quiet", "-c", "other"], check=True)
        self.add_backlog(55555555)
        subprocess.run([*git, "add", "--all"], check=True)
        subprocess.run([*git, "commit", "--quiet", "-m", "branch idea"], check=True)
        subprocess.run([*git, "switch", "--quiet", "main"], check=True)
        self.assertFalse((self.root / "chitty/backlog/BACKLOG-55555555--idea.md").exists())

        result, _ = self.add_backlog(55555555, 66666666)
        self.assertIn("BACKLOG-66666666", result.stdout)

    def test_raises_when_no_number_is_free(self):
        self.add_backlog(48213907)
        with mock.patch("chitty.store._random_number", return_value=48213907):
            result = self.run_cli("add", "Idea", "-c", "backlog", "-s", "backlog", exit_code=1)
        self.assertIn("no unused random number in context 'backlog'", result.stderr)

    def test_todo_add_is_backlog_and_edit_cannot_promote_it(self):
        result, _ = self.add_backlog(48213907)
        task_id = result.stdout.split()[1]
        with mock.patch("chitty.store._random_number", return_value=12345678):
            added = self.run_cli("add", "Needs assessment", "-c", "backlog", "-s", "todo")
        self.assertIn("BACKLOG-12345678", added.stdout)
        task = self.json("show", "BACKLOG-12345678")
        self.assertEqual(task["status"], "backlog")
        self.assertEqual(task["description"], "This ticket needs refining.")
        refused = self.run_cli("edit", task_id, "-s", "todo", exit_code=1)
        self.assertIn(f"chitty move {task_id} tasks", refused.stderr)

    def test_move_into_backlog_sets_status(self):
        self.run_cli("add", "Needs assessment", "-d", "Description.")
        with mock.patch("chitty.store._random_number", return_value=12345678):
            self.run_cli("move", "TASK-1", "backlog")
        task = self.json("show", "BACKLOG-12345678")
        self.assertEqual(task["status"], "backlog")
        self.assertIn("→ backlog", task["history"])

    def test_move_to_tasks_promotes_backlog_and_rewrites_references(self):
        git = ["git", "-C", str(self.root)]
        subprocess.run([*git, "init", "--quiet", "-b", "main"], check=True)
        subprocess.run([*git, "config", "user.email", "test@example.com"], check=True)
        subprocess.run([*git, "config", "user.name", "Test"], check=True)
        with mock.patch("chitty.store._random_number", return_value=48213907):
            self.run_cli("add", "Needs assessment", "-c", "backlog", "-s", "todo")
        self.run_cli("add", "Dependent", "-d", "Description.", "--depends-on", "BACKLOG-48213907")
        subprocess.run([*git, "add", "--all"], check=True)
        subprocess.run([*git, "commit", "--quiet", "-m", "tickets"], check=True)

        moved = self.json("move", "BACKLOG-48213907", "tasks")
        self.assertEqual(
            (moved["id"], moved["title"], moved["status"]),
            ("TASK-2", "Needs assessment", "backlog"),
        )
        dependent = self.json("show", "TASK-1")
        self.assertEqual(dependent["depends_on"], ["TASK-2"])


class TestInitAddsBacklogContext(CliTestCase):
    def test_adds_the_table_after_the_last_context(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text() + '\n[agent_commands]\nother = "x {mode} {id}"\n')

        self.run_cli("init")

        text = config.read_text()
        backlog = tomllib.loads(text)["contexts"]["backlog"]
        self.assertEqual(backlog, {"prefix": "BACKLOG", "random_ids": True})
        self.assertIn(
            'review = false\n\n[contexts.backlog]\nprefix = "BACKLOG"\nrandom_ids = true\n'
            "\n[agent_commands]\n",
            text,
        )
        self.assertTrue((self.root / "chitty/backlog").is_dir())
        self.assertEqual(self.run_cli("init").stdout, "already up to date\n")

    def test_adds_the_table_to_pyproject_before_a_later_table(self):
        (self.root / "chitty.toml").unlink()
        pyproject = self.root / "pyproject.toml"
        pyproject.write_text(
            "[tool.chitty]\nformat = 1\ndefault_context = 'tasks'\nautocommit = false\n"
            f"chitty_version = '{CHITTY_VERSION}'\n"
            "\n[tool.chitty.contexts.tasks]\nprefix = 'TASK'\n[tool.other]\nvalue = true\n"
        )

        self.run_cli("init")

        text = pyproject.read_text()
        data = tomllib.loads(text)
        self.assertEqual(
            data["tool"]["chitty"]["contexts"]["backlog"], {"prefix": "BACKLOG", "random_ids": True}
        )
        self.assertEqual(data["tool"]["other"], {"value": True})
        self.assertIn(
            "prefix = 'TASK'\n\n[tool.chitty.contexts.backlog]\n"
            'prefix = "BACKLOG"\nrandom_ids = true\n\n[tool.other]\n',
            text,
        )

    def test_leaves_a_repository_that_already_has_one_alone(self):
        cases = {
            "backlog context": '\n[contexts.backlog]\nprefix = "IDEA"\n',
            "BACKLOG prefix": '\n[contexts.ideas]\nprefix = "BACKLOG"\n',
        }
        config = self.root / "chitty.toml"
        original = config.read_text()
        for name, table in cases.items():
            with self.subTest(name):
                config.write_text(original + table)
                self.run_cli("init")
                self.assertNotIn("random_ids", config.read_text())

    def test_skips_contexts_written_as_dotted_keys(self):
        config = self.root / "chitty.toml"
        text = config.read_text()
        start = text.index("[contexts.tasks]")
        config.write_text(
            text[:start] + 'contexts.tasks.prefix = "TASK"\ncontexts.human.prefix = "HUMAN"\n'
        )
        os.chdir(self.root)

        self.run_cli("init")

        self.assertNotIn("backlog", tomllib.loads(config.read_text())["contexts"])
