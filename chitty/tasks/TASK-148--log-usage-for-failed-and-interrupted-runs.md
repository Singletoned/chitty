---
title: Log usage for failed and interrupted runs
status: doing
priority: high
depends_on:
  - TASK-127
parent: TASK-106
created: 2026-11-04
---

## Description

Second part of the log designed in `TASK-127`, which already writes a line for a session that ends normally. A session that cost money must not vanish, and dead and unchanged sessions are the expensive ones.

Write the line in a `finally` in `src/chitty/run.py`, covering a non-zero agent exit, Ctrl-C and the unchanged-status error, each keeping its exit code. `status_after` is `null` if the ticket cannot be read. If the usage file is missing or invalid (not JSON, not the expected shape, or an entry missing a field), write `models` null and warn on stderr. A failure to write the log warns on stderr and does not change the exit code: the helper catches its own errors, so the `finally` cannot hide the original one.

An entry's `cost` may be null, because `claude` transcripts hold no cost (`TASK-157`). That is valid, not a missing field, and a sum including one is null, with tokens still summed.

Out of scope: anything in the Pi extension, and any report.

## Acceptance Criteria

- [ ] Tests show a line still written, with `models` null and a warning on stderr, for a missing and an invalid usage file
- [ ] Tests show `status_after` correct and the exit code kept for an agent that exits non-zero, a Ctrl-C and an unchanged status
- [ ] A test shows a failure writing the log warning on stderr and keeping the exit code
- [ ] A test shows a `cost` of null accepted without a warning, summing to a null `cost` with the tokens still added

## Plan

Refactor run lifecycle so usage is read and appended from one finally path after agent interruption, non-zero exit, usage/status failures, and unchanged-status errors. Keep original exceptions and return codes while warning on malformed usage or log-write failures. Add focused run integration tests covering status/exit preservation, invalid or missing usage, write failures, and nullable costs, then run make check.

## Notes

Cold read of the split by a fresh Sonnet subagent, 2026-11-04. Fixed: the write failure now has a criterion and a stated way not to mask an error. Rejected: separate criteria for each invalid shape, `seconds`, and a removed worktree, which state cases, not behaviour.

Added 2026-11-04 from the cold read of `TASK-157`: a null `cost`, because this ticket holds the validation it would otherwise have to change.

## History

- 2026-11-04T15:11:30Z mellow-newt → todo
- 2026-11-04T15:17:32Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T18:03:09Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-05T14:45:29Z able-vole todo → doing
- 2026-11-05T14:45:50Z able-vole: wrote the plan
