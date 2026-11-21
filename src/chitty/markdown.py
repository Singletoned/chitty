"""CommonMark-aware text transformations."""

from markdown_it import MarkdownIt


def escape_literal_asterisks(text: str) -> str:
    parser = MarkdownIt("commonmark")

    def shape(value: str) -> str:
        return parser.render(value).replace("<em>", "*").replace("</em>", "*")

    while True:
        original = text
        target = shape(text)
        position = 0
        while position < len(text):
            if text[position] == "*":
                candidate = text[:position] + "\\" + text[position:]
                if shape(candidate) == target:
                    text = candidate
                    position += 1
            position += 1
        if text == original:
            return text
