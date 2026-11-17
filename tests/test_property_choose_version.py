import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import cast

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.store import StoredTask, Version, choose_version


@st.composite
def versions(draw):
    local = draw(st.booleans())
    branch = draw(st.sampled_from((None, "main", "alpha", "beta")))
    committed_at = None if local else draw(st.integers(0, 5))
    stored = cast(
        StoredTask,
        SimpleNamespace(
            id="TASK-1",
            path=Path(f"{branch}-{local}-{committed_at}-{draw(st.booleans())}"),
            archived=False,
        ),
    )
    return Version(stored, local, local and draw(st.booleans()), branch, committed_at)


class TestChooseVersion(unittest.TestCase):
    @given(
        st.lists(versions(), min_size=1, max_size=12).filter(
            lambda vs: sum(v.local for v in vs) <= 1
        )
    )
    def test_returns_input_and_order_does_not_matter(self, versions_list):
        picked = choose_version(versions_list, "main")
        self.assertIn(picked, versions_list)
        self.assertEqual(picked, choose_version(list(reversed(versions_list)), "main"))

    @given(st.booleans())
    def test_dirty_local_wins_in_either_location(self, archived):
        dirty = Version(
            cast(StoredTask, SimpleNamespace(id="TASK-1", path=Path("dirty"), archived=archived)),
            True,
            True,
            None,
            None,
        )
        history = Version(
            cast(
                StoredTask,
                SimpleNamespace(id="TASK-1", path=Path("history"), archived=not archived),
            ),
            False,
            False,
            "main",
            99,
        )
        self.assertEqual(choose_version([history, dirty], "main"), dirty)

    def test_two_local_versions_raise(self):
        versions_list = [
            Version(
                cast(StoredTask, SimpleNamespace(id="TASK-1", path=Path(str(i)), archived=bool(i))),
                True,
                False,
                None,
                None,
            )
            for i in range(2)
        ]
        with self.assertRaisesRegex(ChittyError, "used by more than one file"):
            choose_version(versions_list, "main")

    @given(
        st.lists(versions(), min_size=1, max_size=10).filter(
            lambda vs: sum(v.local for v in vs) <= 1 and any(not v.local for v in vs)
        )
    )
    def test_adding_older_history_does_not_change_choice(self, versions_list):
        base = choose_version(versions_list, "main")
        oldest = min((v.committed_at for v in versions_list if not v.local), default=0) - 1
        old = Version(
            cast(StoredTask, SimpleNamespace(id="TASK-1", path=Path("older"), archived=False)),
            False,
            False,
            "older",
            oldest,
        )
        self.assertEqual(base, choose_version([*versions_list, old], "main"))
