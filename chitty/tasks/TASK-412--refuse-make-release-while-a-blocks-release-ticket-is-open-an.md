---
title: Refuse `make release` while a `blocks-release` ticket is open, and bump minor only for `done` tickets
status: done
priority: high
created: 2026-11-19
---

## Description

On 2026-11-19 `make release` published `0.5.0` although `HUMAN-12` said not to until `TASK-331` landed. Nothing enforced it, and nobody chose `0.5.0`: `scripts/release_version.py` bumps the minor version whenever any ticket file labelled `needs-minor` changed since the last tag, even when that ticket's work has not landed (an edit to an open ticket counts).

Decisions (with the owner, 2026-11-19):

- Blockers: `scripts/release_version.py` exits non-zero, printing no version, when any ticket file in any context has the label `blocks-release` and a status other than `done`: every `Path("chitty").rglob("*.md")` whose path has no part equal to `archive` (so `chitty/human/HUMAN-12--...md` and `chitty/backlog/` count, and a slug containing `archive` does not exclude a ticket). It scans every such file, not only those changed since the tag. Its standard error names each such ticket, one per line as `<ID>: <title>`; the ID comes from the file name with `chitty.ids.parse_filename`. A file under `chitty/` that fails `parse` or `parse_filename` is not caught: the exception propagates, so the script exits non-zero with a traceback and prints no version. `make release` already stops when the script fails, before it changes `src/chitty/__init__.py`.
- Minor bump: only tickets whose status is `done` count for `needs-minor`. A changed `needs-minor` ticket that is not `done` gives no minor bump and is not listed on standard error.
- Both rules are pure functions in `scripts/release_version.py`, taking a list of `(path, task)` pairs, where `task` is what `chitty.model.parse` returns, and returning the matching pairs in input order: `release_blockers(tickets)` and `minor_tickets(tickets)`. `main()` reads the files and calls them. Tests load the script with `importlib.util.spec_from_file_location`.
- Document the `blocks-release` label and the `done`-only rule in the `Releases` and `needs-minor` paragraphs of `AGENTS.md`.
- Out of scope: tickets that exist only on other branches; labelling tickets (`TASK-413` and `TASK-416` already carry the label; the planner closes `HUMAN-12` after this lands).

Tests in `tests/test_release_version.py`, with Hypothesis, the repository's property-testing tool. The existing subprocess tests stay; their tickets are all `done`, so the blocker check leaves them unchanged. Give the `ticket` helper a `status` parameter (default kept as `done` for the existing tests).

- Generator for the pure functions: lists of tickets, each with a status drawn from `chitty.model.STATUSES`, labels drawn as a subset of `blocks-release`, `needs-minor`, `other`, and the near misses `blocks-release-later` and `needs-minor-old` (which must not match), a title drawn from `string.ascii_letters + " "` with at least one letter, and a path drawn from `chitty/tasks/`, `chitty/human/`, `chitty/backlog/` and `chitty/tasks/archive/`, with a file name whose ID prefix matches the directory (`TASK-<n>` under `chitty/tasks/` and its archive, `HUMAN-<n>` under `chitty/human/`, `BACKLOG-<eight digits>` under `chitty/backlog/`) and a slug of `example` or `archive-notes` (an active ticket whose slug contains `archive`). Build each task by parsing ticket text from a module-level function in the same format as the `ticket` helper (`labels: [a, b]`); do not call `self.ticket` inside `@given`. Archived and active tickets are mixed in one list.
- The subprocess blocker tests commit the blocker ticket, then tag `v0.1.10`, then commit an unrelated change, so the blocker is unchanged since the tag and only a full scan finds it.
- The code does not exist yet: first add both functions raising `NotImplementedError`, so the new tests fail on their own.

## Acceptance Criteria

- [ ] Property (Hypothesis), using the generator in Tests: for any ticket list, `release_blockers` returns exactly the pairs labelled `blocks-release`, not `done`, and with no `archive` path part, in input order; `minor_tickets` returns exactly the pairs labelled `needs-minor` and `done`, archived or not, in input order; near-miss labels never match
- [ ] Subprocess tests in the existing style, with the blocker unchanged since the tag as Tests describes: an open `blocks-release` ticket `TASK-1` under `chitty/tasks/`, and one `HUMAN-12` under `chitty/human/`, each make the script exit non-zero, print nothing on standard output, and print `<ID>: <title>` with that full ID on standard error; with the tag at `v0.1.10` and the ticket `done`, it prints `0.1.11`. A `needs-minor` ticket with status `todo` changed since the tag gives a patch bump and is not listed. The open-blocker and `needs-minor` `todo` tests fail before the change; the `done` test passes before and after
- [ ] The `Releases` paragraph of `AGENTS.md` names the `blocks-release` label and says `make release` refuses while such a ticket is open; the `needs-minor` paragraph says only `done` tickets count. `make check` passes

