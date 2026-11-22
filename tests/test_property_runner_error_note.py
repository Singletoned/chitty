import unittest
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from chitty.commands import code_block
from chitty.run import _runner_error_note


class TestRunnerErrorNoteProperties(unittest.TestCase):
    @given(
        phase=st.sampled_from(("setup", "review preparation", "check", "agent", "landing")),
        parts=st.lists(
            st.one_of(
                st.text(),
                st.sampled_from(
                    ("\n", "\r\n", "\r", "\x85", "\u2028", "```", "Error output:", "Runner error")
                ),
            )
        ),
    )
    def test_note(self, phase: str, parts: list[str]):
        error = "".join(parts)
        worktree = Path("/work/tree")
        lines = error.splitlines() or [""]
        head = f"Runner error ({phase}): {lines[0]}\n\nWorktree: `{worktree}`"
        expected = head
        if any(line.strip() for line in lines[1:]):
            expected += "\n\nError output:\n" + code_block("\n".join(lines[1:]))
        self.assertEqual(_runner_error_note(phase, error, worktree), expected)
