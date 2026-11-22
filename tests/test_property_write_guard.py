import unittest
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from chitty.write_guard import write_refusal


class TestWriteRefusal(unittest.TestCase):
    @given(
        n=st.integers(min_value=1),
        m=st.integers(min_value=1),
        main=st.sampled_from(["main", "master", "trunk"]),
        sha=st.text(alphabet="0123456789abcdef", min_size=40, max_size=40),
        case=st.integers(min_value=0, max_value=2),
        remote=st.sampled_from(["origin", "upstream"]),
        work_parts=st.lists(st.text(alphabet="abc", min_size=1), min_size=1, max_size=3),
        main_parts=st.lists(st.text(alphabet="xyz", min_size=1), min_size=1, max_size=3),
        has_worktree=st.booleans(),
        checkout_is_main=st.booleans(),
        local_behind=st.booleans(),
        main_local=st.booleans(),
    )
    def test_property(
        self,
        n,
        m,
        main,
        sha,
        case,
        remote,
        work_parts,
        main_parts,
        has_worktree,
        checkout_is_main,
        local_behind,
        main_local,
    ):
        task = f"TASK-{n}"
        ref = [main, f"task-{m}", f"{remote}/task-{m}"][case]
        local = main_local if case == 0 else case == 1
        worktree = Path(*work_parts) if has_worktree else None
        checkout = Path(*main_parts)
        if ref == main:
            action = (
                f"switch this checkout to {main} first"
                if checkout_is_main
                else f"edit it in the main checkout {checkout}"
            )
        elif local:
            action = (
                f"edit it in worktree {worktree}"
                if worktree is not None
                else f"run git switch {ref} first"
            )
        else:
            branch = ref.split("/", 1)[1]
            action = (
                f"fast-forward {branch} to {ref} first"
                if local_behind
                else f"run git switch --track {ref} first"
            )
        self.assertEqual(
            write_refusal(
                task, ref, sha, main, local, worktree, checkout, checkout_is_main, local_behind
            ),
            f"{task} has a newer copy on {ref} ({sha[:10]}); {action}",
        )

    def test_examples(self):
        sha = "0123456789abcdef0123456789abcdef01234567"
        examples = [
            (
                "main",
                True,
                None,
                True,
                False,
                "TASK-1 has a newer copy on main (0123456789); switch this checkout to main first",
            ),
            (
                "main",
                False,
                None,
                False,
                False,
                "TASK-1 has a newer copy on main (0123456789); edit it in the main checkout /repo",
            ),
            (
                "task-2",
                True,
                Path("/work"),
                False,
                False,
                "TASK-1 has a newer copy on task-2 (0123456789); edit it in worktree /work",
            ),
            (
                "task-2",
                True,
                None,
                False,
                False,
                "TASK-1 has a newer copy on task-2 (0123456789); run git switch task-2 first",
            ),
            (
                "origin/task-2",
                False,
                None,
                False,
                True,
                (
                    "TASK-1 has a newer copy on origin/task-2 (0123456789); "
                    "fast-forward task-2 to origin/task-2 first"
                ),
            ),
            (
                "origin/task-2",
                False,
                None,
                False,
                False,
                (
                    "TASK-1 has a newer copy on origin/task-2 (0123456789); "
                    "run git switch --track origin/task-2 first"
                ),
            ),
        ]
        for ref, local, worktree, is_main, behind, expected in examples:
            with self.subTest(ref=ref, expected=expected):
                self.assertEqual(
                    write_refusal(
                        "TASK-1", ref, sha, "main", local, worktree, Path("/repo"), is_main, behind
                    ),
                    expected,
                )
