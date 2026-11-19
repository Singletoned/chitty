---
title: Return a ticket to planning when it leaves a test for the worker to design
status: review
labels:
  - untestable
owner: untestable
created: 2026-11-19
---

## Description

Owner decision 2026-11-19: the worker only implements; designing tests is the planner's job, and a ticket that leaves a test undescribed is the planner's defect. `TASK-382` failed review three times: its criterion 1 listed four failure cases and about twelve checks without describing the tests, so the worker invented fixtures and assertions (it read the worktree instead of the branch tip, asserted a value read before the run, and left out checks). Each review filed this as `Review failed (tests)` and sent the ticket back to `doing`, so the same worker guessed again. It should have gone to `planning` the first time.

Change the guides, keeping the advice general because they reach every repository that uses Chitty (`AGENTS.md`):

- `src/chitty/roles/work.md`, in the list of reasons to set `-s planning`: add a test that a criterion needs but the ticket does not describe, meaning its fixture, action and assertions. Do not design it yourself.
- `src/chitty/roles/review.md`: when a failing finding is about a test the ticket did not describe (a missing case, fixture or assertion the worker had to choose), the cause is `design` and the ticket goes to `planning`, not `doing`. Before failing a ticket for `tests` again, check whether the earlier failure had the same cause; if so, the ticket is the problem.
- Add the same reason to the return-to-planning paragraph in `src/chitty/guide-runner.md`.

## Summary

Added the reason to the return-to-planning list in `work.md` (with "Do not design such a test yourself"), `review.md` (plus: such findings are `design` and go to `planning`; before a second `tests` failure, check whether the earlier failure had the same cause) and `guide-runner.md`. Added the phrase to `DEFECT_PHRASES` in `tests/test_guide_return_scope.py`, which fails 3 subtests against the old guides, and regenerated `tests/fixtures/guide-before-workflow.md` for the runner paragraph. `make check` passes (777 tests). Untestable beyond that phrase check: a person should read the three paragraphs. After landing, the main checkout must refresh `AGENTS.md`'s managed block.

## History

- 2026-11-19T13:22:19Z quick-ginger-lapwing → todo
- 2026-11-19T13:24:40Z quick-ginger-lapwing: changed title, description
- 2026-11-19T21:37:42Z daring-amber-kestrel todo → doing
- 2026-11-19T21:40:56Z daring-amber-kestrel: changed summary
- 2026-11-19T21:40:56Z daring-amber-kestrel doing → review
