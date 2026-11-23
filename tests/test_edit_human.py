import os
import subprocess
from pathlib import Path

from tests.test_cli import CliTestCase


class TestHumanEdit(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        (self.root / ".gitignore").write_text(".worktrees/\n")
        for number in range(1, 4):
            self.run_cli("add", f"Ticket {number}", "-d", "Description.")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "base")
        self.worktree = self.root / ".worktrees/task-1"
        self.git("worktree", "add", "-q", "-b", "task-1", str(self.worktree))
        previous = os.getcwd()
        os.chdir(self.worktree)
        try:
            self.run_cli("edit", "TASK-1", "-s", "doing")
            self.run_cli("edit", "TASK-1", "-s", "review")
        finally:
            os.chdir(previous)

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or self.root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def ticket_path(self, checkout: Path, task_id: str = "TASK-1") -> Path:
        return next((checkout / "chitty/tasks").glob(f"{task_id}--*.md"))

    def test_error_to_done_matrix(self):
        statuses = ("backlog", "planning", "cold-read", "todo", "doing", "blocked", "error")
        number = 4
        for status in statuses:
            for human in (False, True):
                for note in (None, "reason"):
                    with self.subTest(status=status, human=human, note=note):
                        task = f"TASK-{number}"
                        number += 1
                        self.run_cli("add", f"Ticket {task}", "-d", "Description.")
                        self.run_cli("edit", task, "-s", "todo")
                        args = ["edit", task, "-s", status]
                        if status in ("blocked", "planning"):
                            args += ["--note", "reason"]
                        self.run_cli(*args)
                        args = ["edit", task, "-s", "done"]
                        if human:
                            args.append("--human")
                        if note:
                            args += ["--note", note]
                        success = status == "error" and human and bool(note)
                        result = self.run_cli(*args, exit_code=0 if success else 1)
                        if success:
                            content = self.ticket_path(self.root, task).read_text()
                            self.assertIn("status: done", content)
                            self.assertIn("reason", content)
                            self.assertIn("human error → done", content)
                        elif status == "error" and human:
                            self.assertIn(
                                "moving error → done requires --note with the reason", result.output
                            )
                        else:
                            self.assertIn(
                                "setting status done requires -s review first", result.output
                            )

    def test_error_to_done_rejects_whitespace_note(self):
        self.run_cli("add", "Ticket 4", "-d", "Description.")
        self.run_cli("edit", "TASK-4", "-s", "error")
        result = self.run_cli(
            "edit", "TASK-4", "-s", "done", "--human", "--note", "   ", exit_code=1
        )
        self.assertIn("moving error → done requires --note with the reason", result.output)

    def test_human_edit_writes_in_the_worktree(self):
        main = self.git("rev-parse", "main").strip()
        result = self.run_cli("edit", "TASK-1", "-s", "done", "--note", "Reviewed: ok", "--human")
        self.assertIn(".worktrees/task-1", result.output)
        content = self.git("show", f"task-1:{self.ticket_path(self.root).relative_to(self.root)}")
        self.assertIn("status: done", content)
        self.assertIn("human review → done", content)
        self.assertEqual(self.git("rev-parse", "main").strip(), main)
        self.assertEqual(self.git("status", "--porcelain").strip(), "")
        self.assertEqual(self.git("status", "--porcelain", cwd=self.worktree).strip(), "")
        self.assertEqual(os.environ["CHITTY_ACTOR"], "test-agent")

    def test_edit_without_human_still_refuses(self):
        result = self.run_cli("edit", "TASK-1", "-s", "done", "--note", "Reviewed: ok", exit_code=1)
        self.assertIn("latest committed version is on branch task-1", result.output)

    def test_human_edit_without_a_worktree_keeps_the_refusal(self):
        self.git("switch", "-q", "-c", "task-3")
        self.run_cli("edit", "TASK-3", "--note", "x")
        self.git("switch", "-q", "main")
        before_task = self.git("rev-parse", "task-3").strip()
        before_main = self.git("rev-parse", "main").strip()
        result = self.run_cli("edit", "TASK-3", "--note", "y", "--human", exit_code=1)
        self.assertIn("run `git switch task-3` first", result.output)
        self.assertEqual(self.git("rev-parse", "task-3").strip(), before_task)
        self.assertEqual(self.git("rev-parse", "main").strip(), before_main)
        self.assertEqual(os.environ.get("CHITTY_ACTOR"), "test-agent")
        del os.environ["CHITTY_ACTOR"]
        try:
            self.run_cli("edit", "TASK-3", "--note", "y", "--human", exit_code=1)
            self.assertNotIn("CHITTY_ACTOR", os.environ)
        finally:
            os.environ["CHITTY_ACTOR"] = "test-agent"

    def test_human_edit_of_a_ticket_on_main_uses_main(self):
        result = self.run_cli("edit", "TASK-2", "--note", "x", "--human")
        self.assertNotIn(".worktrees", result.output)
        content = self.ticket_path(self.root, "TASK-2").read_text()
        self.assertIn("human", content)
