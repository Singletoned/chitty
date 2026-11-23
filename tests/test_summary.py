import random
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from click.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st

import chitty.model
from chitty.cli import cli
from chitty.ids import TaskId
from chitty.model import STATUSES
from chitty.store import StoredTask, SummaryLine, summary_sections
from tests import examples
from tests.support import RepoTestCase

NOW = datetime(2026, 11, 22, 12, 0, tzinfo=UTC)
WINDOW_HOURS = 72
FUTURE_HOURS = 1


def stamp(when: datetime) -> str:
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def ticket_text(title: str, history: list[str]) -> str:
    lines = "\n".join(history)
    return f"---\ntitle: {title}\nstatus: todo\npriority: medium\ncreated: 2026-11-01\n---\n\n## Description\n\nText.\n\n## History\n\n{lines}\n"


def line(when: datetime, old: str | None, new: str, actor: str = "tester") -> str:
    move = f"{old} → {new}" if old else f"→ {new}"
    return f"- {stamp(when)} {actor} {move}"


def stored(number: int, history: list[str], title: str = "Title") -> StoredTask:
    task = chitty.model.parse(ticket_text(title, history))
    return StoredTask(TaskId("TASK", number), "tasks", Path("chitty/tasks/x.md"), False, task)


def hours_ago(hours: float) -> datetime:
    return NOW - timedelta(hours=hours)


class TestTimedTransitions(unittest.TestCase):
    def test_skips_date_only_and_event_lines(self):
        task = chitty.model.parse(
            ticket_text(
                "T",
                [
                    "- 2026-11-20 → todo",
                    line(hours_ago(3), "todo", "doing"),
                    f"- {stamp(hours_ago(2))} tester: changed notes",
                    line(hours_ago(1), "doing", "review"),
                ],
            )
        )
        self.assertEqual(
            task.timed_transitions(),
            [(hours_ago(3), "todo", "doing"), (hours_ago(1), "doing", "review")],
        )


class TestSummarySections(unittest.TestCase):
    def test_full_path_appears_only_under_done(self):
        task = stored(
            1,
            [
                line(hours_ago(4), "todo", "doing"),
                line(hours_ago(3), "doing", "review"),
                line(hours_ago(2), "review", "done"),
            ],
        )
        self.assertEqual(
            summary_sections([task], NOW, 24),
            [("done", [SummaryLine(TaskId("TASK", 1), "Title", hours_ago(2), "tester", False)])],
        )

    def test_window_boundary(self):
        task = stored(1, [line(hours_ago(25), "todo", "doing")])
        self.assertEqual(summary_sections([task], NOW, 24), [])
        self.assertEqual(
            summary_sections([task], NOW, 48),
            [("doing", [SummaryLine(TaskId("TASK", 1), "Title", hours_ago(25), "tester", False)])],
        )

    def test_new_only_when_created_in_window(self):
        created = stored(1, [line(hours_ago(2), None, "todo")])
        older = stored(2, [line(hours_ago(30), None, "todo"), line(hours_ago(1), "todo", "doing")])
        sections = dict(summary_sections([created, older], NOW, 24))
        self.assertTrue(sections["todo"][0].new)
        self.assertFalse(sections["doing"][0].new)

    def test_section_ordering_newest_first_then_id(self):
        tasks = [
            stored(10, [line(hours_ago(1), "todo", "doing")]),
            stored(9, [line(hours_ago(1), "todo", "doing")]),
            stored(3, [line(hours_ago(5), "todo", "doing")]),
            stored(4, [line(hours_ago(0.5), "todo", "doing")]),
        ]
        [(status, lines)] = summary_sections(tasks, NOW, 24)
        self.assertEqual(status, "doing")
        self.assertEqual(
            [str(item.id) for item in lines], ["TASK-4", "TASK-9", "TASK-10", "TASK-3"]
        )

    def test_date_only_line_contributes_nothing(self):
        self.assertEqual(summary_sections([stored(1, ["- 2026-11-22 → todo"])], NOW, 24), [])

    def test_unknown_status_sorts_after_statuses(self):
        tasks = [
            stored(1, [line(hours_ago(1), "todo", "zzz")]),
            stored(2, [line(hours_ago(1), "doing", "done")]),
            stored(3, [line(hours_ago(1), "todo", "backlog")]),
        ]
        self.assertEqual(
            [status for status, _ in summary_sections(tasks, NOW, 24)],
            ["done", "backlog", "zzz"],
        )

    def test_future_transition_left_out(self):
        task = stored(
            1,
            [
                line(hours_ago(2), "todo", "doing"),
                line(NOW + timedelta(minutes=1), "doing", "review"),
            ],
        )
        self.assertEqual([status for status, _ in summary_sections([task], NOW, 24)], ["doing"])

    def test_event_line_ignored(self):
        task = stored(
            1,
            [
                line(hours_ago(2), "todo", "doing"),
                f"- {stamp(hours_ago(1.5))} tester: changed notes",
                line(hours_ago(1), "doing", "review"),
            ],
        )
        self.assertEqual([status for status, _ in summary_sections([task], NOW, 24)], ["review"])

    def test_nothing_in_window(self):
        self.assertEqual(
            summary_sections([stored(1, [line(hours_ago(30), None, "todo")])], NOW, 24), []
        )


