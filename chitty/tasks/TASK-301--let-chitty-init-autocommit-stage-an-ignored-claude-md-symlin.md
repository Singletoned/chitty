---
title: Let `chitty init --autocommit` stage an ignored `CLAUDE.md` symlink
status: done
labels:
  - bug
priority: medium
created: 2026-11-12
---

## Description

In the `taidy` repository on 2026-11-12, `chitty init --autocommit` migrated the Chitty guide markers but failed while running `git add -- chitty.toml .gitignore AGENTS.md CLAUDE.md` because `CLAUDE.md` is ignored. The command should still commit the files that `chitty init` intentionally creates or updates, without changing the repository’s ignore rule or staging unrelated ignored files.

## Acceptance Criteria

- [x] In a repository where `CLAUDE.md` is ignored, `chitty init --autocommit` completes and its commit includes the managed `CLAUDE.md` symlink.
- [x] The autocommit path does not stage an unrelated ignored file that was present before `chitty init` ran.
- [x] A regression test fails against the current implementation before the fix and passes afterward; the existing `chitty init` checks continue to pass.

## Plan

Inspect init autocommit staging and its tests. Add a regression test for an ignored managed CLAUDE.md plus an unrelated pre-existing ignored file, confirm the test fails before the fix, then force-stage only the explicitly changed init paths. Run focused and full checks, commit implementation and tests, and update the ticket.

## Notes

Cold read 1 by a fresh Sonnet subagent, `refs/cold-read/TASK-301/1`; the regression test failed before the fix with Git rejecting ignored `CLAUDE.md`, then passed after the fix. `TestInit` (34 tests) and `make check` (507 tests, lint, typing, and Node tests) passed. No serious findings or surviving mutants. Starting point to inspect, not trust: `src/chitty/git.py` and `tests/test_cli.py` from `git show refs/cold-read/TASK-301/1:<path>`. The reader verified that force-adding only the explicitly touched paths does not include unrelated ignored files, and that the existing clean-tree requirement rejects unrelated staged or modified files.

The new regression test failed before the fix because Git rejected ignored CLAUDE.md; it passes after force-adding only the explicitly changed paths. Focused TestInit (35 tests) and make check (509 Python tests, ruff, pyright, Node tests) passed.

Reviewed: independently verified the change and regression.
1: pass - The ignored CLAUDE.md regression test passed; TestInit also checks the committed CLAUDE.md is a symlink to AGENTS.md, and make check printed OK.
2: pass - The ignored-file regression test passed and checks ignored.txt is absent from the commit and Git status.
3: pass - The regression test printed OK with the fix; running it with git add restored to pre-fix arguments printed FAILED and reported Git rejecting ignored CLAUDE.md. make format && make check passed, including 514 Python tests and Node tests.

## Summary

Implemented and committed as cdd8784 (Task: TASK-301). Force-add is constrained to init-supplied paths, so unrelated ignored files are not staged. Verified regression failure before fix, then focused TestInit and make check pass. No follow-ups.

## History

- 2026-11-12T18:07:33Z lively-violet-puffin → backlog
- 2026-11-12T18:07:41Z lively-violet-puffin backlog → cold-read
- 2026-11-12T18:11:02Z lively-violet-puffin: changed notes
- 2026-11-12T18:11:02Z lively-violet-puffin cold-read → planning
- 2026-11-12T18:11:07Z lively-violet-puffin planning → todo
- 2026-11-12T18:13:28Z upbeat-coral-toad todo → doing
- 2026-11-12T18:13:44Z upbeat-coral-toad: wrote the plan
- 2026-11-12T18:16:13Z upbeat-coral-toad: changed notes, summary; ticked acceptance criteria
- 2026-11-12T18:16:13Z upbeat-coral-toad doing → review
- 2026-11-12T20:27:40Z kind-white-gannet: changed notes; ticked acceptance criteria
- 2026-11-12T20:27:40Z kind-white-gannet review → done