## Plan

Implement and property-test the release blocker/minor ticket selectors, then verify the release-version subprocess behavior and update AGENTS.md release guidance. Run the focused tests before and after the implementation, then make check and commit the implementation changes with Task: TASK-412.

## Notes

Review failed (tests): Add the missing subprocess scenarios and validate every scanned filename before printing a version. These findings are newly discovered; there are no earlier review failures.
1: pass - `make check` passed the Hypothesis property; replacing each selector separately with a `NotImplementedError` stub made the property error with that exception.
2: fail - `test_human_blocker_fails` does not tag after committing the blocker or commit an unrelated change, so it does not verify an unchanged human blocker. There is no test of a done `blocks-release` ticket at tag `v0.1.10`; `test_label_before_tag_is_ignored` uses `needs-minor` instead. Add both scenarios and confirm the done-blocker test passes before and after. Also a throwaway subprocess using the existing test helper with a valid task body at `chitty/tasks/not-a-ticket.md` printed exit 0, stdout `0.1.10\n`, stderr empty: the specification requires `parse_filename` errors to propagate for every scanned active file, not only blockers. Validate all scanned filenames and add a regression test. Against `main`, the existing task-blocker and human-blocker tests failed because exit was 0, and the todo minor test failed with `0.2.0` instead of `0.1.10`.
3: pass - `AGENTS.md` documents both rules; `make check` passed 700 tests, ruff, pyright, and Node checks.

Added the missing regression cases: the unchanged HUMAN-12 blocker and a done blocker at tag v0.1.10 both pass; the malformed active ticket filename test first failed against the existing implementation (exit 0), then passed after validating every scanned active filename with parse_filename. The focused suite now passes (11 tests); make check passes (702 tests plus ruff and pyright).

Reviewed: Previous review findings are resolved.
1: pass - `make check` passed the Hypothesis selector property; the prior review verified each selector stub raised `NotImplementedError` in the property.
2: pass - `make check` passed all subprocess cases, including unchanged human and task blockers, done blocker, malformed filename and todo minor. Running the four blocker and todo cases against the script from `main` produced three expected failures (open blockers returned 0 and todo printed `0.2.0`) and the done case passed. This resolves the earlier review note.
3: pass - `AGENTS.md` documents both rules; `make check` passed 702 tests, ruff and pyright.

## Summary

Validated every active ticket filename before release selection; added regression coverage for unchanged human blockers, done blockers at the tag, and malformed filenames. Verification: focused release-version tests (11) and make check (702 tests, ruff, pyright) pass. Follow-up: independent review.

## History

- 2026-11-19T10:01:36Z quick-ginger-lapwing → planning
- 2026-11-19T11:06:30Z quick-ginger-lapwing: changed title, description, acceptance criteria
- 2026-11-19T11:06:36Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:08:11Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:08:14Z quick-ginger-lapwing: changed description, acceptance criteria
- 2026-11-19T11:08:18Z quick-ginger-lapwing planning → cold-read
- 2026-11-19T11:10:12Z quick-ginger-lapwing cold-read → planning
- 2026-11-19T11:10:15Z quick-ginger-lapwing: changed description
- 2026-11-19T11:10:17Z quick-ginger-lapwing: changed acceptance criteria
- 2026-11-19T11:10:17Z quick-ginger-lapwing planning → todo
- 2026-11-19T11:11:52Z jolly-ebony-toad todo → doing
- 2026-11-19T11:12:56Z jolly-ebony-toad: wrote the plan
- 2026-11-19T11:17:18Z jolly-ebony-toad: changed summary
- 2026-11-19T11:17:18Z jolly-ebony-toad doing → review
- 2026-11-19T11:20:18Z rosy-umber-falcon: changed acceptance criteria, notes
- 2026-11-19T11:20:18Z rosy-umber-falcon review → doing
- 2026-11-19T11:26:13Z rosy-pearl-falcon: changed notes, summary
- 2026-11-19T11:26:13Z rosy-pearl-falcon doing → review
- 2026-11-19T11:27:59Z honest-dusky-gannet: changed notes
- 2026-11-19T11:27:59Z honest-dusky-gannet review → done
