from pathlib import Path
from unittest.mock import patch

from hypothesis import find, given, settings
from hypothesis import strategies as st

from chitty import store
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo, StoredTask
from tests import examples
from tests.support import RepoTestCase
from tests.ticket_placements import (
    PLACEMENTS,
    Expected,
    checkout,
    edit_uncommitted,
    make_repo,
    place,
)


@st.composite
def generated_cases(draw):
    with_errors = draw(st.booleans())
    numbers = draw(st.lists(st.integers(1, 59), min_size=2, max_size=4, unique=True))
    placements = draw(
        st.lists(
            st.sampled_from("abcdeghkm" if with_errors else "abcdgh"),
            min_size=len(numbers),
            max_size=len(numbers),
        )
    )
    return list(zip(numbers, placements))


def generated_mismatches(parent: Path, case) -> list[str]:
    root = make_repo(parent)
    expected = [(number, place(root, placement, number)) for number, placement in case]
    repo = Repo.open(root)
    mismatches = []
    for number, item in expected:
        errors = item.errors or (("no task",) if item.title is None else ())
        try:
            found = repo.find(TaskId("TASK", number))
        except ChittyError as exc:
            if not errors or any(text not in str(exc) for text in errors):
                mismatches.append(f"{number}: unexpected find error {exc}")
        else:
            if errors or (found.task.frontmatter.title, found.archived) != (
                item.title,
                item.archived,
            ):
                mismatches.append(f"{number}: unexpected find result {found}")
    try:
        listed = repo.tasks(repo.context("tasks"), "all")
    except ChittyError as exc:
        if not any(item.errors for _, item in expected):
            mismatches.append(f"unexpected tasks error {exc}")
    else:
        actual = {(t.id.number, t.task.frontmatter.title, t.archived) for t in listed}
        wanted = {(n, item.title, item.archived) for n, item in expected if item.title is not None}
        if any(item.errors for _, item in expected) or actual != wanted:
            mismatches.append(f"tasks {actual!r} != {wanted!r}")
    return mismatches


def placement_mismatches(parent: Path) -> list[str]:
    mismatches: list[str] = []
    for placement in PLACEMENTS:
        for edit in (False, True) if placement not in ("f", "i") else (False,):
            root = make_repo(parent)
            expected = place(root, placement, 5)
            if edit:
                edit_uncommitted(root, 5)
            title = "uncommitted" if edit and placement in ("a", "j") else expected.title
            repo = Repo.open(root)
            task_id = TaskId("TASK", 5)
            prefix = f"{placement} edit={edit}"
            for name, action in (
                ("find", lambda repo=repo, task_id=task_id: repo.find(task_id)),
                ("tasks", lambda repo=repo: repo.tasks(repo.context("tasks"), "all")),
            ):
                errors = (
                    expected.errors
                    if expected.errors
                    else ("no task",)
                    if title is None and name == "find"
                    else ()
                )
                try:
                    result = action()
                except ChittyError as exc:
                    if not errors:
                        mismatches.append(f"{prefix}: {name} raised {exc}")
                    for text in errors:
                        if text not in str(exc):
                            mismatches.append(f"{prefix}: {name} error missing {text!r}: {exc}")
                    continue
                if errors:
                    mismatches.append(f"{prefix}: {name} did not raise ChittyError")
                elif isinstance(result, StoredTask):
                    actual = (result.task.frontmatter.title, result.archived)
                    if actual != (title, expected.archived):
                        mismatches.append(
                            f"{prefix}: find {actual!r} != {(title, expected.archived)!r}"
                        )
                else:
                    actual = [(t.task.frontmatter.title, t.archived) for t in result]
                    wanted = [] if title is None else [(title, expected.archived)]
                    if actual != wanted:
                        mismatches.append(f"{prefix}: tasks {actual!r} != {wanted!r}")
    return mismatches


