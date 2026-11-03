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
- [ ] Node tests cover the new prompt text, and `__version__` is bumped

## Plan

Update Pi worker and review prompt text plus the generated guide. Add focused Node tests for the required wording, bump the package version because existing installations receive the guide through `chitty init`, then run formatting and the full check suite.

## Notes

Verified with `npm test`, `make check`, `chitty check`, and `chitty fix`; the latter retains only pre-existing Markdown-delimiter warnings in older task files.

Review failed: branch-local checks pass, but it cannot merge after TASK-102. Rebase onto current `main` and resolve the content conflicts in `src/chitty/guide.md` and `src/chitty/integrations/pi/chitty.ts`, retaining both tickets’ workflows and tests; rerun the full checks before returning to review. The branch worktree also cannot run `chitty edit` because its project registration belongs to the main checkout; a follow-up was suggested as `suggestion-7d8a71b264364f0888a24e965d8d8834`.

Rebased onto current `main`, resolved the shared prompt and guide changes by retaining both the worktree and criterion-verification workflows, and reran `npm test`, `make check`, `chitty check`, and `chitty fix`. The latter retains only pre-existing Markdown-delimiter warnings in older task files.

Review failed (work): criterion 4 is unmet. `src/chitty/guide.md` changes but `__version__` does not: `git diff main...task-104` does not touch `src/chitty/__init__.py`, and both sides are at `0.1.18`, which `TASK-102` already took. The original commit `31d8e31` had a bump that the rebase appears to have dropped. Repositories on `0.1.18` would never learn to re-run `chitty init`. Bump to `0.1.19`, update `chitty.toml` by re-running `chitty init` if needed, run `make check` and `npm test`, then re-tick criterion 4. Criteria 1 to 3 are met: the wording is in `chittyPrompt`, `continuationPrompt` and `guide.md`, and `npm test` passes (14 tests).

Correction to the failure note above: do not run `chitty init` in this worktree, because it fails until `TASK-107` is fixed. Only bump `__version__` to `0.1.19`.

## History

- 2026-11-02T13:03:21Z lively-otter → todo
- 2026-11-03T07:21:16Z mellow-marten: wrote the plan
- 2026-11-03T07:21:16Z mellow-marten todo → doing
- 2026-11-03T07:25:31Z mellow-marten: changed notes; ticked acceptance criteria
- 2026-11-03T07:25:31Z mellow-marten doing → review
- 2026-11-03T09:22:25Z opal-marten: changed notes
- 2026-11-03T09:22:25Z opal-marten review → doing
- 2026-11-03T09:42:14Z mellow-marten: changed notes
- 2026-11-03T09:42:14Z mellow-marten doing → review
- 2026-11-03T10:39:51Z lively-panda: changed acceptance criteria, notes
- 2026-11-03T10:39:51Z lively-panda review → doing
- 2026-11-03T10:40:57Z lively-panda: changed notes
