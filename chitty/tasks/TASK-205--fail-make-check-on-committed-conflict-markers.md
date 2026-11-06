---
title: Fail `make check` on committed conflict markers
status: backlog
priority: medium
created: 2026-11-06
---

## Description

The `TASK-120` merge (`defcbf3`) committed a lone `<<<<<<< HEAD` line to `README.md`, and `make check` still passed. Fixed by `b6e0e1c`, but nothing stops it happening again.

Add a step to the `check` target in `Makefile` that fails when any tracked file has a line starting with `<<<<<<< `, `>>>>>>> ` or exactly `=======`, for example with `git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'`. Print the matches. If a tracked file legitimately contains such a line (check with that grep on `main` first), exclude it by path in the command.

Out of scope: checking for markers in Chitty itself (`chitty check`).

## Acceptance Criteria

- [ ] `make check` fails and prints the file and line when a tracked file contains a conflict marker line, and passes on `main` today.
- [ ] `mate --list` still lists `check` with its `##` description.

## History

- 2026-11-06T11:51:16Z youthful-toad → backlog