def own_worktree_mismatches(parent: Path) -> list[str]:
    rows = {
        "b": (Expected("branch"), Expected("uncommitted")),
        "d": (Expected("remote"),),
        "e": (Expected(None, errors=("`origin/task-5`", "`task-5`")),) * 2,
        "g": (Expected("branch", archived=True),),
        "h": (Expected(None),),
        "j": (Expected("main-2"), Expected("main-2")),
        "k": (Expected(None, errors=("`task-5`", "`main`", "changed on both")),) * 2,
        "l": (Expected("remote"), Expected("remote")),
    }
    mismatches: list[str] = []
    for placement, variants in rows.items():
        for edit, expected in enumerate(variants):
            root = make_repo(parent)
            place(root, placement, 5)
            worktree = checkout(root, 2, 5)
            if edit:
                edit_uncommitted(worktree, 5)
            repo = Repo.open(worktree)
            task_id = TaskId("TASK", 5)
            prefix = f"{placement} edit={bool(edit)}"
            for name, action in (
                ("find", lambda repo=repo, task_id=task_id: repo.find(task_id)),
                ("tasks", lambda repo=repo: repo.tasks(repo.context("tasks"), "all")),
            ):
                errors = expected.errors or (
                    ("no task",) if expected.title is None and name == "find" else ()
                )
                try:
                    result = action()
                except ChittyError as exc:
                    if not errors or any(text not in str(exc) for text in errors):
                        mismatches.append(f"{prefix}: {name} unexpected error: {exc}")
                    continue
                if errors:
                    mismatches.append(f"{prefix}: {name} did not raise {errors!r}")
                    continue
                tasks = [result] if isinstance(result, StoredTask) else result
                actual = [(task.task.frontmatter.title, task.archived) for task in tasks]
                wanted = [] if expected.title is None else [(expected.title, expected.archived)]
                if actual != wanted:
                    mismatches.append(f"{prefix}: {name} {actual!r} != {wanted!r}")
    return mismatches


class TestTicketPlacementReads(RepoTestCase):
    @settings(max_examples=examples(30), deadline=None)
    @given(case=generated_cases())
    def test_generated_placements(self, case):
        self.assertEqual(generated_mismatches(self.tmp, case), [])

    def test_generated_mutant_swapped_contains(self):
        real = store.ticket_source

        def mutant(*args):
            args = list(args)
            contains = args[7]
            args[7] = lambda a, b: contains(b, a)
            return real(*args)

        with patch("chitty.store.ticket_source", mutant):
            find(
                generated_cases(),
                lambda case: bool(generated_mismatches(self.tmp, case)),
                settings=settings(max_examples=100, deadline=None, database=None),
            )

    def test_own_worktree_placements(self):
        self.assertEqual(own_worktree_mismatches(self.tmp), [])

    def test_own_worktree_mutant_main_branch(self):
        real = store.ticket_source

        def mutant(*args):
            args = list(args)
            args[2] = "main"
            return real(*args)

        with patch("chitty.store.ticket_source", mutant):
            self.assertTrue(own_worktree_mismatches(self.tmp))

    def test_main_checkout_placements(self):
        self.assertEqual(placement_mismatches(self.tmp), [])

    def test_mutant_swapped_contains(self):
        real = store.ticket_source

        def mutant(*args):
            args = list(args)
            contains = args[7]
            args[7] = lambda a, b: contains(b, a)
            return real(*args)

        with patch("chitty.store.ticket_source", mutant):
            self.assertTrue(placement_mismatches(self.tmp))

    def test_mutant_no_main_tip(self):
        real = store.ticket_source

        def mutant(*args):
            args = list(args)
            args[4] = None
            return real(*args)

        with patch("chitty.store.ticket_source", mutant):
            self.assertTrue(placement_mismatches(self.tmp))

    def test_linked_worktree_placements(self):
        for kind in (3, 4, 5):
            for placement in PLACEMENTS:
                for edit in ("none", "linked", "main"):
                    if edit == "main" and placement != "a":
                        continue
                    with self.subTest(kind=kind, placement=placement, edit=edit):
                        root = make_repo(self.tmp)
                        expected = place(root, placement, 5)
                        linked = checkout(root, kind, 5)
                        if placement == "i":
                            expected = Expected(None)
                        if edit == "linked":
                            if not (linked / "chitty/tasks/TASK-5--example.md").exists():
                                continue
                            edit_uncommitted(linked, 5)
                        elif edit == "main":
                            edit_uncommitted(root, 5)
                        repo = Repo.open(linked)
                        task_id = TaskId("TASK", 5)
                        if expected.errors:
                            for action in (
                                lambda repo=repo, task_id=task_id: repo.find(task_id),
                                lambda repo=repo: repo.tasks(repo.context("tasks"), "all"),
                            ):
                                with self.assertRaises(ChittyError) as caught:
                                    action()
                                for text in expected.errors:
                                    self.assertIn(text, str(caught.exception))
                        elif expected.title is None:
                            with self.assertRaisesRegex(ChittyError, "no task"):
                                repo.find(task_id)
                            self.assertEqual(
                                [
                                    t
                                    for t in repo.tasks(repo.context("tasks"), "all")
                                    if t.id == task_id
                                ],
                                [],
                            )
                        else:
                            found = repo.find(task_id)
                            listed = [
                                t
                                for t in repo.tasks(repo.context("tasks"), "all")
                                if t.id == task_id
                            ]
                            self.assertEqual(
                                (found.task.frontmatter.title, found.archived),
                                (expected.title, expected.archived),
                            )
                            self.assertEqual(
                                [(t.task.frontmatter.title, t.archived) for t in listed],
                                [(expected.title, expected.archived)],
                            )
