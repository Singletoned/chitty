import subprocess

from tests.test_cli import CliTestCase


class TestReferenceIsolation(CliTestCase):
    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.run_cli("add", "One", "-d", "Describe.")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "initial")
        self.git("checkout", "-b", "task-1")
        self.run_cli("edit", "TASK-1", "--note", "branch")
        self.git("checkout", "main")
        path = self.root / "chitty/tasks/TASK-1--one.md"
        path.write_text(path.read_text().replace("Describe.", "Main change."))
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "main change")
        self.run_cli("add", "Two", "-d", "Describe.")
        self.run_cli("add", "Three", "-d", "Describe.")
        self.run_cli("add", "Four", "-d", "TASK-1 and TASK-2", "-s", "planning")

    def test_existing_references_do_not_read_conflict(self):
        self.run_cli("show", "TASK-2")
        for command in (("edit", "TASK-2", "--note", "x"), ("note", "TASK-2", "y")):
            before = self.git("rev-parse", "HEAD")
            self.run_cli(*command)
            self.assertNotEqual(before, self.git("rev-parse", "HEAD"))
        path = self.root / "chitty/tasks/TASK-3--three.md"
        path.write_text(
            path.read_text().replace(
                "status: todo\n", "status: todo\ndepends_on:\n  - TASK-1\nparent: TASK-1\n"
            )
        )
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "references")
        before = self.git("rev-parse", "HEAD")
        self.run_cli("edit", "TASK-3", "--note", "x")
        self.assertNotEqual(before, self.git("rev-parse", "HEAD"))

    def test_add_conflicted_dependency(self):
        before = self.git("rev-parse", "HEAD")
        self.run_cli("edit", "TASK-2", "--depends-on", "TASK-1")
        self.assertNotEqual(before, self.git("rev-parse", "HEAD"))

    def test_missing_reference(self):
        result = self.run_cli("edit", "TASK-2", "--depends-on", "TASK-99", exit_code=1)
        self.assertIn("no task TASK-99", result.output)

    def test_unreadable_mention(self):
        result = self.run_cli("edit", "TASK-4", "-s", "todo")
        self.assertIn(
            "TASK-1 unreadable: ticket `TASK-1` changed on both `task-1` and `main`",
            result.stdout,
        )
        self.assertIn("TASK-2 todo Two", result.stdout)
        self.assertIn("status: todo", self.run_cli("show", "TASK-4").stdout)

    def test_unconfigured_context_reference(self):
        directory = self.root / "chitty/other"
        directory.mkdir()
        source = self.root / "chitty/tasks/TASK-2--two.md"
        (directory / "OTHER-1--two.md").write_text(source.read_text())
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "other task")
        self.run_cli("edit", "TASK-2", "--depends-on", "OTHER-1")
