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

    def test_plan_reports_finding_outcomes_in_reply(self):
        output = self.run_guide("plan")
        self.assertIn("Fix or reject each finding", output)
        self.assertIn("in your reply, not in a ticket note", output)

    def test_plan_does_not_replace_converged_read_notes(self):
        output = self.run_guide("plan")
        self.assertNotIn("replace its notes once reads converge", output)

    def test_plan_keeps_starting_point_note(self):
        output = self.run_guide("plan")
        self.assertIn("add a ticket note as a possible starting point", output)


if __name__ == "__main__":
    unittest.main()
