from chitty.check import check, fix
from tests.test_store import StoreTestCase


class TestCheck(StoreTestCase):
    def problems(self, contexts=None, paths=()):
        contexts = self.repo.contexts() if contexts is None else contexts
        return [str(p) for p in check(self.repo, contexts, list(paths))]

    def test_fix_reports_unresolved_problems_without_writing(self):
        stored = self.add("Broken")
        stored.path.write_text("nope\n")

        fixed, problems = fix(self.repo, self.repo.contexts(), [])

        self.assertEqual(fixed, [])
        self.assertEqual(len(problems), 1)
        self.assertEqual(stored.path.read_text(), "nope\n")

    def test_clean_repo(self):
        self.add("One")
        self.assertEqual(self.problems(), [])

    def test_reports_every_problem(self):
        good = self.add("Good")
        blocker = self.add("Blocker", context=self.human)
        dependent = self.add("Blocked", depends_on=[str(blocker.id)])
        broken = self.add("Broken")
        broken.path.write_text("nope\n")
        duplicate = self.tasks.directory / "TASK-1--again.md"
        duplicate.write_text(good.path.read_text())
        blocker.path.unlink()
        (self.tasks.directory / "stray.txt").write_text("")
        problems = "\n".join(self.problems())
        self.assertIn(f"{broken.path}: file must start", problems)
        self.assertIn(f"{duplicate}: TASK-1 is used by more than one file", problems)
        self.assertIn(f"{good.path}: TASK-1 is used by more than one file", problems)
        self.assertIn(f"{duplicate}: filename slug is stale; expected TASK-1--good.md", problems)
        self.assertIn(f"{dependent.path}: depends_on HUMAN-1: no such task", problems)
        self.assertIn("stray.txt: task filename", problems)
        self.assertEqual(len(self.problems()), 6)

    def test_reports_and_repairs_stale_filename_slug(self):
        stored = self.add("Correct title")
        stale_path = stored.path.with_name("TASK-1--stale.md")
        stored.path.rename(stale_path)
        expected_path = stale_path.with_name("TASK-1--correct-title.md")

        self.assertEqual(
            self.problems(),
            [f"{stale_path}: filename slug is stale; expected {expected_path.name}"],
        )

        fixed, problems = fix(self.repo, self.repo.contexts(), [])

        self.assertEqual(problems, [])
        self.assertEqual(
            [problem.message for problem in fixed], [f"renamed to {expected_path.name}"]
        )
        self.assertTrue(expected_path.exists())

    def test_fix_canonicalizes_dependency_ids(self):
        blocker = self.add("Blocker")
        dependent = self.add("Dependent")
        dependent.path.write_text(
            dependent.path.read_text().replace("status", "depends_on: [task-1]\nstatus")
        )

        self.assertIn("must be upper-case", "\n".join(self.problems()))
        fixed, problems = fix(self.repo, self.repo.contexts(), [])

        self.assertEqual(problems, [])
        self.assertEqual(
            [problem.message for problem in fixed], ["rewrote depends_on IDs as upper-case"]
        )
        self.assertIn("depends_on:\n  - TASK-1", dependent.path.read_text())
        self.assertEqual(blocker.id.number, 1)

    def test_self_dependency(self):
        stored = self.add("One")
        stored.path.write_text(
            stored.path.read_text().replace("status", "depends_on: [TASK-1]\nstatus")
        )
        self.assertEqual(self.problems(), [f"{stored.path}: depends_on lists the task itself"])

    def test_reports_each_dependency_cycle_once(self):
        first = self.add("First")
        second = self.add("Second")
        third = self.add("Third")
        for stored, dependency in ((first, second.id), (second, third.id), (third, first.id)):
            stored.path.write_text(
                stored.path.read_text().replace("status", f"depends_on: [{dependency}]\nstatus")
            )

        problems = self.problems()

        self.assertEqual(len(problems), 3)
        for stored in (first, second, third):
            self.assertIn(f"{stored.path}: depends_on cycle: TASK-1, TASK-2, TASK-3", problems)

    def test_scoped_to_context_and_paths(self):
        bad_task = self.add("Bad")
        bad_human = self.add("Bad", context=self.human)
        for stored in (bad_task, bad_human):
            stored.path.write_text("nope\n")
        self.assertEqual(len(self.problems(contexts=[self.human])), 1)
        self.assertEqual(len(self.problems(paths=[bad_task.path])), 1)
        outside = self.root / "README.md"
        outside.write_text("")
        self.assertEqual(
            self.problems(paths=[outside]), [f"{outside}: not a task file in any chitty context"]
        )
