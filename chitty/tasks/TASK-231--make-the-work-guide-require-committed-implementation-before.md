---
title: Make the work guide require committed implementation before review
status: backlog
priority: high
parent: TASK-106
created: 2026-11-08
---

## Description

In `src/chitty/roles/work.md`, clarify that `autocommit = true` commits Chitty ticket-file edits only. It does not commit code, tests, or other implementation files; agents must commit those changes in small logical commits with a `Task: <ID>` trailer. After formatting and checks, require `git status --short` to be empty before moving the ticket to `review`; if it is not, commit the intended changes or resolve the leftover files instead of claiming the work is ready. Keep this a guide-only change: no change to Git, runner, or ticket-file autocommit behavior. TASK-131 and TASK-211 each exhausted three reviews because their guide, code, or test files were still uncommitted despite passing checks and ticket notes.

## Acceptance Criteria

- [ ] A dedicated guide regression test in `tests/test_guide_work_commits.py` fails before the change and verifies `chitty guide work` distinguishes Chitty ticket-file autocommit from code/test commits, requires the `Task: <ID>` commit trailer, and requires an empty `git status --short` before moving to `review`.
- [ ] `make check` passes; the ticket branch does not change `chitty.toml`, the managed `AGENTS.md` block, or `src/chitty/__init__.py`.

## Notes

Observed on TASK-131 and TASK-211: workers recorded successful make checks and moved tickets to review, but reviewers repeatedly refused dirty worktrees. The existing work guide says git status or git add after a Chitty edit is unnecessary without explicitly saying that unrelated implementation changes remain uncommitted.

Read-only cold read found no serious ambiguity: change src/chitty/roles/work.md and add tests/test_guide_work_commits.py; the new guide test must be run against unchanged work.md and fail before the fix, then pass with make check. Rejected the provenance concern: chitty show in the TASK-131 and TASK-211 worktrees records three review preflight failures and human escalation each; the main checkout ticket copies are stale until those branches land. An implementing fail-first cold read remains before promotion from backlog.

Implemented directly for the human request in commit 80ce143: the guide now requires commits and a clean status before review; the same change adds a review transition guard, chitty check diagnostic, and immediate human blocking for dirty review branches. This backlog guide-only ticket is superseded.

## History

- 2026-11-08T17:58:14Z eager-puffin → backlog
- 2026-11-08T17:59:51Z eager-puffin: changed notes
- 2026-11-09T21:08:31Z eager-puffin: changed notes
