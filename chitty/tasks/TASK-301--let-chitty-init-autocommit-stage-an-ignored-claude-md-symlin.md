---
title: Let `chitty init --autocommit` stage an ignored `CLAUDE.md` symlink
status: todo
labels:
  - bug
priority: medium
created: 2026-11-12
---

## Description

In the `taidy` repository on 2026-11-12, `chitty init --autocommit` migrated the Chitty guide markers but failed while running `git add -- chitty.toml .gitignore AGENTS.md CLAUDE.md` because `CLAUDE.md` is ignored. The command should still commit the files that `chitty init` intentionally creates or updates, without changing the repository’s ignore rule or staging unrelated ignored files.

## Acceptance Criteria

- [ ] In a repository where `CLAUDE.md` is ignored, `chitty init --autocommit` completes and its commit includes the managed `CLAUDE.md` symlink.
- [ ] The autocommit path does not stage an unrelated ignored file that was present before `chitty init` ran.
- [ ] A regression test fails against the current implementation before the fix and passes afterward; the existing `chitty init` checks continue to pass.

## Notes

Cold read 1 by a fresh Sonnet subagent, `refs/cold-read/TASK-301/1`; the regression test failed before the fix with Git rejecting ignored `CLAUDE.md`, then passed after the fix. `TestInit` (34 tests) and `make check` (507 tests, lint, typing, and Node tests) passed. No serious findings or surviving mutants. Starting point to inspect, not trust: `src/chitty/git.py` and `tests/test_cli.py` from `git show refs/cold-read/TASK-301/1:<path>`. The reader verified that force-adding only the explicitly touched paths does not include unrelated ignored files, and that the existing clean-tree requirement rejects unrelated staged or modified files.

## History

- 2026-11-12T18:07:33Z lively-violet-puffin → backlog
- 2026-11-12T18:07:41Z lively-violet-puffin backlog → cold-read
- 2026-11-12T18:11:02Z lively-violet-puffin: changed notes
- 2026-11-12T18:11:02Z lively-violet-puffin cold-read → planning
- 2026-11-12T18:11:07Z lively-violet-puffin planning → todo
