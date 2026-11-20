import string
import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.config import CONTEXT_NAME_RE, RESERVED_CONTEXT_NAMES
from chitty.run import _only_ticket_paths


@st.composite
def context_names(draw):
    names = draw(
        st.lists(
            st.from_regex(CONTEXT_NAME_RE, fullmatch=True).filter(
                lambda name: name not in RESERVED_CONTEXT_NAMES
            ),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )
    return names


@st.composite
def paths_and_contexts(draw, contexts):
    segment = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5)
    rest = draw(st.lists(segment, min_size=1, max_size=3).map(lambda parts: "/".join(parts)))
    is_ticket = draw(st.booleans())
    if is_ticket:
        name = draw(st.sampled_from(contexts))
        archive = draw(st.booleans())
        path = f"chitty/{name}/{'archive/' if archive else ''}{rest}"
    else:
        shape = draw(st.integers(min_value=0, max_value=6))
        name = draw(st.sampled_from(contexts))
        if shape == 0:
            path = f"chitty/{name}"
        elif shape == 1:
            path = f"chitty/{name}.d/{rest}"
        elif shape == 2:
            path = f"x/chitty/{name}/{rest}"
        elif shape == 3:
            path = f"chitty/archive/{rest}"
        elif shape == 4:
            path = "chitty.toml"
        elif shape == 5:
            path = f"src/{rest}"
        else:
            other = draw(
                st.one_of(
                    st.from_regex(CONTEXT_NAME_RE, fullmatch=True),
                    st.sampled_from(contexts).map(lambda item: item + "x"),
                ).filter(lambda item: item not in contexts and item != "archive")
            )
            path = f"chitty/{other}/{rest}"
    return path, is_ticket


class TestOnlyTicketPaths(unittest.TestCase):
    def test_context_directory_requires_path_boundary(self):
        self.assertFalse(_only_ticket_paths(["chitty/tasks-extra/item.md"], ["tasks"]))
        self.assertFalse(_only_ticket_paths(["chitty/archive/item.md"], ["tasks"]))

    @given(context_names(), st.data())
    def test_property(self, contexts, data):
        generated = data.draw(st.lists(paths_and_contexts(contexts), min_size=0, max_size=20))
        paths = [path for path, _ in generated]
        expected = all(is_ticket for _, is_ticket in generated)
        self.assertEqual(_only_ticket_paths(paths, contexts), expected)
        self.assertEqual(_only_ticket_paths(list(reversed(paths)), contexts), expected)


if __name__ == "__main__":
    unittest.main()
