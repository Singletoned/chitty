---
title: Treat a ticket with no priority as medium when ordering
status: review
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Decided by the human on 2026-11-04: an unset priority should count as medium, not rank below low. Today `PRIORITY_ORDER` in `src/chitty/store.py` has `None: 3`, so `chitty next` and `chitty list` put an unprioritised ticket after a low one. Set `None` to the same rank as `medium`. Both users of `PRIORITY_ORDER`, `ordered` and `next_action`, then treat them alike, with their existing tie-breaks.

The field stays optional and `chitty list` still shows `-`: only the ordering changes. No version bump, since `chitty init` is not involved.

## Acceptance Criteria

- [x] Any statement of priority ordering in `README.md` and `PLAN.md` matches
- [x] Tests show `chitty next` choosing an unprioritised ticket ahead of a low one and by ID against a medium one, and `chitty list`, in text and `--json`, ranking it level with medium and still showing `-`; the existing tests asserting the old order, in `tests/test_next.py` and `tests/test_cli.py`, are updated

## Plan

1. Change the shared unset-priority rank in `src/chitty/store.py` so both existing ordering paths treat it as medium.
2. Update the priority-ordering statement in `PLAN.md`; confirm `README.md` needs no wording change.
3. Update the focused CLI and next-action tests, first confirming they fail under the old rank, then run `make check`.
4. Verify each acceptance criterion and request an independent review.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04, requested by the human after I skipped it. Confirmed: `ordered` and `next_action` are the only users of `PRIORITY_ORDER`, and the code change is one line. Fixed: existing tests assert the old order and must change, which the ticket omitted; `--json` and the `-` display now have a criterion; and the criterion said `chitty list` orders ties "the same way" as `chitty next`, which is wrong: `next` breaks ties by ID, while `list` keeps source order. Rejected: changing that difference, because it is existing behaviour unrelated to this ticket. The MCP `list` not sorting by priority, for the same reason. A shared constant in place of the dict, because a one-line change does not need it. `PLAN.md` lines 397-398 and 602 are the statements to update; `README.md` line 80 needs no change.

Claim continued on branch `task-139`; the initial `chitty inbox --pull` refreshed task state on `main` after this worktree was created, so the branch was rebased before this recorded claim commit.

Ready for an independent review by an agent other than the implementation agent. Verified both criteria with focused regression tests and `make check`; `chitty check` passes.

## History

- 2026-11-04T10:09:07Z lively-panda → todo
- 2026-11-04T11:58:06Z lively-panda: changed acceptance criteria, notes
- 2026-11-04T12:29:12Z honest-falcon: wrote the plan
- 2026-11-04T12:29:12Z honest-falcon todo → doing
- 2026-11-04T12:30:05Z honest-falcon: changed notes
- 2026-11-04T12:33:21Z honest-falcon: ticked acceptance criteria
- 2026-11-04T12:34:55Z honest-falcon: changed notes
- 2026-11-04T12:34:55Z honest-falcon doing → review
