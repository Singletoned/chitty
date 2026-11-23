from pathlib import Path
from unittest import TestCase

from hypothesis import given
from hypothesis import strategies as st

from chitty.run import display_path

segment = st.text(
    alphabet=st.characters(whitelist_categories=("L",), whitelist_characters=" "), min_size=1
)
segments = st.lists(segment, max_size=3)


class TestDisplayPath(TestCase):
    @given(st.lists(segment, min_size=1, max_size=3), segments)
    def test_paths(self, root_parts, parts):
        root = Path("/").joinpath(*root_parts)
        inside = root.joinpath(*parts)
        result = display_path(inside, root)
        self.assertEqual(root / result, inside)
        self.assertEqual(result, str(inside.relative_to(root)))
        outside = [
            root.with_name(root.name + "-x").joinpath(*parts),
            Path("/" + root_parts[0] + "-x").joinpath(*parts),
            root.parent / "z" / ".." / root.name / "seg",
        ]
        for path in outside:
            self.assertEqual(display_path(path, root), str(path))
