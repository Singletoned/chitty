---
title: Stop reviewers landing tickets, and document landing
status: blocked
priority: high
owner: human
depends_on:
  - TASK-131
parent: TASK-106
created: 2026-11-04
---

## Description

`TASK-131` has `chitty run` land a ticket after a pass, so reviewers should stop doing it. The Pi review prompt in `src/chitty/integrations/pi/chitty.ts` stops telling the reviewer to merge or remove anything. `src/chitty/guide.md` tells agents without `chitty run` to merge `main` into the branch in the worktree and run the configured checks first, then only fast-forward `main`. If `TASK-141` has landed, make the same change in `src/chitty/roles/review.md`, and to whatever now produces the prompt.

`PLAN.md` and `README.md` describe landing.

Out of scope: changing landing itself.

## Acceptance Criteria

- [x] A test shows the review instructions no longer mentioning merging or removing
- [x] `PLAN.md`, `README.md`, and `src/chitty/guide.md` describe landing; the ticket branch does not bump `__version__`.

## Plan

Update review role text and Pi-generated review prompt so reviewers only verify and record verdicts, never land or remove branches/worktrees. Add regression coverage for generated review instructions. Document the landing flow in src/chitty/guide.md, README.md, and the relevant PLAN.md runner section; do not change landing behavior or version.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Repurposed: its refusals moved back into `TASK-131`, because landing without them was unsafe, and this now holds the prompt and documentation part.

TASK-224 supersedes the branch-version-bump requirement; version selection happens at release.

Review prompt and packaged role prohibit reviewers from landing or removing worktrees; regression test covers the generated prompt. README, guide, and PLAN document landing and manual fallback. Verified with make format && make check (397 Python tests and Node tests pass); no version bump.

Review failed (work): the worktree has uncommitted changes: `PLAN.md`, `README.md`, `src/chitty/guide.md`, `src/chitty/integrations/pi/chitty.ts`, `src/chitty/integrations/pi/tests/chitty.test.ts`, `src/chitty/roles/review.md`.

Re-ran make format && make check: format clean, 397 Python tests passed, and Node tests passed. chitty fix completed; it reported pre-existing Markdown warnings in other tasks.

Review failed (work): the worktree has uncommitted changes: `PLAN.md`, `README.md`, `src/chitty/guide.md`, `src/chitty/integrations/pi/chitty.ts`, `src/chitty/integrations/pi/tests/chitty.test.ts`, `src/chitty/roles/review.md`.

Regression test failed against the original continuation prompt (expected prohibition absent), then passed after restoring the updated prompt. Re-verified generated review instructions, packaged review role, landing docs in PLAN.md, README.md, and src/chitty/guide.md; no version change. make format && make check and npm test passed. chitty fix reports existing Markdown warnings in unrelated task files.

Review failed (work): the worktree has uncommitted changes: `PLAN.md`, `README.md`, `src/chitty/guide.md`, `src/chitty/integrations/pi/chitty.ts`, `src/chitty/integrations/pi/tests/chitty.test.ts`, `src/chitty/roles/review.md`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

## Summary

Handoff: Review prompt and packaged role prohibit reviewers from landing or removing branches/worktrees; PLAN.md, README.md, and src/chitty/guide.md document automated and manual landing. Verification: regression test failed against original prompt and passed after fix; make format && make check and npm test passed; no version bump. Follow-ups: none.

## History

- 2026-11-04T15:11:35Z mellow-newt → todo
- 2026-11-04T15:17:39Z mellow-newt: changed title, description, acceptance criteria, notes
- 2026-11-06T16:24:15Z youthful-toad: changed priority
- 2026-11-08T13:05:15Z eager-puffin: changed acceptance criteria, notes
- 2026-11-08T13:08:31Z eager-puffin: changed description
- 2026-11-08T18:16:49Z youthful-vole todo → doing
- 2026-11-08T18:17:08Z youthful-vole: wrote the plan
- 2026-11-08T18:21:02Z youthful-vole: changed notes, summary; ticked acceptance criteria
- 2026-11-08T18:21:02Z youthful-vole doing → review
- 2026-11-08T18:23:24Z sunny-adder: changed notes
- 2026-11-08T18:23:24Z sunny-adder review → doing
- 2026-11-08T18:26:32Z plucky-wren: changed notes, summary
- 2026-11-08T18:26:32Z plucky-wren doing → review
- 2026-11-08T18:27:32Z able-heron: changed notes
- 2026-11-08T18:27:32Z able-heron review → doing
- 2026-11-08T19:52:56Z sunny-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-08T19:52:56Z sunny-ibis doing → review
- 2026-11-08T19:57:53Z rosy-puffin: changed owner, notes
- 2026-11-08T19:57:53Z rosy-puffin review → blocked
