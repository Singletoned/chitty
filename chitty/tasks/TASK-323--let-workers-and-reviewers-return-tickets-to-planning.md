---
title: Let workers and reviewers return tickets to planning
status: done
labels:
  - workflow
  - review
  - needs-minor
priority: high
created: 2026-11-13
moved_from: BACKLOG-48584236
---

## Description

Workers and reviewers must be able to return a ticket with missing or contradictory requirements or an unresolved design decision to planning, rather than bounce it through another worker attempt. A return note explains the discovery, why the current ticket cannot guide the work, and the decision needed. Preserve implementation work and release ownership; existing planning lists expose the ticket and automatic work/review selection skips it. Clear requirements with incorrect implementation stay in work; external obstacles requiring help stay blocked; cheap reversible implementation choices remain with the worker. Scope excludes repeated-cycle diagnosis and retrospective automation (separate backlog ticket), new planning runner modes, automatic replanning agents, and changes to the existing three review-to-doing failures escalation.

## Acceptance Criteria

- [x] The shared `check_edit` validation used by CLI and MCP requires a nonblank note for `doing → planning` and `review → planning` and clears ownership on accepted returns. Review returns retain review independence and one verdict per criterion, including at least one fail when criteria exist; workers can return their own work. Hypothesis tests vary source status, criteria, owner, note presence/content and note versus repeated-notes delivery, checking rejection without mutation and preservation of unrelated ticket content.
- [x] Real-file CLI and MCP tests verify successful worker and reviewer returns, explanatory note and transition history, preserved implementation artifacts, empty owner, visibility in `list -s planning`, and exclusion from `next` and explicit runner selection. Invalid note or review verdict is refused before writing.
- [x] A real-subprocess fake-agent runner regression covers both work and review returning to planning: the run stops without continuation, landing or starting another worker; the existing worktree and branch survive. Continuation prompts offer planning as an outcome for both roles. No real model session is required.
- [x] Work and review guides, README and pipeline design notes explain routing to planning versus work or blocked, the discovery/problem/decision note, preservation of committed work and normal planning/cold-read readiness before resumption. Rendered-guide tests fail before the update; fixed guidance text has no variable-input property. Existing dirty-review stop and review-failure escalation remain unchanged.

## Plan

Use existing planning status and selection machinery, not a new command or runner mode. Add shared validation for doing/review returns requiring a meaningful note and releasing ownership; include review-to-planning in review independence and criterion-verdict validation without altering existing review-to-doing escalation. Write Hypothesis and real-file interface tests first, plus focused guide and fake-agent runner tests; show new regressions fail before implementing. Update both role guides, continuation prompts, README and pipeline notes. Run format and all checks, commit intended paths only, and leave ready for independent review.

## Notes

Implemented return-to-planning validation, runner handoff, tests and guides. make check passes with 536 Python tests plus Node tests.

Compared and consolidated both implementations on `task-323` in `c1c4c5b`. Kept the broader Hypothesis, real-file CLI/MCP and subprocess tests plus the worker generic/Pi guidance; removed redundant runner tests and contradictory blocked/design guidance. The original Python regressions failed before implementation (12 tests, 31 failing subtests), then passed; the additional Pi prompt regression failed before the prompt correction and now passes. Final `make format` and `make check`: 539 Python tests and 28 Node tests pass. Neither implementation was independently reviewed here.

Reviewed:
1: pass - `make check` printed 539 Python tests OK and Node tests passed; Hypothesis validation and independence tests in `tests/test_return_to_planning.py` pass. Running the new tests against main versions of store, runner and guides printed FAILED (failures=31).
2: pass - `make check` passed the real-file CLI/MCP return and rejection tests and runner selection checks; the same new test suite against main printed FAILED (failures=31).
3: pass - `make check` passed both fake-agent subprocess runner tests and continuation prompt tests; the new suite against main printed FAILED (failures=31).
4: pass - `make format && make check` printed 539 tests OK and 28 passing Node tests; rendered guide and prompt tests passed, while the new suite against main printed FAILED (failures=31), including missing planning guidance. Inspected README and pipeline guidance and unchanged escalation and dirty-review rules.

## Summary

Ready for independent review in `.worktrees/task-323` on `task-323`. Consolidation commit `c1c4c5b` preserves both implementation histories. Returns from doing/review to planning require a nonblank note and release ownership; review independence and failing per-criterion verdicts remain enforced. Guides, Python and Pi continuation prompts agree on planning for requirement/design gaps, doing for implementation defects, and blocked for external help. Worktree/branch preservation and planning selection exclusion have real-file/subprocess coverage. Existing escalation and dirty-review stop remain unchanged. Verification: original Python tests failed before the fix; added Pi design-decision prompt test also failed before its fix. Final make format and make check pass: 539 Python tests, 28 Node tests. No changes merged to main. Duplicate manual worktree is being removed after confirming its entire history is reachable here.

## History

- 2026-11-13T19:51:56Z zesty-umber-puffin → backlog
- 2026-11-13T22:55:51Z brisk-yellow-urchin: changed title, description, acceptance criteria; wrote the plan
- 2026-11-13T22:55:51Z brisk-yellow-urchin backlog → doing
- 2026-11-13T23:06:15Z brisk-yellow-urchin: changed summary
- 2026-11-13T23:07:25Z rosy-coral-falcon: changed notes, summary; ticked acceptance criteria
- 2026-11-13T23:07:25Z rosy-coral-falcon doing → review
- 2026-11-13T23:13:43Z brisk-yellow-urchin: changed labels, notes, summary
- 2026-11-13T23:29:28Z tidy-silver-gannet: changed notes; ticked acceptance criteria
- 2026-11-13T23:29:28Z tidy-silver-gannet review → done
