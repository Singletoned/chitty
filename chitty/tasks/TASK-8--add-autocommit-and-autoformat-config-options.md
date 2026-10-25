---
title: Add autocommit and autoformat config options
status: done
labels:
  - config
created: 2026-10-25
---

## Description

autoformat is the command to run on each file chitty writes, e.g. "mdformat". autocommit already exists as a repo-level bool in chitty.toml; check whether it needs more (e.g. user-level config).

## Acceptance Criteria

- [x] autoformat config option names the formatter command
- [x] When autoformat is set, it runs on every written file before the autocommit, so the commit holds the formatted files
- [x] Order on each write: chitty fix (TASK-10), then autoformat, then autocommit

## Plan

Add an optional validated autoformat command to repo config. At the shared autocommit boundary run fix, then invoke the formatter without a shell on existing touched files, then commit; abort before formatting or committing if fix leaves problems.

## Notes

If fix finds a problem it cannot fix, nothing is formatted or committed.

Question: Should autoformat run for user-level cross-repo adds? Answer: no. Those writes intentionally suppress the target repository’s autocommit behavior; formatting alongside it would be an unexpected side effect.

Verified: autoformat is an optional validated repository command. Existing written paths run through fix, formatter, and then autocommit; the committed integration-test task contains formatter output. make check passes.
