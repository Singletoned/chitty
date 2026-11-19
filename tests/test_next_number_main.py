import subprocess
from pathlib import Path

from chitty.errors import ChittyError
from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestNextNumberMain(CliTestCase):
    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", "-C", str(cwd or self.root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def init_git(self):
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

    def write_ticket(self, number: int):
        self.run_cli("add", f"Seed {number}", "-d", "Description.")
        source = next((self.root / "chitty/tasks").glob("TASK-*--seed-*.md"))
        target = source.with_name(f"TASK-{number}--seed-{number}.md")
        source.rename(target)
        return target

    def test_add_ignores_other_local_and_remote_branches(self):
        for number in range(1, 4):
            self.run_cli("add", f"Seed {number}", "-d", "Description.")
        self.init_git()
        source = next((self.root / "chitty/tasks").glob("TASK-1--seed-1.md"))
        feature_file = source.with_name("TASK-50--feature.md")
        self.git("switch", "--quiet", "-c", "feature")
        feature_file.write_text(source.read_text())
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "feature task")
        self.git("switch", "--quiet", "main")
        self.git("switch", "--quiet", "-c", "temporary")
        remote_file = source.with_name("TASK-60--remote.md")
        remote_file.write_text(source.read_text())
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "remote task")
        remote_commit = self.git("rev-parse", "HEAD")
        self.git("switch", "--quiet", "main")
        self.git("branch", "-D", "temporary")
        self.git("update-ref", "refs/remotes/origin/other", remote_commit)
        self.assertEqual(
            self.run_cli("add", "Next", "-d", "Description.").stdout.split()[1], "TASK-4"
        )

    def test_add_counts_uncommitted_and_archived_numbers(self):
        self.run_cli("add", "Seed", "-d", "Description.")
        self.init_git()
        existing = next((self.root / "chitty/tasks").glob("TASK-1--seed.md"))
        for number in (7, 9):
            duplicate = existing.with_name(f"TASK-{number}--seed-{number}.md")
            duplicate.write_text(existing.read_text())
        (self.root / "chitty/tasks/archive").mkdir(parents=True)
        archived = self.root / "chitty/tasks/TASK-9--seed-9.md"
        archived.rename(self.root / "chitty/tasks/archive" / archived.name)
        self.assertEqual(
            self.run_cli("add", "Next", "-d", "Description.").stdout.split()[1], "TASK-10"
        )

    def test_direct_sequential_allocation_refuses_feature_and_detached_head(self):
        self.init_git()
        self.git("switch", "--quiet", "-c", "feature")
        repo = Repo.open(self.root)
        with self.assertRaisesRegex(ChittyError, "only be allocated on main"):
            repo.next_number(repo.context("tasks"))
        self.git("checkout", "--quiet", "--detach")
        repo = Repo.open(self.root)
        with self.assertRaisesRegex(ChittyError, "only be allocated on main"):
            repo.next_number(repo.context("tasks"))

    def test_linked_worktree_refuses_sequential_allocation_but_random_works(self):
        self.init_git()
        worktree = self.tmp / "feature-worktree"
        self.git("worktree", "add", "--quiet", "-b", "feature", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        repo = Repo.open(worktree)
        with self.assertRaisesRegex(ChittyError, "only be allocated on main"):
            repo.next_number(repo.context("tasks"))

        config = worktree / "chitty.toml"
        config.write_text(
            config.read_text() + '\n[contexts.random]\nprefix = "RANDOM"\nrandom_ids = true\n'
        )
        repo = Repo.open(worktree)
        self.assertGreaterEqual(repo.next_number(repo.context("random")), 10_000_000)

    def test_delete_mode_counts_a_number_deleted_on_another_branch(self):
        self.run_cli("add", "Seed", "-d", "Description.")
        self.init_git()
        source = next((self.root / "chitty/tasks").glob("TASK-1--seed.md"))
        self.git("switch", "--quiet", "-c", "other")
        deleted = source.with_name("TASK-9--deleted.md")
        deleted.write_text(source.read_text())
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "add deleted number")
        deleted.unlink()
        self.git("commit", "--quiet", "-am", "delete ticket")
        self.git("switch", "--quiet", "main")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("default_context", 'archive = "delete"\ndefault_context')
        )
        repo = Repo.open(self.root)
        self.assertEqual(repo.next_number(repo.context("tasks")), 10)
