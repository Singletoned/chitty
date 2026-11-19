---
title: Refuse `make release` while a `blocks-release` ticket is open, and bump minor only for `done` tickets
status: planning
priority: high
created: 2026-11-19
---

## Description

On 2026-11-19 `make release` published `0.5.0` although `HUMAN-12` said not to until `TASK-331` landed. Nothing enforced it, and nobody chose `0.5.0`: `scripts/release_version.py` bumps the minor version whenever any ticket file labelled `needs-minor` changed since the last tag, even when that ticket's work has not landed (an edit to an open ticket counts).

Decisions (with the owner, 2026-11-19):

- Blockers: `scripts/release_version.py` exits non-zero, printing no version, when any ticket file under `chitty/` outside an `archive/` directory has the label `blocks-release` and a status other than `done`. Its standard error names each such ticket, one per line, with ID and title. `make release` already stops when the script fails, before it changes `src/chitty/__init__.py`.
- Minor bump: only tickets whose status is `done` count for `needs-minor`. A changed `needs-minor` ticket that is not `done` gives no minor bump and is not listed on standard error.
- Both rules are pure functions in `scripts/release_version.py`, taking a list of `(path, task)` pairs, where `task` is what `chitty.model.parse` returns, and returning the matching pairs in input order: `release_blockers(tickets)` and `minor_tickets(tickets)`. `main()` reads the files and calls them. Tests load the script with `importlib.util.spec_from_file_location`.
- Document the `blocks-release` label and the `done`-only rule in the `Releases` and `needs-minor` paragraphs of `AGENTS.md`.
- Out of scope: tickets that exist only on other branches; labelling tickets (the planner labels `TASK-416` and `TASK-413` and closes `HUMAN-12` after this lands).

Tests in `tests/test_release_version.py`, with Hypothesis, the repository's property-testing tool. The existing subprocess tests stay; their tickets are all `done`, so the blocker check leaves them unchanged. For the pure functions, generate lists of tickets with a status drawn from every status in `chitty.model` (`backlog` to `done`), labels drawn as a subset of `blocks-release`, `needs-minor` and `other`, and a path either under `chitty/tasks/` or under `chitty/tasks/archive/`; build each task by parsing generated ticket text, as the `ticket` helper in that file writes it. The code does not exist yet: first add both functions raising `NotImplementedError`, so the new tests fail on their own.

## Acceptance Criteria

- [ ] Property (Hypothesis): for any generated ticket list, `release_blockers` returns exactly the pairs labelled `blocks-release`, not `done` and not under `archive/`, in input order; `minor_tickets` returns exactly the pairs labelled `needs-minor` and `done`, archived or not, in input order
- [ ] Subprocess tests in the existing style: with one open `blocks-release` ticket committed, the script exits non-zero, prints nothing on standard output, and names that ticket ID on standard error; once the ticket is `done`, it prints the version as before. A `needs-minor` ticket with status `todo` changed since the tag gives a patch bump and is not listed. Each fails before the change
- [ ] `AGENTS.md` describes both rules; `make check` passes

## History

- 2026-11-19T10:01:36Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:30Z quick-ginger-lapwing: changed title, description, acceptance criteria
