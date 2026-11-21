import unittest

from hypothesis import given
from hypothesis import strategies as st
from markdown_it import MarkdownIt

from chitty.markdown import escape_literal_asterisks
from tests.test_formatters import run_formatter

PARSER = MarkdownIt("commonmark")
ALPHABET = "*_\\`/.<>[]()!#- \t\n1abé"


def shape(text: str) -> str:
    return PARSER.render(text).replace("<em>", "*").replace("</em>", "*")


class TestMarkdownEscape(unittest.TestCase):
    @given(st.text(alphabet=ALPHABET))
    def test_shape_and_idempotence(self, text: str) -> None:
        escaped = escape_literal_asterisks(text)
        self.assertEqual(shape(escaped), shape(text))
        self.assertEqual(escape_literal_asterisks(escaped), escaped)

    @given(st.text(alphabet=ALPHABET.replace("_", "")))
    def test_no_emphasis_without_underscores(self, text: str) -> None:
        self.assertNotIn("<em>", PARSER.render(escape_literal_asterisks(text)))

    def test_examples(self) -> None:
        examples = {
            "files/*.jpg and c/*.png": r"files/\*.jpg and c/\*.png",
            "x `a*b` <http://x/*>": "x `a*b` <http://x/*>",
            "**bold** and *em*": r"**bold** and \*em\*",
            "**_*_": r"\*\*_\*_",
            r"a\*b": r"a\*b",
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(escape_literal_asterisks(text), expected)

    def test_prettier(self) -> None:
        for text in ("files/*.jpg and c/*.png", "a * b and c `*` d", r"a \* b and c * d"):
            with self.subTest(text=text):
                escaped = escape_literal_asterisks(text) + "\n"
                self.assertEqual(run_formatter("prettier", escaped), escaped)
