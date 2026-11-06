---
title: Fail `make check` on committed conflict markers
status: done
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

- [x] `make check` fails and prints the file and line when a tracked file contains a conflict marker line, and passes on `main` today.
- [x] `mate --list` still lists `check` with its `##` description.

## Plan

Add the exact conflict-marker git-grep recipe as the first line of Makefile's check target, preserving the existing mate description. Verify with a temporary tracked marker and without it, then run mate --list and make check.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-205/1`; failed with a marker and passed without one). Outcomes:
- The `$$` escape and the `!` inversion weren't mentioned: fixed, the ticket now gives the exact recipe line.
- Placement: fixed, the line goes first so the check fails fast.
- `git grep` reads the working tree, not the index: confirmed, and the ticket now says so.
- Legitimate matches on `main`: none, so the exclusion clause was removed.
- Bare failure output (no explanatory message): accepted, `file:line` is enough.

Verified the regression before the fix: a tracked conflict-marker line made the old make check pass. After adding the first recipe line, the same marker failed fast with README.md:243:<<<<<<< HEAD; removing it let make check pass. make format, make check, and mate --list all pass.

Reviewed: independently verified the implementation and both acceptance criteria; make format && make check passed, mate --list lists check with its description, and a temporary tracked README.md marker made make check fail with README.md:243 output. Working tree is clean.
1: pass - temporary tracked README.md marker made make check fail and print README.md:243; clean make check passed
2: pass - mate --list lists check with its ## description

## Summary

Added the conflict-marker guard as the first check recipe in Makefile. Verified failure output with a temporary tracked marker, then verified clean make format && make check and mate --list. No follow-ups.

## History

- 2026-11-06T11:51:16Z youthful-toad → backlog
- 2026-11-06T11:56:21Z youthful-toad: changed description, notes
- 2026-11-06T11:56:21Z youthful-toad backlog → todo
- 2026-11-06T20:30:27Z rosy-eel todo → doing
- 2026-11-06T20:30:38Z rosy-eel: wrote the plan
- 2026-11-06T20:35:37Z rosy-eel: changed notes, summary; ticked acceptance criteria
- 2026-11-06T20:35:37Z rosy-eel doing → review
- 2026-11-06T20:38:20Z jolly-lapwing: changed notes; ticked acceptance criteria
- 2026-11-06T20:38:20Z jolly-lapwing review → done
