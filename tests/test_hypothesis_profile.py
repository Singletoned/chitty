import unittest

import hypothesis


class TestHypothesisProfile(unittest.TestCase):
    def test_deadline_is_disabled(self):
        self.assertIsNone(hypothesis.settings().deadline)


if __name__ == "__main__":
    unittest.main()
