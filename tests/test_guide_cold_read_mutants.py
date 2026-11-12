import unittest

from chitty.store import guide


class TestColdReadMutantGuide(unittest.TestCase):
    def test_mutants_are_applied_individually_and_reported(self):
        cold_read = " ".join(guide("cold-read").split())
        self.assertIn("apply each mutant alone", cold_read)
        self.assertIn("restore it before the next", cold_read)
        self.assertIn("criterion wording that would catch it", cold_read)
        self.assertIn("Surviving mutants, each with criterion wording", cold_read)


if __name__ == "__main__":
    unittest.main()
