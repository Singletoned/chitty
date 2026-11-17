import os
import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.run import render_command


class TestRenderCommand(unittest.TestCase):
    @given(
        words=st.lists(st.text().filter(lambda word: not word.startswith("~"))),
        mode=st.sampled_from(("work", "review", "repair")),
        ticket_id=st.text(),
        prompt=st.text(),
    )
    def test_replaces_placeholders_in_order(self, words, mode, ticket_id, prompt):
        expected = tuple(
            word.replace("{mode}", mode).replace("{id}", ticket_id).replace("{prompt}", prompt)
            for word in words
        )
        self.assertEqual(render_command(words, mode, ticket_id, prompt), expected)

    def test_expands_only_leading_tilde(self):
        self.assertEqual(
            render_command(("~/x", "a~b"), "work", "TASK-1", ""), (os.path.expanduser("~/x"), "a~b")
        )
