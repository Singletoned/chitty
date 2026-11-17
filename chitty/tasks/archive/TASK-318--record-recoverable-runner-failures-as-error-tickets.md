---
title: Record recoverable runner failures as error tickets
status: done
labels:
  - bug
  - runner
owner: human
depends_on:
  - TASK-325
  - TASK-326
created: 2026-11-13
---

## Description

When automated ticket work fails, the failure currently disappears into terminal output and cannot be discovered or handed to a stronger repair agent. Distinguish recoverable automation errors from human-blocked work, preserve the ticket worktree, and use the existing error reporter for failures that cannot be attached safely to a ticket.

## Acceptance Criteria

- [ ] Ticket-scoped failures after a ticket and worktree are resolved—setup, check, agent, or landing failures—move the ticket to `error`, preserve its branch and worktree, and record the phase, full captured error output, and recovery context in its notes.
- [ ] Normal `chitty next` and `chitty run` never select `error`; explicit `chitty run --errors` selects only error tickets, uses a repair-oriented agent prompt, and rejects `--ticket`, `--mode`, and `--owner` combinations.
- [x] A repair run requires the agent to set a repaired ticket to `review` or a ticket requiring a human decision to `blocked`; any other final status is reported as an error.
- [ ] Failures before a safe ticket handoff, including invalid configuration, dirty main checkout, missing branch, interruption, or failure to write the handoff, leave task state unchanged and invoke `error_reporter` with `phase`, `ticket`, `mode`, `worktree`, and full error output.

## Plan

1. Add `error` to the task status model, validation, selection/display, status transitions, and guides; keep `blocked` for human or external prerequisites. 2. Add a dedicated `--errors` run selection and repair prompt, with explicit option validation and repair result validation. 3. Refactor run failure boundaries so setup, check, agent, and landing failures after ticket/worktree resolution write an error handoff without deleting the worktree or branch; preserve existing behavior for interruptions and unsafe global failures. 4. Pass structured phase/ticket/mode/worktree/error context to `error_reporter`, and add focused real-file tests for each failure class. 5. Update runner documentation and run format/check.

## Notes

Cold-read findings were resolved before implementation. Regression evidence: the new explicit error-repair test failed on the pre-change tree with `Error: Invalid value for -s / --status: error is not one of ...`; it passes with the implementation. `make format && make check` passes: Ruff, Pyright, 525 unittest tests, and Node tests.

Review failed (tests): Add regression coverage and fix the missing output capture, repair result validation, and interruption reporting before retrying.
1: fail - Running `_setup` with a command that printed `SETUP_MARKER` and exited 9 printed the marker to the terminal but the handoff error contained only `setup exited with status 9`; the full output is lost.
2: pass - `test_error_tickets_need_explicit_repair_and_repair_updates_main_state` passed; each forbidden `--errors` combination printed the usage error, and `guide("repair", "TASK-318")` printed the repair instructions.
3: fail - A successful fake agent that left the ticket in error produced `TASK-1: error → error` and exit 0, rather than reporting an error.
4: fail - A fake agent interrupted with `KeyboardInterrupt` printed `interrupted during agent`, but the configured reporter was not called.
`make format && make check` passed: 525 Python tests and Node tests.

Follow-up verification: setup failures now retain command output in the error note; interruption reporter regression confirms phase context. Full `make format && make check` passed (526 Python tests and Node tests). The only uncommitted formatter adjustment previously observed is now absent; working tree is clean.

Implemented the review fixes in commits `1a1348b` and `b4689bb`: setup and agent output are captured in handoff errors, invalid repair final statuses raise a reported error, and interruptions are reported through the configured reporter. Added regression tests for all three findings. `make check` passes 527 Python tests plus Node tests.

Review failed (tests): Add regressions and fix timeout output capture, repair prompting for mode-based agent commands, and missing-branch handling before retrying.
1: fail - Running `_run_session` with `sh -c 'echo TIMEOUT_MARKER; sleep 5'` and a one-second timeout printed `agent timed out after 1 seconds` as the error, without `TIMEOUT_MARKER`; the handoff loses captured output.
2: fail - Running `_agent_command` for an error ticket with `agent_command = "echo --chitty-{mode} {id}"` printed `(/bin/echo, --chitty-work, TASK-1)`, not a repair prompt. The passing explicit repair test covers only the prompt-enabled configuration.
3: pass - `make format && make check` passed 527 Python tests and Node tests; `tests/test_next.py` checks that an unchanged repair exits 1 with `repair agent left TASK-1 in invalid status error`, and that blocked is accepted.
4: fail - `uv run python -m unittest tests.test_review_merge.TestReviewMerge.test_missing_review_branch_blocks_ticket_and_is_not_selected_again -v` printed `OK`: the existing test confirms that a missing review branch changes the ticket to blocked, contrary to the required unchanged state and reporter handoff. The interruption reporter test passed.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Human session, 2026-11-16: this ticket code already reached `main` in `6a9e3ee` (Merge TASK-318 runner error fixes, 19:37 on 2026-11-13), between the worker moving it to review and the third review failing, so there is nothing left on the branch to land. The third review findings are now separate tickets: timeout output (`TASK-324`, done), repair prompts for mode-based agent commands (`TASK-325`) and missing review branches (`TASK-326`). Leave this blocked until those land, then mark it done and archive it.

## Summary

Committed runner failure-output capture and repair-status validation in 1a1348b (Task: TASK-318). Full make format && make check passed: 526 Python tests and Node tests. Added regressions for setup output and interrupted-agent reporter context. Working tree is clean; ready for independent review.

## History

- 2026-11-13T18:27:49Z zesty-umber-puffin → planning
- 2026-11-13T18:28:00Z zesty-umber-puffin: wrote the plan
- 2026-11-13T18:29:28Z zesty-umber-puffin: changed acceptance criteria, notes; wrote the plan
- 2026-11-13T18:29:32Z zesty-umber-puffin planning → doing
- 2026-11-13T18:31:46Z witty-silver-urchin: changed notes
- 2026-11-13T18:31:46Z witty-silver-urchin doing → blocked
- 2026-11-13T19:02:19Z zesty-umber-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-13T19:02:19Z zesty-umber-puffin blocked → review
- 2026-11-13T19:03:34Z zesty-umber-puffin: changed acceptance criteria, notes; overrode review independence
- 2026-11-13T19:03:34Z zesty-umber-puffin review → doing
- 2026-11-13T19:03:39Z zesty-umber-puffin: replaced notes
- 2026-11-13T19:03:53Z zesty-umber-puffin: ticked acceptance criteria
- 2026-11-13T19:03:53Z zesty-umber-puffin doing → review
- 2026-11-13T19:30:40Z sunny-zinc-ibis: changed acceptance criteria, notes; ticked acceptance criteria
- 2026-11-13T19:30:40Z sunny-zinc-ibis review → doing
- 2026-11-13T19:36:45Z friendly-ochre-quail: changed notes, summary
- 2026-11-13T19:36:45Z friendly-ochre-quail doing → review
- 2026-11-13T19:36:48Z zesty-umber-puffin: changed notes; ticked acceptance criteria
- 2026-11-13T19:44:27Z intrepid-teal-toad: changed owner, acceptance criteria, notes; ticked acceptance criteria
- 2026-11-13T19:44:27Z intrepid-teal-toad review → blocked
- 2026-11-16T10:28:15Z intrepid-coral-raven: changed dependencies, notes
- 2026-11-17T17:25:12Z kind-umber-toad done → archived
