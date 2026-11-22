import unittest
from pathlib import Path

from chitty.store import guide


class TestColdReadReportGuide(unittest.TestCase):
    def test_report_instructions_name_the_fixed_report(self):
        cold_read = " ".join(guide("cold-read", directory=Path.cwd(), workflow="runner").split())
        for phrase in (
            "What done means",
            "Ambiguities",
            "Missed properties",
            "Unverified behaviour",
            "Wrong claims",
            "the exact wording to change",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, cold_read)


if __name__ == "__main__":
    unittest.main()
