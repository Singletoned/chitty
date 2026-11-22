import unicodedata
import unittest

from chitty.cli import _columns
from chitty.model import PRIORITY_GLYPHS, STATUS_GLYPHS
from chitty.selection import (
    BLOCKER_GLYPH,
    BROKEN_DEPENDENCY_GLYPH,
    DEPENDENCY_GLYPH,
    HUMAN_GLYPH,
    RUNNING_GLYPH,
    UNTESTABLE_GLYPH,
)
from tests.test_cli import CliTestCase


class TestListGlyphs(unittest.TestCase):
    def test_glyphs_are_single_wide_characters(self):
        for glyph in (
            *STATUS_GLYPHS.values(),
            *PRIORITY_GLYPHS.values(),
            BLOCKER_GLYPH,
            BROKEN_DEPENDENCY_GLYPH,
            DEPENDENCY_GLYPH,
            HUMAN_GLYPH,
            RUNNING_GLYPH,
            UNTESTABLE_GLYPH,
        ):
            if glyph:
                with self.subTest(glyph=glyph):
                    self.assertEqual(len(glyph), 1)
                    self.assertNotIn("\ufe0f", glyph)
                    self.assertEqual(unicodedata.east_asian_width(glyph), "W")


class TestListAlignment(CliTestCase):
    def test_priority_and_unset_titles_align(self):
        self.run_cli("add", "High title", "-d", "x", "-p", "high")
        self.run_cli("add", "Unset title", "-d", "x")
        lines = self.run_cli("list").stdout.splitlines()
        offsets = [
            _columns(line[: line.index(title)])
            for line, title in zip(lines, ("High title", "Unset title"))
        ]
        self.assertEqual(offsets[0], offsets[1])
