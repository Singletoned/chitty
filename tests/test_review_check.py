import re
import sys

from chitty.ids import TaskId
from chitty.store import Edit, Repo
from tests.test_review_merge import ReviewMergeTestCase


class TestReviewCheck(ReviewMergeTestCase):
    def prepare(self, command):
        config = self.root / "chitty.toml"
        config.write_text(
            re.sub(r"^check = .*$", f'check = "{command}"', config.read_text(), flags=re.MULTILINE)
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure check")
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", "doing")

    def script(self, body):
        script = self.tmp / "check.py"
        script.write_text(body)
        return f"{sys.executable} {script}"

    def assert_doing(self):
        self.assertIn(
            "status: doing", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )

    def test_failure(self):
        self.prepare(self.script("print('boom')\nraise SystemExit(3)\n"))
        before = self.git("rev-parse", "HEAD")
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("check failed with status 3", result.output)
        self.assertIn("boom", (self.root / ".chitty/check.log").read_text())
        self.assert_doing()
        self.assertEqual(before, self.git("rev-parse", "HEAD"))

    def test_missing(self):
        self.prepare("nonexistent-chitty-check-command")
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("check command not found", result.output)
        self.assert_doing()

    def test_dirty(self):
        self.prepare(self.script("from pathlib import Path\nPath('made.txt').write_text('x')\n"))
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("the worktree has uncommitted changes: `made.txt`", result.output)
        self.assert_doing()

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
