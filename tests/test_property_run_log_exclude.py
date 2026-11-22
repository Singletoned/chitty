import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.commands import RUN_LOG_EXCLUDE, with_exclude_line

LINES = st.one_of(
    st.text(alphabet=st.characters(blacklist_characters="\n")),
    st.sampled_from((RUN_LOG_EXCLUDE, "/.chitty", ".chitty/", "# comment")),
)


class TestRunLogExcludeProperties(unittest.TestCase):
    @given(lines=st.lists(LINES), trailing=st.booleans(), missing=st.booleans())
    def test_exclude_line_is_unique_and_idempotent(self, lines, trailing, missing):
        text = None if missing else "\n".join(lines) + ("\n" if trailing else "")
        result = with_exclude_line(text)
        result_lines = result.split("\n")[:-1]
        source_lines = [] if text is None or text == "" else text.split("\n")
        if source_lines and source_lines[-1] == "":
            source_lines.pop()
        expected = [line for line in source_lines if line != RUN_LOG_EXCLUDE]
        self.assertTrue(result.endswith("\n"))
        self.assertEqual(result_lines.count(RUN_LOG_EXCLUDE), 1)
        self.assertEqual([line for line in result_lines if line != RUN_LOG_EXCLUDE], expected)
        self.assertEqual(with_exclude_line(result), result)


if __name__ == "__main__":
    unittest.main()
