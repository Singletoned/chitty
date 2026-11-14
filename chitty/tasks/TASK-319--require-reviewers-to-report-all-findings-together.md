---
title: Require reviewers to report all findings together
status: done
labels:
  - workflow
  - review
priority: high
created: 2026-11-13
moved_from: BACKLOG-93769170
---

## Description

Reviewers often stop after the first defect, causing avoidable review cycles and hiding whether the whole change is coherent.

## Acceptance Criteria

- [x] The review guide requires inspecting every acceptance criterion and the complete diff before writing the review note.
- [x] A failing review note reports all findings from that pass together, with actionable findings grouped by criterion; a criterion may have multiple findings.
- [x] The review guide requires checking that the changes fit together, cover useful property-test opportunities, and make sense to users.
- [x] The guide distinguishes newly discovered findings from previously reported findings that remain unresolved. Discovering another bug on a later pass is expected, not evidence of an earlier process failure.

## Plan

Update the review guide and pipeline design notes to require a complete inspection before one consolidated verdict, preserving dirty-worktree and verification-limit handling. Group all actionable findings under the existing criterion lines, and distinguish new discoveries from unresolved earlier findings without blaming prior reviewers. Add fixed-text rendered-guide regression tests (no property tests: fixed instructions with no variable input), demonstrate failure before the guidance change, then run format and all checks. Scope excludes runner changes and review-note parsing.

## Notes

Runner error (agent): TASK-319 was unchanged; only committed changes are visible to `chitty run`

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-319`

Error output:
```text
TASK-319 was unchanged; only committed changes are visible to `chitty run`
```

Planner, 2026-11-14: the runner error was a branch mix-up. The work (`14670e2`) was done on `backlog-93769170` in `../chitty-review-completeness` before the ticket was renumbered, so `task-319` had nothing. Merged that branch and `main` into `task-319` (review guide conflict resolved keeping both the planning/blocked wording from `main` and the consolidated-findings wording); `make check` passes. Ready for independent review.

Reviewed: Complete diff inspected; make format && make check passed (547 Python tests and Node tests). Regression tests against the guide at 14670e2^ reported FAILED (failures=15); the current suite passed.
1: pass - test_complete_inspection_before_verdict checks every criterion and complete diff before the note.
2: pass - test_all_findings_in_one_note checks consolidated findings grouped by criterion, including multiple findings.
3: pass - test_complete_inspection_before_verdict checks coherence, property-test opportunities and user sense.
4: pass - test_new_discoveries_are_not_prior_process_failures checks distinction, citations and no blame for later discoveries.

## History

- 2026-11-13T19:51:41Z zesty-umber-puffin → backlog
- 2026-11-13T22:24:02Z brisk-yellow-urchin: changed acceptance criteria; wrote the plan
- 2026-11-13T22:24:02Z brisk-yellow-urchin backlog → doing
- 2026-11-13T22:27:19Z daring-pearl-dormouse: changed notes
- 2026-11-13T22:27:19Z daring-pearl-dormouse doing → error
- 2026-11-14T09:20:45Z jolly-silver-falcon: changed notes
- 2026-11-14T09:20:45Z jolly-silver-falcon error → review
- 2026-11-14T09:28:25Z golden-khaki-stoat: changed notes; ticked acceptance criteria
- 2026-11-14T09:28:25Z golden-khaki-stoat review → done
