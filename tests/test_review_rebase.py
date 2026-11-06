import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest import mock

from chitty.run import _changed_agents_block
from chitty.store import Repo
from tests.test_cli import CliTestCase

# Records, from the worktree it runs in, whether the branch already contains `main`.
REPORT = (
    "import subprocess, sys\n"
    "from pathlib import Path\n"
    "rebased = subprocess.run(['git', 'merge-base', '--is-ancestor', 'main', 'HEAD']).returncode\n"
    "Path(sys.argv[1]).write_text('rebased' if rebased == 0 else 'not rebased')\n"
)


class ReviewRebaseTestCase(CliTestCase):
    def setUp(self):
        super().setUp()
        self.logs = self.tmp / "logs"
        self.logs.mkdir()
        setup = self.tmp / "setup.py"
        setup.write_text(REPORT)
        agent = self.tmp / "bin" / "fake"
        agent.parent.mkdir()
        agent.write_text(
            "#!"
            + sys.executable
            + "\n"
            + REPORT.replace("sys.argv[1]", "sys.argv[3]")
            + "Path(sys.argv[4]).write_text(Path('main.txt').read_text())\n"
            "path = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "path.write_text(path.read_text().replace('status: review', 'status: done'))\n"
            "subprocess.run(['git', 'commit', '--quiet', '-am', 'reviewed'], check=True)\n"
        )
        agent.chmod(agent.stat().st_mode | stat.S_IXUSR)
        previous_path = os.environ["PATH"]
        os.environ["PATH"] = f"{agent.parent}:{previous_path}"
        self.addCleanup(os.environ.__setitem__, "PATH", previous_path)
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                "autocommit = false",
                f'autocommit = true\nsetup = "{sys.executable} {setup} {self.logs / "setup"}"',
            )
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                f'agent_command = "fake {{mode}} {{id}} {self.logs / "agent"} '
                f'{self.logs / "main.txt"}"',
            )
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        (self.root / "shared.txt").write_text("original\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        self.run_cli("add", "Review me", "-d", "Description.")
        self.worktree = self.root / ".worktrees" / "task-1"

    def git(self, *args: str, cwd: Path | None = None) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, capture_output=True, check=True, text=True
        ).stdout

    def branch_for_review(self, shared: str | None = None, failures: int = 0) -> None:
        """Commit work on `task-1` and put the ticket in review there."""
        self.git("switch", "--quiet", "-c", "task-1")
        (self.root / "work.txt").write_text("work\n")
        if shared is not None:
            (self.root / "shared.txt").write_text(shared)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "work")
        self.run_cli("edit", "1", "-s", "doing")
        self.run_cli("edit", "1", "-s", "review")
        for number in range(failures):
            self.run_cli(
                "edit",
                "1",
                "-s",
                "doing",
                "--note",
                f"Review failed (work): {number}.",
                "--override-review-independence",
            )
            self.run_cli("edit", "1", "-s", "review")
        self.git("switch", "--quiet", "main")

    def move_main(self, shared: str | None = None) -> None:
        (self.root / "main.txt").write_text("from main\n")
        if shared is not None:
            (self.root / "shared.txt").write_text(shared)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "main moved")

    def ticket(self):
        repo = Repo.open(self.worktree)
        return repo.find(repo.resolve("1")).task

    def assert_no_rebase_in_progress(self) -> None:
        for name in ("rebase-merge", "rebase-apply"):
            path = self.git("rev-parse", "--git-path", name, cwd=self.worktree).strip()
            self.assertFalse((self.worktree / path).exists(), name)


