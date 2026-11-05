---
title: Stop `chitty init` replacing a newer Pi extension
status: doing
labels:
  - bug
priority: high
parent: TASK-106
created: 2026-11-04
---

## Description

The Pi extension is one file shared by every repository, but `install_pi_extension` in `src/chitty/actor.py` writes whatever the running Chitty ships, whichever repository it runs in. On 2026-11-04, a session in another repository ran `chitty init` with a stale `~/.envs/default/bin/chitty`, 0.1.25, and replaced the installed extension with that version, which lacks the `TASK-147` fix. Nothing warned, because the state file only records a hash to detect local edits, and it matched. Any older copy can do this, including a worktree's `.venv` binary run from outside a linked worktree, because `init` skips machine-wide setup inside one.

Record the version in the state file, `_PI_EXTENSION_STATE`, as a second line under the hash. In `install_pi_extension`, after `_validate_pi_extension`, so a locally edited file is still refused: when the installed extension is from a newer Chitty than the one running, return `None` and print a warning to stderr, so `chitty init` finishes, because the repository's own setup is still right to update. The warning names both versions and says how to recover: upgrade Chitty, or delete the extension and its state file together. A state file holding only a hash, or an unreadable version, counts as older. An equal version replaces it, as now, so two checkouts at one version may swap it, which is accepted.

Use `_version_key` from `src/chitty/config.py`; `TASK-137` moves it there, and if that has not landed, move it. `actor.py` cannot import from `store.py`.

`chitty run` refreshes setup, so an older Chitty warns on every run, which is intended: it needs upgrading. A branch's `.venv` at a higher version, run outside a worktree, leaves its extension in place until `main` passes that version or the files are deleted. That is accepted too, and the warning covers it.

## Acceptance Criteria

- [x] A locally edited extension is still refused, shown by the existing test passing, and `__version__` is bumped above `main`'s
- [x] Tests show an older Chitty leaving a newer extension in place, warning with both versions and finishing the rest of `init`; a newer or equal Chitty updating and recording its version; and a hash-only state file being replaced

## Plan

Add version metadata to the Pi extension state file and compare it before replacing an otherwise validated extension. Reuse config.version_key, treating missing or malformed state versions as old, and warn to stderr while allowing init to continue when the installed version is newer. Extend actor tests with temporary Pi directories covering newer, equal/newer replacement, and hash-only state behavior; bump the package version and run the full check suite.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the state file's format, where `_version_key` lives given the import direction, the check's order after validation, unreadable versions, what the warning says, and a loose claim about worktrees. Accepted and stated: a warning on every run from an old copy, and a branch's `.venv` holding its extension.

## Summary

Implemented versioned Pi extension state with the hash on line one and Chitty version on line two. Locally edited extensions remain refused; older Chitty warns and leaves newer extensions untouched while init continues, while equal/newer running versions replace and record the version. Verification: `make check` passed (268 Python tests and Node tests); focused Pi/init tests passed. Follow-up: none.

## History

- 2026-11-04T21:00:16Z mellow-newt → backlog
- 2026-11-04T21:01:54Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T21:01:55Z mellow-newt backlog → todo
- 2026-11-05T20:24:26Z kind-adder todo → doing
- 2026-11-05T20:24:43Z kind-adder: wrote the plan
- 2026-11-05T20:32:12Z kind-adder: changed summary; ticked acceptance criteria
