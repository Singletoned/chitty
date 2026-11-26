import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

from chitty.git import rebase_in_progress
from chitty.run import _changed_agents_block
from chitty.store import Repo
from tests.test_cli import CliTestCase

# Records, from the worktree it runs in, whether the branch already contains `main`.
REPORT = (
    "import subprocess, sys\n"
    "from pathlib import Path\n"
    "merged = subprocess.run(['git', 'merge-base', '--is-ancestor', 'main', 'HEAD']).returncode\n"
    "Path(sys.argv[1]).write_text('merged' if merged == 0 else 'not merged')\n"
)


class ReviewMergeTestCase(CliTestCase):
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
            + "with Path(sys.argv[6]).open('a') as starts:\n"
            "    starts.write(subprocess.check_output(\n"
            "        ['git', 'rev-list', '--merges', '--count', 'main..HEAD'], text=True))\n"
            + "if Path('main.txt').exists():\n"
            "    Path(sys.argv[4]).write_text(Path('main.txt').read_text())\n"
            "path = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "path.write_text(path.read_text().replace('status: review', 'status: done'))\n"
            "subprocess.run(['git', 'commit', '--allow-empty', '--quiet', '-am', 'reviewed'], "
            "check=True)\n"
            "if 'status: error' in path.read_text():\n"
            "    sys.exit(1)\n"
            "if Path(sys.argv[5]).exists():\n"
            "    root = Path(sys.argv[5]).read_text().strip()\n"
            "    Path(root, 'main-late.txt').write_text('main advanced during review\\n')\n"
            "    subprocess.run(['git', '-C', root, 'add', 'main-late.txt'], check=True)\n"
            "    subprocess.run(['git', '-C', root, 'commit', '--quiet', '-m', 'main advanced'], "
            "check=True)\n"
        )
        agent.chmod(agent.stat().st_mode | stat.S_IXUSR)
        previous_path = os.environ["PATH"]
        os.environ["PATH"] = f"{agent.parent}:{previous_path}"
        self.addCleanup(os.environ.__setitem__, "PATH", previous_path)
        check_script = self.tmp / "landing_check.py"
        holder_code = (
            "import fcntl, subprocess, sys, time\n"
            "from pathlib import Path\n"
            "root, held = map(Path, sys.argv[1:])\n"
            "with (root / '.git/chitty/run/main-checkout.lock').open('w') as lock:\n"
            "    fcntl.flock(lock, fcntl.LOCK_EX)\n"
            "    (root / 'shared.txt').write_text('dirty\\n')\n"
            "    held.write_text('held')\n"
            "    time.sleep(2)\n"
            "    subprocess.run(\n"
            "        ['git', '-C', str(root), 'checkout', '--', 'shared.txt'], check=True\n"
            "    )\n"
        )
        check_script.write_text(
            "import subprocess, sys, time\nfrom pathlib import Path\n"
            "if Path('main-late.txt').exists() or Path('review-marker').exists():\n"
            "    Path(sys.argv[1]).write_text('checked merged main')\n"
            "    if Path(sys.argv[2]).exists():\n"
            "        print('LANDING_MARKER')\n"
            "        raise SystemExit(7)\n"
            "    if Path(sys.argv[3]).exists():\n"
            "        held = Path(sys.argv[3]).with_name('hold_main_held')\n"
            "        held.unlink(missing_ok=True)\n"
            f"        holder = {holder_code!r}\n"
            "        subprocess.Popen(\n"
            "            [sys.executable, '-c', holder,\n"
            "             Path(sys.argv[3]).read_text(), str(held)],\n"
            "            start_new_session=True, stdout=subprocess.DEVNULL,\n"
            "            stderr=subprocess.DEVNULL,\n"
            "        )\n"
            "        deadline = time.monotonic() + 30\n"
            "        while not held.exists() and time.monotonic() < deadline:\n"
            "            time.sleep(0.05)\n"
            "        if not held.exists():\n"
            "            raise SystemExit('main-checkout lock holder did not start')\n"
        )
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
                f"{self.logs / 'main.txt'} {self.logs / 'advance_main'} "
                f'{self.logs / "review-starts"}"',
            )
            .replace(
                'check = "true"',
                f'check = "{sys.executable} {check_script} '
                f"{self.logs / 'landing_check'} {self.logs / 'fail_landing_check'} "
                f'{self.logs / "hold_main"}"',
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
        self.git("commit", "--quiet", "-m", "work\n\nTask: TASK-1")
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
            with mock.patch.dict(
                os.environ, {"GIT_AUTHOR_DATE": f"@{int(time.time()) + 60} +0000"}
            ):
                self.git("commit", "--quiet", "--allow-empty", "-m", "fix review")
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
        self.assertFalse(rebase_in_progress(self.worktree), "rebase in progress")


class TestReviewMerge(ReviewMergeTestCase):
    def test_agents_file_present_only_on_branch_is_detected(self):
        self.branch_for_review()
        self.git("switch", "--quiet", "main")
        (self.root / "AGENTS.md").unlink()
        self.git("add", "-u", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "remove agents guide")
        self.git("switch", "--quiet", "task-1")
        (self.root / "AGENTS.md").write_text("branch-only instructions\n")

        self.assertTrue(_changed_agents_block(self.root))

    def test_main_only_managed_block_change_does_not_change_branch(self):
        self.branch_for_review()
        agents = self.root / "AGENTS.md"
        agents.write_text(
            agents.read_text().replace(
                "Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit",
                "Tasks live in `tickets/`; use the `chitty` CLI or MCP, and do not hand-edit",
            )
        )
        self.git("add", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "refresh managed guide")
        self.git("switch", "--quiet", "task-1")

        self.assertFalse(_changed_agents_block(self.root))

    def test_branch_managed_block_change_is_detected_after_main_changes_too(self):
        self.branch_for_review()
        self.git("switch", "--quiet", "task-1")
        agents = self.root / "AGENTS.md"
        branch_text = agents.read_text()
        changed_branch_text = branch_text.replace(
            "Tasks live in `chitty/`", "Tasks live in `branch-tickets/`"
        )
        self.assertNotEqual(branch_text, changed_branch_text)
        agents.write_text(changed_branch_text)
        self.git("add", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "change branch managed guide")
        self.git("switch", "--quiet", "main")
        agents.write_text(self.git("show", "main:AGENTS.md"))
        main_text = agents.read_text()
        agents.write_text(
            main_text.replace("<!-- chitty:end -->", "Main refresh.\n<!-- chitty:end -->")
        )
        self.git("add", "AGENTS.md")
        self.git("commit", "--quiet", "-m", "refresh main managed guide")
        self.git("switch", "--quiet", "task-1")
        agents.write_text(self.git("show", "task-1:AGENTS.md"))

        self.assertNotEqual(
            self.git("show", "task-1:AGENTS.md"),
            self.git("show", "main:AGENTS.md"),
        )
        merge_base = self.git("merge-base", "main", "task-1").strip()
        self.assertNotEqual(
            self.git("show", f"{merge_base}:AGENTS.md"),
            self.git("show", "task-1:AGENTS.md"),
        )
        self.assertTrue(_changed_agents_block(self.root, "main"))

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

    def test_missing_review_branch_errors_and_is_selected_for_repair(self):
        self.branch_for_review()
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        self.git("worktree", "remove", "--force", str(self.worktree))
        self.git("branch", "-D", "task-1")
        self.run_cli("edit", "1", "-s", "review")
        self.assertEqual(
            Repo.open(self.root).find(Repo.open(self.root).resolve("1")).task.frontmatter.status,
            "review",
        )

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout, "TASK-1: review → error\n")
        self.assertFalse((self.logs / "agent").exists())
        ticket = Repo.open(self.root).find(Repo.open(self.root).resolve("1")).task
        self.assertIsNone(ticket.frontmatter.owner)
        notes = ticket.section("Notes") or ""
        self.assertIn("Runner error (review)", notes)
        self.assertIn("TASK-1", notes)
        self.assertIn("task-1", notes)
        for mode in ("review", "work"):
            idle = self.run_cli("run", "--mode", mode, exit_code=3)
            self.assertIn("no next ticket", idle.stderr)
        self.run_cli("next", exit_code=3)
        repair = self.run_cli("run", "--errors")
        self.assertEqual(repair.stdout, "TASK-1: error → error\n")

    def test_review_lands_directly_without_an_extra_review(self):
        self.branch_for_review()
        base = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → done")
        self.assertEqual(self.git("merge-base", base, "main").strip(), base)
        self.assertNotEqual(self.git("rev-parse", "main").strip(), base)
        self.assertEqual(self.git("rev-list", "--merges", "--count", "main").strip(), "0")
        self.assertIn(
            "status: done", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )
        self.assertFalse(self.worktree.exists())
        self.assertFalse(self.git("branch", "--list", "task-1").strip())

    def test_landing_waits_for_main_checkout_write(self):
        self.branch_for_review(shared="branch\n")
        (self.logs / "advance_main").write_text(str(self.root))
        (self.logs / "hold_main").write_text(str(self.root))

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout, "TASK-1: review → done\n")
        self.assertEqual(self.git("show", "main:shared.txt"), "branch\n")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertFalse(self.worktree.exists())
        self.assertFalse(self.git("branch", "--list", "task-1").strip())

    def test_main_advances_during_review_and_landing_checks_merged_branch(self):
        self.branch_for_review()
        (self.logs / "advance_main").write_text(str(self.root))
        before = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → done")
        self.assertEqual((self.logs / "landing_check").read_text(), "checked merged main")
        self.assertEqual((self.root / "main-late.txt").read_text(), "main advanced during review\n")
        self.assertNotEqual(self.git("rev-parse", "main").strip(), before)
        self.assertEqual(self.git("rev-list", "--merges", "--count", "main").strip(), "0")
        self.assertIn(
            "status: done", next((self.root / "chitty/tasks").glob("TASK-1--*.md")).read_text()
        )
        self.assertFalse(self.worktree.exists())
        self.assertFalse(self.git("branch", "--list", "task-1").strip())

    def test_review_setup_failure_records_error_on_branch(self):
        self.branch_for_review()
        config = self.root / "chitty.toml"
        # Keep the failing setup command in a main commit so review preflight uses it.
        config.write_text(
            re.sub(r"^setup = .*$", 'setup = "false"', config.read_text(), flags=re.MULTILINE)
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure failing setup")
        main_head = self.git("rev-parse", "main").strip()
        ticket_path = "chitty/tasks/TASK-1--review-me.md"
        main_ticket = self.git("show", f"main:{ticket_path}")

        result = self.run_cli("run", "--mode", "review")

        self.assertIn("review → error", result.stdout)
        self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
        self.assertEqual(self.git("show", f"main:{ticket_path}"), main_ticket)
        branch_ticket = self.git("show", f"task-1:{ticket_path}")
        self.assertIn("status: error", branch_ticket)
        self.assertIn("Runner error (setup)", branch_ticket)
        self.assertIn("setup exited with status 1", branch_ticket)
        prior_ticket = self.git("show", f"task-1~1:{ticket_path}")
        self.assertIn("status: review", prior_ticket)
        self.assertNotIn("Runner error", prior_ticket)

    def test_landing_failure_escalates_after_two_failures(self):
        self.branch_for_review(failures=2)
        (self.logs / "advance_main").write_text(str(self.root))
        (self.logs / "fail_landing_check").write_text("fail")
        self.run_cli("run", "--mode", "review")
        ticket = self.ticket()
        self.assertEqual(ticket.frontmatter.status, "blocked")
        self.assertEqual(ticket.frontmatter.owner, "human")
        notes = ticket.section("Notes") or ""
        self.assertIn("Escalated to human review: failed review 3 times", notes)
        self.assertIn("Review failed (integration):", notes)

    def test_failing_check_after_main_advances_preserves_main_and_worktree(self):
        self.branch_for_review()
        (self.logs / "advance_main").write_text(str(self.root))
        (self.logs / "fail_landing_check").write_text("fail")

        result = self.run_cli("run", "--mode", "review")

        self.assertIn("done → doing", result.stdout)
        notes = self.ticket().section("Notes") or ""
        self.assertIn("landing check exited with status 7", notes)
        self.assertIn("landing check exited with status 7; output in `.chitty/check.log`", notes)
        self.assertIn("LANDING_MARKER", notes)
        self.assertIn("Review failed (integration):", notes)
        self.assertNotIn("Resolve the landing problem", notes)
        self.git("merge-base", "--is-ancestor", "main", "task-1")
        log = (self.worktree / ".chitty/check.log").read_text()
        self.assertTrue(log.startswith("# chitty landing check: "))
        self.assertIn("LANDING_MARKER", log)
        self.assertTrue(log.endswith("# exit 7\n"))
        self.assertIn(str(self.worktree), notes)
        self.assertEqual((self.logs / "landing_check").read_text(), "checked merged main")
        self.assertIn(
            "main advanced",
            self.git("log", "-3", "--format=%s", "main"),
        )
        self.assertEqual(self.git("rev-list", "--merges", "--count", "main").strip(), "0")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertTrue(self.worktree.exists())
        self.assertTrue(self.git("branch", "--list", "task-1").strip())

    def test_missing_landing_command_records_error(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                "autocommit = true",
                f'autocommit = true\nlanding_check = "{self.tmp / "missing-command"}"',
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure missing check")
        self.branch_for_review()
        result = self.run_cli("run", "--mode", "review")
        self.assertIn("done → error", result.stdout)
        ticket = self.git("show", "task-1:chitty/tasks/TASK-1--review-me.md")
        self.assertIn("Runner error (landing)", ticket)
        self.assertIn("command not found", ticket)

    def test_landing_check_timeout_records_error_without_advancing_main(self):
        slow = self.tmp / "slow-landing"
        slow.write_text(
            f"#!{sys.executable}\nimport time\nprint('landing', flush=True)\ntime.sleep(5)\n"
        )
        slow.chmod(slow.stat().st_mode | stat.S_IXUSR)
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                "autocommit = true",
                f'autocommit = true\ncommand_timeout = 1\nlanding_check = "{slow}"',
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure landing timeout")
        self.branch_for_review()
        main_head = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertIn("done → error", result.stdout)
        self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
        branch_ticket = self.git("show", "task-1:chitty/tasks/TASK-1--review-me.md")
        self.assertIn("Runner error (landing)", branch_ticket)
        self.assertIn("landing check timed out after 1 seconds", branch_ticket)
        log = (self.worktree / ".chitty/check.log").read_text()
        self.assertTrue(log.startswith("# chitty landing check: "))
        self.assertTrue(log.endswith("# timed out after 1 seconds\n"))
        self.assertTrue(self.worktree.exists())
        self.assertTrue(self.git("branch", "--list", "task-1").strip())

    def test_landing_failure_records_error_on_branch_without_advancing_main(self):
        self.branch_for_review()
        fake = self.tmp / "bin" / "fake"
        fake.parent.mkdir(exist_ok=True)
        fake.write_text(
            "#!" + sys.executable + "\n"
            "from pathlib import Path\n"
            "import subprocess\n"
            "ticket = next(Path('chitty/tasks').glob('TASK-1--*.md'))\n"
            "ticket.write_text(ticket.read_text().replace('status: review', 'status: done'))\n"
            "Path('review-marker').write_text('fail landing check')\n"
            "subprocess.run(['git', 'add', 'review-marker'], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-am', 'reviewed'], "
            "check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        check_script = self.tmp / "landing_check.py"
        check_script.write_text(
            "from pathlib import Path\n"
            "if Path('review-marker').exists():\n"
            "    raise SystemExit(7)\n"
        )
        config = self.root / "chitty.toml"
        config.write_text(
            re.sub(
                r"^check = .*",
                f'check = "{sys.executable} {check_script}"',
                config.read_text(),
                flags=re.MULTILINE,
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure marker check")
        main_head = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertIn("done → doing", result.stdout)
        self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
        ticket_path = "chitty/tasks/TASK-1--review-me.md"
        branch_ticket = self.git("show", f"task-1:{ticket_path}")
        self.assertIn("status: doing", branch_ticket)
        self.assertIn("Review failed (integration):", branch_ticket)
        self.assertIn(
            "landing check exited with status 7; output in `.chitty/check.log`", branch_ticket
        )
        self.assertIn(str(self.worktree), branch_ticket)
        self.assertNotIn("Resolve the landing problem", branch_ticket)
        self.assertIn("status: done", self.git("show", f"task-1~1:{ticket_path}"))
        latest_paths = self.git(
            "diff-tree", "--no-commit-id", "--name-only", "-r", "task-1"
        ).splitlines()
        self.assertEqual(latest_paths, [ticket_path])

    def test_agent_and_setup_see_the_branch_merged_with_main(self):
        self.branch_for_review()
        self.move_main()
        main_head = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → done")
        self.assertEqual((self.logs / "setup").read_text(), "merged")
        self.assertEqual((self.logs / "agent").read_text(), "merged")
        self.assertEqual((self.logs / "review-starts").read_text(), "0\n")
        self.assertEqual((self.logs / "main.txt").read_text(), "from main\n")
        landed_head = self.git("rev-parse", "main").strip()
        self.assertNotEqual(landed_head, main_head)
        self.assertEqual(self.git("rev-list", "--merges", "--count", "main").strip(), "0")
        self.assertFalse(self.worktree.exists())
        self.assertFalse(self.git("branch", "--list", "task-1").strip())

    def test_conflict_moves_the_ticket_to_doing_without_starting_the_agent(self):
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")
        branch_head = self.git("rev-parse", "task-1").strip()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → doing")
        self.assertFalse((self.logs / "agent").exists())
        self.assertFalse((self.logs / "setup").exists())
        self.assertFalse((self.logs / "review-starts").exists())
        self.assertFalse(rebase_in_progress(self.worktree))
        self.assertEqual(self.git("status", "--porcelain", cwd=self.worktree), "")
        self.assertEqual(self.git("rev-parse", "task-1~1").strip(), branch_head)
        notes = self.ticket().section("Notes") or ""
        self.assertIn(
            "Review failed (integration): rebasing onto `main` conflicts in `shared.txt`",
            notes,
        )

    def test_a_recorded_resolution_is_not_replayed_into_the_review(self):
        # With `rerere.autoupdate`, Git stages a replayed resolution, leaving no
        # unmerged path, yet the merge still stops.
        self.git("config", "rerere.enabled", "true")
        self.git("config", "rerere.autoupdate", "true")
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")
        branch_head = self.git("rev-parse", "task-1").strip()
        self.git("switch", "--quiet", "task-1")
        subprocess.run(["git", "merge", "main"], cwd=self.root, capture_output=True, check=False)
        (self.root / "shared.txt").write_text("resolved\n")
        self.git("add", "shared.txt")
        subprocess.run(
            ["git", "commit", "--quiet", "--no-edit"],
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
        self.assertFalse(rebase_in_progress(self.worktree))
        self.assertEqual(self.git("status", "--porcelain", cwd=self.worktree), "")
        notes = self.ticket().section("Notes") or ""
        self.assertIn("Review failed (integration):", notes)
        self.assertIn("`shared.txt`", notes)

    def test_uncommitted_files_block_for_human_without_starting_the_agent(self):
        self.branch_for_review()
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        (self.worktree / "work.txt").write_text("changed\n")
        (self.worktree / "stray.txt").write_text("untracked\n")

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → blocked")
        self.assertFalse((self.logs / "agent").exists())
        ticket = self.ticket()
        self.assertEqual(ticket.frontmatter.owner, "human")
        notes = ticket.section("Notes") or ""
        self.assertIn("Review blocked (work):", notes)
        self.assertIn("human", notes)
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

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → blocked")
        self.assertEqual(self.ticket().frontmatter.owner, "human")
        self.assertIn("Review blocked (work):", self.ticket().section("Notes") or "")

    def test_check_that_dirties_review_worktree_blocks_before_agent(self):
        self.branch_for_review()
        check_script = self.tmp / "landing_check.py"
        check_script.write_text(
            check_script.read_text() + "Path('check-created.txt').write_text('left over')\n"
        )

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → blocked")
        self.assertEqual(self.ticket().frontmatter.owner, "human")
        self.assertFalse((self.logs / "agent").exists())
        self.assertIn("`check-created.txt`", self.ticket().section("Notes") or "")

    def test_dirty_branch_cannot_enter_review_until_committed(self):
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", "doing")
        (self.root / "untracked.txt").write_text("unfinished\n")
        self.run_cli("check")  # Work can be checked before the changes are committed.

        rejected = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("uncommitted changes", rejected.output)
        self.assertIn("untracked.txt", rejected.output)
        self.assertEqual(
            Repo.open(self.root).find(Repo.open(self.root).resolve("1")).task.frontmatter.status,
            "doing",
        )

        self.git("add", "untracked.txt")
        staged = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn("untracked.txt", staged.output)
        self.git("commit", "--quiet", "-m", "finish work\n\nTask: TASK-1")
        self.run_cli("edit", "1", "-s", "review")

    def test_dirty_review_worktree_cannot_be_marked_done_but_can_be_blocked(self):
        self.branch_for_review()
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        (self.worktree / "untracked.txt").write_text("unfinished\n")
        os.chdir(self.worktree)
        try:
            rejected = self.run_cli(
                "edit",
                "1",
                "-s",
                "done",
                "--note",
                "Reviewed: ready.",
                "--override-review-independence",
                exit_code=1,
            )
            self.assertIn("uncommitted changes", rejected.output)
            self.run_cli(
                "edit",
                "1",
                "-s",
                "blocked",
                "--owner",
                "human",
                "--note",
                "Review blocked (work): untracked.txt needs human resolution.",
            )
        finally:
            os.chdir(self.root)
        self.assertEqual(self.ticket().frontmatter.owner, "human")
        self.assertEqual(self.ticket().frontmatter.status, "blocked")

    def test_check_flags_a_review_worktree_that_became_dirty(self):
        self.branch_for_review()
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        (self.worktree / "untracked.txt").write_text("unfinished\n")
        os.chdir(self.worktree)
        try:
            result = self.run_cli("check", exit_code=1)
        finally:
            os.chdir(self.root)
        self.assertIn("review worktree has uncommitted changes", result.output)
        self.assertIn("untracked.txt", result.output)

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

    def test_an_unfinished_merge_fails_loudly_without_a_status_change(self):
        self.branch_for_review(shared="from the branch\n")
        self.move_main(shared="from main\n")
        self.git("worktree", "add", "--quiet", str(self.worktree), "task-1")
        merge = subprocess.run(
            ["git", "merge", "main"], cwd=self.worktree, capture_output=True, check=False
        )
        self.assertNotEqual(merge.returncode, 0)

        result = self.run_cli("run", "--mode", "review", exit_code=1)

        self.assertIn("unfinished merge", result.stderr)
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

        with mock.patch("chitty.git.rebase_onto", side_effect=interrupted):
            result = self.run_cli("run", "--mode", "review", exit_code=130)

        self.assertIn("interrupted during rebase", result.stderr)
        self.assertFalse(rebase_in_progress(self.worktree))
        self.assertEqual(self.ticket().frontmatter.status, "review")
