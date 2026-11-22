import subprocess
import tempfile
import unittest
from pathlib import Path

from chitty.errors import ChittyError
from chitty.git import restore_work, save_work


class SavedWorkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        (self.root / "a.txt").write_text("original")
        (self.root / ".gitignore").write_text("ign.log\n")
        self.git("add", "-A")
        self.git("commit", "-m", "initial")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout

    def test_invalid_refs(self):
        (self.root / "a.txt").write_text("edited")
        refs = self.git("for-each-ref")
        stash = self.git("stash", "list")
        for ref in (
            "refs/stash",
            "refs/heads/x",
            "refs/chitty/stash/",
            "refs/chitty/stashX/TASK-1",
        ):
            with self.subTest(ref=ref):
                with self.assertRaisesRegex(
                    ChittyError, "saved work must use a ref under refs/chitty/stash/"
                ):
                    save_work(self.root, ref, "message")
                self.assertEqual(self.git("for-each-ref"), refs)
                self.assertEqual(self.git("stash", "list"), stash)
                self.assertEqual((self.root / "a.txt").read_text(), "edited")

    def test_clean_ignored(self):
        (self.root / "ign.log").write_text("ignored")
        self.assertFalse(save_work(self.root, "refs/chitty/stash/TASK-1", "message"))
        self.assertNotIn("refs/chitty/stash/", self.git("for-each-ref"))

    def test_changes(self):
        for name in ("a.txt", "s.txt", "u.txt", "ign.log"):
            (self.root / name).write_text(name)
        self.git("add", "s.txt")
        stash = self.git("stash", "list")
        self.assertTrue(save_work(self.root, "refs/chitty/stash/TASK-1", "message"))
        self.assertEqual((self.root / "ign.log").read_text(), "ign.log")
        self.assertEqual(self.git("status", "--porcelain"), "")
        for name in ("a.txt", "s.txt", "u.txt"):
            self.assertEqual(self.git("show", f"refs/chitty/stash/TASK-1:{name}"), name)
        self.assertEqual(self.git("stash", "list"), stash)

    def test_hidden_untracked(self):
        self.git("config", "status.showUntrackedFiles", "no")
        (self.root / "n.txt").write_text("new")
        self.assertTrue(save_work(self.root, "refs/chitty/stash/TASK-1", "message"))
        self.assertEqual(self.git("show", "refs/chitty/stash/TASK-1:n.txt"), "new")

    def test_existing_ref(self):
        ref = "refs/chitty/stash/TASK-1"
        self.git("update-ref", ref, "HEAD")
        commit = self.git("rev-parse", ref)
        (self.root / "a.txt").write_text("edited")
        with self.assertRaisesRegex(ChittyError, "already exists; apply it with git stash apply"):
            save_work(self.root, ref, "message")
        self.assertEqual(self.git("rev-parse", ref), commit)
        self.assertEqual((self.root / "a.txt").read_text(), "edited")

    def test_restore_round_trip(self):
        ref = "refs/chitty/stash/TASK-1"
        (self.root / "a.txt").write_bytes(b"edited")
        (self.root / "u.txt").write_bytes(b"new")
        save_work(self.root, ref, "message")
        self.assertTrue(restore_work(self.root, ref))
        self.assertEqual((self.root / "a.txt").read_bytes(), b"edited")
        self.assertEqual((self.root / "u.txt").read_bytes(), b"new")
        self.assertNotIn(ref, self.git("for-each-ref"))

    def test_restore_conflict(self):
        ref = "refs/chitty/stash/TASK-1"
        (self.root / "a.txt").write_text("saved\n")
        save_work(self.root, ref, "message")
        commit = self.git("rev-parse", ref)
        (self.root / "a.txt").write_text("head\n")
        self.git("add", "a.txt")
        self.git("commit", "-m", "head")
        self.assertFalse(restore_work(self.root, ref))
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.git("rev-parse", ref), commit)

    def test_restore_add_collision(self):
        ref = "refs/chitty/stash/TASK-1"
        (self.root / "n.txt").write_text("saved")
        save_work(self.root, ref, "message")
        commit = self.git("rev-parse", ref)
        (self.root / "n.txt").write_text("head")
        self.git("add", "n.txt")
        self.git("commit", "-m", "head")
        self.assertFalse(restore_work(self.root, ref))
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual((self.root / "n.txt").read_text(), "head")
        self.assertEqual(self.git("rev-parse", ref), commit)

    def test_restore_missing(self):
        with self.assertRaisesRegex(ChittyError, "refs/chitty/stash/TASK-1 does not exist"):
            restore_work(self.root, "refs/chitty/stash/TASK-1")

    def test_restore_dirty(self):
        ref = "refs/chitty/stash/TASK-1"
        (self.root / "a.txt").write_text("saved")
        save_work(self.root, ref, "message")
        commit = self.git("rev-parse", ref)
        (self.root / "precious.txt").write_text("precious")
        with self.assertRaisesRegex(
            ChittyError, f"cannot restore {ref}: the worktree has uncommitted changes"
        ):
            restore_work(self.root, ref)
        self.assertEqual((self.root / "precious.txt").read_text(), "precious")
        self.assertEqual(self.git("rev-parse", ref), commit)

    def test_restore_invalid_ref(self):
        with self.assertRaisesRegex(
            ChittyError, "saved work must use a ref under refs/chitty/stash/"
        ):
            restore_work(self.root, "refs/stash")
