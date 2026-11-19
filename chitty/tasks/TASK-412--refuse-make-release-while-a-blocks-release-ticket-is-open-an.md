---
title: Refuse `make release` while a `blocks-release` ticket is open, and bump minor only for `done` tickets
status: planning
priority: high
created: 2026-11-19
---

## Description

On 2026-11-19 `make release` published `0.5.0` although `HUMAN-12` said not to until `TASK-331` landed. Nothing enforced it, and nobody chose `0.5.0`: `scripts/release_version.py` bumps the minor version whenever any ticket file labelled `needs-minor` changed since the last tag, even when that ticket's work has not landed (an edit to an open ticket counts).

Decisions (with the owner, 2026-11-19):

- Blockers: `scripts/release_version.py` exits non-zero, printing no version, when any ticket file in any context has the label `blocks-release` and a status other than `done`: every `Path("chitty").rglob("*.md")` whose path has no part equal to `archive` (so `chitty/human/HUMAN-12--...md` and `chitty/backlog/` count, and a slug containing `archive` does not exclude a ticket). It scans every such file, not only those changed since the tag. Its standard error names each such ticket, one per line, with ID and title; the ID comes from the file name with `chitty.ids.parse_filename`. `make release` already stops when the script fails, before it changes `src/chitty/__init__.py`.
- Minor bump: only tickets whose status is `done` count for `needs-minor`. A changed `needs-minor` ticket that is not `done` gives no minor bump and is not listed on standard error.
- Both rules are pure functions in `scripts/release_version.py`, taking a list of `(path, task)` pairs, where `task` is what `chitty.model.parse` returns, and returning the matching pairs in input order: `release_blockers(tickets)` and `minor_tickets(tickets)`. `main()` reads the files and calls them. Tests load the script with `importlib.util.spec_from_file_location`.
- Document the `blocks-release` label and the `done`-only rule in the `Releases` and `needs-minor` paragraphs of `AGENTS.md`.
- Out of scope: tickets that exist only on other branches; labelling tickets (the planner labels `TASK-416` and `TASK-413` and closes `HUMAN-12` after this lands).

Tests in `tests/test_release_version.py`, with Hypothesis, the repository's property-testing tool. The existing subprocess tests stay; their tickets are all `done`, so the blocker check leaves them unchanged. Give the `ticket` helper a `status` parameter (default kept as `done` for the existing tests).

- Generator for the pure functions: lists of tickets, each with a status drawn from `chitty.model.STATUSES`, labels drawn as a subset of `blocks-release`, `needs-minor`, `other`, and the near misses `blocks-release-later` and `needs-minor-old` (which must not match), a title drawn from `string.ascii_letters + " "` with at least one letter, and a path drawn from `chitty/tasks/`, `chitty/human/`, `chitty/backlog/` and `chitty/tasks/archive/`, with a file name such as `TASK-<n>--example.md` or `TASK-<n>--archive-notes.md` (an active ticket whose slug contains `archive`). Build each task by parsing ticket text written as the `ticket` helper writes it. Archived and active tickets are mixed in one list.
- The subprocess blocker tests commit the blocker ticket, then tag `v0.1.10`, then commit an unrelated change, so the blocker is unchanged since the tag and only a full scan finds it.
- The code does not exist yet: first add both functions raising `NotImplementedError`, so the new tests fail on their own.

## Acceptance Criteria

- [ ] Property (Hypothesis), using the generator in Tests: for any ticket list, `release_blockers` returns exactly the pairs labelled `blocks-release`, not `done`, and with no `archive` path part, in input order; `minor_tickets` returns exactly the pairs labelled `needs-minor` and `done`, archived or not, in input order; near-miss labels never match
- [ ] Subprocess tests in the existing style, with the blocker unchanged since the tag as Tests describes: an open `blocks-release` ticket under `chitty/tasks/`, and one under `chitty/human/`, each make the script exit non-zero, print nothing on standard output, and name that ticket ID on standard error; once the ticket is `done`, it prints the version as before. A `needs-minor` ticket with status `todo` changed since the tag gives a patch bump and is not listed. Each fails before the change
- [ ] The `Releases` paragraph of `AGENTS.md` names the `blocks-release` label and says `make release` refuses while such a ticket is open; the `needs-minor` paragraph says only `done` tickets count. `make check` passes

## History

- 2026-11-19T10:01:36Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:30Z quick-ginger-lapwing: changed title, description, acceptance criteria
- 2026-11-19T11:06:36Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:08:11Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:08:14Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:08:18Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:10:12Z quick-ginger-lapwing cold-read → planning
