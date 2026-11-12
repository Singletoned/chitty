---
title: Let `chitty init --autocommit` stage an ignored `CLAUDE.md` symlink
status: backlog
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

## History

- 2026-11-12T18:07:33Z lively-violet-puffin → backlog
