import unittest

from chitty.store import guide


class TestColdReadMutantGuide(unittest.TestCase):
    def test_mutant_procedure_is_removed(self):
        cold_read = " ".join(guide("cold-read").split())
        self.assertNotIn("mutant", cold_read)
        self.assertNotIn("refs/cold-read", cold_read)


if __name__ == "__main__":
    unittest.main()
