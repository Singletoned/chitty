---
title: Return a ticket to planning for any defect in the ticket
status: done
created: 2026-11-16
---

## Description

Workers and reviewers can already return a ticket to `planning` (`TASK-323`), but the guides allow it only for missing or contradictory requirements or an unresolved design decision. With read-only cold reads (`TASK-336`), workers and reviewers become the main check on tickets, so widen the trigger to any defect in the ticket.

A defect in the ticket is any of these five, written with these exact phrases (a criterion that contradicts the description counts as contradictory requirements):

- `missing or contradictory requirements`
- `an unresolved design decision`
- `a wrong claim about the code, files or other tickets`
- `a criterion that cannot be verified as written or would pass with nothing built`
- `a ticket too large to finish in one session`

A defect in the ticket always goes to planning, even when it could be worked around cheaply; the worker's cheap-to-reverse default applies only to choices the ticket leaves open. A reviewer who finds a defect in the ticket writes `Review failed (design):` and sets `-s planning`; `-s doing` is only for implementation defects against clear requirements. `blocked` stays for external obstacles. The note still gives the discovery, why the ticket cannot guide the work, and the decision needed. The store validation from `TASK-323` does not change.

Files:
- `src/chitty/roles/work.md`: the bullet starting `For missing or contradictory requirements`, and the cheap-to-reverse default bullet after it.
- `src/chitty/roles/review.md`: the same bullet; the sentence `A ticket that is itself wrong also fails, with the cause design`, which must now say it goes to planning; and the bullet `If the ticket is too large, say so in the failure note and suggest how to split it`, which must now route to planning with the suggested split in the note.
- `continuation_prompt` in `src/chitty/run.py`.
- `src/chitty/guide-runner.md`, and `tests/fixtures/guide-before-workflow.md`, which `tests/test_guide_workflow_block.py` compares byte for byte with `managed_guide("runner")`: change the fixture to the new runner text, so that test keeps guarding the block layout.
- The return-to-planning paragraph of `README.md`, and the bullets of `docs/plan/pipeline-and-feedback.md` that start `A failed review of implementation` and `A return to planning requires`.

Do not edit `AGENTS.md` or run `chitty init`: the main checkout updates the managed block after landing. No `needs-minor`: the old managed text stays correct, only narrower.

Out of scope: telling them to list every problem in one note (`TASK-354`), and any code change to status validation.

No property tests: fixed text, and the defects are a small fixed set, each listed here and each tested. Tests check text flattened with `" ".join(text.split())`, because the guides wrap lines.

## Acceptance Criteria

- [x] Flattened `guide("work")` and `guide("review")` each contain all five defect phrases as reasons to set `-s planning`; work still contains `For a cheap-to-reverse default, choose it` and says it applies only to choices the ticket leaves open; review still contains `implementation defects against clear requirements`, and its too-large and ticket-is-wrong rules route to `planning`. A test in `tests/test_guide_return_scope.py` checks each phrase in each role as a separate subtest and fails before the change; `tests/test_guide_return_to_planning.py` is updated to the new wording.
- [x] `continuation_prompt("work", ...)` and `continuation_prompt("review", ...)` each contain the literal `a defect in the ticket` and still offer `blocked`; flattened `managed_guide("runner")` contains all five defect phrases. Tested in `tests/test_guide_return_scope.py`; the test fails before the change. `tests/test_guide_workflow_block.py` passes with the updated fixture.
- [x] The `README.md` paragraph and the two `docs/plan/pipeline-and-feedback.md` bullets named above list the same five defects; the reviewer quotes each in the evidence. `make check` passes.

## Plan

Update the work/review guides, continuation prompt, runner guide and fixture, README, and pipeline plan to route all five specified ticket defects to planning while preserving blocked and implementation-defect guidance. First inspect the existing text and tests, add/update focused guide tests so they fail before the documentation changes, then implement the wording, run the focused regression tests followed by make format && make check, review the diff, commit only implementation files with a Task: TASK-360 message, and finish with chitty fix and a clean review handoff.

## Notes

Implemented all five ticket-defect routes to planning across work/review/runner guidance, continuation prompts, README, and pipeline plan. Regression tests were run before the fix and failed (11 failures), then passed after the fix. Verification: uv run python -m unittest tests.test_guide_return_scope tests.test_guide_return_to_planning tests.test_guide_workflow_block; make format; make check. Commit: 9527b6f.

Reviewed: all criteria pass after independent diff inspection and verification.
1: pass - tests/test_guide_return_scope.py and tests/test_guide_return_to_planning.py pass; work.md and review.md route missing or contradictory requirements, an unresolved design decision, a wrong claim about the code, files or other tickets, a criterion that cannot be verified as written or would pass with nothing built, and a ticket too large to finish in one session to planning while preserving the cheap-default and implementation-defect rules.
2: pass - continuation_prompt tests pass for both roles; guide workflow tests pass with the updated fixture, and managed_guide("runner") contains all five defect phrases.
3: pass - README.md and both named pipeline bullets list missing or contradictory requirements, an unresolved design decision, a wrong claim about the code, files or other tickets, a criterion that cannot be verified as written or would pass with nothing built, and a ticket too large to finish in one session; make format && make check passed all 580 tests, ruff, pyright, and formatting checks.

## Summary

Handoff: documentation and continuation-prompt guidance now routes missing or contradictory requirements, an unresolved design decision, a wrong claim about the code, files or other tickets, a criterion that cannot be verified as written or would pass with nothing built, and a ticket too large to finish in one session to planning. Review should inspect commit 9527b6f. Verification: focused guide tests passed; make format && make check passed; worktree is clean. Follow-ups: none.

## History

- 2026-11-16T12:50:58Z open-russet-eel → planning
- 2026-11-16T12:51:14Z open-russet-eel: changed owner
- 2026-11-16T12:51:14Z open-russet-eel planning → cold-read
- 2026-11-16T12:53:25Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T12:53:25Z open-russet-eel cold-read → planning
- 2026-11-16T12:54:42Z open-russet-eel: changed owner
- 2026-11-16T12:54:42Z open-russet-eel planning → todo
- 2026-11-16T12:55:40Z daring-yellow-jay todo → doing
- 2026-11-16T12:55:53Z daring-yellow-jay: wrote the plan
- 2026-11-16T12:58:21Z daring-yellow-jay: changed notes, summary; ticked acceptance criteria
- 2026-11-16T12:58:21Z daring-yellow-jay doing → review
- 2026-11-16T13:00:09Z nimble-jade-toad: changed notes; ticked acceptance criteria
- 2026-11-16T13:00:09Z nimble-jade-toad review → done
