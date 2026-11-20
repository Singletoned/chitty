---
title: Show referenced tickets when promoting a ticket to todo
status: doing
depends_on:
  - TASK-356
created: 2026-11-16
---

## Description

`src/chitty/roles/plan.md` tells planners to re-check claims about other tickets just before promoting, because they can land during the read. Make `chitty edit -s todo` show those tickets instead, so the planner sees what changed without being told to look.

Decisions:

- Add a pure function `ticket_references(text: str, prefixes: Collection[str]) -> list[TaskId]` in `src/chitty/ids.py`. A candidate is a run of ASCII letters (the prefix), then `-`, then the longest run of ASCII letters and digits (the suffix), where the character before the prefix is not an ASCII letter, digit or `-`. It counts when the prefix is exactly one of `prefixes` (case-sensitive) and `TaskId.parse` accepts it. Results are in order of first appearance, without repeats. So with prefixes `TASK`, `TASKS` and `HUMAN`: `see TASK-12.` and `` `TASK-12` `` give `TASK-12`; `TASK-1-2` gives `TASK-1`; `TASK-12a` gives `TASK-12A`; `TASKS-3` gives `TASKS-3` only; `XTASK-12`, `task-12`, `a-TASK-1`, `TASK-012` and `UTF-8` give nothing.
- `Change` in `src/chitty/store.py` gets a `previous_status: str | None` field, which `Repo.edit` sets to the status before the edit (`None` from other writes).
- Add `Repo.referenced_tasks(stored: StoredTask) -> list[tuple[TaskId, StoredTask | None]]` in `src/chitty/store.py`. It scans the ticket as written by the edit: its Description and every criterion's text, with the prefixes of every configured context. It leaves out the ticket's own ID and looks each ID up with `Repo.lookup` from `TASK-356` (`None` when no ticket has it).
- `chitty edit` in `src/chitty/cli.py`, when `previous_status` is not `todo` and the status after the edit is `todo`, prints one line per reference after its result line, in order: `<ID> <status> <title>`, or `<ID> no such task`. Nothing extra otherwise, and nothing with `--json`. The lookups run after the write: if one raises (a duplicate ID, an unreadable file), the status change stands and the error is reported like any other `ChittyError`. A suffix is the longest run of ASCII letters and digits, so `TASK-12é` gives `TASK-12`; that is intended.
- Replace the plan guide bullet `Re-check claims about other tickets just before promoting, because they can land during the read.` with exactly `` `chitty edit -s todo` lists the tickets a ticket mentions: check that its claims about them still hold. ``

Tests use Hypothesis, as `tests/test_property_next.py` does. Put them in a new `tests/test_promote_references.py`; CLI tests inherit `CliTestCase` from `tests/test_cli.py`.

Out of scope: the MCP edit tool, references in Plan or Notes, and lower-case prefixes.

## Acceptance Criteria

- [ ] Property tests with Hypothesis on `ticket_references`, comparing `TaskId` values: (a) for any list of IDs (prefix from a fixed set, number 1 to 9999) joined by separators drawn from space, newline, comma, full stop, backtick, `(` and `)`, the result is that list with repeats removed, first appearance kept; (b) prefixing any one of those IDs with an ASCII letter, digit or `-` drops it from the result and keeps the rest; (c) for any text (`st.text()`) and prefix set (a set of non-empty runs of upper-case ASCII letters, the only prefixes config accepts), the call never raises, and every returned ID has a prefix in the set and its text appears in `text.upper()` (the suffix is normalised to upper case, so `TASK-12a` gives `TASK-12A`, as the Description decides; decided 2026-11-20). In (a), each separator is drawn by Hypothesis for each gap, not taken from a fixed cycle. Fail on `main`, where the function does not exist.
- [x] Example tests on `ticket_references` with prefixes `TASK`, `TASKS` and `HUMAN` give exactly the results listed in the Description for each of `see TASK-12.`, `` `TASK-12` ``, `TASK-1-2`, `TASK-12a`, `TASKS-3`, `XTASK-12`, `task-12`, `a-TASK-1`, `TASK-012` and `UTF-8`.
- [x] CLI test: `TASK-1` in `planning` mentions `TASK-2` (a `doing` ticket) in its Description, and `TASK-1` itself, `TASK-9` (no such ticket) and `TASK-2` again in a criterion. `chitty edit TASK-1 -s todo` prints its `updated` line followed by exactly `TASK-2 doing <title of TASK-2>` and `TASK-9 no such task`, and nothing else. Fails on `main`.
- [ ] CLI test: the whole stdout is only the `updated` or `unchanged` line (compared exactly, not by prefix) for a second `chitty edit TASK-1 -s todo` (which prints `unchanged TASK-1`), by `chitty edit TASK-1 --title x` on a `todo` ticket, by `-s doing` from `planning`, or by `-s todo --json` from `planning` (whose output stays valid JSON).
- [x] The plan guide bullet is replaced with the exact sentence in the Description, and `tests/test_guide_plan_restored.py` asserts that sentence (after `_flat`) instead of `because they can land during the read`. `make check` passes.
- [ ] CLI test: with `TASK-1` in `planning` mentioning `TASK-2`, and two working-tree files for `TASK-2` (a second copy written by hand under `chitty/tasks/`), `chitty edit TASK-1 -s todo` exits 1 with `TASK-2 is used by more than one file` in its output, and `chitty show TASK-1` afterwards prints `status: todo`

