---
title: Add `chitty summary` to show what changed in recent hours
status: cold-read
priority: high
created: 2026-11-22
---

## Description

Requested by the person on 2026-11-21: "chitty needs a summary feature, where I can see what has happened in the last few hours", and again on 2026-11-22.

Today, answering "what happened since this morning?" means piecing together `git log` on `main`, each ticket's `## History` lines, runner output and notes. The data is already there: every status change is a timestamped History line naming the actor (`HISTORY_LINE_RE` in `src/chitty/model.py`, for example `- 2026-11-22T22:16:03Z zesty-ochre-heron doing → planning`).

Decisions:

- New command `chitty summary [--hours N]` (default 24, a module-level constant `SUMMARY_HOURS`; `N` a positive integer). It reads every ticket, active and archived, in every context, from its authoritative copy (`Repo.all_tasks()` in `src/chitty/store.py`, so a ticket being worked shows its branch copy), and keeps the History transition lines whose timestamp is at or after `now - N hours`. Date-only History lines (old format, no time) are ignored.
- Each ticket with at least one transition in the window appears once, under the status of its last transition in the window. Sections are printed in the reverse of `STATUSES` order (so `done` first, then `review`, `error`, `blocked`, `doing`, `todo`, ...), and a status with no tickets is not printed. This needs no change when a status is added (`TASK-599` adds `dropped`).
- Output, plain text: a header line `<status> (<count>)` per section, then one line per ticket sorted by the time of that last transition, newest first: two spaces, the id, two spaces, the title, two spaces, the `HH:MM` UTC time and the actor of that last transition. A ticket whose first-ever History transition (no old status) is in the window gets ` (new)` after its title. With nothing in the window it prints `nothing changed in the last <N> hours` and exits 0.
- Behaviour lives in `src/chitty/store.py` (and a pure helper in `src/chitty/model.py` if useful); `cli.py` only parses `--hours`, gets `now` from `datetime.now(UTC)` and prints, as `AGENTS.md` asks.

Out of scope: MCP, commits and `Task:` trailers, notes, a `--since` time, and any colour or glyphs.

Tests, in a new `tests/test_summary.py`:

- Pure function: given `StoredTask`-like tickets built from text (use `chitty.model.parse` on a ticket file with a `## History` section), a fixed `now` and `hours`, the grouping is as above. Cases: a ticket moved `todo → doing → review → done` inside the window appears only under `done`; a ticket whose only transition is 25 hours old is absent with `hours=24` and present with `hours=48`; a ticket created inside the window is marked `(new)`, one created before it is not; two tickets in one section are ordered newest first; date-only History lines are ignored; nothing in the window gives the empty message.
- Property, with Hypothesis (`max_examples=examples(50)` from `tests/__init__.py`): draw several tickets, each with a History of one to five transitions between drawn statuses at drawn times within 72 hours before a fixed `now`, and a drawn `hours` from 1 to 72. Every ticket with a transition at or after `now - hours` appears exactly once, under the new status of its last such transition; no other ticket appears; within each section the times are non-increasing.
- CLI: in a `RepoTestCase` repository, write three ticket files whose History timestamps are relative to the real current time (2 hours, 10 hours and 30 hours ago), run `chitty summary` and `chitty summary --hours 48` through `click.testing.CliRunner` with `chitty.cli.cli`, and assert the exact output.

To show the tests fail first, run them before the command exists and record the failures in a note.

## Acceptance Criteria

- [ ] The pure-function cases, the property and the CLI test in `tests/test_summary.py` pass, and fail before the change; record both runs in a note
- [ ] `chitty summary --hours 0` and `chitty summary --hours x` exit non-zero with a Click usage error; `chitty --help` lists `summary`; `make check` passes

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:32Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:32Z friendly-jade-stoat: changed notes
- 2026-11-22T22:50:39Z plucky-umber-wren: changed title, priority, description, acceptance criteria
- 2026-11-22T22:50:39Z plucky-umber-wren backlog → cold-read
