import unittest

from chitty.store import guide


class TestColdReadReportGuide(unittest.TestCase):
    def test_report_instructions_filter_findings_and_capture_test_evidence(self):
        cold_read = " ".join(guide("cold-read").split())
        for phrase in (
            "Put failing test output in your report, never in a ticket note",
            "keep every scratch file there and delete it before running the check",
            "change what a worker builds or how a reviewer verifies it",
            "listed in one line without asking for a ticket change",
            "quote the test runner's own summary line, not an exit status",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, cold_read)


if __name__ == "__main__":
    unittest.main()
