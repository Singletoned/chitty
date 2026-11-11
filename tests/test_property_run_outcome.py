import signal
import unittest

from hypothesis import example, given
from hypothesis import strategies as st

from chitty.run import agent_exit, loop_step, status_outcome


class TestRunOutcomeProperties(unittest.TestCase):
    @given(returncode=st.integers(), timed_out=st.booleans())
    @example(returncode=0, timed_out=False)
    @example(returncode=3, timed_out=False)
    @example(returncode=-signal.SIGINT, timed_out=False)
    @example(returncode=-signal.SIGINT, timed_out=True)
    def test_agent_exit(self, returncode: int, timed_out: bool):
        expected = (
            "timed out"
            if timed_out
            else (
                "interrupted" if returncode == -signal.SIGINT else "failed" if returncode else "ok"
            )
        )
        self.assertEqual(agent_exit(returncode, timed_out), expected)

    @given(old=st.text(), new=st.text())
    @example(old="doing", new="done")
    def test_status_outcome(self, old: str, new: str):
        expected = "unchanged" if old == new else "land" if new == "done" else "changed"
        self.assertEqual(status_outcome(old, new), expected)

    @given(returncode=st.integers())
    @example(returncode=0)
    @example(returncode=3)
    @example(returncode=-signal.SIGINT)
    def test_loop_step(self, returncode: int):
        expected = (
            (True, 0)
            if returncode in (0, 3)
            else (False, returncode if returncode > 0 else 128 - returncode)
        )
        self.assertEqual(loop_step(returncode), expected)


if __name__ == "__main__":
    unittest.main()
