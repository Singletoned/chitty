---
title: Set GIT_EDITOR=true in test_review_rebase_session.py
status: backlog
labels:
  - bug
created: 2026-11-26
moved_from: TASK-G7J457
---

## Description

In `tests/test_review_rebase_session.py`, `configure_rebase_agent` runs `git -c core.editor=true rebase --continue`. When the caller environment sets `GIT_EDITOR=false` (as non-interactive agent harnesses do), `GIT_EDITOR` takes precedence over `core.editor` in Git, so all four `finish=True` tests fail with `error: there was a problem with the editor 'false'`.

Pass `env={**os.environ, "GIT_EDITOR": "true"}` (or set `GIT_EDITOR=true` in the test script's environment) so the tests pass regardless of the parent shell's `GIT_EDITOR`.

## Notes

Suggestion origin: chitty

Fixed directly on `hotfix/git-editor` (decided with the person, 2026-11-26): the fake agent passes `GIT_EDITOR=true` to `git rebase --continue`. With `GIT_EDITOR=false`, 4 tests failed before and all 14 pass after.

## History

- 2026-11-26T18:06:04Z calm-ochre-quail → backlog
- 2026-11-26T18:06:06Z calm-ochre-quail: changed notes
- 2026-11-26T18:07:31Z calm-ochre-quail: changed labels
- 2026-11-26T18:22:56Z calm-ochre-quail: changed notes
- 2026-11-26T18:23:19Z calm-ochre-quail backlog → archived
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-G7J457
