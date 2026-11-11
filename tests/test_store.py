import os
import subprocess
from datetime import date

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import GUIDE_BEGIN, GUIDE_END, Edit, Repo, managed_block
from tests.support import RepoTestCase

TODAY = date(2026, 10, 23)


class StoreTestCase(RepoTestCase):
    def setUp(self):
        super().setUp()
        os.environ["CHITTY_ACTOR"] = "test-agent"
        self.repo = Repo.open(self.root)
        self.tasks = self.repo.context("tasks")
        self.human = self.repo.context("human")

    def add(self, title, context=None, **fields):
        context = context or self.tasks
        return self.repo.add(context, title, "Describe.", [], fields, TODAY).task


class TestStore(StoreTestCase):
    def test_managed_block_reads_marked_and_legacy_files(self):
        marked = f"Before\n{GUIDE_BEGIN}\ncontent\n{GUIDE_END}\nAfter\n"
        self.assertEqual(managed_block(marked), f"{GUIDE_BEGIN}\ncontent\n{GUIDE_END}\n")
        legacy = "Before\n## Chitty\nlegacy\n## Other\nAfter\n"
        self.assertEqual(managed_block(legacy), "## Chitty\nlegacy\n")
        self.assertIsNone(managed_block("Before\n## Other\n"))

    def test_missing_directory_is_empty(self):
        self.assertEqual(self.repo.tasks(self.human, "all"), [])
        self.assertFalse(self.human.directory.exists())

    def test_add_numbers_sequentially_and_names_files(self):
        first = self.add("Add search!")
        second = self.add("日本語")
        self.assertEqual(first.id, TaskId("TASK", 1))
        self.assertEqual(first.path, self.root / "chitty/tasks/TASK-1--add-search.md")
        self.assertEqual(second.path.name, "TASK-2.md")
        self.assertEqual([t.id.number for t in self.repo.tasks(self.tasks, "active")], [1, 2])
        self.assertRegex(
            first.task.section("History") or "",
            r"^- \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z test-agent → todo$",
        )

    def test_delete_mode_requires_git_history_for_new_ids(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        repo = Repo.open(self.root)

        with self.assertRaisesRegex(ChittyError, "git history is unavailable"):
            repo.add(repo.context("tasks"), "One", "Describe.", [], {}, TODAY)

    def test_numbers_count_archived_tasks(self):
        self.add("One")
        self.repo.archive(TaskId("TASK", 1))
        self.assertEqual(self.add("Two").id.number, 2)

    def test_numbers_count_committed_tasks_on_another_branch(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.commit("initial setup", "2026-10-23T00:00:00+00:00")

        worktree = self.tmp / "other-branch"
        self.git("worktree", "add", "--quiet", "-b", "other", str(worktree))
        self.addCleanup(self.remove_worktree, worktree)
        branch_repo = Repo.open(worktree)
        branch_tasks = branch_repo.context("tasks")
        branch_repo.add(branch_tasks, "Archived branch task", "Describe.", [], {}, TODAY)
        branch_repo.archive(TaskId("TASK", 1))
        branch_repo.add(branch_tasks, "Active branch task", "Describe.", [], {}, TODAY)
        self.commit("branch tasks", "2026-10-23T00:00:01+00:00", cwd=worktree)
        self.git("worktree", "remove", "--force", str(worktree))

        main_repo = Repo.open(self.root)
        task = main_repo.add(
            main_repo.context("tasks"), "Main branch task", "Describe.", [], {}, TODAY
        ).task
        self.assertEqual(task.id.number, 3)

    def test_add_checks_dependencies(self):
        with self.assertRaisesRegex(ChittyError, "no task HUMAN-1"):
            self.add("Blocked", depends_on=["HUMAN-1"])
        self.add("Password", context=self.human)
        self.assertEqual(
            self.add("Blocked", depends_on=["HUMAN-1"]).task.frontmatter.depends_on, ["HUMAN-1"]
        )

    def test_reads_newer_task_state_from_another_branch_at_the_same_second(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        stored = self.add("One")
        timestamp = "2026-10-23T00:00:00+00:00"
        self.commit("main task", timestamp)
        worktree = self.tmp / "task-1"
        self.git("worktree", "add", "--quiet", "-b", "task-1", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        path = worktree / stored.path.relative_to(self.root)
        path.write_text(path.read_text().replace("status: todo", "status: doing"))
        self.commit("claim task", timestamp, cwd=worktree)

        task = Repo.open(self.root).find(stored.id)
        self.assertEqual(task.task.frontmatter.status, "doing")
        self.assertEqual(task.branch, "task-1")

        task = Repo.open(worktree).find(stored.id)
        self.assertEqual(task.task.frontmatter.status, "doing")
        self.assertEqual(task.path, path)

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def remove_worktree(self, path):
        if path.exists():
            self.git("worktree", "remove", "--force", str(path))

    def commit(self, message: str, timestamp: str, cwd=None) -> None:
        cwd = cwd or self.root
        environment = {
            **os.environ,
            "GIT_AUTHOR_DATE": timestamp,
            "GIT_COMMITTER_DATE": timestamp,
        }
        subprocess.run(["git", "add", "--all"], cwd=cwd, check=True, env=environment)
        subprocess.run(
            ["git", "commit", "--quiet", "-m", message],
            cwd=cwd,
            check=True,
            env=environment,
        )

    def test_find_and_resolve(self):
        self.add("One")
        self.assertEqual(self.repo.find(self.repo.resolve("1")).task.frontmatter.title, "One")
        with self.assertRaisesRegex(ChittyError, "no task TASK-9"):
            self.repo.find(TaskId("TASK", 9))
        with self.assertRaisesRegex(ChittyError, "prefix 'NOPE'"):
            self.repo.find(TaskId("NOPE", 1))

    def test_description_replacement_records_history(self):
        stored = self.add("One")
        changed = self.repo.edit(stored.id, Edit(replace_in_description=("Describe", "Explain")))
        self.assertIn(
            "test-agent: changed description",
            changed.task.task.section("History") or "",
        )

    def test_save_skips_unchanged(self):
        stored = self.add("One")
        mtime = stored.path.stat().st_mtime_ns
        change = self.repo.edit(stored.id, Edit(status="todo"))
        self.assertEqual(change.paths, ())
        self.assertEqual(stored.path.stat().st_mtime_ns, mtime)
        change = self.repo.edit(stored.id, Edit(status="doing"))
        self.assertEqual(change.paths, (stored.path,))
        timestamp = rf"{date.today().isoformat()}T\d{{2}}:\d{{2}}:\d{{2}}Z"
        self.assertRegex(
            change.task.task.section("History") or "",
            rf"^- {timestamp} test-agent → todo\n- {timestamp} test-agent todo → doing$",
        )
        with self.assertRaisesRegex(ChittyError, "nothing to change"):
            self.repo.edit(stored.id, Edit(add_labels=[]))

    def test_review_must_be_independent_and_can_be_explicitly_overridden(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(plan="Implement it."))
        self.repo.edit(stored.id, Edit(status="review"))

        with self.assertRaisesRegex(
            ChittyError,
            "test-agent cannot review this task: wrote the plan, moved the task to review",
        ):
            self.repo.edit(
                stored.id,
                Edit(status="done", note="Reviewed: looks good\n1: pass - looks good"),
            )

        completed = self.repo.edit(
            stored.id,
            Edit(
                status="done",
                note="Reviewed: emergency approval\n1: pass - looks good",
                override_review_independence=True,
            ),
        ).task
        self.assertIn(
            "test-agent: changed notes; overrode review independence\n",
            completed.task.section("History") or "",
        )

    def test_combined_edit_history_still_marks_review_involvement(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(add_criteria=["Works"]))
        self.repo.edit(stored.id, Edit(plan="Implement it.", check=[1], note="Done."))
        os.environ["CHITTY_ACTOR"] = "worker"
        self.repo.edit(stored.id, Edit(status="review"))
        os.environ["CHITTY_ACTOR"] = "test-agent"

        with self.assertRaisesRegex(
            ChittyError,
            "test-agent cannot review this task: wrote the plan, ticked acceptance criteria$",
        ):
            self.repo.edit(
                stored.id,
                Edit(status="done", note="Reviewed: looks good\n1: pass - looks good"),
            )

    def test_tick_made_during_review_does_not_block_the_reviewers_verdict(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(add_criteria=["Works"]))
        os.environ["CHITTY_ACTOR"] = "author"
        self.repo.edit(stored.id, Edit(status="review"))
        os.environ["CHITTY_ACTOR"] = "reviewer"
        self.repo.edit(stored.id, Edit(check=[1]))

        changed = self.repo.edit(stored.id, Edit(status="doing", note="Review\n1: fail - bad"))
        self.assertEqual(changed.task.task.frontmatter.status, "doing")

    def test_tick_made_during_doing_still_blocks_the_reviewer(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(add_criteria=["Works"]))
        self.repo.edit(stored.id, Edit(status="doing"))
        os.environ["CHITTY_ACTOR"] = "reviewer"
        self.repo.edit(stored.id, Edit(check=[1]))
        os.environ["CHITTY_ACTOR"] = "author"
        self.repo.edit(stored.id, Edit(status="review"))
        os.environ["CHITTY_ACTOR"] = "reviewer"

        with self.assertRaisesRegex(ChittyError, "ticked acceptance criteria"):
            self.repo.edit(
                stored.id,
                Edit(status="done", note="Reviewed: looks good\n1: pass - looks good"),
            )

    def test_plan_written_during_review_still_blocks_the_reviewer(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(add_criteria=["Works"]))
        os.environ["CHITTY_ACTOR"] = "author"
        self.repo.edit(stored.id, Edit(status="review"))
        os.environ["CHITTY_ACTOR"] = "reviewer"
        self.repo.edit(stored.id, Edit(plan="Second thoughts."))

        with self.assertRaisesRegex(ChittyError, "wrote the plan"):
            self.repo.edit(
                stored.id,
                Edit(status="done", note="Reviewed: looks good\n1: pass - looks good"),
            )

    def test_review_criteria_are_immutable_through_repo_edit(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(status="review"))
        original = stored.path.read_text()
        for mutation, message in (
            (Edit(add_criteria=["New"]), "--ac is not allowed"),
            (Edit(rm_criteria=[1]), "--rm-ac is not allowed"),
        ):
            with self.assertRaisesRegex(ChittyError, message):
                self.repo.edit(stored.id, mutation)
            self.assertEqual(stored.path.read_text(), original)

    def test_edit_that_changes_nothing_records_no_history(self):
        stored = self.add("One", priority="high")
        before = stored.path.read_text()

        change = self.repo.edit(stored.id, Edit(priority="high"))

        self.assertEqual(change.paths, ())
        self.assertEqual(stored.path.read_text(), before)

    def test_review_completion_requires_a_review_note(self):
        stored = self.add("One")
        self.repo.edit(stored.id, Edit(status="review"))
        os.environ["CHITTY_ACTOR"] = "reviewer"

        with self.assertRaisesRegex(ChittyError, "requires --note starting 'Reviewed:'"):
            self.repo.edit(stored.id, Edit(status="done"))

        self.repo.edit(
            stored.id,
            Edit(status="done", note="Reviewed: looks good\n1: pass - looks good"),
        )

    def test_status_change_adds_history_to_an_existing_task(self):
        stored = self.add("One")
        stored.path.write_text(stored.task.with_section("History", "").render())

        changed = self.repo.edit(stored.id, Edit(status="doing")).task

        self.assertRegex(
            changed.task.section("History") or "",
            rf"^- {date.today().isoformat()}T\d{{2}}:\d{{2}}:\d{{2}}Z test-agent todo → doing$",
        )

    def test_archive_and_restore(self):
        stored = self.add("One")
        archived = self.repo.archive(stored.id).task
        self.assertEqual(archived.path, self.root / "chitty/tasks/archive/TASK-1--one.md")
        self.assertEqual(self.repo.tasks(self.tasks, "active"), [])
        self.assertEqual(len(self.repo.tasks(self.tasks, "archived")), 1)
        timestamp = rf"{date.today().isoformat()}T\d{{2}}:\d{{2}}:\d{{2}}Z"
        self.assertRegex(
            archived.task.section("History") or "",
            rf"^- {timestamp} test-agent → todo\n- {timestamp} test-agent todo → archived$",
        )
        with self.assertRaisesRegex(ChittyError, "already archived"):
            self.repo.archive(stored.id)
        restored = self.repo.restore(stored.id).task
        self.assertEqual(restored.path, stored.path)
        self.assertIn("archived → todo", restored.task.section("History") or "")

    def test_move_rewrites_references(self):
        self.add("First")
        self.add("Second")
        blocker = self.add("Needs a person")
        dependent = self.add("Blocked", depends_on=[str(blocker.id)])
        dependent_history = dependent.task.section("History")
        self.add("Human thing", context=self.human)
        change = self.repo.move(blocker.id, self.human)
        moved = change.task
        self.assertEqual(moved.id, TaskId("HUMAN", 2))
        self.assertEqual(moved.path.name, "HUMAN-2--needs-a-person.md")
        self.assertEqual(moved.task.frontmatter.moved_from, "TASK-3")
        self.assertFalse(blocker.path.exists())
        rewritten = self.repo.find(dependent.id)
        self.assertEqual(rewritten.task.frontmatter.depends_on, ["HUMAN-2"])
        self.assertEqual(rewritten.task.section("History"), dependent_history)
        self.assertEqual(set(change.paths), {blocker.path, moved.path, dependent.path})

    def test_unexpected_files_are_errors(self):
        self.add("One")
        (self.tasks.directory / "notes.txt").write_text("hi")
        with self.assertRaisesRegex(ChittyError, "notes.txt"):
            self.repo.tasks(self.tasks, "active")

    def test_wrong_prefix_is_an_error(self):
        self.tasks.directory.mkdir(parents=True)
        (self.tasks.directory / "HUMAN-1.md").write_text("x")
        with self.assertRaisesRegex(ChittyError, "does not belong"):
            self.repo.tasks(self.tasks, "active")

    def test_malformed_file_error_names_path(self):
        stored = self.add("One")
        stored.path.write_text("nope\n")
        with self.assertRaisesRegex(ChittyError, "TASK-1--one.md: file must start"):
            self.repo.find(stored.id)
