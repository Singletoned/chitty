---
title: Make workers verify criteria and reviewers report every failure at once
status: doing
priority: high
created: 2026-11-02
---

## Description

`TASK-99` bounced through two failed reviews. The worker ticked all four criteria when two were unmet. Each reviewer then reported only the first failure it found, and the ticks stayed in place after both failures. Each round trip costs a full review, and the third failure blocks the ticket to a human.

## Acceptance Criteria

- [x] The Pi work prompt (`chittyPrompt` and `continuationPrompt` in `src/chitty/integrations/pi/chitty.ts`) says to tick a criterion only after verifying it, and to re-check every criterion before setting `review`
- [x] The Pi review prompt says to check every criterion, list every failure in one note, and `--uncheck` each failed criterion
- [x] `src/chitty/guide.md` says the same, so non-Pi agents follow it
- [x] Node tests cover the new prompt text, and `__version__` is bumped

## Plan

Update Pi worker and review prompt text plus the generated guide. Add focused Node tests for the required wording, bump the package version because existing installations receive the guide through `chitty init`, then run formatting and the full check suite.

## Notes

Verified with `npm test`, `make check`, `chitty check`, and `chitty fix`; the latter retains only pre-existing Markdown-delimiter warnings in older task files.

Review failed: branch-local checks pass, but it cannot merge after TASK-102. Rebase onto current `main` and resolve the content conflicts in `src/chitty/guide.md` and `src/chitty/integrations/pi/chitty.ts`, retaining both tickets’ workflows and tests; rerun the full checks before returning to review. The branch worktree also cannot run `chitty edit` because its project registration belongs to the main checkout; a follow-up was suggested as `suggestion-7d8a71b264364f0888a24e965d8d8834`.

## History

- 2026-11-02T13:03:21Z lively-otter → todo
- 2026-11-03T07:21:16Z mellow-marten: wrote the plan
- 2026-11-03T07:21:16Z mellow-marten todo → doing
- 2026-11-03T07:25:31Z mellow-marten: changed notes; ticked acceptance criteria
- 2026-11-03T07:25:31Z mellow-marten doing → review
- 2026-11-03T09:22:25Z opal-marten: changed notes
- 2026-11-03T09:22:25Z opal-marten review → doing
