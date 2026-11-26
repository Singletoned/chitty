import os
import shutil
from datetime import date

from hypothesis import given, settings
from hypothesis import strategies as st

import chitty.check as check_module
from chitty.check import check, errors
from chitty.model import STATUSES, parse
from chitty.store import Repo
from tests import examples
from tests.support import RepoTestCase


class TestTicketSizeWarnings(RepoTestCase):
    @settings(max_examples=examples(100))
    @given(
        entries=st.lists(
            st.one_of(
                st.tuples(
                    st.just("transition"), st.sampled_from(["cold-read", "planning", "todo"])
                ),
                st.tuples(
                    st.just("event"),
                    st.sampled_from(
                        [
                            "changed title",
                            "changed title, description",
                            "changed description, notes",
                            "replaced notes",
                            "replaced notes; changed title, labels",
                        ]
                    ),
                ),
            )
        )
    )
    def test_cold_reads_since_retitle(self, entries):
        lines = []
        expected = 0
        for kind, value in entries:
            if kind == "transition":
                lines.append(f"- 2026-01-01T00:00:00Z a planning → {value}")
                expected += value == "cold-read"
            else:
                lines.append(f"- 2026-01-01T00:00:00Z a: {value}")
                if value in {
                    "changed title",
                    "changed title, description",
                    "replaced notes; changed title, labels",
                }:
                    expected = 0
        self.assertEqual(check_module.cold_reads_since_retitle("\n".join(lines)), expected)

    def test_retitle_resets_warning(self):
        os.environ["CHITTY_ACTOR"] = "test-agent"
        repo = Repo.open(self.root)
        context = repo.context("tasks")
        path = repo.add(
            context, "Ticket", "description", [], {"status": "planning"}, date(2026, 1, 1)
        ).task.path
        task = parse(path.read_text())
        transition = "- 2026-01-01T00:00:00Z a planning → cold-read"
        event = "- 2026-01-01T00:00:00Z a: changed title, description"
        for retitled in (False, True):
            lines = [transition] * 3 + ([event] if retitled else []) + [transition]
            path.write_text(task.with_section("History", "\n".join(lines)).render())
            warnings = [
                p
                for p in check(repo, repo.contexts(), [])
                if p.path == path and "cold reads;" in p.message
            ]
            self.assertEqual(bool(warnings), not retitled)

    @settings(max_examples=examples(100), deadline=None)
    @given(
        status=st.sampled_from(STATUSES),
        description_words=st.sampled_from([1, 2, 250, 499, 500, 501]),
        criterion_words=st.sampled_from([0, 1, 2, 250, 500, 501]),
        notes_words=st.sampled_from([0, 1, 199, 200, 201]),
        history=st.lists(st.sampled_from(["cold-read", "planning", "todo"]), max_size=5),
        archived=st.booleans(),
    )
    def test_limits(
        self, status, description_words, criterion_words, notes_words, history, archived
    ):
        os.environ["CHITTY_ACTOR"] = "test-agent"
        for directory in (self.root / "chitty").glob("*"):
            if directory.is_dir():
                shutil.rmtree(directory)
            else:
                directory.unlink()
        repo = Repo.open(self.root)
        context = repo.context("tasks")
        criteria = ["word " * criterion_words] if criterion_words else []
        path = repo.add(
            context,
            "Ticket",
            "word " * description_words,
            criteria,
            {"status": "review" if status == "done" else status},
            date(2026, 1, 1),
        ).task.path
        task = parse(path.read_text())
        if status == "done":
            task = task.with_field("status", "done")
        if notes_words:
            task = task.with_section("Notes", "word " * notes_words)
        history_text = "\n".join(f"- 2026-01-01 → {new}" for new in history)
        task = task.with_section("History", history_text)
        path.write_text(task.render())
        if archived:
            target = context.archive_directory / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(target)
            path = target

        problems = check(repo, repo.contexts(), [])
        warnings = [problem for problem in problems if problem.path == path]
        spec = [p for p in warnings if "specification has" in p.message]
        notes = [p for p in warnings if "notes have" in p.message]
        reads = [p for p in warnings if "cold reads;" in p.message]
        self.assertEqual(
            bool(spec),
            status in {"to-plan", "planning", "cold-read", "todo"}
            and description_words + criterion_words > 500,
        )
        self.assertEqual(bool(notes), status == "todo" and notes_words > 200)
        self.assertEqual(
            bool(reads),
            status in {"to-plan", "planning", "cold-read", "todo"}
            and history.count("cold-read") > 2,
        )
        for group in (spec, notes, reads):
            self.assertLessEqual(len(group), 1)
            self.assertTrue(all(p.severity == "warning" for p in group))
            self.assertEqual(errors(group), [])
        if spec:
            self.assertIn("simplify or split", spec[0].message)
        if notes:
            self.assertIn("--set-notes ''", notes[0].message)
        if reads:
            self.assertIn("simplify or split", reads[0].message)
