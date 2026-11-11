---
title: Keep tickets in random-ID contexts in `backlog`
status: done
priority: high
depends_on:
  - TASK-190
created: 2026-11-05
---

## Description

Second of three parts, after `TASK-190`. A ticket in a context with `random_ids` waits to be assessed, so it is always `backlog`, and leaves only by being moved. `Repo.add` sets `fields["status"] = "backlog"` before its checks of `done` and the description, whatever `-s` says. The check in `src/chitty/cli.py` that a description is required unless the status is `backlog` runs before `resolve_add_target`, so move it after that call and test the resolved context, not `-c`. `Repo.edit` refuses any other status, with a message saying to run `chitty move <ID> tasks`. `Repo.move` into such a context also sets `backlog`, recording it with `with_history`, because `with_field` writes no History entry. Set it on the moved ticket before the loop over other tickets: that loop reassigns `task`, so today `moved` is built from the last other ticket, and `Repo.move` needs a distinct variable there.

`chitty move <ID> tasks` already gives a ticket the target's next number and rewrites references, so it is the promotion, and its status stays `backlog` so the planning session can cold-read it. It refuses until the ticket has merged to `main`, because `_require_current_version` sends a person to the branch holding the newest copy: leave that alone, and say so in the note of the test.

## Acceptance Criteria

- [x] Tests show `add` with `-s todo` creating a `backlog` ticket with no description needed, `edit -s todo` refused with that message, and `chitty move TASK-5 backlog` setting `backlog`
- [x] A test in a Git repository, with the ticket committed on `main`, shows `chitty move <ID> tasks` giving the next `TASK-` number, keeping `backlog`, and rewriting references in other tickets, and the returned change showing the moved ticket's own title

## Plan

Inspect the repository add/edit/move flows and existing tests, add regression coverage for random-ID backlog behavior and promotion/reference rewriting, implement the smallest store/CLI fixes, run format and full checks, then commit with Task: TASK-191.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-05. Serious, both fixed: the description check runs before the context is known; and `Repo.move` reassigns `task` in a loop, an existing bug that would have lost the status and reports another ticket's content. Also fixed: recording History, the order in `Repo.add`, and the test needing a Git repository.

Regression tests failed before the fix: CLI rejected descriptionless todo adds in random-ID contexts, moves did not set backlog, and promotion was not covered. Added store/CLI behavior and tests. The promotion test commits the ticket on main because _require_current_version intentionally refuses a move while the newest copy is on another branch; that behavior is unchanged.

Reviewed: make format and make check pass, including 336 unittest cases and Node tests. The promotion test correctly commits on main because _require_current_version rejects moves from a newer branch copy.

1: pass - Regression tests verify random-ID add backlog behavior, edit refusal, and move into backlog history.
2: pass - Git-backed regression verifies promotion to next TASK ID, backlog status, reference rewriting, and returned title.

## Summary

Implemented random-ID backlog enforcement: descriptionless adds resolve context before validation, Repo.add forces backlog, edits explain promotion via chitty move, and moves record backlog history before rewriting references. Added CLI/Git regression coverage. Verified with make format, make check, and chitty fix; full suite passes.

## History

- 2026-11-05T14:47:51Z mellow-newt → backlog
- 2026-11-05T14:50:40Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T14:50:41Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T14:50:42Z mellow-newt backlog → todo
- 2026-11-06T18:37:47Z mellow-gannet todo → doing
- 2026-11-06T18:38:01Z mellow-gannet: wrote the plan
- 2026-11-06T18:47:20Z mellow-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-06T18:47:20Z mellow-gannet doing → review
- 2026-11-06T18:55:58Z honest-jay: changed notes; ticked acceptance criteria
- 2026-11-06T18:55:58Z honest-jay review → done
- 2026-11-11T10:17:51Z vivid-yellowhammer: changed parent
