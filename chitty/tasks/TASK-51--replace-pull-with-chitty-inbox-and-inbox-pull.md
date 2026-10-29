---
title: Replace pull with chitty inbox and inbox --pull
status: review
created: 2026-10-28
---

## Description

pull consumes the inbox, with no way to see what is waiting first. chitty inbox lists waiting suggestions (origin, date, title) without changing anything; chitty inbox --pull imports them all, as pull does today. Selective pulls wait until there is a need to pull a single item.

## Acceptance Criteria

- [x] chitty inbox lists waiting suggestions one per line with origin, date and title, supports --json, and changes nothing; when empty it says so on stderr with empty stdout
- [x] When suggestions are waiting, chitty inbox ends with a hint to run chitty inbox --pull
- [x] chitty inbox --pull behaves like today's pull
- [x] The 'suggestions waiting' hint, the managed guide block, MCP tools (inbox list and pull, in inbox.py), README and PLAN.md all use the new command
- [x] pull imports nothing and changes nothing; it exits non-zero with a message telling the user to run chitty inbox --pull and to re-run chitty init to refresh the guide
- [x] Tests cover listing, empty inbox, JSON, --pull and that pull leaves the inbox untouched

## Plan

Trace inbox listing and pull behavior through CLI, MCP and guide documentation. Add a read-only `inbox` listing with JSON and an explicit `--pull`, convert `pull` to a failing migration hint, update callers and tests, then run `make check` and hand off for review.

## Notes

Decided with the human: inbox --pull rather than two top-level commands; no selective pull yet. I added the pull alias so the guide in other repos keeps working until init refreshes it.

Changed by the human: pull no longer works as an alias; it only explains what to run instead.

Implemented the read-only inbox listing and migration behavior; remaining work is MCP exposure, documentation inventory updates, version refresh, and focused coverage.

Review failed: in a repo with no `project` name, `chitty inbox` and the MCP `inbox` tool hit `assert repo.config.project is not None` and print a bare `AssertionError` traceback, while `inbox --pull` gives "this repository has no project name". Reproduced in a scratch repo. Move the project check into an `inbox.py` function that takes the repo and raises `ChittyError` like `pull` does, so `cli.py` and `mcp.py` stay thin, and add a test. Everything else checks out: listing, hint, JSON, `--pull`, the `pull` migration error, guide, README and PLAN.md. Minor: `inbox --pull --json` silently ignores `--json`.

Addressed review feedback: inbox listing now resolves its project name through `inbox.py`, so both the CLI and MCP tool raise `ChittyError` with actionable guidance when it is absent. Added CLI and MCP regressions; verified with `make check` (155 tests) on 2026-10-29.

## Summary

Replaced importing `pull` with the read-only `inbox` command and explicit `inbox --pull`. Added the shared inbox metadata reader, MCP inbox tool, migration error, hints, managed guide, README and PLAN updates, plus CLI/MCP coverage. Bumped the release version and verified with `make check`.

## History

- 2026-10-28 → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-29 review → doing
- 2026-10-29 doing → review
