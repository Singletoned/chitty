import os
import subprocess

from tests.test_cli import CliTestCase


class TestFixSources(CliTestCase):
    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, text=True, capture_output=True
        ).stdout.strip()

    def setUp(self):
        super().setUp()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.ticket("3", "dependency", False)

    def ticket(self, number, title, defect=True):
        path = self.root / "chitty" / "tasks" / f"TASK-{number}--{title}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        dep = "depends_on: [task-3]\n" if defect else ""
        path.write_text(
            f"---\ntitle: {title}\nstatus: backlog\n{dep}created: 2026-01-01\n---\n"
            "\n## Description\n\nFixture.\n"
        )
        return path

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "fixture")

    def test_main_copy_with_branch_ahead_on_other_file(self):
        task = self.ticket("5", "own")
        other = self.ticket("6", "other")
        self.commit()
        self.git("checkout", "-b", "task-5")
        (self.root / "unrelated").write_text("changed\n")
        self.commit()
        self.git("checkout", "main")
        before = task.read_bytes()
        head = self.git("rev-parse", "HEAD")
        result = self.run_cli("fix", exit_code=1)
        self.assertIn("skipped: read from task-5", result.output)
        self.assertEqual(task.read_bytes(), before)
        self.assertIn("TASK-3", other.read_text())
        self.assertEqual(self.git("rev-parse", "HEAD"), head)

    def test_main_branch_and_renamed_file(self):
        old = self.ticket("5", "old")
        other = self.ticket("6", "other")
        self.commit()
        self.git("checkout", "-b", "task-5")
        self.git("mv", str(old), str(old.with_name("TASK-5--new.md")))
        self.commit()
        self.git("checkout", "main")
        before = old.read_bytes()
        head = self.git("rev-parse", "HEAD")
        filtered = self.run_cli("fix", str(other))
        self.assertNotIn("TASK-5", filtered.output)
        result = self.run_cli("fix", exit_code=1)
        self.assertIn("skipped: read from task-5", result.output)
        self.assertEqual(old.read_bytes(), before)
        self.assertIn("TASK-3", other.read_text())
        self.assertEqual(self.git("rev-parse", "HEAD"), head)

    def test_duplicate_files_and_filter(self):
        a = self.ticket("6", "a")
        b = self.ticket("6", "b")
        self.commit()
        before = (a.read_bytes(), b.read_bytes())
        result = self.run_cli("fix", exit_code=1)
        for path in (a, b):
            self.assertIn(
                f"{path}: warning: skipped: TASK-6 is used by more than one file", result.output
            )
        self.assertEqual((a.read_bytes(), b.read_bytes()), before)
        result = self.run_cli("fix", str(a), exit_code=1)
        self.assertIn("skipped: TASK-6 is used by more than one file", result.output)
        self.assertNotIn(f"{b}: warning: skipped", result.output)
        self.assertEqual((a.read_bytes(), b.read_bytes()), before)
        self.assertIn("used by more than one file", self.run_cli("check", exit_code=1).output)

    def test_worktree_sources_and_malformed(self):
        own = self.ticket("5", "own", False)
        self.ticket("6", "other", False)
        self.commit()
        self.git("branch", "task-5")
        worktree = self.tmp / "task-5"
        self.git("worktree", "add", str(worktree), "task-5")
        self.root = worktree
        own = worktree / own.relative_to(self.tmp / "repo")
        own.write_text(own.read_text().replace("title: own", "title: Own"))
        self.commit()
        own.write_text(own.read_text().replace("created:", "depends_on: [task-3]\ncreated:"))
        bad = self.ticket("9", "bad", False)
        bad.write_text("not frontmatter")
        provisional = self.ticket("K7Q2MX", "new")
        numbered = self.ticket("10", "numbered")
        numbered_before = numbered.read_bytes()
        os.chdir(worktree)
        result = self.run_cli("fix", exit_code=1)
        self.assertIn("skipped: read from main", result.output)
        self.assertIn("TASK-9--bad.md: file must end with a newline", result.output)
        self.assertIn(f"{numbered}: warning: skipped: read from main", result.output)
        self.assertEqual(numbered.read_bytes(), numbered_before)
        self.assertEqual(bad.read_text(), "not frontmatter")
        self.assertIn("TASK-3", own.read_text())
        self.assertIn("TASK-3", provisional.read_text())

    def test_diverged_refs_fail(self):
        task = self.ticket("7", "seven", False)
        self.commit()
        self.git("checkout", "-b", "task-7")
        task.write_text(task.read_text() + "\nlocal\n")
        self.commit()
        self.git("checkout", "main")
        self.git("checkout", "-b", "remote-fixture")
        task.write_text(task.read_text() + "\nremote\n")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/task-7", "HEAD")
        self.git("checkout", "main")
        result = self.run_cli("fix", exit_code=1)
        self.assertIn("task-7", result.output)
        self.assertIn("origin/task-7", result.output)
