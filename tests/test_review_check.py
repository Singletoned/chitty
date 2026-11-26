import re
import sys
import tomllib

from chitty.ids import TaskId
from chitty.store import Edit, Repo
from tests.test_review_merge import ReviewMergeTestCase


class TestReviewCheck(ReviewMergeTestCase):
    def configure_check(self, command):
        config = self.root / "chitty.toml"
        config.write_text(
            re.sub(r"^check = .*$", f'check = "{command}"', config.read_text(), flags=re.MULTILINE)
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure check")

    def prepare(self, command):
        self.configure_check(command)
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", "doing")
        self.git("commit", "--allow-empty", "--quiet", "-m", "work")

    def test_runner_main_skips_check(self):
        marker = self.tmp / "marker"
        self.configure_check(
            self.script(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('x')\n"
                "raise SystemExit(3)\n"
            )
        )
        self.run_cli("edit", "1", "-s", "doing")
        result = self.run_cli("edit", "1", "-s", "review")
        self.assertIn(
            "status: review", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )
        self.assertFalse(marker.exists())
        self.assertIn("skipped check: HEAD is already on main", result.stderr)
        self.assertNotIn("running check", result.stderr)
        self.assertNotIn("check finished in", result.stderr)

    def test_merge_only_runs_check(self):
        self.configure_check(self.script("raise SystemExit(3)\n"))
        self.git("switch", "--quiet", "-c", "side")
        (self.root / "side.txt").write_text("side")
        self.git("add", "side.txt")
        self.git("commit", "--quiet", "-m", "side")
        self.git("switch", "--quiet", "main")
        self.run_cli("edit", "1", "-s", "doing")
        self.git("branch", "task-1")
        self.git("switch", "--quiet", "task-1")
        self.git("merge", "--quiet", "--no-ff", "side", "-m", "merge side")
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("check failed with status 3", result.output)

    def test_tickets_workflow_runs_check(self):
        config = self.root / "chitty.toml"
        text = config.read_text().replace('workflow = "runner"', 'workflow = "tickets"')
        config.write_text(text.replace('prefix = "TASK"', 'prefix = "TASK"\nreview = true'))
        self.configure_check(self.script("raise SystemExit(3)\n"))
        self.run_cli("edit", "1", "-s", "doing")
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("check failed with status 3", result.output)

    def script(self, body):
        script = self.tmp / "check.py"
        script.write_text(body)
        return f"{sys.executable} {script}"

    def assert_doing(self):
        self.assertIn(
            "status: doing", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )

    def test_check_progress_passes(self):
        command = self.script("")
        self.prepare(command)
        result = self.run_cli("edit", "1", "-s", "review")
        start = result.stderr.index("running check")
        command_pos = result.stderr.index(command, start)
        self.assertGreater(result.stderr.index("check finished in", command_pos), command_pos)
        self.assertIn(
            f"running check {command} before review (output in .chitty/check.log)", result.stderr
        )
        self.assertRegex(result.stderr, r"check finished in \d+s\n")

    def test_check_progress_fails(self):
        self.prepare(self.script("raise SystemExit(3)\n"))
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertRegex(result.stderr, r"check finished in \d+s\n")

    def assert_refused_review(self, result):
        self.assertIn("Nothing from this edit was saved.", result.output)
        text = next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        self.assertIn("status: doing", text)
        self.assertNotIn("## Summary", text)

    def test_already_dirty(self):
        self.prepare(self.script(""))
        (self.root / "untracked").write_text("dirty")
        result = self.run_cli("edit", "1", "-s", "review", "--summary", "Done.", exit_code=1)
        self.assert_refused_review(result)
        self.assertNotIn("never set up", result.output)

    def test_passing_review_dirty(self):
        self.prepare(self.script(""))
        self.run_cli("edit", "1", "-s", "review")
        (self.root / "untracked").write_text("dirty")
        result = self.run_cli("edit", "1", "-s", "done", "--note", "Reviewed.", exit_code=1)
        self.assertIn("Nothing from this edit was saved.", result.output)
        self.assertIn(
            "status: review", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )

    def test_timeout(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                "autocommit = true", "autocommit = true\ncommand_timeout = 1"
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure timeout")
        self.prepare(self.script("import time\ntime.sleep(5)\n"))
        result = self.run_cli("edit", "1", "-s", "review", "--summary", "Done.", exit_code=1)
        self.assert_refused_review(result)
        self.assertNotIn("never set up", result.output)

    def test_failure_without_setup(self):
        config = self.root / "chitty.toml"
        config.write_text(re.sub(r"^setup = .*\n", "", config.read_text(), flags=re.MULTILINE))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "remove setup")
        self.prepare(self.script("raise SystemExit(3)\n"))
        result = self.run_cli("edit", "1", "-s", "review", "--summary", "Done.", exit_code=1)
        self.assert_refused_review(result)
        self.assertNotIn("never set up", result.output)

    def test_failure(self):
        self.prepare(self.script("print('boom')\nraise SystemExit(3)\n"))
        before = self.git("rev-parse", "HEAD")
        setup = tomllib.loads((self.root / "chitty.toml").read_text())["setup"]
        result = self.run_cli("edit", "1", "-s", "review", "--summary", "Done.", exit_code=1)
        self.assert_refused_review(result)
        self.assertIn(f"If this worktree was never set up, run `{setup}` first.", result.output)
        self.assertIn("check failed with status 3", result.output)
        self.assertIn("boom", (self.root / ".chitty/check.log").read_text())
        self.assert_doing()
        self.assertEqual(before, self.git("rev-parse", "HEAD"))

    def test_missing(self):
        self.prepare("nonexistent-chitty-check-command")
        result = self.run_cli("edit", "1", "-s", "review", "--summary", "Done.", exit_code=1)
        self.assertIn("check command not found", result.output)
        self.assert_refused_review(result)
        self.assertNotIn("never set up", result.output)

    def test_dirty(self):
        self.prepare(self.script("from pathlib import Path\nPath('made.txt').write_text('x')\n"))
        result = self.run_cli("edit", "1", "-s", "review", "--summary", "Done.", exit_code=1)
        self.assertIn("the worktree has uncommitted changes: `made.txt`", result.output)
        self.assert_refused_review(result)
        self.assertNotIn("never set up", result.output)

    def test_skip(self):
        marker = self.tmp / "marker"
        self.prepare(
            self.script(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('x')\n"
                "raise SystemExit(3)\n"
            )
        )
        Repo.open(self.root).edit(
            TaskId.parse("TASK-1"), Edit(status="review", skip_current_version=True)
        )
        self.assertFalse(marker.exists())
        self.assertIn(
            "status: review", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )
