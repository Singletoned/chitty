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
- `Repo._files` (around line 1529) raises on any `scan` problem and is the choke point for working-tree reads: its callers (`_collect_ticket_ids`, `_working_ticket_files` for `show`, and the list and next-number loops) need no change of their own once `scan` skips hidden entries. `chitty check` and `chitty fix` call `scan` directly (`src/chitty/check.py`), so they follow too.
- Other non-ticket entries (`notes.txt`, a directory other than `archive`) keep today's errors.
- Out of scope: dot-files elsewhere under `chitty/`, including a hidden directory directly under `chitty/` (which `discovered_contexts` treats as a context), and `chitty fix`.

Tests: Hypothesis (the repository's property tool) in a new `tests/test_property_hidden_entries.py`, inheriting `CliTestCase` from `tests/test_cli.py` (real Git, `run_cli`), `max_examples=25`, `deadline=None`. Each example: add one to three tickets with `run_cli("add", ...)`, in `tasks` or `human` (drawn), and archive some of the `human` ones with `run_cli("archive", "HUMAN-<n>")` (the `human` context has review off, as `test_dynamic_completion_lists_contexts_and_active_ids_first` does); commit; record the outputs of `chitty list --all --json` and `chitty show <ID>` for each ticket. Then add one to four hidden entries: each a name drawn from `st.sampled_from([".gitkeep", ".DS_Store"])` or `"." + st.text(alphabet=string.ascii_letters + string.digits + "-_.", min_size=1)`, a location (`chitty/tasks`, `chitty/human`, or either one's `archive/`, creating it if absent), a kind (an empty file, or a directory holding one file), and whether it is committed on `main`. Compare against the recorded outputs.

## Acceptance Criteria

- [ ] Property: for every drawn case, after adding the hidden entries, `chitty list --all --json` and `chitty show <ID>` for each ticket print what they printed before, `chitty check` exits 0, and `chitty add Two -d x` succeeds with the next free number; it fails on `main` (a `.gitkeep` makes `chitty list` raise `must end with .md`)
- [ ] Example: a file `chitty/tasks/notes.txt` still makes `chitty list` exit 1 with `must end with .md`, and `chitty check` reports it; `make check` passes

## Notes

Suggestion origin: chitty

## History

- 2026-11-22T09:47:33Z friendly-jade-stoat → backlog
- 2026-11-22T09:47:33Z friendly-jade-stoat: changed notes
- 2026-11-22T09:49:58Z friendly-jade-stoat: changed title, labels, description, acceptance criteria
- 2026-11-22T09:49:58Z friendly-jade-stoat backlog → planning
- 2026-11-22T09:50:27Z friendly-jade-stoat: changed description, acceptance criteria
- 2026-11-22T09:50:27Z friendly-jade-stoat planning → cold-read
- 2026-11-22T09:51:38Z friendly-jade-stoat: changed description
- 2026-11-22T09:51:38Z friendly-jade-stoat cold-read → planning
