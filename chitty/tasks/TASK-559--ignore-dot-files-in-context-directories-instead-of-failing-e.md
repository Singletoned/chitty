---
title: Ignore dot-files in context directories instead of failing every read
status: planning
labels:
  - bug
created: 2026-11-22
---

## Description

Repro (2026-11-21, `main`): in a fresh repository run `chitty init`, `chitty add One -d x`, then `touch chitty/tasks/.gitkeep`. `chitty list` fails with `Error: <root>/chitty/tasks/.gitkeep: task filename '.gitkeep' must end with .md`, committed or not. Placeholder files such as `.gitkeep` are a common way to keep an empty directory in Git, so one stray file stops every read.

Cause: `scan` in `src/chitty/store.py` (around line 2395) reports every non-ticket entry of a context or archive directory as a problem, and `Repo._files` raises on any problem; `Repo._collect_ticket_ids` (around line 595) also raises for a committed file on `main` whose name `ids.parse_filename` rejects.

Decisions:

- An entry whose name starts with `.` (file or directory) in a context directory or its `archive/` directory is not a ticket and is ignored by every read and by `chitty check`: `scan` skips it before any other test, and `_collect_ticket_ids` skips such a path on every ref, including `main`, before calling `ids.parse_filename`. Put the test in one helper, `is_hidden_entry(name: str) -> bool` in `src/chitty/ids.py`, used by both.
- Other non-ticket entries (`notes.txt`, a directory other than `archive`) keep today's errors.
- Out of scope: dot-files elsewhere under `chitty/`, and `chitty fix`.

Tests: Hypothesis (the repository's property tool) in a new `tests/test_property_hidden_entries.py`, inheriting `RepoTestCase` from `tests/support.py`, with real Git. Draw a set of one to three tickets (contexts `tasks` and `human`, some archived, created with `chitty add` and `chitty archive`) and a set of one to four hidden entries: each a name `"." + st.text(alphabet=string.ascii_letters + string.digits + "-_.", min_size=1)` (plus the literal `.gitkeep` always available via `st.sampled_from` mixed in), a location (either context directory or its `archive/`), a kind (file or directory with a file inside), and whether it is committed on `main`. Use `max_examples=25`, `deadline=None`.

## Acceptance Criteria

- [ ] Property: for every drawn case, `chitty list --all --json` and `chitty show <ID>` for each ticket give the same output as the same repository without the hidden entries, `chitty check` exits 0, and `chitty add Two -d x` succeeds with the next number; it fails on `main` (the `.gitkeep` example raises `must end with .md`)
- [ ] Example: a file `chitty/tasks/notes.txt` still makes `chitty list` exit 1 with `must end with .md`, and `chitty check` reports it; `make check` passes

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:33Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:33Z friendly-jade-stoat: changed notes
- 2026-11-22T09:49:58Z friendly-jade-stoat: changed title, labels, description, acceptance criteria
- 2026-11-22T09:49:58Z friendly-jade-stoat backlog → planning
