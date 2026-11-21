"""Runner failures are recorded on their ticket branch, not on main."""

import re
import stat

from tests.test_run_claims_on_branch import TestRunClaimsOnBranch


class TestRunErrorsOnBranch(TestRunClaimsOnBranch):
    def make_doing_branch(self) -> None:
        self.run_cli("edit", "TASK-1", "-s", "doing")
        self.git("branch", "task-1", "main")

    def set_setup_failure_on_main(self) -> str:
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('setup = "true"', 'setup = "false"'))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "fail setup")
        return self.git("rev-parse", "main").strip()

    def test_work_setup_failure_is_only_recorded_on_branch(self):
        self.make_doing_branch()
        before = self.set_setup_failure_on_main()

        self.run_cli("run", "--ticket", "TASK-1")

        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        tip = self.assert_branch_error("setup", "setup exited with status 1")
        self.assertEqual(tip.count("setup exited with status 1"), 1)
        self.assertNotIn("Error output:", tip)
        self.assert_main_error_visible()
        self.assertIn("status: doing", self.main_ticket())

    def test_missing_setup_command_is_recorded_on_branch(self):
        self.make_doing_branch()
        config = self.root / "chitty.toml"
        config.write_text(
            re.sub(
                r"^setup = .*$",
                'setup = "no-such-chitty-setup-command"',
                config.read_text(),
                flags=re.MULTILINE,
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure missing setup")

        self.run_cli("run", "--ticket", "TASK-1")

        self.assert_branch_error("setup", "setup command not found: no-such-chitty-setup-command")

    def test_agent_failure_keeps_error_and_message_on_branch(self):
        self.make_doing_branch()
        fake = self.root / "bin" / "fake"
        fake.write_text(
            "#!/bin/sh\necho AGENT_LINE_1\necho AGENT_LINE_2\n"
            "echo work > work.txt\ngit add work.txt\ngit commit --quiet -m work\nexit 7\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        before = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--ticket", "TASK-1")

        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        tip = self.assert_branch_error("agent", "agent exited with status 7")
        for text in (
            "Runner error (agent): agent exited with status 7:",
            "AGENT_LINE_1",
            "AGENT_LINE_2",
        ):
            with self.subTest(text=text):
                self.assertEqual(tip.count(text), 1)
        self.assertLess(tip.index("Error output:"), tip.index("AGENT_LINE_1"))
        self.assert_main_error_visible()
        self.assertIn("status: doing", self.main_ticket())
        self.assertIn("doing → error", result.stdout)

    def failing_fake(self):
        fake = self.root / "bin" / "fake"
        fake.write_text(
            "#!/bin/sh\necho scratch > scratch.txt\necho 'Error: Model \"x\" not found'\nexit 7\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

    def test_agent_start_failure_on_todo_stops_and_leaves_todo(self):
        before = self.git("rev-parse", "main").strip()
        self.failing_fake()
        result = self.run_cli("run", "--ticket", "TASK-1", exit_code=1)
        self.assertIn(
            "agent failed before committing anything; TASK-1 left at todo: "
            "agent exited with status 7:",
            result.stderr,
        )
        self.assertIn('Error: Model "x" not found', result.stderr)
        tip = self.git("show", "task-1:chitty/tasks/TASK-1--claim-me.md")
        self.assertIn("status: todo", tip)
        self.assertNotIn("Runner error", tip)
        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        self.assertEqual(self.json("show", "TASK-1")["status"], "todo")
        self.assertTrue((self.root / ".worktrees/task-1/scratch.txt").exists())
        self.assertEqual(self.git("rev-list", "--count", "main..task-1").strip(), "2")

    def test_agent_start_failure_on_doing_leaves_doing(self):
        self.make_doing_branch()
        before = self.git("rev-parse", "task-1").strip()
        self.failing_fake()
        self.run_cli("run", "--ticket", "TASK-1", exit_code=1)
        self.assertEqual(self.git("rev-parse", "task-1").strip(), before)
        tip = self.git("show", "task-1:chitty/tasks/TASK-1--claim-me.md")
        self.assertIn("status: doing", tip)
        self.assertNotIn("Runner error", tip)

    def test_repair_start_failure_stops_and_leaves_error(self):
        self.test_agent_failure_keeps_error_and_message_on_branch()
        self.failing_fake()
        before = self.git("rev-parse", "task-1").strip()
        result = self.run_cli("run", "--errors", exit_code=1)
        self.assertIn(
            "agent failed before committing anything; TASK-1 left at error:", result.stderr
        )
        self.assertEqual(self.git("rev-parse", "task-1").strip(), before)

    def assert_branch_error(self, phase: str, message: str) -> str:
        """The newest commit on `task-1` is the one that records the error."""
        path = "chitty/tasks/TASK-1--claim-me.md"
        tip = self.git("show", f"task-1:{path}")
        self.assertIn("status: error", tip)
        self.assertIn(f"Runner error ({phase})", tip)
        self.assertIn(message, tip)
        parent = self.git("show", f"task-1~1:{path}")
        self.assertNotIn("status: error", parent)
        self.assertNotIn(f"Runner error ({phase})", parent)
        return tip

    def main_ticket(self) -> str:
        return self.git("show", "main:chitty/tasks/TASK-1--claim-me.md")

    def assert_main_error_visible(self) -> None:
        from chitty.store import Repo, next_action

        self.assertEqual(self.json("show", "TASK-1")["status"], "error")
        self.assertEqual(str(next_action(Repo.open(self.root), modes=("errors",)).id), "TASK-1")
