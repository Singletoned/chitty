from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from tests.support import RepoTestCase
from tests.ticket_placements import PLACEMENTS, edit_uncommitted, make_repo, place


class TestTicketPlacementReads(RepoTestCase):
    def test_main_checkout_placements(self):
        for placement in PLACEMENTS:
            for edit in (False, True) if placement not in ("f", "i") else (False,):
                with self.subTest(placement=placement, edit=edit):
                    root = make_repo(self.tmp)
                    expected = place(root, placement, 5)
                    if edit:
                        edit_uncommitted(root, 5)
                    title = "uncommitted" if edit and placement in ("a", "j") else expected.title
                    repo = Repo.open(root)
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
                    elif title is None:
                        with self.assertRaisesRegex(ChittyError, "no task"):
                            repo.find(task_id)
                        self.assertEqual(repo.tasks(repo.context("tasks"), "all"), [])
                    else:
                        found = repo.find(task_id)
                        listed = repo.tasks(repo.context("tasks"), "all")
                        self.assertEqual(
                            (found.task.frontmatter.title, found.archived),
                            (title, expected.archived),
                        )
                        self.assertEqual(
                            [(t.task.frontmatter.title, t.archived) for t in listed],
                            [(title, expected.archived)],
                        )
