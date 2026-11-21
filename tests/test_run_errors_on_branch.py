"""Runner failures are recorded on their ticket branch, not on main."""

import re
import stat
import sys

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
        self.assert_branch_error("setup", "setup exited with status 1")
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
        fake.write_text("#!" + sys.executable + "\nraise SystemExit(7)\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        before = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--ticket", "TASK-1")

        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        self.assert_branch_error("agent", "agent exited with status 7")
        self.assert_main_error_visible()
        self.assertIn("status: doing", self.main_ticket())
        self.assertIn("doing → error", result.stdout)

    def assert_branch_error(self, phase: str, message: str) -> None:
        """The newest commit on `task-1` is the one that records the error."""
        path = "chitty/tasks/TASK-1--claim-me.md"
        tip = self.git("show", f"task-1:{path}")
        self.assertIn("status: error", tip)
        self.assertIn(f"Runner error ({phase})", tip)
        self.assertIn(message, tip)
        parent = self.git("show", f"task-1~1:{path}")
        self.assertNotIn("status: error", parent)
        self.assertNotIn(f"Runner error ({phase})", parent)

    def main_ticket(self) -> str:
        return self.git("show", "main:chitty/tasks/TASK-1--claim-me.md")

    def assert_main_error_visible(self) -> None:
        from chitty.store import Repo, next_action

        self.assertEqual(self.json("show", "TASK-1")["status"], "error")
        self.assertEqual(str(next_action(Repo.open(self.root), modes=("errors",)).id), "TASK-1")
