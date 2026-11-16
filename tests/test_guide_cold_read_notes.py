import unittest

from click.testing import CliRunner

from chitty.cli import cli


class TestGuideColdReadNotes(unittest.TestCase):
    def run_guide(self, *args: str) -> str:
        result = CliRunner().invoke(cli, ["guide", *args], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return result.stdout

    def test_cold_read_tells_reader_to_skip_notes(self):
        output = self.run_guide("cold-read", "TASK-1")
        self.assertIn("Work only from its Description and", output)
        self.assertIn("Acceptance Criteria; skip Notes", output)
        self.assertIn("skip Notes", output)

    def test_plan_reports_finding_outcomes(self):
        output = " ".join(self.run_guide("plan").split())
        self.assertIn("resolve every reader finding and sufficiency gap", output)
        self.assertIn("strengthen the ticket, split it, or explicitly reject the finding", output)
        self.assertIn("expected route", output)


if __name__ == "__main__":
    unittest.main()
