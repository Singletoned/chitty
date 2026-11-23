import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.run import continuation_step


class TestContinuationStep(unittest.TestCase):
    @given(st.lists(st.booleans(), min_size=1), st.integers(min_value=0, max_value=6))
    def test_consecutive_idle_sessions(self, progress, cap):
        trailing = len(progress) - next(
            (index + 1 for index in range(len(progress) - 1, -1, -1) if progress[index]), 0
        )
        self.assertEqual(continuation_step(progress, cap), "stop" if trailing > cap else "continue")
        self.assertEqual(continuation_step([*progress, True], cap), "continue")
