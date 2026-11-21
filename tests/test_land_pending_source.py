import contextlib
import io

from chitty.run import _land_pending
from chitty.store import Repo
from tests.test_landing import LandingTestCase


class TestLandPendingSource(LandingTestCase):
    def setUp(self):
        super().setUp()
        for number in range(2, 6):
            self.run_cli("add", f"Ticket {number}", "-d", "Description.")
        self.fifth = self.root / ".worktrees" / "task-5"
        self.git("worktree", "add", "--quiet", "-b", "task-5", str(self.fifth))
        self.task = next((self.fifth / "chitty/tasks").glob("TASK-5--*.md"))
        self.set_status("doing")

    def set_status(self, status):
        text = self.task.read_text()
        for previous in ("todo", "doing", "done"):
            text = text.replace(f"status: {previous}", f"status: {status}")
        self.task.write_text(text)
        self.git("add", str(self.task), cwd=self.fifth)
        self.git("commit", "--quiet", "-m", f"{status}\n\nTask: TASK-5", cwd=self.fifth)

    def remote_at(self, tip):
        self.git("update-ref", "refs/remotes/origin/task-5", tip)

    def remote_done_ahead(self):
        original = self.task.read_text()
        self.task.write_text(original.replace("status: doing", "status: done"))
        self.git("add", str(self.task), cwd=self.fifth)
        tree = self.git("write-tree", cwd=self.fifth).strip()
        tip = self.git("rev-parse", "HEAD", cwd=self.fifth).strip()
        remote = self.git("commit-tree", tree, "-p", tip, "-m", "remote done").strip()
        self.git("reset", "--quiet", "HEAD", "--", str(self.task), cwd=self.fifth)
        self.task.write_text(original)
        self.remote_at(remote)

    def land_pending(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = _land_pending(Repo.open(self.root))
        return result, stderr.getvalue()

    def test_remote_done_ahead_is_not_landed(self):
        self.remote_done_ahead()
        before = self.git("rev-parse", "main")
        result, stderr = self.land_pending()
        self.assertIsNone(result)
        self.assertIn("not landing task-5: TASK-5 is read from origin/task-5", stderr)
        self.assertEqual(self.git("rev-parse", "main"), before)

    def test_local_done_ahead_lands(self):
        self.remote_at(self.git("rev-parse", "task-5").strip())
        self.set_status("done")
        tip = self.git("rev-parse", "task-5")
        result, _ = self.land_pending()
        self.assertIsNotNone(result)
        self.assertEqual(self.git("rev-parse", "main"), tip)

    def test_equal_tips_land(self):
        self.set_status("done")
        self.remote_at(self.git("rev-parse", "task-5").strip())
        tip = self.git("rev-parse", "task-5")
        result, _ = self.land_pending()
        self.assertIsNotNone(result)
        self.assertEqual(self.git("rev-parse", "main"), tip)

    def test_no_remote_lands(self):
        self.set_status("done")
        tip = self.git("rev-parse", "task-5")
        result, _ = self.land_pending()
        self.assertIsNotNone(result)
        self.assertEqual(self.git("rev-parse", "main"), tip)

    def test_skipped_branch_does_not_stop_next(self):
        self.remote_done_ahead()
        self.run_cli("add", "Sixth", "-d", "Description.")
        sixth = self.root / ".worktrees" / "task-6"
        self.git("worktree", "add", "--quiet", "-b", "task-6", str(sixth))
        task = next((sixth / "chitty/tasks").glob("TASK-6--*.md"))
        task.write_text(task.read_text().replace("status: todo", "status: done"))
        self.git("add", str(task), cwd=sixth)
        self.git("commit", "--quiet", "-m", "done\n\nTask: TASK-6", cwd=sixth)
        result, stderr = self.land_pending()
        assert result is not None
        self.assertEqual(str(result.action.id), "TASK-6")
        self.assertIn("not landing task-5:", stderr)
