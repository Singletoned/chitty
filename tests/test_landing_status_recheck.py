import contextlib
import io
import re

from chitty.model import STATUSES
from tests.test_landing import LandingTestCase


class TestLandingStatusRecheck(LandingTestCase):
    def test_non_done_statuses_are_not_landed(self):
        task = next((self.worktree / "chitty/tasks").glob("TASK-1--*.md"))
        for status in STATUSES:
            if status == "done":
                continue
            with self.subTest(status=status):
                task.write_text(
                    re.sub(
                        r"^status: .*$", f"status: {status}", task.read_text(), flags=re.MULTILINE
                    )
                )
                self.git("add", str(task), cwd=self.worktree)
                self.git("commit", "--allow-empty", "--quiet", "-m", str(status), cwd=self.worktree)
                main = self.git("rev-parse", "main")
                branch = self.git("rev-parse", self.branch)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = self.land()
                self.assertFalse(result)
                self.assertEqual(self.git("rev-parse", "main"), main)
                self.assertEqual(self.git("rev-parse", self.branch), branch)
                self.assertTrue(self.worktree.is_dir())
                self.assertIn(f"not landing TASK-1: it is {status}", stderr.getvalue())

    def test_done_lands(self):
        self.finish_ticket()
        self.assertTrue(self.land())
        self.assertFalse(self.worktree.exists())
