import subprocess
import sys

from tests.test_run_continue import TestRunContinue


class TestRunRepairOnBranch(TestRunContinue):
    def setUp(self):
        super().setUp()
        self.prepare_main_setup()

    def repair_ticket(self, status="review"):
        ticket = self.json("add", "Repair branch", "-d", "Description.", "-s", "error")["id"]
        self.write_repair_agent(ticket, status)
        return ticket

    def write_repair_agent(self, ticket, status):
        fake = self.bindir / "fake-agent"
        fake.write_text(
            f"#!{sys.executable}\n"
            "from pathlib import Path\n"
            "import subprocess\n"
            "Path('repair.py').write_text('fixed = True\\n')\n"
            "subprocess.run(['git', 'add', 'repair.py'], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'repair', "
            f"'-m', 'Task: {ticket}'], check=True)\n"
            f"subprocess.run(['chitty', 'edit', {ticket!r}, '-s', {status!r}"
            + (" , '--note', 'Agent needs a person']" if status == "blocked" else "]")
            + ", check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | __import__("stat").S_IXUSR)

    def test_unbranched_error_repair_creates_branch_and_leaves_main_unchanged(self):
        ticket = self.json("add", "Unbranched repair", "-d", "Description.", "-s", "error")["id"]
        self.write_repair_agent(ticket, "review")
        main_head = self.main_head()

        self.run_cli("run", "--errors")

        self.assertEqual(self.main_head(), main_head)
        self.assertEqual(self.json("show", ticket)["status"], "review")
        branch = ticket.lower()
        self.assertEqual(
            subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip(),
            "main",
        )
        self.assertEqual(
            subprocess.run(
                ["git", "rev-parse", branch],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            ).returncode,
            0,
        )

    def prepare_main_setup(self):
        from chitty.store import Repo

        Repo.open(self.root).refresh_setup()

    def main_head(self):
        return subprocess.run(
            ["git", "rev-parse", "main"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def test_review_repair_stays_on_branch_without_runner_commit(self):
        ticket = self.repair_ticket()
        self.git("branch", ticket.lower())
        main_head = self.main_head()
        branch_head = subprocess.run(
            ["git", "rev-parse", ticket.lower()],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        result = self.run_cli("run", "--errors")

        self.assertIn(f"kept merged branch {ticket.lower()}: {ticket} is error", result.stderr)
        self.assertNotIn("removed merged branch", result.stderr)
        self.assertEqual(result.stdout, f"{ticket}: error → review\n", result.stderr)
        self.assertEqual(self.main_head(), main_head, result.stdout + result.stderr)
        self.assertEqual(self.json("show", ticket)["status"], "review")
        commits = subprocess.run(
            ["git", "log", "--format=%s", branch_head + ".." + ticket.lower()],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(
            commits,
            [f"chitty: edit {ticket} Repair branch", "repair"],
        )

    def test_blocked_repair_appends_runner_note_on_branch(self):
        ticket = self.repair_ticket("blocked")
        owner = "repair-agent"
        self.run_cli("edit", ticket, "--owner", owner)
        self.git("branch", ticket.lower())
        main_head = self.main_head()

        run_result = self.run_cli("run", "--errors")

        self.assertEqual(self.main_head(), main_head, run_result.stdout + run_result.stderr)
        result = self.json("show", ticket)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["owner"], owner)
        path = next(
            (self.root / ".worktrees" / ticket.lower() / "chitty/tasks").glob(f"{ticket}--*.md")
        )
        text = path.read_text()
        self.assertIn("Agent needs a person", text)
        self.assertLess(
            text.index("Agent needs a person"),
            text.index("Repair agent determined that human action is required."),
        )
