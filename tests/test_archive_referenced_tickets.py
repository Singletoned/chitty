import os
import subprocess

from tests.test_cli import CliTestCase


class TestArchiveReferencedTickets(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "initial")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        ).stdout

    def done(self, ticket: str):
        self.run_cli("edit", ticket, "-s", "review")
        self.run_cli(
            "edit",
            ticket,
            "-s",
            "done",
            "--human",
            "--override-review-independence",
            "--note",
            "Reviewed: ok",
        )

    def assert_archived_commit(self):
        self.assertEqual(self.git("status", "--short"), "")
        paths = self.git("ls-files", "chitty/tasks").splitlines()
        self.assertIn("chitty/tasks/archive/TASK-1--one.md", paths)
        self.assertNotIn("chitty/tasks/TASK-1--one.md", paths)
        self.assertTrue(self.git("log", "-1", "--format=%s").startswith("chitty: archive TASK-1"))
        self.assertTrue(self.json("show", "TASK-1")["archived"])

    def test_archive_ticket_named_as_parent(self):
        self.run_cli("add", "One", "-d", "Description.")
        self.run_cli("add", "Two", "-d", "Description.", "--parent", "TASK-1")
        self.done("TASK-1")
        self.run_cli("archive", "TASK-1")
        self.assert_archived_commit()

    def test_archive_ticket_named_in_depends_on(self):
        self.run_cli("add", "One", "-d", "Description.")
        self.run_cli("add", "Two", "-d", "Description.", "--depends-on", "TASK-1")
        self.done("TASK-1")
        self.run_cli("archive", "TASK-1")
        self.assert_archived_commit()

    def test_archive_all_done_when_one_is_a_parent(self):
        self.run_cli("add", "One", "-d", "Description.")
        self.run_cli("add", "Two", "-d", "Description.", "--parent", "TASK-1")
        self.done("TASK-1")
        self.run_cli("archive")
        self.assertEqual(self.git("status", "--short"), "")
        self.assertTrue(self.json("show", "TASK-1")["archived"])
        self.assertFalse(self.json("show", "TASK-2")["archived"])

    def test_older_worktree_sees_ticket_archived_on_main(self):
        self.run_cli("add", "One", "-d", "Description.")
        self.run_cli("add", "Two", "-d", "Description.")
        self.done("TASK-2")
        worktree = self.root / ".worktrees/task-1"
        self.git("worktree", "add", "--quiet", str(worktree), "-b", "task-1")
        self.run_cli("archive", "TASK-2")
        os.chdir(worktree)
        self.addCleanup(os.chdir, self.root)
        self.run_cli("edit", "TASK-1", "--depends-on", "TASK-2")
        self.assertTrue(self.json("show", "TASK-2")["archived"])