class TestReviewRebase(ReviewRebaseTestCase):
    def test_agents_file_present_only_on_branch_is_detected(self):
        self.branch_for_review()
        self.git("switch", "--quiet", "main")
        (self.root / "AGENTS.md").unlink()
        self.git("add", "-u", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "remove agents guide")
        self.git("switch", "--quiet", "task-1")
        (self.root / "AGENTS.md").write_text("branch-only instructions\n")

        self.assertTrue(_changed_agents_block(self.root))

    def test_managed_block_change_fails_without_starting_review(self):
        self.branch_for_review()
        self.git("switch", "--quiet", "task-1")
        agents = self.root / "AGENTS.md"
        agents.write_text(
            agents.read_text().replace(
                "Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit",
                "Tasks live elsewhere; use the `chitty` CLI or MCP, and do not hand-edit",
            )
        )
        self.git("add", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "change managed guide")
        self.git("switch", "--quiet", "main")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout, "TASK-1: review → doing\n")
        self.assertFalse((self.logs / "agent").exists())
        self.assertFalse((self.logs / "setup").exists())
        self.assertIn(
            "Review failed (work): the branch changes Chitty's managed block in AGENTS.md; "
            "only chitty init on the main checkout may change it. Restore that block from main.",
            self.ticket().section("Notes") or "",
        )

    def test_change_outside_managed_block_passes_review(self):
        self.branch_for_review()
        self.git("switch", "--quiet", "task-1")
        agents = self.root / "AGENTS.md"
        agents.write_text("Heading outside the guide.\n\n" + agents.read_text())
        self.git("add", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "change outside managed guide")
        self.git("switch", "--quiet", "main")
        self.move_main()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout, "TASK-1: review → done\n")
        self.assertTrue((self.logs / "agent").exists())

    def test_agent_and_setup_see_the_branch_rebased_on_main(self):
        self.branch_for_review()
        self.move_main()
        main_head = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → done")
        self.assertEqual((self.logs / "setup").read_text(), "rebased")
        self.assertEqual((self.logs / "agent").read_text(), "rebased")
        self.assertEqual((self.logs / "main.txt").read_text(), "from main\n")
        self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
        self.assertEqual(self.git("rev-list", "--merges", "--count", "main..task-1").strip(), "0")

    def test_conflict_moves_the_ticket_to_doing_without_starting_the_agent(self):
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")
        branch_head = self.git("rev-parse", "task-1").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → doing")
        self.assertFalse((self.logs / "agent").exists())
        self.assertFalse((self.logs / "setup").exists())
        self.assert_no_rebase_in_progress()
        self.assertEqual(self.git("status", "--porcelain", cwd=self.worktree), "")
        self.assertEqual(self.git("rev-parse", "task-1~1").strip(), branch_head)
        notes = self.ticket().section("Notes") or ""
        self.assertIn("Review failed (integration):", notes)
        self.assertIn("`shared.txt`", notes)

    def test_a_recorded_resolution_is_not_replayed_into_the_review(self):
        # With `rerere.autoupdate`, Git stages a replayed resolution, leaving no
        # unmerged path, yet the rebase still stops.
        self.git("config", "rerere.enabled", "true")
        self.git("config", "rerere.autoupdate", "true")
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")
        branch_head = self.git("rev-parse", "task-1").strip()
        self.git("switch", "--quiet", "task-1")
        subprocess.run(["git", "rebase", "main"], cwd=self.root, capture_output=True, check=False)
        (self.root / "shared.txt").write_text("resolved\n")
        self.git("add", "shared.txt")
        subprocess.run(
            ["git", "rebase", "--continue"],
            cwd=self.root,
            capture_output=True,
            check=True,
            env={**os.environ, "GIT_EDITOR": "true"},
        )
        self.git("reset", "--quiet", "--hard", branch_head)
        self.git("switch", "--quiet", "main")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → doing")
        self.assertFalse((self.logs / "agent").exists())
        self.assert_no_rebase_in_progress()
        self.assertEqual(self.git("status", "--porcelain", cwd=self.worktree), "")
        notes = self.ticket().section("Notes") or ""
        self.assertIn("Review failed (integration):", notes)
        self.assertIn("`shared.txt`", notes)

    def test_uncommitted_files_move_the_ticket_to_doing_without_starting_the_agent(self):
        self.branch_for_review()
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        (self.worktree / "work.txt").write_text("changed\n")
        (self.worktree / "stray.txt").write_text("untracked\n")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → doing")
        self.assertFalse((self.logs / "agent").exists())
        notes = self.ticket().section("Notes") or ""
        self.assertIn("Review failed (work):", notes)
        self.assertIn("`stray.txt`", notes)
        self.assertIn("`work.txt`", notes)

    def test_conflict_fails_a_ticket_with_criteria_without_verdict_lines(self):
        self.run_cli("edit", "1", "--ac", "It works")
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → doing")
        self.assertIn("Review failed (integration):", self.ticket().section("Notes") or "")

    def test_uncommitted_files_fail_a_ticket_with_criteria_without_verdict_lines(self):
        self.run_cli("edit", "1", "--ac", "It works")
        self.branch_for_review()
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        (self.worktree / "stray.txt").write_text("untracked\n")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → doing")
        self.assertIn("Review failed (work):", self.ticket().section("Notes") or "")

    def test_a_manual_review_failure_still_requires_verdict_lines(self):
        self.run_cli("edit", "1", "--ac", "It works")
        self.branch_for_review()

        result = self.run_cli(
            "edit",
            "1",
            "-s",
            "doing",
            "--note",
            "nope",
            "--override-review-independence",
            exit_code=1,
        )

        self.assertIn("review verdict lines must match", result.stderr)

    def test_an_unfinished_rebase_fails_loudly_without_a_status_change(self):
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        rebase = subprocess.run(
            ["git", "rebase", "main"], cwd=self.worktree, capture_output=True, check=False
        )
        self.assertNotEqual(rebase.returncode, 0)

        result = self.run_cli("run", "--mode", "review", exit_code=1)

        self.assertIn("unfinished rebase", result.stderr)
        self.assertEqual(self.ticket().frontmatter.status, "review")
        self.assertFalse((self.logs / "agent").exists())

    def test_automatic_and_reviewer_failures_count_together(self):
        self.branch_for_review(shared="from the branch\n", failures=2)
        self.move_main(shared="from main\n")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout, "TASK-1: review → blocked\n")
        frontmatter = self.ticket().frontmatter
        self.assertEqual((frontmatter.status, frontmatter.owner), ("blocked", "human"))
        self.assertIn("failed review 3 times", self.ticket().section("Notes") or "")

    def test_interrupting_the_rebase_aborts_it_and_exits_130(self):
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")

        def interrupted(root: Path, onto: str) -> list[str]:
            subprocess.run(["git", "rebase", onto], cwd=root, capture_output=True, check=False)
            raise KeyboardInterrupt

        with mock.patch("chitty.git.rebase", side_effect=interrupted):
            result = self.run_cli("run", "--mode", "review", exit_code=130)

        self.assertIn("interrupted during rebase", result.stderr)
        self.assert_no_rebase_in_progress()
        self.assertEqual(self.ticket().frontmatter.status, "review")
