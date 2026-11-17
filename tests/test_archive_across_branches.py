import subprocess

from tests.test_cli import CliTestCase


class TestArchiveAcrossBranches(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", "autocommit = true")
            .replace(
                '[contexts.tasks]\nprefix = "TASK"',
                '[contexts.tasks]\nprefix = "TASK"\nreview = false',
            )
        )
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "initial config")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def test_older_worktree_can_reference_archived_ticket(self):
        self.run_cli("add", "One", "-d", "Describe.")
        self.run_cli("add", "Two", "-d", "Describe.")
        self.git("worktree", "add", "-b", "older", str(self.root.parent / "older"))
        self.run_cli("edit", "2", "-s", "done")
        self.run_cli("archive", "2")
        older = self.root.parent / "older"
        result = subprocess.run(
            ["uv", "run", "chitty", "edit", "1", "--depends-on", "2"],
            cwd=older,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        shown = subprocess.run(
            ["uv", "run", "chitty", "show", "2", "--json"],
            cwd=older,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue(__import__("json").loads(shown.stdout)["archived"])

    def test_archive_referenced_ticket_succeeds_and_commits(self):
        self.run_cli("add", "One", "-d", "Describe.")
        self.run_cli("add", "Two", "-d", "Describe.", "--parent", "1")
        self.run_cli("edit", "1", "-s", "done")
        self.run_cli("archive", "1")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertIn("TASK-1", self.run_cli("show", "2").stdout)