## Plan

Update the existing property and CLI regression tests to address review feedback and cover duplicate lookup failures. Verify the new regressions against the baseline or deliberately reverted behavior, then format, check, and hand off.

## Notes

Review failed (design): Criterion 1(c) contradicts the required normalization in the Description and criterion 2: decide whether input matching should be case-insensitive or should preserve the original suffix, then specify a consistent property. The existing implementation is preserved. The test coverage issues below are newly discovered; there are no earlier review notes.
1: fail - Running ticket_references on `TASK-12a` with prefix `TASK` returned `TASK-12A`; `str(result[0]) in text` printed `False`, although criterion 2 requires this result. The arbitrary-text property therefore cannot hold as written. Also the separator property cycles through a fixed sequence rather than generating arbitrary separators; generate separator choices after the property is clarified. Baseline main fails to import ticket_references; focused tests pass on this branch.
2: pass - `uv run python -m unittest tests.test_promote_references tests.test_promote_references_cli` ran 6 tests and printed OK, including all documented examples.
3: pass - The focused CLI promotion test passes; running the same test against an archive of main failed with `AssertionError: 1 != 3`.
4: fail - The title edit and planning-to-doing checks use startswith and do not assert there are no additional lines; assert the complete output or exact line count for both cases. The focused suite currently prints OK but would not detect extra reference lines in these cases.
5: pass - The guide and restored-guide assertion contain the required sentence; `make check` printed OK for 623 tests, with ruff and pyright passing.

Planning 2026-11-20: property (c) now checks against `text.upper()` over upper-case prefix sets; criterion 4 compares whole stdout; a new criterion covers the lookup-error path. Branch rebased onto `main` (conflicts in `src/chitty/ids.py` and `src/chitty/roles/plan.md` resolved by keeping both sides; old tip tagged `task-350-before-rebase`). Resumed as `doing` because the branch holds the implementation.

## Summary

Implemented ticket reference parsing, promotion output, and plan-guide update. Added Hypothesis, example, and CLI coverage. Verified with make format, make check (623 suites), focused tests, and chitty fix. Follow-up: none.

## History

- 2026-11-16T10:00:02Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:46Z intrepid-coral-raven backlog → planning
- 2026-11-17T16:02:05Z kind-umber-toad: changed dependencies, description, acceptance criteria
- 2026-11-17T16:02:05Z kind-umber-toad planning → cold-read
- 2026-11-17T16:02:13Z kind-umber-toad: changed description
- 2026-11-17T16:04:31Z kind-umber-toad: changed description, acceptance criteria
- 2026-11-17T16:22:03Z kind-umber-toad cold-read → todo
- 2026-11-17T22:28:15Z youthful-hazel-newt todo → doing
- 2026-11-17T22:28:23Z youthful-hazel-newt: wrote the plan
- 2026-11-17T22:33:26Z youthful-hazel-newt: changed summary
- 2026-11-17T22:33:32Z youthful-hazel-newt: ticked acceptance criteria
- 2026-11-17T22:33:33Z youthful-hazel-newt doing → review
- 2026-11-17T22:35:50Z intrepid-yellow-adder: changed owner, acceptance criteria, notes
- 2026-11-17T22:35:50Z intrepid-yellow-adder review → planning
- 2026-11-20T23:16:45Z quick-pearl-lapwing: changed acceptance criteria
- 2026-11-20T23:16:45Z quick-pearl-lapwing planning → cold-read
- 2026-11-20T23:19:01Z quick-pearl-lapwing: changed description, acceptance criteria, notes
- 2026-11-20T23:19:01Z quick-pearl-lapwing cold-read → doing
- 2026-11-20T23:52:15Z lively-ochre-kestrel: wrote the plan
