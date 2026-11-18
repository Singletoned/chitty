import subprocess
from pathlib import Path

from tests.test_cli import CliTestCase


class TestProvisionalIds(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "init")
        config = (self.root / "chitty.toml").read_text()
        (self.root / "chitty.toml").write_text(
            config + '\n[contexts.backlog]\nprefix = "BACKLOG"\nrandom_ids = true\n'
        )

    def git(self, *args: str, cwd: Path | None = None):
        return subprocess.run(
            ["git", *args], cwd=cwd or self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def test_add_on_main_is_sequential_and_feature_is_provisional(self):
        main = self.json("add", "Main ticket", "-d", "Description.")
        self.assertEqual(main["id"], "TASK-1")
        self.assertIsNone(main["provisional"])
        self.git("switch", "-c", "feature")
        branch = self.json("add", "Branch ticket", "-d", "Description.")
        self.assertRegex(branch["id"], r"^TASK-[A-Z0-9]*[A-Z][A-Z0-9]*$")
        self.assertTrue(branch["provisional"])

    def test_random_context_stays_numeric_off_main(self):
        self.git("switch", "-c", "feature")
        ticket = self.json("add", "Backlog ticket", "-c", "backlog")
        self.assertTrue(ticket["id"].startswith("BACKLOG-"))
        self.assertTrue(ticket["id"].split("-")[1].isdigit())
        self.assertIsNone(ticket["provisional"])

    def test_missing_main_ref_fails_on_master(self):
        # Deliberately create a master-only repository with no main ref.
        self.git("branch", "-m", "master")
        result = self.run_cli("add", "No ticket", "-d", "Description.", exit_code=1)
        self.assertIn("main", result.output)
        self.assertIn("main_branch", result.output)
        self.assertEqual(list((self.root / "chitty" / "tasks").glob("*.md")), [])
