---
title: Fail `make check` on committed conflict markers
status: doing
priority: medium
created: 2026-11-06
---

## Description

The `TASK-120` merge (`defcbf3`) committed a lone `<<<<<<< HEAD` line to `README.md`, and `make check` still passed. `b6e0e1c` fixed it, but nothing stops it happening again.

Make the first recipe line of the `check` target in `Makefile` `! git grep -nE '^(<<<<<<< |>>>>>>> |=======$$)'`.
- The `!` inverts the exit status, because `git grep` exits 0 when it finds a match.
- `$$` is make's escape for a literal `$`.
- Putting it first makes the check fail before the slow lint and test steps.

`git grep` searches tracked files in the working tree, so unstaged markers are caught too. On a match it prints `file:line:text`. No tracked file on `main` matches today.

Out of scope: checking for markers in Chitty itself (`chitty check`).

## Acceptance Criteria

- [ ] `make check` fails and prints the file and line when a tracked file contains a conflict marker line, and passes on `main` today.
- [ ] `mate --list` still lists `check` with its `##` description.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-205/1`; failed with a marker and passed without one). Outcomes:
- The `$$` escape and the `!` inversion weren't mentioned: fixed, the ticket now gives the exact recipe line.
- Placement: fixed, the line goes first so the check fails fast.
- `git grep` reads the working tree, not the index: confirmed, and the ticket now says so.
- Legitimate matches on `main`: none, so the exclusion clause was removed.
- Bare failure output (no explanatory message): accepted, `file:line` is enough.

## History

- 2026-11-06T11:51:16Z youthful-toad → backlog
- 2026-11-06T11:56:21Z youthful-toad: changed description, notes
- 2026-11-06T11:56:21Z youthful-toad backlog → todo
- 2026-11-06T20:30:27Z rosy-eel todo → doing
