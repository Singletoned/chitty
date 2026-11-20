import shlex
import sys
from pathlib import Path
from unittest.mock import patch

from chitty.errors import ChittyError
from chitty.run import _land
from chitty.store import NextAction
from tests.test_landing import LandingTestCase


class TestLandingRetry(LandingTestCase):
    def run_script(self, mode: str) -> Path:
        count = self.tmp / "runs"
        script = self.tmp / "check.py"
        script.write_text(
            "import pathlib, subprocess, sys\n"
            "main, count, mode = (pathlib.Path(sys.argv[1]), "
            "pathlib.Path(sys.argv[2]), sys.argv[3])\n"
            "runs = count.read_text().splitlines() if count.exists() else []\n"
            "if len(runs) >= 10: sys.exit(2)\n"
            "number = len(runs) + 1\n"
            "with count.open('a') as output: output.write(str(number) + '\\n')\n"
            "if mode == 'once' and number > 1: sys.exit(0)\n"
            "if mode in ('ticket', 'mixed') and number == 1:\n"
            "    task = next((main / 'chitty/tasks').glob('TASK-1--*.md'))\n"
            "    moved = main / 'chitty/tasks/TASK-9--moved.md'\n"
            "    moved.write_text(task.read_text())\n"
            "    paths = [moved.relative_to(main)]\n"
            "    if mode == 'mixed':\n"
            "        check = main / 'check-1.txt'\n"
            "        check.write_text('main\\n')\n"
            "        paths.append(check.relative_to(main))\n"
            "    subprocess.run(['git', '-C', str(main), 'add', *map(str, paths)], check=True)\n"
            "    subprocess.run(['git', '-C', str(main), 'commit', '--quiet',\n"
            "                    '-m', 'check move'], check=True)\n"
            "    (count.parent / 'check-commit').write_text(\n"
            "        subprocess.check_output(['git', '-C', str(main), 'rev-parse',\n"
            "                                 'HEAD'], text=True))\n"
            "if mode == 'untracked' and number == 1:\n"
            "    (main / 'added.txt').write_text('main\\n')\n"
            "elif mode == 'always' or (mode in ('once', 'conflict') and number == 1):\n"
            "    if mode == 'conflict':\n"
            "        task = next((main / 'chitty/tasks').glob('TASK-1--*.md'))\n"
            "        task.write_text(task.read_text().replace(\n"
            "            'status: todo', 'status: planning'))\n"
            "        path = task.relative_to(main)\n"
            "    else:\n"
            "        path = pathlib.Path('check-' + str(number) + '.txt')\n"
            "        (main / path).write_text('main\\n')\n"
            "    subprocess.run(['git', '-C', str(main), 'add', str(path)], check=True)\n"
            "    subprocess.run(['git', '-C', str(main), 'commit', '--quiet',\n"
            "                    '-m', 'check move'], check=True)\n"
            "    (count.parent / 'check-commit').write_text(\n"
            "        subprocess.check_output(['git', '-C', str(main), 'rev-parse',\n"
            "                                 'HEAD'], text=True))\n"
        )
        return count

    def land_with_script(self, mode: str) -> Path:
        count = self.run_script(mode)
        command = shlex.join(
            [sys.executable, str(self.tmp / "check.py"), str(self.root), str(count), mode]
        )
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        _land(self.main_repo, self.worktree, action, "true", command)
        return count

    def branch_commits(self) -> set[str]:
        return set(self.git("rev-list", f"main..{self.branch}").splitlines())

    def test_ticket_only_move_lands_without_a_second_check(self):
        self.finish_ticket()
        branch_subjects = self.git("log", "--format=%s", f"main..{self.branch}").splitlines()
        count = self.land_with_script("ticket")
        landed = set(self.git("rev-list", "main").splitlines())
        self.assertEqual(len(count.read_text().splitlines()), 1)
        self.assertIn((self.tmp / "check-commit").read_text().strip(), landed)
        self.assertIn(
            "chitty/tasks/TASK-9--moved.md", self.git("ls-tree", "-r", "--name-only", "main")
        )
        landed_subjects = self.git("log", "--format=%s", "main").splitlines()
        self.assertTrue(set(branch_subjects) <= set(landed_subjects))
        self.assertFalse(self.worktree.exists())
        self.assertEqual(self.git("branch", "--list", self.branch), "")

    def test_mixed_move_reruns_the_check(self):
        self.finish_ticket()
        count = self.land_with_script("mixed")
        self.assertEqual(len(count.read_text().splitlines()), 2)
        self.assertFalse(self.worktree.exists())

    def test_retries_when_main_moves_once(self):
        self.finish_ticket()
        branch_subjects = self.git("log", "--format=%s", f"main..{self.branch}").splitlines()
        count = self.land_with_script("once")
        landed_subjects = self.git("log", "--format=%s", "main").splitlines()
        landed = set(self.git("rev-list", "main").splitlines())
        self.assertTrue(set(branch_subjects) <= set(landed_subjects))
        check_commit = (self.tmp / "check-commit").read_text().strip()
        self.assertIn(check_commit, landed)
        self.assertEqual(len(count.read_text().splitlines()), 2)
        self.assertFalse(self.worktree.exists())
        self.assertEqual(self.git("branch", "--list", self.branch), "")

    def test_stops_after_three_main_moves(self):
        self.finish_ticket()
        branch_commits = self.branch_commits()
        start = self.git("rev-parse", "main").strip()
        count = self.run_script("always")
        command = shlex.join(
            [sys.executable, str(self.tmp / "check.py"), str(self.root), str(count), "always"]
        )
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        with self.assertRaisesRegex(
            ChittyError, "main moved during each of the 3 landing attempts"
        ):
            _land(self.main_repo, self.worktree, action, "true", command)
        moved = set(self.git("rev-list", f"{start}..main").splitlines())
        self.assertEqual(len(count.read_text().splitlines()), 3)
        self.assertEqual(len(moved), 3)
        self.assertFalse(moved & branch_commits)
        self.assertTrue(self.worktree.exists())
        self.assertIn(self.branch, self.git("branch", "--list", self.branch))

    def test_quick_path_stops_after_ten_ticket_moves(self):
        self.finish_ticket()
        count = self.tmp / "runs"
        command = shlex.join(
            [
                sys.executable,
                "-c",
                "import pathlib,sys; pathlib.Path(sys.argv[1]).open('a').write('run\\n')",
                str(count),
            ]
        )
        real_fast_forward = __import__("chitty.run", fromlist=["git"]).git.fast_forward
        calls = 0

        def moving_fast_forward(root, branch):
            nonlocal calls
            calls += 1
            if calls > 20:
                raise AssertionError("fast-forward called more than 20 times")
            task = next((self.root / "chitty/tasks").glob("TASK-1--*.md"))
            moved = self.root / f"chitty/tasks/TASK-{20 + calls}--moved.md"
            moved.write_text(task.read_text())
            self.git("add", str(moved))
            self.git("commit", "--quiet", "-m", "ticket move")
            return real_fast_forward(root, branch)

        with (
            patch("chitty.run.git.fast_forward", side_effect=moving_fast_forward),
            self.assertRaisesRegex(
                ChittyError, "main moved during each of the 10 quick landing attempts"
            ),
        ):
            action = NextAction("review", self.main_repo.resolve(self.ticket))
            _land(self.main_repo, self.worktree, action, "true", command)
        self.assertEqual(calls, 11)
        self.assertEqual(len(count.read_text().splitlines()), 1)
        self.assertTrue(self.worktree.exists())
        self.assertIn(self.branch, self.git("branch", "--list", self.branch))

    def test_conflict_on_retry_stops_before_second_check(self):
        self.finish_ticket()
        branch_commits = self.branch_commits()
        count = self.run_script("conflict")
        command = shlex.join(
            [sys.executable, str(self.tmp / "check.py"), str(self.root), str(count), "conflict"]
        )
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        with self.assertRaisesRegex(ChittyError, "conflicts in"):
            _land(self.main_repo, self.worktree, action, "true", command)
        self.assertEqual(len(count.read_text().splitlines()), 1)
        self.assertFalse(branch_commits & set(self.git("rev-list", "main").splitlines()))
        self.assertTrue(self.worktree.exists())

    def test_fast_forward_failure_without_main_move_is_not_retried(self):
        self.finish_ticket()
        (self.worktree / "added.txt").write_text("branch\n")
        self.git("add", "added.txt", cwd=self.worktree)
        self.git("commit", "--quiet", "-m", "branch added file", cwd=self.worktree)
        main_head = self.git("rev-parse", "main").strip()
        worktree_head = self.git("rev-parse", self.branch, cwd=self.worktree).strip()
        worktree_status = self.git(
            "status", "--porcelain", "--untracked-files=all", cwd=self.worktree
        )
        count = self.run_script("untracked")
        command = shlex.join(
            [sys.executable, str(self.tmp / "check.py"), str(self.root), str(count), "untracked"]
        )
        action = NextAction("review", self.main_repo.resolve(self.ticket))
        with self.assertRaises(ChittyError) as raised:
            _land(self.main_repo, self.worktree, action, "true", command)
        self.assertNotIn("main moved", str(raised.exception))
        self.assertEqual(len(count.read_text().splitlines()), 1)
        self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
        self.assertEqual(
            self.git("rev-parse", f"{self.branch}^{{tree}}", cwd=self.worktree),
            self.git("rev-parse", f"{worktree_head}^{{tree}}", cwd=self.worktree),
        )
        self.assertEqual(
            self.git("status", "--porcelain", "--untracked-files=all", cwd=self.worktree),
            worktree_status,
        )
        self.assertTrue(self.worktree.exists())
