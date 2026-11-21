import os
import subprocess
from pathlib import Path

from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestTicketReads(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.file("1", "main")
        self.file("2", "second")
        self.commit("2030-01-01T00:00:00Z")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def commit(self, date="2026-01-01T00:00:00Z"):
        self.git("add", "--all")
        subprocess.run(
            ["git", "commit", "--quiet", "--allow-empty", "-m", "fixture"],
            cwd=self.root,
            env={**os.environ, "GIT_COMMITTER_DATE": date},
            check=True,
            capture_output=True,
        )

    def file(self, number, title, name="example"):
        path = self.root / f"chitty/tasks/TASK-{number}--{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\ntitle: {title}\nstatus: todo\ncreated: 2026-01-01\n---\n"
            "\n## Description\n\nFixture.\n"
        )
        return path

    def branch(self, name="task-1"):
        self.git("checkout", "-b", name)

    def main(self):
        self.git("checkout", "main")

    def test_branch_edit(self):
        self.branch()
        self.file("1", "branch")
        self.commit()
        self.main()
        result = self.run_cli("show", "TASK-1")
        self.assertIn("title: branch", result.stdout)
        self.assertIn("branch: task-1", result.stdout)

    def test_branch_retitle(self):
        self.branch()
        self.file("1", "branch").rename(self.root / "chitty/tasks/TASK-1--branch.md")
        self.commit()
        self.main()
        self.assertIn(
            "TASK-1--branch.md",
            self.run_cli("show", "TASK-1").stdout.split("path: ")[1].splitlines()[0],
        )

    def test_branch_archive(self):
        self.branch()
        path = self.root / "chitty/tasks/TASK-1--example.md"
        archive = path.parent / "archive"
        archive.mkdir(exist_ok=True)
        path.rename(archive / path.name)
        self.commit()
        self.main()
        self.assertTrue(
            self.run_cli("show", "TASK-1")
            .stdout.split("path: ")[1]
            .splitlines()[0]
            .endswith("chitty/tasks/archive/TASK-1--example.md")
        )

    def test_unrelated_branch_only(self):
        self.branch("feature")
        self.file("3", "feature")
        self.commit()
        self.main()
        result = self.run_cli("show", "TASK-3", exit_code=1)
        self.assertTrue(result.stderr.startswith("Error: no task TASK-3"), result.stderr)

    def test_provisional_branch_only(self):
        self.branch("task-k7q2mx")
        path = self.file("K7Q2MX", "provisional")
        path.write_text(path.read_text().replace("status: todo", "provisional: true\nstatus: todo"))
        self.commit()
        self.main()
        result = self.run_cli("show", "TASK-K7Q2MX")
        self.assertIn("title: provisional", result.stdout)
        self.assertIn("branch: task-k7q2mx", result.stdout)

    def test_conflict_does_not_prevent_other_reads_or_edit(self):
        self.branch()
        self.file("1", "branch")
        self.commit()
        self.main()
        self.file("1", "changed main")
        self.commit()
        self.run_cli("show", "TASK-2")
        self.run_cli("edit", "TASK-2", "--note", "x")

    def test_conflicted_ticket_fails(self):
        self.branch()
        self.file("1", "branch")
        self.commit()
        self.main()
        self.file("1", "changed main")
        self.commit()
        result = self.run_cli("show", "TASK-1", exit_code=1)
        for text in ("changed on both", "task-1", "main"):
            self.assertIn(text, result.stderr)

    def test_malformed_branch_copy(self):
        self.branch()
        path = self.root / "chitty/tasks/TASK-1--example.md"
        path.write_text("not frontmatter\n")
        self.commit()
        self.main()
        result = self.run_cli("show", "TASK-1", exit_code=1)
        self.assertIn(
            "task-1:chitty/tasks/TASK-1--example.md: file must start with '---' frontmatter",
            result.stderr,
        )

    def test_malformed_branch_context(self):
        self.branch()
        path = self.root / "chitty/tasks/TASK-1--example.md"
        path.write_text("not frontmatter\n")
        self.commit()
        self.main()
        self.assertEqual(Repo.open(self.root).context_of(TaskId.parse("TASK-1")).name, "tasks")

    def test_malformed_main_working_tree_context(self):
        self.branch()
        self.file("1", "branch")
        self.commit()
        self.main()
        (self.root / "chitty/tasks/TASK-1--example.md").write_text("not frontmatter\n")
        self.assertEqual(Repo.open(self.root).context_of(TaskId.parse("TASK-1")).name, "tasks")

    def test_malformed_main_working_tree_find(self):
        self.branch()
        self.file("1", "branch")
        self.commit()
        self.main()
        (self.root / "chitty/tasks/TASK-1--example.md").write_text("not frontmatter\n")
        task = Repo.open(self.root).find(TaskId.parse("TASK-1")).task
        self.assertEqual(task.frontmatter.title, "branch")

    def test_unrelated_linked_worktree_ignores_uncommitted_title(self):
        linked = self.root / "linked"
        self.git("worktree", "add", "-b", "feature", str(linked))
        path = linked / "chitty/tasks/TASK-2--example.md"
        path.write_text(path.read_text().replace("title: second", "title: uncommitted"))
        previous = Path.cwd()
        try:
            os.chdir(linked)
            result = self.run_cli("show", "TASK-2")
        finally:
            os.chdir(previous)
        self.assertIn("title: second", result.stdout)
        self.assertNotIn("title: uncommitted", result.stdout)