TIMES = st.integers(-WINDOW_HOURS * 3600, FUTURE_HOURS * 3600).map(
    lambda s: NOW + timedelta(seconds=s)
)


@st.composite
def drawn_ticket(draw, number: int, start: datetime):
    count = draw(st.integers(1, 5))
    times = sorted(draw(st.lists(st.one_of(TIMES, st.just(start)), min_size=count, max_size=count)))
    old = draw(st.one_of(st.none(), st.sampled_from(STATUSES)))
    transitions = []
    for when in times:
        new = draw(st.sampled_from(STATUSES))
        transitions.append((when, old, new))
        old = new
    return number, transitions


@st.composite
def scenario(draw):
    hours = draw(st.integers(1, WINDOW_HOURS))
    start = NOW - timedelta(hours=hours)
    count = draw(st.integers(1, 6))
    tickets = [draw(drawn_ticket(number, start)) for number in range(1, count + 1)]
    seed = draw(st.integers(0, 2**32 - 1))
    return hours, tickets, seed


class TestSummaryProperty(unittest.TestCase):
    @settings(max_examples=examples(50))
    @given(scenario())
    def test_latest_eligible_transition_per_ticket(self, drawn):
        hours, tickets, seed = drawn
        start = NOW - timedelta(hours=hours)
        tasks = [stored(n, [line(w, o, s) for w, o, s in ts]) for n, ts in tickets]
        random.Random(seed).shuffle(tasks)
        sections = summary_sections(tasks, NOW, hours)
        placed = {item.id: (status, item) for status, items in sections for item in items}
        self.assertEqual(sum(len(items) for _, items in sections), len(placed))
        for _, items in sections:
            whens = [item.when for item in items]
            self.assertEqual(whens, sorted(whens, reverse=True))
        for number, transitions in tickets:
            task_id = TaskId("TASK", number)
            eligible = [t for t in transitions if start <= t[0] <= NOW]
            if not eligible:
                self.assertNotIn(task_id, placed)
                continue
            # Times are sorted ascending, so the last eligible is latest, later line on a tie.
            when, _, new = eligible[-1]
            status, item = placed[task_id]
            self.assertEqual((status, item.when, item.actor), (new, when, "tester"))
            first_when, first_old, _ = transitions[0]
            self.assertEqual(item.new, first_old is None and start <= first_when <= NOW)


class TestSummaryCommand(RepoTestCase):
    def write(self, name: str, title: str, history: list[str]) -> None:
        directory = self.root / "chitty" / "tasks"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(ticket_text(title, history))

    def invoke(self, *args: str):
        env = {"CHITTY_ROOT": str(self.root), "CHITTY_ACTOR": "test"}
        return CliRunner().invoke(cli, ["summary", *args], env=env)

    def test_output(self):
        now = datetime.now(UTC).replace(microsecond=0)
        one_created, one_done = now - timedelta(hours=2), now - timedelta(hours=1)
        two_created, three_created = now - timedelta(hours=10), now - timedelta(hours=30)
        self.write(
            "TASK-1--one.md",
            "One",
            [line(one_created, None, "todo"), line(one_done, "todo", "done")],
        )
        self.write("TASK-2--two.md", "Two", [line(two_created, None, "todo")])
        self.write("TASK-3--three.md", "Three", [line(three_created, None, "todo")])

        def hm(when: datetime) -> str:
            return when.strftime("%H:%M")

        result = self.invoke()
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            result.output,
            f"done (1)\n  TASK-1  One (new)  {hm(one_done)} tester\n\n"
            f"todo (1)\n  TASK-2  Two (new)  {hm(two_created)} tester\n",
        )
        result = self.invoke("--hours", "48")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            result.output,
            f"done (1)\n  TASK-1  One (new)  {hm(one_done)} tester\n\n"
            f"todo (2)\n  TASK-2  Two (new)  {hm(two_created)} tester\n"
            f"  TASK-3  Three (new)  {hm(three_created)} tester\n",
        )

    def test_nothing_changed(self):
        result = self.invoke("--hours", "1")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "nothing changed in the last 1 hours\n")

    def test_invalid_hours(self):
        self.assertEqual(self.invoke("--hours", "0").exit_code, 2)
        self.assertEqual(self.invoke("--hours", "x").exit_code, 2)
