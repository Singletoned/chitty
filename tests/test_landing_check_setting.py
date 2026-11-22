import re
import sys

from chitty.config import landing_command
from chitty.errors import ChittyError
from chitty.run import _land_pending
from chitty.store import Repo
from tests.test_cli import CliTestCase
from tests.test_landing import LandingTestCase
from tests.test_review_merge import ReviewMergeTestCase


class TestLandingCommand(CliTestCase):
    def test_prefers_landing_check_when_set(self):
        self.assertEqual(landing_command("a", "b"), "b")

    def test_landing_check_can_be_used_without_check(self):
        self.assertEqual(landing_command(None, "b"), "b")

    def test_falls_back_to_check(self):
        self.assertEqual(landing_command("a", None), "a")

    def test_missing_both_names_check(self):
        with self.assertRaisesRegex(ChittyError, "check"):
            landing_command(None, None)

    def test_empty_landing_check_is_not_treated_as_unset(self):
        self.assertEqual(landing_command("a", ""), "")


class TestLandingCheckLoading(CliTestCase):
    def test_blank_landing_check_is_rejected(self):
        config = self.root / "chitty.toml"
        config.write_text('landing_check = "  "\n' + config.read_text())

        result = self.run_cli("list", exit_code=1)

        self.assertIn("landing_check: must not be empty", result.stderr)

    def test_landing_check_is_a_known_setting(self):
        config = self.root / "chitty.toml"
        config.write_text('landing_check = "true"\n' + config.read_text())

        result = self.run_cli("list")

        self.assertNotIn("unknown configuration key", result.stderr)


class TestLandingCheckReview(ReviewMergeTestCase):
    def test_review_uses_landing_check_when_set(self):
        self._configure_checks(landing=True)
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure landing checks")
        self.branch_for_review()

        result = self.run_cli("run", "--mode", "review")

        self.assertEqual(result.stdout.splitlines()[-1], "TASK-1: review → done")
        self.assertEqual((self.logs / "calls").read_text(), "check\ncheck\nlanding\n")

    def test_review_falls_back_to_check_when_unset(self):
        self._configure_checks(landing=False)
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure checks")
        self.branch_for_review()

        self.run_cli("run", "--mode", "review")

        self.assertEqual((self.logs / "calls").read_text(), "check\ncheck\ncheck\n")

    def _configure_checks(self, landing: bool):
        script = self.tmp / "record.py"
        script.write_text(
            "import sys\nfrom pathlib import Path\n"
            "with Path(sys.argv[1]).open('a') as log: log.write(sys.argv[2] + '\\n')\n"
        )
        config = self.root / "chitty.toml"
        replacement = f'check = "{sys.executable} {script} {self.logs / "calls"} check"'
        if landing:
            replacement += (
                f'\nlanding_check = "{sys.executable} {script} {self.logs / "calls"} landing"'
            )
        config.write_text(
            re.sub(r"^check = .*$", replacement, config.read_text(), flags=re.MULTILINE)
        )


class TestLandingCheckPending(LandingTestCase):
    def test_pending_uses_landing_check(self):
        script = self.tmp / "record.py"
        calls = self.tmp / "calls"
        script.write_text(
            "import sys\nfrom pathlib import Path\n"
            "with Path(sys.argv[1]).open('a') as log: log.write(sys.argv[2] + '\\n')\n"
        )
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                'check = "true"',
                f'check = "false"\nlanding_check = "{sys.executable} {script} {calls} landing"',
            )
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "configure landing check")
        self.git("merge", "--ff-only", "--quiet", "main", cwd=self.worktree)
        self.finish_ticket()

        result = _land_pending(Repo.open(self.root))

        self.assertIsNotNone(result)
        self.assertEqual(calls.read_text(), "landing\n")
        self.assertFalse(self.worktree.exists())
