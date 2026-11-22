from pathlib import Path
from unittest.mock import patch

from chitty import store
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo, StoredTask
from tests.support import RepoTestCase
from tests.ticket_placements import (
    PLACEMENTS,
    Expected,
    checkout,
    edit_uncommitted,
    make_repo,
    place,
)


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


class TestTicketPlacementReads(RepoTestCase):
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
