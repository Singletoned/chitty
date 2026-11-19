import subprocess

from chitty.config import CHITTY_VERSION
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestFailedWritesRestore(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=self.root, check=True)
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.assertIn(CHITTY_VERSION, config.read_text())
        self.hook = self.root / ".git" / "hooks" / "pre-commit"

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        )
        return result.stdout

    def fail_commits(self):
        self.hook.write_text("#!/bin/sh\nexit 1\n")
        self.hook.chmod(0o755)

    def snapshot(self):
        files = sorted((self.root / "chitty").rglob("*.md"))
        return (
            self.git("status", "--porcelain"),
            {path: path.read_bytes() for path in files},
        )

    def assert_restored(self, before):
        status, files = before
        self.assertEqual(self.git("status", "--porcelain"), status)
        self.assertEqual(
            {path: path.read_bytes() for path in sorted((self.root / "chitty").rglob("*.md"))},
            files,
        )

    def test_add_restores_files_and_index_after_autocommit_failure(self):
        self.fail_commits()
        before = self.snapshot()

        result = self.run_cli("add", "First", "-d", "description", exit_code=1)

        self.assertIn("autocommit failed", result.output)
        self.assert_restored(before)
        self.hook.unlink()
        self.run_cli("add", "First", "-d", "description")

    def test_edit_restores_files_and_index_after_autocommit_failure(self):
        self.run_cli("add", "First", "-d", "description")
        self.fail_commits()
        before = self.snapshot()

        result = self.run_cli("edit", "1", "--note", "Changed", exit_code=1)

        self.assertIn("autocommit failed", result.output)
        self.assert_restored(before)
        self.hook.unlink()
        self.run_cli("edit", "1", "--note", "Changed")

    def assert_command_restores(self, *args: str):
        self.fail_commits()
        before = self.snapshot()
        result = self.run_cli(*args, exit_code=1)
        self.assertIn("autocommit failed", result.output)
        self.assert_restored(before)
        self.hook.unlink()
        self.run_cli(*args)

    def test_archive_restores_files_and_index_after_autocommit_failure(self):
        self.run_cli("add", "First", "-d", "description")
        self.assert_command_restores("archive", "1")

    def test_archive_done_restores_files_and_index_after_autocommit_failure(self):
        self.run_cli("add", "First", "-d", "description")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
        self.assert_command_restores("archive")

    def test_move_restores_files_and_index_after_autocommit_failure(self):
        self.run_cli("add", "First", "-d", "description")
        self.assert_command_restores("move", "1", "human")

    def test_renumber_restores_files_and_index_after_autocommit_failure(self):
        self.run_cli("add", "First", "-d", "description")
        self.run_cli("add", "Duplicate", "-d", "description")
        original = self.root / "chitty/tasks/TASK-2--duplicate.md"
        duplicate = self.root / "chitty/tasks/TASK-1--duplicate.md"
        self.git("mv", str(original), str(duplicate))
        self.git("commit", "--quiet", "-m", "duplicate task file")
        self.assert_command_restores("renumber", str(duplicate))

    def test_delete_archive_restores_files_and_index_after_autocommit_failure(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('archive = "move"', 'archive = "delete"'))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "enable delete archive")
        self.run_cli("add", "First", "-d", "description")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
        self.assert_command_restores("archive", "1")

    def test_restore_restores_files_and_index_after_autocommit_failure(self):
        self.run_cli("add", "First", "-d", "description")
        self.run_cli("archive", "1")
        self.fail_commits()
        before = self.snapshot()
        repo = Repo.open(self.root)

        with self.assertRaisesRegex(ChittyError, "autocommit failed"):
            repo.restore(TaskId("TASK", 1))

        self.assert_restored(before)
        self.hook.unlink()
        Repo.open(self.root).restore(TaskId("TASK", 1))
